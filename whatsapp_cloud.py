"""Official WhatsApp Business Cloud API: explicit service messages only.

No templates, calls, payment flow, browser automation or account scraping.
All requests go to a fixed Meta HTTPS host. Network errors are ambiguous:
the caller must never retry a send automatically.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import secrets
import urllib.request
import urllib.parse
from whatsapp_security import validate_credentials

class WhatsAppCloudError(RuntimeError): pass
_MEDIA_ID=re.compile(r"^[A-Za-z0-9_-]{5,180}$")
_WAMID=re.compile(r"^wamid\.[A-Za-z0-9_:\-=./+]{6,240}$")
_ALLOWED_MEDIA_DOMAINS=("lookaside.fbsbx.com","lookaside.facebook.com")

def _json_response(data:bytes):
    if len(data)>64_000:
        raise WhatsAppCloudError("Risposta Meta troppo grande.")
    try:
        return json.loads(data.decode("utf-8"))
    except (ValueError,UnicodeError) as exc:
        raise WhatsAppCloudError("Risposta Cloud API non valida.") from exc

class CloudTransport:
    def request(self,url:str,method:str,headers:dict,body:bytes|None=None,
                limit:int=64_000)->bytes:
        target=urllib.parse.urlsplit(url)
        if (target.scheme!="https" or target.username or target.password or
                target.port not in (None,443)):
            raise WhatsAppCloudError("URL HTTPS non consentito.")
        host=(target.hostname or "").lower()
        if host not in ("graph.facebook.com",*_ALLOWED_MEDIA_DOMAINS):
            raise WhatsAppCloudError("Host Meta inatteso; download rifiutato.")
        req=urllib.request.Request(url,data=body,headers=headers,method=method)
        try:
            with urllib.request.urlopen(req,timeout=25) as response:
                # Redirects can otherwise open private endpoints. Check the
                # final URL too, regardless of which host was requested.
                final=urllib.parse.urlsplit(response.geturl())
                if (final.scheme!="https" or final.hostname not in
                        ("graph.facebook.com",*_ALLOWED_MEDIA_DOMAINS)):
                    raise WhatsAppCloudError("Reindirizzamento fuori dai server Meta.")
                data=response.read(limit+1)
                if len(data)>limit:
                    raise WhatsAppCloudError("File Meta oltre il limite.")
                return data
        except WhatsAppCloudError:
            raise
        except Exception as exc:
            raise WhatsAppCloudError(
                "Esito rete Meta incerto. Controlla WhatsApp; non riprovare automaticamente.") from exc

class WhatsAppCloud:
    def __init__(self,credentials:dict,transport=None):
        self.credentials=validate_credentials(credentials)
        self.transport=transport or CloudTransport()
        self.root=("https://graph.facebook.com/"
                   +self.credentials["api_version"]+"/")
        self.phone_id=self.credentials["phone_number_id"]

    def _headers(self):
        return {"Authorization":"Bearer "+self.credentials["access_token"]}

    def _post_json(self,path:str,payload:dict)->dict:
        body=json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode("utf-8")
        data=self.transport.request(
            self.root+path,"POST",
            {**self._headers(),"Content-Type":"application/json"},body)
        result=_json_response(data)
        if not isinstance(result,dict):
            raise WhatsAppCloudError("Risposta invio Meta inattesa.")
        return result

    def _message(self,phone:str,kind:str,detail:dict)->str:
        if not isinstance(phone,str) or not re.fullmatch(r"[1-9][0-9]{7,14}",phone):
            raise WhatsAppCloudError("Numero destinatario non valido.")
        response=self._post_json(self.phone_id+"/messages",{
            "messaging_product":"whatsapp",
            "recipient_type":"individual",
            "to":phone,
            "type":kind,
            kind:detail,
        })
        messages=response.get("messages")
        ident=messages[0].get("id") if isinstance(messages,list) and messages and isinstance(
            messages[0],dict) else None
        if not isinstance(ident,str) or not ident.startswith("wamid."):
            raise WhatsAppCloudError("Ricevuta Meta mancante; nessun reinvio automatico.")
        return ident

    def send_text(self,phone:str,text:str)->str:
        if (not isinstance(text,str) or not 1<=len(text.strip())<=1000
                or any(ord(c)==0 for c in text)):
            raise WhatsAppCloudError("Messaggio di testo non valido.")
        return self._message(phone,"text",{"preview_url":False,"body":text.strip()})

    def upload_ogg(self,path:Path)->str:
        file=Path(path)
        if file.suffix.lower()!=".ogg" or file.is_symlink():
            raise WhatsAppCloudError("Serve un audio OGG/Opus locale.")
        content=file.read_bytes()
        if not 60<=len(content)<=3_000_000 or not content.startswith(b"OggS"):
            raise WhatsAppCloudError("Audio OGG mancante o non riconosciuto.")
        boundary="jarvis"+secrets.token_hex(16)
        b=boundary.encode("ascii")
        body=(b"--"+b+b"\r\nContent-Disposition: form-data; name=\"messaging_product\"\r\n\r\nwhatsapp\r\n"+
              b"--"+b+b"\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\naudio/ogg\r\n"+
              b"--"+b+b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"jarvis.ogg\"\r\nContent-Type: audio/ogg\r\n\r\n"+
              content+b"\r\n--"+b+b"--\r\n")
        data=self.transport.request(
            self.root+self.phone_id+"/media","POST",{
                **self._headers(),"Content-Type":"multipart/form-data; boundary="+boundary
            },body)
        media=_json_response(data)
        ident=media.get("id") if isinstance(media,dict) else None
        if not isinstance(ident,str) or not _MEDIA_ID.fullmatch(ident):
            raise WhatsAppCloudError("Media ID Meta non valido.")
        return ident

    def send_ogg(self,phone:str,path:Path)->str:
        media_id=self.upload_ogg(path)
        return self._message(phone,"audio",{"id":media_id,"voice":True})

    def get_audio(self,media_id:str)->bytes:
        if not isinstance(media_id,str) or not _MEDIA_ID.fullmatch(media_id):
            raise WhatsAppCloudError("Media ID ricevuto non valido.")
        metadata=_json_response(self.transport.request(
            self.root+media_id,"GET",self._headers()))
        if not isinstance(metadata,dict) or metadata.get("mime_type") not in (
                "audio/ogg","audio/opus","audio/mpeg","audio/mp4","audio/aac"):
            raise WhatsAppCloudError("Formato audio ricevuto non supportato.")
        if type(metadata.get("file_size")) is int and metadata["file_size"]>5_000_000:
            raise WhatsAppCloudError("Vocale ricevuto troppo grande.")
        url=metadata.get("url")
        if not isinstance(url,str):
            raise WhatsAppCloudError("URL media Meta assente.")
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!="https" or parsed.hostname not in _ALLOWED_MEDIA_DOMAINS:
            raise WhatsAppCloudError("URL media non verificabile.")
        return self.transport.request(url,"GET",self._headers(),limit=5_000_000)
