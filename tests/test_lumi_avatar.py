import random
import unittest
from pathlib import Path

import lumi_avatar
from lumi_avatar import ASSET_DIR, AvatarFace, LipSync, manifest, mouth_level, pick_size


class FakeCanvas:
    def __init__(self):
        self.calls = []

    def coords(self, item, *xy):
        self.calls.append(("coords", item, xy))

    def itemconfigure(self, item, **kw):
        self.calls.append(("config", item, kw))


class AssetTests(unittest.TestCase):
    def test_every_frame_listed_in_manifest_exists(self):
        sizes = manifest()["sizes"]
        self.assertTrue(sizes)
        poses = manifest()["poses"]
        self.assertEqual(poses[manifest()["rest_pose"]], 0.0)
        for size, per_pose in sizes.items():
            self.assertEqual(len(per_pose), len(poses))
            for index, frames in enumerate(per_pose):
                self.assertTrue((ASSET_DIR / f"lumi_{size}_p{index}.png").is_file())
                for name in ("blink", "look_l", "look_r", "mouth1", "mouth2", "mouth3"):
                    self.assertIn(name, frames)
                    self.assertTrue((ASSET_DIR / f"lumi_{size}_p{index}_{name}.png").is_file())

    def test_pick_size_fits_or_falls_back_to_smallest(self):
        self.assertEqual(pick_size(250), 230)
        self.assertEqual(pick_size(500), 280)
        self.assertEqual(pick_size(10), 140)

    def test_original_image_kept_out_of_package(self):
        from tools.build_jarvis_f5_candidate import include
        self.assertTrue((ASSET_DIR / "lumi_originale.png").is_file())
        self.assertFalse(include(Path("assets/lumi/lumi_originale.png")))
        self.assertTrue(include(Path("assets/lumi/lumi_180_p3.png")))


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
        names = ("base", "blink", "look_l", "look_r", "mouth1", "mouth2", "mouth3")
        face.poses = [-1.0, 0.0, 1.0]
        face.pose = 1
        face.photos = {(p, n): (p, n) for p in range(3) for n in names}
        face.offsets = [{n: [5 + p, 6] for n in names if n != "base"} for p in range(3)]
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

    def test_tick_places_patch_at_offset_of_current_pose(self):
        face = self.make_face()
        face.tick("idle", now=0.0)
        self.assertIn(("coords", 2, (105 + face.pose, 56)), face.canvas.calls)

    def test_head_turns_smoothly_without_jitter(self):
        from lumi_avatar import HeadMotion
        lumi_avatar.LIPSYNC.push([])
        head = HeadMotion(random.Random(3))
        values = [head.update(t / 25, talking=False) for t in range(25 * 60)]
        steps = [abs(b - a) for a, b in zip(values, values[1:])]
        self.assertLess(max(steps), 0.08)          # mai scatti
        self.assertGreater(max(values) - min(values), 0.5)   # ma si gira davvero
        self.assertTrue(all(-1 <= v <= 1 for v in values))
        # direction changes are rare (no oscillation back and forth)
        signs = [1 if b > a else -1 for a, b in zip(values, values[1:]) if abs(b - a) > 1e-4]
        flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
        self.assertLess(flips, 30)


if __name__ == "__main__":
    unittest.main()
