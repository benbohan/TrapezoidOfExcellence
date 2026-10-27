# Trapezoid of Excellence

A fan-made, Bart Torvik-powered, Ryan Hammer-inspired college basketball adjusted-tempo vs adjusted-efficiency plot (chart forthcoming). Not affiliated with either provider.

## Get ratings

Python 3.9+; no third-party Python dependencies. Run:

```bash
python scripts/fetch_data.py --year 2026
python -m unittest discover -s tests -v
```

This fetches a **March 17, 2026 historical snapshot** of Torvik's 2025–26 ratings, archived publicly at [llimllib/ncaa-bracket-randomizer](https://github.com/llimllib/ncaa-bracket-randomizer/blob/6a2868c5eefdfc94159a449d0318723aa4e8bbd8/2026_team_results.csv). It covers all 365 Division I teams. **It is not final-season data and is not a live feed.** The original https://barttorvik.com/2026_team_results.csv returns HTTP 403 from GitHub Actions, so the default source does *not* call that blocked endpoint.

The output is `data/teams.json`. Teams include `name`, `conference`, `record`, `adj_t`, `adj_o`, `adj_d`, and `adj_em = adj_o - adj_d`. The root JSON includes `source`, `source_as_of`, and `data_status` to make source freshness clear. `updated_at` is when the JSON was generated, not when Torvik originally published the ratings.

To use another source in the future:

```bash
python scripts/fetch_data.py --year 2027 --source-url "https://example.com/verified-ratings.csv"
```

It must have columns named `team`, `conf`, `adjoe`, `adjde`, and `adjt`. To process a downloaded local CSV use `--input-csv path/to/file.csv`.

## GitHub Actions

Run **Actions → Refresh Torvik ratings → Run workflow** to regenerate the JSON. Optionally set the year and a new CSV source URL. Scheduled daily updates are intentionally **disabled while we only have a historical snapshot**; re-enable them once an accessible live-source URL is verified.

## Attribution

Ratings: [Bart Torvik / T-Rank](https://barttorvik.com/) (via linked public historical snapshot). Chart concept: Ryan Hammer's *Trapezoid of Excellence*. Torvik ratings are not KenPom ratings. Respect upstream data terms. The chart and Netlify deployment are the next project milestone.
