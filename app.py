from flask import Flask, render_template
from datetime import datetime
from sl_api import get_all_departures, BUFFER_MIN, create_test_departures

app = Flask(__name__)
TEST = False

def get_color(time):
    if time <= 0: return "red"
    elif time <= 2: return "orange"
    elif time <= 4: return "yellow"
    else: return "green"

def get_run_cycle():
    now = datetime.now()
    if 6 <= now.hour < 10:
        return "30s" if now.weekday() < 5 else "1m"
    elif 10 <= now.hour < 20 or 5 <= now.hour < 6:
        return "1m"
    return "5m"

@app.route('/')
def index():
    if TEST:
        departures = create_test_departures()
    else:
        departures = get_all_departures()

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
                           interval=get_run_cycle())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)