"""Streaming of partial local-model text (build 021)."""
import threading
import time
import unittest

from local_model.native_bridge import NativeGemmaBridge
from local_model.native_config import NativeModelConfig
from local_model.token_stream import current, streaming, visible_text


class VisibleTextTests(unittest.TestCase):
    def test_cuts_stop_and_holds_back_partial_stop(self):
        self.assertEqual(visible_text("Ciao!<end_of_turn>x", "<end_of_turn>"), "Ciao!")
        self.assertEqual(visible_text("Ciao <end_of", "<end_of_turn>"), "Ciao ")
        self.assertEqual(visible_text("Ciao", None), "Ciao")

    def test_callback_is_per_thread_and_restored(self):
        def callback(_text):
            pass
        with streaming(callback):
            self.assertIs(current(), callback)
            other = []
            t = threading.Thread(target=lambda: other.append(current()))
            t.start(); t.join()
            self.assertEqual(other, [None])
        self.assertIsNone(current())


class GrowingUpstream:
    """Fake engine: text grows while generate() runs; old answer before start."""

    def __init__(self):
        self.handle = self
        self.text = "risposta precedente"

    def get_pending_output(self):
        return self.text.encode("utf-8")

    def generate(self, args):
        self.text = ""
        for word in ("Ciao", " Alberto.", " Come", " stai?", "<end_of_turn>"):
            time.sleep(0.2)
            self.text += word
        return {"status": 1, "stopreason": 1, "text": "Ciao Alberto. Come stai?"}


class BridgeStreamTests(unittest.TestCase):
    def make_bridge(self, upstream):
        bridge = NativeGemmaBridge(NativeModelConfig(), upstream, initialize=lambda *_: None)
        bridge._loaded = True
        bridge.family = "gemma2"
        return bridge

    def test_partial_text_grows_without_stale_or_stop_markers(self):
        bridge = self.make_bridge(GrowingUpstream())
        chunks = []
        with streaming(chunks.append):
            final = bridge.generate("prompt", timeout=10)
        self.assertEqual(final, "Ciao Alberto. Come stai?")
        self.assertGreaterEqual(len(chunks), 2)
        self.assertNotIn("risposta precedente", "".join(chunks))
        self.assertTrue(all(b.startswith(a) for a, b in zip(chunks, chunks[1:])))
        self.assertFalse(any("<end" in c for c in chunks))

    def test_no_callback_no_stream_thread(self):
        bridge = self.make_bridge(GrowingUpstream())
        self.assertEqual(bridge.generate("prompt", timeout=10), "Ciao Alberto. Come stai?")


class ChatStreamTests(unittest.TestCase):
    def test_speaks_completed_sentences_then_only_the_rest(self):
        from chat_stream import ChatStream
        spoken, final = [], []
        stream = ChatStream()
        stream.speak = lambda text: spoken.append(text) or True
        stream.voice_enabled = lambda: True
        stream._speak_sentences("Ciao Alberto. Come")
        stream._speak_sentences("Ciao Alberto. Come stai")
        self.assertEqual(spoken, ["Ciao Alberto."])
        stream.speak_final("Ciao Alberto. Come stai?", final.append)
        self.assertEqual(final, ["Come stai?"])

    def test_unconfigured_stream_is_a_no_op_and_final_speaks_everything(self):
        from chat_stream import ChatStream
        stream, final = ChatStream(), []
        self.assertIsNone(stream.sink(1))
        stream.drain(1, True)
        stream.speak_final("Tutto.", final.append)
        self.assertEqual(final, ["Tutto."])


if __name__ == "__main__":
    unittest.main()
