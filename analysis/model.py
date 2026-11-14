"""Closed-form predictions, kept separate from measured counters."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CycleModel:
    n: int
    p: int
    b: int
    tiles: int
    useful_equivalent_cycles: int
    fill_drain_cycles: int
    capture_cycles: int
    stall_cycles: int
    advance_cycles: int
    compute_cycles: int
    readout_cycles: int
    total_cycles: int
    useful_macs: int
    input_words: int

    def as_dict(self):
        return asdict(self)


def predict(n, p, b):
    if n not in (8, 16) or p not in (2, 4, 8) or b <= 0 or n % p:
        raise ValueError('expected N=8/16, P=2/4/8, positive B, and P dividing N')
    tiles = (n // p)**2
    steps = n + 2*p - 2
    stalls_per_tile = 0
    for t in range(steps):
        words = 2 * sum(0 <= t-i < n for i in range(p))
        stalls_per_tile += max(0, (words+b-1)//b - 1)
    useful = tiles*n
    fill = tiles*(2*p-2)
    stalls = tiles*stalls_per_tile
    advance = tiles*steps
    compute = advance + stalls + tiles
    return CycleModel(n, p, b, tiles, useful, fill, tiles, stalls, advance,
                      compute, n*n, compute+n*n, n**3, 2*n*p*tiles)
