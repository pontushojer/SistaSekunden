
# Sista sekunden

A public transit departure board which accounts for walk and bike times.

## Setup 


### API key
Requires access to the Trafiklab Realtime API, see https://developer.trafiklab.se/

API keys should be added to a `.env` file as below

```{bash}
API_KEY=<my-key>
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

### Run in production mode using guicorn

```
uv run gunicorn --bind 0.0.0.0:5000 app:app
```

To test guicorn on macOS run

```
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run gunicorn --bind 0.0.0.0:5002 --workers 1 app:app
```

## Development

A full list of stops for the Trafiklab Realtime API can be found here

https://realtime-api.trafiklab.se/v1/stops/list/?key=<key>

Replace `<key>` with API key in the link above.

