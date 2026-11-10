"""Logica dell'add-on Musica.

Ordine: cartella (audio nel lettore MCI, video nel riquadro al posto del
globo) → YouTube nel riquadro (con chiave API: lettore ufficiale incorporato)
→ YouTube nel browser (senza chiave o se il riquadro non è disponibile).
"""
from __future__ import annotations

import os
from pathlib import Path
import threading
import webbrowser

from . import config, library, youtube
from .player import MusicPlayer


class MusicService:
    def __init__(self, is_enabled, *, notify=None, open_url=webbrowser.open,
                 player=None, data_folder=None, url_for=youtube.url_for,
                 media_key=youtube.send_media_key, video_id_for=youtube.video_list,
                 video_panel=None, open_file=None):
        self.is_enabled = is_enabled
        self.notify = notify or (lambda text: None)
        self.open_url = open_url
        self.data_folder = data_folder
        self.url_for = url_for
        self.media_key = media_key
        self.video_id_for = video_id_for
        self.settings = config.load(data_folder)
        self.player = player or MusicPlayer()
        self.player.volume = self.settings["volume"]
        self.video = video_panel          # VideoPanel o None (riquadro non disponibile)
        self.video_hwnd = None            # impostato dalla UI (riquadro al posto del globo)
        self._tracks = None
        self._tracks_folder = None
        self.mode = None                  # None | "local" | "video" | "browser"
        self.browser_title = ""
        self.video_items: list[tuple[str, object, str]] = []   # (tipo, valore, titolo)
        self.video_index = -1
        self._queued_until = 0            # coda YouTube: posizione dopo l'ultimo accodato
        self.video_hidden = False         # video nascosto, audio che continua (solo file)
        self.open_file = open_file or (lambda path: os.startfile(str(path)))
        if self.video is not None:
            self.video.on_event = self._video_event

    # --- impostazioni -----------------------------------------------------
    def configure(self, folders, api_key: str | None = None) -> int:
        """folders: una cartella (testo) o un elenco di cartelle."""
        if isinstance(folders, (str, Path)) or folders is None:
            folders = [str(folders or "")]
        clean = config.clean_folders([str(f) for f in folders])
        self.settings["folders"] = clean
        self.settings["folder"] = clean[0] if clean else ""
        config.save(self.settings, self.data_folder)
        if api_key is not None:
            config.save_api_key(api_key, self.data_folder)
        self._tracks = None
        return len(self.tracks())

    def api_key(self) -> str:
        return config.load_api_key(self.data_folder)

    def folders(self) -> list[str]:
        return list(self.settings.get("folders") or
                    ([self.settings["folder"]] if self.settings.get("folder") else []))

    def tracks(self, refresh: bool = False):
        folders = tuple(self.folders())
        if refresh or self._tracks is None or self._tracks_folder != folders:
            self._tracks = library.scan_all(folders)
            self._tracks_folder = folders
        return self._tracks

    def set_volume(self, value: int) -> None:
        """Un solo volume per brani, video della cartella e YouTube nel riquadro."""
        self.settings["volume"] = max(0, min(100, int(value)))
        self.player.set_volume(self.settings["volume"])
        if self.video is not None:
            self.video.send(cmd="volume", value=self.settings["volume"])
        try:
            config.save(self.settings, self.data_folder)
        except OSError:
            pass

    def video_ready(self) -> bool:
        return self.video is not None and self.video_hwnd is not None

    # --- comandi ----------------------------------------------------------
    def handle(self, action: str, query: str = "") -> str:
        if not self.is_enabled():
            return "L'add-on Musica è spento: attivalo in Impostazioni > Gestisci add-on."
        if action == "play":
            return self.play(query)
        if action == "queue":
            return self.queue_query(query)
        if action == "playlist":
            return self.play_playlist(query)
        if self.mode == "browser":
            if action in ("pause", "resume", "next", "prev", "stop", "volume_up", "volume_down"):
                self.media_key("toggle" if action in ("pause", "resume") else action)
                if action == "stop":
                    self.mode = None
                return {"pause": "Pausa.", "resume": "Riprendo.", "next": "Avanti.",
                        "prev": "Indietro.", "stop": "Musica fermata.", "volume_up": "Volume su.",
                        "volume_down": "Volume giù."}[action]
            return ""
        if action in ("volume_up", "volume_down"):
            self.set_volume(self.settings["volume"] + (10 if action == "volume_up" else -10))
            return f"Volume musica {self.settings['volume']}."
        if self.mode == "video":
            return self._video_action(action)
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
        if action == "prev":
            self.player.prev()
            return "Indietro."
        if action == "stop":
            self.player.stop()
            self.mode = None
            return "Musica fermata."
        return ""

    def _video_action(self, action: str) -> str:
        if action == "pause":
            self.video.send(cmd="pause")
            return "Pausa."
        if action == "resume":
            self.video.send(cmd="resume")
            return "Riprendo."
        if action == "stop":
            self.stop_video()
            return "Musica fermata."
        if action == "next":
            return self._video_step(+1) or "Fine dell'elenco."
        if action == "prev":
            # Oltre 3 s torna all'inizio, altrimenti il precedente.
            if self.video.position > 3 or self.video_index <= 0:
                self.video.send(cmd="restart")
                return "Dall'inizio."
            return self._video_step(-1) or "Dall'inizio."
        return ""

    def current_video_kind(self) -> str | None:
        if self.mode == "video" and 0 <= self.video_index < len(self.video_items):
            return self.video_items[self.video_index][0]
        return None

    def toggle_video_visible(self) -> str:
        """Riduce/ripristina il video lasciando la musica con la sola barra.
        File locali: il video sparisce. YouTube: resta un riquadrino 200x200,
        la misura minima che le regole del lettore incorporato richiedono."""
        kind = self.current_video_kind()
        if kind is None:
            return ""
        self.video_hidden = not self.video_hidden
        if not self.video_hidden:
            return "Video ripristinato."
        if kind == "youtube":
            return "Video ridotto: YouTube richiede un riquadrino visibile, la musica continua."
        return "Video ridotto: continua solo la musica."

    def stop_video(self) -> None:
        # Chiude il riquadro: WebView2 libera la sua RAM (importante sul Pavilion).
        if self.video is not None:
            self.video.close()
        self.mode = None
        self.video_hidden = False
        self.video_items, self.video_index = [], -1

    def _video_step(self, delta: int) -> str:
        index = self.video_index + delta
        if not 0 <= index < len(self.video_items):
            return ""
        self.video_index = index
        kind, value, title = self.video_items[index]
        self.video.send(cmd="volume", value=self.settings["volume"])
        if kind == "file":
            self.video.file(value)
        else:
            self.video.youtube(value)
        return "Metto " + title + "."

    def _video_event(self, event: dict) -> None:
        """Dal thread del riquadro: fine video → il successivo; errore → browser."""
        if self.mode != "video":
            return
        kind = event.get("ev")
        if kind == "state" and event.get("state") == "ended":
            if not self._video_step(+1):
                self.stop_video()
        elif kind == "error":
            current = (self.video_items[self.video_index]
                       if 0 <= self.video_index < len(self.video_items) else None)
            if current and current[0] == "youtube":
                # Video non incorporabile o riquadro non disponibile: browser.
                self.open_url("https://www.youtube.com/watch?v=" + str(current[1]))
                self.notify("Questo video non si può mostrare in Lumi: lo apro nel browser.")
                self.stop_video()
            elif event.get("code") == "webview2":
                self.notify("Riquadro video non disponibile (WebView2): installa o aggiorna "
                            "Microsoft Edge WebView2 Runtime.")
                self.stop_video()
            else:
                # Formato/codec non supportato dal riquadro: lettore di Windows.
                if current and current[0] == "file":
                    try:
                        self.open_file(current[1])
                        self.notify("Il riquadro non riproduce questo video: lo apro con "
                                    "il lettore di Windows.")
                    except OSError:
                        self.notify("Questo video non si può riprodurre.")
                if not self._video_step(+1):
                    self.stop_video()
        elif kind == "closed":
            self.mode = None

    def _start_video(self, items) -> str:
        if self.mode == "local":
            self.player.stop()
        self.video.start(self.video_hwnd)
        self.mode = "video"
        self.video_items, self.video_index = list(items), -1
        self._queued_until = 0
        return self._video_step(+1)

    def play_tracks(self, tracks, start: int = 0) -> str:
        """Dall'elenco brani (doppio clic): parte quello, poi i successivi."""
        if not self.is_enabled():
            return "L'add-on Musica è spento."
        tracks = list(tracks)[start:]
        if not tracks:
            return ""
        if library.is_video(tracks[0]):
            if not library.is_panel_video(tracks[0]) or not self.video_ready():
                try:
                    self.open_file(tracks[0])
                except OSError as exc:
                    return "Non riesco ad aprire il video: " + str(exc)[:80]
                return "Apro " + tracks[0].stem + " con il lettore di Windows."
            return self._start_video([("file", t, t.stem) for t in tracks
                                      if library.is_panel_video(t)])
        if self.mode == "video":
            self.stop_video()
        if self.mode == "browser":
            self.media_key("stop")
        self.mode = "local"
        self.player.play([t for t in tracks if not library.is_video(t)])
        return "Metto " + tracks[0].stem + "."

    # --- coda e playlist (solo brani della cartella) -------------------------
    def enqueue(self, tracks) -> str:
        """Aggiunge in coda senza fermare quello che suona; se non suona nulla parte."""
        if not self.is_enabled():
            return "L'add-on Musica è spento."
        tracks = [Path(t) for t in tracks]
        if not tracks:
            return ""
        if self.mode == "video" and self.current_video_kind() == "youtube":
            # Non interrompe YouTube con un brano della cartella.
            return ("Mentre va YouTube la coda accetta solo video YouTube: "
                    "di' «aggiungi in coda …».")
        if self.mode == "video" and self.current_video_kind() == "file":
            videos = [t for t in tracks if library.is_panel_video(t)]
            self.video_items.extend(("file", t, t.stem) for t in videos)
            skipped = len(tracks) - len(videos)
            return (f"Aggiunti {len(videos)} video in coda." if videos else
                    "In coda al video vanno solo video.") + (
                    f" ({skipped} brani audio esclusi.)" if videos and skipped else "")
        if self.mode == "local" and self.player.state != "stopped":
            audio = [t for t in tracks if not library.is_video(t)]
            if not audio:
                return "In coda alla musica vanno solo brani audio."
            self.player.add(audio)
            return ("Aggiunto in coda: " + audio[0].stem + "." if len(audio) == 1
                    else f"Aggiunti {len(audio)} brani in coda.")
        return self.play_tracks(tracks)

    def queue_query(self, query: str) -> str:
        if self.mode == "video" and self.current_video_kind() == "youtube":
            return self._queue_youtube(query)
        matches = library.best_matches(self.tracks(), query) or \
            library.best_matches(self.tracks(refresh=True), query)
        if not matches:
            return "Non trovo «" + query + "» nelle cartelle musica."
        return self.enqueue(matches[:1])

    def _queue_youtube(self, query: str) -> str:
        """Durante YouTube: cerca (una ricerca della chiave) e mette il primo video
        dopo quelli già in coda, senza interrompere quello in corso."""
        key = self.api_key()
        if not key:
            return "Per la coda YouTube serve la chiave API in Configura."

        def find_and_add():
            try:
                found = self.video_id_for(query, key)
            except Exception:
                self.notify("Ricerca YouTube non riuscita: niente aggiunto in coda.")
                return
            if isinstance(found, str):
                found = [(found, query)]
            if self.mode != "video" or not found:
                return
            video_id, title = found[0]
            # Dopo il video in corso e gli altri già accodati da te.
            position = max(self.video_index + 1, self._queued_until)
            self.video_items.insert(position, ("youtube", video_id, title or query))
            self._queued_until = position + 1
            self.notify("Aggiunto in coda: " + (title or query) + ".")
        threading.Thread(target=find_and_add, daemon=True, name="lumi-youtube-coda").start()
        return "Cerco «" + query + "» su YouTube per la coda."

    def playlists(self) -> dict:
        return config.load_playlists(self.data_folder)

    @staticmethod
    def _entry(item) -> str:
        """Voce di playlist: percorso del file, o «yt:<id>|<titolo>» per YouTube."""
        if isinstance(item, tuple) and item and item[0] == "youtube":
            return "yt:" + str(item[1]) + "|" + str(item[2] if len(item) > 2 else "")[:120]
        if isinstance(item, tuple) and item and item[0] == "file":
            return str(item[1])
        return str(item)

    @staticmethod
    def _item(entry: str):
        if entry.startswith("yt:"):
            vid, _sep, title = entry[3:].partition("|")
            return ("youtube", vid, title or "YouTube")
        return ("file", Path(entry), Path(entry).stem)

    def add_to_playlist(self, name: str, tracks) -> str:
        name = " ".join(str(name or "").split())[:60]
        if not name:
            return "Nome playlist vuoto."
        data = self.playlists()
        if name not in data and len(data) >= config.MAX_PLAYLISTS:
            return "Troppe playlist: eliminane qualcuna."
        current = data.setdefault(name, [])
        ids = {e.partition("|")[0] for e in current}
        added = []
        for item in tracks:
            entry = self._entry(item)
            if entry.partition("|")[0] not in ids:
                ids.add(entry.partition("|")[0])
                added.append(entry)
        current.extend(added)
        config.save_playlists(data, self.data_folder)
        return f"Playlist «{name}»: {len(added)} aggiunti, {len(current)} in totale."

    def remove_from_playlist(self, name: str, tracks=None) -> str:
        """tracks None: elimina la playlist (i file restano dove sono)."""
        data = self.playlists()
        if name not in data:
            return ""
        if tracks is None:
            del data[name]
            message = f"Playlist «{name}» eliminata (i file restano)."
        else:
            drop = {self._entry(t).partition("|")[0] for t in tracks}
            data[name] = [t for t in data[name] if t.partition("|")[0] not in drop]
            message = f"Tolti dalla playlist «{name}»."
        config.save_playlists(data, self.data_folder)
        return message

    def rename_playlist(self, old: str, new: str) -> str:
        new = " ".join(str(new or "").split())[:60]
        data = self.playlists()
        if old not in data or not new:
            return ""
        if new in data and new != old:
            return f"Esiste già una playlist «{new}»."
        data = {(new if k == old else k): v for k, v in data.items()}
        config.save_playlists(data, self.data_folder)
        return f"Playlist rinominata in «{new}»."

    def playlist_items(self, name: str) -> list:
        return [self._item(e) for e in self.playlists().get(name, [])]

    def playlist_tracks(self, name: str) -> list[Path]:
        return [i[1] for i in self.playlist_items(name) if i[0] == "file"]

    def find_playlist(self, query: str):
        data = self.playlists()
        wanted = library.normalized(query)
        return next((n for n in data if library.normalized(n) == wanted), None) or \
            next((n for n in data if wanted and wanted in library.normalized(n)), None)

    def play_playlist(self, query: str, start: int = 0) -> str:
        name = query if query in self.playlists() else self.find_playlist(query)
        if name is None:
            return "Non trovo la playlist «" + query + "»."
        items = self.playlist_items(name)[start:]
        if any(i[0] == "youtube" for i in items):
            if not self.video_ready():
                return "Per i video YouTube della playlist serve il riquadro video (WebView2)."
            playable = [i for i in items if i[0] == "youtube" or
                        (i[1].exists() and library.is_panel_video(i[1]))]
            skipped = len(items) - len(playable)
            message = self._start_video(playable)
            return message + (f" ({skipped} brani audio saltati: con YouTube la playlist "
                              "suona solo video.)" if skipped else "")
        tracks = [i[1] for i in items if i[1].exists()]
        if not tracks:
            return f"La playlist «{name}» è vuota o i file non ci sono più."
        return self.play_tracks(tracks)

    # --- coda visibile e modificabile ---------------------------------------
    def queue_view(self) -> tuple[list[str], int]:
        """(titoli in coda, indice di quello in corso)."""
        if self.mode == "video":
            return [i[2] for i in self.video_items], self.video_index
        if self.mode == "local":
            return [Path(t).stem for t in self.player.playlist], self.player.index
        return [], -1

    def queue_items(self) -> list:
        if self.mode == "video":
            return list(self.video_items)
        if self.mode == "local":
            return [("file", Path(t), Path(t).stem) for t in self.player.playlist]
        return []

    def queue_remove(self, index: int) -> bool:
        if self.mode == "video":
            if 0 <= index < len(self.video_items) and index != self.video_index:
                del self.video_items[index]
                if index < self.video_index:
                    self.video_index -= 1
                self._queued_until = max(0, min(self._queued_until, len(self.video_items)))
                return True
            return False
        if self.mode == "local" and index != self.player.index:
            self.player.remove_at(index)
            return True
        return False

    def queue_move(self, index: int, delta: int) -> bool:
        if self.mode == "video":
            j = index + delta
            if 0 <= index < len(self.video_items) and 0 <= j < len(self.video_items):
                items = self.video_items
                items[index], items[j] = items[j], items[index]
                if self.video_index in (index, j):
                    self.video_index = j if self.video_index == index else index
                return True
            return False
        if self.mode == "local":
            self.player.move(index, delta)
            return True
        return False

    def save_queue_as_playlist(self, name: str) -> str:
        items = self.queue_items()
        if not items:
            return "La coda è vuota."
        return self.add_to_playlist(name, items)

    def play(self, query: str) -> str:
        matches = library.best_matches(self.tracks(), query)
        if not matches and self.folders():
            matches = library.best_matches(self.tracks(refresh=True), query)
        if matches:
            return self.play_tracks(matches)
        key = self.api_key()
        if key and self.video_ready():
            return self._youtube_in_panel(query, key)
        return self._youtube_in_browser(query, key)

    def _youtube_in_panel(self, query: str, key: str) -> str:
        if self.mode == "local":
            self.player.stop()
        self.mode = "video"
        self.video_items, self.video_index = [], -1

        def find_and_play():
            try:
                found = self.video_id_for(query, key)
            except Exception:
                self.mode = None
                self._youtube_in_browser(query, "")
                self.notify("Ricerca YouTube non riuscita: apro i risultati nel browser.")
                return
            if isinstance(found, str):
                found = [(found, query)]
            self.video.start(self.video_hwnd)
            # Più risultati in coda: finito un video parte il successivo.
            self.video_items = [("youtube", vid, title or query) for vid, title in found]
            self._queued_until = 0
            self.video_index = -1
            self._video_step(+1)
        threading.Thread(target=find_and_play, daemon=True, name="lumi-youtube").start()
        return "Cerco «" + query + "» su YouTube."

    def _youtube_in_browser(self, query: str, key: str) -> str:
        if self.mode == "local":
            self.player.stop()
        if self.mode == "video":
            self.stop_video()
        self.mode = "browser"
        self.browser_title = query

        def open_in_browser():
            url, how = self.url_for(query, key)
            self.open_url(url)
            if how != "video" and key:
                self.notify("Ricerca diretta YouTube non riuscita: apro i risultati.")
        threading.Thread(target=open_in_browser, daemon=True, name="lumi-youtube").start()
        return "Cerco «" + query + "» su YouTube nel browser."

    def snapshot(self) -> dict:
        volume = self.settings["volume"]
        if self.mode == "local":
            return {"mode": "local", "state": self.player.state, "title": self.player.title,
                    "volume": volume}
        if self.mode == "video":
            title = (self.video_items[self.video_index][2]
                     if 0 <= self.video_index < len(self.video_items) else "Video")
            state = self.video.state if self.video is not None else "stopped"
            return {"mode": "video", "state": "paused" if state == "paused" else "playing",
                    "title": title, "volume": volume, "video_visible": not self.video_hidden,
                    "video_mini": self.video_hidden and self.current_video_kind() == "youtube",
                    "kind": self.current_video_kind()}
        if self.mode == "browser":
            return {"mode": "browser", "state": "playing", "title": "YouTube: " + self.browser_title,
                    "volume": volume}
        return {"mode": None, "state": "stopped", "title": "", "volume": volume}

    def close(self) -> None:
        try:
            self.player.close()
        except OSError:
            pass
        if self.video is not None:
            self.video.close()
