#!/usr/bin/env python3
"""Scan a git work tree for personal data: emails, secret-shaped strings and denylisted terms. Stdlib only.

usage: privacy_scan.py <dir> <denylist-file>
Scans files git would commit (tracked, plus untracked and not ignored). The denylist is a local file, one term
per line, `#` comments allowed; it never lives in the repo. Exits 0 clean, 1 on any hit, 2 if it can't scan
(missing denylist or not a git tree), so a broken setup fails closed.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# A real address: the last label is letters, so `pkg@1.2.3` (a package version) doesn't match.
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}")
ALLOWED_EMAIL = re.compile(r"(noreply|example\.(com|org))", re.I)
SECRET = re.compile(
    r"-----BEGIN|\b(?:sk|ghp|gho|xox[bp])[-_][A-Za-z0-9_-]{16,}"
    r"|(?:password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*\S{6,}|\b(?:\d[ -]?){13,19}\b",
    re.I,
)
BINARY = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".sqlite", ".mp4", ".woff", ".woff2")


def files(root: Path) -> list[Path]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         capture_output=True, text=True, check=True).stdout.split("\0")
    return [root / f for f in dict.fromkeys(out) if f and not f.lower().endswith(BINARY)]


def denylist(path: Path) -> list[str]:
    return [t.strip() for t in path.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")]


def scan(root: Path, terms: list[str]) -> list[str]:
    pats = [re.compile(r"\b" + re.escape(t) + r"\b", re.I) for t in terms]
    hits = []
    for f in files(root):
        if f.is_symlink():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            where = f"{f.relative_to(root).as_posix()}:{n}"
            hits += [f"{where}: email {e}" for e in EMAIL.findall(line) if not ALLOWED_EMAIL.search(e)]
            # pattern definitions (this file's own) aren't secrets
            if SECRET.search(line) and "re.compile" not in line and not line.lstrip().startswith(("r\"", "r'", "#")):
                hits.append(f"{where}: looks like a secret")
            hits += [f"{where}: denylisted term" for p in pats if p.search(line)]
    return hits


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root, deny = Path(argv[0]).resolve(), Path(argv[1]).expanduser()
    if not deny.is_file():
        print(f"privacy scan: denylist {deny} missing (fails closed)")
        return 2
    try:
        terms = denylist(deny)
        hits = scan(root, terms)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"privacy scan: can't scan {root}: {e} (fails closed)")
        return 2
    print(f"privacy scan: {len(terms)} denylist terms")
    print("\n".join(hits) or "privacy scan: clean")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
