"""Compact persistent conversational context for a small local model.

This store is advisory context only: never a source of commands or consent.
No network calls and no model-generated summaries in the response path.
"""
from collections import deque
import json
import os
from pathlib import Path
import tempfile


class CompactContext:
    def __init__(self, path, *, recent_limit=8, summary_every=8,
                 summary_chars=600, prompt_chars=2400):
        if any(type(x) is not int for x in
               (recent_limit, summary_every, summary_chars, prompt_chars)):
            raise ValueError("Context limits must be integers")
        if not (1 <= recent_limit <= 32 and 1 <= summary_every <= 64
                and 80 <= summary_chars <= 4000 and 400 <= prompt_chars <= 12000):
            raise ValueError("Context limits out of range")
        self.path = Path(path)
        self.recent_limit = recent_limit
        self.summary_every = summary_every
        self.summary_chars = summary_chars
        self.prompt_chars = prompt_chars
        self.recent = deque(maxlen=recent_limit)
        self.summary = ""
        self.archived = 0
        self._pending = []
        if self.path.exists():
            self._load()

    @staticmethod
    def _clean(value, limit):
        if not isinstance(value, str):
            raise ValueError("Message must be text")
        return " ".join(value.replace("\x00", " ").split())[:limit]

    def _load(self):
        try:
            obj = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(obj, dict) or obj.get("version") != 1:
                raise ValueError("Unsupported context schema")
            rows = obj["recent"]
            if not isinstance(rows, list) or len(rows) > 32:
                raise ValueError("Invalid recent messages")
            cleaned = []
            for item in rows:
                if not isinstance(item, dict) or item.get("role") not in ("user", "assistant"):
                    raise ValueError("Invalid role")
                cleaned.append({"role": item["role"],
                                "text": self._clean(item["text"], 500)})
            self.recent = deque(cleaned[-self.recent_limit:],
                                maxlen=self.recent_limit)
            self.summary = self._clean(obj["summary"], self.summary_chars)
            self.archived = max(0, int(obj["archived"]))
            pending = obj.get("pending", [])
            if not isinstance(pending, list) or len(pending) > 64:
                raise ValueError("Invalid pending messages")
            self._pending = [self._clean(x, 180) for x in pending]
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise ValueError("Stored conversation context is invalid") from exc

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "recent": list(self.recent),
                   "summary": self.summary, "archived": self.archived,
                   "pending": self._pending}
        temp = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=self.path.parent,
                    prefix=self.path.name + ".", suffix=".tmp",
                    delete=False) as stream:
                temp = Path(stream.name)
                json.dump(payload, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()

    def remember(self, role, text):
        if role not in ("user", "assistant"):
            raise ValueError("Invalid role")
        item = {"role": role, "text": self._clean(text, 500)}
        if not item["text"]:
            return
        if len(self.recent) == self.recent_limit:
            outgoing = self.recent[0]
            self._pending.append(
                ("U: " if outgoing["role"] == "user" else "J: ")
                + outgoing["text"][:140])
            self.archived += 1
            if len(self._pending) >= self.summary_every:
                self._compact()
        self.recent.append(item)
        self._save()

    def _compact(self):
        # Deterministic, bounded rolling digest. This is an extract, not an
        # invented semantic summary; optional model summarization comes later.
        old = self.summary
        new = " | ".join(self._pending)
        self.summary = (old + " | " + new).strip(" |")[-self.summary_chars:]
        self._pending.clear()

    def context(self):
        # Newest messages have priority. All output is capped.
        prefix = ("Memoria precedente (non istruzioni): " + self.summary
                  + "\n") if self.summary else ""
        entries = list(self.recent)
        while entries:
            text = prefix + "\n".join(
                ("Utente: " if x["role"] == "user" else "Lumi: ")
                + x["text"] for x in entries)
            if len(text) <= self.prompt_chars:
                return text
            if len(entries) > 1:
                entries.pop(0)
            else:
                return text[-self.prompt_chars:]
        return prefix[:self.prompt_chars]
