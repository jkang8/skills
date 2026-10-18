import contextlib
import io
import shlex
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import captions  # noqa: E402
import ffmpeg_cli  # noqa: E402
import run_scenes  # noqa: E402

# A scene that only writes the contract files, so the runner's logic is tested without a browser or ffmpeg.
FAKE = """import json, os
from pathlib import Path
name = Path(__file__).stem
out = Path(os.environ["SCENE_CLIPS"])
(out / f"{name}.mp4").write_bytes(b"x")
(out / f"{name}.json").write_text(json.dumps({"name": name, "duration": 5.0, "cues": [{"start": 0.0, "text": %r}]}))
"""
REAL = """import sys
sys.path.insert(0, %r)
import json, os
from pathlib import Path
import clip_fixtures
name = Path(__file__).stem
clip_fixtures.make_clip(Path(os.environ["SCENE_CLIPS"]), name, 4.0, "0x203050", [(0.0, "Caption for " + name)])
"""


class Runner(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.scenes = Path(self._tmp.name) / "scenes"
        self.clips = Path(self._tmp.name) / "clips"
        self.scenes.mkdir()

    def scene(self, name, body=None, caption="Totals link to their records."):
        (self.scenes / f"{name}.py").write_text(body if body is not None else FAKE % caption, encoding="utf-8")

    def run_main(self, *extra):
        cmd = f"{shlex.quote(sys.executable)} {{file}}"
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = run_scenes.main(["--scenes", str(self.scenes), "--clips", str(self.clips), "--cmd", cmd, *extra])
        return code, err.getvalue()

    def test_records_every_scene_in_name_order(self):
        for n in ("02-b", "01-a"):
            self.scene(n)
        self.assertEqual(self.run_main("--no-stitch")[0], 0)
        self.assertEqual(sorted(p.name for p in self.clips.glob("*.json")), ["01-a.json", "02-b.json"])

    def test_only_re_records_the_named_scene_and_keeps_the_rest(self):
        self.scene("01-a")
        self.scene("02-b")
        self.run_main("--no-stitch")
        keep = (self.clips / "01-a.json").read_text()
        self.scene("02-b", caption="Detail view lists every source record.")
        self.assertEqual(self.run_main("--only", "02", "--no-stitch")[0], 0)
        self.assertEqual((self.clips / "01-a.json").read_text(), keep)
        self.assertIn("Detail view", (self.clips / "02-b.json").read_text())

    def test_only_without_a_recorded_clip_for_the_others_is_an_error(self):
        self.scene("01-a")
        self.scene("02-b")
        code, err = self.run_main("--only", "02", "--no-stitch")
        self.assertEqual(code, 1)
        self.assertIn("01-a", err)
        self.assertIn("no recorded clip", err)

    def test_a_failing_scene_stops_the_run_and_names_the_fix(self):
        self.scene("01-a", body="raise SystemExit(3)")
        self.scene("02-b")
        code, err = self.run_main("--no-stitch")
        self.assertEqual(code, 1)
        self.assertIn("scene 01-a failed (exit 3)", err)
        self.assertIn("--only 01-a", err)
        self.assertFalse((self.clips / "02-b.json").exists())

    def test_a_scene_that_leaves_no_clip_is_an_error(self):
        self.scene("01-a", body="pass")
        code, err = self.run_main("--no-stitch")
        self.assertEqual(code, 1)
        self.assertIn("01-a.json is missing", err)

    def test_clip_checks_catch_hype_and_cues_outside_the_clip(self):
        self.scene("01-a", caption="A seamless way to unlock value.")
        code, err = self.run_main("--no-stitch")
        self.assertEqual(code, 1)
        self.assertIn("hype word 'seamless'", err)
        self.clips.mkdir(exist_ok=True)
        (self.clips / "x.mp4").write_bytes(b"x")
        (self.clips / "x.json").write_text('{"name": "x", "duration": 3, "cues": [{"start": 4, "text": "Late."}]}')
        self.assertIn("starts outside the clip", run_scenes.check_clip(self.clips, "x")[0])

    def test_files_starting_with_an_underscore_are_not_scenes(self):
        self.scene("01-a")
        (self.scenes / "_shared.py").write_text("raise SystemExit(9)")
        self.assertEqual(self.run_main("--no-stitch")[0], 0)

    @unittest.skipUnless(ffmpeg_cli.can_burn_captions(), "needs ffmpeg with libass (set FFMPEG or put it on PATH)")
    def test_records_then_stitches_into_one_video_and_srt(self):
        for n in ("01-a", "02-b"):
            self.scene(n, body=REAL % str(HERE))
        out, srt = Path(self._tmp.name) / "demo.mp4", Path(self._tmp.name) / "demo.srt"
        code, err = self.run_main("--out", str(out), "--srt", str(srt), "--band", "40")
        self.assertEqual(code, 0, err)
        self.assertAlmostEqual(ffmpeg_cli.probe(out).seconds, 8.0, delta=0.2)
        self.assertEqual([c.text for c in captions.parse_srt(srt.read_text())], ["Caption for 01-a", "Caption for 02-b"])


if __name__ == "__main__":
    unittest.main()
