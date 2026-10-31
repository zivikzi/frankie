"""The charter's automatic mind checks (section 7, step 5). They pass on the stub now and run again at every freeze.

Static checks, on the package's files (they never run its code):

- the import guard (FORBIDDEN 1 and 3, LEDGER I02; tools/import_guard.py);
- the file scan for model weights (FORBIDDEN 1);
- the word scans of FORBIDDEN 2, 4, 6, 7, 10, 11, 12, 21 and 22, and the
  code check for references to essence, core or free labels (FORBIDDEN 18).
  Words are matched in names, comments and strings, after splitting names at
  underscores and case changes, ignoring case. A word matches a scan word if
  it is the scan word, or, for scan words of 4 letters or more, starts with
  it ("gradient" for "grad"). A string that is exactly one of the
  interface's own field names ("count" in the thinking record) is not
  scanned, since the harness, not the mind, chose it (KT-107). Every hit
  goes to review; the stub has none;
- the no-unlisted-constants test (FORBIDDEN 28, I06): a number other than
  0 and 1 may appear only as a module-level constant whose line cites its
  register or ledger row (PLACEHOLDER-nn, KT-nn, or a ledger row such as
  M20), and no constant may hold more than one number, so every constant
  has one value shared by every trait and every layer (section 7).

Run-time checks, on the package run in its own process through the harness on
tuning runs:

- the interface test: no object id, role, nature, kind id or core label
  reaches the mind; every message holds only the fields the interface
  names, and the birth configuration only R, b, the trait order and the
  mind's own settings (FORBIDDEN 18, KT-93, KT-97);
- the leak test: swapping the natures of the run's items changes nothing the
  mind observes before an eat, and no reading at all (FORBIDDEN 18);
- taste values reach the mind only in land(), right after a decision that
  ended in an eat (FORBIDDEN 29);
- memory is empty at birth, and every new candidate starts with every
  relevance weight at 5 tenths (FORBIDDEN 20, M20);
- the chooser is satisficing, and every M47 fallback lists every option with
  cleared_bar = false (FORBIDDEN 13; checked on every decision by
  harness/protocol.py, counted here);
- the intercepted-outcome counter check: two copies that differ only in how
  many earlier looks they made, with no outcome landing, must be identical
  after the same last look (FORBIDDEN 9, X43(e));
- every constant the mind reports cites a row and is one number (FORBIDDEN 28);
- a taste-blind stub is classed as not noticing the taste in 100% of runs
  (section 7, step 5). This one runs only on the stub.

Usage: python tools/mind_checks.py [package_dir]   (default: the stub)
Exits 0 if every check passes, 1 if any fails, 2 if the word scans need review.
"""

import ast
import dataclasses
import io
import pathlib
import re
import sys
import tokenize

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import import_guard  # noqa: E402

from harness import protocol, scoring  # noqa: E402
from harness.host import SubprocessHost  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from harness.run import run_one  # noqa: E402
from world import keys  # noqa: E402
from world.kinds import NOURISH, POISON  # noqa: E402
from world.run_plan import generate_run  # noqa: E402

# The word scans, by FORBIDDEN entry
SCAN_WORDS = {
    2: ("grad", "backward", "loss", "optimizer"),
    4: ("novel", "bonus", "visit", "count"),
    6: ("progress", "improvement", "competence"),
    7: ("uncertainty", "entropy", "ucb", "thompson"),
    10: ("seed", "tree", "grow"),
    11: ("td", "q_table", "value_function", "bellman", "discount", "gamma", "bootstrap", "eligibility",
         "advantage"),
    12: ("softmax", "epsilon", "boltzmann", "temperature"),
    18: ("essence", "core", "free"),
    21: ("information_gain", "gini", "entropy"),
    22: ("astar", "dijkstra", "bfs", "plan"),
}
CORE_LABEL = re.compile(r"^c[1-4]$")                       # H's core labels c1 to c4 (FORBIDDEN 18)
WEIGHT_SUFFIXES = (".pt", ".pth", ".onnx", ".safetensors", ".npz", ".npy", ".pkl", ".pickle", ".h5", ".ckpt",
                   ".bin", ".gguf", ".tflite", ".joblib")
ROW = re.compile(r"\b(PLACEHOLDER-\d+|KT-\d+|[A-Z]\d{1,3})\b")
PLAIN_NUMBERS = (0, 1)
# The names the interface itself gives a mind's answers (harness/protocol.py), never scanned as words
INTERFACE_FIELDS = {
    "action", "verdict", "settle_step", "thinking", "drive", "provenance", "log", "unit", "count", "cost_milli",
    "eat_chance", "skip_chance", "bar", "pick", "options_considered", "no_safe_option", "untried_tally", "order",
    "source", "option", "predicted_p_above_R", "cleared_bar", "events", "type", "trigger", "slot", "parent_slot",
    "layer", "weight_deltas", "placeholder_93", "candidates", "ranges", "weights_tenths", "reliability", "eats",
    "version", "constants", "chooser", "neuron", "reserve_milli", "boldness", "params", "trait_order",
    "last_leader", "within_margin",
}
# World-side names that may never reach a mind, by name (FORBIDDEN 18, PLACEHOLDER-64)
WORLD_FIELDS = {"gaze_target", "verdict_subject", "probe_role", "hidden_nature", "kind_id", "creature_id",
                "label", "role", "nature", "place", "replica", "kind", "core", "family", "labels", "essence",
                "set_name", "noise_key", "item_role", "phase", "forced"}
BIRTH_FIELDS = {"reserve_milli", "boldness", "params", "trait_order"}


@dataclasses.dataclass
class Finding:
    check: str
    where: str
    what: str
    review: bool = False      # a word-scan hit, sent to review rather than failed

    def __str__(self):
        return f"[{self.check}] {self.where}: {self.what}"


def _py_files(package_dir):
    return sorted(p for p in pathlib.Path(package_dir).rglob("*.py") if "__pycache__" not in p.parts)


# ------------------------------------------------------------------ static checks

def guard_check(package_dir) -> list:
    return [Finding("import guard", f"{p}:{line}", msg) for p, line, msg in import_guard.check([package_dir])]


def file_scan(package_dir) -> list:
    out = []
    for p in sorted(pathlib.Path(package_dir).rglob("*")):
        if p.is_file() and p.suffix.lower() in WEIGHT_SUFFIXES:
            out.append(Finding("FORBIDDEN 1 file scan", str(p), "a model-weight or data file in the package"))
    return out


def _split_name(name):
    parts = []
    for chunk in re.split(r"[_\W\d]+", name):
        parts += re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+", chunk)
    return [w.lower() for w in parts if w]


def _matches(word, scan):
    if "_" in scan:
        return False
    return word == scan or (len(scan) >= 4 and word.startswith(scan))


def word_scan(package_dir) -> list:
    out = []
    for p in _py_files(package_dir):
        src = p.read_bytes()
        for tok in tokenize.tokenize(io.BytesIO(src).readline):
            if tok.type == tokenize.NAME:
                text, words = tok.string, _split_name(tok.string)
            elif tok.type == tokenize.STRING:
                try:
                    value = ast.literal_eval(tok.string)
                except (ValueError, SyntaxError):
                    value = tok.string
                if isinstance(value, str) and value in INTERFACE_FIELDS:
                    continue
                text, words = tok.string, _split_name(str(value))
            elif tok.type == tokenize.COMMENT:
                text, words = tok.string, _split_name(tok.string)
            else:
                continue
            low = text.lower()
            for n, scan_words in SCAN_WORDS.items():
                for scan in scan_words:
                    hit = (scan in low) if "_" in scan else any(_matches(w, scan) for w in words)
                    if hit:
                        out.append(Finding(f"FORBIDDEN {n} word scan", f"{p}:{tok.start[0]}",
                                           f"'{scan}' in {text[:60]!r}", review=True))
            if tok.type == tokenize.NAME and CORE_LABEL.match(tok.string):
                out.append(Finding("FORBIDDEN 18 code check", f"{p}:{tok.start[0]}",
                                   f"a core label {tok.string!r}", review=True))
    return out


def _number(node):
    """The value of a numeric literal node (with a sign), or None."""
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = _number(node.operand)
        return None if v is None else (-v if isinstance(node.op, ast.USub) else v)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, complex)) \
            and not isinstance(node.value, bool):
        return node.value
    return None


def constants_scan(package_dir) -> list:
    out = []
    for p in _py_files(package_dir):
        src = p.read_text(encoding="utf-8")
        lines = src.splitlines()
        tree = ast.parse(src)
        allowed = set()
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                value = _number(node.value)
                if value is None:
                    continue
                allowed.add(id(node.value))
                if isinstance(node.value, ast.UnaryOp):
                    allowed.add(id(node.value.operand))
                if not ROW.search(lines[node.lineno - 1]):
                    out.append(Finding("FORBIDDEN 28 constants", f"{p}:{node.lineno}",
                                       f"constant {node.targets[0].id} cites no register or ledger row"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
                elts = node.values if isinstance(node, ast.Dict) else node.elts
                nums = [e for e in elts if _number(e) is not None and _number(e) not in PLAIN_NUMBERS]
                if nums:
                    out.append(Finding("FORBIDDEN 28 constants", f"{p}:{node.lineno}",
                                       "a container of numbers: a constant must be one value for every trait "
                                       "and layer"))
            v = _number(node) if isinstance(node, ast.Constant) else None
            if v is not None and id(node) not in allowed and v not in PLAIN_NUMBERS:
                out.append(Finding("FORBIDDEN 28 constants", f"{p}:{node.lineno}",
                                   f"the number {v!r} outside a cited constant"))
    return out


def static_checks(package_dir) -> list:
    return guard_check(package_dir) + file_scan(package_dir) + word_scan(package_dir) + constants_scan(package_dir)


# ------------------------------------------------------------------ run-time checks

class RecordingHost:
    """Passes every request to a real host and keeps a copy of what the mind was sent."""

    def __init__(self, inner):
        self.inner = inner
        self.sent = []

    def new(self, name, config):
        self.sent.append(("new", name, config))
        return self.inner.new(name, config)

    def copy(self, src, dst):
        self.sent.append(("copy", src, dst))
        return self.inner.copy(src, dst)

    def drop(self, name):
        self.sent.append(("drop", name))
        return self.inner.drop(name)

    def decide(self, name, visible, energy_milli):
        out = self.inner.decide(name, visible, energy_milli)
        self.sent.append(("decide", name, list(visible), energy_milli, out["action"]))
        return out

    def land(self, name, delta_milli, energy_after_milli, taste):
        self.sent.append(("land", name, delta_milli, energy_after_milli, list(taste)))
        return self.inner.land(name, delta_milli, energy_after_milli, taste)

    def write(self, name):
        self.sent.append(("write", name))
        return self.inner.write(name)

    def dump(self, name):
        return self.inner.dump(name)

    def info(self, name):
        return self.inner.info(name)

    def fingerprint(self, name):
        return self.inner.fingerprint(name)

    def close(self):
        self.inner.close()


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k)
            yield from _strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _strings(v)


def _tuning_plans(n=2):
    key = keys.tuning_set_key()
    return [generate_run("tuning", key, f, r) for f, r in ((1, 1), (12, 4), (25, 9))[:n]]


def _recorded_run(spec, package_dir, plan, cache=None):
    cache = cache or ReadingCache(plan.noise_key)
    host = RecordingHost(SubprocessHost(package_dir))
    try:
        rec = run_one(plan, spec, cache, host=host)
    finally:
        host.close()
    return rec, host.sent


def interface_check(spec, package_dir, plans) -> list:
    out = []
    for plan in plans:
        rec, sent = _recorded_run(spec, package_dir, plan)
        where = f"tuning family {plan.family_number} run {plan.run_number}"
        last_decide = {}
        for msg in sent:
            op, name = msg[0], msg[1]
            if op == "new":
                cfg = msg[2]
                if set(cfg) - BIRTH_FIELDS:
                    out.append(Finding("FORBIDDEN 18 interface", where, f"birth fields {sorted(set(cfg) - BIRTH_FIELDS)}"))
                if set(cfg["params"]) != set(spec.params):
                    out.append(Finding("FORBIDDEN 18 interface", where, "the mind was told settings not its own"))
                bad = WORLD_FIELDS & set(_strings(cfg))
                if bad:
                    out.append(Finding("FORBIDDEN 18 interface", where, f"world-side names at birth: {sorted(bad)}"))
            elif op == "decide":
                visible, energy = msg[2], msg[3]
                if len(visible) != 18 or not all(isinstance(x, float) for x in visible) or \
                        not isinstance(energy, int):
                    out.append(Finding("FORBIDDEN 18 interface", where, "a look carried more than 18 readings "
                                                                        "and the energy"))
                last_decide[name] = msg
            elif op == "land":
                prev = last_decide.pop(name, None)
                if prev is None:
                    out.append(Finding("FORBIDDEN 29 taste after eat", where, "taste landed with no decision before"))
                if len(msg[4]) != 4:
                    out.append(Finding("FORBIDDEN 29 taste after eat", where, "an eat landed other than 4 tastes"))
        lands = sum(1 for m in sent if m[0] == "land")
        eats = sum(1 for d in rec.decisions.values() if "outcome_milli" in d)
        if lands != eats:
            out.append(Finding("FORBIDDEN 29 taste after eat", where, f"{lands} tastes landed for {eats} eats"))
    return out


def _swap_natures(plan):
    swap = {NOURISH: POISON, POISON: NOURISH}

    def sw(o):
        return dataclasses.replace(o, kind=dataclasses.replace(o.kind, nature=swap.get(o.nature, o.nature)))
    return dataclasses.replace(plan, warmup_items=[sw(o) for o in plan.warmup_items],
                               teaching=[sw(o) for o in plan.teaching], h2=sw(plan.h2),
                               P=[sw(o) for o in plan.P], Q=[sw(o) for o in plan.Q])


def leak_check(spec, package_dir, plan) -> list:
    out = []
    swapped = _swap_natures(plan)
    if swapped.teaching[0].nature == plan.teaching[0].nature:
        return [Finding("FORBIDDEN 18 leak", "the leak test", "swapping natures changed nothing in the plan")]
    _, a = _recorded_run(spec, package_dir, plan)
    _, b = _recorded_run(spec, package_dir, swapped)
    first = next(i for i, m in enumerate(a) if m[0] == "land")
    if a[:first] != b[:first]:
        out.append(Finding("FORBIDDEN 18 leak", "the leak test", "the mind observed something different "
                                                                 "before the first eat"))
    looks = [m[2] for m in a if m[0] == "decide"], [m[2] for m in b if m[0] == "decide"]
    tastes = [m[4] for m in a if m[0] == "land"], [m[4] for m in b if m[0] == "land"]
    if looks[0] != looks[1] or tastes[0] != tastes[1]:
        out.append(Finding("FORBIDDEN 18 leak", "the leak test", "a reading changed with the natures"))
    return out


def birth_check(spec, package_dir, plan) -> list:
    """Empty at birth, and every new candidate starts with equal weights of 5 tenths (FORBIDDEN 20, M20)."""
    from harness.run import birth_config
    out = []
    cache = ReadingCache(plan.noise_key)
    with SubprocessHost(package_dir) as host:
        host.new("born", birth_config(plan, spec))
        if host.dump("born").get("candidates"):
            return [Finding("FORBIDDEN 20 empty at birth", "birth", "the mind holds candidates at birth")]
        run_one(plan, spec, cache, host=_DumpAfterWrite(host, out), checks=False, branches=False)
    return out


class _DumpAfterWrite(RecordingHost):
    def __init__(self, inner, findings):
        super().__init__(inner)
        self.findings = findings

    def write(self, name):
        w = self.inner.write(name)
        made = {e["slot"] for e in w["events"] if e["type"] in ("new", "split")}
        if made:
            for c in self.inner.dump(name)["candidates"]:
                if c["slot"] in made:
                    weights = [x for x in c["weights_tenths"] if x is not None]
                    if any(x != 5 for x in weights):
                        self.findings.append(Finding("M20 equal weights", f"slot {c['slot']}",
                                                     f"a new candidate's weights start at {sorted(set(weights))}"))
        return w


def chooser_check(records) -> dict:
    """Counted only: harness/protocol.py refuses any decision that breaks FORBIDDEN 13."""
    fallbacks = sum(1 for rec in records for d in rec.decisions.values()
                    if d["mind"]["drive"] and d["mind"]["drive"]["no_safe_option"])
    return {"decisions": sum(len(r.decisions) for r in records), "fallbacks": fallbacks,
            "chooser": sorted({r.info["chooser"] for r in records})}


def counter_check(spec, package_dir, plan, extra_looks=7) -> list:
    """Copies that differ only in earlier looks, with no outcome landing, must end identical (FORBIDDEN 9, X43(e))."""
    from harness.run import _Run, birth_config
    cache = ReadingCache(plan.noise_key)
    with SubprocessHost(package_dir) as host:
        run = _Run(plan, spec, host, cache, birth_config(plan, spec))
        host.new("main", run.birth)
        for i, obj in enumerate(plan.warmup_sequence()[:20], 1):
            run._main_taste(i, f"warmup-{i}", obj)
        e = run.reset_to
        host.copy("main", "a")
        host.copy("main", "b")
        for k, obj in enumerate(plan.P[:extra_looks]):
            host.decide("b", cache.visible(obj, 1000 + k), e)
        last = cache.visible(plan.P[-1], 1)
        da, db = host.decide("a", last, e), host.decide("b", last, e)
        fa, fb = host.fingerprint("a"), host.fingerprint("b")
    if da != db or fa != fb:
        return [Finding("FORBIDDEN 9 counter check", "X43(e)", "looks with no outcome changed the mind's state")]
    return []


def constants_check(records) -> list:
    out = []
    for rec in records:
        for name, (value, row) in rec.info["constants"].items():
            if not ROW.search(row):
                out.append(Finding("FORBIDDEN 28 constants", name, f"cites {row!r}, not a register or ledger row"))
    return out


def taste_blind_check(spec, package_dir, plans) -> list:
    out = []
    for plan in plans:
        rec = run_one(plan, spec, ReadingCache(plan.noise_key), package_dir=package_dir)
        if scoring.measures(rec)["noticed"]:
            out.append(Finding("taste-blind stub", f"family {plan.family_number} run {plan.run_number}",
                               "a taste-blind mind was classed as noticing"))
    return out


def run_checks(package_dir, spec, plans=None, taste_blind_plans=None) -> dict:
    plans = plans or _tuning_plans()
    findings = static_checks(package_dir)
    findings += interface_check(spec, package_dir, plans[:1])
    findings += leak_check(spec, package_dir, plans[0])
    findings += birth_check(spec, package_dir, plans[0])
    findings += counter_check(spec, package_dir, plans[0])
    records = [run_one(p, spec, ReadingCache(p.noise_key), package_dir=package_dir) for p in plans]
    findings += constants_check(records)
    if taste_blind_plans is not None:
        findings += taste_blind_check(spec, package_dir, taste_blind_plans)
    return {"findings": findings, "chooser": chooser_check(records),
            "failed": [f for f in findings if not f.review], "review": [f for f in findings if f.review]}


def main(argv) -> int:
    from test_fixtures.stub import STUB_DIR, stub_spec
    package_dir = pathlib.Path(argv[1]) if len(argv) > 1 else STUB_DIR
    if package_dir.resolve() != STUB_DIR.resolve():
        print("Only the stub can be checked until K-F's registry entry exists (Week 3).")
        return 1
    key = keys.tuning_set_key()
    blind = [generate_run("tuning", key, f, 1) for f in range(1, 31)]
    res = run_checks(package_dir, stub_spec(), taste_blind_plans=blind)
    for f in res["findings"]:
        print(("REVIEW " if f.review else "FAIL   ") + str(f))
    print(f"chooser: {res['chooser']}")
    if res["failed"]:
        print(f"mind checks: {len(res['failed'])} failed")
        return 1
    if res["review"]:
        print(f"mind checks: {len(res['review'])} word-scan hits to review")
        return 2
    print("mind checks: all pass")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
