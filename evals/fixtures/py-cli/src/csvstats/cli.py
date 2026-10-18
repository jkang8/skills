"""csvstats: per-column summary statistics for a CSV file."""
from __future__ import annotations

import argparse
import csv
import statistics
import sys


def summarize(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for col in rows[0] if rows else []:
        try:
            vals = [float(r[col]) for r in rows if r[col] != ""]
        except ValueError:
            continue  # non-numeric columns are skipped, not reported
        if vals:
            out[col] = {"count": len(vals), "mean": statistics.fmean(vals), "min": min(vals), "max": max(vals)}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="csvstats", description="Per-column stats for numeric CSV columns.")
    ap.add_argument("path", help="CSV file with a header row")
    ap.add_argument("--delimiter", default=",")
    a = ap.parse_args(argv)
    with open(a.path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter=a.delimiter))
    for col, s in summarize(rows).items():
        print(f"{col}\tcount={s['count']:.0f}\tmean={s['mean']:.2f}\tmin={s['min']:g}\tmax={s['max']:g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
