"""Small durable WhatsApp-only inbox and zero-charge-mode send reservation.

The local counter is intentionally conservative: every attempted outbound
message consumes a slot, even if Meta returned a timeout. A local count cannot
prove that another tool has not used the same Business number's free allowance.
"""
from __future__ import annotations
from datetime import datetime,timezone
import os
from pathlib import Path
import sqlite3
import threading
import time
from settings import default_path

class WhatsAppStateError(RuntimeError): pass

class WhatsAppState:
    def __init__(self,path:Path|None=None,clock=time.time):
        self.path=Path(path) if path is not None else default_path().with_name(
            "whatsapp-inbox.sqlite3")
        self.clock=clock
        self._lock=threading.RLock()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._db() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS incoming(
                    id TEXT PRIMARY KEY, sender TEXT NOT NULL,
                    kind TEXT NOT NULL, text TEXT NOT NULL,
                    message_time INTEGER NOT NULL,
                    recorded INTEGER NOT NULL);
                CREATE INDEX IF NOT EXISTS incoming_sender_time
                    ON incoming(sender, message_time DESC);
                CREATE TABLE IF NOT EXISTS outbound(
                    nonce TEXT PRIMARY KEY, recipient TEXT NOT NULL,
                    period TEXT NOT NULL, started INTEGER NOT NULL,
                    status TEXT NOT NULL, message_id TEXT);
                CREATE INDEX IF NOT EXISTS outbound_period ON outbound(period);
            """)

    def _db(self):
        conn=sqlite3.connect(self.path,timeout=8)
        conn.execute("PRAGMA busy_timeout=8000")
        return conn

    def record_incoming(self,message_id:str,sender:str,kind:str,
                        text:str,when:int)->bool:
        """Insert before replying; duplicated webhook delivery cannot resubmit."""
        if (not isinstance(message_id,str) or not message_id.startswith("wamid.")
                or len(message_id)>250 or not sender.isdigit() or
                kind not in ("text","audio")
                or not isinstance(text,str) or len(text)>1000
                or type(when) is not int):
            raise WhatsAppStateError("Dati del messaggio non validi.")
        now=int(self.clock())
        if when>now+300 or when<now-30*86400:
            raise WhatsAppStateError("Data messaggio fuori limite.")
        with self._lock,self._db() as conn:
            try:
                conn.execute(
                    "INSERT INTO incoming(id,sender,kind,text,message_time,recorded) "
                    "VALUES(?,?,?,?,?,?)",
                    (message_id,sender,kind,text,when,now))
                return True
            except sqlite3.IntegrityError:
                return False

    def set_transcript(self,message_id:str,transcript:str)->None:
        if not isinstance(transcript,str) or len(transcript)>1000:
            raise WhatsAppStateError("Trascrizione non valida.")
        with self._lock,self._db() as conn:
            conn.execute("UPDATE incoming SET text=? WHERE id=?",
                         (transcript,message_id))

    def last_incoming(self,sender:str)->int:
        with self._lock,self._db() as conn:
            result=conn.execute(
                "SELECT MAX(message_time) FROM incoming WHERE sender=?",
                (sender,)).fetchone()
            return int(result[0]) if result and result[0] else 0

    def within_service_window(self,sender:str)->bool:
        stamp=self.last_incoming(sender)
        now=int(self.clock())
        # 2-minute safety margin; never send at the 24-hour boundary.
        return bool(stamp and 0<=now-stamp<24*3600-120)

    def recent(self,sender:str,limit:int=6)->tuple[tuple[str,str],...]:
        with self._lock,self._db() as conn:
            rows=conn.execute(
                "SELECT kind,text FROM incoming WHERE sender=? AND text<>'' "
                "ORDER BY message_time DESC LIMIT ?",
                (sender,max(1,min(10,limit)))).fetchall()
        return tuple((str(a),str(b)[:350]) for a,b in reversed(rows))

    def count(self,period:str)->int:
        with self._lock,self._db() as conn:
            return int(conn.execute(
                "SELECT COUNT(*) FROM outbound WHERE period=?",
                (period,)).fetchone()[0])

    def reserve_send(self,nonce:str,recipient:str,limit:int)->bool:
        """Local hard cap before ANY Cloud API POST. No retry of a nonce."""
        if (not isinstance(nonce,str) or not 8<=len(nonce)<=250 or
                not recipient.isdigit() or type(limit) is not int
                or not 0<=limit<=1000):
            raise WhatsAppStateError("Richiesta invio non valida.")
        if not self.within_service_window(recipient):
            raise WhatsAppStateError(
                "Finestra di risposta WhatsApp scaduta: niente template a pagamento.")
        now=datetime.fromtimestamp(self.clock(),tz=timezone.utc)
        period=now.strftime("%Y-%m")
        with self._lock,self._db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            used=conn.execute(
                "SELECT COUNT(*) FROM outbound WHERE period=?",
                (period,)).fetchone()[0]
            if not limit or used>=limit:
                conn.rollback()
                raise WhatsAppStateError(
                    "Budget gratuito locale esaurito o non autorizzato: non invio.")
            if conn.execute("SELECT 1 FROM outbound WHERE nonce=?",
                            (nonce,)).fetchone():
                conn.rollback()
                return False
            conn.execute(
                "INSERT INTO outbound(nonce,recipient,period,started,status) "
                "VALUES(?,?,?,?,?)",
                (nonce,recipient,period,int(self.clock()),"reserved"))
            conn.commit()
            return True

    def record_send_result(self,nonce:str,message_id:str|None)->None:
        with self._lock,self._db() as conn:
            conn.execute(
                "UPDATE outbound SET status=?, message_id=? WHERE nonce=? "
                "AND status='reserved'",
                ("sent" if message_id else "uncertain",message_id,nonce))
