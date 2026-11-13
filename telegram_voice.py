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
    if ($null -ne $r.rate) { $s.Rate=[Math]::Max(-10,[Math]::Min(10,[int]$r.rate)) }
    if ($null -ne $r.volume) { $s.Volume=[Math]::Max(0,[Math]::Min(100,[int]$r.volume)) }
    $s.SetOutputToWaveFile([string]$r.path)
    $done=$false
    if ($null -ne $r.pitch -and [int]$r.pitch -ne 0) {
        try {
            $t=[System.Security.SecurityElement]::Escape([string]$r.text)
            $lang=$s.Voice.Culture.Name
            $p=[int]([int]$r.pitch/2)
            $sign=if ($p -ge 0) {'+'} else {''}
            $s.SpeakSsml("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='$lang'><prosody pitch='$sign$p%'>$t</prosody></speak>")
            $done=$true
        } catch { $done=$false }
    }
    if (-not $done) { $s.Speak([string]$r.text) }
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
    request={"text":text,"path":str(wav_path),"voice":voice[:180]}
    try:
        import voice_style
        request.update(voice_style.sapi_params())
    except Exception:
        pass
    data=json.dumps(request,ensure_ascii=False).encode("utf-8")
    result=subprocess.run(
        ["powershell.exe","-NoLogo","-NoProfile","-NonInteractive",
         "-EncodedCommand",_ENCODED],
        input=data,capture_output=True,timeout=65,
        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),check=False)
    if result.returncode!=0 or not wav_path.is_file():
        raise TelegramVoiceError("Sintesi vocale Windows non riuscita.")


def _speech_source(text:str,folder:Path,voice:str) -> Path:
    """Audio della risposta con la voce scelta in Lumi.

    Piper (Paola/Serena) -> WAV; Edge (online) -> MP3; Windows -> WAV SAPI.
    Le etichette «Piper: …» / «Edge: …» non sono voci SAPI: prima venivano
    passate a SelectVoice e la nota vocale falliva («Sintesi vocale Windows
    non riuscita»). Se la voce scelta non funziona si usa la voce Windows
    predefinita invece di non rispondere.
    """
    try:
        import edge_voice
        edge_key=edge_voice.key_from_label(voice)
        if edge_key is not None:
            out=folder/"speech.mp3"
            edge_voice.synthesize(text,edge_key,out)
            return out
        import piper_voice
        piper_key=piper_voice.key_from_label(voice)
        if piper_key is not None:
            # Cartella audio di Piper: lì il motore incluso (piper.exe) lavora.
            # Stessa velocità/tonalità/volume della voce in Lumi.
            return piper_voice._render(text,piper_key,0.0,None,None)
    except Exception:
        voice=""                     # ripiego: voce Windows predefinita
    wav=folder/"speech.wav"
    try:
        _sapi_to_wav(text,wav,voice)
    except TelegramVoiceError:
        if not voice:
            raise
        _sapi_to_wav(text,wav,"")    # voce Windows non trovata: predefinita
    return wav


def make_telegram_voice(text:str,folder:Path,voice:str="") -> Path:
    """Return an OGG/Opus file, ready for Telethon voice_note=True."""
    missing=missing_voice_dependencies()
    if missing:
        raise TelegramVoiceError("Manca "+", ".join(missing))
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    ogg=folder/"jarvis-voice.ogg"
    try:
        from offline_tts import speech_text
        clean=speech_text(text)
    except Exception:
        clean=" ".join(str(text).split())
    source=None
    try:
        source=_speech_source(clean[:500],folder,voice or "")
        result=subprocess.run(
            ["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
             "-y","-i",str(source),"-ac","1","-ar","48000",
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
        for leftover in (folder/"speech.wav",folder/"speech.mp3",source):
            if leftover is not None and Path(leftover).exists():
                Path(leftover).unlink()


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
