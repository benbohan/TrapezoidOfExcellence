"""Offline tests; no Torvik network request needed."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_data import parse_ratings_csv, source_for_year  # noqa: E402


EXAMPLE = """Rank,Team,Conf,Record,AdjOE,AdjDE,AdjT,Barthag
1,Arizona,B12,30-4,121.5,94.0,70.3,0.99
2,Duke,ACC,29-5,120.6,95.2,67.4,0.98
"""


class TorvikParserTests(unittest.TestCase):
    def test_chart_coordinates(self):
        teams = parse_ratings_csv(EXAMPLE)
        self.assertEqual(len(teams), 2)
        self.assertEqual(teams[0]["name"], "Arizona")
        self.assertEqual(teams[0]["conference"], "B12")
        self.assertEqual(teams[0]["record"], "30-4")
        self.assertEqual(teams[0]["adj_t"], 70.3)
        self.assertEqual(teams[0]["adj_em"], 27.5)

    def test_header_variants(self):
        csv_text = "\ufeffTeam,Conf,Adj OE,Adj DE,Adj T\nArizona,B12,121,94,70\n"
        self.assertEqual(parse_ratings_csv(csv_text)[0]["adj_em"], 27)

    def test_html_error(self):
        with self.assertRaisesRegex(ValueError, "HTML"):
            parse_ratings_csv("<!doctype html><html><body>Access denied</body></html>")

    def test_missing_column_error(self):
        with self.assertRaisesRegex(ValueError, "adjt"):
            parse_ratings_csv("Team,Conf,AdjOE,AdjDE\nArizona,B12,121,94\n")

    def test_duplicate_teams_error(self):
        csv_text = EXAMPLE + "3,Arizona,B12,29-5,120.0,94.0,70.3,0.97\n"
        with self.assertRaisesRegex(ValueError, "Duplicate team"):
            parse_ratings_csv(csv_text)

    def test_snapshot_provenance(self):
        url, date = source_for_year(2026)
        self.assertIn("githubusercontent.com", url)
        self.assertEqual(date, "2026-03-17")

    def test_future_season_requires_new_source(self):
        with self.assertRaisesRegex(ValueError, "No known publicly hosted"):
            source_for_year(2027)

    def test_non_numeric_error(self):
        with self.assertRaisesRegex(ValueError, "Invalid AdjOE"):
            parse_ratings_csv(EXAMPLE.replace("121.5", "n/a"))


if __name__ == "__main__":
    unittest.main()
