import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
FILES = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]

# One distinctive phrase per rule; each must live in exactly one file.
RULES = [
    "least technical",
    "what do i do next",
    "trust and safety guarantees",
    "one headline number",
    "happened / impact",
    "one idea per sentence",
    "up to 3 words",
    "reconcile",
    "mockups",
]


class RulesAreSaidOnce(unittest.TestCase):
    def test_each_rule_phrase_has_one_home(self):
        texts = {f.name: f.read_text().lower() for f in FILES}
        for phrase in RULES:
            homes = [name for name, t in texts.items() if phrase in t]
            self.assertEqual(len(homes), 1, f"{phrase!r} appears in {homes}")


if __name__ == "__main__":
    unittest.main()
