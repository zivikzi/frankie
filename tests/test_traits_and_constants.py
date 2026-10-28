"""The trait schema (KT-01, KT-02) and the rule that every constant cites its row (FORBIDDEN 28)."""

import ast
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


# A register row (KT-nn, PLACEHOLDER-nn) or a ledger row (B, E, I, M, T, W or X
# and two digits), as FORBIDDEN 28 asks.
CITE = re.compile(r"\b(KT-\d{2}|PLACEHOLDER-\d+|[BEIMTWX]\d{2})\b")


def _numeric_constants(path):
    """Module-level UPPER_CASE names (public or private) assigned a value that holds a number."""
    tree = ast.parse(path.read_bytes())
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not names or not all(re.fullmatch(r"_?[A-Z][A-Z0-9_]*", n) for n in names):
            continue
        if any(isinstance(c, ast.Constant) and type(c.value) in (int, float) for c in ast.walk(node.value)):
            yield names[0], node.lineno


def test_the_citation_pattern():
    assert CITE.search("# drawn from 20 (M33)") and CITE.search("# (KT-81)") and CITE.search("(PLACEHOLDER-45)")
    assert not CITE.search("# (section 5)") and not CITE.search("# the M1 half") and not CITE.search("# B1n-bot")


def test_every_world_constant_cites_its_row():
    uncited = []
    count = 0
    for path in sorted((ROOT / "src" / "world").glob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for name, lineno in _numeric_constants(path):
            count += 1
            here, above = lines[lineno - 1], lines[lineno - 2] if lineno > 1 else ""
            comment = here.split("#", 1)[1] if "#" in here else (above if above.lstrip().startswith("#") else "")
            if not CITE.search(comment):
                uncited.append(f"{path.name}:{lineno} {name}")
    assert count > 60
    assert uncited == []
