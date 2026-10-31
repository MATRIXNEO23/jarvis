"""Local, separately persisted user preferences and operation evidence.

Two distinct databases: explicit user preferences and a typed operation ledger.
Project facts remain in workspace_memory; conversation remains in SecondBrain.
Neither database stores executable commands or grants action permissions.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import re
import sqlite3

from settings import default_path


class MemoryBoundaryError(ValueError):
    pass


_PREFERENCE_VALUES = {
    "response_length": frozenset({"brief", "balanced", "detailed"}),
    "interaction": frozenset({"voice", "text", "both"}),
    "language": frozenset({"it", "en", "es"}),
}
_SECRETS = re.compile(
    r"\b(?:password|passphrase|api[_\s-]?hash|token|chiave\s+api|"
    r"codice\s+otp|pin)\b", re.I,
)
_OPERATION_STATES = frozenset({
    "requested", "running", "reported", "verified",
    "failed", "interrupted", "uncertain",
})


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def _connect(path: Path):
    db = sqlite3.connect(str(path), timeout=5)
    try:
        db.execute("PRAGMA busy_timeout=5000")
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class PreferenceStore:
    """Only *explicitly confirmed* typed preferences. Never infer from dialogue."""

    def __init__(self, path: Path | None = None):
        self.path = (Path(path) if path is not None
                     else default_path().with_name("jarvis_preferences.sqlite3"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS preferences(
                key TEXT PRIMARY KEY, value TEXT NOT NULL,
                source TEXT NOT NULL CHECK(source='user_confirmed'),
                updated_utc TEXT NOT NULL)""")

    def set(self, key: str, value: str, *, user_confirmed: bool = False) -> bool:
        if user_confirmed is not True:
            raise MemoryBoundaryError("Serve una conferma esplicita dell'utente.")
        if (not isinstance(key, str) or not isinstance(value, str)
                or key not in _PREFERENCE_VALUES
                or value not in _PREFERENCE_VALUES[key]):
            raise MemoryBoundaryError("Preferenza non consentita o valore non valido.")
        with _connect(self.path) as db:
            previous = db.execute("SELECT value FROM preferences WHERE key=?",
                                  (key,)).fetchone()
            if previous and previous[0] == value:
                return False
            db.execute("""INSERT INTO preferences(key,value,source,updated_utc)
                VALUES(?,?,'user_confirmed',?)
                ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,source=excluded.source,
                updated_utc=excluded.updated_utc""", (key, value, _now()))
        return True

    def remove(self, key: str, *, user_confirmed: bool = False) -> bool:
        if user_confirmed is not True or key not in _PREFERENCE_VALUES:
            raise MemoryBoundaryError("Rimozione non autorizzata.")
        with _connect(self.path) as db:
            return db.execute("DELETE FROM preferences WHERE key=?", (key,)).rowcount == 1

    def all(self) -> tuple[dict, ...]:
        with _connect(self.path) as db:
            rows = db.execute(
                "SELECT key,value,source,updated_utc FROM preferences "
                "ORDER BY key").fetchall()
        return tuple(dict(zip(("key", "value", "source", "when"), row))
                     for row in rows)

    def context(self) -> tuple[dict, ...]:
        """Safe preference DATA for a prompt, never commands or project facts."""
        return tuple({"key": p["key"], "value": p["value"],
                      "source": "user_confirmed"} for p in self.all())


class OperationJournal:
    """Operation outcomes are not automatically verified just because a tool ran."""

    def __init__(self, path: Path | None = None):
        self.path = (Path(path) if path is not None
                     else default_path().with_name("jarvis_actions.sqlite3"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS action_attempts(
                id TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                origin TEXT NOT NULL,
                project_id TEXT NOT NULL DEFAULT '',
                state TEXT NOT NULL CHECK(state IN (
                    'requested','running','reported','verified',
                    'failed','interrupted','uncertain')),
                verification TEXT NOT NULL DEFAULT 'none',
                receipt TEXT NOT NULL DEFAULT '',
                detail TEXT NOT NULL DEFAULT '',
                created_utc TEXT NOT NULL, updated_utc TEXT NOT NULL
            )""")
            db.execute("""CREATE INDEX IF NOT EXISTS action_attempts_time
                ON action_attempts(updated_utc DESC)""")
            # A process restart is not evidence that an in-flight action succeeded.
            db.execute("""UPDATE action_attempts SET state='interrupted',
                verification='none',detail='Stato sconosciuto dopo riavvio',
                updated_utc=? WHERE state IN ('requested','running')""", (_now(),))

    def begin(self, action: str, *, origin: str = "local",
              project_id: str = "") -> str:
        if (not isinstance(action, str) or not 1 <= len(action) <= 100
                or _SECRETS.search(action) or
                not re.fullmatch(r"[\w .:-]{1,100}", action, re.UNICODE)
                or origin not in ("local", "document", "planner")
                or not isinstance(project_id, str)
                or (project_id and not re.fullmatch("[a-f0-9]{32}", project_id))):
            raise MemoryBoundaryError("Descrizione operazione non valida.")
        ident = uuid4().hex
        when = _now()
        with _connect(self.path) as db:
            db.execute("""INSERT INTO action_attempts(
                id,action,origin,project_id,state,created_utc,updated_utc)
                VALUES(?,?,?,?,?,?,?)""",
                (ident, action, origin, project_id, "requested", when, when))
        return ident

    def running(self, ident: str) -> bool:
        with _connect(self.path) as db:
            result = db.execute("""UPDATE action_attempts
                SET state='running',updated_utc=?
                WHERE id=? AND state='requested'""", (_now(), ident))
        return result.rowcount == 1

    def finish(self, ident: str, outcome: str, *,
               receipt: str = "", detail: str = "",
               observed: bool = False) -> bool:
        """'verified' requires observed evidence plus a nonempty receipt.

        'reported' means the executor returned success without independent
        confirmation that the expected state occurred. No hallucinated receipt.
        """
        if outcome not in ("reported", "verified", "failed",
                           "interrupted", "uncertain"):
            raise MemoryBoundaryError("Esito dell'operazione non valido.")
        if observed is True and outcome != "verified":
            raise MemoryBoundaryError("La prova non corrisponde all'esito.")
        if outcome == "verified" and (observed is not True or
                                      not isinstance(receipt,str) or
                                      not re.fullmatch(r"[a-zA-Z0-9._:-]{3,120}", receipt)):
            raise MemoryBoundaryError("Manca una prova verificabile.")
        if (not isinstance(detail,str) or len(detail)>450
                or _SECRETS.search(detail)
                or not isinstance(receipt,str) or len(receipt)>120):
            raise MemoryBoundaryError("Dettagli dell'operazione non sicuri.")
        with _connect(self.path) as db:
            result = db.execute("""UPDATE action_attempts SET
                state=?,verification=?,receipt=?,detail=?,updated_utc=?
                WHERE id=? AND state IN ('requested','running')""",
                (outcome, "local_observation" if outcome=="verified" else "none",
                 receipt if outcome=="verified" else "",
                 detail[:450], _now(), ident))
        return result.rowcount == 1

    def recent(self, limit: int = 20, *, project_id: str | None = None) -> tuple[dict, ...]:
        count = min(max(int(limit),1),40)
        with _connect(self.path) as db:
            if project_id is None:
                rows=db.execute("""SELECT id,action,origin,project_id,state,
                    verification,receipt,detail,updated_utc FROM action_attempts
                    ORDER BY rowid DESC LIMIT ?""",(count,)).fetchall()
            else:
                rows=db.execute("""SELECT id,action,origin,project_id,state,
                    verification,receipt,detail,updated_utc FROM action_attempts
                    WHERE project_id=? ORDER BY rowid DESC LIMIT ?""",
                    (project_id,count)).fetchall()
        keys=("id","action","origin","project_id","status",
              "verification","receipt","detail","when")
        return tuple(dict(zip(keys,row)) for row in rows)
