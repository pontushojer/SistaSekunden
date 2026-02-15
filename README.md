
# Sista sekunden

A public transit departure board which accounts for walk and bike times.

## Setup 

Requires access to the Trafiklab Realtime API, see https://developer.trafiklab.se/

API keys should be added to a `.env` file as below

```{bash}
API_KEY=<my-key>
```

## Running

### Pixi env

Install pixi

```{bash}
url -fsSL https://pixi.sh/install.sh | sh
```

Install dependencies from lock file

```{bash}
pixi install --locked
```

Run application

```{bash}
pixi run python app.py 
```

### Uv env

Install uv. Follow instructions as needed

```{bash}
url -LsSf https://astral.sh/uv/install.sh | sh 
```

Create environment

```{bash}
uv sync
```

Run application

```{bash}
uv run app.py
```


## Development

A full list of stops for the Trafiklab Realtime API can be found here

https://realtime-api.trafiklab.se/v1/stops/list/?key=<key>

Replace `<key>` with API key in the link above.

