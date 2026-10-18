import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from csvstats.cli import summarize  # noqa: E402


class Summarize(unittest.TestCase):
    def test_numeric_and_text_columns(self):
        rows = [{"city": "Oslo", "temp": "3"}, {"city": "Lima", "temp": "19"}, {"city": "Pune", "temp": ""}]
        self.assertEqual(summarize(rows), {"temp": {"count": 2, "mean": 11.0, "min": 3.0, "max": 19.0}})


if __name__ == "__main__":
    unittest.main()
