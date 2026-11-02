"""Frankie's world: watch creatures live in a 3D world, in your browser.

    uv run python life/lab.py [--port 8770] [--no-browser] [--seed N] [--creature frankie]

It serves a page on this computer only (127.0.0.1) and opens it in your
browser. The world runs live until you press Pause; when every creature in
it has died, a fresh random world starts (unless you turn that off). It uses
only Python's standard library, NumPy and the project's own code; the page
uses three.js, kept in life/web/vendor so it works offline.

Log files (for debugging) go to life/logs/:
- server.log: start-up, every control you press, every new world and seed, errors;
- events.jsonl: every eat and death, one JSON line each, with seed and tick;
- client.log: errors and notes the page itself reports.
"""

import argparse
import json
import logging
import logging.handlers
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
ROOT = HERE.parent
if sys.path and pathlib.Path(sys.path[0]).resolve() == HERE:
    sys.path.pop(0)                                  # keep life/ itself off the path (its world3d is not src/world)
sys.path.insert(0, str(ROOT))

from life import config as C  # noqa: E402
from life import sim  # noqa: E402

WEB = HERE / "web"
LOGS = HERE / "logs"
RESULTS = HERE / "results"
SPEEDS = (1, 2, 5, 10, 20, 50, 100)

log = logging.getLogger("life")
events_log = logging.getLogger("life.events")
client_log = logging.getLogger("life.client")


def setup_logging(folder=LOGS):
    folder.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for logger, name, plain in ((log, "server.log", False), (events_log, "events.jsonl", True),
                                (client_log, "client.log", False)):
        logger.setLevel(logging.INFO)
        logger.propagate = False
        for h in list(logger.handlers):
            logger.removeHandler(h)
        h = logging.handlers.RotatingFileHandler(folder / name, maxBytes=5_000_000, backupCount=3,
                                                 encoding="utf-8")
        h.setFormatter(logging.Formatter("%(message)s") if plain else fmt)
        logger.addHandler(h)


class Live:
    """The world running in the background, one tick at a time, until paused."""

    def __init__(self, seed=None, creatures=("frankie",)):
        self.lock = threading.RLock()
        self.playing = True
        self.speed = 10                  # ticks per second at normal speed
        self.fast = False                # fast forward: as fast as the computer goes
        self.auto_restart = True
        self.creatures = list(creatures)
        self.session = None
        self.lives = 0
        self.dead_since = None
        self.error = None
        self.new_world(seed)
        self.thread = threading.Thread(target=self._loop, daemon=True, name="life-loop")
        self.stop = threading.Event()

    def start(self):
        self.thread.start()

    def new_world(self, seed=None, creatures=None):
        with self.lock:
            if creatures:
                self.creatures = list(creatures)
            self.session = sim.Session(seed, self.creatures)
            self.lives += 1
            self.dead_since = None
            w = self.session.world
            log.info("new world seed=%s creatures=%s obstacles=%s fences=%d walls=%d river=%s objects=%d",
                     self.session.seed, ",".join(self.creatures), w.obstacles.any, len(w.obstacles.fences),
                     len(w.obstacles.walls), w.obstacles.river is not None, len(w.ecology.alive()))
            events_log.info(json.dumps({"t": time.time(), "event": "world", "seed": self.session.seed,
                                        "creatures": self.creatures}))

    def step_once(self):
        with self.lock:
            s = self.session
            if s.all_dead():
                return
            for ev in s.step():
                events_log.info(json.dumps(dict(ev, t=round(time.time(), 3), seed=s.seed), default=list))
            if s.all_dead():
                self.dead_since = time.time()
                for c in s.creatures:
                    r = c.rec.summary(c.mind)
                    log.info("life over seed=%s creature=%s lifespan=%d food=%d poison=%d nothing=%d looks=%d "
                             "bumps=%s", s.seed, c.name, r["lifespan"], r["food"], r["poison"], r["nothing"],
                             r["looks"], r["bumps"])

    def _loop(self):
        next_t = time.perf_counter()
        while not self.stop.is_set():
            try:
                if not self.playing:
                    time.sleep(0.05)
                    next_t = time.perf_counter()
                    continue
                if self.session.all_dead():
                    if self.auto_restart and self.dead_since and time.time() - self.dead_since > 3.0:
                        self.new_world()
                    time.sleep(0.05)
                    continue
                if self.session.tick >= C.MAX_TICKS * 10:      # a very long life: start afresh
                    log.info("life capped at %d ticks, seed=%s", self.session.tick, self.session.seed)
                    self.new_world()
                if self.fast:
                    end = time.perf_counter() + 0.05
                    while time.perf_counter() < end and not self.session.all_dead():
                        self.step_once()
                    time.sleep(0.005)
                    next_t = time.perf_counter()
                    continue
                self.step_once()
                next_t += 1.0 / self.speed
                pause = next_t - time.perf_counter()
                if pause > 0:
                    time.sleep(pause)
                else:
                    next_t = time.perf_counter()
            except Exception as e:                            # logged, shown on the page, and the world paused
                self.error = f"{type(e).__name__}: {e}"
                self.playing = False
                log.error("simulation error (paused): %s\n%s", self.error, traceback.format_exc())

    def control(self, cmd):
        c = cmd.get("cmd")
        with self.lock:
            if c == "play":
                self.playing, self.error = True, None
            elif c == "pause":
                self.playing = False
            elif c == "step":
                self.playing = False
                for _ in range(max(1, min(int(cmd.get("n", 1)), 1000))):
                    self.step_once()
            elif c == "speed":
                v = int(cmd.get("value", 10))
                self.speed = v if v in SPEEDS else 10
            elif c == "fast":
                self.fast = bool(cmd.get("value"))
            elif c == "auto":
                self.auto_restart = bool(cmd.get("value"))
            elif c == "new":
                seed = cmd.get("seed")
                seed = int(seed) if seed not in (None, "") else None
                creatures = [n for n in cmd.get("creatures", []) if n in sim.CREATURES][:2] or None
                self.new_world(seed, creatures)
            elif c == "restart":
                self.new_world(self.session.seed)
            else:
                raise ValueError(f"unknown command {c!r}")
            log.info("control %s", json.dumps(cmd))
            return self.status()

    def status(self):
        return {"playing": self.playing, "speed": self.speed, "fast": self.fast, "auto": self.auto_restart,
                "lives": self.lives, "error": self.error, "creatures_running": self.creatures}


LIVE = None


def results():
    p = RESULTS / "batch.json"
    if not p.exists():
        return {"runs": 0}
    return json.loads(p.read_text())


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB), **k)

    def log_message(self, fmt, *args):
        pass

    def log_error(self, fmt, *args):
        log.warning("http: " + fmt, *args)

    def end_headers(self):
        if not self.path.startswith("/vendor/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _json(self, obj, status=HTTPStatus.OK):
        body = json.dumps(obj, separators=(",", ":"), default=list).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        try:
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 1_000_000:
            raise ValueError("request too large")
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw or b"{}")

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(url.query))
        try:
            if url.path == "/api/world":
                with LIVE.lock:
                    out = LIVE.session.world.static()
                    out["view"] = {"range": C.VIEW_RANGE, "half_angle_deg": C.VIEW_HALF_ANGLE_DEG,
                                   "eye": C.EYE_HEIGHT, "sharp_range": C.SHARP_RANGE}
                    out["energy_max"] = C.ENERGY_MAX
                return self._json(out)
            if url.path == "/api/state":
                known = int(q.get("objects", -1))
                with LIVE.lock:
                    s = LIVE.session
                    out = s.state(with_objects=known != s.world.ecology.version)
                    out["live"] = LIVE.status()
                return self._json(out)
            if url.path == "/api/creatures":
                return self._json({n: {"label": v["label"], "colour": v["colour"]} for n, v in sim.CREATURES.items()})
            if url.path == "/api/results":
                return self._json(results())
            if url.path == "/api/health":
                return self._json({"ok": True})
        except Exception as e:
            log.error("GET %s failed: %s\n%s", url.path, e, traceback.format_exc())
            return self._json({"error": f"{type(e).__name__}: {e}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
        return super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        try:
            body = self._body()
            if url.path == "/api/control":
                return self._json(LIVE.control(body))
            if url.path == "/api/log":
                client_log.info("%s %s", str(body.get("level", "info")).upper(),
                                json.dumps(body, separators=(",", ":"))[:4000])
                return self._json({"ok": True})
        except Exception as e:
            log.error("POST %s failed: %s\n%s", url.path, e, traceback.format_exc())
            return self._json({"error": f"{type(e).__name__}: {e}"}, HTTPStatus.BAD_REQUEST)
        return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)


def serve(port=8770, tries=20):
    for p in range(port, port + tries):
        try:
            return ThreadingHTTPServer(("127.0.0.1", p), Handler)
        except OSError:
            continue
    raise SystemExit(f"no free port between {port} and {port + tries - 1}")


def main(argv=None) -> int:
    global LIVE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--seed", type=int, default=None, help="start with this world (default: a fresh random one)")
    ap.add_argument("--creature", action="append", default=None,
                    help="creature to run (repeat for two side by side); default frankie")
    ap.add_argument("--paused", action="store_true", help="start paused")
    a = ap.parse_args(argv)
    setup_logging()
    sim._load_minds()
    creatures = a.creature or (["frankie"] if "frankie" in sim.CREATURES else ["wanderer"])
    LIVE = Live(a.seed, creatures)
    LIVE.playing = not a.paused
    server = serve(a.port)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    log.info("serving %s (pid %d)", url, __import__("os").getpid())
    LIVE.start()
    print(f"Frankie's world is running at {url}\nLeave this window open while you watch. Press Ctrl+C to stop.\n"
          f"Logs: {LOGS}", flush=True)
    if not a.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        LIVE.stop.set()
        server.server_close()
        log.info("stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
