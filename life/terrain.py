"""The land: a smooth height map and its regions (conventional).

Heights come from value noise summed over a few octaves (fractal value
noise, a standard terrain method). Regions follow the land: the lowest
ground is marsh, the highest is rocky, and the middle is split between
meadow and forest by a second noise field.
"""

import numpy as np

from life import config as C


def _smooth(t):
    return t * t * (3.0 - 2.0 * t)


def value_noise(rng, n, cells):
    """One octave: random values on a (cells + 1)^2 lattice, smoothly interpolated onto an n x n grid."""
    lattice = rng.random((cells + 1, cells + 1))
    u = np.linspace(0.0, cells, n, endpoint=True)
    i = np.minimum(u.astype(int), cells - 1)
    f = _smooth(u - i)
    a = lattice[i][:, i]
    b = lattice[i][:, i + 1]
    c = lattice[i + 1][:, i]
    d = lattice[i + 1][:, i + 1]
    fx = f[None, :]
    fz = f[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz


def fractal(rng, n, base_cells, octaves, persistence):
    out = np.zeros((n, n))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        out += amp * value_noise(rng, n, base_cells * (2 ** o))
        total += amp
        amp *= persistence
    out /= total
    lo, hi = out.min(), out.max()
    return (out - lo) / (hi - lo)


class Terrain:
    """Heights on a GRID x GRID lattice 1 m apart; row index is z, column index is x."""

    def __init__(self, rng):
        n = C.GRID
        self.n = n
        self.cell = C.WORLD_SIZE / (n - 1)
        h = fractal(rng, n, C.NOISE_BASE_CELLS, C.NOISE_OCTAVES, C.NOISE_PERSISTENCE)
        self.height = (h ** 1.4) * C.HEIGHT_MAX           # flatter valleys, steeper tops
        split = fractal(rng, n, 3, 3, 0.5)
        order = np.sort(self.height.ravel())
        low = order[int(C.MARSH_BELOW * (order.size - 1))]
        high = order[int(C.ROCKY_ABOVE * (order.size - 1))]
        region = np.where(split > 0.5, 1, 0)              # 0 meadow, 1 forest
        region = np.where(self.height <= low, 2, region)  # 2 marsh
        region = np.where(self.height >= high, 3, region) # 3 rocky
        self.region = region.astype(np.int8)

    # -------------------------------------------------------------- lookups

    def height_at(self, x, z):
        """Bilinear height at world position(s) x, z (scalars or arrays)."""
        gx = np.clip(np.asarray(x, dtype=float) / self.cell, 0.0, self.n - 1.000001)
        gz = np.clip(np.asarray(z, dtype=float) / self.cell, 0.0, self.n - 1.000001)
        i = gx.astype(int)
        j = gz.astype(int)
        fx = gx - i
        fz = gz - j
        h = self.height
        top = h[j, i] * (1 - fx) + h[j, i + 1] * fx
        bot = h[j + 1, i] * (1 - fx) + h[j + 1, i + 1] * fx
        out = top * (1 - fz) + bot * fz
        return float(out) if np.ndim(out) == 0 else out

    def region_at(self, x, z):
        i = int(np.clip(round(x / self.cell), 0, self.n - 1))
        j = int(np.clip(round(z / self.cell), 0, self.n - 1))
        return int(self.region[j, i])

    def cells_of(self, region):
        """Grid positions (x, z) in metres of every cell in a region."""
        j, i = np.nonzero(self.region == region)
        return np.stack([i * self.cell, j * self.cell], axis=1)

    def line_of_sight(self, ax, az, ah, bx, bz, bh):
        """True if the straight line from (ax, az, height ah) to (bx, bz, height bh) clears the ground."""
        d = float(np.hypot(bx - ax, bz - az))
        k = int(d / C.SIGHT_SAMPLE_M)
        if k < 2:
            return True
        t = np.linspace(0.0, 1.0, k + 1)[1:-1]
        ground = self.height_at(ax + (bx - ax) * t, az + (bz - az) * t)
        line = ah + (bh - ah) * t
        return bool(np.all(ground < line))
