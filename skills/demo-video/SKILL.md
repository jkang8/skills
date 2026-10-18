---
name: demo-video
description: "Use when recording an app demo: storyboard, clips, captions."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [demo, video, playwright, ffmpeg, captions, screen-recording]
    related_skills: [ui-design-system, doc-writing]
---

# Demo video

## When to use
A 60 to 90 second captioned walkthrough of a running app, for someone who will watch it without you: a stakeholder, a customer, a PR reviewer. Not narrated tutorials, marketing edits, or anything with real user data.

## Local overrides
If `demo-video.local.md` exists in this skill's folder or in `overrides/` at the root of the checkout this skill came from (resolve symlinks to find it), read it first. Its values fill the `<placeholders>` here; its rules add to these and win on conflict.

## Method
1. **Storyboard first, no code.** 5 to 7 scenes. Each makes one point and gets a caption for each beat of it (usually one to four), written before any script. Read the captions in order: muted, they should still tell the story. Cut a scene with no point.
2. **Record last.** Land the UI, theme, data and copy changes first; re-record after any change a scene shows.
3. **One script per scene**, each recording its own clip (see Scenes). A broken scene is re-recorded alone.
4. **Stitch** the clips with the caption band, and write the `.srt` from the same cues.
5. **Frame check** every caption, fix, and re-record only the scenes that failed.
6. Report the video path, its length and what you cut.

## Scenes
- A scene opens its own URL and builds its own state. It never depends on the previous scene, or re-recording one would break the next.
- Fixed viewport (1440×900), seeded synthetic data, storage cleared at the start, one theme unless the scene is about theme.
- Select by role and visible text, never by position: tables re-sort and the first row changes.
- Move like a person. Headless video draws no pointer, so inject a cursor and a click ring; move in 6 to 18 steps, pause about 250 ms before a click and 400 to 900 ms after.
- Call `start()` only once the first screen has rendered, so blank lead-in frames are trimmed.
- Show a caption while its action happens. Before closing or leaving what a caption describes, wait out its reading time (`hold`).
- Hold a finished state long enough to read it: a run that ends, a toast, a filtered table. End the clip a beat after the last caption has been read (the template adds 300 ms) or a crossfade cuts that caption short.
- Synthetic data only. Never record a real person's data, a real token, or a URL with a real ID in it.

`references/scene-lib.example.ts` is a runnable scene library (cursor, `say`, `hold`, clip and cue output); `references/scene.example.ts` is one scene using it.

## Captions
- Say what the viewer is looking at, with the number: "Recoverable now: $24,087. Each dollar traces to a signed note." One or two lines, at most 110 characters. Plain sentences, no hype words, no emoji.
- State the demo's limits once, in the last caption ("All data is synthetic. The rules are not yet verified.").
- Reading time is about 285 ms a word plus 800 ms, never under 2.6 s. The clip waits for it.
- The band sits below the app: pad the canvas about 72 px with a dark strip and put the text in it. A caption over the UI hides what it describes.
- The band follows the `ui-design-system` banned list: a flat dark strip, plain sans text, no gradient, glass, emoji or sparkle.
- Burn captions from an ASS file, not SRT with `force_style`. libass lays an SRT out on a 288-line canvas, so size 22 renders near 60 px on a 972 px video. ASS declares its canvas, so sizes are pixels. Ship the `.srt` too.

## Scripts
Stdlib Python; ffmpeg with libass on PATH or at `$FFMPEG`. The scene command is yours (`node scene.ts`, `python scene.py`). The contract is two files per scene in `$SCENE_CLIPS`: `<name>.mp4` and `<name>.json` (`{"name", "duration", "cues": [{"start", "text"}]}`, seconds from the clip start).
- `scripts/run_scenes.py --scenes DIR --clips DIR --cmd "node {file}" --out demo.mp4 --srt demo.srt` records every scene and stitches. `--only 03` re-records one; `--no-stitch` stops after recording. It stops at a scene that fails or leaves a clip with bad cues or wording.
- `scripts/stitch.py CLIPS --out demo.mp4 --srt demo.srt [--band 72] [--crossfade 0.2]` joins clips by name, straight cuts or a 150 to 250 ms dissolve, and burns the captions into the band.
- `scripts/captions.py`: the cue timeline (it accounts for crossfade overlap), SRT and ASS writers, reading time and the wording lint. Import it; it has no command line.
- `scripts/frame_check.py VIDEO SRT` prints timing problems and writes a contact sheet of one frame per caption.
- `scripts/test_*.py` are the fixture tests. The ones that need ffmpeg skip without it, so set `FFMPEG` to run them all.

## Frame check
Run `scripts/frame_check.py demo.mp4 demo.srt`, open every sheet, and compare each frame with its caption. It exists because each of these survived a clean render: captions several lines tall over the app, a side panel closed before its caption was read, a palette closed before its question was readable, a link running off a panel, a caption that said "finished" over the next page. One wrong frame means fixing that scene and re-recording only it. The exit code covers timing; whether a frame matches its caption is your call (`references/notes.md`).

## Checklist
1. The storyboard has 5 to 7 scenes, each with one point and its captions, and the muted video tells the story.
2. Every scene runs alone (`--only`) and leaves its clip and cues.
3. Captions sit in the band, read at 285 ms a word plus a beat, say what is on screen, and have no hype or emoji.
4. `frame_check.py` prints no problem, and every frame was looked at.
5. Length 60 to 90 s, canvas app width by (app height + band), `.srt` shipped.
6. Data is synthetic and the last caption states the demo's limits.
7. The report gives the video path, its length, and anything cut.

Sources and why each rule exists: `references/notes.md`.
