import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import tempfile  # noqa: E402

from doc_check import check, stale  # noqa: E402


class DocCheck(unittest.TestCase):
    def test_good_repo_is_clean(self):
        self.assertEqual(check(HERE / "fixtures/good"), [])

    def test_bad_repo(self):
        self.assertEqual(sorted(check(HERE / "fixtures/bad")), [
            "CLAUDE.md: 101 lines, budget 100",
            "README.md:3: stale path `src/gone.py`",
            "docs/decisions/0002-long.md: 16 lines, budget 15",
        ])

    def test_git_paths_skipped_in_worktrees(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".git").write_text("gitdir: elsewhere\n")  # how a worktree looks
            self.assertFalse(stale(".git/hooks/pre-commit", root / "CLAUDE.md", root))


if __name__ == "__main__":
    unittest.main()
