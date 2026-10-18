import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from summarize import summarize  # noqa: E402


class Summarize(unittest.TestCase):
    def test_means_per_task_and_arm(self):
        lines = ["adr without 1 1 6/10", "adr without 2 3 8/10", "adr with 1 0 9/10", "adr with 2 0 ?"]
        table, log = summarize(lines, "doc-writing", "opus", "opus", "2026-10-18")
        self.assertEqual(table[2], "| adr | 2.0 | 0.0 | 7.0/10(70.0%) | 9.0/10(90.0%) |")
        self.assertEqual(log, ["2026-10-18 doc-writing adr model=opus judge=opus n=2 hits_without=2.0 hits_with=0.0 "
                               "judge_without=7.0/10(70.0%) judge_with=9.0/10(90.0%)"])

    def test_skills_without_a_check_script(self):
        table, _ = summarize(["plan without 1 - 5/10", "plan with 1 - ?"], "x", "m", "j", "d")
        self.assertEqual(table[2], "| plan | - | - | 5.0/10(50.0%) | ? |")


if __name__ == "__main__":
    unittest.main()
