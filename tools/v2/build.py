"""Baut v2/index.html (NCN „Leuchtfeuer & Seekarte“) aus tools/v2/index.tpl.html: Seekarte, Register, Gastgeber-Rad.

Aufruf (aus dem NCN-Ordner): python3 tools/v2/build.py v2 tools/v2/index.tpl.html
"""
import math, html, sys
from pathlib import Path
from PIL import Image

V = Path(sys.argv[1])

MAIL = "mailto:constantin.keitz@bcpro.de,julien-finley.kutzner@bcpro.de?subject=NCN"
ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# Stadt, Breite, Länge, Verein (offiziell), Logo, Höhe (angeglichen), Website, Label-Lage
C = [
  ("Kiel",        54.3233, 10.1228, "UNICONSULT Kiel e. V.", "uniconsult", 43, "https://uniconsult-kiel.de/", "r"),
  ("Greifswald",  54.0931, 13.3879, "Capufaktur e. V.", "capufaktur", 64, "https://www.capufaktur.de/", "b"),
  ("Hamburg",     53.5511,  9.9937, "Hanseatic Consulting – Studentische Unternehmensberatung e. V.", "hanseatic", 43, "https://hanseaticconsulting.de/", "l"),
  ("Lüneburg",    53.2464, 10.4115, "Contact &amp; Cooperation Lüneburg e. V.", "cc", 64, "https://www.contact-cooperation.de/", "r"),
  ("Bremen",      53.0793,  8.8017, "Active e. V.", "active", 44, "https://www.active-bremen.de/", "l"),
  ("Berlin",      52.5200, 13.4050, "BCPro e. V.", "bcpro", 41, "https://bcpro.de/", "b"),
  ("Hannover",    52.3759,  9.7320, "Janus Consultants e. V.", "janus", 39, "https://janus-consultants.de/", "l"),
  ("Osnabrück",   52.2799,  8.0472, "StudenTop e. V.", "studentop", 39, "https://studentop.de/", "b"),
  ("Braunschweig",52.2689, 10.5268, "Consult One Unternehmensberatung e. V.", "consultone", 64, "https://consult-one.de/", "r"),
  ("Göttingen",   51.5413,  9.9158, "Consulting Team e. V.", "consulting-team", 33, "https://www.consulting-team.eu/", "r"),
]
# Register alphabetisch nach Verein
REG = sorted(C, key=lambda c: html.unescape(c[3]).lower())

def dms(v, pos):
    d = int(v); m = round((v - d) * 60)
    if m == 60: d += 1; m = 0
    return f"{d}°{m:02d}′{pos}"

def slug(s): return s.lower().replace("ü", "ue").replace("ö", "oe").replace("ä", "ae")

# ------------------------------------------------ Seekarte
lon0, lon1, lat0, lat1 = 7.0, 14.4, 51.1, 55.0
k = math.cos(math.radians(53)); s = 760 / (lat1 - lat0)
W = (lon1 - lon0) * k * s
def P(lat, lon): return ((lon - lon0) * k * s, (lat1 - lat) * s)
pts = {c[0]: P(c[1], c[2]) for c in C}
g = []
for lat in (52, 53, 54):
    y = P(lat, lon0)[1]; g.append(f'<line class="grat" x1="0" y1="{y:.1f}" x2="{W:.1f}" y2="{y:.1f}"/><text class="grat-label" x="6" y="{y-6:.1f}">{lat}°N</text>')
for lon in range(8, 15):
    x = P(lat1, lon)[0]; g.append(f'<line class="grat" x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="760"/><text class="grat-label" x="{x+6:.1f}" y="752">{lon}°E</text>')
links = []
names = [c[0] for c in C]
for i in range(len(C)):
    for j in range(i + 1, len(C)):
        a, b = pts[names[i]], pts[names[j]]
        links.append(f'<line class="link" data-a="{slug(names[i])}" data-b="{slug(names[j])}" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
cities = []
for n, la, lo, je, logo, h, url, pos in C:
    x, y = pts[n]
    if pos == "r": tx, ty, anc = x + 16, y + 5, "start"
    elif pos == "l": tx, ty, anc = x - 16, y + 5, "end"
    else: tx, ty, anc = x, y + 30, "middle"
    sub_y = ty + 17
    cities.append(
        f'<g class="city" data-city="{slug(n)}" tabindex="0" role="img" aria-label="{n}, {dms(la,"N")} {dms(lo,"E")}: {html.unescape(je)}">'
        f'<circle class="halo" cx="{x:.1f}" cy="{y:.1f}" r="22"/><circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="5"/>'
        f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anc}">{n}</text>'
        f'<text class="sub" x="{tx:.1f}" y="{sub_y:.1f}" text-anchor="{anc}">{dms(la,"N")} {dms(lo,"E")}</text></g>')
nx, ny = P(54.4, 7.45); ox, oy = P(54.7, 11.9)
CHART = f'''<svg viewBox="-10 -10 {W+20:.0f} 790" aria-labelledby="chart-t">
          <title id="chart-t">Seekarte Norddeutschlands mit den zehn Städten der NCN-Mitgliedsvereine, jede mit jeder verbunden</title>
          {''.join(g)}
          <text class="sea" x="{nx:.1f}" y="{ny:.1f}">NORDSEE</text><text class="sea" x="{ox:.1f}" y="{oy:.1f}">OSTSEE</text>
          {''.join(links)}
          {''.join(cities)}
        </svg>'''

# ------------------------------------------------ Register
rows = []
for i, (n, la, lo, je, logo, h, url, pos) in enumerate(REG, 1):
    src = f"assets/logos/{logo}.webp"; w0, h0 = Image.open(V / src).size
    small = V / f"assets/logos/{logo}-360.webp"
    srcset = f' srcset="assets/logos/{logo}-360.webp 360w, {src} {w0}w" sizes="150px"' if small.exists() else ""
    rows.append(f'''          <li><a href="{url}" target="_blank" rel="noopener" data-city="{slug(n)}">
            <span class="name">{je}</span><span class="city">{n}</span>
            <span class="logo"><img src="{src}"{srcset} style="--h:{h}" width="{round(h*w0/h0)}" height="{h}" alt="Logo {html.unescape(je)}" loading="lazy"></span></a></li>''')
REGISTER = "\n".join(rows)

# ------------------------------------------------ Gastgeber-Rad
ORDER = ["Kiel", "Greifswald", "Berlin", "Braunschweig", "Göttingen", "Hannover", "Osnabrück", "Bremen", "Hamburg", "Lüneburg"]
R, cx, cy = 230, 300, 300
nodes, spokes = [], []
for i, n in enumerate(ORDER):
    a = -math.pi / 2 + i * 2 * math.pi / len(ORDER)
    x, y = cx + R * math.cos(a), cy + R * math.sin(a)
    tx, ty = cx + (R + 34) * math.cos(a), cy + (R + 34) * math.sin(a) + 5
    anc = "middle" if abs(math.cos(a)) < .3 else ("start" if math.cos(a) > 0 else "end")
    spokes.append(f'<line class="spoke" x1="{cx + 92*math.cos(a):.1f}" y1="{cy + 92*math.sin(a):.1f}" x2="{x:.1f}" y2="{y:.1f}"/>')
    nodes.append(f'<g class="node" data-host="{n}"><circle cx="{x:.1f}" cy="{y:.1f}" r="7"/><text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anc}">{n}</text></g>')
WHEEL = f'''<svg viewBox="0 0 600 600" aria-hidden="true">
            <circle class="ring" cx="300" cy="300" r="{R}"/><circle class="ring ring--dash" cx="300" cy="300" r="92"/>
            {''.join(spokes)}{''.join(nodes)}
          </svg>'''

COORDS = "".join(f'<span><b>{n}</b>{dms(la,"N")} {dms(lo,"E")}</span>' for n, la, lo, *_ in C)

page = Path(sys.argv[2]).read_text()
for k_, v in {"{{CHART}}": CHART, "{{REGISTER}}": REGISTER, "{{WHEEL}}": WHEEL, "{{COORDS}}": COORDS, "{{MAIL}}": MAIL, "{{ARROW}}": ARROW}.items():
    page = page.replace(k_, v)
(V / "index.html").write_text(page)
print("ok", len(page))
