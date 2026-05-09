import argparse
import csv
import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import requests


API_URL = "https://mubi.com/services/api/wishes"
DEFAULT_OUTPUT = "films.csv"
DEFAULT_PER_PAGE = 24
REQUEST_TIMEOUT = 15
USER_AGENT = "mubi2letterboxd/1.0"


class MubiExportError(Exception):
    """Raised when a MUBI watchlist cannot be exported."""


@dataclass(frozen=True)
class Film:
    title: str
    year: int | str | None = None


def extract_user_id(value: str) -> str:
    """Extract a numeric MUBI user id from a user id or watchlist URL."""
    value = value.strip()
    if not value:
        raise MubiExportError("Please provide a MUBI watchlist URL or numeric user id.")

    if value.isdigit():
        return value

    parsed = urlparse(value)
    if parsed.netloc and "mubi.com" not in parsed.netloc.lower():
        raise MubiExportError("That does not look like a MUBI URL.")

    match = re.search(r"(?:^|/)users/(\d+)(?:/|$)", parsed.path)
    if not match:
        raise MubiExportError(
            "Could not find a numeric MUBI user id in the URL. "
            "Expected something like https://mubi.com/users/123/watchlist."
        )

    return match.group(1)


def fetch_watchlist(
    user_id: str,
    *,
    per_page: int = DEFAULT_PER_PAGE,
    session: requests.Session | None = None,
) -> list[Film]:
    """Fetch all films from a public MUBI watchlist."""
    if per_page < 1:
        raise ValueError("per_page must be greater than zero.")

    client = session or requests.Session()
    films: list[Film] = []
    page = 1

    while True:
        try:
            response = client.get(
                API_URL,
                params={"user_id": user_id, "page": page, "per_page": per_page},
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise MubiExportError(
                f"Could not reach MUBI while fetching page {page}: {exc}"
            ) from exc

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise MubiExportError(
                f"MUBI returned HTTP {response.status_code} while fetching page {page}."
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise MubiExportError("MUBI returned a non-JSON response.") from exc

        if not isinstance(data, list):
            raise MubiExportError("MUBI returned an unexpected response format.")

        if not data:
            break

        for item in data:
            film_data = item.get("film") if isinstance(item, dict) else None
            if not isinstance(film_data, dict):
                continue

            title = film_data.get("title")
            if not title:
                continue

            films.append(Film(title=str(title), year=film_data.get("year")))

        page += 1

    return films


def write_letterboxd_csv(films: Iterable[Film], file_obj) -> None:
    """Write films in Letterboxd's CSV import format."""
    writer = csv.writer(file_obj)
    writer.writerow(["Title", "Year"])
    for film in films:
        writer.writerow([film.title, film.year or ""])


def build_letterboxd_csv(films: Iterable[Film]) -> str:
    """Return a CSV string. Useful for a future web response body."""
    buffer = io.StringIO()
    write_letterboxd_csv(films, buffer)
    return buffer.getvalue()


def export_watchlist(source: str, output_path: Path, *, per_page: int = DEFAULT_PER_PAGE) -> int:
    user_id = extract_user_id(source)
    films = fetch_watchlist(user_id, per_page=per_page)

    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        write_letterboxd_csv(films, file_obj)

    return len(films)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a public MUBI watchlist to a Letterboxd-compatible CSV."
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="MUBI watchlist URL, profile URL, or numeric MUBI user id.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"CSV output path. Defaults to {DEFAULT_OUTPUT}.",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=DEFAULT_PER_PAGE,
        help=f"MUBI API page size. Defaults to {DEFAULT_PER_PAGE}.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    source = args.source or input("Please enter the MUBI watchlist URL: ")

    try:
        count = export_watchlist(source, Path(args.output), per_page=args.per_page)
    except (MubiExportError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Exported {count} films to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
