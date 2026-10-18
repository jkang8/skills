#!/usr/bin/env python3
"""Fail on ui-design-system violations in a frontend tree. Stdlib only.

usage: design_lint.py <dir> [--tokens GLOB ...]
Tokens files (default: anything under a tokens/ folder, tokens.css, theme.css) may define colors and gradients.
A line containing `design-lint: ignore` is skipped. Exits 1 with `path:line: rule: text` per hit.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePath

EXTS = {".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".html", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", "dist", "build", ".git", ".next", "coverage", "public"}
DEFAULT_TOKENS = ["tokens/*", "tokens/**/*", "tokens.css", "theme.css"]
PALETTE = "slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose"
UTIL = "bg|text|border|ring|from|via|to|fill|stroke|outline|divide|placeholder|shadow|decoration|accent|caret"

# (rule, pattern, applies outside tokens only)
RULES = [
    ("hex color", re.compile(r"#[0-9a-fA-F]{3,8}\b(?![-\w])"), True),
    ("rgb/hsl color", re.compile(r"\b(?:rgba?|hsla?|oklch)\("), True),
    ("palette class", re.compile(rf"\b(?:{UTIL})-(?:{PALETTE})-\d{{2,3}}\b"), True),
    ("gradient", re.compile(r"\bbg-(?:gradient|linear|radial|conic)-|\b(?:linear|radial|conic)-gradient\("), True),
    ("rounded-2xl/3xl", re.compile(r"\brounded(?:-[trblse]{1,2})?-(?:2xl|3xl)\b"), False),
    ("gradient text", re.compile(r"\bbg-clip-text\b|background-clip:\s*text"), False),
    ("backdrop blur", re.compile(r"\bbackdrop-blur\b|backdrop-filter:"), False),
    ("transition-all", re.compile(r"\btransition-all\b|transition:\s*all\b"), False),
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF☀-➿⭐⭕]")
# UI libraries that only components/ui/ may wrap.
UI_IMPORT = re.compile(r"""from\s+['"](@radix-ui/|@mui/|@chakra-ui/|@headlessui/|@mantine/|antd\b|react-bootstrap\b|@nextui-org/)""")


def is_tokens(rel: PurePath, globs: list[str]) -> bool:
    parts = rel.parts
    return any(rel.match(g) or PurePath(*parts[i:]).match(g) for g in globs for i in range(len(parts)))


def lint_file(path: Path, rel: PurePath, tokens: bool) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    in_ui = "components/ui" in rel.as_posix()
    jsx = path.suffix in {".tsx", ".jsx"}
    hits = []
    for n, line in enumerate(lines, 1):
        if "design-lint: ignore" in line:
            continue
        where = f"{rel.as_posix()}:{n}"
        hits += [f"{where}: {rule}: {line.strip()}" for rule, pat, outside in RULES if pat.search(line) and not (outside and tokens)]
        if jsx and EMOJI.search(line):
            hits.append(f"{where}: emoji: {line.strip()}")
        if not in_ui and UI_IMPORT.search(line):
            hits.append(f"{where}: UI import outside components/ui: {line.strip()}")
    return hits


def lint(root: Path, token_globs: list[str]) -> list[str]:
    hits = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.suffix not in EXTS or not path.is_file() or SKIP_DIRS & set(rel.parts):
            continue
        hits += lint_file(path, rel, is_tokens(rel, token_globs))
    return hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir", type=Path)
    ap.add_argument("--tokens", action="append", help="glob for tokens files (repeatable)")
    a = ap.parse_args(argv)
    hits = lint(a.dir.resolve(), a.tokens or DEFAULT_TOKENS)
    print("\n".join(hits) or "design lint: clean")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
