"""Avatar 2D di LUMI: occhi vivi (battito, sguardo) e bocca in lip sync.

Usa solo Tk PhotoImage (nessuna dipendenza): l'immagine di base e le
piccole toppe per palpebre/sguardo/bocca sono generate in anticipo da
tools/build_lumi_avatar_assets.py partendo dall'immagine originale.
"""
from __future__ import annotations

import json
import math
import random
import sys
import threading
import time
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent / "assets" / "lumi"
_MANIFEST_CACHE: dict | None = None


def manifest() -> dict:
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is None:
        try:
            _MANIFEST_CACHE = json.loads(
                (ASSET_DIR / "lumi_avatar.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _MANIFEST_CACHE = {"sizes": {}}
    return _MANIFEST_CACHE


def pick_size(height: float) -> int | None:
    """Altezza disponibile in pixel -> altezza dell'immagine pronta piu' adatta."""
    sizes = sorted(int(s) for s in manifest().get("sizes", {}))
    if not sizes:
        return None
    fitting = [s for s in sizes if s <= height]
    return fitting[-1] if fitting else sizes[0]


def mouth_level(value: float) -> int:
    """Volume normalizzato 0..1 -> apertura bocca 0..3."""
    if value < .12:
        return 0
    if value < .35:
        return 1
    if value < .65:
        return 2
    return 3


class LipSync:
    """Curva del volume condivisa tra il thread della voce e la UI."""

    def __init__(self, fps: int = 30):
        self.fps = fps
        self._lock = threading.Lock()
        self._envelope: list[float] = []
        self._start = 0.0

    def push(self, envelope) -> None:
        with self._lock:
            self._envelope = [float(v) for v in (envelope or ())]
            self._start = time.monotonic()

    def level(self, now: float | None = None) -> float | None:
        """Valore corrente o None se non c'e' audio con curva in corso."""
        now = time.monotonic() if now is None else now
        with self._lock:
            if not self._envelope:
                return None
            index = int((now - self._start) * self.fps)
            if index < 0 or index >= len(self._envelope):
                return None
            return self._envelope[index]


LIPSYNC = LipSync()


class AvatarFace:
    """Volto animato disegnato su un Canvas Tk esistente."""

    def __init__(self, rng: random.Random | None = None):
        self.canvas = None
        self.size = None
        self.items = {}
        self.photos = {}
        self.offsets = {}
        self.rng = rng or random.Random()
        self._next_blink = 0.0
        self._blink_until = 0.0
        self._next_gaze = 0.0
        self._gaze = None
        self._eye_state = None
        self._mouth_state = None
        self._shift = (0, 0)
        self._phase = self.rng.uniform(0, 100)

    def attach(self, canvas, cx: float, cy: float, height: float) -> bool:
        """Figura intera centrata in orizzontale, volto all'altezza cy."""
        import tkinter as tk
        self.canvas = canvas
        self.items = {}
        self._eye_state = self._mouth_state = None
        self._shift = (0, 0)
        size = pick_size(height)
        if size is None:
            return False
        try:
            if size != self.size or not self.photos:
                self.photos = {"base": tk.PhotoImage(
                    master=canvas, file=str(ASSET_DIR / f"lumi_{size}.png"))}
                self.offsets = manifest()["sizes"][str(size)]
                for name in self.offsets:
                    self.photos[name] = tk.PhotoImage(
                        master=canvas, file=str(ASSET_DIR / f"lumi_{size}_{name}.png"))
                self.size = size
        except (tk.TclError, OSError, KeyError):
            self.photos = {}
            return False
        base = self.photos["base"]
        face_y = float(manifest().get("face_y", .5))
        x0, y0 = cx - base.width() / 2, cy - face_y * size
        self.origin = (x0, y0)
        self.items["base"] = canvas.create_image(x0, y0, anchor="nw",
                                                 image=self.photos["base"])
        self.items["eyes"] = canvas.create_image(x0, y0, anchor="nw", state="hidden")
        self.items["mouth"] = canvas.create_image(x0, y0, anchor="nw", state="hidden")
        return True

    def _show(self, slot: str, name: str | None) -> None:
        item = self.items.get(slot)
        if item is None:
            return
        if name is None or name not in self.photos:
            self.canvas.itemconfigure(item, state="hidden")
            return
        dx, dy = self.offsets[name]
        x0, y0 = self.origin
        x0, y0 = x0 + self._shift[0], y0 + self._shift[1]
        self.canvas.coords(item, x0 + dx, y0 + dy)
        self.canvas.itemconfigure(item, image=self.photos[name], state="normal")

    def eye_frame(self, now: float) -> str | None:
        if now >= self._next_blink:
            self._blink_until = now + .13
            # Ogni tanto un doppio battito, come una persona vera.
            gap = .25 if self.rng.random() < .15 else self.rng.uniform(2.5, 6.0)
            self._next_blink = now + gap
        if now < self._blink_until:
            return "blink"
        if now >= self._next_gaze:
            self._gaze = self.rng.choice((None, None, "look_l", "look_r"))
            self._next_gaze = now + self.rng.uniform(1.2, 4.0)
        return self._gaze

    def mouth_frame(self, now: float, speaking: bool = False) -> str | None:
        """Bocca guidata SOLO dall'audio in riproduzione.

        La curva arriva un istante prima che parta il suono (dopo la sintesi),
        quindi la bocca non si muove mentre la voce viene ancora preparata.
        Con la voce Windows non c'e' curva: la bocca resta chiusa, invece di
        muoversi fuori tempo. `speaking` resta solo per compatibilita'.
        """
        level = mouth_level(LIPSYNC.level(now) or 0.0)
        return f"mouth{level}" if level else None

    def head_offset(self, now: float) -> tuple[int, int]:
        """Lieve oscillazione della testa: respiro + ondeggiamento, piu' vivo quando parla."""
        t = now + self._phase
        talk = LIPSYNC.level(now) or 0.0
        amp = (self.size or 180) / 180.0
        dx = amp * (2.2 * math.sin(t * 0.55) + 0.8 * math.sin(t * 1.3))
        dy = amp * (1.4 * math.sin(t * 0.9 + 1.0) + 1.6 * talk * math.sin(t * 9.0))
        return round(dx), round(dy)

    def _apply_shift(self, shift: tuple[int, int]) -> None:
        mx, my = shift[0] - self._shift[0], shift[1] - self._shift[1]
        if not (mx or my):
            return
        for item in self.items.values():
            self.canvas.move(item, mx, my)
        self._shift = shift

    def tick(self, mode: str = "idle", now: float | None = None) -> None:
        if not self.items:
            return
        now = time.monotonic() if now is None else now
        self._apply_shift(self.head_offset(now))
        eye = self.eye_frame(now)
        if eye != self._eye_state:
            self._show("eyes", eye)
            self._eye_state = eye
        mouth = self.mouth_frame(now)
        if mouth != self._mouth_state:
            self._show("mouth", mouth)
            self._mouth_state = mouth


def _work_area(root) -> tuple[int, int, int, int]:
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            rect = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                return rect.left, rect.top, rect.right, rect.bottom
        except Exception:
            pass
    return 0, 0, root.winfo_screenwidth(), root.winfo_screenheight() - 48


class AvatarDock:
    """Mini avatar in basso a destra quando LUMI e' ridotta a icona.

    Doppio clic: ripristina la finestra principale.
    """

    HEIGHT = 180
    KEY = "#010203"

    def __init__(self, root, mode_provider=lambda: "idle"):
        self.root = root
        self.mode_provider = mode_provider
        self.window = None
        self.face = AvatarFace()
        self._job = None
        root.bind("<Unmap>", self._on_unmap, add="+")
        root.bind("<Map>", self._on_map, add="+")

    def _on_unmap(self, event=None):
        if event is not None and event.widget is not self.root:
            return
        self.root.after(120, self._check_iconic)

    def _check_iconic(self):
        try:
            if self.root.state() == "iconic":
                self.show()
        except Exception:
            pass

    def _on_map(self, event=None):
        if event is not None and event.widget is not self.root:
            return
        self.hide()

    def show(self):
        import tkinter as tk
        if self.window is not None:
            return
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.configure(bg=self.KEY)
        try:
            win.attributes("-topmost", True)
            win.attributes("-transparentcolor", self.KEY)
        except tk.TclError:
            pass
        height = self.HEIGHT
        width = round(height * .94)
        left, top, right, bottom = _work_area(self.root)
        win.geometry(f"{width}x{height}+{right - width - 12}+{bottom - height}")
        canvas = tk.Canvas(win, width=width, height=height, bg=self.KEY,
                           highlightthickness=0, bd=0)
        canvas.pack()
        face_y = float(manifest().get("face_y", .5))
        if not self.face.attach(canvas, width / 2, face_y * height, height):
            canvas.create_text(width / 2, height / 2, text="LUMI", fill="#d9f8ff",
                               font=("Segoe UI", 18, "bold"))
        for widget in (win, canvas):
            widget.bind("<Double-Button-1>", self.restore)
        self.window = win
        self._animate()

    def _animate(self):
        if self.window is None:
            return
        try:
            self.face.tick(self.mode_provider())
        except Exception:
            pass
        self._job = self.window.after(40, self._animate)

    def hide(self):
        win, self.window = self.window, None
        if win is not None:
            if self._job is not None:
                try:
                    win.after_cancel(self._job)
                except Exception:
                    pass
            self._job = None
            win.destroy()

    def restore(self, _event=None):
        self.hide()
        self.root.deiconify()
        self.root.lift()
        try:
            self.root.focus_force()
        except Exception:
            pass
