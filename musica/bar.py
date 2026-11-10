"""Barra musica sotto il nucleo, elenco brani (☰) e riquadro video al posto del globo."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import library


class TrackList:
    """Elenco dei brani della cartella: ricerca in alto, doppio clic per suonare."""

    def __init__(self, parent, service, on_message):
        self.service = service
        self.on_message = on_message
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Brani")
        self.window.geometry("460x520")
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="both", expand=True)
        self.query = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.query)
        entry.pack(fill="x")
        entry.focus_set()
        self.query.trace_add("write", lambda *_a: self.fill())
        holder = ttk.Frame(frame)
        holder.pack(fill="both", expand=True, pady=(8, 0))
        self.listbox = tk.Listbox(holder, activestyle="none", bg="#031522", fg="#d7f6ff",
                                  selectbackground="#1b6f8f", highlightthickness=0)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", self.play_selected)
        self.listbox.bind("<Return>", self.play_selected)
        self.status = tk.StringVar()
        ttk.Label(frame, textvariable=self.status).pack(anchor="w", pady=(6, 0))
        self.shown = []
        self.fill()

    def fill(self):
        tracks = self.service.tracks()
        words = library.normalized(self.query.get()).split()
        if words:
            tracks = [t for t in tracks
                      if all(w in library.normalized(" ".join(t.parts[-3:])) for w in words)]
        self.shown = list(tracks[:3000])
        self.listbox.delete(0, "end")
        for track in self.shown:
            mark = "▶ " if library.is_video(track) else "♪ "
            self.listbox.insert("end", mark + track.stem)
        total = len(self.service.tracks())
        self.status.set(f"{len(self.shown)} di {total} brani. Doppio clic per ascoltare."
                        if total else "Nessun brano: scegli la cartella in Gestisci add-on > Musica.")

    def play_selected(self, _event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        message = self.service.play_tracks(self.shown, selection[0])
        if message:
            self.on_message(message)


class MusicBar:
    def __init__(self, host, service, *, on_message=None, video_host=None):
        self.host = host                 # il canvas del nucleo HUD
        self.service = service
        self.on_message = on_message or (lambda text: None)
        self.frame = tk.Frame(host, bg="#031522", highlightthickness=1,
                              highlightbackground="#1b6f8f")
        ttk.Button(self.frame, text="☰", width=3, command=self.open_list).pack(side="left", padx=(4, 0))
        self.title = tk.StringVar(value="")
        tk.Label(self.frame, textvariable=self.title, bg="#031522", fg="#d7f6ff",
                 font=("Segoe UI", 9), width=22, anchor="w").pack(side="left", padx=(6, 4))
        ttk.Button(self.frame, text="⏮", width=3, command=lambda: self._do("prev")).pack(side="left")
        self.toggle_button = ttk.Button(self.frame, text="⏸", width=3, command=self._toggle)
        self.toggle_button.pack(side="left")
        ttk.Button(self.frame, text="⏹", width=3, command=lambda: self._do("stop")).pack(side="left")
        ttk.Button(self.frame, text="⏭", width=3, command=lambda: self._do("next")).pack(side="left")
        self.volume = tk.IntVar(value=service.settings.get("volume", 70))
        self.volume_scale = ttk.Scale(self.frame, from_=0, to=100, variable=self.volume,
                                      length=80, command=self._volume)
        self.volume_scale.pack(side="left", padx=(4, 6))
        # Riquadro video: stessa area del globo, visibile solo durante un video.
        self.video_host = video_host
        self.video_frame = None
        if video_host is not None and getattr(service, "video", None) is not None:
            self.video_frame = tk.Frame(video_host, bg="#000000", highlightthickness=0, bd=0)
            service.video_hwnd = self.video_frame.winfo_id()
        self._shown = False
        self._video_shown = False
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
        if snap["mode"] is None:
            self.open_list()
            return
        self._do("pause" if snap["state"] == "playing" else "resume")

    def _volume(self, value) -> None:
        if self._volume_job is not None:
            self.host.after_cancel(self._volume_job)
        self._volume_job = self.host.after(250, lambda: self.service.set_volume(int(float(value))))

    def refresh(self, reschedule: bool = True) -> None:
        try:
            enabled = self.service.is_enabled()
            snap = self.service.snapshot() if enabled else {"mode": None, "state": "stopped"}
            active = snap.get("mode") is not None and snap.get("state") != "stopped"
            if enabled:
                self.title.set(snap["title"][:36] if active else "Musica")
                self.toggle_button.configure(text="▶" if not active or snap["state"] == "paused"
                                             else "⏸")
                if snap.get("mode") == "browser":
                    self.volume_scale.state(["disabled"])
                else:
                    self.volume_scale.state(["!disabled"])
                if not self._shown:
                    self.frame.place(in_=self.host, relx=0.5, rely=0.93, anchor="s")
                    self._shown = True
            elif self._shown:
                self.frame.place_forget()
                self._shown = False
            want_video = enabled and snap.get("mode") == "video"
            if self.video_frame is not None and want_video != self._video_shown:
                if want_video:
                    self.video_frame.place(in_=self.video_host, relx=0, rely=0,
                                           relwidth=1, relheight=1)
                    self.video_frame.lift()
                else:
                    self.video_frame.place_forget()
                self._video_shown = want_video
        except tk.TclError:
            return
        if reschedule:
            self._job = self.host.after(500, self.refresh)
