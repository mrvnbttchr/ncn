"""Gleicht die Mitglieder-Logos optisch an.

1. Schneidet leere Ränder (transparent oder weiß) aus assets/logos/*.png weg.
2. Berechnet für jedes Logo eine Höhe, sodass alle etwa dieselbe Fläche haben
   (breite Logos werden flacher, quadratische höher), begrenzt durch MAX_W/MAX_H.
3. Schreibt die Höhe als style="--h:…" an das <img> in index.html.

Aufruf (aus dem NCN-Ordner): python3 tools/normalize_logos.py
Neue Logos einfach nach assets/logos legen, im HTML einbinden und das Skript erneut ausführen.
"""
import hashlib
import math
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "logos"
HTML = ROOT / "index.html"

AREA = 6000      # Ziel-Fläche in px² (Desktop)
MAX_W = 180      # Höchstbreite in px
MAX_H = 64       # Höchsthöhe in px
PAD = 2          # Rand, der nach dem Zuschneiden stehen bleibt


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


def main():
    html = HTML.read_text()
    for f in sorted(LOGOS.glob("*.png")):
        im = Image.open(f)
        box = content_box(im)
        if box != (0, 0, *im.size):
            im.crop(box).save(f, optimize=True)
            im = Image.open(f)
        w, h = im.size
        hpx = height_for(w / h)
        v = hashlib.md5(f.read_bytes()).hexdigest()[:8]   # Cache-Busting: neue Datei -> neue URL
        pat = re.compile(r'<img src="assets/logos/' + re.escape(f.name) + r'(?:\?v=\w+)?"(?: style="--h:\d+")?')
        html, n = pat.subn(f'<img src="assets/logos/{f.name}?v={v}" style="--h:{hpx}"', html)
        print(f"{f.name:22} {w}x{h}  ratio {w/h:.2f}  ->  {round(hpx*w/h)}x{hpx}px  ({n}x im HTML)")
    HTML.write_text(html)


if __name__ == "__main__":
    main()
