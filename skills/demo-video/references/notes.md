# Notes behind the rules

## Why one clip per scene
A single take through the whole flow means one slip in the last scene re-records all of it, and each scene's start depends on the one before. Separate clips cost a fresh page load per scene (trimmed from the video) and make every scene start from its own URL. `run_scenes.py --only` re-records one and re-stitches with the others' clips.

## Why the caption band is padded on, not drawn over the app
A caption over the UI covers the thing it describes, and a fixed position that is clear in one scene lands on a button in another. A 72 px strip below the app is never in the way. Pad the canvas (`pad=W:H+band`) and write the captions into the strip.

## Why ASS, not SRT with `force_style`
libass lays an SRT out on a default 288-line canvas and then scales to the video. `FontSize=22` on a 972 px video renders near 60 px, and margins scale the same way, so captions came out several lines tall and spilled over the app. An ASS file declares `PlayResX` and `PlayResY` as the real canvas, so `Fontsize` and margins are pixels. `captions.py` writes both from the same cues.

## Reading time
About 285 ms a word plus 800 ms, never under 2.6 s, is 3.5 words a second: slower than subtitle norms for film, because the viewer is also looking at a screen they haven't seen. `frame_check.py` flags a caption shown for less than that, with a 0.15 s tolerance (a cue ends 0.05 s before the next).

## What the frame check has caught
Each of these rendered without an error and was visible only in a frame beside its caption:
- captions at 60 px that wrapped over the app (the ASS point above);
- a side panel closed by the script before its caption had been read, so the caption described an empty list;
- a command palette that closed before the caption about its follow-up question was read;
- a long link that ran off the right edge of a panel;
- a caption that said a run had finished while the script had already clicked through to the next page.

One more was avoided rather than caught: after a table's default sort changed, a script that clicked the first row would have opened a different finding than its caption described. Select by role and text.

## Timeline with a crossfade
A dissolve of x seconds overlaps each clip with the next, so clip k starts at (sum of earlier durations) minus k times x, and the video is shorter by (clips - 1) times x. A caption that is still up during a dissolve would sit half over the next scene, so the last caption of a clip ends before it. That shortens it by the crossfade, so the clip needs a tail of at least that long after its last caption has been read; `frame_check.py` reports a caption cut short this way. `captions.timeline` does this; `stitch.py` builds the matching `xfade` chain.

## Sources
Known, not re-read for this skill: Playwright's video recording docs (`recordVideo`), the ASS format specification and libass, and the BBC subtitle guidelines for reading speed.
