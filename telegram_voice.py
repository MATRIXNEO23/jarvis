"""Offline Telegram voice notes using existing Windows SAPI + optional FFmpeg.

Never send a WAV pretending it is an OGG voice message. Either generate
valid OGG/Opus voice-note media or fail and leave the Telegram reply unsent.
Incoming voice can optionally be decoded with FFmpeg and recognized by the
same local Vosk Italian model as Lumi's microphone.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import shutil
import subprocess


class TelegramVoiceError(RuntimeError):
    pass


_PS_WAV = r"""
$ErrorActionPreference='Stop'
[Console]::InputEncoding=[System.Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName System.Speech
$r=[Console]::In.ReadToEnd() | ConvertFrom-Json
$s=New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    if ($r.voice) { $s.SelectVoice([string]$r.voice) }
    $s.Rate=0
    $s.SetOutputToWaveFile([string]$r.path)
    $s.Speak([string]$r.text)
} finally { $s.Dispose() }
"""
_ENCODED=base64.b64encode(_PS_WAV.encode("utf-16-le")).decode("ascii")


def missing_voice_dependencies():
    missing=[]
    if os.name!="nt":
        missing.append("Windows SAPI")
    if not shutil.which("ffmpeg"):
        missing.append("FFmpeg (libero, per OGG/Opus)")
    return tuple(missing)


def _sapi_to_wav(text:str,wav_path:Path,voice:str=""):
    if os.name!="nt":
        raise TelegramVoiceError("SAPI richiede Windows.")
    if not text.strip() or len(text)>520:
        raise TelegramVoiceError("Testo vocale vuoto o troppo lungo.")
    data=json.dumps({"text":text,"path":str(wav_path),
                     "voice":voice[:180]},ensure_ascii=False).encode("utf-8")
    result=subprocess.run(
        ["powershell.exe","-NoLogo","-NoProfile","-NonInteractive",
         "-EncodedCommand",_ENCODED],
        input=data,capture_output=True,timeout=65,
        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),check=False)
    if result.returncode!=0 or not wav_path.is_file():
        raise TelegramVoiceError("Sintesi vocale Windows non riuscita.")


def make_telegram_voice(text:str,folder:Path,voice:str="") -> Path:
    """Return an OGG/Opus file, ready for Telethon voice_note=True."""
    missing=missing_voice_dependencies()
    if missing:
        raise TelegramVoiceError("Manca "+", ".join(missing))
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    wav=folder/"speech.wav"
    ogg=folder/"jarvis-voice.ogg"
    try:
        _sapi_to_wav(" ".join(text.split())[:500],wav,voice)
        result=subprocess.run(
            ["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
             "-y","-i",str(wav),"-ac","1","-ar","48000",
             "-c:a","libopus","-application","voip",
             "-b:a","24k","-f","ogg",str(ogg)],
            capture_output=True,timeout=45,check=False,
            creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        if result.returncode!=0 or not ogg.is_file() or ogg.stat().st_size<60:
            raise TelegramVoiceError("Conversione OGG/Opus non disponibile.")
        if ogg.stat().st_size>3_000_000:
            raise TelegramVoiceError("Nota vocale troppo grande.")
        return ogg
    finally:
        if wav.exists():
            wav.unlink()


def transcribe_incoming_voice(path:Path,max_seconds:int=90):
    """Opt-in decoding; no continuous recording of user microphone."""
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg:
        raise TelegramVoiceError("FFmpeg non installato: impossibile ascoltare vocali.")
    from voice_control import model_directory
    model_path=model_directory()
    if not model_path.is_dir():
        raise TelegramVoiceError("Modello Vosk italiano non installato.")
    try:
        import vosk
    except ImportError as exc:
        raise TelegramVoiceError("Vosk non installato.") from exc
    max_seconds=min(90,max(1,int(max_seconds)))
    cmd=[ffmpeg,"-nostdin","-hide_banner","-loglevel","error",
         "-t",str(max_seconds),"-i",str(path),
         "-f","s16le","-acodec","pcm_s16le",
         "-ar","16000","-ac","1","pipe:1"]
    job=subprocess.run(cmd,capture_output=True,timeout=max_seconds+15,
                       check=False,creationflags=getattr(
                           subprocess,"CREATE_NO_WINDOW",0))
    if job.returncode or not job.stdout:
        raise TelegramVoiceError("Impossibile decodificare il vocale ricevuto.")
    # Explicit upper cap: 90 sec * 16000 samples * 2 bytes.
    if len(job.stdout)>2_880_000:
        raise TelegramVoiceError("Vocale ricevuto oltre il limite.")
    model=vosk.Model(str(model_path))
    recognizer=vosk.KaldiRecognizer(model,16000)
    chunks=[]
    for i in range(0,len(job.stdout),16000):
        if recognizer.AcceptWaveform(job.stdout[i:i+16000]):
            chunks.append(json.loads(recognizer.Result()).get("text",""))
    chunks.append(json.loads(recognizer.FinalResult()).get("text",""))
    return " ".join(" ".join(chunks).split())[:900]
