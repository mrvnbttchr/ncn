"""SVG -> transparentes PNG über macOS Quick Look (nur macOS).

Quick Look rendert quadratisch auf Weiß. Deshalb: viewBox quadratisch polstern,
einmal auf weißem und einmal auf schwarzem Hintergrund rendern, daraus den
Alphakanal zurückrechnen und auf die echte viewBox zuschneiden.
Aufruf: python3 tools/rasterize.py eingabe.svg ausgabe.png breite_px
"""
import re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageChops


def _render(svg_text, px, td, name):
    p = Path(td) / f"{name}.svg"
    p.write_text(svg_text)
    subprocess.run(["qlmanage", "-t", "-s", str(px), "-o", td, str(p)], capture_output=True, check=True)
    return Image.open(Path(td) / f"{name}.svg.png").convert("RGB")


def rasterize(svg_path, out_png, width):
    s = Path(svg_path).read_text()
    x, y, w, h = map(float, re.search(r'viewBox="([^"]+)"', s).group(1).split())
    side = max(w, h)
    nx, ny = x - (side - w) / 2, y - (side - h) / 2
    sq = re.sub(r'viewBox="[^"]+"', f'viewBox="{nx} {ny} {side} {side}"', s, count=1)
    sq = re.sub(r'width="[^"]+" height="[^"]+"', f'width="{side}" height="{side}"', sq, count=1)
    bg = f'<rect x="{nx}" y="{ny}" width="{side}" height="{side}" fill="#000"/>'
    sq_black = re.sub(r'(<svg[^>]*>)', r'\1' + bg, sq, count=1)
    px = int(round(width * side / w))
    with tempfile.TemporaryDirectory() as td:
        on_w = _render(sq, px, td, "w")
        on_b = _render(sq_black, px, td, "b")
    # alpha = 1 - (weiß - schwarz)
    diff = ImageChops.subtract(on_w, on_b).convert("L")
    alpha = diff.point(lambda v: 255 - v)
    # Farbe = schwarz-Render / alpha
    rgb = Image.new("RGB", on_b.size)
    pb, pa, po = on_b.load(), alpha.load(), rgb.load()
    for j in range(on_b.height):
        for i in range(on_b.width):
            a = pa[i, j]
            if a:
                r, g, b = pb[i, j]
                po[i, j] = (min(255, r * 255 // a), min(255, g * 255 // a), min(255, b * 255 // a))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    k = out.width / side
    box = (round((x - nx) * k), round((y - ny) * k), round((x - nx + w) * k), round((y - ny + h) * k))
    out.crop(box).save(out_png, optimize=True)


if __name__ == "__main__":
    rasterize(sys.argv[1], sys.argv[2], int(sys.argv[3]))
