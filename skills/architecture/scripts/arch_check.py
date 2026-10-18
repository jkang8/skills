#!/usr/bin/env python3
"""Fail on architecture smells a script can see: long files, grab-bag file names, import cycles. Stdlib only.

usage: arch_check.py <dir> [--exclude GLOB ...]
Python cycles come from `import` statements (imports under `if TYPE_CHECKING:` don't count); TS/JS
cycles come from relative `import ... from "./x"` (type-only imports don't count).
Exits 1 with `path: problem` per hit.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path, PurePath

MAX_LINES = 500
BANNED_STEMS = {"utils", "util", "helpers", "helper", "misc", "common"}
CODE = {".py", ".ts", ".tsx", ".js", ".jsx"}
SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "dist", "build", "__pycache__", "fixtures", "migrations", "alembic"}
TS_IMPORT = re.compile(r"""^\s*(?:import|export)\s+(?!type\b)[^'"]*?from\s+['"](\.{1,2}/[^'"]+)['"]|import\(\s*['"](\.{1,2}/[^'"]+)['"]\s*\)""", re.M)
TS_EXTS = (".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js")


def code_files(root: Path, exclude: list[str]) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.suffix in CODE and p.is_file() and not SKIP_DIRS & set(rel.parts) and not any(rel.match(g) for g in exclude):
            out.append(p)
    return out


def module_name(rel: PurePath) -> str:
    parts = list(rel.with_suffix("").parts)
    if parts and parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def py_imports(path: Path, mod: str, is_pkg: bool) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    skip: set[int] = set()
    for node in ast.walk(tree):  # imports guarded by TYPE_CHECKING don't run
        if isinstance(node, ast.If) and "TYPE_CHECKING" in ast.unparse(node.test):
            skip |= {id(n) for b in node.body for n in ast.walk(b)}
    names = []
    pkg = mod.split(".") if is_pkg else mod.split(".")[:-1]
    for node in ast.walk(tree):
        if id(node) in skip:
            continue
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = pkg[: len(pkg) - node.level + 1] if node.level else []
            stem = ".".join(base + ([node.module] if node.module else []))
            # Longest-prefix resolution maps `from pkg import name` to pkg.name if it's a module, else pkg.
            names += [f"{stem}.{a.name}" if stem else a.name for a in node.names]
    return names


def resolve(name: str, known: set[str]) -> str | None:
    parts = name.split(".")
    for i in range(len(parts), 0, -1):
        cand = ".".join(parts[:i])
        if cand in known:
            return cand
    return None


def ts_target(path: Path, spec: str, known: set[Path]) -> Path | None:
    base = (path.parent / spec).resolve()
    for cand in [base, *[Path(str(base) + e) for e in TS_EXTS]]:
        if cand in known:
            return cand
    return None


def cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Strongly connected components with more than one node (or a self-import), via Tarjan."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on: set[str] = set()
    out: list[list[str]] = []

    def visit(v: str) -> None:
        index[v] = low[v] = len(index)
        stack.append(v)
        on.add(v)
        for w in sorted(graph.get(v, ())):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1 or v in graph.get(v, ()):
                out.append(sorted(comp))

    for v in sorted(graph):
        if v not in index:
            visit(v)
    return out


def check(root: Path, exclude: list[str] | None = None) -> list[str]:
    files = code_files(root, exclude or [])
    hits = []
    for f in files:
        rel = f.relative_to(root)
        n = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        if n > MAX_LINES:
            hits.append(f"{rel.as_posix()}: {n} lines, over {MAX_LINES}; split by concept")
        if f.stem.lower() in BANNED_STEMS:
            hits.append(f"{rel.as_posix()}: grab-bag file name; name it for the concept it owns")

    py = {module_name(f.relative_to(root)): f for f in files if f.suffix == ".py"}
    known = set(py)
    graph = {m: {t for n in py_imports(f, m, f.name == "__init__.py") if (t := resolve(n, known)) and t != m} for m, f in py.items()}
    hits += [f"import cycle: {' -> '.join(c + [c[0]])}" for c in cycles(graph)]

    ts = {f.resolve() for f in files if f.suffix != ".py"}
    tgraph: dict[str, set[str]] = {}
    for f in ts:
        text = f.read_text(encoding="utf-8", errors="replace")
        deps = {ts_target(f, a or b, ts) for a, b in TS_IMPORT.findall(text)}
        tgraph[f.relative_to(root.resolve()).as_posix()] = {d.relative_to(root.resolve()).as_posix() for d in deps if d}
    hits += [f"import cycle: {' -> '.join(c + [c[0]])}" for c in cycles(tgraph)]
    return hits


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir", type=Path)
    ap.add_argument("--exclude", action="append", default=[], help="glob of paths to skip (repeatable)")
    a = ap.parse_args(argv)
    hits = check(a.dir.resolve(), a.exclude)
    print("\n".join(hits) or "arch check: clean")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
