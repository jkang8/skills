"""Fixture tests for privacy_scan.py. Secret-shaped and email-shaped strings are built at run time, so this file
never holds one (the repo's own privacy check would reject it)."""
import shutil
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

    def test_a_secret_in_a_comment_or_heading_is_flagged(self):
        self.write("a.py", "# pass" + "word = hunter22hunter\n")
        self.write("b.md", "## api" + "_k" + "ey: " + "abcdef" + "123456\n")
        r = run(self.root, self.deny)
        self.assertEqual(r.returncode, 1)
        self.assertIn("a.py:1: looks like a secret", r.stdout)
        self.assertIn("b.md:1: looks like a secret", r.stdout)

    def test_only_the_scanners_own_pattern_lines_are_exempt(self):
        (self.root / "scripts").mkdir()
        shutil.copy(SCAN, self.root / "scripts/privacy_scan.py")
        self.assertEqual(run(self.root, self.deny).returncode, 0)  # its own regex definitions are not secrets
        shutil.copy(SCAN, self.root / "scripts/other_name.py")  # same text anywhere else is scanned
        self.write("c.py", "x = re.compile(r'a'); api" + "_k" + "ey = " + "'hunter" + "22hunter'\n")  # a re.compile on the line is no exemption
        r = run(self.root, self.deny)
        self.assertEqual(r.returncode, 1)
        self.assertIn("scripts/other_name.py", r.stdout)
        self.assertIn("c.py:1: looks like a secret", r.stdout)

    def test_unreadable_files_are_hits_not_skipped(self):
        for name in ("data.bin", "notes.sqlite", "scan.pdf"):
            (self.root / name).write_bytes(b"\xff\xfe\x00not utf-8")
        (self.root / "logo.png").write_bytes(b"\xff\xfe\x00image")  # plain images are skipped
        r = run(self.root, self.deny)
        self.assertEqual(r.returncode, 1)
        for name in ("data.bin", "notes.sqlite", "scan.pdf"):
            self.assertIn(f"{name}:1: can't be read as UTF-8 text", r.stdout)
        self.assertNotIn("logo.png", r.stdout)

    def test_output_never_echoes_the_matched_text(self):
        address = "someone" + AT + "gmail.com"
        self.write("a.md", f"mail {address}\n")
        r = run(self.root, self.deny)
        self.assertIn("a.md:1: email address", r.stdout)
        self.assertNotIn(address, r.stdout)

    def test_fails_closed(self):
        self.assertEqual(run(self.root, Path(self.tmp.name) / "missing.txt").returncode, 2)
        self.assertEqual(run(Path(self.tmp.name), self.deny).returncode, 2)  # not a git tree


if __name__ == "__main__":
    unittest.main()
