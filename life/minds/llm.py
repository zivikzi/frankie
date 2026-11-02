"""The LLM creature: one more opponent to race against Frankie (later, optional). Every choice here is untested.

This is not Frankie. Frankie's mind never uses a language model; this is a
separate creature with the same body and the same senses, whose choices
come from an LLM, so the two can be raced in the same worlds.

- Same senses, as neutral numbers. At each decision the LLM is told, as
  text: its energy and reserve, what is in its blurry view (distance,
  bearing and 6 numbers per object), what a sharp look showed (18
  numbers), and the energy change and 4 taste numbers after each eat.
  Nothing is named: no "apple", "poison", "forest" or "red", so its
  training can't hand it the answers; it has to learn this world's rules
  from experience, as Frankie does.
- Its memory is its prompt: every prompt carries its history of eats (what
  it ate, by its numbers, and what happened), trimmed to the last
  HISTORY_LINES lines.
- Calls only at decision points: when something in view could be
  approached and it has no target (at most once every DECIDE_EVERY ticks,
  or at once when its energy crosses its reserve), and when it reaches its
  target (look, eat or leave). Simple shared code walks it to the target
  it chose.
- Plumbing: the standard library's urllib, the key from ANTHROPIC_API_KEY,
  the model from --llm-model or FRANKIE_LLM_MODEL (never written in code).
  Every call (prompt, answer, tokens) is saved to a JSON-lines file so a
  race can be replayed and checked without paying again (ReplayLLM). With
  no key the creature is greyed out on the page, and the tests use FakeLLM.
"""

import json
import os
import pathlib
import time
import urllib.error
import urllib.request

import numpy as np

from life import config as C
from life.minds.common import EAT_REACH, RandomWalk, dist, steer

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2026-10-21"
HISTORY_LINES = 40            # the context budget: this many lines of experience go into each prompt
DECIDE_EVERY = 15             # ticks between "where to?" decisions when nothing has changed
EMPTY_EVERY = 100             # with nothing in view, ask "wander or rest?" this often
MAX_TOKENS = 2048             # room for the model's own reasoning plus a one-line JSON answer
IGNORE_TICKS = 300
BUMPS_TO_ASK = 10             # bumping this often on the way to a target is a decision point (touch is a sense)

SYSTEM = (
    "You control a creature in a world you know nothing about. You see objects only as numbers between 0 and 1. "
    "Eating an object changes your energy, up or down, by an amount you must learn. Your energy falls a little "
    "every tick and a little more when you walk; at 0 you die. A close look at an object shows more of its "
    "numbers and costs 0.25 energy. Learn from your own experience which objects are worth eating. "
    "Reply with exactly one JSON object and nothing else."
)


def available():
    return bool(os.environ.get("ANTHROPIC_API_KEY")) and bool(os.environ.get("FRANKIE_LLM_MODEL"))


class LLMError(RuntimeError):
    pass


class AnthropicLLM:
    """One Messages API call per decision, through urllib (no new packages)."""

    def __init__(self, model=None, key=None, effort=None, timeout=120):
        self.model = model or os.environ.get("FRANKIE_LLM_MODEL")
        self.key = key or os.environ.get("ANTHROPIC_API_KEY")
        self.effort = effort or os.environ.get("FRANKIE_LLM_EFFORT")
        self.timeout = timeout
        if not self.key:
            raise LLMError("no ANTHROPIC_API_KEY: the LLM creature can't run")
        if not self.model:
            raise LLMError("no model: pass --llm-model or set FRANKIE_LLM_MODEL")

    def request(self, prompt):
        body = {"model": self.model, "max_tokens": MAX_TOKENS, "system": SYSTEM,
                "messages": [{"role": "user", "content": prompt}]}
        if self.effort:
            body["output_config"] = {"effort": self.effort}
        return urllib.request.Request(API_URL, data=json.dumps(body).encode("utf-8"), method="POST",
                                      headers={"content-type": "application/json", "x-api-key": self.key,
                                               "anthropic-version": API_VERSION})

    def __call__(self, prompt):
        req = self.request(prompt)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    out = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504, 529) and attempt < 3:
                    time.sleep(float(e.headers.get("retry-after") or 2 ** attempt))
                    continue
                raise LLMError(f"API error {e.code}: {e.read()[:300].decode('utf-8', 'replace')}") from None
            except urllib.error.URLError as e:
                if attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise LLMError(f"network error: {e.reason}") from None
        text = "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
        usage = out.get("usage", {})
        return {"text": text, "stop_reason": out.get("stop_reason"),
                "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0)}


class FakeLLM:
    """A scripted stand-in for tests: approaches the nearest object, looks once, eats if trait 1 is above 0.5."""

    model = "fake"

    def __call__(self, prompt):
        if "Choose: look, eat or leave" in prompt:
            ans = {"do": "look", "why": "scripted"}
        elif "Choose: eat or leave" in prompt:
            line = next((l for l in prompt.splitlines() if l.startswith("Close look:")), "")
            v = float(line.split("t1=")[1].split()[0]) if "t1=" in line else 0.0
            ans = {"do": "eat" if v > 0.5 else "leave", "why": "scripted"}
        elif "[1]" in prompt:
            ans = {"do": "approach", "object": 1, "why": "scripted"}
        else:
            ans = {"do": "wander", "why": "scripted"}
        return {"text": json.dumps(ans), "stop_reason": "end_turn", "input_tokens": len(prompt) // 4,
                "output_tokens": 12}


class ReplayLLM:
    """Answers from a saved run, in order, checking each prompt matches: a race checked without paying again."""

    model = "replay"

    def __init__(self, path):
        self.calls = [json.loads(l) for l in pathlib.Path(path).read_text().splitlines() if l.strip()]
        self.i = 0

    def __call__(self, prompt):
        if self.i >= len(self.calls):
            raise LLMError("the saved run has no more answers")
        c = self.calls[self.i]
        self.i += 1
        if c["prompt"] != prompt:
            raise LLMError(f"replay diverged at call {self.i}: the prompt differs from the saved one")
        return c["answer"]


def _nums(values, prefix="t"):
    return " ".join(f"{prefix}{i + 1}={v:.2f}" for i, v in enumerate(values))


def parse(text):
    """The first JSON object in the answer; anything unreadable becomes 'leave'/'wander'."""
    a, b = text.find("{"), text.rfind("}")
    if a < 0 or b < a:
        return {}
    try:
        out = json.loads(text[a:b + 1])
        return out if isinstance(out, dict) else {}
    except json.JSONDecodeError:
        return {}


class LLMCreature:
    name = "llm"
    label = "LLM creature"

    def __init__(self, seed, reserve, boldness, llm=None, log_path=None):
        self.llm = llm if llm is not None else AnthropicLLM()
        self.reserve = float(reserve)
        self.rng = np.random.default_rng([seed, 13])
        self.walk = RandomWalk(self.rng)
        self.history = []
        self.target = None
        self.mode = "wander"          # until its first decision
        self.sharp = {}
        self.ignore = {}
        self.last_decide = -10**9
        self.was_hungry = None
        self.pending_eat = None
        self.bumps = 0
        self.note = ""
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.refusals = 0
        self.errors = 0
        self.thought = "Waiting for its first decision."
        self.look_log = []            # stays empty: the LLM states no decision before a look, so none can change
        self.tick = 0
        self.log_path = pathlib.Path(log_path) if log_path else None

    # -------------------------------------------------------------- asking

    def _ask(self, prompt):
        try:
            ans = self.llm(prompt)
        except LLMError as e:
            self.errors += 1
            self.thought = f"(LLM call failed: {e})"
            return {}
        self.calls += 1
        self.input_tokens += int(ans.get("input_tokens", 0))
        self.output_tokens += int(ans.get("output_tokens", 0))
        if ans.get("stop_reason") == "refusal":
            self.refusals += 1
        if self.log_path is not None:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a") as f:
                f.write(json.dumps({"tick": self.tick, "prompt": prompt, "answer": ans}) + "\n")
        out = parse(ans.get("text", ""))
        self.thought = f"LLM: {ans.get('text', '')[:200]}"
        return out

    def _header(self, p):
        lines = [f"Tick {p['tick']}. Your energy: {p['energy']:.1f} (your reserve: {self.reserve:.1f}; the most you "
                 f"can hold is {C.ENERGY_MAX:.0f})."]
        if self.history:
            lines.append("What happened when you ate before (oldest first):")
            lines += self.history[-HISTORY_LINES:]
        else:
            lines.append("You have not eaten anything yet.")
        return lines

    # -------------------------------------------------------------- one tick

    def act(self, p):
        self.tick = p["tick"]
        if p.get("ate") and self.pending_eat is not None:
            a = p["ate"]
            what = self.pending_eat
            self.history.append(f"- ate an object with {what}; energy change {a['delta']:+.0f}; "
                                f"taste {_nums(a['taste'], 'q')}")
            self.pending_eat = None
        if p.get("sharp"):
            self.sharp[p["sharp"]["ref"]] = p["sharp"]["traits"]
        seen = {s["ref"]: s for s in p["seen"]}
        hungry = p["energy"] < self.reserve
        crossed = self.was_hungry is not None and hungry != self.was_hungry
        self.was_hungry = hungry
        if self.target is not None and p.get("touch"):
            self.bumps += 1
            if self.bumps >= BUMPS_TO_ASK:
                self.note = (f"You bumped into something {'wet' if p['touch'] == 'water' else 'solid'} "
                             f"{self.bumps} times while walking towards the object you chose.")
                self.ignore[self.target] = self.tick + IGNORE_TICKS // 3
                self.target, self.bumps, self.last_decide = None, 0, -10**9
        if self.target is not None:
            s = seen.get(self.target)
            if s is None:
                self.target = None
            elif s["dist"] <= EAT_REACH:
                return self._at_object(p, s)
            else:
                return steer(p, s["x"], s["z"])
        options = [s for s in p["seen"] if self.ignore.get(s["ref"], -1) < self.tick][:8]
        if options and (crossed or self.tick - self.last_decide >= DECIDE_EVERY):
            self.last_decide = self.tick
            lines = self._header(p) + ([self.note] if self.note else []) + [
                "Objects you can see now (distance in metres, bearing in degrees, + is to your left):"]
            self.note = ""
            for i, s in enumerate(options):
                lines.append(f"[{i + 1}] {s['dist']:.1f} m, {np.degrees(s['bearing']):+.0f} deg, {_nums(s['traits'])}")
            lines.append('Choose: approach one object, wander, or rest. Answer like {"do": "approach", "object": 2, '
                         '"why": "..."} or {"do": "wander", "why": "..."} or {"do": "rest", "why": "..."}.')
            ans = self._ask("\n".join(lines))
            do = ans.get("do")
            k = ans.get("object")
            if do == "approach" and isinstance(k, int) and 1 <= k <= len(options):
                self.target, self.bumps = options[k - 1]["ref"], 0
                return steer(p, options[k - 1]["x"], options[k - 1]["z"])
            self.mode = "rest" if do == "rest" else "wander"
        elif not options and (crossed or self.tick - self.last_decide >= EMPTY_EVERY):
            self.last_decide = self.tick
            lines = self._header(p) + ["You can see nothing right now.",
                                       'Choose: wander or rest. Answer like {"do": "wander", "why": "..."}.']
            self.mode = "rest" if self._ask("\n".join(lines)).get("do") == "rest" else "wander"
        if self.mode == "rest":
            return {"do": "rest"}
        return self.walk.act(p)

    def _at_object(self, p, s):
        ref = s["ref"]
        lines = self._header(p)
        if ref in self.sharp:
            lines.append(f"Close look: {_nums(self.sharp[ref])}")
            lines.append('Choose: eat or leave. Answer like {"do": "eat", "why": "..."}.')
        else:
            lines.append(f"The object in front of you: {_nums(s['traits'])}")
            lines.append('Choose: look, eat or leave. A look costs 0.25 energy and shows more numbers. '
                         'Answer like {"do": "look", "why": "..."}.')
        ans = self._ask("\n".join(lines))
        do = ans.get("do")
        if do == "look" and ref not in self.sharp:
            return {"do": "look", "ref": ref}
        if do == "eat":
            shown = self.sharp.get(ref, s["traits"])
            self.pending_eat = _nums(shown)
            self.target = None
            return {"do": "eat", "ref": ref}
        self.ignore[ref] = self.tick + IGNORE_TICKS
        self.target = None
        return {"do": "rest"}

    def cost(self):
        return {"calls": self.calls, "input_tokens": self.input_tokens, "output_tokens": self.output_tokens,
                "refusals": self.refusals, "errors": self.errors, "history_lines_budget": HISTORY_LINES,
                "model": getattr(self.llm, "model", None)}

    def panel(self):
        return {"thought": self.thought + f"\n({self.calls} LLM calls, {self.input_tokens + self.output_tokens} tokens)",
                "mode": self.mode, "focus": self.target, "look_target": None,
                "memory": {"kinds": [], "places": []}}
