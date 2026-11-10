"""Logica dell'add-on Musica: cartella prima, YouTube nel browser dopo."""
from __future__ import annotations

import threading
import webbrowser

from . import config, library, youtube
from .player import MusicPlayer


class MusicService:
    def __init__(self, is_enabled, *, notify=None, open_url=webbrowser.open,
                 player=None, data_folder=None, url_for=youtube.url_for,
                 media_key=youtube.send_media_key):
        self.is_enabled = is_enabled
        self.notify = notify or (lambda text: None)
        self.open_url = open_url
        self.data_folder = data_folder
        self.url_for = url_for
        self.media_key = media_key
        self.settings = config.load(data_folder)
        self.player = player or MusicPlayer()
        self.player.volume = self.settings["volume"]
        self._tracks = None
        self._tracks_folder = None
        self.mode = None            # None | "local" | "browser"
        self.browser_title = ""

    # --- impostazioni -----------------------------------------------------
    def configure(self, folder: str, api_key: str | None = None) -> int:
        self.settings["folder"] = str(folder or "").strip()
        config.save(self.settings, self.data_folder)
        if api_key is not None:
            config.save_api_key(api_key, self.data_folder)
        self._tracks = None
        return len(self.tracks())

    def api_key(self) -> str:
        return config.load_api_key(self.data_folder)

    def tracks(self, refresh: bool = False):
        folder = self.settings.get("folder", "")
        if refresh or self._tracks is None or self._tracks_folder != folder:
            self._tracks = library.scan(folder)
            self._tracks_folder = folder
        return self._tracks

    def set_volume(self, value: int) -> None:
        self.settings["volume"] = max(0, min(100, int(value)))
        self.player.set_volume(self.settings["volume"])
        try:
            config.save(self.settings, self.data_folder)
        except OSError:
            pass

    # --- comandi ----------------------------------------------------------
    def handle(self, action: str, query: str = "") -> str:
        if not self.is_enabled():
            return "L'add-on Musica è spento: attivalo in Impostazioni > Gestisci add-on."
        if action == "play":
            return self.play(query)
        if self.mode == "browser":
            if action in ("pause", "resume", "next", "stop", "volume_up", "volume_down"):
                self.media_key("toggle" if action in ("pause", "resume") else action)
                if action == "stop":
                    self.mode = None
                return {"pause": "Pausa.", "resume": "Riprendo.", "next": "Avanti.",
                        "stop": "Musica fermata.", "volume_up": "Volume su.",
                        "volume_down": "Volume giù."}[action]
            return ""
        if self.mode != "local" or self.player.state == "stopped" and action != "stop":
            return "Non c'è musica in riproduzione."
        if action == "pause":
            self.player.pause()
            return "Pausa."
        if action == "resume":
            self.player.resume()
            return "Riprendo."
        if action == "next":
            self.player.next()
            return "Brano successivo."
        if action == "stop":
            self.player.stop()
            self.mode = None
            return "Musica fermata."
        if action in ("volume_up", "volume_down"):
            self.set_volume(self.settings["volume"] + (10 if action == "volume_up" else -10))
            return f"Volume musica {self.settings['volume']}."
        return ""

    def play(self, query: str) -> str:
        matches = library.best_matches(self.tracks(), query)
        if not matches and self.settings.get("folder"):
            matches = library.best_matches(self.tracks(refresh=True), query)
        if matches:
            if self.mode == "browser":
                self.media_key("stop")
            self.mode = "local"
            self.player.play(matches)
            return "Metto " + matches[0].stem + "."
        if self.mode == "local":
            self.player.stop()
        self.mode = "browser"
        self.browser_title = query
        key = self.api_key()

        def open_in_browser():
            url, how = self.url_for(query, key)
            self.open_url(url)
            if how != "video" and key:
                self.notify("Ricerca diretta YouTube non riuscita: apro i risultati.")
        threading.Thread(target=open_in_browser, daemon=True, name="lumi-youtube").start()
        return "Cerco «" + query + "» su YouTube nel browser."

    def snapshot(self) -> dict:
        if self.mode == "local":
            return {"mode": "local", "state": self.player.state, "title": self.player.title,
                    "volume": self.settings["volume"]}
        if self.mode == "browser":
            return {"mode": "browser", "state": "playing", "title": "YouTube: " + self.browser_title,
                    "volume": self.settings["volume"]}
        return {"mode": None, "state": "stopped", "title": "", "volume": self.settings["volume"]}

    def close(self) -> None:
        try:
            self.player.close()
        except OSError:
            pass
