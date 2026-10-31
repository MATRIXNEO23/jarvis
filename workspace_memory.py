"""JARVIS project-scoped Second Brain: indexed SQLite + durable continuity.

A project, the general chat and a Telegram contact are distinct partitions.
Historic v1 SecondBrain files are not modified or migrated automatically.
Every per-project Markdown snapshot is reconstructed from verified database
state, never composed by the language model or blindly replayed as commands.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
from uuid import uuid4

from settings import default_path


class WorkspaceError(ValueError):
    pass


MAX_TURN = 900
MAX_ANSWER = 1100
MAX_NOTE = 320
MAX_SUMMARY = 1800
_SECRET = re.compile(r"\b(?:password|passphrase|token|api[_\s-]?hash|codice\s+otp|pin)\b",re.I)
_WORDS = re.compile(r"[\w]{3,}",re.UNICODE)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _trim(s, limit):
    return " ".join(s.split())[:limit] if isinstance(s,str) else ""


def _project_id(value):
    return isinstance(value,str) and bool(re.fullmatch(r"[a-f0-9]{32}",value))


class WorkspaceMemory:
    """Small bounded retrieval; no persistent heap cache of conversation text."""

    def __init__(self,path: Path | None = None):
        self.path = Path(path) if path is not None else default_path().with_name(
            "jarvis_workspaces.sqlite3")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.continuities=self.path.parent/"projects"
        self._initialize()

    @contextmanager
    def _db(self):
        db=sqlite3.connect(str(self.path),timeout=6)
        try:
            db.execute("PRAGMA busy_timeout=6000")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _initialize(self):
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS projects(
                id TEXT PRIMARY KEY, name TEXT NOT NULL,
                active INTEGER NOT NULL CHECK(active IN(0,1)),
                summary TEXT NOT NULL DEFAULT '',
                created_utc TEXT NOT NULL, updated_utc TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL CHECK(scope IN('general','project','telegram')),
                scope_id TEXT NOT NULL,
                user_text TEXT NOT NULL, reply TEXT NOT NULL,
                kind TEXT NOT NULL, time_utc TEXT NOT NULL)""")
            db.execute("""CREATE INDEX IF NOT EXISTS msg_scope_recent
                ON messages(scope,scope_id,id DESC)""")
            db.execute("""CREATE TABLE IF NOT EXISTS telegram_events(
                peer_id INTEGER NOT NULL, direction TEXT NOT NULL
                CHECK(direction IN('incoming','outgoing')),
                message_id INTEGER NOT NULL, kind TEXT NOT NULL,
                text TEXT NOT NULL, read INTEGER NOT NULL DEFAULT 0,
                time_utc TEXT NOT NULL,
                PRIMARY KEY(peer_id,direction,message_id))""")
            db.execute("""CREATE INDEX IF NOT EXISTS tg_events_recent
                ON telegram_events(peer_id,time_utc DESC)""")
            db.execute("""CREATE TABLE IF NOT EXISTS telegram_outbox(
                id TEXT PRIMARY KEY, peer_id INTEGER NOT NULL,
                message TEXT NOT NULL, state TEXT NOT NULL
                CHECK(state IN('pending','sending','sent','uncertain')),
                receipt_id INTEGER, created_utc TEXT NOT NULL)""")
            db.execute("""CREATE INDEX IF NOT EXISTS tg_outbox_ready
                ON telegram_outbox(peer_id,state,created_utc)""")
            # Optional FTS5: built into common Windows Python distributions.
            # If unavailable, search only a small recent window by SQL.
            self.fts_available=True
            try:
                db.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS msg_fts
                    USING fts5(user_text,reply,content='messages',
                    content_rowid='id',tokenize='unicode61')""")
                db.execute("""CREATE TRIGGER IF NOT EXISTS msg_fts_insert
                    AFTER INSERT ON messages BEGIN
                    INSERT INTO msg_fts(rowid,user_text,reply)
                    VALUES(new.id,new.user_text,new.reply); END""")
                db.execute("""CREATE TRIGGER IF NOT EXISTS msg_fts_delete
                    AFTER DELETE ON messages BEGIN
                    INSERT INTO msg_fts(msg_fts,rowid,user_text,reply)
                    VALUES('delete',old.id,old.user_text,old.reply); END""")
            except sqlite3.OperationalError:
                self.fts_available=False

    def create_project(self,name:str) -> str:
        name=_trim(name,65)
        if not name or _SECRET.search(name):
            raise WorkspaceError("Nome del progetto non valido.")
        ident=uuid4().hex
        now=_now()
        with self._db() as db:
            db.execute("INSERT INTO projects(id,name,active,summary,created_utc,updated_utc)"
                       " VALUES(?,?,1,'',?,?)",(ident,name,now,now))
        self._save_snapshot(ident)
        return ident

    def project(self,ident:str):
        if not _project_id(ident):
            return None
        with self._db() as db:
            row=db.execute("SELECT id,name,active,summary,updated_utc"
                           " FROM projects WHERE id=?",(ident,)).fetchone()
        return ({"id":row[0],"name":row[1],"active":bool(row[2]),
                 "summary":row[3],"updated_utc":row[4]}
                if row else None)

    def projects(self,active_only=False,limit=60):
        with self._db() as db:
            query=("SELECT id,name,active,updated_utc FROM projects "
                   + ("WHERE active=1 " if active_only else "")
                   + "ORDER BY updated_utc DESC,id ASC LIMIT ?")
            rows=db.execute(query,(min(200,max(1,int(limit))),)).fetchall()
        return tuple({"id":r[0],"name":r[1],"active":bool(r[2]),
                      "updated_utc":r[3]} for r in rows)

    def set_active(self,ident:str,active:bool):
        if type(active) is not bool or not self.project(ident):
            raise WorkspaceError("Progetto inesistente o stato non valido.")
        with self._db() as db:
            db.execute("UPDATE projects SET active=?, updated_utc=? WHERE id=?",
                       (int(active),_now(),ident))
        self._save_snapshot(ident)

    def set_summary(self,ident:str,summary:str):
        if not self.project(ident):
            raise WorkspaceError("Progetto inesistente.")
        if not isinstance(summary,str) or len(summary)>MAX_SUMMARY or _SECRET.search(summary):
            raise WorkspaceError("Continuità troppo lunga o contenente credenziali.")
        with self._db() as db:
            db.execute("UPDATE projects SET summary=?, updated_utc=? WHERE id=?",
                       (_trim(summary,MAX_SUMMARY),_now(),ident))
        self._save_snapshot(ident)

    def add_turn(self,scope:str,scope_id:str,user:str,reply:str,kind="chat"):
        if scope not in ("general","project","telegram") or kind not in (
                "chat","action","clarify","error"):
            raise WorkspaceError("Tipo di memoria non valido.")
        if (scope=="project" and not self.project(scope_id)) or (
                scope=="general" and scope_id!="general") or (
                scope=="telegram" and (not scope_id.isdecimal() or int(scope_id)<=0)):
            raise WorkspaceError("Contesto di memoria non valido.")
        if _SECRET.search(str(user)) or _SECRET.search(str(reply)):
            return False
        u=_trim(user,MAX_TURN)
        a=_trim(reply,MAX_ANSWER)
        if not u or not a:
            return False
        with self._db() as db:
            db.execute("INSERT INTO messages(scope,scope_id,user_text,reply,kind,time_utc)"
                       " VALUES(?,?,?,?,?,?)",(scope,scope_id,u,a,kind,_now()))
            if scope=="project":
                db.execute("UPDATE projects SET updated_utc=? WHERE id=?",(_now(),scope_id))
        if scope=="project":
            self._save_snapshot(scope_id)
        return True

    def recent(self,scope,scope_id,limit=6):
        with self._db() as db:
            rows=db.execute(
                "SELECT user_text,reply,kind,time_utc FROM messages "
                "WHERE scope=? AND scope_id=? ORDER BY id DESC LIMIT ?",
                (scope,scope_id,min(12,max(0,int(limit))))).fetchall()
        return tuple({"utente":u,"jarvis":a,"tipo":k,"when":t}
                     for u,a,k,t in reversed(rows))

    def search(self,scope,scope_id,query,limit=5):
        if scope not in ("general","project","telegram"):
            return ()
        terms=list(dict.fromkeys(_WORDS.findall(_trim(query,170).casefold())))[:7]
        if not terms:
            return ()
        n=min(8,max(1,int(limit)))
        with self._db() as db:
            if self.fts_available:
                # Quote every token to prevent FTS query syntax injection.
                match=" OR ".join('"' + term.replace('"','""') + '"' for term in terms)
                rows=db.execute(
                    """SELECT m.user_text,m.reply,m.time_utc FROM msg_fts f
                       JOIN messages m ON m.id=f.rowid
                       WHERE msg_fts MATCH ? AND m.scope=? AND m.scope_id=?
                       ORDER BY bm25(msg_fts),m.id DESC LIMIT ?""",
                    (match,scope,scope_id,n)).fetchall()
            else:
                # Bounded fallback avoids loading every old conversation into RAM.
                rows=db.execute(
                    """SELECT user_text,reply,time_utc FROM messages
                       WHERE scope=? AND scope_id=? ORDER BY id DESC LIMIT 150""",
                    (scope,scope_id)).fetchall()
                rows=[r for r in rows if any(t in (r[0]+" "+r[1]).casefold()
                                               for t in terms)][:n]
        return tuple({"user":u[:160],"reply":a[:180],"when":t}
                     for u,a,t in rows)

    def prompt_context(self,scope,scope_id,query,budget=950):
        budget=max(160,min(1800,int(budget)))
        context={"recent":[],"evidence":[]}
        for row in self.recent(scope,scope_id,4):
            item={"utente":row["utente"][:115],"jarvis":row["jarvis"][:140],
                  "tipo":row["tipo"]}
            proposed={**context,"recent":context["recent"]+[item]}
            if len(json.dumps(proposed,ensure_ascii=False))<=budget:
                context=proposed
        for row in self.search(scope,scope_id,query,4):
            item={"source":"conversation","when":row["when"],
                  "fact":"Utente: "+row["user"]+" | Jarvis: "+row["reply"]}
            proposed={**context,"evidence":context["evidence"]+[item]}
            if len(json.dumps(proposed,ensure_ascii=False))<=budget:
                context=proposed
        if scope=="project":
            project=self.project(scope_id)
            if project:
                context["project"]=project["name"][:65]
                if project["summary"]:
                    summary=project["summary"][:280]
                    if len(json.dumps({**context,"state":summary},ensure_ascii=False))<=budget:
                        context["state"]=summary
        return json.dumps(context,ensure_ascii=False,separators=(",",":"))

    def continuity_file(self,ident):
        if not _project_id(ident):
            raise WorkspaceError("Progetto inesistente.")
        return self.continuities/ident/"CONTINUITA.md"

    def _save_snapshot(self,ident):
        project=self.project(ident)
        if not project:
            raise WorkspaceError("Progetto inesistente.")
        history=self.recent("project",ident,8)
        lines=[
            "# Continuità — "+project["name"],
            "",
            "ID progetto: "+ident,
            "Stato: "+("attivo" if project["active"] else "archiviato"),
            "Aggiornato (UTC): "+project["updated_utc"],
            "",
            "## Stato consolidato dall'utente",
            project["summary"] or "(nessuno stato consolidato fornito)",
            "",
            "## Ultimi scambi (estratto automatico, non decisioni verificate)",
        ]
        for item in history:
            lines.extend([
                "", "- ["+item["when"]+"] Utente: "+item["utente"][:240],
                "  - JARVIS: "+item["jarvis"][:260],
            ])
        contents="\n".join(lines)+"\n"
        target=self.continuity_file(ident)
        target.parent.mkdir(parents=True,exist_ok=True)
        # Last valid generation remains recoverable if a write fails.
        if target.is_file():
            backup=target.with_suffix(".previous.md")
            backup.write_bytes(target.read_bytes())
        temp=target.with_suffix(".pending")
        try:
            temp.write_text(contents,encoding="utf-8")
            os.replace(temp,target)
        finally:
            if temp.exists():
                temp.unlink()

    def note_for_contact(self,peer_id:int,message:str) -> str:
        if type(peer_id) is not int or peer_id<=0:
            raise WorkspaceError("Contatto Telegram non autorizzato.")
        if (not isinstance(message,str) or len(message)>MAX_NOTE
                or not message.strip() or _SECRET.search(message)):
            raise WorkspaceError("Messaggio da riferire non valido.")
        note_id=uuid4().hex
        with self._db() as db:
            db.execute(
                "INSERT INTO telegram_outbox(id,peer_id,message,state,created_utc)"
                " VALUES(?,?,?,'pending',?)",
                (note_id,peer_id,_trim(message,MAX_NOTE),_now()))
        return note_id

    def pending_for_contact(self,peer_id:int):
        with self._db() as db:
            rows=db.execute(
                """SELECT id,message FROM telegram_outbox
                   WHERE peer_id=? AND state='pending'
                   ORDER BY created_utc,id LIMIT 3""",(peer_id,)).fetchall()
        return tuple({"id":i,"message":message} for i,message in rows)

    def reserve_notes(self,peer_id:int,note_ids):
        """Commit an attempt BEFORE external network send to prevent replay."""
        with self._db() as db:
            for ident in note_ids:
                r=db.execute(
                    "UPDATE telegram_outbox SET state='sending' "
                    "WHERE id=? AND peer_id=? AND state='pending'",
                    (ident,peer_id))
                if r.rowcount != 1:
                    raise WorkspaceError("Messaggio già inoltrato o non disponibile.")

    def finish_notes(self,peer_id,note_ids,receipt_id=None):
        # Unknown Telegram delivery must remain uncertain; never auto-retry.
        state="sent" if type(receipt_id) is int and receipt_id>0 else "uncertain"
        with self._db() as db:
            for ident in note_ids:
                db.execute(
                    "UPDATE telegram_outbox SET state=?,receipt_id=? "
                    "WHERE id=? AND peer_id=? AND state='sending'",
                    (state,receipt_id,ident,peer_id))

    def telegram_event(self,peer_id:int,direction:str,message_id:int,kind:str,text=""):
        if (type(peer_id) is not int or peer_id<=0
                or type(message_id) is not int or message_id<=0
                or direction not in ("incoming","outgoing")):
            raise WorkspaceError("Ricevuta Telegram non valida.")
        with self._db() as db:
            r=db.execute(
                """INSERT OR IGNORE INTO telegram_events(
                   peer_id,direction,message_id,kind,text,time_utc)
                   VALUES(?,?,?,?,?,?)""",
                (peer_id,direction,message_id,_trim(kind,28),
                 _trim(text,550),_now()))
        return bool(r.rowcount)

    def telegram_transcript(self,peer_id:int,message_id:int,text:str):
        """Attach locally recognized voice text only to that received event."""
        if not isinstance(text,str) or not text.strip():
            return False
        with self._db() as db:
            cur=db.execute(
                "UPDATE telegram_events SET text=? WHERE peer_id=? "
                "AND direction='incoming' AND message_id=? AND kind='voice'",
                (_trim(text,550),peer_id,message_id))
        return bool(cur.rowcount)

    def telegram_counts(self,peer_id:int):
        with self._db() as db:
            r=db.execute("""SELECT
                SUM(CASE WHEN direction='incoming' AND read=0 THEN 1 ELSE 0 END),
                SUM(CASE WHEN direction='incoming' THEN 1 ELSE 0 END),
                SUM(CASE WHEN direction='outgoing' THEN 1 ELSE 0 END)
                FROM telegram_events WHERE peer_id=?""",(peer_id,)).fetchone()
        return {"unread":int(r[0] or 0),"received":int(r[1] or 0),
                "replied":int(r[2] or 0)}

    def mark_telegram_read(self,peer_id:int):
        with self._db() as db:
            db.execute("UPDATE telegram_events SET read=1 "
                       "WHERE peer_id=? AND direction='incoming'",(peer_id,))

    def telegram_activity(self,peer_id:int,limit=16):
        with self._db() as db:
            rows=db.execute(
                "SELECT direction,kind,text,time_utc FROM telegram_events "
                "WHERE peer_id=? ORDER BY time_utc DESC,message_id DESC LIMIT ?",
                (peer_id,min(100,max(1,int(limit))))).fetchall()
        return tuple({"direction":d,"kind":k,"text":text,"when":when}
                     for d,k,text,when in rows)
