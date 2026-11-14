"""Lokale Vorschau mit einem Farbthema, ohne die Website zu ändern.

  python tools/preview.py 8778 themes/basalt.css
  python tools/preview.py 8779 themes/kies.css

Liefert die Website aus und hängt das Thema an styles.css an. Nichts wird zwischengespeichert.
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
port = int(sys.argv[1])
theme = ROOT / sys.argv[2] if len(sys.argv) > 2 else None


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if theme and self.path.split("?")[0].endswith("/styles.css"):
            body = ((ROOT / "styles.css").read_text(encoding="utf-8") + chr(10) + theme.read_text(encoding="utf-8")).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *a):
        pass


ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(ROOT))).serve_forever()
