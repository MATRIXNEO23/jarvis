import random
import unittest
from pathlib import Path

import lumi_avatar
from lumi_avatar import ASSET_DIR, AvatarFace, LipSync, manifest, mouth_level, pick_size


class FakeCanvas:
    def __init__(self):
        self.calls = []

    def move(self, item, dx, dy):
        self.calls.append(("move", item, dx, dy))

    def coords(self, item, *xy):
        self.calls.append(("coords", item, xy))

    def itemconfigure(self, item, **kw):
        self.calls.append(("config", item, kw))


class AssetTests(unittest.TestCase):
    def test_every_frame_listed_in_manifest_exists(self):
        sizes = manifest()["sizes"]
        self.assertTrue(sizes)
        for size, frames in sizes.items():
            self.assertTrue((ASSET_DIR / f"lumi_{size}.png").is_file())
            for name in ("blink", "look_l", "look_r", "mouth1", "mouth2", "mouth3"):
                self.assertIn(name, frames)
                self.assertTrue((ASSET_DIR / f"lumi_{size}_{name}.png").is_file())

    def test_pick_size_fits_or_falls_back_to_smallest(self):
        self.assertEqual(pick_size(250), 230)
        self.assertEqual(pick_size(500), 280)
        self.assertEqual(pick_size(10), 140)

    def test_original_image_kept_out_of_package(self):
        from tools.build_jarvis_f5_candidate import include
        self.assertTrue((ASSET_DIR / "lumi_originale.png").is_file())
        self.assertFalse(include(Path("assets/lumi/lumi_originale.png")))
        self.assertTrue(include(Path("assets/lumi/lumi_180.png")))


class LipSyncTests(unittest.TestCase):
    def test_level_follows_envelope_then_stops(self):
        sync = LipSync(fps=10)
        sync.push([0.1, 0.9])
        start = sync._start
        self.assertEqual(sync.level(start + 0.05), 0.1)
        self.assertEqual(sync.level(start + 0.15), 0.9)
        self.assertIsNone(sync.level(start + 0.5))

    def test_mouth_waits_for_playback_start(self):
        sync = LipSync(fps=10)
        sync.push([0.9, 0.9], delay=0.5)
        self.assertIsNone(sync.level(sync._start - 0.3))
        self.assertEqual(sync.level(sync._start + 0.05), 0.9)

    def test_mouth_levels(self):
        self.assertEqual([mouth_level(v) for v in (0, .2, .5, .9)], [0, 1, 2, 3])


class FaceTests(unittest.TestCase):
    def make_face(self):
        face = AvatarFace(rng=random.Random(1))
        face.canvas = FakeCanvas()
        face.items = {"base": 1, "eyes": 2, "mouth": 3}
        face.photos = {n: n for n in ("base", "blink", "look_l", "look_r",
                                      "mouth1", "mouth2", "mouth3")}
        face.offsets = {n: [5, 6] for n in face.photos if n != "base"}
        face.origin = (100, 50)
        return face

    def test_blinks_then_reopens(self):
        face = self.make_face()
        self.assertEqual(face.eye_frame(0.0), "blink")
        self.assertNotEqual(face.eye_frame(0.2), "blink")

    def test_mouth_moves_with_envelope_and_closes_when_idle(self):
        face = self.make_face()
        lumi_avatar.LIPSYNC.push([1.0] * 30)
        now = lumi_avatar.LIPSYNC._start + 0.1
        self.assertEqual(face.mouth_frame(now, speaking=False), "mouth3")
        lumi_avatar.LIPSYNC.push([])
        self.assertIsNone(face.mouth_frame(now, speaking=False))

    def test_mouth_stays_closed_while_voice_is_only_being_prepared(self):
        face = self.make_face()
        lumi_avatar.LIPSYNC.push([])
        self.assertIsNone(face.mouth_frame(123.0, speaking=True))

    def test_tick_places_patch_at_offset_plus_head_motion(self):
        face = self.make_face()
        face.tick("idle", now=0.0)
        sx, sy = face._shift
        self.assertIn(("coords", 2, (105 + sx, 56 + sy)), face.canvas.calls)

    def test_head_moves_gently_over_time(self):
        face = self.make_face()
        lumi_avatar.LIPSYNC.push([])
        offsets = {face.head_offset(t / 10) for t in range(200)}
        self.assertGreater(len(offsets), 3)
        self.assertTrue(all(abs(x) <= 4 and abs(y) <= 4 for x, y in offsets))


if __name__ == "__main__":
    unittest.main()
