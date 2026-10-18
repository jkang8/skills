#!/usr/bin/env python3
"""Record every scene as its own clip, then stitch. A broken scene is re-recorded alone. Stdlib only.

usage: run_scenes.py --scenes DIR --clips DIR --cmd "node {file}" --out demo.mp4 [--srt demo.srt]
                     [--only 03,04] [--no-stitch] [--ext .ts] [--band 72] [--crossfade 0.2]
Each file in --scenes (sorted by name; --ext filters; names starting with _ or . are skipped) is one scene. The
scene command runs with SCENE_CLIPS set to --clips and must leave <name>.mp4 and <name>.json there (the
contract in captions.py). --only re-records scenes whose name contains one of the comma-separated parts;
every other scene must already have a clip. A scene that fails or leaves a bad clip stops the run.
"""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

import captions
import stitch


def scene_files(scenes: Path, ext: str | None) -> list[Path]:
    return sorted(p for p in scenes.iterdir()
                  if p.is_file() and not p.name.startswith(("_", ".")) and (ext is None or p.suffix == ext))


def check_clip(clips: Path, name: str) -> list[str]:
    """Problems with a scene's clip: missing files, an empty duration, cues out of order or out of range, bad wording."""
    problems = []
    if not (clips / f"{name}.mp4").is_file():
        problems.append(f"{name}.mp4 is missing")
    meta = clips / f"{name}.json"
    if not meta.is_file():
        return [*problems, f"{name}.json is missing"]
    try:
        clip = captions.load_clip(meta)
    except (KeyError, ValueError) as e:
        return [*problems, f"{name}.json is not a clip file ({e})"]
    if clip.duration <= 0:
        problems.append("duration is not positive")
    starts = [c.start for c in clip.cues]
    if starts != sorted(starts):
        problems.append("cues are not in time order")
    problems += [f"cue at {c.start:.1f}s starts outside the clip" for c in clip.cues if not 0 <= c.start < clip.duration]
    for c in clip.cues:
        problems += [f"caption {c.text[:30]!r}: {p}" for p in captions.lint(c.text)]
    return problems


def selected(name: str, only: list[str] | None) -> bool:
    return only is None or any(part in name for part in only)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scenes", type=Path, required=True)
    ap.add_argument("--clips", type=Path, required=True)
    ap.add_argument("--cmd", required=True, help='scene command; {file} is the scene file, e.g. "node {file}"')
    ap.add_argument("--out", type=Path)
    ap.add_argument("--srt", type=Path)
    ap.add_argument("--only")
    ap.add_argument("--no-stitch", action="store_true")
    ap.add_argument("--ext")
    ap.add_argument("--band", type=int, default=72)
    ap.add_argument("--crossfade", type=float, default=0.0)
    a = ap.parse_args(argv)
    only = a.only.split(",") if a.only else None
    a.clips = a.clips.resolve()  # scene commands may run from another folder
    a.clips.mkdir(parents=True, exist_ok=True)

    files = scene_files(a.scenes, a.ext)
    if not files:
        print(f"no scene files in {a.scenes}", file=sys.stderr)
        return 1
    for f in files:
        name = f.stem
        if selected(name, only):
            proc = subprocess.run(shlex.split(a.cmd.format(file=str(f))), env={**os.environ, "SCENE_CLIPS": str(a.clips)})
            if proc.returncode != 0:
                print(f"scene {name} failed (exit {proc.returncode}); fix it and run again with --only {name}", file=sys.stderr)
                return 1
        problems = check_clip(a.clips, name)
        if problems:
            hint = "" if selected(name, only) else f" (no recorded clip: run once without --only, or with --only {name})"
            print(f"scene {name}: " + "; ".join(problems) + hint, file=sys.stderr)
            return 1
        clip = captions.load_clip(a.clips / f"{name}.json")
        print(f"{name}: {clip.duration:.1f}s, {len(clip.cues)} captions" + ("" if selected(name, only) else " (kept)"))
    if a.no_stitch:
        return 0
    if not a.out:
        print("--out is required unless --no-stitch", file=sys.stderr)
        return 1
    result = stitch.stitch(a.clips, a.out, srt_path=a.srt, order=[f.stem for f in files], band=a.band, crossfade=a.crossfade)
    print(f"wrote {result.video} ({result.seconds:.1f}s, {len(result.cues)} captions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
