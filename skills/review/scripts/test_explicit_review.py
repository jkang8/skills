"""Review is explicit, never automatic: the published text says so, and no script wires it in."""
import re
import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]


def text(rel: str) -> str:
    return " ".join((SKILLS / rel).read_text(encoding="utf-8").split())


class ExplicitReview(unittest.TestCase):
    def test_review_skill_states_the_rule(self):
        t = text("review/SKILL.md")
        for phrase in ("Only when the user asks", "Never automatically", "not on PR open", "not on push",
                       "not from cron", "never as a merge gate", "default check is `make gate`"):
            self.assertIn(phrase, t)

    def test_orchestration_states_the_rule(self):
        t = text("coding-orchestration/SKILL.md")
        for phrase in ("Review is explicit, never automatic", "only when the user asks", "Never on PR open, push or cron",
                       "never as a merge gate", "default check is `make gate`"):
            self.assertIn(phrase, t)

    def test_no_script_runs_a_review(self):
        for rel in ("coding-orchestration/scripts/improve.sh", "coding-orchestration/scripts/improve.md",
                    "doc-writing/scripts/prune_docs.sh"):
            self.assertFalse(re.search(r"review\.sh|review skill|independent review|reviewer run", text(rel), re.I), rel)

    def test_orchestration_does_not_require_a_reviewer_verdict(self):
        t = text("coding-orchestration/SKILL.md")
        self.assertNotIn("returned `VERDICT: PASS`", t)
        self.assertNotIn("Report to the user once it passes", t)


if __name__ == "__main__":
    unittest.main()
