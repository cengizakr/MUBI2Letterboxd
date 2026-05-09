# MUBI2Letterboxd

A small Flask website and CLI tool for exporting a public MUBI watchlist to a
Letterboxd-compatible CSV.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app app run
```

Then open:

```text
http://127.0.0.1:5000
```

## Accepted input

- MUBI profile URL, for example `https://mubi.com/en/users/10335289`
- MUBI watchlist URL, for example `https://mubi.com/en/users/10335289/watchlist`
- Numeric MUBI user ID, for example `10335289`

## CLI usage

```bash
python3 mubi2lttrbx.py https://mubi.com/en/users/10335289 --output films.csv
```

The generated CSV contains `Title` and `Year` columns for Letterboxd import.
