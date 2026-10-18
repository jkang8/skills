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

    def test_the_rule_is_stated_once_and_everywhere_else_points_to_it(self):
        rule = (r"never as a merge gate", r"on PR open", r"Never automatically", r"explicit, never automatic",
                r"(?:only when the user asks for a review|review[^.]{0,80}only (?:when|if) the user asks)")
        homes = {}
        for md in sorted(list(SKILLS.glob("*/SKILL.md")) + list(SKILLS.glob("*/references/*.md")) + [SKILLS.parent / "README.md"]):
            body = " ".join(md.read_text(encoding="utf-8").split())
            for pattern in rule:
                if re.search(pattern, body, re.I):
                    homes.setdefault(pattern, []).append(md.relative_to(SKILLS.parent).as_posix())
        for pattern, files in homes.items():
            self.assertEqual(files, ["skills/review/SKILL.md"], f"{pattern!r} is restated outside the review skill: {files}")
        for pointer in ("coding-orchestration/SKILL.md", "coding-orchestration/references/review.md",
                        "review/references/reviewer-prompt.md", "ui-design-system/SKILL.md"):
            self.assertIn("`review` skill", text(pointer), f"{pointer} should point to the review skill")

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
