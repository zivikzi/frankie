"""K-F's memory rule, blame moves outward, on hand-made cases (section 6, M10 to M15, KT-70 to KT-77)."""

import numpy as np
import pytest

from harness import protocol
from harness.agents import tower_minds
from mind import constants as K
from mind.memory import Kind, Memory, outcome_class

# These cases were worked out at the agreed start values (TUNING_PLAN.md), not the values set later on the tuning set
START = K.Settings(leak=0.1, threshold=2.5, refractory_ms=2, inhibition=0.3125, detector_width_nw=4, commit_margin=2,
                   objection_threshold=0.5, new_kind_threshold=0.5)

W = 0.04                       # the start detector width, 4 noise widths (KT-23)
GAIN, NOTHING, POISON = 15000, 0, -20000
FORCED, CHOSEN = "designed-exposure", "chosen-eat"


def item(v=0.5, **at):
    x = np.full(K.N_TRAITS, v)
    for t, value in at.items():
        x[int(t[1:])] = value
    return x


def fresh():
    return Memory(START)


def test_outcome_classes_follow_the_sign():
    assert [outcome_class(d) for d in (GAIN, 1, NOTHING, -1, POISON)] == [1, 1, 0, -1, -1]


def test_an_unknown_eat_starts_a_kind_with_equal_weights_and_unclipped_ranges():
    m = fresh()
    ev = m.write("unknown", item(0.5, t0=0.01, t21=0.99), GAIN, True, FORCED)
    assert ev == [{"type": "new", "trigger": FORCED, "slot": 0, "parent_slot": None, "layer": None,
                   "weight_deltas": [], "placeholder_93": True}]
    k = m.kinds[0]
    assert k.lo[0] == pytest.approx(0.01 - W) and k.lo[0] < 0          # not clipped (KT-77)
    assert k.hi[21] == pytest.approx(0.99 + W) and k.hi[21] > 1
    assert list(k.tenths) == [5] * 22 and k.reliability == 20 and k.eats == [[1, True]] and k.wins == 0


def test_an_unsettled_eat_is_written_as_an_unknown_one():
    m = fresh()
    assert m.write("unsettled", item(), POISON, False, FORCED)[0]["type"] == "new"      # (KT-74, PLACEHOLDER-93)


def test_a_right_guess_stretches_exactly_and_only_far_traits_lose_weight():
    m = fresh()
    m.write("unknown", item(0.5), GAIN, True, FORCED)
    # t3 just at the line (one width outside the range), t4 just beyond it, t20 a taste far out
    edge = 0.5 + W + W
    ev = m.write(0, item(0.5, t3=edge, t4=edge + 1e-9, t20=0.9), GAIN, False, CHOSEN)
    k = m.kinds[0]
    assert ev[0]["type"] == "stretch" and ev[0]["slot"] == 0 and ev[0]["trigger"] == CHOSEN
    assert k.hi[3] == edge and k.hi[4] == edge + 1e-9 and k.hi[20] == 0.9     # exactly to include (PLACEHOLDER-06)
    assert k.tenths[3] == 5 and k.tenths[4] == 4 and k.tenths[20] == 4          # (KT-71)
    assert ev[0]["weight_deltas"] == [[0, 4, -1], [0, 20, -1]]
    assert k.reliability == 20 and k.wins == 1 and k.last_win == 2 and k.eats == [[1, True], [1, False]]


def test_weights_never_fall_below_zero_and_reliability_never_rises_above_one():
    m = fresh()
    m.write("unknown", item(0.5), NOTHING, True, FORCED)
    k = m.kinds[0]
    k.tenths[:] = 0
    k.reliability = 19
    m.write(0, item(0.9), NOTHING, True, FORCED)            # a "nothing" kind and a "nothing" eat: right
    assert k.tenths.min() == 0 and k.reliability == 20
    m.write(0, item(0.5), NOTHING, True, FORCED)
    assert k.reliability == 20


def test_the_founding_eats_class_decides_right_and_wrong():
    m = fresh()
    m.write("unknown", item(0.5), NOTHING, True, FORCED)
    assert m.write(0, item(0.5), NOTHING, True, CHOSEN)[0]["type"] == "stretch"
    assert m.write(0, item(0.5), GAIN, True, CHOSEN)[0]["type"] == "mark-unreliable"     # wrong, unexplained


@pytest.mark.parametrize("far,layer", [({"t15": 0.9}, "details"), ({"t19": 0.9}, "details"),
                                       ({"t8": 0.9, "t3": 0.9}, "parts"), ({"t3": 0.9, "t0": 0.1}, "object"),
                                       ({"t1": 0.9}, "context"), ({"t9": 0.9, "t12": 0.1}, "details")])
def test_blame_starts_at_details_taste_included_and_moves_outward(far, layer):
    m = fresh()
    m.write("unknown", item(0.5), GAIN, True, FORCED)
    ev = m.write(0, item(0.5, **far), POISON, True, CHOSEN)
    assert ev[-1]["type"] == "split" and ev[-1]["layer"] == layer and ev[-1]["parent_slot"] == 0


def test_a_split_raises_the_blamed_layers_traits_on_the_guessed_kind_then_the_child_copies():
    m = fresh()
    m.write("unknown", item(0.5), GAIN, True, FORCED)
    parent = m.kinds[0]
    parent.tenths[12] = 9
    ev = m.write(0, item(0.5, t12=0.9, t13=0.1, t7=0.9), POISON, False, FORCED)
    assert ev == [{"type": "split", "trigger": FORCED, "slot": 1, "parent_slot": 0, "layer": "details",
                   "weight_deltas": [[0, 12, 1], [0, 13, 2]]}]
    assert parent.tenths[12] == 10 and parent.tenths[13] == 7 and parent.tenths[7] == 5     # parts not touched (M12)
    child = m.kinds[1]
    assert list(child.tenths) == list(parent.tenths) and child.tenths is not parent.tenths  # (KT-72)
    assert child.lo[12] == pytest.approx(0.9 - W) and child.eats == [[-1, False]] and child.reliability == 20
    assert child.wins == 0
    assert parent.eats == [[1, True]] and parent.lo[12] == pytest.approx(0.5 - W)     # records never cross a split


def test_an_unexplained_mistake_marks_the_kind_and_goes_on_its_record():
    m = fresh()
    m.write("unknown", item(0.5), GAIN, True, FORCED)
    k = m.kinds[0]
    before = (k.lo.copy(), k.hi.copy(), k.tenths.copy())
    ev = m.write(0, item(0.52), POISON, False, CHOSEN)
    assert ev == [{"type": "mark-unreliable", "trigger": CHOSEN, "slot": 0, "parent_slot": None, "layer": None,
                   "weight_deltas": []}]
    assert k.reliability == 15 and k.eats == [[1, True], [-1, False]]
    assert all((a == b).all() for a, b in zip(before, (k.lo, k.hi, k.tenths)))
    for _ in range(5):
        m.write(0, item(0.52), POISON, False, CHOSEN)
    assert k.reliability == 0                                 # never below 0


def _full(m):
    for s in range(K.SLOTS):
        m.write("unknown", item(s / 100), GAIN, True, FORCED)
    assert len(m.kinds) == K.SLOTS


def test_a_full_memory_forgets_the_kind_with_fewest_confirmed_wins_lowest_slot_first():
    m = fresh()
    _full(m)
    m.write(0, item(0.0), GAIN, True, CHOSEN)                 # slot 0 gets a confirmed win
    ev = m.write("unknown", item(0.95), GAIN, True, FORCED)
    assert [e["type"] for e in ev] == ["forget", "new"]
    assert ev[0]["slot"] == 1 and ev[1]["slot"] == 1          # the lowest slot with no win; its slot is reused
    assert len(m.kinds) == K.SLOTS


def test_among_equal_wins_the_oldest_last_win_goes():
    m = fresh()
    _full(m)
    for s in range(K.SLOTS):
        m.kinds[s].wins = 1
    m.kinds[30].last_win, m.kinds[7].last_win = 1, 1
    for s in range(K.SLOTS):
        if s not in (7, 30):
            m.kinds[s].last_win = 2 + s
    ev = m.write("unknown", item(0.95), GAIN, True, FORCED)
    assert ev[0] == {"type": "forget", "trigger": FORCED, "slot": 7, "parent_slot": None, "layer": None,
                     "weight_deltas": []}


def test_forgetting_comes_after_the_split_child_copies_and_may_take_the_parent():
    m = fresh()
    _full(m)
    m.kinds[0].tenths[15] = 8
    ev = m.write(0, item(0.0, t15=0.9), POISON, True, FORCED)  # slot 0 is wrong, and has the fewest wins
    assert [e["type"] for e in ev] == ["forget", "split"]
    assert ev[0]["slot"] == 0 and ev[1]["slot"] == 0 and ev[1]["parent_slot"] == 0     # (KT-75)
    assert m.kinds[0].tenths[15] == 10 and m.kinds[0].eats == [[-1, True]]


def test_kinds_never_merge():
    m = fresh()
    m.write("unknown", item(0.5), GAIN, True, FORCED)
    m.write("unknown", item(0.5), GAIN, True, FORCED)        # the same item again, judged unknown
    assert len(m.kinds) == 2


def test_the_dump_passes_the_harness_check():
    m = fresh()
    m.write("unknown", item(0.5), GAIN, True, FORCED)
    m.write(0, item(0.5, t15=0.9), POISON, False, FORCED)
    d = m.dump()
    protocol.check_dump(d, tower_minds(None)[-1])
    assert [c["slot"] for c in d["candidates"]] == [0, 1]
    assert d["candidates"][0]["weights_tenths"][15] == 7 and d["candidates"][0]["reliability"] == 1.0
    assert all(isinstance(x, int) for x in d["candidates"][0]["weights_tenths"])


def test_a_kind_stores_every_trait_taste_included():
    k = Kind(item(0.3), W, np.full(K.N_TRAITS, K.WEIGHT_START), 1, True)
    assert k.lo.shape == (22,) and k.founding_class() == 1 and k.above_flags() == [True]
