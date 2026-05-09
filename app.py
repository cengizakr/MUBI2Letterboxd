from flask import Flask, Response, render_template, request

from mubi2lttrbx import MubiExportError, build_letterboxd_csv, extract_user_id, fetch_watchlist


app = Flask(__name__)


def format_error(message: str) -> str:
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


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/export")
def export():
    source = request.form.get("mubi_url", "").strip()

    try:
        user_id = extract_user_id(source)
        films = fetch_watchlist(user_id)
    except MubiExportError as exc:
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
