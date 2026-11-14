"""Baut die ganze Website aus layout.html + pages/ + Routendaten.

  python tools/site.py                 # alles bauen
  python tools/site.py --import <dir>  # Routen (BRouter-GeoJSON) und Mur neu einlesen

Erzeugt: index.html, radrouten/*.html, e-bike-laden.html, bike-and-spa.html,
gpx/*.gpx, sitemap.xml, robots.txt (Bike-&-Spa-Karte: tools/bikespa_map.py).
Routen: BRouter (Profil trekking) auf OpenStreetMap-Daten, © OpenStreetMap-Mitwirkende.
"""
import json
import math
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "rad.json"
# Übergang: solange s-genussplatzl.at noch nicht auf GitHub Pages zeigt, gilt die github.io-Adresse.
# Nach der DNS-Umstellung (CNAME-Datei + A-Records) hier wieder auf "https://s-genussplatzl.at/" stellen und neu bauen.
SITE = "https://s-genussplatzl.github.io/"
HOME = (15.9061, 46.7324)
KEYS = ("west", "nord", "nordost", "ost", "sued")
# Besucherstatistik (Umami, ohne Cookies). Website-ID aus dem Umami-Konto eintragen; leer = kein Skript.
UMAMI_SRC = "https://cloud.umami.is/script.js"
UMAMI_ID = "0a0fc72a-b9eb-4cef-9d81-b69e85b1510c"


def hav(a, b):
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    dp, dl = la2 - la1, math.radians(b[0] - a[0])
    return 2 * 6371 * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dl / 2) ** 2))


# ---------------------------------------------------------------- import
if len(sys.argv) > 2 and sys.argv[1] == "--import":
    src = Path(sys.argv[2])
    routes = {}
    for key in KEYS:
        f = json.loads((src / f"{key}.geojson").read_text(encoding="utf-8"))["features"][0]
        p = f["properties"]
        routes[key] = {
            "km": round(int(p["track-length"]) / 1000, 1),
            "up": int(p.get("filtered ascend", 0)),
            "coords": [[round(c[0], 5), round(c[1], 5), round(c[2], 1)] for c in f["geometry"]["coordinates"]],
        }
    river = []
    for name in ("mur2.json", "mur3.json"):
        for e in json.loads((src / name).read_text(encoding="utf-8"))["elements"]:
            if e.get("tags", {}).get("name") in ("Mur", "Mur / Mura"):
                river.append([[round(p["lon"], 5), round(p["lat"], 5)] for p in e["geometry"]])
    for way in json.loads((src.parent / "mur.json").read_text(encoding="utf-8")):
        river.append([[round(x, 5), round(y, 5)] for x, y in way])
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps({"routes": routes, "river": river}), encoding="utf-8")
    print("importiert", {k: (v["km"], v["up"]) for k, v in routes.items()})

D = json.loads(DATA.read_text(encoding="utf-8"))
for r in D["routes"].values():  # kumulierte Distanz
    cum = [0.0]
    for i in range(1, len(r["coords"])):
        cum.append(cum[-1] + hav(r["coords"][i - 1], r["coords"][i]))
    r["cum"] = cum


def km_at(key, lon, lat):
    r = D["routes"][key]
    i = min(range(len(r["coords"])), key=lambda j: hav(r["coords"][j], (lon, lat)))
    return r["cum"][i]


def de(x, nd=0):
    s = f"{x:.{nd}f}"
    return s.replace(".", ",")


# ---------------------------------------------------------------- content
GENUSS = ("s’Genussplatz’l", HOME[0], HOME[1],
          "Rast unterm Nussbaum mit regionalen Weinen, Schatten, WC, kostenloser E-Bike-Ladestation und einem klimatisierten Raum für heiße Tage.")

ROUTES = {
    "west": dict(
        slug="murradweg-ab-spielfeld", komoot="3392769165", name="Murradweg ab Spielfeld", short="Murradweg ab Spielfeld",
        start=("Spielfeld", 15.6360, 46.7085), sky="Westen",
        h1="Von Spielfeld die Mur entlang.",
        lead="Der Klassiker an der Mur: flach am Fluss entlang, über Mureck bis zu uns nach Unterpurkla.",
        ways="Murradweg R2, zuletzt Gleichenberger Radweg R45",
        title="Murradweg ab Spielfeld nach Unterpurkla, Radroute mit GPX",
        desc="Radroute am Murradweg R2 von Spielfeld über Mureck zum s’Genussplatz’l in Unterpurkla: ca. 27 km, flach, mit Karte, Höhenprofil und GPX-Download.",
        index_text="Der Klassiker an der Mur, aus dem Westen über Mureck mit seiner Schiffsmühle, 1997 nach historischem Vorbild wieder aufs Wasser gesetzt.",
        stops=[("Spielfeld", 15.6360, 46.7085, "Grenzort an der Mur, gleich bei der Südsteirischen Weinstraße. Hier beginnt die Tour flussabwärts."),
               ("Mureck", 15.7695, 46.7076, "Die Schiffsmühle wurde 1997 nach historischem Vorbild wieder auf die Mur gesetzt, eine der letzten schwimmenden Schiffsmühlen Mitteleuropas."),
               ("Gosdorf", 15.80911, 46.72221, "Durch die Auen der Mur, ringsum der UNESCO-Biosphärenpark Mur-Drau-Donau."),
               GENUSS]),
    "nord": dict(
        slug="r45-ab-bad-gleichenberg", komoot="3392769397", name="R45 ab Bad Gleichenberg", short="R45 ab Bad Gleichenberg",
        start=("Bad Gleichenberg", 15.9050, 46.8745), sky="Norden",
        h1="Von Bad Gleichenberg durchs Vulkanland.",
        lead="Am Gleichenberger Radweg R45 vom Kurort sanft bergab bis zur Mur, durch Dörfer, Felder und Hügel des Vulkanlands.",
        ways="Gleichenberger Radweg R45",
        title="R45 ab Bad Gleichenberg nach Unterpurkla, Radroute mit GPX",
        desc="Gleichenberger Radweg R45 von Bad Gleichenberg über Trautmannsdorf und Radochen zum s’Genussplatz’l in Unterpurkla: ca. 20 km, leicht fallend, mit GPX.",
        index_text="Aus dem Norden vom Kurort mitten im Vulkanland, der Gleichenberger Radweg führt direkt bei uns vorbei.",
        stops=[("Bad Gleichenberg", 15.9050, 46.8745, "Kurort mitten im Vulkanland und Etappenort der Bike-&-Spa-Runde, deren Etappe ab Mureck auf dem R45 bei uns vorbeiführt."),
               ("Trautmannsdorf", 15.88906, 46.85782, "Der R45 verlässt den Kurort Richtung Süden, durch das sanfte Hügelland."),
               ("Radochen", 15.88857, 46.76614, "Die letzten Kilometer durch Felder und Dörfer, bis die Mur in Sichtweite ist."),
               GENUSS]),
    "nordost": dict(
        slug="ab-st-anna-ueber-kloech", komoot="3392769506", name="Ab St. Anna am Aigen über Klöch", short="Ab St. Anna über Klöch",
        start=("St. Anna am Aigen", 15.9610, 46.8355), sky="Nordosten",
        h1="Von St. Anna durch die Weinberge.",
        lead="Die hügelige Route durch das Weinland: von St. Anna am Aigen über Klöch, die Heimat des Traminers, hinunter zu uns an die Mur.",
        ways="Radwege und Nebenstraßen durch das Klöcher Weinland",
        title="Radtour St. Anna am Aigen, Klöch, Unterpurkla mit GPX",
        desc="Radtour von St. Anna am Aigen über Klöch zum s’Genussplatz’l in Unterpurkla: ca. 19 km, hügelig, rund 150 Höhenmeter, mit Karte und GPX-Download.",
        index_text="Aus dem Nordosten durch die Weinberge des Vulkanlands, über Klöch, seit 1444 urkundlich Weinland und Heimat des Traminers. Leicht hügelig, rund 150 Höhenmeter.",
        stops=[("St. Anna am Aigen", 15.9610, 46.8355, "Weinort im Vulkanland. Von hier geht es durch die Weingärten Richtung Süden."),
               ("Klöch", 15.9656, 46.7642, "Seit 1444 urkundlich Weinland. Vulkanböden geben dem Traminer seinen Duft nach Rosen, dazu Vinothek, Weinbaumuseum und Burgruine."),
               GENUSS]),
    "ost": dict(
        slug="ab-bad-radkersburg", komoot="3392769623", name="Ab Bad Radkersburg", short="Ab Bad Radkersburg",
        start=("Bad Radkersburg", 15.9867, 46.6875), sky="Osten",
        h1="Von Bad Radkersburg die Mur hinauf.",
        lead="Kurz und flach: von der Altstadt an der Mur über Dietzen zu uns nach Unterpurkla, ideal als Ausflug von der Therme.",
        ways="Murradweg R2, zuletzt Gleichenberger Radweg R45",
        title="Radroute Bad Radkersburg nach Unterpurkla mit GPX",
        desc="Radroute von Bad Radkersburg an der Mur zum s’Genussplatz’l in Unterpurkla: ca. 12 km, flach, mit Karte, Höhenprofil und GPX-Download.",
        index_text="Aus dem Osten von Altstadt und Parktherme an der Mur, dem Startpunkt des Thermenradwegs R12.",
        stops=[("Bad Radkersburg", 15.9867, 46.6875, "Altstadt und Parktherme an der Mur, Startpunkt des Thermenradwegs R12 und Etappenort der Bike-&-Spa-Runde."),
               ("Dietzen", 15.94248, 46.71051, "Flach durch die Felder am Rand der Murauen."),
               GENUSS]),
    "sued": dict(
        slug="ab-apace-ueber-die-steirerbruecke", komoot="3392769770", name="Ab Apače in Slowenien", short="Ab Apače über die Steirerbrücke",
        start=("Apače", 15.9100, 46.6965), sky="Süden",
        h1="Von Apače über die Steirerbrücke.",
        lead="Die kürzeste Route kommt aus Slowenien: über die Hängebrücke und durch die Auen der Mur, in einer halben Stunde bei uns.",
        ways="Radwege beidseits der Mur, Steirerbrücke, zuletzt Gleichenberger Radweg R45",
        title="Radroute Apače, Steirerbrücke, Unterpurkla mit GPX",
        desc="Radroute von Apače in Slowenien über die Steirerbrücke zum s’Genussplatz’l in Unterpurkla: ca. 7 km, flach, mit Karte und GPX-Download.",
        index_text="Aus dem Süden über die Steirerbrücke, die seit 2006 auf 82,5 Metern über die Mur schwingt, mitten durch die Auen des Biosphärenparks Mur-Drau-Donau.",
        stops=[("Apače", 15.9100, 46.6965, "Dorf am slowenischen Ufer der Mur, Ausgangspunkt für die Brücke nach Österreich."),
               ("Steirerbrücke", 15.8930, 46.7140, "Seit 2006 schwingt die Hängebrücke auf 82,5 Metern über die Mur, mitten im UNESCO-Biosphärenpark Mur-Drau-Donau."),
               GENUSS]),
}
WAYPOINT_LABELS = {  # Kartenbeschriftung: dx, dy, anchor
    "Spielfeld": (0, -20, "start"), "Bad Gleichenberg": (-16, -6, "end"), "St. Anna am Aigen": (16, 6, "start"),
    "Bad Radkersburg": (-4, 34, "middle"), "Apače": (-16, 30, "end"), "Mureck": (0, 34, "middle"),
    "Steirerbrücke": (-16, 6, "end"), "Klöch": (16, 6, "start"), "Gosdorf": (0, 34, "middle"),
    "Trautmannsdorf": (16, 6, "start"), "Radochen": (16, 6, "start"), "Dietzen": (0, -18, "middle"),
}


# ---------------------------------------------------------------- maps
class Proj:
    def __init__(self, lon_w, lon_e, lat_n, lat_s, w=1000):
        self.lon_w, self.lat_n = lon_w, lat_n
        self.cos = math.cos(math.radians((lat_n + lat_s) / 2))
        self.k = w / ((lon_e - lon_w) * self.cos)
        self.w, self.h = w, round((lat_n - lat_s) * self.k)

    def xy(self, lon, lat):
        return round((lon - self.lon_w) * self.cos * self.k, 1), round((self.lat_n - lat) * self.k, 1)

    def path(self, coords):
        return "M" + " L".join("{} {}".format(*self.xy(c[0], c[1])) for c in coords)


def label(P, name, lon, lat, cls=""):
    x, y = P.xy(lon, lat)
    dx, dy, anchor = WAYPOINT_LABELS.get(name, (16, 6, "start"))
    return f'<text{cls} x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{escape(name)}</text>'


def home_marker(P):
    hx, hy = P.xy(*HOME)
    return (f'<circle class="home-ring" cx="{hx}" cy="{hy}" r="24"/><circle class="place--home" cx="{hx}" cy="{hy}" r="12"/>'
            f'<text class="label-home" x="{hx + 34}" y="{hy - 16}">s’Genussplatz’l</text>')


def overview_map():
    P = Proj(15.60, 16.09, 46.89, 46.66)
    o = [f'<svg viewBox="0 0 {P.w} {P.h}" role="img" aria-labelledby="ride-title">',
         '<title id="ride-title">Karte: fünf Radrouten zum Genussplatzl, ab Spielfeld über Mureck, ab Bad Gleichenberg, '
         'ab St. Anna am Aigen über Klöch, ab Bad Radkersburg und ab Apače über die Steirerbrücke</title>']
    o += [f'<path class="river" d="{P.path(w)}"/>' for w in D["river"]]
    x, y = P.xy(15.79, 46.672)
    o.append(f'<text class="label-country" x="{x}" y="{y}">Slowenien</text>')
    x, y = P.xy(15.62, 46.885)
    o.append(f'<text class="label-country" x="{x}" y="{y + 20}">Steiermark</text>')
    for key in KEYS:
        p = P.path(D["routes"][key]["coords"])
        o.append(f'<g class="route" data-route="{key}"><path class="route__hit" d="{p}"/><path class="route__line" d="{p}"/></g>')
    x, y = P.xy(15.9505, 46.7203)
    o.append(f'<circle class="place" cx="{x}" cy="{y}" r="5"/><text x="{x + 14}" y="{y + 6}">Halbenrain</text>')
    for key, (name, lon, lat) in ((k, ROUTES[k]["start"]) for k in KEYS):
        x, y = P.xy(lon, lat)
        o.append(f'<g class="start" data-route="{key}"><circle cx="{x}" cy="{y}" r="9"/>{label(P, name, lon, lat)}</g>')
    for key, name in (("west", "Mureck"), ("sued", "Steirerbrücke"), ("nordost", "Klöch")):
        s = next(s for s in ROUTES[key]["stops"] if s[0] == name)
        x, y = P.xy(s[1], s[2])
        o.append(f'<g class="stop" data-route="{key}"><circle cx="{x}" cy="{y}" r="6"/>{label(P, name, s[1], s[2])}</g>')
    o.append(home_marker(P))
    o.append("</svg>")
    return "\n".join(o)


def route_map(key):
    r = D["routes"][key]
    lons = [c[0] for c in r["coords"]] + [HOME[0]]
    lats = [c[1] for c in r["coords"]] + [HOME[1]]
    w0, e0, s0, n0 = min(lons), max(lons), min(lats), max(lats)
    padx, pady = (e0 - w0) * 0.18 + 0.02, (n0 - s0) * 0.18 + 0.015
    w0, e0, s0, n0 = w0 - padx, e0 + padx * 1.6 + 0.045, s0 - pady, n0 + pady
    # Seitenverhältnis mindestens 4:3 quer
    cos = math.cos(math.radians((n0 + s0) / 2))
    if (e0 - w0) * cos < (n0 - s0) * 4 / 3:
        extra = ((n0 - s0) * 4 / 3 / cos - (e0 - w0)) / 2
        w0, e0 = w0 - extra, e0 + extra
    P = Proj(w0, e0, n0, s0)
    R = ROUTES[key]
    o = [f'<svg viewBox="0 0 {P.w} {P.h}" role="img" aria-labelledby="map-{key}">',
         f'<title id="map-{key}">Karte der Route {escape(R["name"])} zum Genussplatzl in Unterpurkla</title>']
    o += [f'<path class="river" d="{P.path(w)}"/>' for w in D["river"]]
    for k in KEYS:
        if k != key:
            o.append(f'<path class="route-other" d="{P.path(D["routes"][k]["coords"])}"/>')
    o.append(f'<path class="route-main" d="{P.path(r["coords"])}"/>')
    for name, lon, lat, _ in R["stops"][:-1]:
        x, y = P.xy(lon, lat)
        cls = "start" if name == R["start"][0] else "stop"
        rad = 9 if cls == "start" else 6
        o.append(f'<g class="{cls}"><circle cx="{x}" cy="{y}" r="{rad}"/>{label(P, name, lon, lat)}</g>')
    o.append(home_marker(P))
    o.append("</svg>")
    return "\n".join(o)


def profile(key):
    r = D["routes"][key]
    cum, ele = r["cum"], [c[2] for c in r["coords"]]
    total = cum[-1]
    n = 160  # gleichmäßig abgetastet
    pts = []
    j = 0
    for i in range(n + 1):
        d = total * i / n
        while j < len(cum) - 1 and cum[j + 1] < d:
            j += 1
        pts.append((d, ele[j]))
    # leicht glätten (DEM-Rauschen)
    sm = [(pts[i][0], sum(p[1] for p in pts[max(0, i - 2):i + 3]) / len(pts[max(0, i - 2):i + 3])) for i in range(len(pts))]
    lo, hi = min(e for _, e in sm), max(e for _, e in sm)
    y0 = math.floor((lo - 10) / 10) * 10
    y1 = max(math.ceil((hi + 10) / 10) * 10, y0 + 60)
    W, H, L, B, T, Rm = 1000, 240, 56, 34, 12, 8
    sx = lambda d: L + (W - L - Rm) * d / total
    sy = lambda e: T + (H - T - B) * (1 - (e - y0) / (y1 - y0))
    line = "M" + " L".join(f"{sx(d):.1f} {sy(e):.1f}" for d, e in sm)
    area = line + f" L{sx(total):.1f} {sy(y0):.1f} L{sx(0):.1f} {sy(y0):.1f} Z"
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="prof-{key}" data-profile=\'{json.dumps([[round(d, 2), round(e)] for d, e in sm])}\' data-x0="{L}" data-x1="{W - Rm}" data-y0="{y0}" data-y1="{y1}" data-top="{T}" data-bottom="{H - B}">',
         f'<title id="prof-{key}">Höhenprofil {escape(ROUTES[key]["name"])}: {de(total, 1)} Kilometer, von {round(sm[0][1])} auf {round(sm[-1][1])} Meter, tiefster Punkt {round(lo)} Meter, höchster Punkt {round(hi)} Meter</title>']
    step = 50 if (y1 - y0) > 120 else 20
    for e in range(int(math.ceil(y0 / step) * step), int(y1) + 1, step):
        o.append(f'<line class="grid" x1="{L}" x2="{W - Rm}" y1="{sy(e):.1f}" y2="{sy(e):.1f}"/><text class="tick" x="{L - 10}" y="{sy(e) + 5:.1f}" text-anchor="end">{e}</text>')
    kstep = 5 if total > 12 else 2
    k = 0
    while k <= total + 0.01:
        o.append(f'<text class="tick" x="{sx(k):.1f}" y="{H - 8}" text-anchor="middle">{k} km</text>')
        k += kstep
    o.append(f'<path class="prof-area" d="{area}"/><path class="prof-line" d="{line}"/>')
    o.append(f'<line class="prof-cross" x1="0" x2="0" y1="{T}" y2="{H - B}" visibility="hidden"/>')
    o.append("</svg>")
    return "\n".join(o), lo, hi


def gpx(key):
    R, r = ROUTES[key], D["routes"][key]
    pts = "\n".join(f'      <trkpt lat="{c[1]}" lon="{c[0]}"><ele>{c[2]}</ele></trkpt>' for c in r["coords"])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="s-genussplatzl.at" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>{escape(R["name"])} zum s’Genussplatz’l</name>
    <desc>{escape(R["desc"])} Route berechnet mit BRouter auf Daten von OpenStreetMap (© OpenStreetMap-Mitwirkende, ODbL).</desc>
    <link href="{SITE}radrouten/{R["slug"]}.html"><text>s’Genussplatz’l</text></link>
  </metadata>
  <wpt lat="{HOME[1]}" lon="{HOME[0]}"><name>s’Genussplatz’l</name><desc>Unterpurkla 28, 8484 Halbenrain</desc></wpt>
  <trk>
    <name>{escape(R["name"])} zum s’Genussplatz’l</name>
    <trkseg>
{pts}
    </trkseg>
  </trk>
</gpx>
'''


# ---------------------------------------------------------------- pages
LAYOUT = (ROOT / "layout.html").read_text(encoding="utf-8")


def render(path, title, desc, content, root="", jsonld=None, bodyclass="page"):
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"
    canonical = SITE + ("" if path == "index.html" else path)
    out = (LAYOUT.replace("{{title}}", escape(title, quote=True)).replace("{{description}}", escape(desc, quote=True))
           .replace("{{canonical}}", canonical).replace("{{site}}", SITE).replace("{{jsonld}}", ld).replace("{{bodyclass}}", bodyclass)
           .replace("{{analytics}}", f'<script defer src="{UMAMI_SRC}" data-website-id="{UMAMI_ID}" data-domains="s-genussplatzl.at,www.s-genussplatzl.at,s-genussplatzl.github.io"></script>' if UMAMI_ID else "")
           .replace("{{content}}", content).replace("{{root}}", root))
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_text(out, encoding="utf-8")
    return path


def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def picture(name, alt, w, h, sizes, widths, root, lazy=True, cls=""):
    webp = ", ".join(f"{root}images/{name}-{x}.webp {x}w" for x in widths)
    jpg = ", ".join(f"{root}images/{name}-{x}.jpg {x}w" for x in widths)
    return (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="{root}images/{name}-{widths[-1]}.jpg" srcset="{jpg}" sizes="{sizes}" width="{w}" height="{h}" alt="{escape(alt)}"{" loading=\"lazy\"" if lazy else ""}></picture>')


def route_page(key):
    R, r = ROUTES[key], D["routes"][key]
    root = "../"
    prof_svg, lo, hi = profile(key)
    stops = "".join(
        f'<li><span class="distance">{"Start" if i == 0 else ("Ziel" if i == len(R["stops"]) - 1 else "km " + de(km_at(key, s[1], s[2]), 0))}</span>'
        f'<h3>{escape(s[0])}</h3><p>{escape(s[3])}</p></li>'
        for i, s in enumerate(R["stops"]))
    others = "".join(
        f'<li><a href="{ROUTES[k]["slug"]}.html"><span class="others__name">{escape(ROUTES[k]["name"])}</span>'
        f'<span class="distance">ca. {de(round(D["routes"][k]["km"]))} km</span></a></li>'
        for k in KEYS if k != key)
    hm = f"ca. {r['up']} m" if r["up"] >= 40 else "kaum Steigungen"
    content = f'''
  <section class="page-head" aria-labelledby="page-title">
    <div class="container">
      <p class="crumbs"><a href="{root}index.html">Startseite</a> <span aria-hidden="true">/</span> <a href="{root}index.html#umgebung">Radrouten</a></p>
      <h1 id="page-title">{escape(R["h1"])}</h1>
      <p class="lead">{escape(R["lead"])}</p>
      <dl class="facts">
        <div><dt>Länge</dt><dd>ca. {de(r["km"], 1)} km</dd></div>
        <div><dt>Bergauf</dt><dd>{hm}</dd></div>
        <div><dt>Start</dt><dd>{escape(R["start"][0])}</dd></div>
        <div><dt>Ziel</dt><dd>s’Genussplatz’l, Unterpurkla</dd></div>
      </dl>
    </div>
  </section>

  <section class="section route-body" aria-labelledby="way-title">
    <div class="container route__grid">
      <figure class="map route__map">
        {route_map(key)}
        <figcaption>Route berechnet mit BRouter, Verlauf der Mur nach OpenStreetMap, © OpenStreetMap-Mitwirkende</figcaption>
      </figure>
      <div>
        <h2 id="way-title" class="title-s">Unterwegs</h2>
        <ol class="index stops">{stops}</ol>
        <p class="route__ways">Wege: {escape(R["ways"])}.</p>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="prof-title">
    <div class="container">
      <h2 id="prof-title" class="title-s">Höhenprofil</h2>
      <figure class="profile" data-profile-figure>
        {prof_svg}
        <figcaption><span class="profile__readout" aria-live="polite">Tiefster Punkt {round(lo)} m, höchster Punkt {round(hi)} m über dem Meer.</span></figcaption>
      </figure>
    </div>
  </section>

  <section class="band--visit" aria-labelledby="take-title">
    <div class="container take__grid">
      <div>
        <h2 id="take-title">Route mitnehmen.</h2>
        <p>Öffnen Sie die Route direkt in Komoot, mit Navigation auf dem Handy, oder laden Sie die Strecke als GPX-Datei für Ihr Navi, Garmin, Wahoo oder Ihre Rad-App.</p>
      </div>
      <div class="actions take__actions">
        <a class="btn btn--primary" href="{root}gpx/{R["slug"]}.gpx" download>GPX herunterladen</a>
        <a class="btn btn--secondary" href="https://www.komoot.com/de-de/tour/{R["komoot"]}">In Komoot öffnen</a>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="goal-title">
    <div class="container goal__grid">
      <div class="goal__photo" data-slot="ziel-{key}" data-alt="Das Genussplatzl in der Abenddämmerung">
        {picture("abend-q", "Das Genussplatzl in der Abenddämmerung, innen beleuchtet", 1200, 1200, "(max-width: 60rem) 100vw, 45vw", [1200], root)}
      </div>
      <div class="goal__text">
        <h2 id="goal-title">Am Ziel: Rast unterm Nussbaum.</h2>
        <p>Am Ende der Route warten Schatten unterm Nussbaum, regionale Weine und Spritzer, ein WC, kostenloses <a href="{root}e-bike-laden.html">E-Bike-Laden</a> und an heißen Tagen ein klimatisierter Raum. Von März bis Oktober, täglich 9 bis 22 Uhr.</p>
        <div class="actions"><a class="btn btn--secondary" href="{root}index.html#anfahrt">Anfahrt und Öffnungszeiten</a></div>
      </div>
    </div>
  </section>

  <section class="section section--last" aria-labelledby="more-title">
    <div class="container">
      <h2 id="more-title" class="title-s">Weitere Routen zum Genussplatzl</h2>
      <ul class="others">{others}</ul>
    </div>
  </section>
'''
    path = f"radrouten/{R['slug']}.html"
    ld = crumbs([("Startseite", ""), ("Radrouten", "#umgebung"), (R["name"], path)])
    return render(path, f"{R['title']} | s’Genussplatz’l", R["desc"], content, root, ld)


def ebike_page():
    root = ""
    west = D["routes"]["west"]
    content = f'''
  <section class="page-head" aria-labelledby="page-title">
    <div class="container">
      <p class="crumbs"><a href="index.html">Startseite</a></p>
      <h1 id="page-title">E-Bike laden am Radweg.</h1>
      <p class="lead">Kostenlos Akku laden, während Sie unterm Nussbaum rasten: direkt am Gleichenberger Radweg R45, kurz vor dem Murradweg.</p>
      <dl class="facts">
        <div><dt>Kosten</dt><dd>kostenlos</dd></div>
        <div><dt>Wo</dt><dd>Unterpurkla 28, am R45</dd></div>
        <div><dt>Wann</dt><dd>März bis Oktober, 9 bis 22 Uhr</dd></div>
        <div><dt>Murradweg</dt><dd>wenige Minuten entfernt</dd></div>
      </dl>
    </div>
  </section>

  <section class="section" aria-labelledby="how-title">
    <div class="container goal__grid">
      <div class="goal__photo goal__photo--wide" data-slot="ebike" data-alt="Fahrrad an der Ladesäule">
        {picture("radstation", "Fahrrad neben der Ladesäule am Genussplatzl", 1600, 1200, "(max-width: 60rem) 100vw, 50vw", [800, 1600], root)}
      </div>
      <div class="goal__text">
        <h2 id="how-title">Laden und durchatmen.</h2>
        <p>Stellen Sie Ihr Rad an die Ladesäule, schließen Sie Ihr Ladegerät an und gönnen Sie sich eine Pause. Während der Akku lädt, warten Schatten unterm Nussbaum, regionale Weine und Spritzer, kühle Getränke, ein WC und an heißen Tagen ein klimatisierter Raum.</p>
        <p>Bitte nehmen Sie Ihr eigenes Ladegerät mit.</p>
      </div>
    </div>
  </section>

  <section class="section section--last" aria-labelledby="routes-title">
    <div class="container">
      <h2 id="routes-title" class="title-s">Mit dem Rad zu uns</h2>
      <ul class="others">{"".join(f'<li><a href="radrouten/{ROUTES[k]["slug"]}.html"><span class="others__name">{escape(ROUTES[k]["name"])}</span><span class="distance">ca. {de(round(D["routes"][k]["km"]))} km</span></a></li>' for k in KEYS)}</ul>
    </div>
  </section>
'''
    return render("e-bike-laden.html", "E-Bike laden am Murradweg und R45 in Halbenrain | s’Genussplatz’l",
                  "Kostenlose E-Bike-Ladestation am Gleichenberger Radweg R45 in Unterpurkla, Halbenrain, kurz vor dem Murradweg R2. Laden im Schatten unterm Nussbaum, März bis Oktober.",
                  content, root, crumbs([("Startseite", ""), ("E-Bike laden", "e-bike-laden.html")]))


def index_page():
    content = (ROOT / "pages" / "index.html").read_text(encoding="utf-8")
    items = "\n".join(
        f'          <li data-route="{k}"><h3>{escape(ROUTES[k]["name"])}</h3><span class="distance">ca. {de(round(D["routes"][k]["km"]))} km</span>'
        f'<p>{escape(ROUTES[k]["index_text"])}</p><a class="ride__more" href="radrouten/{ROUTES[k]["slug"]}.html">Route, Höhenprofil und GPX</a></li>'
        for k in KEYS)
    content = content.replace("{{ROUTE_ITEMS}}", items).replace("{{MAP}}", overview_map())
    content = content.replace("{{BIKESPA}}", (ROOT / "bikespa.svg.part").read_text(encoding="utf-8"))
    ld = {
        "@context": "https://schema.org",
        "@type": ["TouristAttraction", "LocalBusiness"],
        "@id": SITE + "#genussplatzl",
        "name": "s’Genussplatz’l",
        "description": "Rastplatz unterm Nussbaum am Gleichenberger Radweg R45 in Unterpurkla: regionale Weine, Kunst und Naturschatten im Thermen- & Vulkanland, der Toskana der Steiermark.",
        "url": SITE,
        "image": SITE + "images/og-abend.jpg",
        "email": "info@s-genussplatzl.at",
        "telephone": "+43 664 5785026",
        "address": {"@type": "PostalAddress", "streetAddress": "Unterpurkla 28", "postalCode": "8484",
                    "addressLocality": "Halbenrain", "addressRegion": "Steiermark", "addressCountry": "AT"},
        "geo": {"@type": "GeoCoordinates", "latitude": HOME[1], "longitude": HOME[0]},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                       "opens": "09:00", "closes": "22:00", "validFrom": "2027-03-01", "validThrough": "2027-10-31"}],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                           for n in ("E-Bike-Ladestation", "WC", "Schatten unterm Nussbaum", "Klimatisierter Raum")],
        "isAccessibleForFree": True,
        "touristType": ["Radfahrer", "Wanderer", "Ausflügler"],
        "sameAs": ["https://www.instagram.com/s_genussplatz_l_/", "https://www.komoot.com/de-de/highlight/8495359",
                   "https://maps.google.com/?cid=5193859400819937139",
                   "https://www.steiermark.com/de/Thermen-Vulkanland/Urlaub-planen/Ausflugsziele/sGenussplatzl_isd_60512740"],
    }
    return render("index.html", "s’Genussplatz’l, Rasten unterm Nussbaum in Unterpurkla am Radweg R45",
                  "Rasten unterm Nussbaum in Unterpurkla: eine Oase der Entspannung in der Toskana der Steiermark, mit regionalen Weinen, Kunst und Naturschatten am Gleichenberger Radweg R45.",
                  content, "", ld, bodyclass="home")


def legal_page():
    content = (ROOT / "pages" / "datenschutz.html").read_text(encoding="utf-8")
    return render("datenschutz.html", "Datenschutz | s’Genussplatz’l",
                  "Datenschutzerklärung der Website des s’Genussplatz’l in Unterpurkla: Hosting, Besucherstatistik ohne Cookies, Ihre Rechte.",
                  content, "", crumbs([("Startseite", ""), ("Datenschutz", "datenschutz.html")]))


def bikespa_page():
    src = ROOT / "pages" / "bike-and-spa.html"
    if not src.exists():
        return None
    meta = json.loads((ROOT / "pages" / "bike-and-spa.json").read_text(encoding="utf-8"))
    content = src.read_text(encoding="utf-8").replace("{{BIKESPA}}", (ROOT / "bikespa.svg.part").read_text(encoding="utf-8"))
    return render("bike-and-spa.html", meta["title"], meta["description"], content, "",
                  crumbs([("Startseite", ""), ("Bike & Spa", "bike-and-spa.html")]))


if __name__ == "__main__":
    (ROOT / "gpx").mkdir(exist_ok=True)
    for k in KEYS:
        (ROOT / "gpx" / f"{ROUTES[k]['slug']}.gpx").write_text(gpx(k), encoding="utf-8")
    pages = [index_page()] + [route_page(k) for k in KEYS] + [ebike_page(), legal_page()]
    bs = bikespa_page()
    if bs:
        pages.append(bs)
    urls = "\n".join(f"  <url><loc>{SITE}{'' if p == 'index.html' else p}</loc></url>" for p in pages)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    print("gebaut:", ", ".join(pages))
