"""Fixture tests for privacy_scan.py. Secret-shaped and email-shaped strings are built at run time, so this file
never holds one (the repo's own privacy check would reject it)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
SCAN = HERE / "privacy_scan.py"
AT = "@"


def run(root: Path, denylist: Path):
    return subprocess.run([sys.executable, str(SCAN), str(root), str(denylist)], capture_output=True, text=True)


class PrivacyScan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        subprocess.run(["git", "-C", str(self.root), "init", "-q"], check=True)
        self.deny = Path(self.tmp.name) / "denylist.txt"
        self.deny.write_text("# terms\nzebracorn\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name: str, text: str):
        (self.root / name).write_text(text)

    def test_clean_tree_passes(self):
        self.write("README.md", "Contact: dev" + AT + "example.com, noreply" + AT + "users.noreply.github.com. pkg" + AT + "1.2.3\n")
        r = run(self.root, self.deny)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("privacy scan: clean", r.stdout)

    def test_flags_email_secret_and_denylisted_term(self):
        self.write("a.md", "mail me: someone" + AT + "gmail.com\n")
        self.write("b.py", "pass" + "word = hunter22hunter\n")
        self.write("c.md", "a note about Zebracorn here\n")
        self.write("d.txt", "key: gh" + "p_" + "A" * 36 + "\n")
        r = run(self.root, self.deny)
        self.assertEqual(r.returncode, 1)
        for expected in ("a.md:1: email", "b.py:1: looks like a secret", "c.md:1: denylisted term", "d.txt:1: looks like a secret"):
            self.assertIn(expected, r.stdout)

    def test_term_matches_whole_words_only(self):
        self.write("a.md", "zebracorns graze\n")
        self.assertEqual(run(self.root, self.deny).returncode, 0)

    def test_scans_untracked_files_but_not_ignored_ones(self):
        self.write(".gitignore", "local.md\n")
        self.write("local.md", "zebracorn\n")
        self.assertEqual(run(self.root, self.deny).returncode, 0)
        self.write("new.md", "zebracorn\n")  # untracked, not ignored: must be caught before it is committed
        self.assertEqual(run(self.root, self.deny).returncode, 1)

    def test_fails_closed(self):
        self.assertEqual(run(self.root, Path(self.tmp.name) / "missing.txt").returncode, 2)
        self.assertEqual(run(Path(self.tmp.name), self.deny).returncode, 2)  # not a git tree


if __name__ == "__main__":
    unittest.main()
