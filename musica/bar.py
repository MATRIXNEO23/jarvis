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
