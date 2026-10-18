"""sec_check.sh pins its tools and verifies the gitleaks download. Offline: a fake release is served from file://.

The real-tool test is test_sec_check.sh (needs the network). This one checks the logic around it: the versions are
pinned (no "latest"), a download matching its pinned SHA-256 is installed and run, and one that doesn't is a
failure that is never executed.
"""
import hashlib
import io
import os
import platform
import re
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sec_check.sh"
VERSION = re.search(r"^GITLEAKS_VERSION=(\S+)", SCRIPT.read_text(), re.M).group(1)
OS = platform.system().lower()
ARCH = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "x64", "amd64": "x64"}[platform.machine().lower()]


def release_tarball(marker: Path) -> bytes:
    """A tar.gz holding a fake `gitleaks` that records that it ran and reports no leaks."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        body = f"#!/bin/sh\necho ran >> '{marker}'\nexit 0\n".encode()
        info = tarfile.TarInfo("gitleaks")
        info.size, info.mode = len(body), 0o755
        tar.addfile(info, io.BytesIO(body))
    return buf.getvalue()


class SecCheckPins(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "notes.txt").write_text("nothing to see\n")  # no Python, no lockfiles: only gitleaks runs
        self.marker = self.root / "ran.log"
        self.releases = self.root / "releases" / f"v{VERSION}"
        self.releases.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def publish(self, content: bytes):
        (self.releases / f"gitleaks_{VERSION}_{OS}_{ARCH}.tar.gz").write_bytes(content)

    def run_check(self, pinned: str):
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.root), "SEC_CHECK_HOME": str(self.root / "tools"),
               "SEC_CHECK_GITLEAKS_BASE": f"file://{self.root / 'releases'}", "SEC_CHECK_GITLEAKS_SHA256": pinned}
        return subprocess.run(["sh", str(SCRIPT), str(self.repo)], capture_output=True, text=True, env=env)

    def test_versions_are_pinned_not_latest(self):
        text = SCRIPT.read_text()
        self.assertNotIn("releases/latest", text)
        self.assertRegex(text, r"(?m)^GITLEAKS_VERSION=\d+\.\d+\.\d+$")
        self.assertRegex(text, r"(?m)^RUFF_VERSION=\d+\.\d+\.\d+$")
        self.assertRegex(text, r"(?m)^PIP_AUDIT_VERSION=\d+\.\d+\.\d+$")
        self.assertIn('"ruff@$RUFF_VERSION"', text)
        self.assertIn('"pip-audit@$PIP_AUDIT_VERSION"', text)
        pins = re.findall(r"(?m)^(?:GITLEAKS_SHA256=\")?((?:darwin|linux)_(?:arm64|x64))=([0-9a-f]{64})\"?$", text)
        self.assertEqual(sorted(p for p, _ in pins), ["darwin_arm64", "darwin_x64", "linux_arm64", "linux_x64"])

    def test_a_download_matching_its_checksum_is_installed_and_run(self):
        tarball = release_tarball(self.marker)
        self.publish(tarball)
        out = self.run_check(f"{OS}_{ARCH}={hashlib.sha256(tarball).hexdigest()}")
        self.assertIn("ok    gitleaks", out.stdout, out.stdout + out.stderr)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(self.marker.read_text().strip(), "ran")

    def test_a_download_that_does_not_match_is_a_failure_and_never_runs(self):
        self.publish(release_tarball(self.marker))
        out = self.run_check(f"{OS}_{ARCH}={'0' * 64}")
        self.assertIn("FAIL  gitleaks", out.stdout)
        self.assertIn("does not match its pinned SHA-256", out.stdout)
        self.assertEqual(out.returncode, 1)
        self.assertFalse(self.marker.exists())  # the unverified binary was never executed

    def test_a_platform_without_a_pin_is_skipped_with_a_warning_not_downloaded(self):
        self.publish(release_tarball(self.marker))
        out = self.run_check("plan9_mips=" + "0" * 64)
        self.assertIn("skip  gitleaks (warning: no pinned checksum for", out.stdout)
        self.assertEqual(out.returncode, 0)
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    unittest.main()
