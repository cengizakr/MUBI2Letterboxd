import time
from collections import defaultdict, deque

from flask import Flask, Response, render_template, request

from mubi2lttrbx import (
    DEFAULT_MAX_FILMS,
    MubiExportError,
    build_letterboxd_csv,
    extract_user_id,
    fetch_watchlist,
)


app = Flask(__name__)

MAX_INPUT_LENGTH = 300
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def format_error(message: str) -> str:
    if "larger than" in message and "film limit" in message:
        return (
            f"That watchlist is too large for this tool. "
            f"The current limit is {DEFAULT_MAX_FILMS} films."
        )
    if "Could not find a numeric MUBI user id" in message:
        return (
            "I could not find the MUBI profile number in that text. "
            "Open your MUBI profile page and paste the full address from your browser."
        )
    if "That does not look like a MUBI URL" in message:
        return "That link is not from MUBI. Paste a MUBI profile or watchlist link."
    if "Please provide" in message:
        return "Paste your MUBI profile link first."
    if "Could not reach MUBI" in message:
        return "MUBI did not respond. Wait a moment, then try again."
    if "MUBI returned HTTP" in message:
        return "MUBI would not return that watchlist. Check that the profile is public."
    return message


def client_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.remote_addr or "unknown"


def rate_limited(ip_address: str) -> bool:
    now = time.time()
    bucket = RATE_LIMIT_BUCKETS[ip_address]

    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return True

    bucket.append(now)
    return False


@app.after_request
def add_privacy_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/export")
def export():
    source = request.form.get("mubi_url", "").strip()
    ip_address = client_ip()

    if rate_limited(ip_address):
        return (
            render_template(
                "index.html",
                error="Too many export attempts. Wait a minute, then try again.",
                mubi_url=source,
            ),
            429,
        )

    if len(source) > MAX_INPUT_LENGTH:
        return (
            render_template(
                "index.html",
                error="That input is too long. Paste only the MUBI profile link.",
                mubi_url="",
            ),
            400,
        )

    try:
        user_id = extract_user_id(source)
        films = fetch_watchlist(user_id, max_films=DEFAULT_MAX_FILMS)
    except (MubiExportError, ValueError) as exc:
        return render_template("index.html", error=format_error(str(exc)), mubi_url=source), 400

    if not films:
        return (
            render_template(
                "index.html",
                error=(
                    "No watchlist films were found for that MUBI profile. "
                    "Check that the profile has public watchlist items."
                ),
                mubi_url=source,
            ),
            404,
        )

    csv_text = build_letterboxd_csv(films)
    filename = f"mubi-watchlist-letterboxd-{user_id}.csv"

    return Response(
        csv_text,
        content_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    app.run(debug=True)
