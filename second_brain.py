"""Lumi Second Brain v1: local, durable and evidence-backed continuity.

Stores bounded conversational episodes and *verified* task receipts in SQLite.
No cloud database, model training, API costs, executable memories or automatic
import of email bodies. Recollection is data only; it never authorizes actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from contextlib import contextmanager
from uuid import uuid4

from settings import default_path


class BrainError(ValueError):
    pass


MAX_QUERY = 180
MAX_STORED_UTTERANCE = 320
MAX_STORED_ANSWER = 350
MAX_LABEL = 180
MAX_REF = 180
MAX_PROMPT_MEMORY = 1100
_STOP_WORDS = frozenset({
    "che", "cosa", "come", "quella", "quello", "quelle", "quelli", "oggi",
    "domani", "ieri", "dopo", "prima", "una", "uno", "con", "per", "del",
    "della", "delle", "degli", "dove", "quando", "lui", "lei", "mio", "mia",
    "hai", "fatto", "avuto", "avrei", "voglio", "ricordi", "ricordare",
    "ricordami", "sapresti", "puoi", "potresti", "perche", "alla", "agli",
    "quel", "questa", "questa", "stavo", "abbiamo", "stati", "stato", "mandato",
    "inviato", "inviata", "inviati", "inviate", "aperto", "aperta", "file",
    "cose", "cosa", "fare", "era", "sono", "sei", "era", "due", "tre", "giorni",
})
_SENSITIVE = re.compile(
    r"\b(?:password|passphrase|token|chiave\s+api|codice\s+otp|pin)\b",
    re.I,
)


@dataclass(frozen=True)
class Evidence:
    time_utc: str
    source: str
    summary: str
    reference: str = ""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _clean(text: object, maximum: int) -> str:
    if not isinstance(text, str):
        return ""
    clean = " ".join(text.split()).strip()
    return clean[:maximum]


def _tokens(text: str) -> set[str]:
    from unicodedata import normalize
    folded = normalize("NFKD", text.casefold())
    plain = "".join(c for c in folded if not 0x300 <= ord(c) <= 0x36F)
    return {part for part in re.findall(r"[a-z0-9]{3,}", plain)
            if part not in _STOP_WORDS}


class SecondBrain:
    """Single-machine memory with strong separation between facts and speech."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_path().with_name(
            "second_brain.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _db(self):
        conn = sqlite3.connect(str(self.path), timeout=5.0)
        try:
            conn.execute("PRAGMA secure_delete=ON")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize(self):
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS conversations(
                id INTEGER PRIMARY KEY,
                time_utc TEXT NOT NULL,
                user_text TEXT NOT NULL,
                reply TEXT NOT NULL,
                kind TEXT NOT NULL CHECK(kind IN ('chat', 'clarify', 'action', 'error'))
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS action_receipts(
                id INTEGER PRIMARY KEY,
                receipt_id TEXT NOT NULL UNIQUE,
                time_utc TEXT NOT NULL,
                action_id TEXT NOT NULL,
                application TEXT NOT NULL,
                summary TEXT NOT NULL,
                external_ref TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                verified INTEGER NOT NULL CHECK(verified=1)
            )""")
            if "proof_kind" not in {r[1] for r in db.execute("PRAGMA table_info(action_receipts)")}:
                db.execute("ALTER TABLE action_receipts ADD COLUMN "
                           "proof_kind TEXT NOT NULL DEFAULT 'legacy_unassessed'")
            db.execute("CREATE INDEX IF NOT EXISTS receipts_time ON action_receipts(time_utc)")
            db.execute("CREATE INDEX IF NOT EXISTS conversations_time ON conversations(time_utc)")
            db.execute("""CREATE TABLE IF NOT EXISTS recent_dialogue(
                turn_id INTEGER PRIMARY KEY, user_text TEXT NOT NULL, reply TEXT NOT NULL)""")
            # Triggers also apply when an older Jarvis clears the parent table.
            db.execute("""CREATE TRIGGER IF NOT EXISTS recent_dialogue_delete
                AFTER DELETE ON conversations BEGIN
                DELETE FROM recent_dialogue WHERE turn_id=OLD.id; END""")
            db.execute("DELETE FROM recent_dialogue WHERE turn_id NOT IN (SELECT id FROM conversations)")

    def remember_turn(self, user: str, reply: str, kind: str = "chat") -> bool:
        """Persist brief episodes and bounded recent chat; never auto-import file bodies."""
        if kind not in ("chat", "clarify", "action", "error"):
            raise BrainError("Tipo episodio non valido.")
        if _SENSITIVE.search(str(user)) or _SENSITIVE.search(str(reply)):
            return False
        u = _clean(user, MAX_STORED_UTTERANCE)
        a = _clean(reply, MAX_STORED_ANSWER)
        if not u or not a:
            return False
        with self._db() as db:
            cursor = db.execute("INSERT INTO conversations(time_utc,user_text,reply,kind)"
                       " VALUES(?,?,?,?)", (_now(), u, a, kind))
            if kind in ("chat", "clarify"):
                db.execute("INSERT INTO recent_dialogue VALUES(?,?,?)",
                           (cursor.lastrowid, user.strip()[:16384], reply.strip()[:16384]))
                db.execute("DELETE FROM recent_dialogue WHERE turn_id NOT IN "
                           "(SELECT turn_id FROM recent_dialogue ORDER BY turn_id DESC LIMIT 16)")
        return True

    def record_completed_action(self, action_id: str, application: str,
                                summary: str, *, receipt_id: str,
                                external_ref: str = "",
                                metadata: dict | None = None,
                                verified: bool = False,
                                proof_kind: str = "external_receipt") -> bool:
        """An actual executor/connector must pass verified=True after success.

        A GPT intention or a pending operation is not evidence of completion.
        Receipt identifiers make event recording retry-safe.
        """
        if verified is not True or proof_kind not in (
                "local_observation","provider_receipt","external_receipt"):
            raise BrainError("Non posso registrare come verificata un'azione senza prova.")
        action = _clean(action_id, 80)
        app = _clean(application, 60)
        label = _clean(summary, MAX_LABEL)
        rid = _clean(receipt_id, MAX_REF)
        external = _clean(external_ref, MAX_REF)
        if (not all((action, app, label, rid))
                or _SENSITIVE.search(label)
                or not re.fullmatch(r"[a-zA-Z0-9._:-]+", action)
                or len(receipt_id) > MAX_REF
                or not isinstance(metadata, (dict, type(None)))):
            raise BrainError("Ricevuta incompleta o non sicura.")
        safe_metadata = {}
        if metadata:
            # Never store arbitrary freeform connector payloads or message
            # bodies; only the explicitly reviewed metadata fields.
            allowed = {"recipient", "subject", "file_name", "folder", "service"}
            if set(metadata) - allowed:
                raise BrainError("Metadati non autorizzati nel ricordo.")
            for key, value in metadata.items():
                if not isinstance(value, str) or len(value) > 180:
                    raise BrainError("Metadati del ricordo non validi.")
                if _SENSITIVE.search(value):
                    raise BrainError("Un segreto non può essere salvato nella memoria.")
                safe_metadata[key] = _clean(value, 180)
        payload = json.dumps(safe_metadata, ensure_ascii=False)
        with self._db() as db:
            cur = db.execute(
                """INSERT OR IGNORE INTO action_receipts(
                     receipt_id,time_utc,action_id,application,summary,
                     external_ref,metadata_json,verified,proof_kind)
                   VALUES(?,?,?,?,?,?,?,1,?)""",
                (rid, _now(), action, app, label, external, payload, proof_kind),
            )
            return bool(cur.rowcount)

    def record_email_sent(self, *, recipient: str, subject: str,
                          provider_message_id: str, verified: bool) -> bool:
        """Future mail adapter hook: called ONLY after real provider success.

        Mail sending is NOT implemented in Lumi yet. No email body is stored.
        """
        if (not recipient.strip() or not subject.strip()
                or not provider_message_id.strip()):
            raise BrainError("Prova dell'invio email incompleta.")
        return self.record_completed_action(
            "mail.send", "email", "Email inviata: " + _clean(subject, 125),
            receipt_id="mail:" + provider_message_id,
            external_ref=provider_message_id,
            metadata={"recipient": recipient, "subject": subject},
            verified=verified,proof_kind="provider_receipt",
        )

    def dialogue_pairs(self, count=16):
        """Recent chat in original roles; old truncated records remain usable."""
        count = min(16, max(0, int(count)))
        with self._db() as db:
            rows = db.execute(
                "SELECT COALESCE(r.user_text,c.user_text),COALESCE(r.reply,c.reply) "
                "FROM conversations c LEFT JOIN recent_dialogue r ON r.turn_id=c.id "
                "WHERE c.kind IN ('chat','clarify') ORDER BY c.id DESC LIMIT ?", (count,)).fetchall()
        return tuple((("user", u), ("assistant", a)) for u, a in reversed(rows))

    def recent_turns(self, count: int = 4) -> tuple[dict, ...]:
        count = min(max(int(count), 0), 8)
        with self._db() as db:
            rows = db.execute(
                "SELECT time_utc,user_text,reply,kind FROM conversations "
                "ORDER BY id DESC LIMIT ?", (count,)).fetchall()
        return tuple({"when": when, "user": user, "lia": reply, "kind": kind}
                     for when, user, reply, kind in reversed(rows))

    def search(self, query: str, *, limit: int = 4) -> tuple[Evidence, ...]:
        """Search across past sessions, not just the last few seconds."""
        if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY:
            return ()
        terms = _tokens(query)
        if not terms:
            return ()
        limit = min(max(int(limit), 1), 8)
        hits: list[tuple[int, Evidence]] = []
        with self._db() as db:
            rows = db.execute(
                "SELECT time_utc,application,action_id,summary,external_ref,"
                "metadata_json,proof_kind FROM action_receipts ORDER BY id DESC LIMIT 3000"
            ).fetchall()
            dialogue = db.execute(
                "SELECT time_utc,user_text,reply,kind FROM conversations "
                "ORDER BY id DESC LIMIT 1500"
            ).fetchall()
        for when, app, aid, label, ref, details, proof in rows:
            meta = json.loads(details)
            searchable = " ".join(
                [app, aid.replace(".", " "), label, *meta.values()])
            overlap = len(terms & _tokens(searchable))
            # Recipients and subjects are explicit evidence of a sent message.
            if overlap:
                description = label
                if aid == "mail.send":
                    description += " a " + meta.get("recipient", "destinatario non noto")
                source=("verified_action" if proof in
                        ("local_observation","provider_receipt","external_receipt")
                        else "reported_action")
                hits.append((overlap * 10 + (4 if source=="verified_action" else 1),
                             Evidence(when,source,description,ref)))
        for when, user, reply, kind in dialogue:
            overlap = len(terms & _tokens(user + " " + reply))
            if overlap:
                hits.append((overlap * 10, Evidence(
                    when, "conversation", "Utente: " + user[:130]
                    + " | Lia: " + reply[:130])))
        # Stable recency order for equal scores (both tables are newest-first).
        hits.sort(key=lambda item: (item[0], item[1].time_utc), reverse=True)
        return tuple(e for _, e in hits[:limit])

    def prompt_context(self, query: str, *, budget: int = MAX_PROMPT_MEMORY) -> str:
        """Only evidence, with timestamps and source; never an action directive."""
        if type(budget) is not int or budget < 100:
            return "{}"
        budget = min(budget, MAX_PROMPT_MEMORY)
        candidate = {"related": [], "recent": []}
        for evidence in self.search(query, limit=5):
            item = {"when": evidence.time_utc, "source": evidence.source,
                    "fact": evidence.summary}
            if evidence.reference:
                item["ref"] = evidence.reference
            draft = dict(candidate)
            draft["related"] = candidate["related"] + [item]
            if len(json.dumps(draft, ensure_ascii=False)) <= budget:
                candidate = draft
        for turn in reversed(self.recent_turns(3)):
            item = {"when": turn["when"], "user": turn["user"][:110],
                    "lia": turn["lia"][:100]}
            draft = dict(candidate)
            draft["recent"] = [item] + candidate["recent"]
            if len(json.dumps(draft, ensure_ascii=False)) <= budget:
                candidate = draft
        return json.dumps(candidate, ensure_ascii=False, separators=(",", ":"))

    def stats(self) -> tuple[int, int]:
        with self._db() as db:
            turns = db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            actions = db.execute(
                "SELECT COUNT(*) FROM action_receipts WHERE proof_kind!='legacy_unassessed'"
            ).fetchone()[0]
        return turns, actions

    def clear_all(self) -> None:
        """Explicit user operation, never triggered by the LLM."""
        with self._db() as db:
            db.execute("DELETE FROM conversations")
            db.execute("DELETE FROM action_receipts")
            # The adaptive vocabulary belongs to the same opt-in
            # Second Brain. Erasing memory also erases learned corrections.
            known = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' "
                "AND name='speech_corrections'").fetchone()
            if known:
                db.execute("DELETE FROM speech_corrections")
        with self._db() as db:
            db.execute("VACUUM")
