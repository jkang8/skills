"""privacy_check.sh skips GitHub's default merge line for the remote's owner, and nothing else."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
OWNER = "zebracorn"


class MergeMessage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        (self.root / "scripts").mkdir(parents=True)
        for f in ("privacy_check.sh", "privacy_scan.py"):
            shutil.copy(HERE / f, self.root / "scripts" / f)
        deny = Path(self.tmp.name) / "denylist.txt"
        deny.write_text(OWNER + "\n")
        cfg = Path(self.tmp.name) / "privacy.env"
        cfg.write_text(f"PRIVACY_DENYLIST={deny}\nPRIVACY_TERMS={OWNER}\n")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env["PRIVACY_CONFIG"] = str(cfg)
        self.git("init", "-q")
        self.git("remote", "add", "origin", f"https://github.com/{OWNER}/skills.git")
        (self.root / "a.txt").write_text("hello\n")
        self.git("add", "-A")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                       check=True, capture_output=True, env=self.env)

    def commit(self, msg):
        self.git("commit", "-q", "--allow-empty", "-m", msg)

    def check(self):
        return subprocess.run(["sh", str(self.root / "scripts" / "privacy_check.sh")], capture_output=True, text=True,
                              env=self.env)

    def test_default_merge_line_passes(self):
        self.commit(f"Merge pull request #7 from {OWNER}/feat/some-branch")
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PRIVACY CHECK PASS", r.stdout)

    def test_owner_elsewhere_in_a_commit_message_fails(self):
        self.commit(f"Merge pull request #7 from {OWNER}/feat/x")
        self.commit(f"Fix thing for {OWNER}")
        r = self.check()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("commit message: Fix thing", r.stdout)

    def test_merge_line_with_extra_text_fails(self):
        self.commit(f"Merge pull request #7 from {OWNER}/feat/x and {OWNER} private note")
        self.assertNotEqual(self.check().returncode, 0)

    def test_other_owner_in_merge_line_is_not_skipped(self):
        self.commit("Merge pull request #7 from someone-else/feat/x")
        self.assertEqual(self.check().returncode, 0)  # nothing denied in that line
        self.commit(f"Merge pull request #8 from {OWNER}-fork/feat/x")
        self.assertNotEqual(self.check().returncode, 0)

    def test_file_content_still_fails(self):
        self.commit(f"Merge pull request #7 from {OWNER}/feat/x")
        (self.root / "a.txt").write_text(f"{OWNER}\n")
        self.git("add", "-A")
        self.assertNotEqual(self.check().returncode, 0)


if __name__ == "__main__":
    unittest.main()
