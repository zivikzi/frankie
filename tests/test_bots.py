"""Every bot's rule on hand-made items (section 4, KT-05, KT-97, KT-100).

Readings are built around 0.5 with offsets in whole noise widths, kept well
away from each bound (half a noise width or more), so these tests check the
rules, not floating-point rounding at a bound.
"""

import numpy as np
import pytest

from baselines import bots
from baselines import rules as K
from world import traits
from world.constants import NOISE_WIDTH

GOOD, BAD, NOTHING = 15000, -20000, 0


def reading(**offsets_nw):
    """A reading of the 18 visible traits: 0.5 everywhere, moved by whole noise widths on named traits."""
    r = np.full(18, 0.5)
    for name, nw in offsets_nw.items():
        r[traits.INDEX[name]] += nw * NOISE_WIDTH
    return r


def make(cls, **params):
    return cls({"reserve_milli": 30000, "boldness": 0.3, "params": params})


def feed(bot, items):
    """Store items as forced tastes: decide, land, write, as the harness does."""
    for r, outcome in items:
        bot.decide(r, 40000)
        bot.land(outcome, 40000 + outcome, np.zeros(4))
        bot.write()
    return bot


def eats(bot, r, energy=40000):
    return bot.decide(r, energy)["action"] == "eat"


def warmup(n=40, outcome=NOTHING):
    return [(reading(scene=20 + k), outcome) for k in range(n)]


# ---------------------------------------------------------------- shared rules

def test_an_empty_memory_eats_and_says_so():
    for cls in (bots.B1nBot, bots.B1t, bots.B2, bots.G04, bots.G17):
        d = make(cls).decide(reading(), 40000)
        assert d["action"] == "eat" and d["log"] == {"undefined": True}


def test_ties_go_to_the_most_recent_item():
    b = feed(make(bots.B1nBot), [(reading(), GOOD), (reading(), BAD)])
    assert not eats(b, reading())
    b = feed(make(bots.B1nBot), [(reading(), BAD), (reading(), GOOD)])
    assert eats(b, reading())
    assert K.nearest(np.array([1.0, 0.5, 0.5, 2.0])) == 2


def test_good_means_above_zero():
    b = feed(make(bots.B1nBot), [(reading(), NOTHING)])
    assert not eats(b, reading())


def test_distances_are_mean_absolute_differences_in_noise_widths():
    stored = np.vstack([reading(size=4, lobes=-2), reading()])
    d = K.mean_nw(stored, reading(), K.OBSERVABLE)
    assert d[0] == pytest.approx(6 / 18) and d[1] == 0.0
    assert K.mean_nw(stored, reading(), K.SURFACE)[0] == pytest.approx(6 / 4)


def test_exact_means_within_five_on_every_trait():
    stored = np.vstack([reading(sheen=4.5), reading(sheen=5.5)])
    assert list(K.exact(stored, reading())) == [True, False]


def test_no_bot_reads_energy():
    items = warmup() + [(reading(stem=1), GOOD), (reading(stem=30), BAD)] * 4
    probes = [reading(stem=k) for k in (0, 2, 15, 29, 40)]
    for name, cls in [("B1n-bot", bots.B1nBot), ("B1t", bots.B1t), ("B2", bots.B2), ("G01", bots.G01),
                      ("G04", bots.G04), ("G05", bots.G05), ("G06", bots.G06), ("G07", bots.G07),
                      ("G08", bots.G08), ("G09", bots.G09), ("G17", bots.G17)]:
        b = feed(make(cls), items)
        for p in probes:
            assert eats(b, p, 0) == eats(b, p, 10**9), name


# ---------------------------------------------------------------- one bot at a time

def test_b1n_bot_r_eats_only_within_its_radius():
    items = [(reading(stem=54), GOOD)]          # mean distance 54 / 18 = 3 noise widths
    assert not eats(feed(make(bots.B1nBotR, radius=2), items), reading())
    assert eats(feed(make(bots.B1nBotR, radius=4), items), reading())
    assert eats(feed(make(bots.B1nBotR, radius=None), items), reading())
    assert not eats(feed(make(bots.B1nBotR, radius=None), [(reading(stem=54), BAD)]), reading())


def test_b1t_skips_exact_matches_of_bad_items_only():
    b = feed(make(bots.B1t), [(reading(), BAD)])
    assert not eats(b, reading(spots=4.5))
    assert eats(b, reading(spots=5.5))


def test_b2_eats_by_surface_distance_to_good_items():
    b = feed(make(bots.B2), [(reading(), BAD)])
    assert not eats(b, reading())                  # no good item stored: skip
    b = feed(make(bots.B2), [(reading(size=39, stem=200), GOOD)])
    assert eats(b, reading())                      # surface 39 / 4 = 9.75; parts don't count
    b = feed(make(bots.B2), [(reading(size=41), GOOD)])
    assert not eats(b, reading())                  # 10.25


def test_b2e_reads_only_the_core_traits_one_by_one():
    core = [traits.INDEX[n] for n in ("lobes", "stem", "sheen", "smell_2")]
    b = feed(make(bots.B2e, core=core), [(reading(lobes=7.5, scene=100, size=80), GOOD)])
    assert eats(b, reading())
    b = feed(make(bots.B2e, core=core), [(reading(lobes=8.5), GOOD)])
    assert not eats(b, reading())
    b = feed(make(bots.B2e, core=core), [(reading(), BAD)])
    assert not eats(b, reading())
    with pytest.raises(ValueError):
        make(bots.B2e, core=[18, 19, 20, 21])


def test_g01_always_eats():
    assert eats(feed(make(bots.G01), [(reading(), BAD)] * 3), reading())


def test_g04_eats_only_exact_matches_of_good_items():
    b = feed(make(bots.G04), [(reading(), GOOD), (reading(texture=20), BAD)])
    assert eats(b, reading(texture=4.5))
    assert not eats(b, reading(texture=5.5))
    assert not eats(b, reading(texture=20))


def test_g05_needs_h1_and_refuses_what_looks_like_it():
    b = feed(make(bots.G05), warmup())
    d = b.decide(reading(), 40000)
    assert d["action"] == "eat" and d["log"] == {"undefined": True}
    feed(b, [(reading(), GOOD)])                    # h1, the 41st item
    assert eats(b, reading(stem=4.5))               # an exact copy of h1
    assert not eats(b, reading(stem=10))            # near h1 on the surface, not a copy
    assert eats(b, reading(size=41))                # surface distance 10.25 from h1
    assert not eats(b, reading(size=39, stem=10))   # 9.75


def test_g06_weights_each_trait_by_its_rarity():
    # Near the probe, stem is rare among the stored items (weight 2/3) and spots common (1/3), so G06's
    # nearest item is the good one, where plain B1n-bot ties and takes the most recent, bad item.
    items = [(reading(stem=0, spots=20), GOOD), (reading(stem=20, spots=0), BAD), (reading(stem=20, spots=1), BAD)]
    probe = reading()
    assert eats(feed(make(bots.G06), items), probe)
    assert not eats(feed(make(bots.B1nBot), items[:2]), probe)


def test_g07_picks_the_trait_that_sorts_the_teaching_items_best():
    teach = []
    for k in range(4):
        teach.append((reading(thorns=0, leaves=k * 3), GOOD))
        teach.append((reading(thorns=30, leaves=k * 3), BAD))
    b = feed(make(bots.G07), warmup() + teach)
    d = b.decide(reading(thorns=7.5), 40000)
    assert d["log"]["traits"] == [traits.INDEX["thorns"]] and d["log"]["score"] == 8
    assert d["action"] == "eat"
    assert not eats(b, reading(thorns=8.5))


def test_g07_ties_keep_the_lower_trait_number():
    teach = []
    for k in range(4):
        teach.append((reading(stem=0, spots=0), GOOD))
        teach.append((reading(stem=30, spots=30), BAD))
    b = feed(make(bots.G07), warmup() + teach)
    assert b.decide(reading(), 40000)["log"]["traits"] == [traits.INDEX["stem"]]


def test_g07_uses_only_the_teaching_items():
    bad_warmup = [(reading(stem=0), BAD) for _ in range(40)]
    teach = [(reading(stem=0), GOOD), (reading(stem=30), BAD)] * 4
    b = feed(make(bots.G07), bad_warmup + teach)
    assert eats(b, reading(stem=1))


def test_g08_needs_both_traits_of_the_best_pair():
    teach = []
    for k in range(4):
        teach += [(reading(stem=0, spots=0), GOOD), (reading(stem=30, spots=0), BAD),
                  (reading(stem=0, spots=30), BAD)]
    b = feed(make(bots.G08), warmup() + teach[:8])
    d = b.decide(reading(), 40000)
    assert d["log"]["traits"] == [traits.INDEX["stem"], traits.INDEX["spots"]]
    assert d["action"] == "eat"
    assert not eats(b, reading(stem=30))
    assert not eats(b, reading(spots=30))


def test_g09_eats_in_h1s_scene():
    b = feed(make(bots.G09), warmup() + [(reading(), BAD)])
    assert eats(b, reading(scene=4.5, stem=50))
    assert not eats(b, reading(scene=5.5))


def test_g16_matches_on_parts_and_details_only():
    b = feed(make(bots.G16, radius=4), [(reading(scene=100, size=100), GOOD)])
    assert eats(b, reading())
    b = feed(make(bots.G16, radius=4), [(reading(stem=60), GOOD)])       # 60 / 12 = 5 noise widths
    assert not eats(b, reading())


def test_g17_refuses_near_copies_once_triggered():
    b = feed(make(bots.G17), [(reading(), GOOD)])
    assert eats(b, reading(stem=60))                 # mean 3.3: near, but not triggered yet
    feed(b, [(reading(stem=120), BAD)])               # mean 6.7 from the good item: triggers
    d = b.decide(reading(stem=60), 40000)
    assert d["log"]["triggered"] and d["log"]["near_copy_refused"] and d["action"] == "skip"
    assert eats(b, reading(stem=4.5))                 # an exact match is not a near-copy


def test_g17_is_not_triggered_by_a_far_bad_item():
    b = feed(make(bots.G17), [(reading(), GOOD), (reading(stem=200), BAD)])     # 11.1 away
    assert not b.decide(reading(), 40000)["log"]["triggered"]


def test_g18_is_g16_plus_g17s_refusal_over_all_traits():
    b = feed(make(bots.G18, radius=24), [(reading(scene=100), GOOD)])
    assert eats(b, reading())                         # G16 ignores scene; not triggered
    feed(b, [(reading(scene=100, stem=120), BAD)])
    d = b.decide(reading(scene=100, stem=30), 40000)
    assert d["log"]["triggered"] and d["action"] == "skip"
