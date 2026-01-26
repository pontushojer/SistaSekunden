from datetime import datetime, date
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

STOPS = [
    {
        "id": "740045606",
        "name": "Gribbylund Västra",
        "lines_w_destinations": [
            ("610", "11029"), # mot Danderyds sjukhus
            ("684", "11884"), # mot Täby centrum
        ],
        "walkduration": 5,
        "bikeduration": None,
    },
    {
        "id": "740024370",
        "name": "Visinge",
        "lines_w_destinations": [
            ("27", "11965"), # mot Stockholms Östra
        ],
        "walkduration": 15,
        "bikeduration": 6
    },
    {
        "id": "740024798",
        "name": "Galoppfältet",
        "lines_w_destinations": [
            ("28S", "11965"), # mot Stockholms Östra
        ],
        "walkduration": None,
        "bikeduration": 10
    },
]

BUFFER_MIN = 2    # Säkerhetsmarginal
MAX_DEPARTURES = 5

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
            return -10
        return self.departure_minutes - (self.walkduration + BUFFER_MIN)

    @property
    def bike_leave_in(self):
        if self.bikeduration is None:
            return -10
        return self.departure_minutes - (self.bikeduration + BUFFER_MIN)

    def is_too_late(self):
        return max(self.walk_leave_in, self.bike_leave_in) < -BUFFER_MIN
    
    @property
    def time_to_leave(self):
        if self.walk_leave_in >= -BUFFER_MIN and self.bike_leave_in >= -BUFFER_MIN: 
            t = min(self.walk_leave_in, self.bike_leave_in)
        elif self.walk_leave_in >= -BUFFER_MIN:
            t = self.walk_leave_in
        else:
            t = self.bike_leave_in

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
        
        departures = data.get('departures', {})
        
        results = []
        for departure in departures:
            line = departure['route']['designation']
            dest_id = departure['route']['destination']['id']

            if (line, dest_id) not in stop['lines_w_destinations']:
                continue
            else:
                 log.debug(f"Skipping {line} to {dest_id}")

            # SL skickar tid som en sträng, t.ex. "2024-05-20T14:30:00"
            dep_time = datetime.fromisoformat(departure['realtime'])
            
            departure = Departure(
                line=line,
                destination=departure['route']['direction'],
                destination_id=dest_id,
                departure=dep_time,
                stop_name=stop['name'],
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
    departures = []
    for stop in STOPS:
        departures.extend(get_sl_departures(stop))

    log.info(f"Found {len(departures)} departures")
    departures.sort()
    return departures

# Testa funktionen
if __name__ == "__main__":
    departures = []
    for stop in STOPS:
        departures.extend(get_sl_departures(stop))

    departures.sort()
    
    n = 0
    for d in departures:
        if not d.is_too_late():
            print(d)
            n += 1

        if n >= MAX_DEPARTURES:
            break
