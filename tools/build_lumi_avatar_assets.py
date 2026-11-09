"""Genera i fotogrammi dell'avatar LUMI dall'immagine originale (solo sviluppo, usa Pillow).

L'immagine originale non viene modificata: si ritaglia il volto, si
ricavano palpebre/sguardo/bocca come piccole toppe sovrapposte.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "lumi" / "lumi_originale.png"
OUT = ROOT / "assets" / "lumi"
CROP = (60, 0, 1140, 1150)           # figura intera: capelli, volto, inizio busto
SIZES = (190, 290)                   # altezza in pixel: mini avatar, nucleo HUD
FACE_Y = 690                         # centro del volto (coordinate originali)
EYES = ((509, 586, 470, 562, 568, 604), (712, 586, 664, 758, 568, 604))  # iride cx,cy, x0,x1,y0,y1
IRIS_R = 21
MOUTH_X = (532, 702)
MOUTH_LEVELS = (2, 4, 6, 8, 10, 12, 14, 16)   # 8 aperture: labbra piu' fluide
HAIR = (-1.0, 0.0, 1.0)             # ritardo delle ciocche quando la testa si gira
BREATH = (0.0, 0.33, 0.66, 1.0)     # spalle/petto che salgono piano


def _eye_mask(size, eye, grow=0):
    _, _, x0, x1, y0, y1 = eye
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse((x0 - grow, y0 - grow, x1 + grow, y1 + grow), fill=255)
    return m


def _avg(im, box):
    patch = im.crop(box).convert("RGB").resize((1, 1), Image.BOX)
    return patch.getpixel((0, 0))


def blink(im):
    out = im.copy()
    for eye in EYES:
        cx, cy, x0, x1, y0, y1 = eye
        skin = _avg(im, (x0 + 10, y1 + 12, x1 - 10, y1 + 24))
        lid = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lid)
        for y in range(y0 - 6, y1 + 7):
            t = (y - (y0 - 6)) / (y1 - y0 + 12)
            k = 1.10 - 0.16 * t
            d.line((x0 - 6, y, x1 + 6, y), fill=(int(skin[0] * k), int(skin[1] * k), int(skin[2] * k), 255))
        mask = _eye_mask(im.size, eye, 2).filter(ImageFilter.GaussianBlur(3))
        out.paste(lid, (0, 0), mask)
        ImageDraw.Draw(out).arc((x0 + 4, y0 - 14, x1 - 4, y1 - 2), 30, 150, fill=(14, 32, 60, 255), width=2)
    return out


def gaze(im, dx):
    """Sposta l'iride con un campo di spostamento che vale zero agli angoli."""
    out = im.copy()
    src, dst = im.load(), out.load()
    for eye in EYES:
        cx, cy, x0, x1, y0, y1 = eye
        for y in range(y0 - 2, y1 + 3):
            for x in range(x0, x1 + 1):
                if x <= cx:
                    w = (x - x0) / max(1, cx - x0)
                else:
                    w = (x1 - x) / max(1, x1 - cx)
                w = math.sin(max(0.0, w) * math.pi / 2) ** 2
                sx = x - dx * w
                a = int(math.floor(sx)); f = sx - a
                pa, pb = src[a, y], src[a + 1, y]
                dst[x, y] = tuple(int(pa[i] * (1 - f) + pb[i] * f) for i in range(4))
    return out


def mouth(im, d):
    """Apre la bocca: il labbro inferiore scende, quello superiore sale un
    poco, angoli quasi fermi; interno scuro con sfumatura."""
    out = im.copy()
    src = im.load()
    dst = out.load()
    x0, x1 = MOUTH_X
    cx, hw = (x0 + x1) / 2, (x1 - x0) / 2

    def sample(x, sy, lo, hi):
        sy = min(max(sy, lo), hi)
        a = int(sy)
        b = min(a + 1, hi)
        f = sy - a
        pa, pb = src[x, a], src[x, b]
        return tuple(int(pa[i] * (1 - f) + pb[i] * f) for i in range(4))

    for x in range(x0, x1 + 1):
        u = (x - cx) / hw
        open_ = d * max(0.0, 1 - u * u) ** 1.1
        if open_ < 0.5:
            continue
        lift = open_ * 0.28
        drop = open_ - lift
        seam = min(range(778, 806), key=lambda y: sum(src[x, y][:3]))
        top, bottom = seam - 34, seam + 70
        for y in range(top, seam):                       # labbro superiore sale
            if y < seam - lift:
                sy = top + (y - top) * (seam - top) / (seam - lift - top)
                dst[x, y] = sample(x, sy, top, seam)
        for y in range(int(seam - lift), bottom):         # interno + labbro inferiore
            if y < seam + drop:
                depth = (y - (seam - lift)) / max(1.0, open_)
                g = int(14 + 14 * (1 - abs(depth - .45) * 2))
                dst[x, y] = (g, g // 2 + 6, g + 26, 255)
            else:
                sy = seam + (y - seam - drop) * (bottom - seam) / (bottom - seam - drop)
                dst[x, y] = sample(x, sy, seam, bottom)
    return out


POSES = tuple(round(-1 + i / 6, 3) for i in range(13))   # 13 pose: rotazione fluida


def turn(im, yaw, amount=24.0, theta=0.02, hair=0.0, breath=0.0):
    """Leggera rotazione della testa (destra/sinistra) con un campo di
    spostamento morbido: volto e lineamenti si spostano piu' del contorno
    (parallasse), piccola inclinazione attorno al collo, busto fermo."""
    import numpy as np
    from scipy.ndimage import map_coordinates
    if yaw == 0 and hair == 0 and breath == 0:
        return im.copy()
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    head = np.exp(-(((x - 600) / 270) ** 2 + ((y - 560) / 340) ** 2))
    head *= np.clip((1000 - y) / 150, 0, 1)
    features = np.exp(-(((x - 606) / 95) ** 2 + ((y - 690) / 130) ** 2))
    t = theta * yaw
    dx = amount * yaw * (head + 0.6 * features) - t * (y - 960) * head
    dy = t * (x - 600) * head
    if hair:
        # Ciocche fuori dall'ovale del volto: piu' mobili verso le punte.
        r = np.sqrt(((x - 606) / 195) ** 2 + ((y - 650) / 265) ** 2)
        loose = np.clip((r - 1.0) / 0.35, 0, 1) * np.clip((y - 280) / 520, 0, 1)
        loose *= np.clip((990 - y) / 60, 0, 1)
        dx += 11.0 * hair * loose ** 1.3
    if breath:
        # Respiro: spalle e petto salgono e si allargano appena.
        chest = np.clip((y - 1000) / 110, 0, 1)
        dy += -6.0 * breath * chest
        dx += (x - 600) * 0.005 * breath * chest
    out = np.stack([map_coordinates(a[..., c], [y - dy, x - dx], order=1, mode="constant", cval=0)
                    for c in range(4)], -1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def fade_bottom(im, band=0.14):
    """Sfuma il taglio del busto invece di una riga netta."""
    alpha = im.getchannel("A")
    ap = alpha.load()
    w, h = im.size
    start = int(h * (1 - band))
    for y in range(start, h):
        k = (h - 1 - y) / max(1, h - 1 - start)
        for x in range(w):
            ap[x, y] = int(ap[x, y] * k)
    im.putalpha(alpha)
    return im


def _patch(frame, ref_array):
    import numpy as np
    diff = np.abs(np.asarray(frame).astype(np.int16) - ref_array)[..., :3].max(-1) > 2
    if not diff.any():
        return None
    rows, cols = np.where(diff)
    return (int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1)


def main() -> int:
    import numpy as np
    full = Image.open(SRC).convert("RGBA")
    states = {"blink": blink(full), "look_l": gaze(full, -4), "look_r": gaze(full, 4)}
    for n, d in enumerate(MOUTH_LEVELS, 1):
        states[f"mouth{n}"] = mouth(full, d)
    for old in OUT.glob("lumi_[0-9]*.png"):
        old.unlink()
    cw, ch = CROP[2] - CROP[0], CROP[3] - CROP[1]
    rest_hair = HAIR.index(0.0)
    manifest = {"source": SRC.name, "crop": CROP, "face_y": (FACE_Y - CROP[1]) / ch,
                "poses": list(POSES), "rest_pose": POSES.index(0.0),
                "hair": list(HAIR), "rest_hair": rest_hair,
                "breath": list(BREATH), "mouth_levels": len(MOUTH_LEVELS), "sizes": {}}
    full_frames = []
    for yaw in POSES:
        bases = [turn(full, yaw, hair=h) for h in HAIR]
        patches = {k: turn(v, yaw) for k, v in states.items()}
        full_frames.append((bases, patches))
    breaths = [turn(full, 0.0, breath=b) for b in BREATH]

    def shrink(im, width, size):
        return fade_bottom(im.crop(CROP).resize((width, size), Image.LANCZOS))

    for size in SIZES:
        width = round(size * cw / ch)
        poses = []
        for index, (bases, patches) in enumerate(full_frames):
            small_bases = [shrink(im, width, size) for im in bases]
            for h, im in enumerate(small_bases):
                im.save(OUT / f"lumi_{size}_p{index}_h{h}.png", optimize=True)
            ref = np.asarray(small_bases[rest_hair]).astype(np.int16)
            entry = {}
            for name, frame in patches.items():
                small = shrink(frame, width, size)
                box = _patch(small, ref)
                if box:
                    small.crop(box).save(OUT / f"lumi_{size}_p{index}_{name}.png", optimize=True)
                    entry[name] = list(box[:2])
            poses.append(entry)
        rest = np.asarray(shrink(breaths[0], width, size)).astype(np.int16)
        breath_boxes = []
        for level, frame in enumerate(breaths):
            small = shrink(frame, width, size)
            box = _patch(small, rest) if level else None
            if box:
                small.crop(box).save(OUT / f"lumi_{size}_b{level}.png", optimize=True)
            breath_boxes.append(list(box[:2]) if box else None)
        manifest["sizes"][str(size)] = {"poses": poses, "breath": breath_boxes}
    (OUT / "lumi_avatar.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
