"""Barra musica sotto il nucleo: compare solo quando c'è musica."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class MusicBar:
    def __init__(self, host, service, *, on_message=None):
        self.host = host                 # il canvas del nucleo HUD
        self.service = service
        self.on_message = on_message or (lambda text: None)
        self.frame = tk.Frame(host, bg="#031522", highlightthickness=1,
                              highlightbackground="#1b6f8f")
        self.title = tk.StringVar(value="")
        tk.Label(self.frame, textvariable=self.title, bg="#031522", fg="#d7f6ff",
                 font=("Segoe UI", 9), width=26, anchor="w").pack(side="left", padx=(6, 4))
        self.toggle_button = ttk.Button(self.frame, text="⏸", width=3, command=self._toggle)
        self.toggle_button.pack(side="left")
        ttk.Button(self.frame, text="⏹", width=3, command=lambda: self._do("stop")).pack(side="left")
        ttk.Button(self.frame, text="⏭", width=3, command=lambda: self._do("next")).pack(side="left")
        self.volume = tk.IntVar(value=service.settings.get("volume", 70))
        self.volume_scale = ttk.Scale(self.frame, from_=0, to=100, variable=self.volume,
                                      length=80, command=self._volume)
        self.volume_scale.pack(side="left", padx=(4, 6))
        self._shown = False
        self._job = None
        self._volume_job = None
        self.refresh()

    def _do(self, action: str) -> None:
        message = self.service.handle(action)
        if message:
            self.on_message(message)
        self.refresh(reschedule=False)

    def _toggle(self) -> None:
        snap = self.service.snapshot()
        self._do("pause" if snap["state"] == "playing" and snap["mode"] == "local" else
                 "resume" if snap["mode"] == "local" else "pause")

    def _volume(self, value) -> None:
        if self.service.snapshot()["mode"] != "local":
            return
        if self._volume_job is not None:
            self.host.after_cancel(self._volume_job)
        self._volume_job = self.host.after(250, lambda: self.service.set_volume(int(float(value))))

    def refresh(self, reschedule: bool = True) -> None:
        try:
            snap = self.service.snapshot() if self.service.is_enabled() else {"mode": None}
            active = snap.get("mode") is not None and snap.get("state") != "stopped"
            if active:
                self.title.set(snap["title"][:40])
                self.toggle_button.configure(text="▶" if snap["state"] == "paused" else "⏸")
                if snap["mode"] == "browser":
                    self.volume_scale.state(["disabled"])
                else:
                    self.volume_scale.state(["!disabled"])
                if not self._shown:
                    self.frame.place(in_=self.host, relx=0.5, rely=0.93, anchor="s")
                    self._shown = True
            elif self._shown:
                self.frame.place_forget()
                self._shown = False
        except tk.TclError:
            return
        if reschedule:
            self._job = self.host.after(500, self.refresh)
