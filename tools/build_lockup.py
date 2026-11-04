"""Baut das NCN-Logo mit Schriftzug „North Consulting Network“ als SVG.

Der Text wird mit Open Sans (tools/fonts, OFL-Lizenz) in Vektorpfade umgewandelt,
das fertige SVG braucht also keine Schrift. Proportionen wie im Original-Logo:
Kreisdurchmesser D, Textbreite 2,675·D, Abstand Kreis→Versalhöhe 0,179·D.

Aufruf: python3 tools/build_lockup.py [gewicht]   (aus dem NCN-Ordner, Standard 360)
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

import build_logo as L

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets" / "logo"
FONT = ROOT / "fonts" / "OpenSans[wdth,wght].ttf"
TEXT = "North Consulting Network"
TEXT_COLOR = "#000000"
TRACKING = 41             # Buchstabenabstand in Font-Einheiten (≈ 0,02 em, wie Original)
WEIGHT = 360              # zwischen Light (300) und Regular (400), wie Original

D = 674.0                 # Kreisdurchmesser im Icon-Koordinatenraum (2·r)
TEXT_W = 2.675 * D        # Breite des Schriftzugs
GAP = 0.179 * D           # Abstand Kreisunterkante → Oberkante Versalien
PAD = 0.06 * D            # Rand rundum


def kerning(font):
    """Paar-Kerning aus GPOS (Format 1 und 2) als dict[(l, r)] -> Wert."""
    kern = {}
    gpos = font["GPOS"].table
    for lookup in gpos.LookupList.Lookup:
        subs = lookup.SubTable
        if lookup.LookupType == 9:
            subs = [s.ExtSubTable for s in subs]
        for st in subs:
            if getattr(st, "LookupType", lookup.LookupType) not in (2, 9) or not hasattr(st, "Format"):
                continue
            if not hasattr(st, "Coverage"):
                continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for i, first in enumerate(cov):
                    for pvr in st.PairSet[i].PairValueRecord:
                        v = getattr(pvr.Value1, "XAdvance", 0) or 0
                        kern.setdefault((first, pvr.SecondGlyph), v)
            elif st.Format == 2:
                c1 = st.ClassDef1.classDefs
                c2 = st.ClassDef2.classDefs
                for first in cov:
                    rec = st.Class1Record[c1.get(first, 0)]
                    for second, k2 in c2.items():
                        v = getattr(rec.Class2Record[k2].Value1, "XAdvance", 0) or 0
                        if v:
                            kern.setdefault((first, second), v)
    return kern


def text_path(weight):
    vf = TTFont(FONT)
    font = instancer.instantiateVariableFont(vf, {"wght": weight, "wdth": 100})
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    kern = kerning(font)
    upm = font["head"].unitsPerEm
    cap = font["OS/2"].sCapHeight

    names = [cmap[ord(c)] for c in TEXT]
    parts, x = [], 0
    xmin, xmax = None, None
    for i, g in enumerate(names):
        pen = SVGPathPen(gs)
        gs[g].draw(pen)
        bp = BoundsPen(gs)
        gs[g].draw(bp)
        d = pen.getCommands()
        if d:
            parts.append((x, d))
        if bp.bounds:
            gx0, gx1 = x + bp.bounds[0], x + bp.bounds[2]
            xmin = gx0 if xmin is None else min(xmin, gx0)
            xmax = gx1 if xmax is None else max(xmax, gx1)
        x += hmtx[g][0]
        if i + 1 < len(names):
            x += kern.get((g, names[i + 1]), 0) + TRACKING
    return parts, xmin, xmax, cap, upm


def lockup_svg(weight=WEIGHT, icon_color=L.GREEN, text_color=TEXT_COLOR):
    cx, cy, r = L.CIRCLE
    parts, xmin, xmax, cap, upm = text_path(weight)
    s = TEXT_W / (xmax - xmin)                     # Font-Einheiten → Icon-Einheiten
    baseline = cy + r + GAP + cap * s
    tx = cx - TEXT_W / 2 - xmin * s
    descent = 0.25 * upm * s                       # Platz für das g
    left, right = cx - TEXT_W / 2 - PAD, cx + TEXT_W / 2 + PAD
    top, bottom = cy - r - PAD, baseline + descent + PAD
    w, h = right - left, bottom - top

    glyphs = "\n    ".join(
        f'<path transform="translate({x:.0f} 0)" d="{d}"/>' for x, d in parts
    )
    polys = "\n      ".join(f'<polygon points="{L.fmt(p)}" fill="#000"/>' for p in L.SHAPES)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left:.1f} {top:.1f} {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="NCN – North Consulting Network">
  <defs>
    <mask id="ncn-cut" maskUnits="userSpaceOnUse" x="0" y="0" width="800" height="800">
      <rect width="800" height="800" fill="#fff"/>
      {polys}
    </mask>
  </defs>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{icon_color}" mask="url(#ncn-cut)"/>
  <g fill="{text_color}" transform="translate({tx:.2f} {baseline:.2f}) scale({s:.6f} {-s:.6f})">
    {glyphs}
  </g>
</svg>
'''


if __name__ == "__main__":
    weight = float(sys.argv[1]) if len(sys.argv) > 1 else WEIGHT
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ncn-logo-schriftzug.svg").write_text(lockup_svg(weight))
    (OUT / "ncn-logo-schriftzug-weiss.svg").write_text(lockup_svg(weight, "#FFFFFF", "#FFFFFF"))
    print("fertig, Gewicht", weight)
