from datetime import datetime, date, timedelta
import os
import json
import dataclasses
import logging

from dotenv import load_dotenv
import requests

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# https://blog.gitguardian.com/how-to-handle-secrets-in-python/
API_KEY = os.getenv("API_KEY")

BUFFER_MIN = 2    # Säkerhetsmarginal

@dataclasses.dataclass()
class Departure:
    line: str
    destination: str
    destination_id: str
    departure: date
    stop_name: str
    walkduration: int = None # min
    bikeduration: int = None # min

    @property
    def departure_minutes(self):
        return int((self.departure - datetime.now()).total_seconds() / 60)
    
    @property
    def walk_leave_in(self):
        if self.walkduration is None:
            return -1000
        return self.departure_minutes - (self.walkduration + BUFFER_MIN)

    @property
    def bike_leave_in(self):
        if self.bikeduration is None:
            return -1000
        return self.departure_minutes - (self.bikeduration + BUFFER_MIN)

    def is_too_late(self):
        return max(self.walk_leave_in, self.bike_leave_in) < -BUFFER_MIN
    
    @property
    def time_to_leave(self):
        if self.walk_leave_in >= -BUFFER_MIN and self.bike_leave_in >= -BUFFER_MIN: 
            t = min(self.walk_leave_in, self.bike_leave_in)
        elif self.walk_leave_in >= -BUFFER_MIN:
            t = self.walk_leave_in
        elif self.bike_leave_in >= -BUFFER_MIN:
            t = self.bike_leave_in
        else:
            t = -1000

        return t

    def __lt__(self, other):    
        return self.time_to_leave < other.time_to_leave
    
    def __str__(self):
        s = f"{self.stop_name:<17}: {self.line:>3} - {self.destination:>17} - {self.departure_minutes:>3} min"
        if self.walk_leave_in >= -BUFFER_MIN:
            s += f"\n Walk: {self.walk_leave_in:>3} min"

        if self.bike_leave_in >= -BUFFER_MIN:
            s += f"\n Bike: {self.bike_leave_in:>3} min"
        return s

def get_sl_departures(stop):
    url = f"https://realtime-api.trafiklab.se/v1/departures/{stop['id']}?key={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Kastar fel om statuskoden är dålig
        data = response.json()
        
        # Get stop name if missing provided
        if not stop["name"]:
            stop_name = data['stops'][0]['name']
        else:
            stop_name = stop["name"]
        
        # Get lines of interest with destination name if provided
        lines_of_interest = {}
        for info in stop["lines_w_destinations"]:
            name = None
            if len(info) == 2:
                line, dest_id = info
            elif len(info) == 3:
                line, dest_id, name = info
            else:
                log.error(f"Invalid line info, must be (line, dest_id) or (line, dest_id, name): {info}")
                return []

            lines_of_interest[(line, dest_id)] = name

        departures = data.get('departures', {})
        
        results = []
        for departure in departures:
            line = departure['route']['designation']
            dest_id = departure['route']['destination']['id']

            if (line, dest_id) not in lines_of_interest:
                continue
            
            if not lines_of_interest[(line, dest_id)]:
                destination = departure['route']['direction']
            else:
                destination = lines_of_interest[(line, dest_id)]
            
            # SL skickar tid som en sträng, t.ex. "2024-05-20T14:30:00"
            dep_time = datetime.fromisoformat(departure['realtime'])
            
            # TODO - add info if cancelled
            departure = Departure(
                line=line,
                destination=destination,
                destination_id=dest_id,
                departure=dep_time,
                stop_name=stop_name,
                walkduration=stop["walkduration"],
                bikeduration=stop["bikeduration"],
            )
            
            if departure.is_too_late():
                continue

            results.append(departure)

        return results

    except Exception as e:
        print(f"Ett fel uppstod: {e}")
        return []


def get_all_departures():
    # Load stops from file
    with open("stops.json", "r") as f:
        stops = json.load(f)
    
    departures = []
    for stop in stops:
        departures.extend(get_sl_departures(stop))

    log.info(f"Found {len(departures)} departures")
    departures.sort()
    return departures

def create_test_departures():
    departures = [
        Departure(
            line="666",
            destination="Hell",
            destination_id="666",
            departure=datetime.now() + timedelta(minutes=12),
            stop_name="Level 1",
            walkduration=15,
            bikeduration=6
        ),
        Departure(
            line="42",
            destination="The answer",
            destination_id="42",
            departure=datetime.now() + timedelta(minutes=8),
            stop_name="Confussion",
            walkduration=5,
            bikeduration=None
        )
    ]
    departures.sort()
    return departures

# Testa funktionen
if __name__ == "__main__":
    # Set logging level to DEBUG
    logging.basicConfig(level=logging.DEBUG)
    
    departures = get_all_departures()
    
    for d in departures:
        if not d.is_too_late():
            print(d)
