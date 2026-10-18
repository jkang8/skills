import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import captions  # noqa: E402
import clip_fixtures  # noqa: E402
import ffmpeg_cli  # noqa: E402
import frame_check  # noqa: E402
import stitch  # noqa: E402

C = captions.Cue


class Timing(unittest.TestCase):
    def test_a_frame_is_sampled_inside_the_caption_and_never_past_two_seconds_in(self):
        self.assertAlmostEqual(frame_check.sample_time(C(10.0, 12.0, "x")), 11.2)
        self.assertAlmostEqual(frame_check.sample_time(C(10.0, 20.0, "x")), 12.2)

    def test_clean_cues_pass(self):
        cues = [C(0.0, 4.0, "Totals link to the records behind them."), C(4.05, 8.0, "Detail view lists every record.")]
        self.assertEqual(frame_check.check_timing(cues, 75.0), [])

    def test_a_caption_that_leaves_before_it_can_be_read_is_flagged(self):
        problems = frame_check.check_timing([C(0.0, 1.5, "Totals link to the records behind them.")], None)
        self.assertEqual(problems, ["caption 1 is on screen 1.5s and needs 2.8s to read"])

    def test_a_caption_within_the_tolerance_of_its_reading_time_passes(self):
        self.assertEqual(frame_check.check_timing([C(0.0, 2.5, "Two words")], None), [])

    def test_length_wording_and_overlap_are_flagged(self):
        cues = [C(0.0, 4.0, "A seamless flow."), C(3.0, 8.0, "Fine caption text here.")]
        problems = frame_check.check_timing(cues, None)
        self.assertIn("caption 1: hype word 'seamless'", problems)
        self.assertIn("caption 2 starts before caption 1 ends", problems)

    def test_total_length_is_held_to_the_range(self):
        self.assertEqual(frame_check.check_timing([], 59.0), ["video is 59.0s; aim for 60 to 90"])
        self.assertEqual(frame_check.check_timing([], 91.0), ["video is 91.0s; aim for 60 to 90"])
        self.assertEqual(frame_check.check_timing([], 60.0), [])


@unittest.skipUnless(ffmpeg_cli.can_burn_captions(), "needs ffmpeg with libass (set FFMPEG or put it on PATH)")
class Frames(unittest.TestCase):
    def test_writes_one_frame_per_caption_and_contact_sheets_of_six(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            cues = [(i * 0.5, f"Caption number {i}") for i in range(4)]
            clip_fixtures.make_clip(d, "a", 8.0, "0x203050", cues)
            clip_fixtures.make_clip(d, "b", 8.0, "0x305020", [(0.0, "Last caption here.")])
            out = d / "out.mp4"
            stitch.stitch(d, out, srt_path=d / "out.srt", band=40, size=16)
            with contextlib.redirect_stdout(io.StringIO()):
                frame_check.main([str(out), str(d / "out.srt"), "--out", str(d / "frames"), "--min", "1", "--max", "100"])
            frames = sorted(p.name for p in (d / "frames").glob("*.png"))
            self.assertEqual(frames, ["01.png", "02.png", "03.png", "04.png", "05.png", "sheet-1.png"])


if __name__ == "__main__":
    unittest.main()
