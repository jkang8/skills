#!/usr/bin/env python3
"""Check a captioned demo: caption timing, total length, and one frame inside every caption. Stdlib only.

usage: frame_check.py VIDEO SRT [--out frames] [--min 60] [--max 90] [--no-frames]
Prints a problem for each caption that leaves before it can be read, is too long, has hype or emoji, or overlaps
the next, and for a video outside --min/--max seconds. Then writes one frame per caption (60% of the way into
it, at most 2.2s in) and tiles them six to a contact sheet, frames/sheet-N.png. The sheets are for you to look
at: every frame must show what its caption says. Exits 1 on any timing problem; the look is not automatable.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import captions
import ffmpeg_cli

TOLERANCE = 0.15  # seconds a caption may fall short of its reading time (cues end 0.05s before the next)
PER_SHEET = 6


def sample_time(cue: captions.Cue) -> float:
    return cue.start + min(2.2, (cue.end - cue.start) * 0.6)


def check_timing(cues: list[captions.Cue], seconds: float | None, lo: float = 60, hi: float = 90) -> list[str]:
    problems = []
    if seconds is not None and not lo <= seconds <= hi:
        problems.append(f"video is {seconds:.1f}s; aim for {lo:g} to {hi:g}")
    for i, c in enumerate(cues, 1):
        shown, need = c.end - c.start, captions.reading_seconds(c.text)
        if shown + TOLERANCE < need:
            problems.append(f"caption {i} is on screen {shown:.1f}s and needs {need:.1f}s to read")
        problems += [f"caption {i}: {p}" for p in captions.lint(c.text)]
        if i > 1 and c.start < cues[i - 2].end - 1e-6:
            problems.append(f"caption {i} starts before caption {i - 1} ends")
    return problems


def extract(video: Path, cues: list[captions.Cue], out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(cues, 1):
        ffmpeg_cli.run(["-ss", f"{sample_time(c):.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=960:-1",
                        str(out / f"{i:02}.png")])
    sheets = []
    for start in range(0, len(cues), PER_SHEET):
        rows = -(-min(PER_SHEET, len(cues) - start) // 2)
        sheet = out / f"sheet-{start // PER_SHEET + 1}.png"
        ffmpeg_cli.run(["-framerate", "1", "-start_number", str(start + 1), "-i", str(out / "%02d.png"),
                        "-frames:v", "1", "-vf", f"tile=2x{rows}", str(sheet)])
        sheets.append(sheet)
    return sheets


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video", type=Path)
    ap.add_argument("srt", type=Path)
    ap.add_argument("--out", type=Path, default=Path("frames"))
    ap.add_argument("--min", type=float, default=60)
    ap.add_argument("--max", type=float, default=90)
    ap.add_argument("--no-frames", action="store_true", help="timing checks only; no ffmpeg needed")
    a = ap.parse_args(argv)
    cues = captions.parse_srt(a.srt.read_text(encoding="utf-8"))
    seconds = None if a.no_frames else ffmpeg_cli.probe(a.video).seconds
    problems = check_timing(cues, seconds, a.min, a.max)
    for p in problems:
        print(f"PROBLEM: {p}")
    if not a.no_frames:
        for sheet in extract(a.video, cues, a.out):
            print(f"look at {sheet}")
        print(f"{len(cues)} captions; check every frame against its caption")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
