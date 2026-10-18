#!/usr/bin/env python3
"""Fail on doc-writing violations in a repo: line budgets, skill description length and stale backticked paths. Stdlib only.

usage: doc_check.py <repo>
CLAUDE.md must contain only `@AGENTS.md` (AGENTS.md is the real agent context file).
A backticked path is checked when its first segment exists next to the doc or at the repo root, so
`src/app.py` is checked in a repo with src/, while `web/src/api/` in a repo without web/ is taken as
an example. Exits 1 with `path[:line]: problem` per hit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path, PurePath

# Pattern (matched from the right, like PurePath.match) -> max lines. First match wins.
BUDGETS = {
    "AGENTS.md": 100,
    "README.md": 150,
    "docs/decisions/*.md": 15,
    "skills/*/SKILL.md": 120,
}
DESCRIPTION_MAX = 60  # skill descriptions load into every session, so each is a short trigger
DESCRIPTION = re.compile(r'^description:\s*"?(.*?)"?\s*$', re.M)
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".venv", "fixtures"}
TICK = re.compile(r"`([^`\s]+)`")
FENCE = re.compile(r"^\s*(```|~~~)")
NOT_A_PATH = re.compile(r"[<>{}*$|()\[\]=@,;]|^-|^\w+://|^~|^/")


def docs(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file() and not p.is_symlink()
                  and not SKIP_DIRS & set(p.relative_to(root).parts))


def budget(rel: PurePath) -> int | None:
    return next((limit for pat, limit in BUDGETS.items() if rel.match(pat)), None)


def looks_like_path(tok: str) -> bool:
    return "/" in tok and not NOT_A_PATH.search(tok)


def stale(tok: str, doc: Path, root: Path) -> bool:
    tok = re.sub(r":\d+(-\d+)?$", "", tok)
    first = PurePath(tok).parts[0]
    if first == ".git":  # a file, not a folder, in worktrees; never tracked content
        return False
    bases = [b for b in (doc.parent, root) if (b / first).exists() or first in (".", "..")]
    return bool(bases) and not any((b / tok).exists() for b in bases)


def check(root: Path) -> list[str]:
    hits = []
    for claude in sorted(root.rglob("CLAUDE.md")):
        rel = claude.relative_to(root)
        if SKIP_DIRS & set(rel.parts):
            continue
        if claude.is_symlink() or claude.read_text(encoding="utf-8").strip() != "@AGENTS.md":
            hits.append(f"{rel.as_posix()}: must contain only `@AGENTS.md`")
        if not (claude.parent / "AGENTS.md").is_file() or (claude.parent / "AGENTS.md").is_symlink():
            hits.append(f"{rel.parent.as_posix()}/AGENTS.md: missing or a symlink; it must be the real file")
    for doc in docs(root):
        rel = doc.relative_to(root)
        lines = doc.read_text(encoding="utf-8").splitlines()
        limit = budget(rel)
        if limit is not None and len(lines) > limit:
            hits.append(f"{rel.as_posix()}: {len(lines)} lines, budget {limit}")
        if rel.match("skills/*/SKILL.md") and lines[:1] == ["---"]:
            front = "\n".join(lines[1:lines.index("---", 1)] if "---" in lines[1:] else [])
            m = DESCRIPTION.search(front)
            if m and len(m.group(1)) > DESCRIPTION_MAX:
                hits.append(f"{rel.as_posix()}: description is {len(m.group(1))} chars, max {DESCRIPTION_MAX}")
        fenced = False
        for n, line in enumerate(lines, 1):
            if FENCE.match(line):
                fenced = not fenced
                continue
            if fenced:
                continue
            hits += [f"{rel.as_posix()}:{n}: stale path `{t}`" for t in TICK.findall(line)
                     if looks_like_path(t) and stale(t, doc, root)]
    return hits


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    hits = check(Path(argv[0]).resolve())
    print("\n".join(hits) or "doc check: clean")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
