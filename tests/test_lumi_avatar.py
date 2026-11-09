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
        data = manifest()
        poses, hair = data["poses"], data["hair"]
        self.assertEqual(poses[data["rest_pose"]], 0.0)
        self.assertEqual(hair[data["rest_hair"]], 0.0)
        names = ["blink", "look_l", "look_r"] + [f"mouth{n}" for n in range(1, data["mouth_levels"] + 1)]
        for size, entry in sizes.items():
            self.assertEqual(len(entry["poses"]), len(poses))
            for index, frames in enumerate(entry["poses"]):
                for h in range(len(hair)):
                    self.assertTrue((ASSET_DIR / f"lumi_{size}_p{index}_h{h}.png").is_file())
                for name in names:
                    self.assertIn(name, frames)
                    self.assertTrue((ASSET_DIR / f"lumi_{size}_p{index}_{name}.png").is_file())
            self.assertIsNone(entry["breath"][0])
            for level, box in enumerate(entry["breath"][1:], 1):
                self.assertTrue((ASSET_DIR / f"lumi_{size}_b{level}.png").is_file())

    def test_pick_size_fits_or_falls_back_to_smallest(self):
        self.assertEqual(pick_size(300), 290)
        self.assertEqual(pick_size(200), 190)
        self.assertEqual(pick_size(10), 190)

    def test_original_image_kept_out_of_package(self):
        from tools.build_jarvis_f5_candidate import include
        self.assertTrue((ASSET_DIR / "lumi_originale.png").is_file())
        self.assertFalse(include(Path("assets/lumi/lumi_originale.png")))
        self.assertTrue(include(Path("assets/lumi/lumi_190_p6_h1.png")))


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
        self.assertEqual([mouth_level(v) for v in (0, .05, .1, .5, 1.0)], [0, 0, 1, 3, 5])


class FaceTests(unittest.TestCase):
    def make_face(self):
        face = AvatarFace(rng=random.Random(1))
        face.canvas = FakeCanvas()
        face.items = {"base": 1, "eyes": 2, "mouth": 3}
        names = ("blink", "look_l", "look_r", "mouth1", "mouth2", "mouth3", "mouth4", "mouth5")
        face.poses = [-1.0, 0.0, 1.0]
        face.pose = 1
        face.hair_levels = [-1.0, 0.0, 1.0]
        face.hair_index = 1
        face.photos = {(p, n): (p, n) for p in range(3) for n in names}
        face.photos.update({(p, "base", h): (p, h) for p in range(3) for h in range(3)})
        face.offsets = [{n: [5 + p, 6] for n in names} for p in range(3)]
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
        frames = [face.mouth_frame(now) for _ in range(6)]
        self.assertEqual(frames[-1], "mouth5")          # si apre in pochi fotogrammi
        self.assertNotEqual(frames[0], "mouth5")        # non di scatto
        lumi_avatar.LIPSYNC.push([])
        closing = [face.mouth_frame(now) for _ in range(12)]
        self.assertIsNone(closing[-1])                  # poi si richiude

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


class HairAndBreathTests(unittest.TestCase):
    def test_hair_lags_behind_turn_then_settles(self):
        from lumi_avatar import HairLag
        hair = HairLag()
        values = []
        for step in range(100):
            t = step * 0.04
            yaw = min(1.0, t / 1.0)          # gira per 1 s, poi ferma
            values.append(hair.update(t, yaw))
        self.assertLess(min(values[:25]), -0.3)   # mentre gira resta indietro
        self.assertLess(abs(values[-1]), 0.05)    # da ferma torna a posto
        steps = [abs(b - a) for a, b in zip(values, values[1:])]
        self.assertLess(max(steps), 0.35)

    def test_breath_is_slow_and_cyclic(self):
        face = AvatarFace(rng=random.Random(2))
        face.breath_boxes = [None, [0, 1], [0, 1], [0, 1]]
        levels = [face.breath_level(t / 25) for t in range(25 * 10)]
        self.assertEqual(set(levels), {0, 1, 2, 3})
        changes = sum(1 for a, b in zip(levels, levels[1:]) if a != b)
        self.assertLess(changes, 20)               # pochi cambi in 10 s


if __name__ == "__main__":
    unittest.main()
