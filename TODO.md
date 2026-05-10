# MUBI to Letterboxd Website TODO

## Current Step

- Prepare deployment files and instructions.

## Next Steps

- Prepare deployment files and instructions.

## Done

- Added production safeguards: stricter input validation, request timeout, max watchlist size, simple per-IP rate limit, no-store headers, and no saved CSV files.
- Added the unofficial-tool disclaimer.
- Improved user-facing error messages.
- Updated the UI for people who do not know what URL to paste or what to do with the downloaded file.
- Created the first website version with a Python backend and a simple download page.
- Added project dependencies in `requirements.txt`.
- Created a Flask app in `app.py`.
- Added a homepage template with one MUBI URL input.
- Added a CSV download route that uses the existing exporter functions.
- Added basic styling for the page.
- Tested the website locally with a real MUBI profile URL.
- Refactored `mubi2lttrbx.py` into reusable exporter functions.
- Verified profile URLs like `https://mubi.com/en/users/10335289` are accepted.
- Verified a live export can generate a Letterboxd-compatible CSV.
