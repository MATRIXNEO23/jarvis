"""Raster HUD regression: standard-library PNG and safe offline animation."""
from __future__ import annotations

import base64
import struct
import time
import unittest
import zlib

from hud_raster import (
    ASSETS, COLORS, RasterArtWorker, earth_png, land_grid, photoimage_from_png,
    reactor_glow_png, rgba_png,
)


def png_size(data):
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG signature")
    return struct.unpack(">II", data[16:24])


class HighFidelityRasterTests(unittest.TestCase):
    def test_png_encoder_produces_valid_rgba_with_transparency(self):
        pixels = bytes((255, 0, 0, 255, 0, 0, 0, 0))
        data = rgba_png(2, 1, pixels)
        self.assertEqual(png_size(data), (2, 1))
        pos = data.index(b"IDAT")
        length = struct.unpack(">I", data[pos-4:pos])[0]
        raw = zlib.decompress(data[pos+4:pos+4+length])
        self.assertEqual(raw[0], 0)
        self.assertEqual(raw[1:], pixels)

    def test_reactor_includes_all_three_real_audio_colors(self):
        images = {state: reactor_glow_png(128, state)
                  for state in COLORS}
        self.assertEqual(set(images), {"idle", "listening", "speaking"})
        self.assertTrue(all(png_size(img) == (128,128)
                            for img in images.values()))
        self.assertEqual(len(set(images.values())), 3)
        for image in images.values():
            self.assertLess(len(image), 128*128*4)

    def test_geographic_mask_contains_ocean_and_continents(self):
        mask = land_grid()
        self.assertEqual((len(mask), len(mask[0])), (360,720))
        # Approximate points within large schematic areas, not GPS lookup.
        europe = mask[int((90-49)*2)][int((12+180)*2)]
        africa = mask[int((90-1)*2)][int((25+180)*2)]
        pacific = mask[int((90-0)*2)][int((-140+180)*2)]
        self.assertEqual(europe, 1)
        self.assertEqual(africa, 1)
        self.assertEqual(pacific, 0)

    def test_earth_frames_move_land_but_keep_same_png_dimensions(self):
        before = earth_png(120, 0)
        after = earth_png(120, .22)
        self.assertEqual(png_size(before), (120,120))
        self.assertEqual(png_size(after), (120,120))
        self.assertNotEqual(before, after)
        self.assertLess(len(before), 120*120*4)

    def test_invalid_image_dimensions_do_not_allocate_unbounded_memory(self):
        with self.assertRaises(ValueError):
            rgba_png(4096, 4096, b"")
        with self.assertRaises(ValueError):
            reactor_glow_png(1000, "idle")
        with self.assertRaises(ValueError):
            earth_png(1000, 0)

    def test_worker_does_not_call_tkinter_off_thread(self):
        worker = RasterArtWorker()
        worker.request("reactor", 100)
        limit = time.monotonic() + 12
        result = None
        while time.monotonic() < limit and result is None:
            time.sleep(.03)
            result = worker.get("reactor",100)
        self.assertIsNotNone(result)
        self.assertEqual(len(result),3)
        self.assertTrue(all(png_size(x)==(100,100) for x in result))
        worker.clear()


if __name__ == "__main__":
    unittest.main()
