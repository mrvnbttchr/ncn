"""Baut das NCN-Leuchtturm-Logo als SVG und hochaufgelöste PNGs.

Geometrie im 800x800-Raster, symmetrisch um x=400, abgemessen am Original-Icon.
Aufruf: python3 tools/build_logo.py   (aus dem NCN-Ordner)
"""
from pathlib import Path
from PIL import Image, ImageDraw

GREEN = "#1EA273"
OUT = Path(__file__).resolve().parent.parent / "assets" / "logo"
AX = 400  # Symmetrieachse

CIRCLE = (400, 402, 337)  # cx, cy, r

def mirror(pts):
    return [(2 * AX - x, y) for x, y in pts]

# Lichtkegel links (transparent): zwei Geraden, die sich in der Laterne treffen
def beam_left():
    a = lambda x: 212 + 0.23 * (x - 186.5)     # Oberkante
    b = lambda x: 268 - 0.172 * (x - 325.5)    # Unterkante
    apex_x = 385.0
    return [(-50, a(-50)), (apex_x, a(apex_x)), (-50, b(-50))]

# Leuchtturm (transparent), Hälften als (y, halbe Breite) von oben nach unten
def tower():
    left = [
        (151, 21),     # Dach oben
        (188, 44.5),   # Dachschräge
        (199, 44.5),
        (199, 58.5),   # Galerie
        (209, 58.5),
        (209, 44.5),   # Hals / Laterne
        (311, 44.5),
        (311, 61.5),   # Turmschaft (verjüngt)
        (581.5, 85),
        (581.5, 195),  # Bodenplatte
        (593.5, 195),
    ]
    pts_left = [(AX - w, y) for y, w in left]
    pts_right = [(AX + w, y) for y, w in reversed(left)]
    return pts_left + pts_right

SHAPES = [beam_left(), mirror(beam_left()), tower()]

def fmt(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

def _circle_hits(slope, x0, y0):
    """Schnittpunkte der Geraden y = y0 + slope·(x − x0) mit dem Kreis (links, rechts)."""
    cx, cy, r = CIRCLE
    # y = m·x + c
    m, c = slope, y0 - slope * x0
    A = 1 + m * m
    B = 2 * (m * (c - cy) - cx)
    C = cx * cx + (c - cy) ** 2 - r * r
    D = (B * B - 4 * A * C) ** 0.5
    xs = sorted([(-B - D) / (2 * A), (-B + D) / (2 * A)])
    return [(x, m * x + c) for x in xs]


def icon_path():
    """Logo als reiner Pfad ohne Maske (zwei grüne Flächen: über und unter den Lichtkegeln).

    Masken werden von mobilen Browsern (v. a. Safari) teils niedrig aufgelöst gerastert
    und wirken dann unscharf – ein einfacher Pfad bleibt in jeder Größe gestochen scharf.
    """
    cx, cy, r = CIRCLE
    wall = AX - 44.5                                   # Außenwand der Laterne (links)
    a_l = _circle_hits(0.23, 186.5, 212)[0]            # Oberkante Lichtkegel trifft Kreis
    b_l = _circle_hits(-0.172, 325.5, 268)[0]          # Unterkante Lichtkegel trifft Kreis
    a_y = 212 + 0.23 * (wall - 186.5)                  # Oberkante trifft Laterne
    b_y = 268 - 0.172 * (wall - 325.5)                 # Unterkante trifft Laterne
    m = lambda p: (2 * AX - p[0], p[1])
    t = tower()
    n = len(t) // 2
    left = t[:n]                                       # linke Turmseite, oben -> unten
    right = t[n:]                                      # rechte Turmseite, unten -> oben
    neck = [p for p in left if p[0] == wall and 209 <= p[1] <= 311]
    i_top = left.index(neck[0])                        # (wall, 209)
    i_bot = left.index(neck[1])                        # (wall, 311)
    f = lambda p: f"{p[0]:.2f},{p[1]:.2f}"

    # Obere Fläche: Bogen über den Kopf, rechter Kegel rein, Turmspitze, linker Kegel raus
    upper = [f"M{f(a_l)}", f"A{r},{r} 0 0 1 {f(m(a_l))}", f"L{f((2*AX-wall, a_y))}"]
    upper += [f"L{f(m(p))}" for p in reversed(left[:i_top + 1])]
    upper += [f"L{f(p)}" for p in left[:i_top + 1]]
    upper += [f"L{f((wall, a_y))}", "Z"]

    # Untere Fläche: Bogen unten herum, linker Kegel rein, Turmschaft + Sockel, rechter Kegel raus
    lower = [f"M{f(m(b_l))}", f"A{r},{r} 0 1 1 {f(b_l)}", f"L{f((wall, b_y))}"]
    lower += [f"L{f(p)}" for p in left[i_bot:]]
    lower += [f"L{f(p)}" for p in right[:n - i_bot]]
    lower += [f"L{f((2*AX-wall, b_y))}", "Z"]
    return " ".join(upper) + " " + " ".join(lower)


def svg(color=GREEN, size=800):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="55 60 690 690" width="{size}" height="{size}" role="img" aria-label="NCN – Northern Consulting Network">
  <path fill="{color}" d="{icon_path()}"/>
</svg>
'''

def png(px, color=GREEN, bg=None):
    """Rendert mit 4x-Supersampling; Ausschnitt wie die SVG-viewBox."""
    ss = 4
    S = px * ss
    scale = S / 690
    tx = lambda p: ((p[0] - 55) * scale, (p[1] - 60) * scale)
    shape = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(shape)
    cx, cy, r = CIRCLE
    (x0, y0), (x1, y1) = tx((cx - r, cy - r)), tx((cx + r, cy + r))
    d.ellipse([x0, y0, x1, y1], fill=255)
    for p in SHAPES:
        d.polygon([tx(q) for q in p], fill=0)
    shape = shape.resize((px, px), Image.LANCZOS)
    img = Image.new("RGBA", (px, px), bg or (0, 0, 0, 0))
    fill = Image.new("RGBA", (px, px), color)
    img.paste(fill, (0, 0), shape)
    return img

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ncn-logo.svg").write_text(svg())
    (OUT / "ncn-logo-weiss.svg").write_text(svg("#FFFFFF"))
    for px in (512, 1024, 2048, 4096):
        png(px).save(OUT / f"ncn-logo-{px}.png", optimize=True)
    png(4096, "#FFFFFF").save(OUT / "ncn-logo-weiss-4096.png", optimize=True)
    png(1024, bg=(255, 255, 255, 255)).save(OUT / "ncn-logo-1024-weisser-hintergrund.png", optimize=True)
    print("fertig:", sorted(p.name for p in OUT.iterdir()))
