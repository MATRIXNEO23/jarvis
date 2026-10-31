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
import threading
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
        self._projection_lock=threading.RLock()
        self._initialize()
        self._recover_unfinished()

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
            if "trashed" not in {r[1] for r in db.execute("PRAGMA table_info(projects)")}: 
                db.execute("ALTER TABLE projects ADD COLUMN trashed INTEGER NOT NULL DEFAULT 0")
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
            db.execute("""CREATE TABLE IF NOT EXISTS workspace_session(
                key TEXT PRIMARY KEY, value TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS project_steps(
                id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
                title TEXT NOT NULL, source TEXT NOT NULL,
                status TEXT NOT NULL CHECK(
                    status IN ('planned','running','completed','failed','interrupted')),
                detail TEXT NOT NULL DEFAULT '', receipt TEXT NOT NULL DEFAULT '',
                created_utc TEXT NOT NULL, updated_utc TEXT NOT NULL)""")
            db.execute("""CREATE INDEX IF NOT EXISTS project_steps_recent
                ON project_steps(project_id,updated_utc DESC,id DESC)""")
            db.execute("""CREATE TABLE IF NOT EXISTS project_events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL, step_id TEXT NOT NULL DEFAULT '',
                kind TEXT NOT NULL CHECK(kind IN ('step','artifact')),
                title TEXT NOT NULL, status TEXT NOT NULL,
                detail TEXT NOT NULL, time_utc TEXT NOT NULL)""")
            db.execute("""CREATE INDEX IF NOT EXISTS project_events_recent
                ON project_events(project_id,id DESC)""")
            db.execute("""CREATE TABLE IF NOT EXISTS project_artifacts(
                project_id TEXT NOT NULL, path TEXT NOT NULL,
                verified_utc TEXT NOT NULL, PRIMARY KEY(project_id,path))""")
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
            row=db.execute("SELECT id,name,active,summary,updated_utc,trashed"
                           " FROM projects WHERE id=?",(ident,)).fetchone()
        return ({"id":row[0],"name":row[1],"active":bool(row[2]),
                 "summary":row[3],"updated_utc":row[4],
                 "trashed":bool(row[5])}
                if row else None)

    def select_project(self, ident=None):
        """Persist the current focus; None means general chat."""
        if ident is not None and (
                not self.project(ident) or self.project(ident)["trashed"]):
            raise WorkspaceError("Progetto da aprire inesistente o nel cestino.")
        with self._db() as db:
            db.execute(
                "INSERT OR REPLACE INTO workspace_session(key,value) "
                "VALUES('current_project',?)",(ident or "",))

    def current_project(self):
        """Restore the last selected project only if it still exists."""
        with self._db() as db:
            row=db.execute("SELECT value FROM workspace_session "
                           "WHERE key='current_project'").fetchone()
        ident=row[0] if row and row[0] else None
        return (ident if ident and self.project(ident)
                and not self.project(ident)["trashed"] else None)

    def projects(self,active_only=False,limit=60):
        with self._db() as db:
            query=("SELECT id,name,active,updated_utc FROM projects "
                   "WHERE trashed=0 "
                   + ("AND active=1 " if active_only else "")
                   + "ORDER BY updated_utc DESC,id ASC LIMIT ?")
            rows=db.execute(query,(min(200,max(1,int(limit))),)).fetchall()
        return tuple({"id":r[0],"name":r[1],"active":bool(r[2]),
                      "updated_utc":r[3]} for r in rows)

    def trashed_projects(self,limit=60):
        """Projects are hidden but recoverable; no file/database deletion."""
        with self._db() as db:
            rows=db.execute(
                "SELECT id,name,active,updated_utc FROM projects WHERE trashed=1 "
                "ORDER BY updated_utc DESC,id ASC LIMIT ?",
                (min(200,max(1,int(limit))),)).fetchall()
        return tuple({"id":r[0],"name":r[1],"active":bool(r[2]),
                      "updated_utc":r[3]} for r in rows)

    def rename_project(self,ident,new_name):
        """Rename the same UUID; keep messages, documents and steps intact."""
        from project_voice import safe_project_name
        try:
            new_name=safe_project_name(new_name)
        except ValueError as exc:
            raise WorkspaceError(str(exc)) from exc
        project=self.project(ident)
        if not project or project["trashed"]:
            raise WorkspaceError("Progetto inesistente o nel cestino.")
        if any(p["name"].casefold()==new_name.casefold() and p["id"]!=ident
               for p in self.projects(limit=200)):
            raise WorkspaceError("Un altro progetto possiede già questo nome.")
        if project["name"]==new_name:
            return False
        now=_now()
        with self._db() as db:
            db.execute("UPDATE projects SET name=?,updated_utc=? "
                       "WHERE id=? AND trashed=0",(new_name,now,ident))
        folder=self.continuities/ident
        self._atomic_file(folder/"PROGETTO.txt",
            "Progetto: "+new_name+"\nID: "+ident+"\n"
            "Cartella documenti: files\n"
            "La memoria è in CONTINUITA.md, STATO.json e PASSI.md.\n")
        self._save_snapshot(ident)
        return True

    def trash_project(self,ident):
        """Reversible logical deletion. NEVER erase the project folder."""
        project=self.project(ident)
        if not project or project["trashed"]:
            raise WorkspaceError("Progetto non trovato o già nel cestino.")
        now=_now()
        with self._db() as db:
            db.execute("UPDATE projects SET trashed=1,active=0,updated_utc=? "
                       "WHERE id=?",(now,ident))
            db.execute("UPDATE workspace_session SET value='' "
                       "WHERE key='current_project' AND value=?",(ident,))
        self._save_snapshot(ident)

    def restore_project(self,ident):
        """Restore from Jarvis's logical trash with the same stable ID."""
        project=self.project(ident)
        if not project or not project["trashed"]:
            raise WorkspaceError("Progetto non trovato nel cestino.")
        if any(p["name"].casefold()==project["name"].casefold()
               for p in self.projects(limit=200)):
            raise WorkspaceError(
                "Esiste già un progetto con lo stesso nome. "
                "Rinominalo prima di ripristinare.")
        with self._db() as db:
            db.execute("UPDATE projects SET trashed=0,active=1,updated_utc=? "
                       "WHERE id=?",(_now(),ident))
        self._save_snapshot(ident)

    def set_active(self,ident:str,active:bool):
        if (type(active) is not bool or not self.project(ident)
                or self.project(ident)["trashed"]):
            raise WorkspaceError("Progetto inesistente, eliminato o stato non valido.")
        with self._db() as db:
            db.execute("UPDATE projects SET active=?, updated_utc=? WHERE id=?",
                       (int(active),_now(),ident))
        self._save_snapshot(ident)

    def set_summary(self,ident:str,summary:str):
        if not self.project(ident) or self.project(ident)["trashed"]:
            raise WorkspaceError("Progetto inesistente o nel cestino.")
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
        if (scope=="project" and (not self.project(scope_id)
                                   or self.project(scope_id)["trashed"])) or (
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
            self._save_snapshot(scope_id, steps_changed=False)
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
                # Include verified operational state, not GPT-inferred achievements.
                steps=self.project_steps(scope_id,limit=5)
                compact=[{"step":x["title"][:90],"status":x["status"],
                          "detail":x["detail"][:120]} for x in steps]
                for count in range(len(compact),0,-1):
                    candidate={**context,"steps":compact[:count]}
                    if len(json.dumps(candidate,ensure_ascii=False))<=budget:
                        context=candidate
                        break
        return json.dumps(context,ensure_ascii=False,separators=(",",":"))

    def project_directory(self,ident):
        """Stable folder inside AppData/Jarvis/projects; never use spoken names as paths."""
        if not _project_id(ident) or not self.project(ident):
            raise WorkspaceError("Progetto inesistente.")
        return self.continuities/ident

    def project_files_directory(self,ident):
        """Authoritative destination for documents of this single project."""
        folder=self.project_directory(ident)/"files"
        if folder.is_symlink():
            raise WorkspaceError("Cartella file del progetto non sicura.")
        folder.mkdir(parents=True,exist_ok=True)
        return folder

    def continuity_file(self,ident):
        if not _project_id(ident):
            raise WorkspaceError("Progetto inesistente.")
        return self.continuities/ident/"CONTINUITA.md"

    def project_steps(self, ident, limit=40):
        if not self.project(ident):
            raise WorkspaceError("Progetto inesistente.")
        with self._db() as db:
            rows=db.execute(
                "SELECT id,title,source,status,detail,receipt,created_utc,updated_utc "
                "FROM project_steps WHERE project_id=? "
                "ORDER BY updated_utc DESC,rowid DESC LIMIT ?",
                (ident,min(100,max(1,int(limit))))).fetchall()
        return tuple(dict(zip(("id","title","source","status","detail","receipt",
                               "created_utc","updated_utc"),row)) for row in rows)

    def begin_step(self, ident, title, *, source="jarvis", planned=False):
        """Record before dispatch. An unfinished step is never silently marked done."""
        if not self.project(ident):
            raise WorkspaceError("Progetto inesistente.")
        if (not isinstance(title,str) or not title.strip()
                or len(title)>240 or _SECRET.search(title)
                or not isinstance(source,str) or not source.isidentifier()
                or len(source)>30 or type(planned) is not bool):
            raise WorkspaceError("Passo non valido o potenzialmente sensibile.")
        ticket=uuid4().hex
        now=_now()
        state="planned" if planned else "running"
        label=_trim(title,240)
        with self._db() as db:
            db.execute(
                "INSERT INTO project_steps(id,project_id,title,source,status,created_utc,updated_utc) "
                "VALUES(?,?,?,?,?,?,?)",
                (ticket,ident,label,source,state,now,now))
            db.execute(
                "INSERT INTO project_events(project_id,step_id,kind,title,status,detail,time_utc) "
                "VALUES(?,?,'step',?,?,?,?)",
                (ident,ticket,label,state,"",now))
            db.execute("UPDATE projects SET updated_utc=? WHERE id=?",(now,ident))
        self._save_snapshot(ident)
        return ticket

    def finish_step(self, ident, ticket, status, detail="", *, receipt=""):
        """Idempotent terminal transition, backed by one SQLite transaction."""
        if not self.project(ident) or not _project_id(ticket):
            raise WorkspaceError("Progetto o passo non valido.")
        if status not in ("completed","failed","interrupted"):
            raise WorkspaceError("Stato del passo non valido.")
        # Sensitive error/output text must never be persisted.
        detail=("[Dettaglio omesso per sicurezza]"
                if _SECRET.search(str(detail)) else _trim(str(detail),480))
        receipt=_trim(str(receipt),120) if receipt else ""
        if status=="completed" and not receipt:
            raise WorkspaceError("Un passo completato richiede una ricevuta verificabile.")
        now=_now()
        with self._db() as db:
            cur=db.execute(
                "UPDATE project_steps SET status=?,detail=?,receipt=?,updated_utc=? "
                "WHERE id=? AND project_id=? AND status IN ('planned','running')",
                (status,detail,receipt,now,ticket,ident))
            if cur.rowcount!=1:
                return False
            row=db.execute(
                "SELECT title FROM project_steps WHERE id=?",(ticket,)).fetchone()
            db.execute(
                "INSERT INTO project_events(project_id,step_id,kind,title,status,detail,time_utc) "
                "VALUES(?,?,'step',?,?,?,?)",
                (ident,ticket,row[0],status,detail,now))
            db.execute("UPDATE projects SET updated_utc=? WHERE id=?",(now,ident))
        self._save_snapshot(ident)
        return True

    def record_artifact(self, ident, path):
        """Only register a file that really exists; never copy or move it."""
        if not self.project(ident):
            raise WorkspaceError("Progetto inesistente.")
        target=Path(path).resolve(strict=True)
        if (not target.is_file() or
                any(_SECRET.search(part) for part in target.parts) or
                target.suffix.casefold() in (".dpapi",".key",".pem")):
            raise WorkspaceError("File non verificabile o sensibile.")
        now=_now()
        with self._db() as db:
            cur=db.execute(
                "INSERT OR IGNORE INTO project_artifacts(project_id,path,verified_utc) "
                "VALUES(?,?,?)",(ident,str(target),now))
            if cur.rowcount:
                db.execute(
                    "INSERT INTO project_events(project_id,kind,title,status,detail,time_utc) "
                    "VALUES(?,'artifact',?,'verified',?,?)",
                    (ident,target.name,str(target)[:480],now))
                db.execute("UPDATE projects SET updated_utc=? WHERE id=?",(now,ident))
        if cur.rowcount:
            self._save_snapshot(ident)
        return bool(cur.rowcount)

    def _recover_unfinished(self):
        """On restart, stop stale plans; never pretend they finished or replay."""
        now=_now()
        with self._db() as db:
            rows=db.execute(
                "SELECT id,project_id,title FROM project_steps "
                "WHERE status IN ('planned','running')").fetchall()
            for ticket,ident,title in rows:
                db.execute(
                    "UPDATE project_steps SET status='interrupted', "
                    "detail='Sessione precedente interrotta: verificare prima di ripetere.', "
                    "updated_utc=? WHERE id=?",(now,ticket))
                db.execute(
                    "INSERT INTO project_events(project_id,step_id,kind,title,status,detail,time_utc) "
                    "VALUES(?,?,'step',?,'interrupted',?,?)",
                    (ident,ticket,title,"Interrotto al riavvio: risultato non verificato.",now))
            ids={ident for _,ident,_ in rows}
            # Regenerate projections absent after migration or a crash.
            existing=db.execute("""SELECT p.id, p.name, p.active, p.trashed, p.summary,
                COALESCE((SELECT MAX(id) FROM project_events
                          WHERE project_id=p.id),0),
                COALESCE((SELECT MAX(id) FROM messages
                          WHERE scope='project' AND scope_id=p.id),0)
                FROM projects p""").fetchall()
        for ident,name,active,trashed,summary,last_event,last_message in existing:
            folder=self.continuities/ident
            state_file=folder/"STATO.json"
            try:
                with state_file.open("r",encoding="utf-8") as handle:
                    state=json.load(handle)
                if (state.get("name")!=name
                        or state.get("trashed")!=bool(trashed)
                        or state.get("last_event_id")!=last_event
                        or state.get("last_message_id")!=last_message
                        or state.get("summary_from_user")!=summary
                        or state.get("active")!=bool(active)
                        or any(not (folder/name).is_file() for name in (
                            "CONTINUITA.md","PASSI.md","ARTIFATTI.md",
                            "EVENTI.jsonl","PROGETTO.txt"))):
                    ids.add(ident)
            except (OSError,ValueError,TypeError,AttributeError):
                ids.add(ident)
        for ident in ids:
            self._save_snapshot(ident)

    @staticmethod
    def _atomic_file(path, content, *, keep_previous=False):
        path.parent.mkdir(parents=True,exist_ok=True)
        temp=path.with_name(path.name+"."+uuid4().hex+".pending")
        try:
            with temp.open("w",encoding="utf-8",newline="\n") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            if keep_previous and path.is_file():
                backup=path.with_suffix(".previous.md")
                # Old snapshot remains available across interrupted writes.
                backup.write_bytes(path.read_bytes())
            os.replace(temp,path)
        finally:
            if temp.exists():
                temp.unlink()

    def _save_snapshot(self, ident, *, steps_changed=True):
        """SQLite is canonical; projections can be rebuilt at any restart."""
        with self._projection_lock:
            project=self.project(ident)
            if not project:
                raise WorkspaceError("Progetto inesistente.")
            history=self.recent("project",ident,8)
            steps=self.project_steps(ident,limit=80)
            with self._db() as db:
                files=db.execute(
                    "SELECT path,verified_utc FROM project_artifacts "
                    "WHERE project_id=? ORDER BY verified_utc DESC,path LIMIT 70",
                    (ident,)).fetchall()
                events=db.execute(
                    "SELECT id,step_id,kind,title,status,detail,time_utc "
                    "FROM project_events WHERE project_id=? ORDER BY id DESC LIMIT 100",
                    (ident,)).fetchall()
                counters=db.execute(
                    "SELECT status,COUNT(*) FROM project_steps "
                    "WHERE project_id=? GROUP BY status",(ident,)).fetchall()
                message_seq=db.execute(
                    "SELECT COALESCE(MAX(id),0) FROM messages "
                    "WHERE scope='project' AND scope_id=?",(ident,)).fetchone()[0]
            counts=dict(counters)
            lines=[
                "# Continuità — "+project["name"],
                "",
                "ID progetto: "+ident,
                "Stato: "+("nel cestino" if project["trashed"]
                          else "attivo" if project["active"] else "archiviato"),
                "Aggiornato (UTC): "+project["updated_utc"],
                "",
                "## Stato consolidato dall'utente",
                project["summary"] or "(nessuno stato consolidato fornito)",
                "",
                "## Avanzamento operativo (registrato, non inventato da GPT)",
            ]
            if not steps:
                lines.append("(nessun passo operativo ancora registrato)")
            for item in steps[:18]:
                lines.append("- ["+item["status"].upper()+"] "+item["title"]
                             +(" — "+item["detail"][:180] if item["detail"] else ""))
            lines.extend(["","## File verificati"])
            lines.extend("- "+path for path,_ in files[:18])
            if not files:
                lines.append("(nessun file prodotto verificato)")
            lines.extend(["","## Ultimi scambi (estratto automatico, non decisioni verificate)"])
            for item in history:
                lines.extend(["", "- ["+item["when"]+"] Utente: "+item["utente"][:240],
                              "  - JARVIS: "+item["jarvis"][:260]])
            folder=self.continuities/ident
            self.project_files_directory(ident)
            identity=folder/"PROGETTO.txt"
            if (not identity.is_file() or
                    not identity.read_text(encoding="utf-8").startswith(
                        "Progetto: "+project["name"]+"\n")):
                self._atomic_file(identity,
                    "Progetto: "+project["name"]+"\n"
                    "ID: "+ident+"\n"
                    "Cartella documenti: files\n"
                    "La memoria è in CONTINUITA.md, STATO.json e PASSI.md.\n")
            self._atomic_file(folder/"CONTINUITA.md","\n".join(lines)+"\n",
                              keep_previous=True)
            state={
                "schema_version":1, "project_id":ident,"name":project["name"],
                "last_event_id":events[0][0] if events else 0,
                "last_message_id":message_seq,
                "active":project["active"],"trashed":project["trashed"],
                "updated_utc":project["updated_utc"],
                "summary_from_user":project["summary"],
                "counts":counts,
                "unfinished":[{"id":x["id"],"title":x["title"],"status":x["status"]}
                              for x in steps if x["status"] in ("planned","running","interrupted")][:20],
                "recent_completed":[{"id":x["id"],"title":x["title"],"detail":x["detail"],
                                     "receipt":x["receipt"]}
                                    for x in steps if x["status"]=="completed"][:12],
            }
            self._atomic_file(folder/"STATO.json",
                              json.dumps(state,ensure_ascii=False,indent=2)+"\n")
            if not steps_changed:
                return
            tasks=["# Passi del progetto — "+project["name"],"",
                   "Fonte: ricevute locali e registro; i passi pianificati non sono completati.",""]
            tasks.extend("- ["+x["status"]+"] "+x["title"]
                         +(" — "+x["detail"] if x["detail"] else "")
                         +(" (ricevuta "+x["receipt"]+")" if x["receipt"] else "")
                         for x in steps)
            self._atomic_file(folder/"PASSI.md","\n".join(tasks)+"\n")
            artifact_lines=["# File verificati — "+project["name"],"",
                            "Questo elenco registra riferimenti a file esistenti, "
                            "non li copia né li sposta.",""]
            artifact_lines.extend("- ["+when+"] "+p for p,when in files)
            self._atomic_file(folder/"ARTIFATTI.md","\n".join(artifact_lines)+"\n")
            # Capped read-friendly projection; complete append-only evidence is in SQLite.
            audit=[]
            for seq,ticket,kind,title,status,detail,when in reversed(events):
                audit.append(json.dumps({"id":seq,"step_id":ticket,"kind":kind,
                    "title":title,"status":status,"detail":detail,"utc":when},
                    ensure_ascii=False,separators=(",",":")))
            self._atomic_file(folder/"EVENTI.jsonl","\n".join(audit)+("\n" if audit else ""))

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
