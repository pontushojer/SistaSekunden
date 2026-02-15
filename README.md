
# Sista sekunden

A public transit departure board which accounts for walk and bike times.


![example of departure board](assets/display.png "Departure board")

## Setup 

Clone this repo into your raspberry pi.

```
git clone https://github.com/pontushojer/SistaSekunden.git
cd SistaSekunden
```

### API key
Requires access to the Trafiklab Realtime API, see https://developer.trafiklab.se/

API keys should be added to a `.env` file as below

```{bash}
API_KEY=<my-key>
```

e.g do 

```{bash}
echo "API_KEY=<my-key>" > .env
```

### Stop information

List of stops defined in JSON file `stops.json`

Each stop entry is a mapping with

- `id`: string for stop id, see [Development](#development)
- `name`: (optional) custom name for stop
- `lines_w_destinations`: array of arrays defining lines + destinations of interest. Each array contains `line_nr`, `destination_id` and optionally a custom destination name
- `walkduration`: integer with estimated walk time to stop, null if not relevant
- `bikeduration`: integer with estimated cykling time to stop, null if not relevant

Example
```
[
    {
        "id": "740045606",
        "name": "Gribbyl V\u00e4stra",
        "lines_w_destinations": [
            [
                "610",
                "11029",
                "Danderyds sjkh"
            ],
            [
                "684",
                "11884"
            ]
        ],
        "walkduration": 4,
        "bikeduration": null
    }
]
```

### Pixi env

Install pixi

```{bash}
curl -fsSL https://pixi.sh/install.sh | sh
```

Install dependencies from lock file

```{bash}
pixi install --locked
```

### Uv env

Install uv. Follow instructions as needed

```{bash}
curl -LsSf https://astral.sh/uv/install.sh | sh 
```

Create environment

```{bash}
uv sync
```

## Running

Using `uv` in examples, replace for `pixi` if desired.

### Run application using Flask (debug mode)

```{bash}
uv run python app.py 
```

### Run in production mode using guicorn [on Raspberry Pi]

```
uv run gunicorn --bind 0.0.0.0:5000 app:app
```

To test guicorn on macOS run

```
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run gunicorn --bind 0.0.0.0:5002 --workers 1 app:app
```

### Create service [on Raspberry Pi]

Create service script

```
sudo nano /etc/systemd/system/sistasekunden.service
```

Fill in as with correct paths

```
[Unit]
Description=Gunicorn instance to serve SistaSekunden
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/SistaSekunden
Environment="PATH=/home/pi/SistaSekunden/.venv/bin"
ExecStart=/home/pi/SistaSekunden/.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Start and enable

```
sudo systemctl start sistasekunden
sudo systemctl enable sistasekunden
```

## Development

A full list of stops for the Trafiklab Realtime API can be found here

https://realtime-api.trafiklab.se/v1/stops/list/?key=<key>

Replace `<key>` with API key in the link above.

