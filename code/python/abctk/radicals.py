# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk.radicals — the radical, and the sieves that make it computable in bulk.

The radical rad(n) = prod_{p | n} p is the only arithmetic function the abc
conjecture mentions, and essentially all of the computational difficulty of
searching for good abc triples is the difficulty of computing rad(n) for every
n in a long range.  Factoring each n separately is hopeless; the right tool is
a linear sieve that accumulates the radical of every n <= N in one pass.
"""

from __future__ import annotations

import math
from typing import Dict, Iterator, List


def prime_factors(n: int) -> Dict[int, int]:
    """Return the factorisation of n > 0 as {prime: exponent}.

    Trial division by 2, 3 and then the 6k +- 1 wheel.  This is only used on
    single integers; bulk work goes through :func:`radical_sieve`.
    """
    if n <= 0:
        raise ValueError(f"prime_factors requires n > 0, got {n}")
    f: Dict[int, int] = {}
    for p in (2, 3):
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
    d = 5
    while d * d <= n:
        for p in (d, d + 2):
            while n % p == 0:
                f[p] = f.get(p, 0) + 1
                n //= p
        d += 6
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def radical(n: int) -> int:
    """rad(n), the product of the distinct primes dividing n.  rad(1) = 1."""
    if n == 0:
        raise ValueError("rad(0) is undefined")
    r = 1
    for p in prime_factors(abs(n)):
        r *= p
    return r


def radical_sieve(limit: int) -> List[int]:
    """Return a list R with R[n] = rad(n) for every 0 <= n <= limit.

    One pass of a linear sieve: for each prime p, walk its multiples and
    multiply the accumulator by p exactly once.  Time O(N log log N), space
    O(N) machine words.  This is the routine that makes an exhaustive abc
    search feasible: factoring each n separately would not finish.
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")
    rad = [1] * (limit + 1)
    for i in range(2, limit + 1):
        if rad[i] == 1:                     # i is prime: nothing has touched it
            for j in range(i, limit + 1, i):
                rad[j] *= i
    return rad


def smooth_part(n: int, bound: int) -> int:
    """The largest divisor of n composed only of primes <= bound."""
    s = 1
    for p, e in prime_factors(abs(n)).items():
        if p <= bound:
            s *= p ** e
    return s


def is_squarefree(n: int) -> bool:
    """True iff rad(n) = |n|."""
    return radical(n) == abs(n)


def powerful_part(n: int) -> int:
    """The product of p^e over the primes p dividing n with exponent e >= 2.

    Good abc triples are exactly those in which a, b and c are, between them,
    very powerful; this is the quantity that measures it.
    """
    out = 1
    for p, e in prime_factors(abs(n)).items():
        if e >= 2:
            out *= p ** e
    return out


def iter_primes(limit: int) -> Iterator[int]:
    """Yield the primes up to and including limit (sieve of Eratosthenes)."""
    if limit < 2:
        return
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p :: p] = bytearray(len(range(p * p, limit + 1, p)))
    for n in range(2, limit + 1):
        if sieve[n]:
            yield n
