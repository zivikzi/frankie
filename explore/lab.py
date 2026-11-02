"""Frankie Lab: watch a mind think, and compare minds, in your browser.

    uv run python explore/lab.py [--port 8765] [--no-browser]

It serves a page on this computer only (127.0.0.1) and opens it in your
browser. Nothing is sent anywhere else. It uses only Python's standard
library and the project's own code: no new packages.

The page has three views:

- Watch a run: pick a mind, a family and a run, and step through it decision
  by decision: the object drawn as a picture, its numbers layer by layer, the
  kinds the mind considered and where each was ruled out, its verdict and
  choice, its energy, and its memory.
- Scoreboard: every mind's key measures against the kill test's pass marks,
  on the search half (odd families) and the check half (even families), and
  the learning curve.
- Variants: every E1 variant tried, with its numbers.

Runs the page asks for that are not saved yet are worked out on the spot
(a second or two; K-F takes about ten, mostly the first time).
"""

import argparse
import json
import pathlib
import sys
import threading
import time
import traceback
import urllib.parse
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import minds  # noqa: E402
import runtrace  # noqa: E402

WEB = HERE / "web"
RESULTS = HERE / "results"
SHOWN = ("B1n-bot-r", "B1n-mind", "B2e", "K-F")
BATCH = {"running": False, "mind": None, "half": None, "done": 0, "total": 0, "error": None, "finished_at": None}
LOCK = threading.Lock()


def meta():
    variants = list(minds.VARIANTS)
    return {"minds": list(SHOWN) + variants, "variants": minds.VARIANTS,
            "families": [{"n": f, "half": "search half (odd)" if f % 2 else "check half (even)"} for f in range(1, 31)],
            "runs": list(range(1, minds.RUNS + 1)), "traits": list(runtrace.traits.TRAITS),
            "layers": runtrace.LAYER_SPANS}


def scoreboard():
    p = RESULTS / "scoreboard.json"
    if not p.exists():
        return {"halves": {}}
    board = json.loads(p.read_text())
    board.pop("runs", None)                       # the per-run numbers stay on disk
    return board


def variants_log():
    p = RESULTS / "variants.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def run_batch(mind, half):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    fams = minds.ODD if half == "odd" else minds.EVEN
    jobs = [(mind, None, f, r) for f in fams for r in range(1, minds.RUNS + 1)]
    with LOCK:
        BATCH.update(running=True, mind=mind, half=half, done=0, total=len(jobs), error=None, finished_at=None)
    try:
        runs = {}
        with ProcessPoolExecutor() as pool:
            futures = [pool.submit(minds.one, j) for j in jobs]
            for fut in as_completed(futures):
                _, f, r, _, m = fut.result()
                runs[(f, r)] = m
                with LOCK:
                    BATCH["done"] += 1
        tower = minds.spec(mind).mind_class == "tower"
        s = minds.summary(runs, tower)
        p = RESULTS / "scoreboard.json"
        board = json.loads(p.read_text()) if p.exists() else {"halves": {}}
        board.setdefault("halves", {}).setdefault(half, {})[mind] = s
        h = board["halves"][half]
        h["floor"] = max(h.get("B1n-bot-r", {}).get("d_learn", float("-inf")),
                         h.get("B1n-mind", {}).get("d_learn", float("-inf")))
        RESULTS.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(board, indent=1, sort_keys=True) + "\n")
    except Exception as e:                                     # shown on the page, never hidden
        with LOCK:
            BATCH["error"] = f"{type(e).__name__}: {e}"
    finally:
        with LOCK:
            BATCH.update(running=False, finished_at=time.strftime("%H:%M:%S"))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB), **k)

    def log_message(self, fmt, *args):            # keep the terminal quiet
        pass

    def _json(self, obj, status=HTTPStatus.OK):
        body = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        try:
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):       # the page went away mid-answer: nothing to do
            pass

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(url.query))
        try:
            if url.path == "/api/meta":
                return self._json(meta())
            if url.path == "/api/trace":
                mind, family, run = q.get("mind", "E1"), int(q.get("family", 1)), int(q.get("run", 1))
                if mind not in meta()["minds"] or not 1 <= family <= 30 or not 1 <= run <= minds.RUNS:
                    return self._json({"error": "unknown mind, family or run"}, HTTPStatus.BAD_REQUEST)
                return self._json(runtrace.get(mind, family, run))
            if url.path == "/api/scoreboard":
                return self._json(scoreboard())
            if url.path == "/api/variants":
                return self._json(variants_log())
            if url.path == "/api/batch":
                with LOCK:
                    return self._json(dict(BATCH))
        except Exception as e:
            return self._json({"error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-1500:]},
                              HTTPStatus.INTERNAL_SERVER_ERROR)
        return super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(url.query))
        if url.path == "/api/batch":
            mind, half = q.get("mind", ""), q.get("half", "odd")
            if mind not in meta()["minds"] or half not in ("odd", "even"):
                return self._json({"error": "unknown mind or half"}, HTTPStatus.BAD_REQUEST)
            with LOCK:
                if BATCH["running"]:
                    return self._json({"error": "a batch is already running"}, HTTPStatus.CONFLICT)
            threading.Thread(target=run_batch, args=(mind, half), daemon=True).start()
            return self._json({"started": True})
        return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)


def serve(port=8765, open_browser=True, tries=20):
    for p in range(port, port + tries):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", p), Handler)
            break
        except OSError:
            continue
    else:
        raise SystemExit(f"no free port between {port} and {port + tries - 1}")
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Frankie Lab is running at {url}\nLeave this window open while you use it. Press Ctrl+C to stop.",
          flush=True)
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    return server, url


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args(argv)
    server, _ = serve(a.port, not a.no_browser)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
