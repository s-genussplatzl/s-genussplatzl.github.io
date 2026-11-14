"""Baut die ganze Website aus layout.html + pages/ + Routendaten.

  python tools/site.py                 # alles bauen
  python tools/site.py --import <dir>  # Routen (BRouter-GeoJSON) und Mur neu einlesen

Erzeugt: index.html, radrouten/*.html, e-bike-laden.html, bike-and-spa.html,
gpx/*.gpx, sitemap.xml, robots.txt (Bike-&-Spa-Karte: tools/bikespa_map.py).
Routen: BRouter (Profil trekking) auf OpenStreetMap-Daten, © OpenStreetMap-Mitwirkende.
"""
import json
import math
import re
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
    return s.replace(".", U["decimal"])


# ---------------------------------------------------------------- languages
# Deutsch liegt im Wurzelverzeichnis, die anderen Sprachen in /sl/, /en/, /hu/ mit gleichen Dateinamen.
LANGS = ("de", "sl", "en", "hu")
HREFLANG = {"de": "de", "sl": "sl", "en": "en", "hu": "hu"}
LANG_DIR = ROOT / "tools" / "lang"
TEXTS = {l: json.loads((LANG_DIR / f"{l}.json").read_text(encoding="utf-8")) for l in LANGS if (LANG_DIR / f"{l}.json").exists()}
# Eine Sprache ist aktiv, sobald Texte und Seiten-Vorlagen da sind.
AVAIL = [l for l in LANGS if l in TEXTS and (l == "de" or (ROOT / "pages" / l / "index.html").exists())]
L = "de"
U = TEXTS["de"]["ui"]
TR = TEXTS["de"]["routes"]


def set_lang(l):
    global L, U, TR
    L, U, TR = l, TEXTS[l]["ui"], TEXTS[l]["routes"]


def prefix(l):
    return "" if l == "de" else f"{l}/"


def t(key, **kw):
    v = U[key]
    return v.format(**kw) if kw else v


def komoot(kind, ident):
    loc = U.get("komoot_locale")
    return f"https://www.komoot.com/{loc + '/' if loc else ''}{kind}/{ident}"


# ---------------------------------------------------------------- content
GENUSS = ("s’Genussplatz’l", HOME[0], HOME[1])

# Nur Struktur und Koordinaten; alle Texte stehen in tools/lang/<sprache>.json unter "routes".
ROUTES = {
    "west": dict(slug="murradweg-ab-spielfeld", komoot="3392769165", start=("Spielfeld", 15.6360, 46.7085),
                 stops=[("Spielfeld", 15.6360, 46.7085), ("Mureck", 15.7695, 46.7076), ("Gosdorf", 15.80911, 46.72221), GENUSS]),
    "nord": dict(slug="r45-ab-bad-gleichenberg", komoot="3392769397", start=("Bad Gleichenberg", 15.9050, 46.8745),
                 stops=[("Bad Gleichenberg", 15.9050, 46.8745), ("Trautmannsdorf", 15.88906, 46.85782), ("Radochen", 15.88857, 46.76614), GENUSS]),
    "nordost": dict(slug="ab-st-anna-ueber-kloech", komoot="3392769506", start=("St. Anna am Aigen", 15.9610, 46.8355),
                    stops=[("St. Anna am Aigen", 15.9610, 46.8355), ("Klöch", 15.9656, 46.7642), GENUSS]),
    "ost": dict(slug="ab-bad-radkersburg", komoot="3392769623", start=("Bad Radkersburg", 15.9867, 46.6875),
                stops=[("Bad Radkersburg", 15.9867, 46.6875), ("Dietzen", 15.94248, 46.71051), GENUSS]),
    "sued": dict(slug="ab-apace-ueber-die-steirerbruecke", komoot="3392769770", start=("Apače", 15.9100, 46.6965),
                 stops=[("Apače", 15.9100, 46.6965), ("Steirerbrücke", 15.8930, 46.7140), GENUSS]),
}
WAYPOINT_LABELS = {  # Kartenbeschriftung: dx, dy, anchor (Schlüssel: deutscher Ortsname)
    "Spielfeld": (0, -20, "start"), "Bad Gleichenberg": (-16, -6, "end"), "St. Anna am Aigen": (16, 6, "start"),
    "Bad Radkersburg": (-4, 34, "middle"), "Apače": (-16, 30, "end"), "Mureck": (0, 34, "middle"),
    "Steirerbrücke": (-16, 6, "end"), "Klöch": (16, 6, "start"), "Gosdorf": (0, 34, "middle"),
    "Trautmannsdorf": (16, 6, "start"), "Radochen": (16, 6, "start"), "Dietzen": (0, -18, "middle"),
}


def stop_name(key, i):
    """Angezeigter Ortsname der i-ten Station in der aktuellen Sprache."""
    return TR[key]["stops"][i][0]


def stop_name_by_de(key, de_name):
    i = next(j for j, s in enumerate(ROUTES[key]["stops"]) if s[0] == de_name)
    return stop_name(key, i)


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


def label(P, de_name, lon, lat, shown=None, cls=""):
    x, y = P.xy(lon, lat)
    dx, dy, anchor = WAYPOINT_LABELS.get(de_name, (16, 6, "start"))
    return f'<text{cls} x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{escape(shown or de_name)}</text>'


def home_marker(P):
    hx, hy = P.xy(*HOME)
    return (f'<circle class="home-ring" cx="{hx}" cy="{hy}" r="24"/><circle class="place--home" cx="{hx}" cy="{hy}" r="12"/>'
            f'<text class="label-home" x="{hx + 34}" y="{hy - 16}">s’Genussplatz’l</text>')


def overview_map():
    P = Proj(15.60, 16.09, 46.89, 46.66)
    o = [f'<svg viewBox="0 0 {P.w} {P.h}" role="img" aria-labelledby="ride-title">',
         f'<title id="ride-title">{escape(t("overview_title"))}</title>']
    o += [f'<path class="river" d="{P.path(w)}"/>' for w in D["river"]]
    x, y = P.xy(15.79, 46.672)
    o.append(f'<text class="label-country" x="{x}" y="{y}">{escape(t("map_slovenia"))}</text>')
    x, y = P.xy(15.62, 46.885)
    o.append(f'<text class="label-country" x="{x}" y="{y + 20}">{escape(t("map_styria"))}</text>')
    for key in KEYS:
        p = P.path(D["routes"][key]["coords"])
        o.append(f'<g class="route" data-route="{key}"><path class="route__hit" d="{p}"/><path class="route__line" d="{p}"/></g>')
    x, y = P.xy(15.9505, 46.7203)
    o.append(f'<circle class="place" cx="{x}" cy="{y}" r="5"/><text x="{x + 14}" y="{y + 6}">{escape(t("map_halbenrain"))}</text>')
    for key in KEYS:
        name, lon, lat = ROUTES[key]["start"]
        x, y = P.xy(lon, lat)
        o.append(f'<g class="start" data-route="{key}"><circle cx="{x}" cy="{y}" r="9"/>{label(P, name, lon, lat, stop_name(key, 0))}</g>')
    for key, name in (("west", "Mureck"), ("sued", "Steirerbrücke"), ("nordost", "Klöch")):
        s = next(s for s in ROUTES[key]["stops"] if s[0] == name)
        x, y = P.xy(s[1], s[2])
        o.append(f'<g class="stop" data-route="{key}"><circle cx="{x}" cy="{y}" r="6"/>{label(P, name, s[1], s[2], stop_name_by_de(key, name))}</g>')
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
         f'<title id="map-{key}">{escape(t("map_title", name=TR[key]["name"]))}</title>']
    o += [f'<path class="river" d="{P.path(w)}"/>' for w in D["river"]]
    for k in KEYS:
        if k != key:
            o.append(f'<path class="route-other" d="{P.path(D["routes"][k]["coords"])}"/>')
    o.append(f'<path class="route-main" d="{P.path(r["coords"])}"/>')
    for i, (name, lon, lat) in enumerate(R["stops"][:-1]):
        x, y = P.xy(lon, lat)
        cls = "start" if i == 0 else "stop"
        rad = 9 if cls == "start" else 6
        o.append(f'<g class="{cls}"><circle cx="{x}" cy="{y}" r="{rad}"/>{label(P, name, lon, lat, stop_name(key, i))}</g>')
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
    W, H, Lm, B, T, Rm = 1000, 240, 56, 34, 12, 8
    sx = lambda d: Lm + (W - Lm - Rm) * d / total
    sy = lambda e: T + (H - T - B) * (1 - (e - y0) / (y1 - y0))
    line = "M" + " L".join(f"{sx(d):.1f} {sy(e):.1f}" for d, e in sm)
    area = line + f" L{sx(total):.1f} {sy(y0):.1f} L{sx(0):.1f} {sy(y0):.1f} Z"
    ttl = t("prof_svg_title", name=TR[key]["name"], km=de(total, 1), a=round(sm[0][1]), b=round(sm[-1][1]), lo=round(lo), hi=round(hi))
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="prof-{key}" data-profile=\'{json.dumps([[round(d, 2), round(e)] for d, e in sm])}\' data-x0="{Lm}" data-x1="{W - Rm}" data-y0="{y0}" data-y1="{y1}" data-top="{T}" data-bottom="{H - B}">',
         f'<title id="prof-{key}">{escape(ttl)}</title>']
    step = 50 if (y1 - y0) > 120 else 20
    for e in range(int(math.ceil(y0 / step) * step), int(y1) + 1, step):
        o.append(f'<line class="grid" x1="{Lm}" x2="{W - Rm}" y1="{sy(e):.1f}" y2="{sy(e):.1f}"/><text class="tick" x="{Lm - 10}" y="{sy(e) + 5:.1f}" text-anchor="end">{e}</text>')
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
    """GPX-Dateien sind für alle Sprachen gleich (deutsche Beschreibung)."""
    R, r, TD = ROUTES[key], D["routes"][key], TEXTS["de"]["routes"][key]
    pts = "\n".join(f'      <trkpt lat="{c[1]}" lon="{c[0]}"><ele>{c[2]}</ele></trkpt>' for c in r["coords"])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="s-genussplatzl.at" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>{escape(TD["name"])} zum s’Genussplatz’l</name>
    <desc>{escape(TD["desc"])} Route berechnet mit BRouter auf Daten von OpenStreetMap (© OpenStreetMap-Mitwirkende, ODbL).</desc>
    <link href="{SITE}radrouten/{R["slug"]}.html"><text>s’Genussplatz’l</text></link>
  </metadata>
  <wpt lat="{HOME[1]}" lon="{HOME[0]}"><name>s’Genussplatz’l</name><desc>Unterpurkla 28, 8484 Halbenrain</desc></wpt>
  <trk>
    <name>{escape(TD["name"])} zum s’Genussplatz’l</name>
    <trkseg>
{pts}
    </trkseg>
  </trk>
</gpx>
'''


# ---------------------------------------------------------------- pages
LAYOUT = (ROOT / "layout.html").read_text(encoding="utf-8")


def page_url(l, path):
    return SITE + prefix(l) + ("" if path == "index.html" else path)


def lang_links(path, root):
    """hreflang-Verweise (head) und Sprachumschalter (nav) für eine Seite."""
    avail = AVAIL
    alt = "\n".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{page_url(l, path)}">' for l in avail)
    alt += f'\n<link rel="alternate" hreflang="x-default" href="{page_url("de", path)}">'
    items = []
    for l in avail:
        u = TEXTS[l]["ui"]
        cur = ' aria-current="true"' if l == L else ""
        items.append(f'<li><a href="{root}{prefix(l)}{path}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}"{cur} '
                     f'aria-label="{escape(u["lang_name"], quote=True)}">{escape(u["lang_short"])}</a></li>')
    switch = f'<ul class="lang-switch" aria-label="{escape(t("lang_label"), quote=True)}">' + "".join(items) + "</ul>"
    foot = "".join(f'<li><a href="{root}{prefix(l)}{path}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}">{escape(TEXTS[l]["ui"]["lang_name"])}</a></li>'
                   for l in avail if l != L)
    return alt, switch, foot


def fill_ui(text):
    def rep(m):
        k = m.group(1)
        v = U[k]
        return v if k.endswith("_html") else escape(v, quote=True)
    return re.sub(r"\{\{t\.([a-z0-9_]+)\}\}", rep, text)


def render(path, title, desc, content, jsonld=None, bodyclass="page"):
    """path: Seitenpfad relativ zur Sprachwurzel, z. B. radrouten/x.html."""
    out_path = prefix(L) + path
    root = "../" * out_path.count("/")   # Wurzel der Website (Bilder, CSS, GPX)
    home = "../" * path.count("/")       # Wurzel der aktuellen Sprache (Seiten)
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"
    alt, switch, foot = lang_links(path, root)
    # Bildpfade in den Seiten-Vorlagen auf die Website-Wurzel beziehen
    content = re.sub(r'(?<=[" ,])images/', root + "images/", content) if root else content
    out = (fill_ui(LAYOUT).replace("{{title}}", escape(title, quote=True)).replace("{{description}}", escape(desc, quote=True))
           .replace("{{canonical}}", page_url(L, path)).replace("{{site}}", SITE).replace("{{jsonld}}", ld).replace("{{bodyclass}}", bodyclass)
           .replace("{{lang}}", HREFLANG[L]).replace("{{locale}}", U["locale"]).replace("{{alternates}}", alt)
           .replace("{{langswitch}}", switch).replace("{{langfoot}}", foot)
           .replace("{{analytics}}", f'<script defer src="{UMAMI_SRC}" data-website-id="{UMAMI_ID}" data-domains="s-genussplatzl.at,www.s-genussplatzl.at,s-genussplatzl.github.io"></script>' if UMAMI_ID else "")
           .replace("{{content}}", content).replace("{{root}}", root).replace("{{home}}", home))
    (ROOT / out_path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / out_path).write_text(out, encoding="utf-8")
    return out_path


def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + prefix(L) + u} for i, (n, u) in enumerate(items)]}


def picture(name, alt, w, h, sizes, widths, root, lazy=True, cls=""):
    webp = ", ".join(f"{root}images/{name}-{x}.webp {x}w" for x in widths)
    jpg = ", ".join(f"{root}images/{name}-{x}.jpg {x}w" for x in widths)
    return (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="{root}images/{name}-{widths[-1]}.jpg" srcset="{jpg}" sizes="{sizes}" width="{w}" height="{h}" alt="{escape(alt)}"{" loading=\"lazy\"" if lazy else ""}></picture>')


ZIELE_FILE = ROOT / "tools" / "data" / "ziele.json"
ZIELE = json.loads(ZIELE_FILE.read_text(encoding="utf-8")) if ZIELE_FILE.exists() else {"routes": {}, "photos": {}}


def spots_section(key, root):
    """Slider mit Sehenswertem entlang der Route (Fotos von Wikimedia Commons mit Nachweis)."""
    ids = [i for i in ZIELE["routes"].get(key, []) if i in ZIELE["photos"] and i in TEXTS[L].get("spots", {})]
    if not ids:
        return ""
    S = TEXTS[L]["spots"]
    slides = []
    for i in ids:
        ph, (name, text) = ZIELE["photos"][i], S[i]
        credit = (f'{escape(t("photo_by"))} <a href="{ph["page"]}">{escape(ph["author"])}</a>, '
                  f'<a href="{ph["license_url"]}">{escape(ph["license"])}</a>')
        slides.append(f'''
          <figure class="slide spot">
            <div class="slide__frame">
              {picture("ziele/" + i, ph["alt"].get(L) or name, 1600, 1200, "(max-width: 40rem) 80vw, 32vw", [800, 1600], root)}
            </div>
            <figcaption>
              <h3>{escape(name)}</h3>
              <p>{escape(text)}</p>
              <p class="spot__credit">{credit}</p>
            </figcaption>
          </figure>''')
    n = len(ids)
    word = t("spots_word")
    return f'''
  <section class="section spots" aria-labelledby="spots-title">
    <div class="container">
      <h2 id="spots-title" class="title-s">{escape(t("spots_title"))}</h2>
      <div class="slider slider--spots" data-slider>
        <div class="slider__track" tabindex="0" role="region" aria-label="{escape(t("spots_region"), quote=True)}">{"".join(slides)}
        </div>
        <div class="slider__controls" hidden>
          <button class="slider__btn" type="button" data-dir="-1" aria-label="{escape(t("spots_prev"), quote=True)}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
          <p class="slider__status" aria-live="polite">{escape(word)} {escape(t("js_of", i=1, n=n))}</p>
          <button class="slider__btn" type="button" data-dir="1" aria-label="{escape(t("spots_next"), quote=True)}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
        </div>
      </div>
      <p class="spot__credit spots__note">{escape(t("spots_note"))}</p>
    </div>
  </section>
'''


def approx_km(k):
    return f'{t("approx")} {de(round(D["routes"][k]["km"]))} km'


def route_page(key):
    R, r, X = ROUTES[key], D["routes"][key], TR[key]
    root = "../" * (prefix(L) + "radrouten/").count("/")
    home = "../"
    prof_svg, lo, hi = profile(key)
    n = len(R["stops"])

    def stop_tag(i, s):
        if i == 0:
            return t("stop_start")
        if i == n - 1:
            return t("stop_goal")
        return t("stop_km", km=de(km_at(key, s[1], s[2]), 0))
    stops = "".join(
        f'<li><span class="distance">{escape(stop_tag(i, s))}</span>'
        f'<h3>{escape(X["stops"][i][0])}</h3><p>{escape(X["stops"][i][1])}</p></li>'
        for i, s in enumerate(R["stops"]))
    others = "".join(
        f'<li><a href="{ROUTES[k]["slug"]}.html"><span class="others__name">{escape(TR[k]["name"])}</span>'
        f'<span class="distance">{approx_km(k)}</span></a></li>'
        for k in KEYS if k != key)
    hm = t("fact_up_value", m=r["up"]) if r["up"] >= 40 else t("fact_up_flat")
    content = f'''
  <section class="page-head" aria-labelledby="page-title">
    <div class="container">
      <p class="crumbs"><a href="{home}index.html">{escape(t("crumb_home"))}</a> <span aria-hidden="true">/</span> <a href="{home}index.html#umgebung">{escape(t("crumb_routes"))}</a></p>
      <h1 id="page-title">{escape(X["h1"])}</h1>
      <p class="lead">{escape(X["lead"])}</p>
      <dl class="facts">
        <div><dt>{escape(t("fact_length"))}</dt><dd>{t("approx")} {de(r["km"], 1)} km</dd></div>
        <div><dt>{escape(t("fact_up"))}</dt><dd>{escape(hm)}</dd></div>
        <div><dt>{escape(t("fact_start"))}</dt><dd>{escape(X["stops"][0][0])}</dd></div>
        <div><dt>{escape(t("fact_goal"))}</dt><dd>{escape(t("fact_goal_value"))}</dd></div>
      </dl>
    </div>
  </section>

  <section class="section route-body" aria-labelledby="way-title">
    <div class="container route__grid">
      <figure class="map route__map">
        {route_map(key)}
        <figcaption>{escape(t("map_caption"))}</figcaption>
      </figure>
      <div>
        <h2 id="way-title" class="title-s">{escape(t("way_title"))}</h2>
        <ol class="index stops">{stops}</ol>
        <p class="route__ways">{escape(t("ways_prefix"))} {escape(X["ways"])}.</p>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="prof-title">
    <div class="container">
      <h2 id="prof-title" class="title-s">{escape(t("prof_title"))}</h2>
      <figure class="profile" data-profile-figure>
        {prof_svg}
        <figcaption><span class="profile__readout" aria-live="polite">{escape(t("prof_resting", lo=round(lo), hi=round(hi)))}</span></figcaption>
      </figure>
    </div>
  </section>

{spots_section(key, root)}
  <section class="band--visit" aria-labelledby="take-title">
    <div class="container take__grid">
      <div>
        <h2 id="take-title">{escape(t("take_title"))}</h2>
        <p>{escape(t("take_text"))}</p>
      </div>
      <div class="actions take__actions">
        <a class="btn btn--primary" href="{root}gpx/{R["slug"]}.gpx" download>{escape(t("gpx_btn"))}</a>
        <a class="btn btn--secondary" href="{komoot("tour", R["komoot"])}">{escape(t("komoot_btn"))}</a>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="goal-title">
    <div class="container goal__grid">
      <div class="goal__photo" data-slot="ziel-{key}" data-alt="{escape(t("goal_slot_alt"), quote=True)}">
        {picture("abendrot-q", t("goal_alt"), 1000, 1000, "(max-width: 60rem) 100vw, 45vw", [1000], root)}
      </div>
      <div class="goal__text">
        <h2 id="goal-title">{escape(t("goal_title"))}</h2>
        <p>{U["goal_text_html"].replace("{ebike}", home + "e-bike-laden.html")}</p>
        <div class="actions"><a class="btn btn--secondary" href="{home}index.html#anfahrt">{escape(t("goal_btn"))}</a></div>
      </div>
    </div>
  </section>

  <section class="section section--last" aria-labelledby="more-title">
    <div class="container">
      <h2 id="more-title" class="title-s">{escape(t("more_title"))}</h2>
      <ul class="others">{others}</ul>
    </div>
  </section>
'''
    path = f"radrouten/{R['slug']}.html"
    ld = crumbs([(t("crumb_home"), ""), (t("crumb_routes"), "#umgebung"), (X["name"], path)])
    return render(path, f"{X['title']} | s’Genussplatz’l", X["desc"], content, ld)


def ebike_page():
    root = "../" * prefix(L).count("/")
    content = f'''
  <section class="page-head" aria-labelledby="page-title">
    <div class="container">
      <p class="crumbs"><a href="index.html">{escape(t("crumb_home"))}</a></p>
      <h1 id="page-title">{escape(t("ebike_h1"))}</h1>
      <p class="lead">{escape(t("ebike_lead"))}</p>
      <dl class="facts">
        <div><dt>{escape(t("ebike_cost"))}</dt><dd>{escape(t("ebike_cost_value"))}</dd></div>
        <div><dt>{escape(t("ebike_where"))}</dt><dd>{escape(t("ebike_where_value"))}</dd></div>
        <div><dt>{escape(t("ebike_when"))}</dt><dd>{escape(t("ebike_when_value"))}</dd></div>
        <div><dt>{escape(t("ebike_mur"))}</dt><dd>{escape(t("ebike_mur_value"))}</dd></div>
      </dl>
    </div>
  </section>

  <section class="section" aria-labelledby="how-title">
    <div class="container goal__grid">
      <div class="goal__photo goal__photo--wide" data-slot="ebike" data-alt="{escape(t("ebike_slot_alt"), quote=True)}">
        {picture("radstation", t("ebike_alt"), 1600, 1200, "(max-width: 60rem) 100vw, 50vw", [800, 1600], root)}
      </div>
      <div class="goal__text">
        <h2 id="how-title">{escape(t("ebike_how_title"))}</h2>
        <p>{escape(t("ebike_how_text"))}</p>
        <p>{escape(t("ebike_charger"))}</p>
      </div>
    </div>
  </section>

  <section class="section section--last" aria-labelledby="routes-title">
    <div class="container">
      <h2 id="routes-title" class="title-s">{escape(t("ebike_routes_title"))}</h2>
      <ul class="others">{"".join(f'<li><a href="radrouten/{ROUTES[k]["slug"]}.html"><span class="others__name">{escape(TR[k]["name"])}</span><span class="distance">{approx_km(k)}</span></a></li>' for k in KEYS)}</ul>
    </div>
  </section>
'''
    return render("e-bike-laden.html", t("ebike_title"), t("ebike_desc"), content,
                  crumbs([(t("crumb_home"), ""), (t("crumb_ebike"), "e-bike-laden.html")]))


def page_src(name):
    p = ROOT / "pages" / (name if L == "de" else f"{L}/{name}")
    return p.read_text(encoding="utf-8")


def bikespa_svg():
    f = ROOT / ("bikespa.svg.part" if L == "de" else f"bikespa.{L}.svg.part")
    if not f.exists():
        f = ROOT / "bikespa.svg.part"
    return f.read_text(encoding="utf-8")


def index_page():
    content = page_src("index.html")
    items = "\n".join(
        f'          <li data-route="{k}"><h3>{escape(TR[k]["name"])}</h3><span class="distance">{approx_km(k)}</span>'
        f'<p>{escape(TR[k]["index_text"])}</p><a class="ride__more" href="radrouten/{ROUTES[k]["slug"]}.html">{escape(t("ride_more"))}</a></li>'
        for k in KEYS)
    content = content.replace("{{ROUTE_ITEMS}}", items).replace("{{MAP}}", overview_map())
    content = content.replace("{{BIKESPA}}", bikespa_svg())
    ld = {
        "@context": "https://schema.org",
        "@type": ["TouristAttraction", "LocalBusiness"],
        "@id": SITE + "#genussplatzl",
        "name": "s’Genussplatz’l",
        "description": t("ld_desc"),
        "url": page_url(L, "index.html"),
        "inLanguage": HREFLANG[L],
        "image": SITE + "images/og-abend.jpg",
        "email": "info@s-genussplatzl.at",
        "telephone": "+43 664 5785026",
        "address": {"@type": "PostalAddress", "streetAddress": "Unterpurkla 28", "postalCode": "8484",
                    "addressLocality": "Halbenrain", "addressRegion": "Steiermark", "addressCountry": "AT"},
        "geo": {"@type": "GeoCoordinates", "latitude": HOME[1], "longitude": HOME[0]},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                       "opens": "09:00", "closes": "22:00", "validFrom": "2027-03-01", "validThrough": "2027-10-31"}],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in U["ld_amenities"]],
        "isAccessibleForFree": True,
        "touristType": U["ld_tourist"],
        "sameAs": ["https://www.instagram.com/s_genussplatz_l_/", "https://www.komoot.com/de-de/highlight/8495359",
                   "https://maps.google.com/?cid=5193859400819937139",
                   "https://www.steiermark.com/de/Thermen-Vulkanland/Urlaub-planen/Ausflugsziele/sGenussplatzl_isd_60512740"],
    }
    return render("index.html", t("index_title"), t("index_desc"), content, ld, bodyclass="home")


def legal_page():
    return render("datenschutz.html", t("privacy_title"), t("privacy_desc"), page_src("datenschutz.html"),
                  crumbs([(t("crumb_home"), ""), (t("crumb_privacy"), "datenschutz.html")]))


def bikespa_page():
    base = ROOT / "pages" / ("" if L == "de" else L)
    if not (base / "bike-and-spa.html").exists():
        return None
    meta = json.loads((base / "bike-and-spa.json").read_text(encoding="utf-8"))
    content = (base / "bike-and-spa.html").read_text(encoding="utf-8").replace("{{BIKESPA}}", bikespa_svg())
    return render("bike-and-spa.html", meta["title"], meta["description"], content,
                  crumbs([(t("crumb_home"), ""), (t("crumb_bikespa"), "bike-and-spa.html")]))


def build_lang(l):
    set_lang(l)
    pages = [index_page()] + [route_page(k) for k in KEYS] + [ebike_page(), legal_page()]
    bs = bikespa_page()
    if bs:
        pages.append(bs)
    return pages


if __name__ == "__main__":
    only = [a for a in sys.argv[1:] if a in LANGS]
    (ROOT / "gpx").mkdir(exist_ok=True)
    for k in KEYS:
        (ROOT / "gpx" / f"{ROUTES[k]['slug']}.gpx").write_text(gpx(k), encoding="utf-8")
    pages = []
    for l in AVAIL:
        if not only or l in only:
            pages += build_lang(l)
    set_lang("de")
    all_pages = []
    for l in AVAIL:  # Sitemap immer vollständig
        if True:
            all_pages += [prefix(l) + p for p in ["index.html", *[f"radrouten/{ROUTES[k]['slug']}.html" for k in KEYS],
                                                    "e-bike-laden.html", "datenschutz.html", "bike-and-spa.html"]]
    urls = "\n".join(f"  <url><loc>{SITE}{p[:-10] if p.endswith('index.html') else p}</loc></url>" for p in all_pages)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    print("gebaut:", ", ".join(pages))
