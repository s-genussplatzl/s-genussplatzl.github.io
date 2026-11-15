"""Faltflyer DIN lang, 6 Seiten, Wickelfalz (99 x 210 mm geschlossen, 297 x 210 mm offen).

  python tools/print_dl.py <zielordner>

Erzeugt faltflyer-din-lang.html (2 Bogenseiten mit 3 mm Beschnitt, 303 x 216 mm).
PDF: Chrome headless --print-to-pdf (siehe Konzept). QR-Codes: qrcode-generator (cdnjs).

Aufbau (Wickelfalz, Seitenbreiten 97/100/100):
  Aussen:  [Klappe 97] [Rueckseite 100] [Titel 100]
  Innen:   [Geschichte 100] [Karte 100] [Routen + QR 97]
"""
import base64
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gp_site", Path(__file__).resolve().parent / "site.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
S.set_lang("de")

ROOT = S.ROOT
DEST = Path(sys.argv[1])
DEST.mkdir(parents=True, exist_ok=True)

QR = {
    "routen": "https://s-genussplatzl.at/?utm_source=faltflyer&utm_campaign=routen#umgebung",
    "komoot": "https://www.komoot.com/de-de/highlight/8495359",
    "maps": "https://maps.google.com/?cid=5193859400819937139",
}


def b64(p, mime="image/jpeg"):
    return f"data:{mime};base64," + base64.b64encode((ROOT / p).read_bytes()).decode()


IMG = {
    "titel": b64("images/abend-q-1600.jpg"),
    "nussbaum": b64("images/nussbaum-800.jpg"),
    "pavillon": b64("images/pavillon-800.jpg"),
    "rad": b64("images/radstation-800.jpg"),
    "sitz": b64("images/sitzplaetze-800.jpg"),
    "logo": b64("images/logo-mask.png", "image/png"),
}
ICON = {k: b64(f"images/icons/{k}.png", "image/png") for k in ("regional", "radeln", "relaxen")}

AT = [k for k in S.KEYS if k not in ("sued", "maribor", "ptuj", "banovci", "moravske")]
SI = [k for k in S.KEYS if k not in AT]


def rows(keys):
    out = []
    for k in keys:
        name = S.TR[k]["name"].replace(" in Slowenien", "")
        out.append(f'<li><span>{name}</span><b>{S.approx_km(k).replace("ca. ", "")}</b></li>')
    return "".join(out)


slogan = "".join(f'<li><i style="--i:url(\'{ICON[k]}\')"></i>{k.capitalize()}</li>' for k in ("regional", "radeln", "relaxen"))

HTML = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Faltflyer DIN lang</title>
<style>
@page {{ size: 303mm 216mm; margin: 0; }}
@font-face {{ font-family: 'Prata'; src: url('{b64("fonts/prata-latin.woff2", "font/woff2")}') format('woff2'); }}
@font-face {{ font-family: 'Manrope'; font-weight: 400 700; src: url('{b64("fonts/manrope-latin.woff2", "font/woff2")}') format('woff2'); }}
@font-face {{ font-family: 'Manrope'; font-weight: 400 700; src: url('{b64("fonts/manrope-latin-ext.woff2", "font/woff2")}') format('woff2'); unicode-range: U+0100-024F; }}
:root {{
  --paper: oklch(24% 0.052 158); --ink: oklch(93% 0.022 88); --ink-2: oklch(81% 0.035 150);
  --cream: oklch(95% 0.02 88); --cream-2: oklch(91% 0.025 88); --green: oklch(30% 0.055 158); --green-2: oklch(45% 0.05 158);
  --copper: oklch(62% 0.12 52); --copper-light: oklch(74% 0.115 58); --river: oklch(80% 0.03 230); --rule: oklch(82% 0.03 120);
  --display: 'Prata', Georgia, serif; --body: 'Manrope', system-ui, sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: var(--body); background: oklch(55% 0 0); color: var(--green); }}
.note {{ font: 12px/1.5 var(--body); color: #111; max-width: 303mm; margin: 6mm auto; }}
.sheet {{ position: relative; width: 303mm; height: 216mm; margin: 8mm auto; overflow: hidden; background: var(--cream); break-after: page; }}
@media print {{ body {{ background: none; }} .note, .fold {{ display: none; }} .sheet {{ margin: 0; }} }}
/* panels: x in trim coordinates + 3 mm bleed offset */
.p {{ position: absolute; top: 0; bottom: 0; overflow: hidden; }}
.inner {{ position: absolute; inset: 9mm 6mm 8mm 6mm; display: flex; flex-direction: column; }}
.fold {{ position: absolute; top: 0; bottom: 0; width: 0; border-left: 0.2mm dashed oklch(60% 0.15 25); z-index: 9; }}
h1, h2, h3 {{ font-family: var(--display); font-weight: 400; line-height: 1.08; }}
h2 {{ font-size: 18pt; }}
p {{ font-size: 8.6pt; line-height: 1.5; }}
.rule {{ border-top: 0.4mm solid var(--copper); }}
.qr {{ background: white; padding: 1.3mm; border-radius: 1.4mm; }}
.qr svg {{ display: block; width: 100%; height: auto; }}
.qrrow {{ display: grid; grid-template-columns: 21mm 1fr; gap: 3mm; align-items: center; }}
.qrrow b {{ display: block; font-size: 8.6pt; }}
.qrrow span {{ font-size: 7.4pt; color: var(--green-2); }}
.photo {{ background-size: cover; background-position: center; border-radius: 1.5mm; }}
.slogan {{ display: flex; gap: 6mm; list-style: none; }}
.slogan li {{ display: grid; justify-items: center; gap: 1mm; font-family: var(--display); font-size: 9.5pt; }}
.slogan i {{ display: block; width: 8mm; height: 8mm; background: var(--copper-light); -webkit-mask: var(--i) center / contain no-repeat; mask: var(--i) center / contain no-repeat; }}
/* title */
.title {{ background: var(--paper); color: var(--ink); }}
.title .bg {{ position: absolute; inset: 0 0 auto 0; height: 128mm; background: url('{IMG["titel"]}') 50% 6% / cover; }}
.title .shade {{ position: absolute; inset: 0; background: linear-gradient(to bottom, oklch(24% 0.052 158 / 0.5) 0%, transparent 16%, transparent 40%, var(--paper) 60%); }}
.title .inner {{ justify-content: space-between; }}
.title .word {{ font-family: var(--display); font-size: 12pt; }}
.title .logo {{ width: 52mm; aspect-ratio: 640 / 502; background: var(--ink); -webkit-mask: url('{IMG["logo"]}') left bottom / contain no-repeat; mask: url('{IMG["logo"]}') left bottom / contain no-repeat; }}
.title h1 {{ font-size: 24pt; margin-top: 4mm; }}
.title .sub {{ color: var(--ink-2); margin-top: 2.5mm; }}
/* lists */
.amen {{ list-style: none; margin-top: 3mm; }}
.amen li {{ font-size: 8.8pt; padding: 1.7mm 0; border-bottom: 0.2mm solid var(--rule); }}
.amen li b {{ font-family: var(--display); font-weight: 400; font-size: 10.5pt; display: block; }}
.routes {{ list-style: none; }}
.routes li {{ display: flex; justify-content: space-between; gap: 2mm; font-size: 7.9pt; padding: 1.15mm 0; border-bottom: 0.2mm solid var(--rule); }}
.routes b {{ color: var(--copper); white-space: nowrap; }}
.group {{ font-family: var(--display); font-size: 10pt; margin: 3mm 0 1mm; }}
/* map */
.map {{ background: var(--cream-2); border-radius: 1.5mm; padding: 1mm; }}
.map svg {{ width: 100%; height: auto; display: block; }}
.map .river {{ fill: none; stroke: var(--river); stroke-width: 7; stroke-linecap: round; stroke-linejoin: round; }}
.map .route__hit {{ display: none; }}
.map .route__line {{ fill: none; stroke: var(--copper); stroke-width: 5.5; stroke-linecap: round; stroke-linejoin: round; }}
.map .start circle {{ fill: var(--cream); stroke: var(--copper); stroke-width: 4; }}
.map .stop circle, .map .place {{ fill: var(--green-2); }}
.map text {{ font-family: var(--body); font-size: 30px; fill: var(--green); paint-order: stroke; stroke: var(--cream-2); stroke-width: 8px; stroke-linejoin: round; }}
.map .start text {{ font-weight: 700; }}
.map .label-country {{ font-size: 26px; fill: var(--green-2); }}
.map .home-ring {{ fill: none; stroke: var(--copper); stroke-width: 2.5; }}
.map .place--home {{ fill: var(--copper); }}
.map .label-home {{ font-family: var(--display); font-size: 42px; fill: var(--green); }}
.small {{ font-size: 7.4pt; color: var(--green-2); }}
.back .qrrow + .qrrow {{ margin-top: 3mm; }}
</style></head><body>
<p class="note">Faltflyer DIN lang, 6 Seiten, Wickelfalz. Offen 297 × 210 mm, mit 3 mm Beschnitt 303 × 216 mm. Seitenbreiten außen 97 | 100 | 100 mm, innen 100 | 100 | 97 mm (die schmale Seite wird nach innen eingeklappt). Rote Strichlinien = Falz, werden nicht gedruckt. Graue Fläche und dieser Text werden nicht gedruckt.</p>

<!-- AUSSEN: Klappe | Rückseite | Titel -->
<section class="sheet">
  <div class="p" style="left:0;width:100mm">
    <div class="inner" style="left:9mm">
      <div class="photo" style="height:62mm;background-image:url('{IMG["nussbaum"]}')"></div>
      <h2 style="margin-top:5mm">Ankommen und durchatmen.</h2>
      <ul class="amen">
        <li><b>Schatten unterm Nussbaum</b>Liegestühle und Plätze im großen Garten</li>
        <li><b>E-Bike laden</b>kostenlos, mit Ihrem eigenen Ladegerät</li>
        <li><b>Abkühlen</b>klimatisierter Raum an heißen Tagen</li>
        <li><b>Kunst im Garten</b>handgeschmiedete Einzelstücke</li>
        <li><b>Regionale Getränke</b>von unseren Partner-Winzern aus Klöch und Tieschen</li>
      </ul>
    </div>
  </div>
  <div class="p back" style="left:100mm;width:100mm">
    <div class="inner">
      <h2>So finden Sie uns.</h2>
      <p style="margin-top:3mm;font-size:10pt;line-height:1.4">Unterpurkla 28<br>8484 Halbenrain</p>
      <p style="margin-top:2mm">Direkt am Gleichenberger Radweg R45, wenige Minuten vom Murradweg.</p>
      <div class="rule" style="margin:4mm 0 3mm"></div>
      <p><b>Saison</b><br>März bis Oktober, täglich 9 bis 22 Uhr</p>
      <div class="photo" style="margin-top:5mm;flex:1;min-height:40mm;background-image:url('{IMG["rad"]}')"></div>
      <div style="margin-top:5mm">
        <div class="qrrow"><div class="qr" data-qr="{QR['maps']}"></div><div><b>Route in Google Maps</b><span>Navigation zu uns starten</span></div></div>
        <div class="rule" style="margin:4mm 0 3mm"></div>
        <p class="small">info@s-genussplatzl.at<br>Instagram @s_genussplatz_l_<br>Partner von Bike &amp; Spa, der 12-Thermen-Tour<br>Website auch auf Slovenščina, English und Magyar</p>
      </div>
    </div>
  </div>
  <div class="p title" style="left:200mm;width:103mm">
    <div class="bg"></div><div class="shade"></div>
    <div class="inner" style="right:9mm">
      <p class="word">s’Genussplatz’l</p>
      <div>
        <div class="logo" role="img" aria-label="Logo"></div>
        <h1>Rasten unterm Nussbaum.</h1>
        <p class="sub">Eine Oase der Entspannung in der Toskana der Steiermark, am Gleichenberger Radweg R45 in Unterpurkla.</p>
      </div>
    </div>
  </div>
  <div class="fold" style="left:100mm"></div><div class="fold" style="left:200mm"></div>
</section>

<!-- INNEN: Geschichte | Karte | Routen -->
<section class="sheet">
  <div class="p" style="left:0;width:103mm">
    <div class="inner" style="left:9mm">
      <h2>Aus Freude am Steirerland.</h2>
      <p style="margin-top:3mm">Das s’Genussplatz’l ist aus Freude entstanden: an Begegnungen, an Genuss und an unserem grünen Steirerland. Ein Ort, an dem Radfahrer, Wanderer und Ausflügler ankommen, durchatmen und sich ein Stück Region schmecken lassen.</p>
      <p style="margin-top:2mm">Mit Stil und Liebe zum Detail: ein Rastplatz, an dem Design auf Natur trifft, umgeben von Kunst und einem großen Garten unter dem alten Nussbaum.</p>
      <div class="photo" style="margin-top:5mm;flex:1;background-image:url('{IMG["pavillon"]}')"></div>
      <ul class="slogan" style="margin-top:5mm">{slogan}</ul>
    </div>
  </div>
  <div class="p" style="left:103mm;width:100mm">
    <div class="inner">
      <h2>Radwege zu uns.</h2>
      <p style="margin-top:2mm">Aus allen Himmelsrichtungen, aus der Steiermark und aus Slowenien.</p>
      <div class="map" style="margin-top:4mm">{S.overview_map()}</div>
      <p class="group" style="margin-top:4mm">Unterwegs entdecken</p>
      <p>Die Steirerbrücke über die Mur, die Schiffsmühle in Mureck, das Weinbaugebiet rund um Klöch und die Thermen in Bad Radkersburg, Bad Gleichenberg und Moravske Toplice.</p>
      <div style="margin-top:auto">
        <div class="qrrow"><div class="qr" data-qr="{QR['routen']}"></div><div><b>Alle Routen</b><span>Karte, Höhenprofil und GPX auf s-genussplatzl.at</span></div></div>
        <div class="qrrow" style="margin-top:3mm"><div class="qr" data-qr="{QR['komoot']}"></div><div><b>Auf Komoot</b><span>Uns als Ziel in Ihre Tour übernehmen</span></div></div>
      </div>
    </div>
  </div>
  <div class="p" style="left:203mm;width:100mm">
    <div class="inner" style="right:9mm">
      <p class="group" style="margin-top:0">Österreich</p>
      <ul class="routes">{rows(AT)}</ul>
      <p class="group">Slowenien</p>
      <ul class="routes">{rows(SI)}</ul>
      <div class="photo" style="margin-top:5mm;flex:1;background-image:url('{IMG["sitz"]}')"></div>
      <p class="small" style="margin-top:2.5mm">Alle Strecken mit Fahrrad-Routing berechnet, Entfernungen bis zum Genussplatzl, gerundet.</p>
    </div>
  </div>
  <div class="fold" style="left:103mm"></div><div class="fold" style="left:203mm"></div>
</section>

<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>
<script>
document.querySelectorAll('[data-qr]').forEach(function (el) {{
  var q = qrcode(0, 'M'); q.addData(el.dataset.qr); q.make();
  el.innerHTML = q.createSvgTag({{ cellSize: 4, margin: 0, scalable: true }});
}});
</script>
</body></html>"""

(DEST / "faltflyer-din-lang.html").write_text(HTML, encoding="utf-8")
print("geschrieben:", DEST / "faltflyer-din-lang.html")
