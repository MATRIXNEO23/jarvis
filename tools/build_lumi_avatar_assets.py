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
CROP = (300, 330, 900, 930)          # quadrato del volto, coordinate originali
SIZES = (96, 128, 160, 200)
EYES = ((509, 586, 470, 562, 568, 604), (712, 586, 664, 758, 568, 604))  # iride cx,cy, x0,x1,y0,y1
IRIS_R = 21
MOUTH_X = (532, 702)
MOUTH_LEVELS = (4, 8, 13)


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
    out = im.copy()
    src = im.load()
    dst = out.load()
    x0, x1 = MOUTH_X
    cx, hw = (x0 + x1) / 2, (x1 - x0) / 2
    for x in range(x0, x1 + 1):
        u = (x - cx) / hw
        s = d * max(0.0, 1 - u * u) ** 0.9
        if s < 0.5:
            continue
        seam = min(range(778, 806), key=lambda y: sum(src[x, y][:3]))
        bottom = seam + 70
        for y in range(seam, bottom):
            if y < seam + s:
                depth = (y - seam) / max(1.0, s)
                g = int(18 + 12 * (1 - abs(depth - .5) * 2))
                dst[x, y] = (g, g // 2 + 8, g + 28, 255)
            else:
                sy = seam + (y - seam - s) * (bottom - seam) / (bottom - seam - s)
                a, b = int(sy), min(int(sy) + 1, bottom)
                f = sy - a
                pa, pb = src[x, a], src[x, b]
                dst[x, y] = tuple(int(pa[i] * (1 - f) + pb[i] * f) for i in range(4))
    return out


def circle(im):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse((2, 2, im.size[0] - 3, im.size[1] - 3), fill=255)
    bg = Image.new("RGBA", im.size, (4, 14, 26, 255))
    bg.alpha_composite(im)
    bg.putalpha(m.filter(ImageFilter.GaussianBlur(1)))
    return bg


def main() -> int:
    full = Image.open(SRC).convert("RGBA")
    frames = {"base": full, "blink": blink(full), "look_l": gaze(full, -4),
              "look_r": gaze(full, 4)}
    for n, d in enumerate(MOUTH_LEVELS, 1):
        frames[f"mouth{n}"] = mouth(full, d)
    manifest = {"source": SRC.name, "crop": CROP, "sizes": {}}
    for size in SIZES:
        scaled = {k: circle(v.crop(CROP).resize((size, size), Image.LANCZOS))
                  for k, v in frames.items()}
        base = scaled["base"]
        base.save(OUT / f"lumi_{size}.png", optimize=True)
        entry = {}
        for name, frame in scaled.items():
            if name == "base":
                continue
            diff = Image.new("L", base.size, 0)
            dp, bp, fp = diff.load(), base.load(), frame.load()
            for y in range(size):
                for x in range(size):
                    if max(abs(bp[x, y][i] - fp[x, y][i]) for i in range(3)) > 2:
                        dp[x, y] = 255
            box = diff.getbbox()
            if not box:
                continue
            frame.crop(box).save(OUT / f"lumi_{size}_{name}.png", optimize=True)
            entry[name] = list(box[:2])
        manifest["sizes"][str(size)] = entry
    (OUT / "lumi_avatar.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
