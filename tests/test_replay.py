"""Bit-for-bit replay (KT-34, I05): golden values that every machine must reproduce.

CI runs these on Linux (x86 and ARM), macOS and Windows. A change to the
counter layout, the draw order or the noise arithmetic changes them.
"""

import decimal
import hashlib
import json
import math
import subprocess
import sys

from philox_reference import philox4x64, words
from world import keys
from world import run_plan as rp
from world.streams import box_muller, counter, sensor_noise, to_unit

KEY = 0x0123456789ABCDEF_FEDCBA9876543210

GOLDEN_BOX_MULLER = [
    (("0x1.0000000000000p-1", "0x1.0000000000000p-1"), "-0x1.81d04fb4142e5p-7"),
    (("0x1.fffffffffffffp-1", "0x0.0p+0"), "0x1.5f18851fe880ap-4"),
    (("0x1.f9add3739635fp-4", "0x1.f9add3c0e56b8p-1"), "0x1.4f6c892c27677p-8"),
    (("0x1.ccccccccccccdp-1", "0x1.3333333333333p-2"), "-0x1.b2986ce6cb6a7p-8"),
    (("0x1.3333333333333p-2", "0x1.f972474538ef3p-4"), "0x1.8b4f8df0cf8a5p-8"),
    (("0x1.0000000000000p-1", "0x1.0000000000000p-2"), "0x1.a4ebeea7d3e8dp-140"),   # cos near 0
]


def test_box_muller_golden_values():
    for (u1, u2), want in GOLDEN_BOX_MULLER:
        assert box_muller(float.fromhex(u1), float.fromhex(u2)).hex() == want


def test_box_muller_ignores_the_callers_decimal_settings():
    """No decimal setting made elsewhere in the process changes a reading or trips on one."""
    with decimal.localcontext() as ctx:
        ctx.prec, ctx.Emin, ctx.rounding = 3, -5, decimal.ROUND_DOWN
        for signal in (decimal.FloatOperation, decimal.Inexact, decimal.Rounded):
            ctx.traps[signal] = True
        for (u1, u2), want in GOLDEN_BOX_MULLER:
            assert box_muller(float.fromhex(u1), float.fromhex(u2)).hex() == want
        assert not any(ctx.flags.values())


def test_box_muller_ignores_a_changed_default_context():
    """Nor does a decimal.DefaultContext changed before the world is imported."""
    code = ("import decimal, json, sys\n"
            "dc = decimal.DefaultContext\n"
            "dc.prec, dc.Emin, dc.Emax, dc.rounding = 2, -3, 3, decimal.ROUND_UP\n"
            "dc.traps[decimal.Inexact] = dc.traps[decimal.FloatOperation] = dc.traps[decimal.Rounded] = True\n"
            "from world.streams import box_muller\n"
            "pairs = json.loads(sys.argv[1])\n"
            "print(json.dumps([box_muller(float.fromhex(a), float.fromhex(b)).hex() for a, b in pairs]))\n")
    pairs = [list(p) for p, _ in GOLDEN_BOX_MULLER]
    r = subprocess.run([sys.executable, "-c", code, json.dumps(pairs)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == [want for _, want in GOLDEN_BOX_MULLER]


def test_box_muller_agrees_with_the_float_formula():
    for i in range(1, 2000):
        u1, u2 = (i * 7919 % 2003) / 2003, (i * 104729 % 2011) / 2011
        want = 0.01 * math.sqrt(-2 * math.log(1 - u1)) * math.cos(2 * math.pi * u2)
        assert abs(box_muller(u1, u2) - want) < 1e-16


def test_noise_reads_the_counter_of_its_trait_place_and_replica():
    for place, replica, trait in ((1, 0, 0), (433, 2003, 7), (652, 9020, 21)):
        w = philox4x64(words(counter(trait, place, 0, replica), 4), words(KEY, 2))
        assert sensor_noise(KEY, place, replica, trait) == box_muller(to_unit(w[0]), to_unit(w[1]))


def test_golden_noise_fingerprint():
    h = hashlib.sha256()
    for place in range(1, 101):
        for trait in range(22):
            h.update(sensor_noise(KEY, place, 1002, trait).hex().encode())
    assert h.hexdigest() == "d6890312e77e74ea602e65a48ae182e7c5178ad5d8f9057f4fb42bf9b22bb452"


def test_golden_run_plan_fingerprint():
    p = rp.generate_run("practice", keys.tuning_set_key(), 200_001, 1)
    h = hashlib.sha256()
    for o in p.all_objects():
        h.update(o.label.encode())
        h.update(repr(o.values).encode())
        h.update(o.hue_offset.hex().encode())
    h.update(repr((p.reserve_milli, p.boldness.hex(), p.trait_order, p.warmup_order)).encode())
    assert h.hexdigest() == "74e682579703ee3f9b9c7b77c2d683b0c4377d9c7d5ee2b0899952517bfffd99"
    assert len(p.log) == 25
