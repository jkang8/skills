"""run.sh hands the task's test results to the judge. Uses a fake `claude` on PATH, so no model is called.

The architecture rubric's item 2 requires "`.tests.txt` ends with OK and (exit 0)", but the judge can only read
files. This test proves run.sh runs the task's tests after the agent and puts their raw output in the judge's
folder, and that a broken change produces a failing `.tests.txt`.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Agent calls carry --permission-mode; judge calls run in a folder holding .judge-prompt.
FAKE_CLAUDE = r"""#!/bin/sh
if [ -f .judge-prompt ]; then
  if [ -f .tests.txt ]; then echo "tests.txt seen" >> "$FAKE_LOG"; else echo "tests.txt missing" >> "$FAKE_LOG"; fi
  if [ -f .tests.txt ] && grep -q '^OK' .tests.txt && grep -q '(exit 0)' .tests.txt; then echo "SCORE: 10/10"; else echo "SCORE: 0/10"; fi
else
  [ "${FAKE_BREAK:-}" = 1 ] && echo "def broken(" > app/utils.py
  echo "done"
fi
"""


class RunPassesTestResultsToJudge(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # a private copy of just what run.sh needs, so results.log in the real repo is untouched
        (self.tmp / "skills").mkdir()
        shutil.copytree(REPO / "evals", self.tmp / "evals", ignore=shutil.ignore_patterns("results.log", "__pycache__"))
        shutil.copytree(REPO / "skills/architecture", self.tmp / "skills/architecture",
                        ignore=shutil.ignore_patterns("references", "__pycache__"))
        (self.tmp / "skills/architecture/references").mkdir()
        (self.tmp / "skills/architecture/SKILL.md").write_text("fake skill\n")
        (self.tmp / "bin").mkdir()
        fake = self.tmp / "bin/claude"
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        self.log = self.tmp / "judge.log"

    def run_evals(self, **env):
        e = {**os.environ, "PATH": f"{self.tmp / 'bin'}:{os.environ['PATH']}", "FAKE_LOG": str(self.log), **env}
        out = subprocess.run(["sh", str(self.tmp / "evals/run.sh"), "architecture"], capture_output=True, text=True, env=e)
        self.assertEqual(out.returncode, 0, out.stderr)
        raw = re.search(r"raw outputs: (.+)/architecture", out.stdout).group(1)
        self.addCleanup(shutil.rmtree, Path(raw), True)
        return out.stdout, Path(raw) / "architecture"

    def test_passing_change_is_scored_from_the_tests_output(self):
        table, raw = self.run_evals()
        tests = sorted(raw.glob("*/*/tests.txt"))
        self.assertEqual(len(tests), 6)  # 3 tasks x 2 arms
        for t in tests:
            text = t.read_text()
            self.assertRegex(text, r"(?m)^OK$")
            self.assertTrue(text.rstrip().endswith("(exit 0)"), text)
        self.assertEqual(self.log.read_text().split("\n").count("tests.txt seen"), 6)
        self.assertNotIn("tests.txt missing", self.log.read_text())
        self.assertEqual(table.count("10.0/10(100.0%) | 10.0/10(100.0%)"), 3)

    def test_broken_change_gets_a_failing_tests_output(self):
        table, raw = self.run_evals(FAKE_BREAK="1")
        for t in raw.glob("*/*/tests.txt"):
            self.assertNotIn("(exit 0)", t.read_text())
        self.assertEqual(table.count("0.0/10(0.0%) | 0.0/10(0.0%)"), 3)


if __name__ == "__main__":
    unittest.main()
