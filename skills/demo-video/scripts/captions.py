"""Caption cues for a stitched demo: timing, reading time, SRT and ASS output, and a lint. Stdlib only.

A scene records its cues relative to its own clip (`{"name", "duration", "cues": [{"start", "text"}]}`).
`timeline` moves them onto the stitched video's clock. ASS, not SRT, is what gets burned in: libass lays an
SRT out on a 288-line canvas, so `FontSize=22` in `force_style` renders near 60px on a 972px-high video.
An ASS file declares its own canvas (PlayResX/PlayResY), so sizes and margins are real pixels.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

READING_FLOOR = 2.6  # seconds: no caption is shown for less
PER_WORD = 0.285  # seconds a word needs, about 3.5 words a second
READING_PAD = 0.8  # a beat to look at the screen first
MAX_CHARS = 110  # one or two short lines

HYPE = ("seamless", "effortless", "powerful", "revolutionary", "game-changing", "cutting-edge", "ai-powered",
        "magic", "unlock", "supercharge", "next-generation", "blazing", "world-class", "best-in-class")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆✅]")


@dataclass(frozen=True)
class ClipCue:
    start: float  # seconds from the clip's first frame
    text: str


@dataclass(frozen=True)
class Clip:
    name: str
    duration: float
    cues: tuple[ClipCue, ...]


@dataclass(frozen=True)
class Cue:
    start: float  # seconds on the stitched video's clock
    end: float
    text: str


def reading_seconds(text: str) -> float:
    return max(READING_FLOOR, len(text.split()) * PER_WORD + READING_PAD)


def load_clip(path: Path) -> Clip:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Clip(data["name"], float(data["duration"]), tuple(ClipCue(float(c["start"]), c["text"]) for c in data["cues"]))


def timeline(clips: list[Clip], crossfade: float = 0.0, gap: float = 0.05) -> list[Cue]:
    """Cues on the stitched clock. Each ends `gap` before the next in its clip; the last leaves before the dissolve.

    A crossfade of x seconds overlaps each clip with the next, so clip k starts at (sum of earlier durations) - k*x.
    """
    cues: list[Cue] = []
    offset = 0.0
    for k, clip in enumerate(clips):
        offset = sum(c.duration for c in clips[:k]) - k * crossfade
        tail = max(gap, crossfade)
        for i, cue in enumerate(clip.cues):
            end = clip.cues[i + 1].start - gap if i + 1 < len(clip.cues) else clip.duration - tail
            cues.append(Cue(offset + cue.start, offset + end, cue.text))
    return cues


def _srt_time(s: float) -> str:
    ms = max(0, round(s * 1000))
    return f"{ms // 3600000:02}:{ms % 3600000 // 60000:02}:{ms % 60000 // 1000:02},{ms % 1000:03}"


def srt(cues: list[Cue]) -> str:
    return "\n".join(f"{i}\n{_srt_time(c.start)} --> {_srt_time(c.end)}\n{c.text}\n" for i, c in enumerate(cues, 1))


def parse_srt(text: str) -> list[Cue]:
    cues = []
    for block in text.strip().split("\n\n"):
        lines = block.split("\n")
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", lines[1])
        if not m:
            raise ValueError(f"bad SRT block: {block!r}")
        a, b, c, d, e, f, g, h = (int(x) for x in m.groups())
        cues.append(Cue(a * 3600 + b * 60 + c + d / 1000, e * 3600 + f * 60 + g + h / 1000, " ".join(lines[2:])))
    return cues


def _ass_time(s: float) -> str:
    cs = max(0, round(s * 100))
    return f"{cs // 360000}:{cs % 360000 // 6000:02}:{cs % 6000 // 100:02}.{cs % 100:02}"


def ass(cues: list[Cue], width: int, height: int, *, font: str = "Helvetica", size: int = 22,
        margin_v: int = 10, margin_x: int = 140) -> str:
    """An ASS file on a `width` x `height` canvas: white text, bottom-centre, `margin_v` px above the bottom edge."""
    def clean(t: str) -> str:
        return t.replace("{", "(").replace("}", ")").replace("\n", "\\N")

    head = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {width}", f"PlayResY: {height}", "WrapStyle: 0",
        "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        f"Style: Default,{font},{size},&H00FAFAFA,&H00FAFAFA,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,"
        f"{margin_x},{margin_x},{margin_v},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    body = [f"Dialogue: 0,{_ass_time(c.start)},{_ass_time(c.end)},Default,,0,0,0,,{clean(c.text)}" for c in cues]
    return "\n".join([*head, *body, ""])


def lint(text: str) -> list[str]:
    """Problems with one caption's wording: too long, emoji, or hype."""
    problems = []
    if len(text) > MAX_CHARS:
        problems.append(f"{len(text)} characters (max {MAX_CHARS})")
    if EMOJI.search(text):
        problems.append("emoji")
    lower = text.lower()
    problems += [f"hype word '{w}'" for w in HYPE if w in lower]
    return problems
