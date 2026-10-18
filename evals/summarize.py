#!/usr/bin/env python3
"""Turn run.sh's per-run result lines into the with/without table and the results.log lines. Stdlib only.

usage: summarize.py <skill> <agent-model> <judge-model> <results.log> < result lines
Each input line: `<task> <arm> <run> <check-hits or -> <judge score like 7/10, or ?>`.
"""
from __future__ import annotations

import collections
import datetime
import sys


def mean(xs: list[str]) -> str:
    nums = [float(x) for x in xs if x not in ("-", "?")]
    return f"{sum(nums) / len(nums):.1f}" if nums else "-"


def aggregate(runs: list[tuple[str, str]]) -> tuple[str, str]:
    """(mean check hits, mean judge score as 'a/b(p%)') over one task and arm's runs."""
    scores = [s.split("/") for _, s in runs if s != "?"]
    if not scores:
        return mean([h for h, _ in runs]), "?"
    pct = mean([str(100 * int(a) / int(b)) for a, b in scores])
    return mean([h for h, _ in runs]), f"{mean([a for a, _ in scores])}/{scores[0][1]}({pct}%)"


def summarize(lines: list[str], skill: str, model: str, judge: str, day: str) -> tuple[list[str], list[str]]:
    rows: dict[tuple[str, str], list[tuple[str, str]]] = collections.defaultdict(list)
    for line in lines:
        if line.strip():
            task, arm, _, hits, score = line.split()
            rows[(task, arm)].append((hits, score))
    table = ["| task | check hits without | check hits with | judge without | judge with |", "|---|---|---|---|---|"]
    log = []
    for task in sorted({t for t, _ in rows}):
        (hw, jw), (hh, jh) = aggregate(rows[(task, "without")]), aggregate(rows[(task, "with")])
        table.append(f"| {task} | {hw} | {hh} | {jw} | {jh} |")
        log.append(f"{day} {skill} {task} model={model} judge={judge} n={len(rows[(task, 'with')])} "
                   f"hits_without={hw} hits_with={hh} judge_without={jw} judge_with={jh}")
    return table, log


if __name__ == "__main__":
    skill, model, judge, log_path = sys.argv[1:5]
    table, log = summarize(sys.stdin.read().splitlines(), skill, model, judge, datetime.date.today().isoformat())
    print("\n".join(table))
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("".join(line + "\n" for line in log))
