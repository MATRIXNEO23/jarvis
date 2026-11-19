"""High-fidelity PNG lighting and Earth surfaces rendered with Python stdlib.

The old Pavilion renders each texture ONCE in a daemon worker, not on every
Tkinter frame. Tk PhotoImage creation remains on the GUI thread. No Pillow,
video, GPU, network, downloaded models or third-party dependencies are used.

These textures are decorative: country outlines are schematic and city lights
are approximate, never live satellite imagery or the user's location.
"""
from __future__ import annotations

import base64
from functools import lru_cache
import math
from queue import SimpleQueue
import struct
import threading
import zlib

BG = (1, 7, 17)
COLORS = {
    "idle": (24, 203, 255),
    "listening": (255, 150, 39),
    "speaking": (49, 245, 158),
}


def _chunk(name: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + name + payload
            + struct.pack(">I", zlib.crc32(name + payload) & 0xffffffff))


def rgba_png(width: int, height: int, pixels: bytes) -> bytes:
    """Encode RGBA PNG without Pillow or an image library."""
    if (type(width) is not int or type(height) is not int
            or not 1 <= width <= 1024 or not 1 <= height <= 1024
            or len(pixels) != width * height * 4):
        raise ValueError("Invalid RGBA image dimensions")
    row_size = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * row_size:(y + 1) * row_size])
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + _chunk(b"IEND", b"")
    )


def reactor_glow_png(size: int, mode: str = "idle") -> bytes:
    """Layered emissive bloom, luminous arcs and soft core illumination."""
    if type(size) is not int or size < 96 or size > 600:
        raise ValueError("Invalid reactor size")
    if mode not in COLORS:
        raise ValueError("Invalid reactor mode")
    cr, cg, cb = COLORS[mode]
    p = bytearray(size * size * 4)
    center = (size - 1) / 2
    radius = size * .444
    rings = (
        (.98, 2.6, .50, 28), (.885, 4.8, .85, 19),
        (.79, 3.9, 1.00, 16), (.68, 2.4, .50, 29),
        (.59, 6.8, 1.00, 13), (.47, 3.5, .72, 12),
        (.375, 2.4, .66, 16),
    )
    for y in range(size):
        dy = y - center
        for x in range(size):
            dx = x - center
            d = math.hypot(dx, dy)
            if d > radius * 1.17:
                continue
            ang = math.atan2(dy, dx)
            glow = 0.0
            for scale, thick, power, sectors in rings:
                delta = (d - radius * scale) / thick
                if abs(delta) > 4.0:
                    continue
                angular = .40 + .60 * max(
                    0.0, math.sin(ang * sectors + scale * 15.0))
                glow += power * math.exp(-.5 * delta * delta) * angular
            # Dense, gently luminous center like the reference screenshot.
            if d < radius * .53:
                glow += .12 * (1 - d / (radius * .55)) ** 2
            if d < radius * 1.13:
                glow += .15 * math.exp(
                    -((d - radius * .92) / (radius * .13)) ** 2)
            if glow < .018:
                continue
            power = min(1.0, glow)
            # Less neon bloom: preserve the detailed dark-blue vector rings
            # instead of washing the HUD into a uniform bright disk.
            alpha = min(148, int(104 * power + 12 * min(1.0, glow * 2)))
            # Pale center of the glow with a saturated colored halo.
            white = min(1.0, power * .32)
            r = round(cr * (1-white) + 218 * white)
            g = round(cg * (1-white) + 246 * white)
            b = round(cb * (1-white) + 255 * white)
            off = (y * size + x) * 4
            p[off:off+4] = bytes((r, g, b, alpha))
    return rgba_png(size, size, bytes(p))


@lru_cache(maxsize=2)
def land_grid(width: int = 720, height: int = 360) -> tuple[bytes, ...]:
    """Scan-convert the project's existing schematic coastline polygons."""
    from hud_reference import COASTS
    grid = [bytearray(width) for _ in range(height)]
    for y in range(height):
        latitude = 90.0 - (y + .5) * 180.0 / height
        row = grid[y]
        for polygon in COASTS:
            crossings = []
            prev = polygon[-1]
            for point in polygon:
                x1, y1 = prev
                x2, y2 = point
                if (y1 > latitude) != (y2 > latitude):
                    crossings.append(x1 + (latitude - y1) * (x2-x1) / (y2-y1))
                prev = point
            crossings.sort()
            for left, right in zip(crossings[::2], crossings[1::2]):
                a = max(0, round((left + 180) * width / 360))
                b = min(width, round((right + 180) * width / 360))
                if b > a:
                    row[a:b] = b"\x01" * (b-a)
    return tuple(bytes(row) for row in grid)


def _city_glow(p: bytearray, size: int, radius: float, yaw: float) -> None:
    from hud_reference import LIGHTS
    cx = (size - 1) / 2
    cy = cx
    for lat, lon in LIGHTS:
        latitude = math.radians(lat)
        longitude = math.radians(lon) + yaw
        depth = math.cos(latitude) * math.cos(longitude)
        if depth <= .05:
            continue
        xpos = int(cx + radius * math.cos(latitude) * math.sin(longitude))
        ypos = int(cy - radius * math.sin(latitude))
        for dy in range(-4, 5):
            y = ypos + dy
            if y < 0 or y >= size:
                continue
            for dx in range(-4, 5):
                x = xpos + dx
                if x < 0 or x >= size:
                    continue
                d2 = dx*dx + dy*dy
                if d2 > 17:
                    continue
                off = (y*size + x)*4
                if p[off+3] == 0:
                    continue
                strength = .58 * math.exp(-d2 / 5.5)
                for ch, goal in enumerate((255, 211, 153)):
                    p[off+ch] = min(
                        255, round(p[off+ch] * (1-strength) + goal * strength))


def earth_png(size: int, yaw: float = 0.0) -> bytes:
    """One pre-rendered projection of a shaded, textured miniature Earth."""
    if type(size) is not int or size < 100 or size > 480:
        raise ValueError("Invalid Earth size")
    if not -math.tau <= yaw <= math.tau:
        raise ValueError("Invalid Earth angle")
    grid = land_grid()
    gh = len(grid)
    gw = len(grid[0])
    radius = size * .476
    center = (size - 1) / 2
    p = bytearray(size * size * 4)
    for y in range(size):
        dy = (y-center)/radius
        dyy = dy * dy
        if dyy > 1:
            continue
        lat = math.asin(max(-1.0, min(1.0, -dy)))
        lat_deg = math.degrees(lat)
        row = grid[min(gh-1, max(0, int((90-lat_deg) * gh/180)))]
        for x in range(size):
            dx = (x-center)/radius
            dist2 = dx*dx + dyy
            if dist2 > 1:
                continue
            depth = math.sqrt(max(0, 1-dist2))
            lon = math.atan2(dx, depth) - yaw
            lon_deg = (math.degrees(lon)+180) % 360 - 180
            pos = min(gw-1,max(0,int((lon_deg+180)*gw/360)))
            land = bool(row[pos])
            # Procedural illuminated terrain and subtle dark-ocean texture.
            waves = (.5 + .27*math.sin(lon*19 + lat*23)
                     + .16*math.sin(lon*33-lat*21)
                     + .09*math.sin(lon*75+lat*33))
            cloud = max(0.0, math.sin(lon*17+lat*14)
                        * math.sin(lon*9-lat*37))*.13
            illumination = max(.22, min(1.0,
                .39 + .48*depth - .28*dx - .20*dy))
            rim = max(0.0, (1.0-depth)**5)
            if land:
                shade = illumination * (.71 + .32*waves)
                base = (42 + 50*waves, 75 + 64*waves, 86 + 73*waves)
            else:
                shade = illumination * (.73 + .22*waves)
                base = (6 + 11*waves, 34 + 39*waves, 62 + 61*waves)
            atmosphere = 110 * rim
            r = min(255, round(base[0]*shade + atmosphere*.25 + cloud*56))
            g = min(255, round(base[1]*shade + atmosphere*.72 + cloud*73))
            b = min(255, round(base[2]*shade + atmosphere*1.20 + cloud*83))
            off = (y*size + x)*4
            p[off:off+4] = bytes((r,g,b,255))
    _city_glow(p,size,radius,yaw)
    return rgba_png(size,size,bytes(p))


class RasterArtWorker:
    """Pre-renders assets in a daemon thread; Tk calls remain main-thread-only."""

    def __init__(self) -> None:
        self._result = SimpleQueue()
        self._pending = set()
        self._ready = {}

    def request(self,kind: str,size: int) -> None:
        key = (kind,int(size))
        if key in self._ready or key in self._pending:
            return
        if kind not in ("reactor","earth") or not 96 <= size <= 500:
            return
        self._pending.add(key)

        def work():
            try:
                if kind == "reactor":
                    # The outer reactor texture remains cyan in all voice
                    # states. Generate only one image: lower CPU/RAM on i3.
                    result = [reactor_glow_png(size,"idle")]
                else:
                    # A slight geographic turn under moving orbits is smoother
                    # than flickering a low-poly globe every Tk redraw.
                    result = [earth_png(size,angle) for angle in (
                        -.24,-.18,-.12,-.06,0,.06,.12,.18,.24)]
                self._result.put((key,result))
            except Exception:
                self._result.put((key,None))

        threading.Thread(target=work,daemon=True,
                         name="LUMI-HUD-Raster").start()

    def get(self,kind: str,size: int):
        while not self._result.empty():
            key,value = self._result.get()
            self._pending.discard(key)
            self._ready[key] = value
        return self._ready.get((kind,int(size)))

    def clear(self) -> None:
        """Only clear cached bytes; worker never controls Tk widgets."""
        self._ready.clear()


ASSETS = RasterArtWorker()


def photoimage_from_png(tk, png: bytes):
    """Decode a PNG in Tk without a third-party dependency."""
    return tk.PhotoImage(data=base64.b64encode(png),format="png")
