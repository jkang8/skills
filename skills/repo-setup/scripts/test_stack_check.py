import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from stack_check import check  # noqa: E402


class StackCheck(unittest.TestCase):
    def test_good_repo_is_clean(self):
        self.assertEqual(check(HERE / "fixtures/good"), [])

    def test_bad_repo(self):
        self.assertEqual(sorted(check(HERE / "fixtures/bad")), sorted([
            "Makefile has no `test` target",
            "Makefile has no `gate` target",
            "missing .env.example",
            ".env is not in .gitignore",
            "missing README.md",
            "AGENTS.md is not a symlink to CLAUDE.md",
            "missing api/uv.lock",
            "missing api/src",
            "missing api/tests",
            "api/alembic/ exists but no compose.yaml for the local Postgres",
            ".github/workflows/ci.yml doesn't run `make gate` (keep check logic in the Makefile)",
        ]))


if __name__ == "__main__":
    unittest.main()
