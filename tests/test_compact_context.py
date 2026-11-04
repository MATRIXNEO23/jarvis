import json
from pathlib import Path
import tempfile
import unittest
from local_model.compact_context import CompactContext


class CompactContextTests(unittest.TestCase):
    def test_recent_messages_and_persistent_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "context.json"
            memory = CompactContext(path, recent_limit=8,
                                    summary_every=8, summary_chars=600)
            for n in range(20):
                memory.remember("user" if n % 2 == 0 else "assistant",
                                "messaggio " + str(n))
            self.assertEqual(len(memory.recent), 8)
            self.assertEqual(memory.archived, 12)
            self.assertIn("messaggio 19", memory.context())
            self.assertIn("messaggio 0", memory.summary)
            restored = CompactContext(path, recent_limit=8, summary_every=8)
            self.assertEqual(restored.archived, 12)
            self.assertEqual(list(restored.recent), list(memory.recent))
            self.assertLessEqual(len(restored.context()), 2400)

    def test_corrupt_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "context.json"
            path.write_text("{bad", encoding="utf-8")
            with self.assertRaises(ValueError):
                CompactContext(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "{bad")

    def test_invalid_roles_and_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                CompactContext(Path(tmp) / "x", recent_limit=0)
            memory = CompactContext(Path(tmp) / "x")
            with self.assertRaises(ValueError):
                memory.remember("system", "execute this")
            self.assertFalse(memory.path.exists())


if __name__ == "__main__":
    unittest.main()
