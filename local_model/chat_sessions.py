"""Opt-in local chat instances for a future Kobold-style Jarvis interface.

ARCH-01/F1 only: metadata and atomic, paired transcripts, NO runtime wiring.
No imports from Jarvis, Second Brain, native model or internet. Instantiation
requires an explicit file path and creates only that database.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
import sqlite3
import threading
from uuid import uuid4


_CHAT_ID = re.compile(r"[a-f0-9]{32}\Z")


class ChatSessionError(ValueError):
    """Invalid chat identifier, scope, content or missing conversation."""


@dataclass(frozen=True)
class ChatInfo:
    id: str
    title: str
    project_id: str | None
    created_utc: str
    updated_utc: str


def _scope(project_id):
    if project_id is None:
        return "general", "general"
    if type(project_id) is not str or _CHAT_ID.fullmatch(project_id) is None:
        raise ChatSessionError("ID progetto non valido.")
    return "project", project_id


def _id(value):
    if type(value) is not str or _CHAT_ID.fullmatch(value) is None:
        raise ChatSessionError("ID conversazione non valido.")
    return value


def _title(value):
    if not isinstance(value, str) or "\x00" in value:
        raise ChatSessionError("Titolo conversazione non valido.")
    text = " ".join(value.split())
    if not 1 <= len(text) <= 100:
        raise ChatSessionError("Titolo conversazione fuori limite.")
    return text


def _message(value):
    if type(value) is not str or "\x00" in value or not value.strip():
        raise ChatSessionError("Messaggio non valido.")
    if len(value) > 16384:
        raise ChatSessionError("Messaggio oltre il limite locale.")
    return value


def _timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class ChatSessionStore:
    """Sidecar SQLite store; all operations explicit and scoped.

    This module NEVER decides which model to run, which memories to retrieve
    or which local actions to execute. It does not migrate or delete data.
    A UI/controller must check project authorization before providing a
    project_id or feeding its chat history to a language model.
    """

    def __init__(self, path):
        self.path = Path(path)
        self._lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS chat_sessions(
                    id TEXT PRIMARY KEY,
                    scope TEXT NOT NULL CHECK(scope IN ('general','project')),
                    scope_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_utc TEXT NOT NULL,
                    updated_utc TEXT NOT NULL)""")
            db.execute(
                """CREATE INDEX IF NOT EXISTS chat_sessions_scope
                   ON chat_sessions(scope,scope_id,updated_utc DESC)""")
            db.execute(
                """CREATE TABLE IF NOT EXISTS chat_exchanges(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL REFERENCES chat_sessions(id),
                    user_text TEXT NOT NULL,
                    assistant_text TEXT NOT NULL,
                    created_utc TEXT NOT NULL)""")
            db.execute(
                """CREATE INDEX IF NOT EXISTS chat_exchanges_recent
                   ON chat_exchanges(chat_id,id DESC)""")
            db.execute(
                """CREATE TABLE IF NOT EXISTS chat_selection(
                    scope TEXT NOT NULL,
                    scope_id TEXT NOT NULL,
                    chat_id TEXT NOT NULL REFERENCES chat_sessions(id),
                    PRIMARY KEY(scope,scope_id))""")

    @contextmanager
    def _db(self):
        with self._lock:
            db = sqlite3.connect(str(self.path), timeout=6)
            db.row_factory = sqlite3.Row
            try:
                db.execute("PRAGMA foreign_keys=ON")
                db.execute("PRAGMA busy_timeout=6000")
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

    @staticmethod
    def _info(row):
        if row is None:
            return None
        return ChatInfo(
            id=row["id"], title=row["title"],
            project_id=None if row["scope"] == "general" else row["scope_id"],
            created_utc=row["created_utc"], updated_utc=row["updated_utc"])

    @staticmethod
    def _require(db, chat_id, scope, scope_id):
        row = db.execute(
            "SELECT * FROM chat_sessions WHERE id=? AND scope=? AND scope_id=?",
            (chat_id, scope, scope_id)).fetchone()
        if row is None:
            raise ChatSessionError("Conversazione non presente nell'ambito selezionato.")
        return row

    def create_chat(self, title="Nuova chat", *, project_id=None, activate=False):
        scope, scope_id = _scope(project_id)
        title = _title(title)
        if type(activate) is not bool:
            raise ChatSessionError("Opzione attivazione non valida.")
        chat_id, now = uuid4().hex, _timestamp()
        with self._db() as db:
            db.execute(
                """INSERT INTO chat_sessions(id,scope,scope_id,title,created_utc,updated_utc)
                   VALUES(?,?,?,?,?,?)""",
                (chat_id, scope, scope_id, title, now, now))
            if activate:
                db.execute(
                    """INSERT INTO chat_selection(scope,scope_id,chat_id)
                       VALUES(?,?,?)
                       ON CONFLICT(scope,scope_id) DO UPDATE SET chat_id=excluded.chat_id""",
                    (scope, scope_id, chat_id))
        return ChatInfo(chat_id, title, project_id, now, now)

    def list_chats(self, *, project_id=None):
        scope, scope_id = _scope(project_id)
        with self._db() as db:
            rows = db.execute(
                """SELECT * FROM chat_sessions WHERE scope=? AND scope_id=?
                   ORDER BY updated_utc DESC, rowid DESC""",
                (scope, scope_id)).fetchall()
        return tuple(self._info(row) for row in rows)

    def get_chat(self, chat_id, *, project_id=None):
        scope, scope_id = _scope(project_id)
        _id(chat_id)
        with self._db() as db:
            row = self._require(db, chat_id, scope, scope_id)
        return self._info(row)

    def active_chat(self, *, project_id=None):
        scope, scope_id = _scope(project_id)
        with self._db() as db:
            row = db.execute(
                "SELECT chat_id FROM chat_selection WHERE scope=? AND scope_id=?",
                (scope, scope_id)).fetchone()
        return row["chat_id"] if row else None

    def select_chat(self, chat_id, *, project_id=None):
        scope, scope_id = _scope(project_id)
        _id(chat_id)
        with self._db() as db:
            self._require(db, chat_id, scope, scope_id)
            db.execute(
                """INSERT INTO chat_selection(scope,scope_id,chat_id)
                   VALUES(?,?,?)
                   ON CONFLICT(scope,scope_id) DO UPDATE SET chat_id=excluded.chat_id""",
                (scope, scope_id, chat_id))

    def rename_chat(self, chat_id, title, *, project_id=None):
        scope, scope_id = _scope(project_id)
        _id(chat_id)
        title = _title(title)
        with self._db() as db:
            self._require(db, chat_id, scope, scope_id)
            db.execute(
                "UPDATE chat_sessions SET title=?,updated_utc=? WHERE id=?",
                (title, _timestamp(), chat_id))

    def append_exchange(self, chat_id, question, answer, *, project_id=None):
        """Persist one accepted user/assistant exchange atomically, never half."""
        scope, scope_id = _scope(project_id)
        _id(chat_id)
        question, answer = _message(question), _message(answer)
        with self._db() as db:
            self._require(db, chat_id, scope, scope_id)
            now = _timestamp()
            cursor = db.execute(
                """INSERT INTO chat_exchanges(chat_id,user_text,assistant_text,created_utc)
                   VALUES(?,?,?,?)""", (chat_id, question, answer, now))
            db.execute(
                "UPDATE chat_sessions SET updated_utc=? WHERE id=?",
                (now, chat_id))
            return cursor.lastrowid

    def display_pairs(self, chat_id, *, project_id=None, limit=500):
        """Read-only full transcript for the chat view (never sent to a model)."""
        scope, scope_id = _scope(project_id)
        _id(chat_id)
        if type(limit) is not int or not 1 <= limit <= 5000:
            raise ChatSessionError("Numero scambi richiesti non valido.")
        with self._db() as db:
            self._require(db, chat_id, scope, scope_id)
            rows = db.execute(
                """SELECT user_text, assistant_text FROM chat_exchanges
                   WHERE chat_id=? ORDER BY id DESC LIMIT ?""",
                (chat_id, limit)).fetchall()
        return tuple((row["user_text"], row["assistant_text"]) for row in reversed(rows))

    def recent_pairs(self, chat_id, *, project_id=None, count=8):
        """Return last N complete exchanges, chronological, no LLM side effects.

        All exchanges are kept in the database. Only the *read* is bounded.
        """
        scope, scope_id = _scope(project_id)
        _id(chat_id)
        if type(count) is not int or not 1 <= count <= 32:
            raise ChatSessionError("Numero scambi richiesti non valido.")
        with self._db() as db:
            self._require(db, chat_id, scope, scope_id)
            rows = db.execute(
                """SELECT user_text, assistant_text FROM chat_exchanges
                   WHERE chat_id=? ORDER BY id DESC LIMIT ?""",
                (chat_id, count)).fetchall()
        return tuple(
            (("user", row["user_text"]), ("assistant", row["assistant_text"]))
            for row in reversed(rows))
