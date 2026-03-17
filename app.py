import logging
import os
import subprocess
from datetime import datetime, timedelta

from flask import Flask, render_template

from sl_api import get_all_departures, BUFFER_MIN, create_test_departures

app = Flask(__name__)
TEST = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def get_git_revision_short_hash():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        # Runs 'git rev-parse --short HEAD' and decodes the output
        return subprocess.check_output(
            ['/usr/bin/git', 'rev-parse', '--short', 'HEAD'],
            cwd=script_dir
        ).decode('ascii').strip()
    except Exception as e:
        log.warning("Error getting git hash:", e)
        return "Unknown"

def get_color(time):
    if time > 4:
        return "green"
    elif time > 2:
        return "yellow"
    elif time > 0:
        return "orange"
    elif time >= -BUFFER_MIN:
        return "red"
    return ""

def get_run_cycle():
    now = datetime.now()
    if 6 <= now.hour < 10:
        return timedelta(minutes=5) if now.weekday() < 5 else timedelta(minutes=10)
    elif 10 <= now.hour < 20 or 5 <= now.hour < 6:
        return timedelta(minutes=10)
    elif 20 <= now.hour < 22:
        return timedelta(minutes=20)
    return timedelta(hours=1)

cache = {
    'last_update': datetime.now() - timedelta(hours=24),
    'data': [],
    "git_hash": get_git_revision_short_hash()
}

@app.route('/')
def index():
    now = datetime.now()

    if now - cache["last_update"] > get_run_cycle():
        cache["last_update"] = now
        if TEST:
            departures_new = create_test_departures()
        else:
            departures_new = get_all_departures()

        # Only update if new data
        if departures_new:
            cache["data"] = departures_new

    departures = cache["data"]

    # Filter and limit to max 5
    active_departures = [d for d in departures if not d.is_too_late()]
    active_departures = active_departures[:min(5, len(active_departures))]
    
    # Process colors and data for the template
    display_data = []
    for d in active_departures:
        display_data.append({
            'stop_name': d.stop_name,
            'line': d.line,
            'destination': d.destination,
            'departure_minutes': d.departure_minutes,
            'walk_leave_in': d.walk_leave_in,
            'walk_color': get_color(d.walk_leave_in),
            'bike_leave_in': d.bike_leave_in,
            'bike_color': get_color(d.bike_leave_in),
            'show_walk': d.walk_leave_in >= -BUFFER_MIN,
            'show_bike': d.bike_leave_in >= -BUFFER_MIN
        })

    return render_template('index.html', 
                           departures=display_data, 
                           updated=datetime.now().strftime('%H:%M:%S'),
                           data_pulled=cache["last_update"].strftime('%H:%M:%S') if cache["last_update"] else "-",
                           interval="15s",
                           git_hash=cache["git_hash"])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)