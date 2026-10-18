"""The README's account of the gate matches the Makefile, so the two can't drift again."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReadmeMatchesGate(unittest.TestCase):
    def setUp(self):
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        section = re.search(r"## Checks and evals\n(.*?)\n## ", self.readme, re.S).group(1)
        self.section = " ".join(section.split())

    def test_points_at_the_makefile_instead_of_restating_it(self):
        self.assertIn("the `Makefile` lists what it runs", self.section)

    def test_sec_check_is_described_as_inside_the_gate(self):
        self.assertIn("`sec_check.sh` is in the gate", self.section)
        self.assertIn("sec_check.sh", self.makefile)
        self.assertNotIn("sec_check.sh` and the privacy check. It passes", self.section)

    def test_every_script_listed_as_outside_the_gate_exists_and_is_not_in_the_makefile(self):
        outside = self.section.split("stay outside the gate", 1)[1]
        scripts = re.findall(r"`(skills/[\w./-]+\.sh)`", outside)
        self.assertEqual(len(scripts), 3)
        for rel in scripts:
            self.assertTrue((ROOT / rel).is_file(), rel)
            self.assertNotIn(rel, self.makefile, rel)  # full path: "check.sh" is a substring of "sec_check.sh"

    def test_every_check_the_makefile_runs_is_one_the_readme_names(self):
        for tool in ("doc_check", "arch_check", "design_lint", "sec_check"):
            self.assertIn(tool, self.makefile)
            self.assertIn(tool, self.section, f"README doesn't mention {tool}, which the Makefile runs")


if __name__ == "__main__":
    unittest.main()
