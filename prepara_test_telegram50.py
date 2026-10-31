"""Prepare a separate local test profile for the Telegram-50 Jarvis trial.

Only READ the owner's original Jarvis profile. Copy the SQLite workspace via
the online backup API, never with a raw file copy while connections may be open.
All writes stay inside the dedicated test directory.
"""
from __future__ import annotations

from contextlib import closing
import os
from pathlib import Path
import shutil
import sqlite3

from settings import load_settings, save_settings


def prepare_trial(original_home: Path, trial_home: Path) -> list[str]:
    source = Path(original_home).resolve()
    target = Path(trial_home).resolve()
    if source == target or source in target.parents or target in source.parents:
        raise RuntimeError("Percorso di test non isolato: operazione annullata.")
    target.mkdir(parents=True, exist_ok=True)
    notes = []
    trial_settings = target / "settings.json"
    microphone_migration = target / ".microphone-on-startup-v1"
    if not trial_settings.exists():
        current = load_settings(source / "settings.json")
        current["telegram_enabled"] = False
        current["auto_listen"] = True
        save_settings(current, trial_settings)
        notes.append("Profilo nuovo: Telegram automatico OFF, microfono ON all'avvio.")
    elif not microphone_migration.exists():
        # Apply the owner's newly approved startup preference once, including
        # an existing trial profile. Future explicit OFF choices remain valid.
        current = load_settings(trial_settings)
        current["auto_listen"] = True
        save_settings(current, trial_settings)
        notes.append("Preferenza aggiornata: microfono ON all'avvio (modificabile).")
    else:
        notes.append("Impostazioni del test gia presenti: non sovrascritte.")
    if not microphone_migration.exists():
        microphone_migration.write_text("microphone-on-startup-v1\n",
                                        encoding="utf-8")

    source_auth = source / "telegram-auth.dpapi"
    trial_auth = target / "telegram-auth.dpapi"
    if source_auth.is_file() and not trial_auth.exists():
        # The file stays DPAPI encrypted, under the same Windows user account.
        shutil.copyfile(source_auth, trial_auth)
        notes.append("Credenziali Telegram cifrate copiate nel solo profilo di test.")

    source_db = source / "jarvis_workspaces.sqlite3"
    trial_db = target / "jarvis_workspaces.sqlite3"
    if source_db.is_file() and not trial_db.exists():
        tmp_db = target / "jarvis_workspaces.initializing.sqlite3"
        if tmp_db.exists():
            raise RuntimeError("Copia temporanea gia presente. Verifica il profilo di test.")
        try:
            with closing(sqlite3.connect(source_db.as_uri() + "?mode=ro",
                                         uri=True, timeout=10)) as src:
                with closing(sqlite3.connect(str(tmp_db), timeout=10)) as dst:
                    src.backup(dst)
            os.replace(tmp_db, trial_db)
        finally:
            if tmp_db.exists():
                tmp_db.unlink()
        notes.append("Database copiato con backup SQLite consistente.")
    elif trial_db.exists():
        notes.append("Database di test gia presente: conservato con i suoi messaggi.")
    else:
        notes.append("Nessun database originale: Jarvis creera un archivio di test vuoto.")
    return notes


def main():
    appdata = os.environ.get("LOCALAPPDATA")
    test_dir = os.environ.get("JARVIS_TRIAL_HOME")
    if not appdata or not test_dir:
        raise RuntimeError("Avvia tramite AVVIA_TEST_TELEGRAM50.bat su Windows.")
    original = Path(appdata) / "Jarvis"
    trial = Path(test_dir)
    print("JARVIS // PROVA TELEGRAM 50")
    print("Profilo originale (sola lettura):", original)
    print("Profilo di prova:", trial)
    for line in prepare_trial(original, trial):
        print("-", line)
    print("La vecchia cartella di Jarvis non viene modificata dallo script.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
        print("Prova non avviata:", str(exc))
        raise SystemExit(1)
