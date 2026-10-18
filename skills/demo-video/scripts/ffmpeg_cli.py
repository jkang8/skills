"""Find and run ffmpeg, and read a video's size and length. Stdlib only."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


def ffmpeg_path() -> str | None:
    """$FFMPEG if set, else ffmpeg on PATH, else None."""
    return os.environ.get("FFMPEG") or shutil.which("ffmpeg")


def require_ffmpeg() -> str:
    path = ffmpeg_path()
    if not path:
        raise SystemExit("ffmpeg not found: put it on PATH or set FFMPEG to its full path")
    return path


def run(args: list[str], cwd: Path | None = None) -> None:
    """Run ffmpeg quietly with -y; raise RuntimeError carrying ffmpeg's own message on failure."""
    proc = subprocess.run([require_ffmpeg(), "-y", "-loglevel", "error", *args], cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.strip()}")


def has_filter(name: str) -> bool:
    """True when this ffmpeg build has the named filter (the `ass` filter needs libass)."""
    out = subprocess.run([require_ffmpeg(), "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return any(re.match(rf"\s*\S+\s+{re.escape(name)}\s", line) for line in out.splitlines())


def can_burn_captions() -> bool:
    """True when ffmpeg is present with the filters stitching needs (ass from libass, xfade, pad)."""
    return ffmpeg_path() is not None and all(has_filter(f) for f in ("ass", "xfade", "pad"))


@dataclass(frozen=True)
class Probe:
    width: int
    height: int
    seconds: float


def probe(video: Path) -> Probe:
    """Size and length from `ffmpeg -i`, which exits 1 for lack of an output file but prints both."""
    text = subprocess.run([require_ffmpeg(), "-hide_banner", "-i", str(video)], capture_output=True, text=True).stderr
    length = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", text)
    size = re.search(r",\s*(\d{2,5})x(\d{2,5})\b", text)
    if not length or not size:
        raise RuntimeError(f"could not read size and duration of {video}")
    h, m, s = length.groups()
    return Probe(int(size.group(1)), int(size.group(2)), int(h) * 3600 + int(m) * 60 + float(s))


def frame_gray(video: Path, at: float, crop: str | None = None) -> bytes:
    """One frame at `at` seconds as raw 8-bit gray, optionally cropped (`w:h:x:y`); for checking pixels."""
    vf = f"crop={crop}," if crop else ""
    proc = subprocess.run(
        [require_ffmpeg(), "-loglevel", "error", "-ss", f"{at:.3f}", "-i", str(video), "-frames:v", "1",
         "-vf", f"{vf}format=gray", "-f", "rawvideo", "-"],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout
