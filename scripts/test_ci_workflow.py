"""The CI workflow runs the gate with pinned actions and least-privilege permissions."""
import re
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


class CiWorkflow(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_every_action_is_pinned_to_a_commit_sha(self):
        uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)", self.text, re.M)
        self.assertTrue(uses)
        for u in uses:
            self.assertRegex(u, r"@[0-9a-f]{40}$", f"{u} is not pinned to a SHA")

    def test_permissions_are_read_only(self):
        self.assertRegex(self.text, r"(?m)^permissions:\n  contents: read\n")
        self.assertNotRegex(self.text, r"write")

    def test_runs_the_gate_on_prs_and_main_without_pull_request_target(self):
        self.assertRegex(self.text, r"(?m)^  pull_request:")
        self.assertRegex(self.text, r"branches: \[main\]")
        self.assertNotIn("pull_request_target", self.text)
        self.assertRegex(self.text, r"(?m)^      - run: make gate$")

    def test_does_not_write_bytecode_for_gitleaks_to_scan(self):
        self.assertIn('PYTHONDONTWRITEBYTECODE: "1"', self.text)

    def test_installs_ffmpeg_so_demo_video_tests_run(self):
        self.assertIn("apt-get install -y -qq ffmpeg", self.text)


if __name__ == "__main__":
    unittest.main()
