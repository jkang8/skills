#!/usr/bin/env python3
"""Fail when a repo doesn't match the repo-setup layout. Stdlib only.

usage: stack_check.py <repo>
api/ and web/ are optional (scaffold only what the project uses), but whichever exists must be complete.
Exits 1 with one line per problem.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TARGETS = ("dev", "test", "gate")


def make_targets(root: Path) -> set[str] | None:
    for name in ("Makefile", "justfile"):
        f = root / name
        if f.is_file():
            return set(re.findall(r"^([A-Za-z][\w-]*)\s*:(?!=)", f.read_text(encoding="utf-8"), re.M))
    return None


def gitignored(root: Path, entry: str) -> bool:
    f = root / ".gitignore"
    return f.is_file() and entry in {line.strip().lstrip("/") for line in f.read_text(encoding="utf-8").splitlines()}


def check(root: Path) -> list[str]:
    out: list[str] = []

    def need(rel: str, why: str = "") -> None:
        if not (root / rel).exists():
            out.append(f"missing {rel}{why}")

    targets = make_targets(root)
    if targets is None:
        out.append("missing Makefile (or justfile)")
    else:
        out += [f"Makefile has no `{t}` target" for t in TARGETS if t not in targets]
    need(".env.example")
    if not gitignored(root, ".env"):
        out.append(".env is not in .gitignore")
    need("README.md")
    need("CLAUDE.md")
    agents = root / "AGENTS.md"
    if not agents.is_symlink() or agents.resolve() != (root / "CLAUDE.md").resolve():
        out.append("AGENTS.md is not a symlink to CLAUDE.md")

    api, web = root / "api", root / "web"
    if not api.is_dir() and not web.is_dir():
        out.append("neither api/ nor web/ exists")
    if api.is_dir():
        for rel in ("api/pyproject.toml", "api/uv.lock", "api/src", "api/tests"):
            need(rel)
        if (api / "alembic").is_dir() and not any((root / c).is_file() for c in ("compose.yaml", "docker-compose.yml")):
            out.append("api/alembic/ exists but no compose.yaml for the local Postgres")
    if web.is_dir():
        for rel in ("web/package.json", "web/tsconfig.json", "web/components.json", "web/src/components/ui"):
            need(rel)
        if not any((root / p).is_file() for p in ("pnpm-lock.yaml", "web/pnpm-lock.yaml")):
            out.append("missing pnpm-lock.yaml (pnpm is the package manager)")
        if api.is_dir():
            need("web/src/api", " (generated OpenAPI types)")

    ci = root / ".github/workflows"
    if ci.is_dir():
        for wf in sorted(ci.glob("*.y*ml")):
            if "make gate" not in wf.read_text(encoding="utf-8"):
                out.append(f"{wf.relative_to(root)} doesn't run `make gate` (keep check logic in the Makefile)")
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    out = check(Path(argv[0]).resolve())
    print("\n".join(out) or "stack check: clean")
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
