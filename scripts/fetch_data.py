#!/usr/bin/env python3
"""Fetch Bart Torvik team ratings and export chart-ready JSON (stdlib only)."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "teams.json"
SOURCE_URL = "https://barttorvik.com/{year}_team_results.csv"


def normalize_header(value: str) -> str:
    """Make headings like 'Adj OE', 'AdjOE' and 'adj_oe' comparable."""
    return "".join(char for char in value.lower() if char.isalnum())


def numeric(value: str | None, field: str, team: str) -> float:
    if value is None or not value.strip():
        raise ValueError(f"Missing {field} for {team}")
    try:
        result = float(value.strip().replace(",", ""))
    except ValueError as exc:
        raise ValueError(f"Invalid {field} for {team}: {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError(f"Non-finite {field} for {team}: {value!r}")
    return result


def parse_ratings_csv(raw: str) -> list[dict]:
    """Parse Torvik's headed CSV; fail loudly if the source format changes."""
    if raw.lstrip().lower().startswith(("<!doctype", "<html", "<head")):
        raise ValueError("Received HTML instead of a CSV (source may be blocking the request)")

    reader = csv.DictReader(io.StringIO(raw.lstrip("\ufeff")))
    if not reader.fieldnames:
        raise ValueError("No CSV header found")

    fields: dict[str, str] = {}
    for heading in reader.fieldnames:
        if heading:
            fields.setdefault(normalize_header(heading), heading)

    required = ("team", "conf", "adjoe", "adjde", "adjt")
    missing = [name for name in required if name not in fields]
    if missing:
        raise ValueError(
            f"Unexpected CSV headers: missing {', '.join(missing)}. "
            f"Found: {', '.join(reader.fieldnames)}"
        )

    teams = []
    names = set()
    for row in reader:
        team = (row.get(fields["team"]) or "").strip()
        if not team:
            continue
        if team in names:
            raise ValueError(f"Duplicate team in source data: {team}")
        names.add(team)

        offense = numeric(row.get(fields["adjoe"]), "AdjOE", team)
        defense = numeric(row.get(fields["adjde"]), "AdjDE", team)
        pace = numeric(row.get(fields["adjt"]), "AdjT", team)
        teams.append(
            {
                "name": team,
                "conference": (row.get(fields["conf"]) or "").strip(),
                "record": (row.get(fields["record"]) or "").strip() if "record" in fields else "",
                "adj_t": round(pace, 2),
                "adj_o": round(offense, 2),
                "adj_d": round(defense, 2),
                "adj_em": round(offense - defense, 2),
            }
        )

    if not teams:
        raise ValueError("CSV contained no teams")
    return sorted(teams, key=lambda team: team["name"].casefold())


def fetch_csv(year: int) -> str:
    url = SOURCE_URL.format(year=year)
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; TrapezoidOfExcellence/1.0; "
                "+https://github.com/benbohan/TrapezoidOfExcellence)"
            ),
            "Accept": "text/csv,text/plain,*/*",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            charset = response.headers.get_content_charset() or "utf-8-sig"
            return response.read().decode(charset)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not download {url}: {exc}") from exc


def run(year: int, output: Path, input_csv: Path | None = None) -> int:
    raw = input_csv.read_text(encoding="utf-8-sig") if input_csv else fetch_csv(year)
    teams = parse_ratings_csv(raw)
    if input_csv is None and len(teams) < 300:
        raise ValueError(f"Expected at least 300 Division I teams, got {len(teams)}; refusing to overwrite output")

    payload = {
        "season": year,
        "source": SOURCE_URL.format(year=year),
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "teams": teams,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(output)

    print(f"Saved {len(teams)} teams from {year - 1}-{str(year)[-2:]} to {output}")
    print("Top 5 teams by AdjEM:")
    for team in sorted(teams, key=lambda team: team["adj_em"], reverse=True)[:5]:
        print(f"  {team['name']:<25} pace={team['adj_t']:>5.1f}  AdjEM={team['adj_em']:+6.2f}")
    return len(teams)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2026, help="Ending season year (2026 = 2025-26)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path for chart-ready JSON")
    parser.add_argument("--input-csv", type=Path, help="Optional local CSV for offline testing")
    args = parser.parse_args()
    if not 2008 <= args.year <= 2100:
        parser.error("--year must be between 2008 and 2100")
    try:
        run(args.year, args.output, args.input_csv)
    except (ValueError, RuntimeError, OSError, UnicodeError) as exc:
        parser.exit(1, f"Data update failed: {exc}\n")


if __name__ == "__main__":
    main()
