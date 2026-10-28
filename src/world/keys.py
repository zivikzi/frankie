"""Keys: from a set key down to the key of each random stream (KT-14, KT-31).

- The tuning set's key is the committed tuning key (kill-test/TUNING_KEY.md),
  decoded from its 64 hex characters to 32 bytes.
- A kill-run set's key is the SHA-256 of the 64 lowercase hex characters that
  Bitcoin Core shows for block N + 6's hash, with no newline. It is read only
  once that block has 6 confirmations.
- Family key = HMAC-SHA256(set key, "family/" + family number).
- Run key = HMAC-SHA256(family key, "run/" + run number).
- A stream's key is the first 128 bits of HMAC-SHA256(family or run key,
  stream name). It is the Philox key (W37).
"""

import hashlib
import hmac
import string

# kill-test/TUNING_KEY.md, committed in Week 0 (commit 886a8ed).
TUNING_KEY_HEX = "4deb9efbd94bfbaf8f1087ea7148c3fb120b4941b26b2ab6ac79c76264fcff0e"

# Stream names (W37 lists world, sensor noise, proposals, teacher, evolution;
# the bench uses the first two).
STREAM_WORLD = "world"
STREAM_SENSOR_NOISE = "sensor_noise"

_HEX = set(string.hexdigits.lower()) - set("ABCDEF")


def tuning_set_key() -> bytes:
    """The tuning set's key: the committed tuning key, decoded to 32 bytes."""
    key = bytes.fromhex(TUNING_KEY_HEX)
    assert len(key) == 32
    return key


def kill_run_set_key(block_hash_hex: str) -> bytes:
    """A kill-run set's key from Bitcoin block N + 6's hash (KT-14, KT-31).

    The hash must be given exactly as Bitcoin Core shows it: 64 lowercase hex
    characters, nothing else.
    """
    if len(block_hash_hex) != 64 or not set(block_hash_hex) <= _HEX:
        raise ValueError("expected the block hash as 64 lowercase hex characters")
    return hashlib.sha256(block_hash_hex.encode("ascii")).digest()


def _hmac(key: bytes, text: str) -> bytes:
    return hmac.new(key, text.encode("ascii"), hashlib.sha256).digest()


def family_key(set_key: bytes, family_number: int) -> bytes:
    if family_number < 1:
        raise ValueError("family numbers start at 1")
    return _hmac(set_key, f"family/{family_number}")


def run_key(fam_key: bytes, run_number: int) -> bytes:
    if run_number < 1:
        raise ValueError("run numbers start at 1")
    return _hmac(fam_key, f"run/{run_number}")


def stream_key(parent_key: bytes, stream_name: str) -> int:
    """The 128-bit Philox key of one stream, as an integer.

    The 16 bytes are read little-endian, so bytes 0-7 are the key's first
    64-bit word and bytes 8-15 its second.
    """
    return int.from_bytes(_hmac(parent_key, stream_name)[:16], "little")
