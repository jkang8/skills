"""Build tiny scene clips (a solid-colour video plus its cue file) for the tests. Stdlib only."""
from __future__ import annotations

import json
from pathlib import Path

import ffmpeg_cli

SIZE = "320x180"


def make_clip(folder: Path, name: str, seconds: float, color: str, cues: list[tuple[float, str]]) -> None:
    """Write <name>.mp4 (SIZE, 30fps, `seconds` long) and <name>.json (the contract captions.load_clip reads)."""
    ffmpeg_cli.run(["-f", "lavfi", "-i", f"color=c={color}:s={SIZE}:r=30:d={seconds}", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", str(folder / f"{name}.mp4")])
    meta = {"name": name, "duration": seconds, "cues": [{"start": s, "text": t} for s, t in cues]}
    (folder / f"{name}.json").write_text(json.dumps(meta), encoding="utf-8")
