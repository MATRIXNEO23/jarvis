"""Regressions for the reference-inspired static, dark circuit backdrop."""
import unittest

from hud_backdrop import (
    DEEP_BLACK, TRACE_DARK, backdrop_tone, draw_cinematic_backdrop
)


class RecordingCanvas:
    def __init__(self):
        self.calls = []

    def create_rectangle(self, *points, **kwargs):
        self.calls.append(("rectangle", points, kwargs))
        return len(self.calls)

    def create_line(self, *points, **kwargs):
        self.calls.append(("line", points, kwargs))
        return len(self.calls)

    def create_oval(self, *points, **kwargs):
        self.calls.append(("oval", points, kwargs))
        return len(self.calls)


class CinematicBackdropTests(unittest.TestCase):
    def test_background_is_almost_black_not_a_blue_solid(self):
        self.assertEqual(DEEP_BLACK, "#01040a")
        for band in range(24):
            shade = backdrop_tone(band)
            self.assertEqual(len(shade), 7)
            rgb = [int(shade[i:i+2], 16) for i in (1, 3, 5)]
            self.assertLessEqual(max(rgb), 18)
            self.assertLessEqual(rgb[0], 2)
        self.assertEqual(TRACE_DARK, "#071a2b")

    def test_reactor_uses_sparse_circuits_not_full_screen_grid(self):
        canvas = RecordingCanvas()
        draw_cinematic_backdrop(canvas, 460, 490, "reactor")
        background = [call for call in canvas.calls
                      if call[0] == "rectangle"
                      and len(call[1]) == 4
                      and call[1][0] == 0
                      and call[1][2] == 460]
        self.assertEqual(len(background), 24)
        traces = [call for call in canvas.calls if call[0] == "line"]
        self.assertGreater(len(traces), 30)
        self.assertLess(len(traces), 100)
        self.assertLess(len(canvas.calls), 170)
        # No dense 36px vertical-horizontal mesh across the center.
        full_height_lines = [call for call in traces
                             if min(call[1][1::2]) <= 5
                             and max(call[1][1::2]) >= 485]
        self.assertFalse(full_height_lines)

    def test_earth_background_has_circuit_motifs_not_solid_grid(self):
        canvas = RecordingCanvas()
        draw_cinematic_backdrop(canvas, 320, 490, "earth")
        self.assertGreater(
            sum(kind == "line" for kind,_,__ in canvas.calls), 20)
        self.assertLess(len(canvas.calls), 160)

    def test_backdrop_is_deterministic_and_reusable(self):
        first, second = RecordingCanvas(), RecordingCanvas()
        draw_cinematic_backdrop(first, 420, 500, "reactor")
        draw_cinematic_backdrop(second, 420, 500, "reactor")
        self.assertEqual(first.calls, second.calls)

    def test_invalid_geometry_and_region_are_rejected(self):
        c = RecordingCanvas()
        for region in ("", "map", "unknown"):
            with self.assertRaises(ValueError):
                draw_cinematic_backdrop(c, 400, 400, region)
        for width, height in ((-1, 300), (6000, 400), (200, 0)):
            with self.assertRaises(ValueError):
                draw_cinematic_backdrop(c, width, height, "earth")
        with self.assertRaises(ValueError):
            backdrop_tone(24)


if __name__ == "__main__":
    unittest.main()
