"""The 22-trait schema of the kill-test bench (KT-01, LEDGER W15).

Every object is 22 numbers from 0 to 1 (PLACEHOLDER-57). The names follow
W15; they are labels only, so the 4 smell channels are 4 independent numbers
(KT-43). Taste is known only after eating (FORBIDDEN 29) and counts as a
detail trait for the tower and the memory rule (KT-01).
"""

CONTEXT = ("scene", "host")
OBJECT = ("coarse_hue", "size", "roundness", "lobes")
PARTS = ("stem", "leaves", "spots", "thorns", "sticker_mark")
DETAILS = ("exact_hue", "sheen", "texture", "smell_1", "smell_2", "smell_3", "smell_4")
TASTE = ("sweet", "sour", "bitter", "salty")

TRAITS = CONTEXT + OBJECT + PARTS + DETAILS + TASTE
N_TRAITS = len(TRAITS)
INDEX = {name: i for i, name in enumerate(TRAITS)}

# Which layer each trait belongs to, for the tower (section 2 table).
# Taste is listed apart because it is never visible before eating.
LAYER_OF = {}
for _layer, _names in (("context", CONTEXT), ("object", OBJECT), ("parts", PARTS),
                       ("details", DETAILS), ("taste", TASTE)):
    for _name in _names:
        LAYER_OF[_name] = _layer

SCENE = INDEX["scene"]
HOST = INDEX["host"]
COARSE_HUE = INDEX["coarse_hue"]
SIZE = INDEX["size"]
EXACT_HUE = INDEX["exact_hue"]
SWEET = INDEX["sweet"]
SOUR = INDEX["sour"]

# "Observable" means context, object, parts and details, never taste (KT-05).
OBSERVABLE = tuple(INDEX[n] for n in CONTEXT + OBJECT + PARTS + DETAILS)
TASTE_INDICES = tuple(INDEX[n] for n in TASTE)

# Surface distance uses the object-layer traits (PLACEHOLDER-91).
SURFACE = tuple(INDEX[n] for n in OBJECT)

# The 13 traits a core trait may be drawn from: roundness, lobes, the 5 parts
# traits and the 6 details traits other than exact hue (KT-02).
CORE_ELIGIBLE = tuple(
    INDEX[n] for n in ("roundness", "lobes") + PARTS + DETAILS if n != "exact_hue"
)

# Every trait except exact hue gets a range in a kind record (KT-01, KT-02).
RANGED = tuple(i for i in range(N_TRAITS) if i != EXACT_HUE)

assert N_TRAITS == 22
assert len(CORE_ELIGIBLE) == 13
assert len(OBSERVABLE) == 18
