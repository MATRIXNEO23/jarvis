"""Barra musica sotto il nucleo, elenco brani (☰) e riquadro video al posto del globo."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import library


class TrackList:
    """Brani per cartella: si naviga nelle cartelle e sottocartelle (▸ per aprire),
    doppio clic su un brano per ascoltarlo (poi seguono gli altri della stessa cartella).
    «Suona cartella» suona tutta la cartella scelta. Scrivendo in alto si cerca ovunque."""

    def __init__(self, parent, service, on_message):
        self.service = service
        self.on_message = on_message
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Brani")
        self.window.geometry("480x560")
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)
        self.query = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.query)
        entry.pack(fill="x")
        entry.focus_set()
        self.query.trace_add("write", lambda *_a: self.fill())
        holder = ttk.Frame(frame)
        holder.pack(fill="both", expand=True, pady=(8, 0))
        self.tree = ttk.Treeview(holder, show="tree", selectmode="browse")
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-Button-1>", self.play_selected)
        self.tree.bind("<Return>", self.play_selected)
        self.tree.bind("<<TreeviewOpen>>", self._open_node)
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(actions, text="▶ Suona", command=self.play_folder).pack(side="left")
        ttk.Button(actions, text="+ Coda", command=self.add_to_queue).pack(side="left", padx=4)
        ttk.Button(actions, text="+ Playlist...", command=self.add_to_playlist).pack(side="left")
        ttk.Button(actions, text="Togli", command=self.remove_selected).pack(side="right")
        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", pady=(4, 0))
        self.status = tk.StringVar()
        ttk.Label(bottom, textvariable=self.status, wraplength=440).pack(side="left", anchor="w")
        self.nodes = {}       # id albero -> ("dir", chiave cartella) | ("track", Path)
        self.dirs = {}        # chiave cartella -> {"subdirs": [...], "tracks": [...]}
        self.fill()

    # --- struttura cartelle (costruita dall'elenco già letto, senza rileggere il disco)
    def _build_dirs(self, tracks):
        roots, self.dirs = library.folder_tree(tracks, self.service.folders())
        return roots

    def _insert_dir(self, parent_id, key, label):
        node = self.tree.insert(parent_id, "end", text="📁 " + label, open=False)
        self.nodes[node] = ("dir", key)
        self.tree.insert(node, "end", text="…")      # segnaposto: si riempie all'apertura
        return node

    def _open_node(self, _event=None):
        node = self.tree.focus()
        kind, key = self.nodes.get(node, (None, None))
        if kind not in ("dir", "playlist"):
            return
        children = self.tree.get_children(node)
        if len(children) == 1 and children[0] not in self.nodes:
            self.tree.delete(children[0])
            if kind == "dir":
                self._fill_dir(node, key)
            else:
                for track in self.service.playlist_tracks(key):
                    mark = "▶ " if library.is_video(track) else "♪ "
                    item = self.tree.insert(node, "end", text=mark + track.stem)
                    self.nodes[item] = ("track", track)

    def _selected_tracks(self):
        """Brani del nodo scelto: un brano, o tutta la cartella/playlist."""
        node = self.tree.focus()
        kind, value = self.nodes.get(node, (None, None))
        if kind == "track":
            return [value]
        if kind == "dir":
            return self._tracks_under(value)
        if kind == "playlist":
            return [t for t in self.service.playlist_tracks(value) if t.exists()]
        return []

    def _say(self, message):
        if message:
            self.status.set(message)
            self.on_message(message)

    def add_to_queue(self):
        tracks = self._selected_tracks()
        if not tracks:
            self.status.set("Scegli un brano, una cartella o una playlist.")
            return
        self._say(self.service.enqueue(tracks))

    def add_to_playlist(self):
        tracks = self._selected_tracks()
        if not tracks:
            self.status.set("Scegli un brano, una cartella o una playlist.")
            return
        names = sorted(self.service.playlists(), key=str.lower)
        dialog = tk.Toplevel(self.window)
        dialog.title("Aggiungi a playlist")
        dialog.transient(self.window)
        body = ttk.Frame(dialog, padding=10)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"{len(tracks)} brani. Playlist (scegli o scrivi un nome nuovo):"
                  ).pack(anchor="w")
        name = tk.StringVar(value=names[0] if names else "")
        box = ttk.Combobox(body, textvariable=name, values=names, width=36)
        box.pack(fill="x", pady=6)
        box.focus_set()

        def confirm(_event=None):
            try:
                message = self.service.add_to_playlist(name.get(), tracks)
            except OSError as exc:
                message = "Playlist non salvata: " + str(exc)[:80]
            dialog.destroy()
            self.status.set(message)
            self.fill()
        box.bind("<Return>", confirm)
        ttk.Button(body, text="Aggiungi", command=confirm).pack(side="left")
        ttk.Button(body, text="Annulla", command=dialog.destroy).pack(side="right")

    def remove_selected(self):
        """Toglie un brano dalla playlist, o elimina la playlist (i file restano)."""
        from tkinter import messagebox
        node = self.tree.focus()
        kind, value = self.nodes.get(node, (None, None))
        parent_kind, parent_value = self.nodes.get(self.tree.parent(node), (None, None))
        if kind == "track" and parent_kind == "playlist":
            self.status.set(self.service.remove_from_playlist(parent_value, [value]))
            self.tree.delete(node)
        elif kind == "playlist":
            if messagebox.askyesno("Elimina playlist", f"Eliminare la playlist «{value}»?\n"
                                   "I file musicali restano dove sono.", parent=self.window):
                self.status.set(self.service.remove_from_playlist(value))
                self.fill()
        else:
            self.status.set("«Togli» vale per i brani di una playlist o per una playlist. "
                            "Le cartelle si tolgono in Configura.")

    def _fill_dir(self, node, key):
        import os
        entry = self.dirs.get(key, {"subdirs": [], "tracks": []})
        for sub in entry["subdirs"]:
            self._insert_dir(node, sub, os.path.basename(sub) or sub)
        for track in entry["tracks"]:
            mark = "▶ " if library.is_video(track) else "♪ "
            item = self.tree.insert(node, "end", text=mark + track.stem)
            self.nodes[item] = ("track", track)

    def _tracks_under(self, key):
        return library.tracks_under(self.dirs, key)

    def fill(self):
        tracks = self.service.tracks()
        self.tree.delete(*self.tree.get_children())
        self.nodes = {}
        words = library.normalized(self.query.get()).split()
        total = len(tracks)
        if words:          # ricerca: elenco piatto da tutte le cartelle
            found = [t for t in tracks
                     if all(w in library.normalized(" ".join(t.parts[-3:])) for w in words)][:3000]
            self._build_dirs(tracks)
            for track in found:
                mark = "▶ " if library.is_video(track) else "♪ "
                item = self.tree.insert("", "end", text=mark + track.stem)
                self.nodes[item] = ("track", track)
            self.status.set(f"{len(found)} di {total} brani. Doppio clic per ascoltare.")
            return
        roots = self._build_dirs(tracks)
        lists = self.service.playlists()
        if lists:
            top = self.tree.insert("", "end", text="★ Playlist", open=False)
            self.nodes[top] = ("lists", None)
            for name in sorted(lists, key=str.lower):
                node = self.tree.insert(top, "end", text="♫ " + name)
                self.nodes[node] = ("playlist", name)
                self.tree.insert(node, "end", text="…")
        for root in roots:
            node = self._insert_dir("", root, root)
            if len(roots) == 1:
                self.tree.item(node, open=True)
                self.tree.delete(*self.tree.get_children(node))
                self._fill_dir(node, root)
        self.status.set(f"{total} brani in {len(roots)} cartelle. Doppio clic per ascoltare."
                        if total else "Nessun brano: scegli le cartelle in Gestisci add-on > Musica.")

    def play_selected(self, _event=None):
        node = self.tree.focus()
        kind, value = self.nodes.get(node, (None, None))
        if kind != "track":
            return                       # su una cartella il doppio clic la apre/chiude
        parent = self.tree.parent(node)
        siblings = [self.nodes[i][1] for i in self.tree.get_children(parent)
                    if self.nodes.get(i, ("",))[0] == "track"]
        start = siblings.index(value) if value in siblings else 0
        message = self.service.play_tracks(siblings, start)
        if message:
            self.on_message(message)

    def play_folder(self):
        node = self.tree.focus()
        kind, _value = self.nodes.get(node, (None, None))
        if kind == "track":
            self.play_selected()
            return
        tracks = self._selected_tracks()
        if not tracks:
            self.status.set("Scegli un brano, una cartella o una playlist.")
            return
        self._say(self.service.play_tracks(tracks, 0))


class MusicBar:
    """Barra sotto il video, nell'area del globo; visibile solo con musica attiva.

    Riga 1: ⏮ ⏸ ⏹ ⏭ e volume. Riga 2: ☰ elenco brani, titolo, «riduci» video.
    Durante un video il riquadro occupa l'area sopra la barra.
    """

    def __init__(self, host, service, *, on_message=None, video_host=None):
        self.service = service
        self.on_message = on_message or (lambda text: None)
        self.video_host = video_host
        self.host = video_host if video_host is not None else host
        self.frame = tk.Frame(self.host, bg="#031522", highlightthickness=1,
                              highlightbackground="#1b6f8f")
        controls = tk.Frame(self.frame, bg="#031522")
        controls.pack(fill="x", padx=4, pady=(4, 2))
        ttk.Button(controls, text="⏮", width=3, command=lambda: self._do("prev")).pack(side="left")
        self.toggle_button = ttk.Button(controls, text="⏸", width=3, command=self._toggle)
        self.toggle_button.pack(side="left")
        ttk.Button(controls, text="⏹", width=3, command=lambda: self._do("stop")).pack(side="left")
        ttk.Button(controls, text="⏭", width=3, command=lambda: self._do("next")).pack(side="left")
        self.volume = tk.IntVar(value=service.settings.get("volume", 70))
        self.volume_scale = ttk.Scale(controls, from_=0, to=100, variable=self.volume,
                                      command=self._volume)
        self.volume_scale.pack(side="left", fill="x", expand=True, padx=(8, 2))
        info = tk.Frame(self.frame, bg="#031522")
        info.pack(fill="x", padx=4, pady=(0, 4))
        ttk.Button(info, text="☰", width=3, command=self.open_list).pack(side="left")
        self.title = tk.StringVar(value="")
        tk.Label(info, textvariable=self.title, bg="#031522", fg="#d7f6ff",
                 font=("Segoe UI", 9), anchor="w").pack(side="left", fill="x", expand=True, padx=6)
        self.video_button = ttk.Button(info, text="▁ riduci", width=9, command=self._toggle_video)
        self.video_frame = None
        if video_host is not None and getattr(service, "video", None) is not None:
            self.video_frame = tk.Frame(video_host, bg="#000000", highlightthickness=0, bd=0)
            service.video_hwnd = self.video_frame.winfo_id()
        self._shown = False
        self._video_shown = False
        self._video_button_shown = False
        self._job = None
        self._volume_job = None
        self._list = None
        self.refresh()

    def open_list(self) -> None:
        if self._list is not None:
            try:
                self._list.window.lift()
                return
            except tk.TclError:
                self._list = None
        self._list = TrackList(self.host.winfo_toplevel(), self.service, self.on_message)

    def _do(self, action: str) -> None:
        message = self.service.handle(action)
        if message:
            self.on_message(message)
        self.refresh(reschedule=False)

    def _toggle(self) -> None:
        snap = self.service.snapshot()
        self._do("pause" if snap["state"] == "playing" else "resume")

    def _toggle_video(self) -> None:
        message = self.service.toggle_video_visible()
        if message:
            self.on_message(message)
        self.refresh(reschedule=False)

    def _volume(self, value) -> None:
        if self._volume_job is not None:
            self.host.after_cancel(self._volume_job)
        self._volume_job = self.host.after(250, lambda: self.service.set_volume(int(float(value))))

    def refresh(self, reschedule: bool = True) -> None:
        try:
            enabled = self.service.is_enabled()
            snap = self.service.snapshot() if enabled else {"mode": None, "state": "stopped"}
            active = snap.get("mode") is not None and snap.get("state") != "stopped"
            if active:
                self.title.set(snap["title"][:48])
                self.toggle_button.configure(text="▶" if snap["state"] == "paused" else "⏸")
                if snap.get("mode") == "browser":
                    self.volume_scale.state(["disabled"])
                else:
                    self.volume_scale.state(["!disabled"])
                if not self._shown:
                    self.frame.place(in_=self.host, relx=0, rely=1, relwidth=1, anchor="sw")
                    self.frame.lift()
                    self._shown = True
            elif self._shown:
                self.frame.place_forget()
                self._shown = False
            is_video = active and snap.get("mode") == "video"
            want_button = is_video
            if want_button != self._video_button_shown:
                if want_button:
                    self.video_button.pack(side="right")
                else:
                    self.video_button.pack_forget()
                self._video_button_shown = want_button
            if is_video:
                self.video_button.configure(
                    text="▁ riduci" if snap.get("video_visible", True) else "▣ video")
            mini = is_video and snap.get("video_mini", False)
            want_video = is_video and (snap.get("video_visible", True) or mini)
            if self.video_frame is not None:
                if mini:
                    # YouTube ridotto: riquadrino 200x200 sopra la barra (minimo richiesto).
                    bar_h = self.frame.winfo_reqheight() + 4
                    self.video_frame.place(in_=self.video_host, relx=1, rely=1, x=-4,
                                           y=-bar_h - 4, width=200, height=200, anchor="se",
                                           relwidth=0, relheight=0)
                    if not self._video_shown:
                        self.video_frame.lift()
                        self.frame.lift()
                elif want_video:
                    # Video sopra la barra: il riquadro si accorcia dell'altezza della barra.
                    bar_h = self.frame.winfo_reqheight() + 4
                    self.video_frame.place(in_=self.video_host, relx=0, rely=0, x=0, y=0,
                                           relwidth=1, relheight=1, width=0, height=-bar_h,
                                           anchor="nw")
                    if not self._video_shown:
                        self.video_frame.lift()
                        self.frame.lift()
                elif self._video_shown:
                    self.video_frame.place_forget()
                self._video_shown = want_video
        except tk.TclError:
            return
        if reschedule:
            self._job = self.host.after(400, self.refresh)
