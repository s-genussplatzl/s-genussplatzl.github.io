"""Schematische Karte der Bike-&-Spa-Runde (12-Thermen-Tour) als SVG-Teil.

Eigene Zeichnung aus Ortskoordinaten (OpenStreetMap/Nominatim), keine Kopie der
offiziellen Karte. Ergebnis: bikespa.svg.part (wird von build.py eingesetzt).
"""
import json
import math
from pathlib import Path

LAT_N, LAT_S = 47.20, 46.38
LON_W, LON_E = 15.55, 16.55
W = 800
K = W / ((LON_E - LON_W) * math.cos(math.radians(46.8)))
H = round((LAT_N - LAT_S) * K)

# Etappenorte in Reihenfolge der Runde; (lat, lon, Beschriftung: dx, dy, anchor)
STAGES = [
    ("Bad Waltersdorf", 47.1685, 16.0089, 16, 6, "start"),
    ("Loipersdorf", 47.0129, 16.1008, 16, 6, "start"),
    ("Kapfenstein", 46.8851, 15.9740, 16, 6, "start"),
    ("Bad Radkersburg", 46.6880, 15.9880, 14, 30, "start"),
    ("Moravske Toplice", 46.6858, 16.2217, 0, -18, "middle"),
    ("Lendava", 46.5640, 16.4526, 0, 32, "middle"),
    ("Banovci", 46.5720, 16.1550, 0, -18, "middle"),
    ("Mala Nedelja", 46.5235, 16.0545, 14, 28, "start"),
    ("Ptuj", 46.4198, 15.8717, 0, 32, "middle"),
    ("Maribor", 46.5576, 15.6456, 0, 32, "middle"),
    ("Mureck", 46.7076, 15.7695, -16, 6, "end"),
    ("Bad Gleichenberg", 46.8745, 15.9050, -16, 6, "end"),
    ("Riegersburg", 47.0008, 15.9360, -16, 6, "end"),
]
HOME = (46.7324, 15.9061)  # Unterpurkla 28: die Etappe Mureck–Bad Gleichenberg führt am R45 hier vorbei (laut Betreiber)


def xy(lat, lon):
    x = (lon - LON_W) * math.cos(math.radians(46.8)) * K
    y = (LAT_N - lat) * K
    return round(x, 1), round(y, 1)


pts = [xy(s[1], s[2]) for s in STAGES]
hx, hy = xy(*HOME)
route = []
for i, p in enumerate(pts):
    route.append(p)
    if STAGES[i][0] == "Mureck":
        route.append((hx, hy))
d = "M" + " L".join(f"{x} {y}" for x, y in route) + " Z"

names = ", ".join(s[0] for s in STAGES)
out = [
    f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="bs-title">',
    f'<title id="bs-title">Schematische Karte der Bike-&amp;-Spa-Runde mit den Etappenorten {names}; '
    'die Etappe von Mureck nach Bad Gleichenberg führt am Radweg R45 am Genussplatzl vorbei</title>',
    '<text class="bs-country" x="{}" y="{}">Österreich</text>'.format(*xy(47.13, 15.60)),
    '<text class="bs-country" x="{}" y="{}">Ungarn</text>'.format(*xy(46.80, 16.40)),
    '<text class="bs-country" x="{}" y="{}">Slowenien</text>'.format(*xy(46.47, 16.18)),
    f'<path class="bs-route" d="{d}"/>',
]
BORDERS = json.loads((Path(__file__).resolve().parent / 'data' / 'borders.json').read_text(encoding='utf-8'))
def _bpath(w, cls):
    return f'<path class="{cls}" d="M' + ' L'.join('{} {}'.format(*xy(lat, lon)) for lon, lat in w) + '"/>'
LANDS = json.loads((Path(__file__).resolve().parent / 'data' / 'countries.json').read_text(encoding='utf-8'))
def _land(k):
    d = ''.join('M' + ' L'.join('{} {}'.format(*xy(lat, lon)) for lon, lat in ring) + 'Z' for poly in LANDS[k] for ring in poly)
    return f'<path class="bs-land bs-land--{k}" d="{d}" fill-rule="evenodd"/>'
out[2:2] = [_land('si'), _land('hu')]
out[7:7] = [_bpath(w, 'bs-border') for w in BORDERS['national']]
out += [
]
for (name, lat, lon, dx, dy, anchor), (x, y) in zip(STAGES, pts):
    out.append(f'<circle class="bs-stop" cx="{x}" cy="{y}" r="7"/>')
    out.append(f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{name}</text>')
out.append(f'<circle class="bs-home-ring" cx="{hx}" cy="{hy}" r="20"/>')
out.append(f'<circle class="bs-home" cx="{hx}" cy="{hy}" r="10"/>')
out.append(f'<text class="bs-home-label" x="{hx - 30}" y="{hy - 22}" text-anchor="end">s’Genussplatz’l</text>')
out.append("</svg>")

Path(__file__).resolve().parent.parent.joinpath("bikespa.svg.part").write_text("\n".join(out), encoding="utf-8")
print(W, H, "home", hx, hy)
