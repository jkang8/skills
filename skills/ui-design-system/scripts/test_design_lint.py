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

    def test_src_index_css_is_a_tokens_file(self):
        # shadcn's token stylesheet: oklch() custom properties and a hex ring color are fine here
        self.assertEqual([h for h in lint(HERE / "fixtures/good", DEFAULT_TOKENS) if "index.css" in h], [])

    def test_custom_property_in_a_component_stylesheet_is_flagged(self):
        hits = lint(HERE / "fixtures/bad", DEFAULT_TOKENS)
        self.assertIn("src/components/brand.css:2: rgb/hsl color: --brand: oklch(0.6 0.2 30);", hits)

    def test_index_css_below_src_root_is_not_a_tokens_file(self):
        hits = lint(HERE / "fixtures/bad", DEFAULT_TOKENS)
        self.assertIn("src/components/index.css:2: hex color: --accent: #7c3aed;", hits)

    def test_fixtures_folders_below_the_root_are_skipped(self):
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src/components/ui").mkdir(parents=True)
            (root / "src/components/ui/ok.tsx").write_text("export const Ok = () => <p>ok</p>;\n")
            shutil.copytree(HERE / "fixtures/bad", root / "tests/fixtures/bad")  # deliberate bad test data
            self.assertEqual(lint(root, DEFAULT_TOKENS), [])
            self.assertTrue(lint(root / "tests/fixtures/bad", DEFAULT_TOKENS))  # linting the folder itself still reports

    def test_a_real_violation_outside_fixtures_is_still_flagged(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src/components").mkdir(parents=True)
            (root / "src/components/x.tsx").write_text('export const X = () => <p style={{ color: "#7c3aed" }}>x</p>;\n')
            self.assertEqual(len(lint(root, DEFAULT_TOKENS)), 1)

    def test_tokens_file_may_hold_colors(self):
        hits = lint(HERE / "fixtures/good", ["nothing-matches"])
        self.assertTrue(any("theme.css" in h and "hex color" in h for h in hits))


if __name__ == "__main__":
    unittest.main()
