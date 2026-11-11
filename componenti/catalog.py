"""Componenti esterni e chiavi API: cosa serve, come controllarlo, come installarlo.

Ogni voce dice a quale add-on appartiene (o «base» per Lumi stessa), come si
verifica se c'è, il link ufficiale (modificabile dall'utente) e il modo di
installarla da dentro Lumi:
- "pip": pacchetto Python per l'utente corrente (stesso Python di Lumi);
- "script": programma di installazione già incluso nel pacchetto;
- "winget": programma ufficiale tramite Gestione pacchetti di Windows.
Niente parte senza conferma dell'utente.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _module(name):
    return lambda: importlib.util.find_spec(name) is not None


def _program(name):
    return lambda: shutil.which(name) is not None


def _webview2() -> bool:
    if os.name != "nt":
        return False
    import winreg
    key = r"SOFTWARE\{}Microsoft\EdgeUpdate\Clients\{{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}}"
    for hive, wow in ((winreg.HKEY_LOCAL_MACHINE, "WOW6432Node\\"), (winreg.HKEY_LOCAL_MACHINE, ""),
                      (winreg.HKEY_CURRENT_USER, "")):
        try:
            with winreg.OpenKey(hive, key.format(wow)) as handle:
                version, _ = winreg.QueryValueEx(handle, "pv")
                if version and version != "0.0.0.0":
                    return True
        except OSError:
            continue
    return False


def _vosk_ready() -> bool:
    if importlib.util.find_spec("vosk") is None:
        return False
    try:
        from voice_control import model_directory
        return Path(model_directory()).is_dir()
    except Exception:
        return False


def _gpt_sdk() -> bool:
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Jarvis" / "runtime" / "siwc"
    return (base / "packages" / "local" / "dist" / "index.js").is_file()


# id, nome, add-on («base» = Lumi), a cosa serve, controllo, installazione, link ufficiale
COMPONENTS = (
    {"id": "telethon", "name": "Telethon (libreria Telegram)", "addon": "telegram",
     "purpose": "Collegamento al tuo account Telegram.", "check": _module("telethon"),
     "kind": "pip", "packages": ["Telethon>=1.36,<2"],
     "link": "https://pypi.org/project/Telethon/", "online": False},
    {"id": "ffmpeg", "name": "FFmpeg", "addon": "telegram",
     "purpose": "Note vocali Telegram (OGG/Opus).", "check": _program("ffmpeg"),
     "kind": "winget", "winget": "Gyan.FFmpeg",
     "link": "https://ffmpeg.org/download.html#build-windows", "online": False,
     "restart": True},
    {"id": "webview2", "name": "Microsoft Edge WebView2 Runtime", "addon": "musica",
     "purpose": "Riquadro video (YouTube e video offline).", "check": _webview2,
     "kind": "winget", "winget": "Microsoft.EdgeWebView2Runtime",
     "link": "https://developer.microsoft.com/microsoft-edge/webview2/", "online": False},
    {"id": "vosk", "name": "Riconoscimento vocale offline (Vosk + modello italiano)", "addon": "base",
     "purpose": "Comandi a voce senza internet.", "check": _vosk_ready,
     "kind": "pip+script", "packages": ["vosk==0.3.45", "sounddevice==0.5.3"],
     "script": ["installa_modello_voce.py"],
     "link": "https://alphacephei.com/vosk/models", "online": False},
    {"id": "edge_tts", "name": "Voci Microsoft Edge (online)", "addon": "base",
     "purpose": "Voci Isabella, Elsa, Diego, Giuseppe: gratuite ma il testo va a Microsoft.",
     "check": _module("edge_tts"), "kind": "pip", "packages": ["edge-tts>=7.2,<8"],
     "link": "https://pypi.org/project/edge-tts/", "online": True},
    {"id": "nodejs", "name": "Node.js LTS", "addon": "base",
     "purpose": "Serve al modulo GPT (Sign in with ChatGPT).", "check": _program("node"),
     "kind": "winget", "winget": "OpenJS.NodeJS.LTS", "link": "https://nodejs.org/",
     "online": False, "restart": True},
    {"id": "gpt_sdk", "name": "Modulo GPT (SDK ufficiale OpenAI)", "addon": "base",
     "purpose": "Collegamento a ChatGPT con il tuo account (facoltativo).", "check": _gpt_sdk,
     "kind": "powershell", "script": ["installa_gpt.ps1"], "needs": ["nodejs"],
     "link": "https://github.com/openai/sign-in-with-chatgpt-devkit", "online": True},
)

# Chiavi API e dati d'accesso: dove si creano (link) e dove si inseriscono.
API_KEYS = (
    {"id": "youtube_key", "addon": "musica", "name": "Chiave API YouTube Data v3",
     "purpose": "Video YouTube nel riquadro di Lumi (gratuita, quota giornaliera).",
     "link": "https://console.cloud.google.com/apis/library/youtube.googleapis.com",
     "where": "Gestisci add-on > Musica > Configura"},
    {"id": "telegram_api", "addon": "telegram", "name": "API ID e API hash di Telegram",
     "purpose": "Accesso al tuo account Telegram (gratuiti).",
     "link": "https://my.telegram.org/apps",
     "where": "Gestisci add-on > Telegram > Configura account"},
)


def by_id(component_id: str):
    return next((c for c in COMPONENTS if c["id"] == component_id), None)


def for_addon(addon_id: str):
    return [c for c in COMPONENTS if c["addon"] == addon_id]


def keys_for_addon(addon_id: str):
    return [k for k in API_KEYS if k["addon"] == addon_id]


# --- preferenze nel profilo: link aggiornati dall'utente, finestra già vista ----
def _state_path() -> Path:
    try:
        from settings import default_path
        return default_path().parent / "componenti.json"
    except Exception:
        return Path.home() / ".lumi" / "componenti.json"


def load_state(path: Path | None = None) -> dict:
    try:
        data = json.loads(Path(path or _state_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    links = data.get("links") if isinstance(data, dict) else None
    return {"links": {str(k)[:40]: str(v)[:400] for k, v in (links or {}).items()
                      if isinstance(v, str) and v.startswith("https://")},
            "wizard_shown": bool(isinstance(data, dict) and data.get("wizard_shown"))}


def save_state(state: dict, path: Path | None = None) -> None:
    target = Path(path or _state_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, target)


def link_for(item: dict, state: dict | None = None) -> str:
    state = load_state() if state is None else state
    return state["links"].get(item["id"], item["link"])


def set_link(item_id: str, url: str, path: Path | None = None) -> str:
    url = url.strip()
    if url and not url.startswith("https://"):
        return "Il link deve iniziare con https://"
    state = load_state(path)
    if url:
        state["links"][item_id] = url[:400]
    else:
        state["links"].pop(item_id, None)        # vuoto: torna il link originale
    save_state(state, path)
    return "Link salvato." if url else "Link originale ripristinato."


def is_installed(item: dict) -> bool:
    try:
        return bool(item["check"]())
    except Exception:
        return False


def install_commands(item: dict) -> list[list[str]]:
    """Comandi da eseguire in ordine (nessuna shell, argomenti separati)."""
    commands = []
    if "pip" in item["kind"]:
        commands.append([sys.executable, "-m", "pip", "install", "--user", *item["packages"]])
    if item["kind"] == "pip+script" or item["kind"] == "script":
        commands.append([sys.executable, str(ROOT / item["script"][0])])
    if item["kind"] == "powershell":
        commands.append(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                         str(ROOT / item["script"][0])])
    if item["kind"] == "winget":
        commands.append(["winget", "install", "--id", item["winget"], "-e", "--source", "winget",
                         "--accept-package-agreements", "--accept-source-agreements"])
    return commands


def can_install_here(item: dict) -> str:
    """'' se si può installare da Lumi, altrimenti il motivo (si usa il link)."""
    if item["kind"] == "winget" and shutil.which("winget") is None:
        return "Gestione pacchetti di Windows (winget) non presente: usa il link."
    for need in item.get("needs", ()):
        other = by_id(need)
        if other and not is_installed(other):
            return "Prima installa " + other["name"] + "."
    return ""
