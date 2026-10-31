"""The one mind interface, and the live checks on everything a mind says (B21, KT-93).

A mind is made by make(config) and then answers five requests:

    decide(visible, energy_milli) -> decision
        visible: a fresh, read-only float64 array of the 18 visible readings, in
        schema order. energy_milli: the body's energy in whole milli-units,
        after the reset and the sharp look. Nothing else reaches the mind:
        no taste, label, place, role, nature, kind, key or phase (FORBIDDEN 18).
        decide() may not change what the mind keeps; it may hold the current
        decision in a buffer for land() and write().
    land(delta_milli, energy_after_milli, taste) -> landing
        Only right after a decision that ended in an eat, chosen or forced. The
        outcome and the 4 taste readings land (FORBIDDEN 29); a tower mind
        makes its verdict after eating. Nothing is written yet.
    write() -> memory write events
        The mind's own memory rule. Bots store the item here (section 4).
    dump() -> memory_state_dump (glossary), read by the harness only
    info() -> version record, constants table, chooser mode, neuron type

The checks below run on every answer, in every run (FORBIDDEN 13, 18, 29).
A failed check stops the run with an error.
"""

import math

from . import constants as C

VERDICT_WORDS = ("unknown", "unsettled")
WRITE_TYPES = ("new", "stretch", "split", "mark-unreliable", "forget")
FILING_TYPES = ("new", "stretch", "split", "mark-unreliable")
TRIGGERS = ("chosen-eat", "designed-exposure")
SPLIT_LAYERS = ("context", "object", "parts", "details", "taste", None)


class InterfaceError(RuntimeError):
    """A mind's answer broke the interface. The run stops (KT-95)."""


def _need(cond, msg):
    if not cond:
        raise InterfaceError(msg)


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _is_num(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)) and math.isfinite(x)


def _keys(d, required, optional=(), what="answer"):
    _need(isinstance(d, dict), f"a mind's {what} must be an object")
    missing = [k for k in required if k not in d]
    extra = [k for k in d if k not in required and k not in optional]
    _need(not missing, f"{what} lacks {missing}")
    _need(not extra, f"{what} has fields outside the interface: {extra}")


def thinking_cost_milli(count: int, unit_nano: int) -> int:
    """count x unit cost, summed exactly, rounded to the nearest milli-unit, halves up (KT-48, KT-92)."""
    return (2 * count * unit_nano + C.NANO_PER_MILLI) // (2 * C.NANO_PER_MILLI)


def check_verdict(v, spec, what):
    if spec.mind_class == "bot":
        _need(v is None, f"a bot's {what} names no candidate")
    else:
        _need((_is_int(v) and v >= 0) or v in VERDICT_WORDS,
              f"{what} must be a candidate slot, 'unknown' or 'unsettled', not {v!r}")


def check_decision(d, spec):
    _keys(d, ("action", "verdict", "settle_step", "thinking", "drive", "provenance"), ("log",), "decision")
    _need(d["action"] in ("eat", "skip"), "the only actions are eat and skip (FORBIDDEN 29)")
    check_verdict(d["verdict"], spec, "verdict")
    _need(d["settle_step"] is None or _is_int(d["settle_step"]), "settle_step must be a whole number")
    th = d["thinking"]
    _keys(th, ("unit", "count", "cost_milli"), (), "thinking")
    _need(th["unit"] == spec.thinking_unit, f"{spec.label} pays per {spec.thinking_unit}, not {th['unit']}")
    _need(_is_int(th["count"]) and th["count"] >= 0, "thinking count must be a whole number")
    _need(_is_int(th["cost_milli"]), "thinking cost must be in whole milli-units")
    _need("log" not in d or isinstance(d["log"], dict), "log must be an object")
    if spec.mind_class == "bot":
        _need(d["drive"] is None, "a bot has no drive")
        _need(d["provenance"] == "baseline-rule", "a bot's choices carry baseline-rule (glossary)")
        _need(th["count"] == 0 and th["cost_milli"] == 0, "bots pay nothing (KT-46)")
        return
    _check_drive(d, spec)


def _check_drive(d, spec):
    """The drive trace (KT-49) and the satisficing chooser's own list (FORBIDDEN 13, M47)."""
    dr = d["drive"]
    _keys(dr, ("eat_chance", "skip_chance", "bar", "pick", "options_considered", "no_safe_option",
               "untried_tally"), (), "drive trace")
    _need(dr["eat_chance"] is None or _is_num(dr["eat_chance"]), "eat_chance must be a number or null")
    for k in ("skip_chance", "bar"):
        _need(_is_num(dr[k]), f"{k} must be a number")
    _need(dr["untried_tally"] is None or _is_num(dr["untried_tally"]), "untried_tally must be a number or null")
    _need(dr["pick"] in ("eat", "skip"), "the drive picks eat or skip")
    _need(isinstance(dr["no_safe_option"], bool), "no_safe_option must be true or false")
    _need(d["provenance"] in ("bench", "no-safe-option-fallback"),
          "an ordinary bench choice carries 'bench' and the fallback its own tag (KT-49)")
    _need(d["action"] == dr["pick"], "the action taken is the drive's pick")
    opts = dr["options_considered"]
    _need(isinstance(opts, list), "options_considered must be a list")
    for n, o in enumerate(opts, 1):
        _keys(o, ("order", "source", "option", "predicted_p_above_R", "cleared_bar"), (), "option")
        _need(o["order"] == n, "options are listed in the order considered")
        _need(o["source"] == "bench", "habits are off and there are no proposals (KT-49)")
        _need(o["option"] in ("eat", "skip"), "options are eat and skip")
        _need(_is_num(o["predicted_p_above_R"]), "an option's chance must be a number")
        _need(o["cleared_bar"] is (o["predicted_p_above_R"] >= dr["bar"]),
              "cleared_bar must say whether the chance reached the bar")
    if d["verdict"] in VERDICT_WORDS:
        _need(d["action"] == "skip", "an unknown or unsettled verdict is always a skip on the bench (section 5)")
        _need(not opts and not dr["no_safe_option"] and dr["eat_chance"] is None,
              "the chooser does not run on an unknown or unsettled verdict")
        _need(d["provenance"] == "bench", "an unknown or unsettled skip carries 'bench'")
        return
    _need(dr["eat_chance"] is not None, "a named candidate has an eat's chance (KT-49)")
    _need([o["option"] for o in opts] in (["eat"], ["eat", "skip"]), "eat is considered first, then skip")
    if dr["no_safe_option"]:
        _need(len(opts) == 2 and not any(o["cleared_bar"] for o in opts),
              "every option of an M47 fallback has cleared_bar = false (FORBIDDEN 13)")
        _need(d["provenance"] == "no-safe-option-fallback", "the fallback is tagged (M47)")
        eat, skip = opts[0]["predicted_p_above_R"], opts[1]["predicted_p_above_R"]
        _need(dr["pick"] == ("eat" if eat > skip else "skip"), "the fallback takes the higher chance; ties skip (KT-50)")
    else:
        _need(opts[-1]["cleared_bar"] and not any(o["cleared_bar"] for o in opts[:-1]),
              "the chooser takes the first option that clears the bar (M29)")
        _need(dr["pick"] == opts[-1]["option"] and d["provenance"] == "bench", "the pick is the option that cleared")
    _need(opts[0]["predicted_p_above_R"] == dr["eat_chance"], "eat's listed chance is its chance")
    if len(opts) == 2:
        _need(opts[1]["predicted_p_above_R"] == dr["skip_chance"], "skip's listed chance is its chance")


def check_landing(d, spec):
    _keys(d, ("verdict", "settle_step"), ("log",), "verdict after eating")
    if spec.mind_class == "tower":
        check_verdict(d["verdict"], spec, "verdict after eating")
    else:
        _need(d["verdict"] is None, "only tower minds make a verdict after eating (section 6)")


def check_write(w, spec):
    _keys(w, ("events",), ("log",), "write")
    ev = w["events"]
    _need(isinstance(ev, list), "events must be a list")
    if spec.mind_class != "tower":
        _need(ev == [], "only tower minds report memory write events")
        return
    filings = 0
    for e in ev:
        _keys(e, ("type", "trigger", "slot", "parent_slot", "layer", "weight_deltas"), ("placeholder_93",),
              "memory write event")
        _need(e["type"] in WRITE_TYPES, f"unknown write type {e['type']!r} (no merges on the bench, KT-74)")
        _need(e["trigger"] in TRIGGERS, "a write is triggered by a chosen eat or a designed exposure")
        _need(_is_int(e["slot"]) and e["slot"] >= 0, "a write names a slot")
        _need(e["parent_slot"] is None or _is_int(e["parent_slot"]), "parent_slot is a slot or null")
        _need((e["parent_slot"] is not None) == (e["type"] == "split"), "only a split has a parent")
        _need(e["layer"] in SPLIT_LAYERS, "layer must be a layer name or null")
        _need(isinstance(e["weight_deltas"], list), "weight_deltas must be a list")
        if e["type"] in FILING_TYPES:
            filings += 1
    _need(filings == 1, "each eat is filed under exactly one candidate (section 5)")


def check_dump(d, spec):
    _need(isinstance(d, dict), "a memory dump is an object")
    if spec.mind_class != "tower":
        return
    _keys(d, ("candidates",), ("log",), "memory dump")
    for c in d["candidates"]:
        _keys(c, ("slot", "ranges", "weights_tenths", "reliability", "eats"), ("log",), "candidate")
        _need(len(c["ranges"]) == 22 and len(c["weights_tenths"]) == 22, "ranges and weights cover 22 traits")
        for r in c["ranges"]:
            _need(r is None or (len(r) == 2 and all(_is_num(x) for x in r) and r[0] <= r[1]),
                  "a stored range is [lo, hi] or null")
        for w in c["weights_tenths"]:
            _need(w is None or (_is_int(w) and 0 <= w <= 10), "weights are whole tenths from 0 to 10 (KT-94)")
        taste = [c["ranges"][t] for t in (18, 19, 20, 21)]
        _need(all(r is None for r in taste) or all(r is not None for r in taste),
              "a candidate stores all 4 taste ranges or none")


def check_info(d, spec):
    _keys(d, ("version", "constants", "chooser", "neuron"), ("log",), "info")
    _need(isinstance(d["constants"], dict), "constants is a table")
    for name, entry in d["constants"].items():
        _need(isinstance(entry, list) and len(entry) == 2 and isinstance(entry[1], str) and entry[1],
              f"constant {name} must be [value, row] with the row it comes from (FORBIDDEN 28)")
        _need(entry[0] is None or _is_num(entry[0]), f"constant {name} must be one number (section 7)")
    if spec.mind_class == "bot":
        _need(d["chooser"] is None, "bots have no chooser")
    else:
        _need(d["chooser"] == "satisficing", "the chooser is satisficing in every bench run (FORBIDDEN 13)")
        _need(d["version"] == [dict(v) for v in spec.version], "the mind's version record matches the registry")
    if spec.mind_class == "tower":
        _need(d["neuron"] in ("spiking", "rate"), "a tower mind records its neuron type (FORBIDDEN 27)")
