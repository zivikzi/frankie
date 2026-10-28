"""A plain-Python Philox4x64, written from the Random123 paper and its reference code.

Used only by the tests, to check NumPy's Philox and the streams built on it.
"""

M0 = 0xD2E7470EE14C6C93
M1 = 0xCA5A826395121157
W0 = 0x9E3779B97F4A7C15
W1 = 0xBB67AE8584CAA73B
MASK = (1 << 64) - 1


def _mulhilo(a, b):
    p = a * b
    return p >> 64, p & MASK


def philox4x64(counter_words, key_words, rounds=10):
    c0, c1, c2, c3 = counter_words
    k0, k1 = key_words
    for r in range(rounds):
        if r:
            k0, k1 = (k0 + W0) & MASK, (k1 + W1) & MASK
        hi0, lo0 = _mulhilo(M0, c0)
        hi1, lo1 = _mulhilo(M1, c2)
        c0, c1, c2, c3 = hi1 ^ c1 ^ k0, lo1, hi0 ^ c3 ^ k1, lo0
    return c0, c1, c2, c3


def words(value, n):
    """An integer split into n 64-bit words, lowest first."""
    return tuple((value >> (64 * i)) & MASK for i in range(n))
