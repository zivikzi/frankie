"""The trait schema (KT-01, KT-02) and the rule that every constant cites its row (FORBIDDEN 28)."""

import re
from pathlib import Path

from world import traits

ROOT = Path(__file__).resolve().parents[1]


def test_schema_counts():
    assert traits.N_TRAITS == 22
    assert (len(traits.CONTEXT), len(traits.OBJECT), len(traits.PARTS), len(traits.DETAILS), len(traits.TASTE)) \
        == (2, 4, 5, 7, 4)
    assert len(traits.OBSERVABLE) == 18
    assert set(traits.OBSERVABLE).isdisjoint(traits.TASTE_INDICES)
    assert traits.TRAITS[traits.SWEET] == "sweet" and traits.TRAITS[traits.SOUR] == "sour"


def test_core_eligible_traits():
    names = {traits.TRAITS[i] for i in traits.CORE_ELIGIBLE}
    assert len(names) == 13
    assert names == {"roundness", "lobes"} | set(traits.PARTS) | (set(traits.DETAILS) - {"exact_hue"})
    assert not names & (set(traits.CONTEXT) | set(traits.TASTE) | {"coarse_hue", "size", "exact_hue"})


def test_every_trait_but_exact_hue_is_ranged():
    assert set(traits.RANGED) == set(range(22)) - {traits.EXACT_HUE}


CITE = re.compile(r"#.*\b(KT-\d+|PLACEHOLDER-\d+|[MWXDIB]\d+|section \d+)")


def test_every_world_constant_cites_its_row():
    lines = (ROOT / "src" / "world" / "constants.py").read_text().splitlines()
    assigned = [ln for ln in lines if re.match(r"^[A-Z_][A-Z0-9_]* = ", ln)]
    assert len(assigned) > 40
    uncited = [ln for ln in assigned if not CITE.search(ln)]
    assert uncited == []
