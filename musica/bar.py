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
        ttk.Button(actions, text="Rinomina", command=self.rename_selected).pack(side="right", padx=4)
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
                for index, entry in enumerate(self.service.playlist_items(key)):
                    if entry[0] == "youtube":
                        mark = "▷ YouTube: "
                    else:
                        mark = "▶ " if library.is_video(entry[1]) else "♪ "
                    item = self.tree.insert(node, "end", text=mark + entry[2])
                    self.nodes[item] = ("pitem", (key, index, entry))

    def _selected_tracks(self):
        """Brani del nodo scelto: un brano, o tutta la cartella/playlist."""
        node = self.tree.focus()
        kind, value = self.nodes.get(node, (None, None))
        if kind == "track":
            return [value]
        if kind == "pitem":
            return [value[2][1]] if value[2][0] == "file" else []
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
        tracks = self._selected_tracks()   # vuoto: crea solo la playlist col nome scelto
        names = sorted(self.service.playlists(), key=str.lower)
        dialog = tk.Toplevel(self.window)
        dialog.title("Aggiungi a playlist")
        dialog.transient(self.window)
        body = ttk.Frame(dialog, padding=10)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=(f"{len(tracks)} brani. " if tracks else "Nuova playlist vuota. ") +
                  "Playlist (scegli o scrivi un nome nuovo):").pack(anchor="w")
        name = tk.StringVar(value=(names[0] if names and tracks else ""))
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

    def rename_selected(self):
        from tkinter import simpledialog
        kind, value = self.nodes.get(self.tree.focus(), (None, None))
        if kind != "playlist":
            self.status.set("Scegli una playlist da rinominare.")
            return
        new = simpledialog.askstring("Rinomina playlist", "Nuovo nome:", initialvalue=value,
                                     parent=self.window)
        if new:
            self.status.set(self.service.rename_playlist(value, new) or "Nome non valido.")
            self.fill()

    def remove_selected(self):
        """Toglie un brano dalla playlist, o elimina la playlist (i file restano)."""
        from tkinter import messagebox
        node = self.tree.focus()
        kind, value = self.nodes.get(node, (None, None))
        parent_kind, parent_value = self.nodes.get(self.tree.parent(node), (None, None))
        if kind == "pitem":
            self.status.set(self.service.remove_from_playlist(value[0], [value[2]]))
            self.fill()
        elif kind == "playlist":
            if messagebox.askyesno("Elimina playlist", f"Eliminare la playlist «{value}»?\n"
                                   "I file musicali restano dove sono.", parent=self.window):
                self.status.set(self.service.remove_from_playlist(value))
                self.fill()
        else:
            self.status.set("«Togli» vale per le voci di una playlist o per una playlist. "
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
        if kind == "pitem":
            self._say(self.service.play_playlist(value[0], value[1]))
            return
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
        kind, value = self.nodes.get(node, (None, None))
        if kind in ("track", "pitem"):
            self.play_selected()
            return
        if kind == "playlist":
            self._say(self.service.play_playlist(value))
            return
        tracks = self._selected_tracks()
        if not tracks:
            self.status.set("Scegli un brano, una cartella o una playlist.")
            return
        self._say(self.service.play_tracks(tracks, 0))


class QueueWindow:
    """Coda attuale (cartelle o YouTube): togli, sposta, cerca e aggiungi, salva come playlist."""

    def __init__(self, parent, service, on_message):
        self.service = service
        self.on_message = on_message
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Coda")
        self.window.geometry("440x500")
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)
        add = ttk.Frame(frame)
        add.pack(fill="x")
        self.query = tk.StringVar()
        entry = ttk.Entry(add, textvariable=self.query)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda _e: self.add())
        ttk.Button(add, text="+ Aggiungi", command=self.add).pack(side="left", padx=(4, 0))
        ttk.Label(frame, text="Cerca nelle cartelle; mentre va YouTube cerca su YouTube.",
                  wraplength=410).pack(anchor="w", pady=(2, 6))
        holder = ttk.Frame(frame)
        holder.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(holder, activestyle="none", bg="#031522", fg="#d7f6ff",
                                  selectbackground="#1b6f8f", highlightthickness=0)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(6, 0))
        ttk.Button(row, text="▲", width=3, command=lambda: self.move(-1)).pack(side="left")
        ttk.Button(row, text="▼", width=3, command=lambda: self.move(+1)).pack(side="left", padx=4)
        ttk.Button(row, text="Togli", command=self.remove).pack(side="left")
        ttk.Button(row, text="Salva come playlist...", command=self.save).pack(side="right")
        self.status = tk.StringVar()
        ttk.Label(frame, textvariable=self.status, wraplength=410).pack(anchor="w", pady=(4, 0))
        self._last = None
        self.refresh()

    def refresh(self):
        try:
            view = self.service.queue_view()
            if view != self._last:
                keep = self.listbox.curselection()
                self._last = (list(view[0]), view[1])
                titles, current = view
                self.listbox.delete(0, "end")
                for i, title in enumerate(titles):
                    self.listbox.insert("end", ("▶ " if i == current else "   ") + title)
                for i in keep:
                    if i < len(titles):
                        self.listbox.selection_set(i)
                if not titles:
                    self.status.set("Coda vuota: metti un brano o una playlist.")
            self.window.after(1000, self.refresh)
        except tk.TclError:
            pass

    def _selected(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def move(self, delta):
        index = self._selected()
        if index is not None and self.service.queue_move(index, delta):
            self._last = None
            self.window.after(150, lambda: self.listbox.selection_set(index + delta))

    def remove(self):
        index = self._selected()
        if index is None:
            return
        if not self.service.queue_remove(index):
            self.status.set("Quello in corso non si toglie: usa ⏭ o ⏹.")
        self._last = None

    def add(self):
        text = self.query.get().strip()
        if text:
            message = self.service.queue_query(text)
            self.status.set(message)
            self.on_message(message)
            self.query.set("")

    def save(self):
        names = sorted(self.service.playlists(), key=str.lower)
        dialog = tk.Toplevel(self.window)
        dialog.title("Salva coda come playlist")
        dialog.transient(self.window)
        body = ttk.Frame(dialog, padding=10)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Nome playlist (nuovo, o esistente per aggiungere):").pack(anchor="w")
        name = tk.StringVar()
        box = ttk.Combobox(body, textvariable=name, values=names, width=36)
        box.pack(fill="x", pady=6)
        box.focus_set()

        def confirm(_event=None):
            try:
                message = self.service.save_queue_as_playlist(name.get())
            except OSError as exc:
                message = "Playlist non salvata: " + str(exc)[:80]
            dialog.destroy()
            self.status.set(message)
        box.bind("<Return>", confirm)
        ttk.Button(body, text="Salva", command=confirm).pack(side="left")
        ttk.Button(body, text="Annulla", command=dialog.destroy).pack(side="right")


class MusicBar:
    """Barra sotto il video, nell'area del globo; visibile solo con musica attiva.

    Riga 1: ⏮ ⏸ ⏹ ⏭ e volume. Riga 2: ☰ elenco brani, Coda, titolo, «⛶ intero» e «riduci» video.
    Durante un video il riquadro occupa l'area sopra la barra.
    """

    def __init__(self, host, service, *, on_message=None, video_host=None):
        self.service = service
        self.on_message = on_message or (lambda text: None)
        self.video_host = video_host
        self.host = video_host if video_host is not None else host
        # Figli della finestra principale: così barra e video possono stare nell'area
        # del globo (place in_=…) oppure coprire tutta la finestra a schermo intero.
        self.top = self.host.winfo_toplevel()
        self.frame = tk.Frame(self.top, bg="#031522", highlightthickness=1,
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
        ttk.Button(info, text="Coda", width=5, command=self.open_queue).pack(side="left", padx=(3, 0))
        self.title = tk.StringVar(value="")
        # width=1: il titolo lungo non spinge fuori i tasti video (prendono spazio prima).
        self.title_label = tk.Label(info, textvariable=self.title, bg="#031522", fg="#d7f6ff",
                                    font=("Segoe UI", 9), anchor="w", width=1)
        self.title_label.pack(side="left", fill="x", expand=True, padx=6)
        self.video_button = ttk.Button(info, text="▁ riduci", width=9, command=self._toggle_video)
        self.full_button = ttk.Button(info, text="⛶ intero", width=9, command=self._toggle_full)
        self._full = False
        self._full_shown = False
        self._bar_in = None
        self.top.bind("<Escape>", lambda _e: self._full and self._toggle_full(), add="+")
        self.video_frame = None
        if video_host is not None and getattr(service, "video", None) is not None:
            self.video_frame = tk.Frame(self.top, bg="#000000", highlightthickness=0, bd=0)
            service.video_hwnd = self.video_frame.winfo_id()
        self._shown = False
        self._video_shown = False
        self._video_button_shown = False
        self._job = None
        self._volume_job = None
        self._list = None
        self._marquee_text = ""
        self._marquee_pos = 0
        self._marquee()
        self.refresh()

    def open_list(self) -> None:
        if self._list is not None:
            try:
                self._list.window.lift()
                return
            except tk.TclError:
                self._list = None
        self._list = TrackList(self.host.winfo_toplevel(), self.service, self.on_message)

    def open_queue(self) -> None:
        current = getattr(self, "_queue_window", None)
        if current is not None:
            try:
                current.window.lift()
                return
            except tk.TclError:
                pass
        self._queue_window = QueueWindow(self.host.winfo_toplevel(), self.service,
                                         self.on_message)

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

    def _marquee(self) -> None:
        """Titolo scorrevole quando non entra nella barra."""
        try:
            import tkinter.font as tkfont
            text = self._marquee_text
            width = self.title_label.winfo_width()
            font = tkfont.Font(font=self.title_label.cget("font"))
            if text and width > 20 and font.measure(text) > width:
                loop = text + "     •     "
                self._marquee_pos = (self._marquee_pos + 1) % len(loop)
                self.title.set(loop[self._marquee_pos:] + loop[:self._marquee_pos])
            elif self.title.get() != text:
                self.title.set(text)
            self.host.after(220, self._marquee)
        except tk.TclError:
            pass

    def _toggle_full(self) -> None:
        self._set_full(not self._full)
        self.refresh(reschedule=False)

    def _set_full(self, value: bool) -> None:
        """Schermo intero: finestra di Lumi a tutto schermo, video su tutta l'area,
        barra in fondo (il tasto «⛶ esci» torna come prima)."""
        if value == self._full:
            return
        try:
            self.top.attributes("-fullscreen", value)
        except tk.TclError:
            pass
        self._full = value
        self._video_shown = False          # forza il nuovo posizionamento
        self._bar_in = None
        self.on_message("Schermo intero." if value else "Schermo intero chiuso.")

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
                if snap["title"] != self._marquee_text:
                    self._marquee_text, self._marquee_pos = snap["title"], 0
                    self.title.set(snap["title"])
                self.toggle_button.configure(text="▶" if snap["state"] == "paused" else "⏸")
                if snap.get("mode") == "browser":
                    self.volume_scale.state(["disabled"])
                else:
                    self.volume_scale.state(["!disabled"])
                bar_in = self.top if self._full else self.host
                if not self._shown or self._bar_in is not bar_in:
                    self.frame.place(in_=bar_in, relx=0, rely=1, relwidth=1, anchor="sw")
                    self.frame.lift()
                    self._shown = True
                    self._bar_in = bar_in
            elif self._shown:
                self.frame.place_forget()
                self._shown = False
            is_video = active and snap.get("mode") == "video"
            full_ok = is_video and snap.get("video_visible", True)
            if self._full and not full_ok:
                self._set_full(False)              # video finito o ridotto: si esce
                self.frame.place(in_=self.host, relx=0, rely=1, relwidth=1, anchor="sw")
                self._bar_in = self.host
            if full_ok != self._full_shown:
                if full_ok:
                    self.full_button.pack(side="right", padx=(0, 3), before=self.title_label)
                else:
                    self.full_button.pack_forget()
                self._full_shown = full_ok
            if full_ok:
                self.full_button.configure(text="⛶ esci" if self._full else "⛶ intero")
            want_button = is_video
            if want_button != self._video_button_shown:
                if want_button:
                    self.video_button.pack(side="right", before=self.title_label)
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
                    self.video_frame.place(in_=self.top if self._full else self.video_host,
                                           relx=0, rely=0, x=0, y=0,
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
