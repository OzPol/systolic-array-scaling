#!/usr/bin/env python3
"""Generate test vectors and independent full-width reference results.

Output: tb/vectors/vec_n08.txt, vec_n16.txt, MANIFEST.txt
File format (one hex token per line, so VHDL textio can read it):
  line 1          : number of cases (decimal)
  per case        : N*N lines of A (4 hex digits, row-major two's complement),
                    N*N lines of B, then N*N lines of C (9 hex digits, 36-bit)
Case order is fixed; CASE_NAMES[PERF_CASE] is the fixed-seed random case used
as the principal performance workload.
"""
import hashlib
import pathlib
import random

SEED = 5764
CASE_NAMES = ["zero", "identity", "min_x_min", "min_x_max", "mixed_sign",
              "random_perf", "random_2", "random_3"]
PERF_CASE = 5


def matmul(a, b, n):
    return [sum(a[i * n + k] * b[k * n + j] for k in range(n)) for i in range(n) for j in range(n)]


def cases(n):
    rng = random.Random(SEED + n)
    rnd = lambda: [rng.randint(-32768, 32767) for _ in range(n * n)]
    ident = [1 if i == j else 0 for i in range(n) for j in range(n)]
    mixed_a = [(-1) ** (i + j) * (1000 + 37 * i + j) for i in range(n) for j in range(n)]
    mixed_b = [(-1) ** (i * j + 1) * (32767 - 13 * i - 7 * j) for i in range(n) for j in range(n)]
    return [
        ([0] * (n * n), rnd()),
        (ident, rnd()),
        ([-32768] * (n * n), [-32768] * (n * n)),
        ([-32768] * (n * n), [32767] * (n * n)),
        (mixed_a, mixed_b),
        (rnd(), rnd()),
        (rnd(), rnd()),
        (rnd(), rnd()),
    ]


def main():
    out = pathlib.Path(__file__).resolve().parent.parent / "tb" / "vectors"
    out.mkdir(parents=True, exist_ok=True)
    manifest = [f"seed_base={SEED}", f"perf_case_index={PERF_CASE}", "cases=" + ",".join(CASE_NAMES)]
    for n in (8, 16):
        lines = [str(len(CASE_NAMES))]
        for a, b in cases(n):
            c = matmul(a, b, n)
            assert all(-(1 << 35) <= x < (1 << 35) for x in c)  # fits 36-bit accumulator
            lines += [f"{x & 0xFFFF:04x}" for x in a]
            lines += [f"{x & 0xFFFF:04x}" for x in b]
            lines += [f"{x & ((1 << 36) - 1):09x}" for x in c]
        path = out / f"vec_n{n:02d}.txt"
        path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
        manifest.append(f"{path.name} sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
    (out / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="ascii", newline="\n")
    print("\n".join(manifest))


if __name__ == "__main__":
    main()
