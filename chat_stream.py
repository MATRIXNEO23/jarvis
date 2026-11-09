"""Live text of the local model in the console + voice from the first sentence.

Configured once by jarvis.main(); until then every method is a harmless no-op,
so the existing callbacks keep their behaviour (and their tests).
"""
from __future__ import annotations

from datetime import datetime
import queue
import re

_SENTENCE_END = re.compile(r"[.!?…:;](?=\s)|\n")


class ChatStream:
    def __init__(self):
        self.queue: queue.Queue = queue.Queue()
        self.output = None
        self.speak = None          # callable(text) -> bool, or None
        self.voice_enabled = lambda: False
        self.shown = False
        self.spoken = ""

    def configure(self, *, output, speak, voice_enabled) -> None:
        self.output, self.speak, self.voice_enabled = output, speak, voice_enabled

    # worker side -------------------------------------------------------
    def sink(self, epoch):
        if self.output is None:
            return None
        return lambda text: self.queue.put((text, epoch))

    # UI side -----------------------------------------------------------
    def start_request(self) -> None:
        self.spoken = ""

    def drain(self, epoch, active: bool) -> None:
        latest = None
        try:
            while True:
                text, item_epoch = self.queue.get_nowait()
                if item_epoch == epoch and active:
                    latest = text
        except queue.Empty:
            pass
        if latest is not None and self.output is not None:
            self._show(latest)
            self._speak_sentences(latest)

    def clear(self) -> None:
        if self.shown and self.output is not None:
            self.output.configure(state="normal")
            self.output.delete("lumi_stream_start", "lumi_stream_end")
            self.output.configure(state="disabled")
        self.shown = False

    def _show(self, text: str) -> None:
        out = self.output
        out.configure(state="normal")
        if self.shown:
            out.delete("lumi_stream_start", "lumi_stream_end")
        else:
            out.mark_set("lumi_stream_start", "end-1c")
            out.mark_gravity("lumi_stream_start", "left")
            out.mark_set("lumi_stream_end", "end-1c")
            out.mark_gravity("lumi_stream_end", "right")
            self.shown = True
        out.insert("lumi_stream_start",
                   "◉  LUMI         " + datetime.now().strftime("%H:%M:%S") + "  …\n",
                   ("jarvis", "message_head"))
        out.insert("lumi_stream_end", text.strip() + "\n\n", "jarvis")
        out.see("end")
        out.configure(state="disabled")

    def _speak_sentences(self, text: str) -> None:
        if self.speak is None or not self.voice_enabled():
            return
        done = self.spoken
        if not text.startswith(done):
            return
        rest = text[len(done):]
        last = None
        for match in _SENTENCE_END.finditer(rest):
            last = match
        if last is None or len(rest[:last.end()].strip()) < 2:
            return
        chunk = rest[:last.end()]
        if self.speak(chunk.strip()):
            self.spoken = done + chunk

    def speak_final(self, text: str, speak_result) -> None:
        """Say only what streaming has not already said."""
        done, self.spoken = self.spoken, ""
        if not done:
            speak_result(text)
        elif text.startswith(done):
            rest = text[len(done):].strip()
            if rest:
                speak_result(rest)


STREAM = ChatStream()
