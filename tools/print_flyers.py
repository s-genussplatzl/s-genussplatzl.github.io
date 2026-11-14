"""Druckentwürfe (Flyer, Postkarte, QR-Schild) als HTML mit 3 mm Beschnitt.

  python tools/print_flyers.py <zielordner>

Danach PDF mit Chrome: siehe Konzept, Abschnitt "PDF erzeugen" (tools/print_pdf.sh).
QR-Codes werden beim Öffnen im Browser erzeugt (qrcode-generator, cdnjs).
"""
import base64
import sys
from pathlib import Path

import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("gp_site", Path(__file__).resolve().parent / "site.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)  # tools/site.py: Routen, Karte

ROOT = S.ROOT
DEST = Path(sys.argv[1])
DEST.mkdir(parents=True, exist_ok=True)

BASE = "https://s-genussplatzl.at/"
QR = {
    "routen": BASE + "?utm_source=flyer&utm_campaign=routenflyer#umgebung",
    "postkarte": BASE + "?utm_source=postkarte&utm_campaign=hotels",
    "schild": BASE + "?utm_source=schild&utm_campaign=vor-ort#umgebung",
    "bewertung": "https://g.page/r/CXMPMlebSxRIEBM/review",
    "schaukasten": BASE + "bike-and-spa.html?utm_source=schaukasten&utm_campaign=bike-spa",
}


def b64(p, mime):
    return f"data:{mime};base64," + base64.b64encode((ROOT / p).read_bytes()).decode()


FONTS = f"""
@font-face {{ font-family: 'Prata'; src: url('{b64("fonts/prata-latin.woff2", "font/woff2")}') format('woff2'); }}
@font-face {{ font-family: 'Manrope'; font-weight: 400 700; src: url('{b64("fonts/manrope-latin.woff2", "font/woff2")}') format('woff2'); }}
@font-face {{ font-family: 'Manrope'; font-weight: 400 700; src: url('{b64("fonts/manrope-latin-ext.woff2", "font/woff2")}') format('woff2'); unicode-range: U+0100-024F; }}
"""
PHOTO = b64("images/abend-q-1200.jpg", "image/jpeg")
LOGO = b64("images/logo-mask.png", "image/png")
ICONS = {k: b64(f"images/icons/{k}.png", "image/png") for k in ("regional", "radeln", "relaxen")}

CSS = FONTS + """
:root {
  --paper: oklch(24% 0.052 158); --paper-2: oklch(19.5% 0.045 158); --ink: oklch(93% 0.022 88);
  --ink-2: oklch(81% 0.035 150); --cream: oklch(95% 0.02 88); --cream-2: oklch(91% 0.025 88);
  --green: oklch(30% 0.055 158); --green-2: oklch(42% 0.05 158); --copper: oklch(62% 0.12 52); --copper-light: oklch(74% 0.115 58);
  --river: oklch(80% 0.03 230);
  --display: 'Prata', Georgia, serif; --body: 'Manrope', system-ui, sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: var(--body); background: oklch(60% 0 0); }
.sheet { position: relative; overflow: hidden; margin: 10mm auto; page-break-after: always; break-after: page; }
.safe { position: absolute; inset: 8mm; }
@media print { body { background: none; } .sheet { margin: 0; } .note { display: none; } }
.note { font: 12px/1.4 var(--body); color: #222; max-width: 180mm; margin: 6mm auto; }
.dark { background: var(--paper); color: var(--ink); }
.light { background: var(--cream); color: var(--green); }
h1, h2, h3 { font-family: var(--display); font-weight: 400; line-height: 1.08; }
.slogan { display: flex; gap: 5mm; list-style: none; }
.slogan li { display: grid; justify-items: center; gap: 1.2mm; font-family: var(--display); }
.slogan i { display: block; background: var(--copper-light); -webkit-mask: var(--i) center / contain no-repeat; mask: var(--i) center / contain no-repeat; }
.logo { background: var(--ink); -webkit-mask: url('LOGO') left bottom / contain no-repeat; mask: url('LOGO') left bottom / contain no-repeat; }
.qr svg { display: block; width: 100%; height: auto; }
.qr { background: white; padding: 1.6mm; border-radius: 1.5mm; }
/* map on cream */
.map svg { width: 100%; height: auto; display: block; }
.map .river { fill: none; stroke: var(--river); stroke-width: 7; stroke-linecap: round; stroke-linejoin: round; }
.map .route__hit { display: none; }
.map .route__line { fill: none; stroke: var(--copper); stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; }
.map .start circle { fill: var(--cream); stroke: var(--copper); stroke-width: 3.5; }
.map .stop circle, .map .place { fill: var(--green-2); }
.map text { font-family: var(--body); font-size: 25px; fill: var(--green); paint-order: stroke; stroke: var(--cream); stroke-width: 7px; stroke-linejoin: round; }
.map .start text { font-weight: 700; }
.map .label-country { font-size: 21px; fill: var(--green-2); }
.map .home-ring { fill: none; stroke: var(--copper); stroke-width: 2; }
.map .place--home { fill: var(--copper); }
.map .label-home { font-family: var(--display); font-size: 36px; fill: var(--green); }
""".replace("LOGO", LOGO)

ICON_STYLE = "".join(f".i-{k} {{ --i: url('{v}'); }}\n" for k, v in ICONS.items())

QR_JS = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>
<script>
document.querySelectorAll('[data-qr]').forEach(function (el) {
  var q = qrcode(0, 'M'); q.addData(el.dataset.qr); q.make();
  el.innerHTML = q.createSvgTag({ cellSize: 4, margin: 0, scalable: true });
});
</script>"""


def page(title, sheets, note, size="210mm 297mm"):
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{title}</title>
<style>@page {{ size: {size}; margin: 0; }}
{CSS}{ICON_STYLE}{sheets[1]}</style></head><body>
<p class="note">{note}</p>
{sheets[0]}
{QR_JS}
</body></html>"""


def slogan(size_icon, size_text):
    return (f'<ul class="slogan" style="font-size:{size_text}">' +
            "".join(f'<li><i class="i-{k}" style="width:{size_icon};height:{size_icon}"></i>{k.capitalize()}</li>'
                    for k in ("regional", "radeln", "relaxen")) + "</ul>")


# ---------------------------------------------------------------- A5 Routenflyer
routes = "".join(
    f'<li><span class="r-name">{S.ROUTES[k]["name"]}</span><span class="r-km">ca. {S.de(round(S.D["routes"][k]["km"]))} km</span></li>'
    for k in S.KEYS)
a5 = f"""
<section class="sheet a5 dark">
  <div class="a5-photo" style="background-image:url('{PHOTO}')"></div>
  <div class="a5-fade"></div>
  <div class="safe a5-front">
    <p class="a5-word">s’Genussplatz’l</p>
    <div class="a5-bottom">
      <h1>Rasten unterm Nussbaum.</h1>
      <p class="a5-lead">Eine Oase der Entspannung in der Toskana der Steiermark, mitten im Thermen- &amp; Vulkanland.</p>
      {slogan("9mm", "11pt")}
      <p class="a5-meta">Unterpurkla 28, 8484 Halbenrain, direkt am Gleichenberger Radweg R45<br>März bis Oktober, täglich 9 bis 22 Uhr</p>
    </div>
  </div>
</section>
<section class="sheet a5 light">
  <div class="safe a5-back">
    <h2>Fünf Radwege zu uns.</h2>
    <p class="a5-sub">Aus allen Himmelsrichtungen führt ein Radweg zum Genussplatzl. Routen mit Höhenprofil, GPX-Download und Komoot-Link auf unserer Website.</p>
    <div class="map">{S.overview_map()}</div>
    <ul class="a5-routes">{routes}</ul>
    <div class="a5-foot">
      <div class="qr" data-qr="{QR['routen']}"></div>
      <div>
        <p class="a5-cta">Alle Routen, GPX und Komoot</p>
        <p class="a5-url">s-genussplatzl.at</p>
        <p class="a5-small">E-Bike laden kostenlos, WC, Schatten unterm Nussbaum, klimatisierter Raum an heißen Tagen. Regionale Weine von Winzern aus Klöch und Tieschen.</p>
      </div>
    </div>
  </div>
</section>"""
a5_css = """
.a5 { width: 154mm; height: 216mm; }
.a5-photo { position: absolute; inset: 0 0 auto 0; height: 150mm; background-size: cover; background-position: 50% 8%; }
.a5-fade { position: absolute; inset: 0; background: linear-gradient(to bottom, oklch(24% 0.052 158 / 0.55) 0%, transparent 18%, transparent 46%, var(--paper) 70%); }
.a5-front { display: flex; flex-direction: column; justify-content: space-between; }
.a5-word { font-family: var(--display); font-size: 15pt; }
.a5-bottom { display: grid; gap: 4mm; }
.a5-front h1 { font-size: 34pt; max-width: 11ch; }
.a5-lead { font-size: 11pt; line-height: 1.45; color: var(--ink-2); max-width: 46ch; }
.a5-meta { font-size: 8.5pt; line-height: 1.5; color: var(--ink-2); border-top: 0.3mm solid var(--copper-light); padding-top: 3mm; }
.a5-back { display: flex; flex-direction: column; gap: 3mm; }
.a5-back h2 { font-size: 22pt; }
.a5-sub { font-size: 8.5pt; line-height: 1.45; max-width: 60ch; }
.a5-back .map { background: var(--cream-2); border-radius: 2mm; padding: 1.5mm; }
.a5-routes { list-style: none; display: grid; gap: 1mm; border-top: 0.4mm solid var(--copper); padding-top: 2mm; }
.a5-routes li { display: flex; justify-content: space-between; font-size: 9pt; border-bottom: 0.2mm solid oklch(80% 0.03 120); padding-bottom: 1mm; }
.a5-routes .r-name { font-family: var(--display); font-size: 10.5pt; }
.a5-routes .r-km { color: var(--copper); font-weight: 700; }
.a5-foot { margin-top: auto; display: grid; grid-template-columns: 26mm 1fr; gap: 4mm; align-items: center; }
.a5-cta { font-size: 9pt; font-weight: 700; }
.a5-url { font-family: var(--display); font-size: 15pt; color: var(--copper); }
.a5-small { font-size: 7.5pt; line-height: 1.45; margin-top: 1mm; }
"""
(DEST / "flyer-a5-radrouten.html").write_text(page("Flyer A5 Radrouten", (a5, a5_css),
    "Flyer A5 hochkant, beidseitig, 148 × 210 mm, mit 3 mm Beschnitt (154 × 216 mm). Graue Fläche und dieser Text werden nicht gedruckt.", "154mm 216mm"), encoding="utf-8")

# ---------------------------------------------------------------- A6 Postkarte (Hotels, Thermen)
a6 = f"""
<section class="sheet a6 dark">
  <div class="a6-photo" style="background-image:url('{PHOTO}')"></div>
  <div class="a6-fade"></div>
  <div class="safe a6-front"><div class="logo a6-logo" role="img" aria-label="Logo s’Genussplatz’l"></div></div>
</section>
<section class="sheet a6 light">
  <div class="safe a6-back">
    <h2>Ihr Ausflug mit dem Rad.</h2>
    <p>Rast unterm Nussbaum, regionale Getränke und Kunst im Garten, am Gleichenberger Radweg R45 in Unterpurkla.</p>
    <ul class="a6-dist">
      <li><span>Bad Radkersburg</span><b>12 km</b></li>
      <li><span>Bad Gleichenberg</span><b>20 km</b></li>
      <li><span>Klöch</span><b>8 km</b></li>
    </ul>
    <div class="map a6-map">{S.overview_map()}</div>
    <p class="a6-small">E-Bike laden kostenlos, WC, klimatisierter Raum. März bis Oktober, täglich 9 bis 22 Uhr. Fünf Radrouten mit GPX und Komoot auf unserer Website.</p>
    <div class="a6-foot"><div class="qr" data-qr="{QR['postkarte']}"></div><div><p class="a6-url">s-genussplatzl.at</p><p class="a6-small">Unterpurkla 28<br>8484 Halbenrain</p></div></div>
  </div>
</section>"""
a6_css = """
.a6 { width: 111mm; height: 154mm; }
.a6-photo { position: absolute; inset: 0; background-size: cover; background-position: 50% 30%; }
.a6-fade { position: absolute; inset: 0; background: linear-gradient(to top, oklch(24% 0.052 158 / 0.92) 0%, oklch(24% 0.052 158 / 0.4) 38%, transparent 60%); }
.a6-front { display: flex; align-items: flex-end; }
.a6-logo { width: 62mm; aspect-ratio: 640 / 502; }
.a6-back { display: flex; flex-direction: column; gap: 2.4mm; font-size: 9pt; line-height: 1.45; }
.a6-back h2 { font-size: 19pt; }
.a6-dist { list-style: none; border-top: 0.4mm solid var(--copper); }
.a6-dist li { display: flex; justify-content: space-between; padding: 1mm 0; border-bottom: 0.2mm solid oklch(80% 0.03 120); }
.a6-dist b { color: var(--copper); }
.a6-small { font-size: 7.5pt; }
.a6-map { background: var(--cream-2); border-radius: 2mm; padding: 1mm; }
.a6-map svg { height: 46mm; width: auto; max-width: 100%; margin: 0 auto; }
.a6-map text { font-size: 24px; }
.a6-map .label-home { font-size: 32px; }
.a6-map .label-country { display: none; }
.a6-foot { margin-top: auto; display: grid; grid-template-columns: 24mm 1fr; gap: 4mm; align-items: center; }
.a6-url { font-family: var(--display); font-size: 13pt; color: var(--copper); }
"""
(DEST / "postkarte-a6-hotels.html").write_text(page("Postkarte A6 Hotels", (a6, a6_css),
    "Postkarte A6 hochkant, beidseitig, 105 × 148 mm, mit 3 mm Beschnitt (111 × 154 mm). Für Rezeptionen von Thermen, Hotels und Tourismusbüros.", "111mm 154mm"), encoding="utf-8")

# ---------------------------------------------------------------- A6 QR-Schild vor Ort
sign = f"""
<section class="sheet a6 light">
  <div class="safe sign">
    <div class="sign-block">
      <h2>Hat’s Ihnen gefallen?</h2>
      <p>Wir freuen uns über Ihre Bewertung auf Google.</p>
      <div class="qr sign-qr" data-qr="{QR['bewertung']}"></div>
    </div>
    <div class="sign-block">
      <h2>Weiterradeln?</h2>
      <p>Radrouten, GPX und E-Bike-Infos</p>
      <div class="qr sign-qr" data-qr="{QR['schild']}"></div>
    </div>
    <p class="sign-url">s-genussplatzl.at</p>
  </div>
</section>"""
sign_css = """
.sign { display: grid; grid-template-rows: 1fr 1fr auto; gap: 4mm; text-align: center; }
.sign-block { display: grid; justify-items: center; align-content: center; gap: 1.5mm; border-bottom: 0.3mm solid var(--copper); padding-bottom: 3mm; }
.sign-block h2 { font-size: 17pt; }
.sign-block p { font-size: 8.5pt; }
.sign-qr { width: 33mm; margin-top: 1mm; }
.sign-url { font-family: var(--display); font-size: 12pt; color: var(--copper); }
"""
(DEST / "qr-schild-a6-vor-ort.html").write_text(page("QR-Schild A6", (sign, a6_css + sign_css),
    "QR-Schild A6 hochkant, einseitig, 105 × 148 mm mit 3 mm Beschnitt. Für einen Acryl-Aufsteller am Tisch oder an der Theke.", "111mm 154mm"), encoding="utf-8")

# ---------------------------------------------------------------- QR-Codes einzeln (für Druckerei/Grafik)
qr_list = "".join(f'<figure><div class="qr" data-qr="{u}" data-name="{k}"></div><figcaption><b>{k}</b><br>{u}</figcaption></figure>' for k, u in QR.items())
qr_css = "figure { width: 60mm; margin: 6mm; display: inline-block; vertical-align: top; font: 9px/1.4 var(--body); color:#222; word-break: break-all; } .qr { margin-bottom: 2mm; }"
(DEST / "qr-codes.html").write_text(page("QR-Codes", (f'<section style="background:white;padding:8mm;max-width:210mm;margin:auto">{qr_list}</section>', qr_css),
    "Alle QR-Codes mit Ziel-Adresse. Die Kennung utm_source zeigt in Umami, über welches Druckstück jemand kam."), encoding="utf-8")
print("geschrieben:", ", ".join(p.name for p in DEST.glob("*.html")))
