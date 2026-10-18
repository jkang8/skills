import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import captions  # noqa: E402
import clip_fixtures  # noqa: E402
import ffmpeg_cli  # noqa: E402
import stitch  # noqa: E402

GRAPH = dict(width=320, height=180, band=40, ass_name="c.ass")


class FilterGraph(unittest.TestCase):
    def test_straight_cuts_concat_then_pad_and_burn(self):
        g = stitch.filter_graph([2.0, 2.0], **GRAPH)
        self.assertEqual(g, "[0:v][1:v]concat=n=2:v=1:a=0[joined];"
                            "[joined]pad=320:220:0:0:color=0x18181b,ass=c.ass[out]")

    def test_one_clip_needs_no_join(self):
        self.assertTrue(stitch.filter_graph([2.0], **GRAPH).startswith("[0:v]null[joined];"))

    def test_crossfade_offsets_account_for_each_earlier_overlap(self):
        g = stitch.filter_graph([2.0, 2.0, 3.0], crossfade=0.3, **GRAPH)
        self.assertIn("[0:v][1:v]xfade=transition=fade:duration=0.3:offset=1.700[x1]", g)
        self.assertIn("[x1][2:v]xfade=transition=fade:duration=0.3:offset=3.400[joined]", g)

    def test_args_list_every_input_then_the_graph_then_the_output(self):
        args = stitch.build_args([Path("/c/a.mp4"), Path("/c/b.mp4")], [2.0, 2.0], Path("/o/d.mp4"), **GRAPH)
        self.assertEqual(args[:4], ["-i", "/c/a.mp4", "-i", "/c/b.mp4"])
        self.assertEqual(args[-1], "/o/d.mp4")
        self.assertIn("[out]", args)


@unittest.skipUnless(ffmpeg_cli.can_burn_captions(), "needs ffmpeg with libass (set FFMPEG or put it on PATH)")
class Stitching(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        clip_fixtures.make_clip(self.dir, "a", 2.0, "0x203050", [(0.0, "Short caption here")])
        clip_fixtures.make_clip(self.dir, "b", 2.0, "0x305020", [(0.0, "Second caption")])
        self.addCleanup(self._tmp.cleanup)

    def run_stitch(self, **kw):
        out = self.dir / "out.mp4"
        result = stitch.stitch(self.dir, out, srt_path=self.dir / "out.srt", band=40, size=16, **kw)
        return out, result

    def test_canvas_is_the_app_plus_the_band_and_length_is_the_sum(self):
        out, result = self.run_stitch()
        p = ffmpeg_cli.probe(out)
        self.assertEqual((p.width, p.height), (320, 220))
        self.assertAlmostEqual(p.seconds, 4.0, delta=0.2)
        self.assertAlmostEqual(result.seconds, 4.0)

    def test_a_relative_clips_folder_works(self):
        # ffmpeg runs from inside the clips folder, so a relative "work/a.mp4" would resolve to "work/work/a.mp4"
        work = self.dir / "work"
        work.mkdir()
        for f in list(self.dir.glob("[ab].*")):
            f.rename(work / f.name)
        before = Path.cwd()
        os.chdir(self.dir)
        self.addCleanup(os.chdir, before)
        stitch.stitch(Path("work"), Path("rel.mp4"), band=40, size=16)
        self.assertTrue((self.dir / "rel.mp4").is_file())

    def test_crossfade_shortens_the_video_by_the_overlap(self):
        out, _ = self.run_stitch(crossfade=0.4)
        self.assertAlmostEqual(ffmpeg_cli.probe(out).seconds, 3.6, delta=0.2)

    def test_captions_are_burned_into_the_band_and_nowhere_else(self):
        out, _ = self.run_stitch()
        band = ffmpeg_cli.frame_gray(out, 1.0, crop="320:40:0:180")
        app = ffmpeg_cli.frame_gray(out, 1.0, crop="320:180:0:0")
        self.assertGreater(max(band), 200, "no caption text in the band")
        self.assertLess(max(app), 120, "caption text reached the app area")

    def test_srt_sidecar_matches_the_burned_cues(self):
        _, result = self.run_stitch()
        written = captions.parse_srt((self.dir / "out.srt").read_text(encoding="utf-8"))
        self.assertEqual([c.text for c in written], [c.text for c in result.cues])


if __name__ == "__main__":
    unittest.main()
