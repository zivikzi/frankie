"""K-F's tower on hand-made cases (D13, M01 to M08, section 6, KT-51 to KT-66).

Most cases run the tower on scripted units: each group's activation at the
end of each step is written into the case, so the timetable, elimination,
attention, objections, holds and the step-30 rule can be checked by hand.
The last cases run TW7's real rate units.
"""

import numpy as np
import pytest

from mind import constants as K
from mind.memory import Kind, Memory
from mind.tower import CENTRES, UNKNOWN, UNSETTLED, Race, fits

W = 0.04
ORDER = list(range(K.N_TRAITS))           # the run's trait order: schema order in these cases
POSITIONS = list(range(K.N_TRAITS))


class Scripted:
    """Units whose activations at each step's end are given; rest() holds a group at 0 until its next step."""

    def __init__(self, script):
        self.script = script                 # step -> list of activations, one per group ("unknown" last)
        self.a = None
        self.n_sub = 0
        self.spikes = 0
        self.inputs_seen = {}

    def bind(self, n_groups):
        self.a = np.zeros(n_groups)
        return self

    def activation(self):
        return self.a.copy()

    def rest(self, g):
        self.a[g] = 0.0

    def substep(self, inputs, live):
        self.n_sub += 1
        if self.n_sub % K.SUBSTEPS == 0:
            step = self.n_sub // K.SUBSTEPS
            self.inputs_seen[step] = inputs.copy()
            row = self.script(step) if callable(self.script) else self.script.get(step, self.script.get("rest"))
            self.a = np.where(live, np.asarray(row, dtype=float), 0.0)


def memory_of(*values, tenths=None):
    m = Memory(K.Settings())
    for i, v in enumerate(values):
        m.kinds[i] = Kind(np.asarray(v, dtype=float), W,
                          np.full(K.N_TRAITS, K.WEIGHT_START) if tenths is None else tenths[i], 1, True)
    return m


def race(memory, values, script, taste_known=False, settings=None, after=False):
    units = Scripted(script).bind(len(memory.kinds) + 1)
    r = Race(memory, values, taste_known, POSITIONS, settings or K.Settings(), units)
    return r.run(after_eating=after), r, units


def flat(v=0.5):
    return np.full(K.N_TRAITS, v)


# ------------------------------------------------------------------ detectors and fit (KT-53)

def test_sixteen_detectors_tile_each_trait():
    assert len(CENTRES) == 16 and CENTRES[0] == 1 / 32 and CENTRES[-1] == 31 / 32


def test_a_trait_fits_when_a_lit_detectors_centre_is_inside_the_range():
    lo, hi = np.zeros((1, K.N_TRAITS)), np.zeros((1, K.N_TRAITS))
    lo[0, 0], hi[0, 0] = 0.34, 0.35            # holds the centre 0.34375, lit by 0.34
    lo[0, 1], hi[0, 1] = 0.335, 0.343          # holds the reading 0.34 but no centre (KT-53's strictness)
    lo[0, 2], hi[0, 2] = 0.40, 0.41            # holds 0.40625, lit by 0.37 since |0.37 - 0.40625| <= 0.04
    values = np.zeros(K.N_TRAITS)
    values[:3] = [0.34, 0.34, 0.37]
    f = fits(values, K.TASTE_FROM, lo, hi, W)
    assert list(f[0, :3]) == [True, False, True]
    values[18] = 0.34                          # taste has no reading before an eat
    lo[0, 18], hi[0, 18] = 0.34, 0.35
    assert not fits(values, K.TASTE_FROM, lo, hi, W)[0, 18]
    assert fits(values, K.N_TRAITS, lo, hi, W)[0, 18]


# ------------------------------------------------------------------ the timetable and checks (KT-51, KT-45)

def test_layers_open_one_step_apart_and_each_test_is_paid_once():
    m = memory_of(flat(0.5), flat(0.5))
    script = {"rest": [1.0, 1.0, 0.0]}         # a lasting tie: nothing wins
    st, r, units = race(m, flat(0.5), script)
    assert r.log["checked"] == {"context": [0, 1], "object": [2, 3, 4, 5], "parts": [6, 7, 8],
                                "details": [11, 12, 13]}
    assert st.checks == 2 * (2 + 4 + 3 + 3)
    # the steady input grows as each layer opens: 0.5 per fitting checked trait (PLACEHOLDER-01)
    assert [units.inputs_seen[s][0] for s in (1, 2, 3, 4, 5)] == [1.0, 3.0, 4.5, 6.0, 6.0]
    assert units.inputs_seen[1][2] == K.NEW_KIND_THRESHOLD        # "unknown" from step 1 (KT-58)


def test_a_tie_that_never_breaks_is_unsettled_and_names_no_kind():
    m = memory_of(flat(0.5), flat(0.5))
    st, _, _ = race(m, flat(0.5), {"rest": [5.0, 5.0, 0.0]})
    assert st.verdict == UNSETTLED and st.settle_step is None


def test_an_empty_memory_ends_unknown_at_step_30():
    m = Memory(K.Settings())
    st, r, _ = race(m, flat(0.5), {"rest": [0.3]})
    assert (st.verdict, st.settle_step, st.checks) == (UNKNOWN, 30, 0)


def test_unknown_alone_wins_once_it_stands_the_margin_above_rest():
    st, _, _ = race(Memory(K.Settings()), flat(0.5), {"rest": [2.0]})
    assert (st.verdict, st.settle_step) == (UNKNOWN, 6)


# ------------------------------------------------------------------ elimination (KT-52)

def test_handovers_drop_candidates_trailing_by_the_margin_and_never_unknown():
    m = memory_of(flat(0.5), flat(0.5), flat(0.5))
    script = {1: [3.0, 1.5, 0.5, 0.2], 2: [3.0, 1.0, 0.0, 0.2], 3: [3.0, 1.0, 0.0, 0.1],
              "rest": [3.0, 1.0, 0.0, 0.0]}
    st, r, _ = race(m, flat(0.5), script)
    assert r.log["eliminated"] == [[1, 2], [2, 1]]            # trailing 3.0 by at least 2, at steps 1 and 2
    # checks: context for 3, object for 2 (one dropped at step 1), parts and details for 1
    assert st.checks == 3 * 2 + 2 * 4 + 1 * 3 + 1 * 3
    assert st.verdict == 0


def test_no_elimination_after_step_3():
    m = memory_of(flat(0.5), flat(0.5))
    script = {1: [1.0, 1.0, 0.0], 2: [1.0, 1.0, 0.0], 3: [1.0, 1.0, 0.0], "rest": [5.0, 1.0, 0.0]}
    _, r, _ = race(m, flat(0.5), script)
    assert r.log["eliminated"] == []


# ------------------------------------------------------------------ attention (PLACEHOLDER-14, KT-54)

def test_attention_pools_weights_by_activation_and_breaks_ties_by_trait_order():
    t0 = np.full(K.N_TRAITS, 5)
    t1 = np.full(K.N_TRAITS, 5)
    t0[9], t0[10] = 9, 0          # kind 0 leans on traits 9 and 10 differently
    t1[9], t1[10] = 0, 9
    t0[16] = 7
    m = memory_of(flat(0.5), flat(0.5), tenths=[t0, t1])
    script = {1: [1.0, 0.5, 0.0], 2: [3.0, 1.5, 0.0], "rest": [3.0, 1.5, 0.0]}
    _, r, _ = race(m, flat(0.5), script)
    # pooled on 9: (3 x 9 + 1.5 x 0)/4.5 = 6, on 10: 3; the rest 5: so 9 first, then 6 and 7 by trait order
    assert r.log["checked"]["parts"] == [6, 7, 9]
    assert r.log["checked"]["details"] == [11, 12, 16]


def test_attention_counts_every_survivor_equally_when_all_are_at_rest():
    t0 = np.full(K.N_TRAITS, 5)
    t1 = np.full(K.N_TRAITS, 5)
    t0[8], t1[8] = 9, 0           # pooled 4.5 on trait 8: below 5
    m = memory_of(flat(0.5), flat(0.5), tenths=[t0, t1])
    _, r, _ = race(m, flat(0.5), {"rest": [0.0, 0.0, 0.0]})
    assert r.log["checked"]["parts"] == [6, 7, 9]


def test_attention_follows_the_runs_trait_order_on_ties():
    m = memory_of(flat(0.5))
    units = Scripted({"rest": [0.0, 0.0]}).bind(2)
    positions = list(range(K.N_TRAITS))
    positions[10], positions[6] = 0, 10          # trait 10 comes first in this run's order
    r = Race(m, flat(0.5), False, positions, K.Settings(), units)
    r.run()
    assert r.log["checked"]["parts"] == [7, 8, 10]


def test_after_an_eat_details_read_all_four_tastes_besides_three_visible_traits():
    m = memory_of(flat(0.5))
    _, r, _ = race(m, flat(0.5), {"rest": [0.0, 0.0]}, taste_known=True, after=True)
    assert r.log["checked"]["details"] == [11, 12, 13, 18, 19, 20, 21]


# ------------------------------------------------------------------ wins, holds and the step-30 rule (KT-10, KT-63, KT-64)

def test_a_win_needs_two_steps_and_settles_four_steps_later():
    m = memory_of(flat(0.5))
    script = {1: [1.0, 0.0], 2: [2.5, 0.0], "rest": [3.0, 0.0]}   # leads by 2 from step 2
    st, _, _ = race(m, flat(0.5), script)
    assert (st.verdict, st.settle_step) == (0, 7)                  # wins at step 3, settles at 3 + 4


def test_the_earliest_settle_is_step_6():
    m = memory_of(flat(0.5))
    st, _, _ = race(m, flat(0.5), {"rest": [9.0, 0.0]})
    assert (st.verdict, st.settle_step) == (0, 6)


def test_a_tie_during_the_hold_breaks_it():
    m = memory_of(flat(0.5), flat(0.5))

    def script(step):
        if step <= 3:
            return [2.0, 2.0, 0.0]          # no lead, so no one is dropped at the handovers
        if step in (7, 8):
            return [4.0, 4.0, 0.0]
        return [4.0, 1.0, 0.0]
    st, _, _ = race(m, flat(0.5), script)
    # wins at step 5 (leads at 4 and 5), the tie at 7 breaks the hold; it wins again at 10 and settles at 14
    assert (st.verdict, st.settle_step) == (0, 14)


def test_a_lead_over_unknown_with_no_win_is_unsettled_at_step_30():
    m = memory_of(flat(0.5), flat(0.5))
    st, _, _ = race(m, flat(0.5), {"rest": [3.0, 3.0, 0.5]})
    assert (st.verdict, st.settle_step) == (UNSETTLED, None)


def test_no_candidate_leading_unknown_at_step_30_means_unknown():
    m = memory_of(flat(0.5), flat(0.5))
    st, _, _ = race(m, flat(0.5), {"rest": [1.0, 1.0, 0.5]})
    assert (st.verdict, st.settle_step) == (UNKNOWN, 30)


def _late(win_from, until=99):
    def script(step):
        if win_from <= step <= until:
            return [5.0, 0.5, 0.0]
        return [1.0, 1.0, 0.0]
    return script


def test_a_hold_running_at_step_30_runs_on_and_settles():
    m = memory_of(flat(0.5), flat(0.5))
    st, _, _ = race(m, flat(0.5), _late(28))       # leads at 28 and 29: wins at 29
    assert (st.verdict, st.settle_step) == (0, 33)  # (KT-64)


def test_a_hold_that_breaks_after_step_30_is_unsettled():
    m = memory_of(flat(0.5), flat(0.5))
    st, _, _ = race(m, flat(0.5), _late(28, until=31))
    assert (st.verdict, st.settle_step) == (UNSETTLED, None)


def test_the_verdict_after_eating_stops_at_step_30():
    m = memory_of(flat(0.5), flat(0.5))
    st, _, _ = race(m, flat(0.5), _late(28), taste_known=True, after=True)
    assert (st.verdict, st.settle_step) == (UNSETTLED, None)      # the hold is cut; candidate 0 leads unknown
    st, _, _ = race(m, flat(0.5), _late(25), taste_known=True, after=True)
    assert (st.verdict, st.settle_step) == (0, 30)                # won at 26, settled at 30 (KT-66)


# ------------------------------------------------------------------ objections (M07, M08, KT-56, KT-57)

def _misfit_on_parts():
    """Kind 0 fits everything but trait 6, a parts trait checked from step 3."""
    m = memory_of(flat(0.5), flat(0.5))
    values = flat(0.5)
    values[6] = 0.9
    m.kinds[1].lo[6], m.kinds[1].hi[6] = 0.86, 0.94
    return m, values


def test_two_steps_of_mismatch_knock_the_leader_down_and_bring_the_eliminated_back():
    m, values = _misfit_on_parts()
    script = {1: [3.0, 0.5, 0.0], 2: [4.0, 1.0, 0.0], 3: [5.0, 1.0, 0.0], 4: [5.0, 1.0, 0.0],
              "rest": [1.0, 4.0, 0.0]}
    st, r, _ = race(m, values, script)
    # kind 1 was dropped at step 1; kind 0 led with trait 6 unfit at steps 3 and 4: an objection at 4
    assert r.log["eliminated"] == [[1, 1]]
    assert r.log["objections"][0] == [4, 0, ["parts"], "reset", [1]]
    # kind 1's tests switch on again for the 12 traits now checked (KT-45)
    assert st.checks == 2 * 2 + 1 * 4 + 1 * 3 + 1 * 3 + 12
    assert st.verdict == 1


def test_a_third_objection_removes_the_leader():
    m, values = _misfit_on_parts()
    st, r, _ = race(m, values, {"rest": [5.0, 3.5, 0.0]})        # kind 1 trails by 1.5: never dropped
    kinds = [o[3] for o in r.log["objections"]]
    assert kinds[:3] == ["reset", "reset", "removed"]
    assert [o[0] for o in r.log["objections"][:3]] == [4, 6, 8]
    assert (st.verdict, st.settle_step) == (1, 13)   # with kind 0 removed at 8, kind 1 leads at 8 and 9


def test_a_mismatch_below_the_threshold_never_objects():
    m, values = _misfit_on_parts()
    st, r, _ = race(m, values, {"rest": [5.0, 1.0, 0.0]}, settings=K.Settings(objection_threshold=0.75))
    assert r.log["objections"] == [] and st.verdict == 0


def test_a_leading_unknown_is_never_objected_to():
    m, values = _misfit_on_parts()
    st, r, _ = race(m, values, {"rest": [0.0, 0.0, 5.0]})
    assert r.log["objections"] == [] and (st.verdict, st.settle_step) == (UNKNOWN, 6)


def test_a_change_of_leader_restarts_the_mismatch_streak():
    m, values = _misfit_on_parts()
    script = {3: [5.0, 1.0, 0.0], 4: [1.0, 5.0, 0.0], 5: [5.0, 1.0, 0.0], "rest": [1.0, 5.0, 0.0]}
    _, r, _ = race(m, values, script)
    assert r.log["objections"] == []


# ------------------------------------------------------------------ the log (KT-69)

def test_the_log_names_the_last_leader_and_who_was_within_the_margin():
    m = memory_of(flat(0.5), flat(0.5), flat(0.5))
    st, _, _ = race(m, flat(0.5), {"rest": [3.0, 2.0, 0.5, 1.5]})
    assert st.log["last_leader"] == 0 and st.log["within_margin"] == [1, UNKNOWN]


# ------------------------------------------------------------------ TW7's rate units (KT-68)

def test_tw7_names_a_perfect_copy_and_calls_an_empty_memory_unknown():
    from twins.entry import RateMaker
    s = K.Settings()
    m = memory_of(flat(0.5), flat(0.2))
    r = Race(m, flat(0.5), False, POSITIONS, s, RateMaker().start(3, s))
    st = r.run()
    assert st.verdict == 0 and 6 <= st.settle_step <= 34 and st.spikes == 0
    empty = Race(Memory(s), flat(0.5), False, POSITIONS, s, RateMaker().start(1, s)).run()
    assert empty.verdict == UNKNOWN


def test_rate_units_settle_toward_their_target_and_push_each_other_down():
    from twins.entry import RateUnits
    s = K.Settings()
    one = RateUnits(1, s, 1, 10)
    live = np.array([True])
    for _ in range(2000):
        one.substep(np.array([1.0]), live)
    scale = K.GROUP_NEURONS / (s.threshold * (1 - K.TRACE_DECAY))
    assert one.activation()[0] == pytest.approx(scale * (1.0 - s.threshold * s.leak))
    two = RateUnits(2, s, 1, 10)
    both = np.array([True, True])
    for _ in range(2000):
        two.substep(np.array([1.0, 1.0]), both)
    assert two.activation()[0] < one.activation()[0]              # each pushes the other down (KT-59)
    two.rest(0)
    assert two.activation()[0] == 0.0
    for _ in range(5):
        two.substep(np.array([1.0, 1.0]), np.array([False, True]))
    assert two.activation()[0] == 0.0                              # a group at rest stays at rest


@pytest.mark.parametrize("bad", [list(range(21)), [0] * 22])
def test_a_trait_order_must_list_every_trait_once(bad):
    from twins.entry import make
    with pytest.raises(ValueError, match="KT-41"):
        make({"reserve_milli": 40000, "boldness": 0.3, "params": {"twin": "TW7"}, "trait_order": bad})
