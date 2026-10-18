"""Fixture test for review.sh: routing, checks and the prompt on a throwaway repo with one branch."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                   check=True, capture_output=True)


class Review(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        (self.repo / "app").mkdir(parents=True)
        (self.repo / "app/orders.py").write_text("def total(xs):\n    return sum(xs)\n")
        (self.repo / "README.md").write_text("# demo\n\nEntry point: `app/orders.py`.\n")
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")
        git(self.repo, "checkout", "-q", "-b", "feature")
        (self.repo / "app/utils.py").write_text("def money(c):\n    return f'${c / 100:.2f}'\n")
        (self.repo / "README.md").write_text("# demo\n\nEntry point: `app/orders.py`. Money: `app/gone.py`.\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "feature")
        self.out = root / "out"
        env = {**os.environ, "REVIEW_OUT": str(self.out), "REVIEW_NO_FETCH": "1", "REVIEW_SKIP_SEC": "1",
               "REVIEW_GATE": "true", "REVIEW_GOAL": "# Add money formatting\n\nOwned paths: app/, README.md"}
        self.run_ = subprocess.run(["sh", str(HERE / "review.sh"), str(self.repo), "feature", "main"],
                                   capture_output=True, text=True, env=env)

    def tearDown(self):
        self.tmp.cleanup()

    def test_routes_by_what_changed(self):
        out = self.run_.stdout
        self.assertIn("skills: architecture security doc-writing", out)
        self.assertIn("not applicable: ui-design-system repo-setup", out)

    def test_failing_checks_are_blocking_and_exit_1(self):
        self.assertEqual(self.run_.returncode, 1)
        checks = (self.out / "checks.txt").read_text()
        self.assertIn("app/utils.py: grab-bag file name", checks)
        self.assertIn("README.md:3: stale path `app/gone.py`", checks)
        self.assertIn("(exit 1: blocking)", checks)
        self.assertIn("FAIL  arch_check", self.run_.stdout)
        self.assertIn("ok    gate", self.run_.stdout)

    def test_reviewer_inputs(self):
        self.assertIn("VERDICT: PASS | CHANGES", (self.out / "prompt.md").read_text())
        lists = (self.out / "checklists.md").read_text()
        self.assertIn("# architecture", lists)
        self.assertIn("# doc-writing", lists)
        self.assertNotIn("# ui-design-system", lists)
        self.assertIn("Owned paths: app/, README.md", (self.out / "goal.md").read_text())
        self.assertIn("+def money", (self.out / "diff.patch").read_text())


if __name__ == "__main__":
    unittest.main()
