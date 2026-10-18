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

    def test_launch_command_uses_review_claude_when_set(self):
        env = {**os.environ, "REVIEW_OUT": str(self.out) + "2", "REVIEW_NO_FETCH": "1", "REVIEW_SKIP_SEC": "1",
               "REVIEW_GATE": "true", "REVIEW_GOAL": "# g", "REVIEW_CLAUDE": "wrapper run acct claude"}
        r = subprocess.run(["sh", str(HERE / "review.sh"), str(self.repo), "feature", "main"],
                           capture_output=True, text=True, env=env)
        cmd = next(line for line in r.stdout.splitlines() if " -p " in line and "prompt.md" in line)
        self.assertIn('&& wrapper run acct claude -p "', cmd)
        self.assertIn("claude -p", next(l for l in self.run_.stdout.splitlines() if "prompt.md" in l and " -p " in l))

    def test_launch_command_is_read_only(self):
        cmd = next(line for line in self.run_.stdout.splitlines() if "claude -p" in line)
        self.assertIn('--tools "Read,Glob,Grep"', cmd)
        self.assertIn("--disallowedTools", cmd)
        for tool in ("Edit", "Write", "NotebookEdit", "Bash"):
            self.assertIn(tool, cmd.split("--disallowedTools")[1])
        self.assertNotIn("--allowedTools", cmd)  # pre-approval alone doesn't restrict anything

    def test_check_output_and_checklists_are_inline_in_the_prompt(self):
        prompt = (self.out / "prompt.md").read_text()
        for section in ("=== goal.md ===", "=== checks.txt ===", "=== checklists.md ==="):
            self.assertIn(section, prompt)
        # the raw output itself, not a pointer to it
        self.assertIn("app/utils.py: grab-bag file name", prompt)
        self.assertIn("(exit 1: blocking)", prompt)
        self.assertIn("Owned paths: app/, README.md", prompt)
        self.assertIn("# architecture", prompt)
        self.assertNotIn("you don't need to open those files", prompt.split("=== goal.md ===")[1])  # prose comes first

    def test_inline_text_is_capped_with_a_note(self):
        env = {**os.environ, "REVIEW_OUT": str(self.out) + "-small", "REVIEW_NO_FETCH": "1", "REVIEW_SKIP_SEC": "1",
               "REVIEW_GATE": "true", "REVIEW_GOAL": "# goal", "REVIEW_MAX_INLINE": "60"}
        subprocess.run(["sh", str(HERE / "review.sh"), str(self.repo), "feature", "main"], capture_output=True, text=True, env=env)
        prompt = (Path(str(self.out) + "-small") / "prompt.md").read_text()
        self.assertIn("[truncated at 60 bytes; the full file is checks.txt in the review folder]", prompt)
        self.assertGreater(len((Path(str(self.out) + "-small") / "checks.txt").read_text()), 60)  # the file keeps everything

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
