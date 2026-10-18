import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from doc_check import check  # noqa: E402


class DocCheck(unittest.TestCase):
    def test_good_repo_is_clean(self):
        self.assertEqual(check(HERE / "fixtures/good"), [])

    def test_bad_repo(self):
        self.assertEqual(sorted(check(HERE / "fixtures/bad")), [
            "CLAUDE.md: 101 lines, budget 100",
            "README.md:3: stale path `src/gone.py`",
            "docs/decisions/0002-long.md: 16 lines, budget 15",
        ])


if __name__ == "__main__":
    unittest.main()
