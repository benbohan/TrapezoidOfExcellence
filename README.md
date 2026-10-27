# Trapezoid of Excellence

A fan-made, **Bart Torvik-powered, Ryan Hammer-inspired** college basketball efficiency-versus-tempo chart. Not affiliated with Bart Torvik or Ryan Hammer.

## Step 1: Get data (Python, no pip dependencies)

The source is https://barttorvik.com/2026_team_results.csv for the completed 2025-26 season. We chart adjusted tempo (adj_t) on X and adjusted efficiency margin (adj_em = AdjOE - AdjDE) on Y.

Run: `python scripts/fetch_data.py --year 2026` (or `py` on Windows). This saves `data/teams.json` with a top-level `season`, `source`, `updated_at` and `teams` array. Each team has `name`, `conference`, `record`, `adj_t`, `adj_o`, `adj_d` and `adj_em`.

Test offline with: `python -m unittest discover -s tests -v`.

If you have a local CSV, run: `python scripts/fetch_data.py --year 2026 --input-csv path/to/file.csv`.

## GitHub automatic updates

Under **Actions → Refresh Torvik ratings → Run workflow**, choose a season end year. The workflow also attempts a daily refresh using 2026, committing `data/teams.json` if the source is accessible. When 2026-27 ratings exist, change the scheduled `DATA_YEAR` fallback in `.github/workflows/refresh-data.yml` from 2026 to 2027.

If GitHub Actions cannot push, enable **Settings → Actions → General → Workflow permissions → Read and write permissions** if allowed.

## Sources and attribution

Ratings come from [Bart Torvik / T-Rank](https://barttorvik.com/), not KenPom, so they will differ from Ryan Hammer's published visuals. The concept is inspired by Ryan Hammer's Trapezoid of Excellence. The public CSV is not a guaranteed API; respect site terms and keep requests infrequent. On fetch errors the script refuses to replace the existing JSON.

The interactive chart and Netlify site are next.
