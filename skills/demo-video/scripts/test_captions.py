import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import captions  # noqa: E402

CLIPS = [captions.load_clip(HERE / "fixtures" / "clips" / f) for f in ("01-intro.json", "02-detail.json")]


class Timeline(unittest.TestCase):
    def test_second_clip_starts_when_the_first_ends(self):
        cues = captions.timeline(CLIPS)
        got = [(round(c.start, 2), round(c.end, 2)) for c in cues]
        # each cue ends 0.05s before the next one in its clip; the last in a clip ends 0.05s before the clip does
        self.assertEqual(got, [(0.0, 3.95), (4.0, 9.95), (10.5, 17.95)])

    def test_crossfade_pulls_later_clips_earlier_and_ends_captions_before_the_dissolve(self):
        cues = captions.timeline(CLIPS, crossfade=0.4)
        got = [(round(c.start, 2), round(c.end, 2)) for c in cues]
        self.assertEqual(got, [(0.0, 3.95), (4.0, 9.6), (10.1, 17.2)])


class Formats(unittest.TestCase):
    cues = [captions.Cue(3.2, 7.05, "A {braced} caption"), captions.Cue(3725.5, 3730.0, "Later")]

    def test_srt_timecodes_and_numbering(self):
        text = captions.srt(self.cues)
        self.assertIn("1\n00:00:03,200 --> 00:00:07,050\nA {braced} caption\n", text)
        self.assertIn("2\n01:02:05,500 --> 01:02:10,000\nLater\n", text)

    def test_srt_round_trips(self):
        back = captions.parse_srt(captions.srt(self.cues))
        self.assertEqual([(c.start, c.end, c.text) for c in back], [(c.start, c.end, c.text) for c in self.cues])

    def test_ass_declares_its_canvas_so_sizes_are_pixels(self):
        text = captions.ass(self.cues, 1440, 972, size=22, margin_v=10)
        self.assertIn("PlayResX: 1440", text)
        self.assertIn("PlayResY: 972", text)
        self.assertIn("Style: Default,Helvetica,22,", text)
        self.assertIn(",2,140,140,10,1", text)  # bottom-centre, side margins, margin above the bottom edge

    def test_ass_events_use_centiseconds_and_cannot_be_broken_by_braces(self):
        text = captions.ass(self.cues, 1440, 972)
        self.assertIn("Dialogue: 0,0:00:03.20,0:00:07.05,Default,,0,0,0,,A (braced) caption", text)
        self.assertIn("1:02:05.50", text)


class Wording(unittest.TestCase):
    def test_reading_time_has_a_floor_and_grows_with_words(self):
        self.assertEqual(captions.reading_seconds("Two words"), 2.6)
        self.assertAlmostEqual(captions.reading_seconds(" ".join(["word"] * 20)), 20 * 0.285 + 0.8)

    def test_lint_flags_length_emoji_and_hype(self):
        self.assertEqual(captions.lint("Totals link to the records behind them."), [])
        self.assertTrue(any("characters" in p for p in captions.lint("x" * 111)))
        self.assertIn("emoji", captions.lint("Done ✨"))
        self.assertEqual(captions.lint("A seamless, powerful flow."), ["hype word 'seamless'", "hype word 'powerful'"])

    def test_command_symbol_is_not_emoji(self):
        self.assertEqual(captions.lint("Press ⌘K to search."), [])


if __name__ == "__main__":
    unittest.main()
