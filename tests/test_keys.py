"""Keys from a set key down to each stream (KT-14, KT-31)."""

import hashlib
import hmac
import re
from pathlib import Path

import pytest

from world import keys

ROOT = Path(__file__).resolve().parents[1]


def test_tuning_key_is_the_committed_one():
    lines = (ROOT / "kill-test" / "TUNING_KEY.md").read_text(encoding="utf-8").splitlines()
    committed = [ln.strip() for ln in lines if re.fullmatch(r"[0-9a-f]{64}", ln.strip())]
    assert committed == [keys.TUNING_KEY_HEX]
    assert keys.tuning_set_key() == bytes.fromhex(committed[0])
    assert len(keys.tuning_set_key()) == 32


def test_family_run_and_stream_keys_follow_kt31():
    set_key = keys.tuning_set_key()
    fam = hmac.new(set_key, b"family/7", hashlib.sha256).digest()
    run = hmac.new(fam, b"run/3", hashlib.sha256).digest()
    assert keys.family_key(set_key, 7) == fam
    assert keys.run_key(fam, 3) == run
    full = hmac.new(run, b"world", hashlib.sha256).digest()
    assert keys.stream_key(run, "world") == int.from_bytes(full[:16], "little")
    assert keys.stream_key(run, "world") != keys.stream_key(run, "sensor_noise")


def test_numbers_start_at_one():
    with pytest.raises(ValueError):
        keys.family_key(keys.tuning_set_key(), 0)
    with pytest.raises(ValueError):
        keys.run_key(b"x" * 32, 0)


def test_kill_run_key_is_sha256_of_the_hex_text():
    block_hash = "0" * 58 + "abcdef"
    assert keys.kill_run_set_key(block_hash) == hashlib.sha256(block_hash.encode("ascii")).digest()


@pytest.mark.parametrize("bad", ["0" * 63, "0" * 65, "A" * 64, "0" * 63 + "\n", "g" * 64, " " + "0" * 63])
def test_kill_run_key_refuses_anything_but_64_lowercase_hex(bad):
    with pytest.raises(ValueError):
        keys.kill_run_set_key(bad)
