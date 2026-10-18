#!/usr/bin/env python3
"""Stitch scene clips into one video with a caption band below the app, and write the .srt. Stdlib only.

usage: stitch.py CLIPS_DIR --out demo.mp4 [--srt demo.srt] [--order a,b,c] [--band 72] [--crossfade 0.2]
CLIPS_DIR holds <name>.mp4 and <name>.json per scene (see captions.py). Clips join in name order unless
--order says otherwise. The canvas is the clips' size plus a --band px dark strip at the bottom, and the
captions are burned into that strip from an ASS file, so they never cover the app. --crossfade is a dissolve
in seconds (0 = straight cuts; 0.15 to 0.25 reads as a cut that isn't jarring). Needs ffmpeg with libass.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import captions
import ffmpeg_cli

BAND_COLOR = "0x18181b"


def filter_graph(durations: list[float], *, width: int, height: int, band: int, ass_name: str,
                 crossfade: float = 0.0) -> str:
    """The filter_complex: join the inputs (concat, or a chain of xfades), pad the band, burn the ASS. Output [out]."""
    n = len(durations)
    if n == 1:
        joined = "[0:v]null[joined]"
    elif crossfade <= 0:
        joined = "".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0[joined]"
    else:
        steps, prev = [], "0:v"
        for i in range(1, n):
            offset = sum(durations[:i]) - i * crossfade
            label = "joined" if i == n - 1 else f"x{i}"
            steps.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={crossfade}:offset={offset:.3f}[{label}]")
            prev = label
        joined = ";".join(steps)
    return f"{joined};[joined]pad={width}:{height + band}:0:0:color={BAND_COLOR},ass={ass_name}[out]"


def build_args(inputs: list[Path], durations: list[float], out: Path, *, width: int, height: int, band: int,
               ass_name: str, crossfade: float = 0.0, crf: int = 18) -> list[str]:
    args: list[str] = []
    for p in inputs:
        args += ["-i", str(p)]
    graph = filter_graph(durations, width=width, height=height, band=band, ass_name=ass_name, crossfade=crossfade)
    return [*args, "-filter_complex", graph, "-map", "[out]", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", "-an", str(out)]


@dataclass(frozen=True)
class Stitched:
    video: Path
    seconds: float
    cues: list[captions.Cue]


def stitch(clips_dir: Path, out: Path, *, srt_path: Path | None = None, order: list[str] | None = None,
           band: int = 72, crossfade: float = 0.0, crf: int = 18, font: str = "Helvetica", size: int = 22) -> Stitched:
    clips_dir = clips_dir.resolve()  # ffmpeg runs from inside it, so a relative path would point at the wrong place
    names = order or sorted(p.stem for p in clips_dir.glob("*.json"))
    if not names:
        raise SystemExit(f"no clips (*.json) in {clips_dir}")
    clips = [captions.load_clip(clips_dir / f"{n}.json") for n in names]
    inputs = [clips_dir / f"{n}.mp4" for n in names]
    size_px = ffmpeg_cli.probe(inputs[0])
    cues = captions.timeline(clips, crossfade=crossfade)
    total_h = size_px.height + band
    ass_name = "captions.ass"
    (clips_dir / ass_name).write_text(captions.ass(cues, size_px.width, total_h, font=font, size=size,
                                                   margin_v=max(4, (band - size * 2) // 2),
                                                   margin_x=round(size_px.width * 0.1)), encoding="utf-8")
    if srt_path:
        srt_path.write_text(captions.srt(cues), encoding="utf-8")
    durations = [c.duration for c in clips]
    # The ass filter takes a bare file name, so run from the clips folder and avoid path escaping.
    ffmpeg_cli.run(build_args(inputs, durations, out.resolve(), width=size_px.width, height=size_px.height, band=band,
                              ass_name=ass_name, crossfade=crossfade, crf=crf), cwd=clips_dir)
    return Stitched(out, sum(durations) - crossfade * (len(clips) - 1), cues)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("clips_dir", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--srt", type=Path)
    ap.add_argument("--order", help="comma-separated clip names")
    ap.add_argument("--band", type=int, default=72)
    ap.add_argument("--crossfade", type=float, default=0.0)
    a = ap.parse_args(argv)
    if not ffmpeg_cli.has_filter("ass"):
        print("this ffmpeg has no `ass` filter (libass); captions can't be burned in", file=sys.stderr)
        return 2
    result = stitch(a.clips_dir, a.out, srt_path=a.srt, order=a.order.split(",") if a.order else None,
                    band=a.band, crossfade=a.crossfade)
    print(f"wrote {result.video} ({result.seconds:.1f}s, {len(result.cues)} captions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
