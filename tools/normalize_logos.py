"""Gleicht die Mitglieder-Logos optisch an und erzeugt die WebP-Dateien für die Website.

Die PNGs in assets/logos sind die Quelldateien, eingebunden werden die WebP-Versionen.

1. Schneidet leere Ränder (transparent oder weiß) aus assets/logos/*.png weg.
2. Erzeugt <name>.webp, wenn sie fehlt oder das PNG gerade zugeschnitten wurde
   (mit --force alle neu). Bestehende WebPs bleiben sonst unverändert.
3. Berechnet für jedes Logo eine Höhe, sodass alle etwa dieselbe Fläche haben
   (breite Logos werden flacher, quadratische höher), begrenzt durch MAX_W/MAX_H.
4. Setzt im <img> in index.html src="…webp?v=<hash>" und style="--h:…".
   Der Hash ändert sich mit der WebP-Datei, damit Browser keine alte Version zeigen.

Aufruf (aus dem NCN-Ordner): python3 tools/normalize_logos.py [--force]
Neues Logo: PNG nach assets/logos legen, im HTML einbinden
(<img src="assets/logos/name.png" …>), Skript ausführen.
"""
import hashlib
import math
import re
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "logos"
HTML = ROOT / "index.html"

AREA = 6000      # Ziel-Fläche in px² (Desktop)
MAX_W = 180      # Höchstbreite in px
MAX_H = 64       # Höchsthöhe in px
PAD = 2          # Rand, der nach dem Zuschneiden stehen bleibt
WEBP = dict(quality=90, method=6)   # verlustbehaftet, Transparenz bleibt erhalten


def content_box(im):
    rgba = im.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 20 and not (r > 240 and g > 240 and b > 240):
                xs.append(x)
                ys.append(y)
    if not xs:
        return (0, 0, w, h)
    return (max(min(xs) - PAD, 0), max(min(ys) - PAD, 0),
            min(max(xs) + 1 + PAD, w), min(max(ys) + 1 + PAD, h))


def height_for(ratio):
    h = math.sqrt(AREA / ratio)
    h = min(h, MAX_H, MAX_W / ratio)
    return round(h)


def save_webp(im, path):
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    im.convert("RGBA" if has_alpha else "RGB").save(path, "WEBP", **WEBP)


def main(force=False):
    html = HTML.read_text()
    for f in sorted(LOGOS.glob("*.png")):
        im = Image.open(f)
        box = content_box(im)
        trimmed = box != (0, 0, *im.size)
        if trimmed:
            im.crop(box).save(f, optimize=True)
            im = Image.open(f)

        webp = f.with_suffix(".webp")
        if force or trimmed or not webp.exists():
            save_webp(im, webp)
            note = "WebP neu"
        else:
            note = "WebP unverändert"

        w, h = im.size
        hpx = height_for(w / h)
        v = hashlib.md5(webp.read_bytes()).hexdigest()[:8]
        pat = re.compile(r'<img src="assets/logos/' + re.escape(f.stem)
                         + r'\.(?:png|webp)(?:\?v=\w+)?"(?: style="--h:\d+")?')
        html, n = pat.subn(f'<img src="assets/logos/{webp.name}?v={v}" style="--h:{hpx}"', html)
        warn = "" if n else "  ⚠ nicht im HTML gefunden"
        print(f"{f.name:22} {w}x{h}  -> {round(hpx * w / h)}x{hpx}px  {note}{warn}")
    HTML.write_text(html)


if __name__ == "__main__":
    main(force="--force" in sys.argv)
