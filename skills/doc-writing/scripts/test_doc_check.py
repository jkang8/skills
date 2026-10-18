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
            "AGENTS.md: 101 lines, budget 100",
            "CLAUDE.md: must contain only `@AGENTS.md`",
            "README.md:3: stale path `src/gone.py`",
            "docs/decisions/0002-long.md: 16 lines, budget 15",
        ])

    def test_skill_budget(self):
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d) / "skills/demo/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("rule\n" * 121)
            self.assertEqual(check(Path(d)), ["skills/demo/SKILL.md: 121 lines, budget 120"])

    def test_skill_description_max(self):
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d) / "skills/demo/SKILL.md"
            skill.parent.mkdir(parents=True)
            ok = "x" * 60
            skill.write_text(f'---\nname: demo\ndescription: "{ok}"\n---\n# Demo\n')
            self.assertEqual(check(Path(d)), [])
            skill.write_text(f'---\nname: demo\ndescription: "{ok}y"\n---\n# Demo\n')
            self.assertEqual(check(Path(d)), ["skills/demo/SKILL.md: description is 61 chars, max 60"])

    def test_git_paths_skipped_in_worktrees(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".git").write_text("gitdir: elsewhere\n")  # how a worktree looks
            self.assertFalse(stale(".git/hooks/pre-commit", root / "AGENTS.md", root))


if __name__ == "__main__":
    unittest.main()
