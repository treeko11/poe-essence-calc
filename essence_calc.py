"""
Path of Exile essence upgrade calculator - local version with live prices.

Run:  python essence_calc.py        (opens http://127.0.0.1:8765 in your browser)

Serves index.html and proxies poe.ninja (5-minute cache), using the same
data paths as the GitHub Pages build, so prices are always current.
Only uses the Python standard library.
"""
import json
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from build_data import HERE, get_essences, get_leagues

PORT = 8765
CACHE_SECONDS = 300
_cache = {}
_lock = threading.Lock()


def cached(key, fn):
    with _lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < CACHE_SECONDS:
            return hit[1]
    val = fn()
    with _lock:
        _cache[key] = (time.time(), val)
    return val


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, code, body, ctype):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        try:
            if path in ("/", "/index.html"):
                self.send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif path == "/data/leagues.json":
                self.send(200, json.dumps(cached("leagues", get_leagues)), "application/json")
            elif path.startswith("/data/essences/") and path.endswith(".json"):
                slug = urllib.parse.unquote(path[len("/data/essences/"):-len(".json")])
                league = next((l for l in cached("leagues", get_leagues) if l["url"] == slug), None)
                if not league:
                    return self.send(404, "unknown league", "text/plain")
                d = cached("ess:" + slug, lambda: get_essences(league["name"]))
                self.send(200, json.dumps(d), "application/json")
            else:
                self.send(404, "not found", "text/plain")
        except Exception as e:  # surface upstream errors to the page
            self.send(502, json.dumps({"error": str(e)}), "application/json")


if __name__ == "__main__":
    # On Windows, address reuse lets a second copy bind the same port silently; refuse instead.
    ThreadingHTTPServer.allow_reuse_address = sys.platform != "win32"
    url = f"http://127.0.0.1:{PORT}/"
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"Port {PORT} is busy - is the calculator already running? Opening it instead.")
        webbrowser.open(url)
        sys.exit(0)
    print(f"Essence calculator running at {url}  (Ctrl+C to stop)")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
