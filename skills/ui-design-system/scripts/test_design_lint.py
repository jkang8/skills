import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from design_lint import DEFAULT_TOKENS, lint  # noqa: E402


class DesignLint(unittest.TestCase):
    def test_good_tree_is_clean(self):
        self.assertEqual(lint(HERE / "fixtures/good", DEFAULT_TOKENS), [])

    def test_bad_tree_hits_every_rule(self):
        hits = lint(HERE / "fixtures/bad", DEFAULT_TOKENS)
        rules = {h.split(": ")[1] for h in hits}
        self.assertEqual(rules, {
            "hex color", "rgb/hsl color", "palette class", "gradient", "rounded-2xl/3xl", "gradient text",
            "backdrop blur", "transition-all", "emoji", "UI import outside components/ui",
        })
        self.assertTrue(all(h.startswith("src/") for h in hits))

    def test_tokens_file_may_hold_colors(self):
        hits = lint(HERE / "fixtures/good", ["nothing-matches"])
        self.assertTrue(any("theme.css" in h and "hex color" in h for h in hits))


if __name__ == "__main__":
    unittest.main()
