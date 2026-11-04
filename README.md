# NCN – North Consulting Network

Statische Website des North Consulting Network (Netzwerk studentischer Unternehmensberatungen in Norddeutschland).

- `index.html` – One-Pager (Über uns, Mitglieder, Vorteile, Organisation, Treffen, Events, Kontakt)
- `impressum.html`, `datenschutz.html` – Rechtstexte (Platzhalter `[...]` vor Go-live ausfüllen)
- `styles.css`, `main.js`, `assets/`

Lokal ansehen: `python3 -m http.server 4176` im Ordner, dann http://localhost:4176
Hosting: GitHub Pages (Branch `main`, Root).

## Logo
Alle Logo-Dateien liegen in `assets/logo/` (SVG + PNG bis 4096 px, grün und weiß, mit und ohne Schriftzug).
Neu erzeugen: `python3 tools/build_logo.py`, `cd tools && python3 build_lockup.py`,
PNGs des Schriftzug-Logos: `python3 tools/rasterize.py <svg> <png> <breite>` (macOS).
Schrift des Schriftzugs: Open Sans (SIL Open Font License, `tools/fonts/OFL.txt`), Gewicht 360, Laufweite +0,02 em.
