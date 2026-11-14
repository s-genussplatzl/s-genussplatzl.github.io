"""Exportiert die gebaute Website in einen Ordner, der per Doppelklick (file://) funktioniert.

  python tools/export.py <zielordner>

CSS, Schriften und Slogan-Symbole werden in jede Seite eingebettet (Browser blockieren
Schriften und Masken über file://), Bilder, GPX und Skript werden kopiert.
"""
import base64
import re
import shutil
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
dest = Path(sys.argv[1])
MIME = {".woff2": "font/woff2", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml"}


def data_uri(p):
    return f"data:{MIME[p.suffix]};base64," + base64.b64encode(p.read_bytes()).decode()


def css_inline(path):
    css = path.read_text(encoding="utf-8")
    css = re.sub(r'@import url\("\./([^"]+)"\);', lambda m: css_inline(root / m.group(1)), css)
    return re.sub(r"""url\(["']?((?:fonts|images)/[^"')]+)["']?\)""", lambda m: f'url("{data_uri(root / m.group(1))}")', css)


if dest.exists():
    shutil.rmtree(dest)
dest.mkdir(parents=True)
style = "<style>\n" + css_inline(root / "styles.css") + "\n</style>"
pages = []
for base in [root] + [root / l for l in ("sl", "en", "hu") if (root / l / "index.html").exists()]:
    pages += [base / "index.html", base / "e-bike-laden.html", base / "bike-and-spa.html", base / "datenschutz.html"] + sorted((base / "radrouten").glob("*.html"))
for page in pages:
    if not page.exists():
        continue
    html = page.read_text(encoding="utf-8")
    html = re.sub(r'<link rel="preload"[^>]*>\n?', "", html)
    html = re.sub(r'<link rel="stylesheet" href="(\.\./)*styles\.css">', lambda m: style, html)
    out = dest / page.relative_to(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
for d in ("images", "gpx"):
    shutil.copytree(root / d, dest / d)
shutil.copy(root / "site.js", dest / "site.js")
size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
print(dest, len(pages), "Seiten,", round(size / 1e6, 1), "MB")
