# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk.frey — the Frey-Hellegouarch curve and the Szpiro ratio.

Given an abc triple (a, b, c) the Frey-Hellegouarch curve is

        E_{a,b} :  y^2 = x (x - a) (x + b).

Its discriminant and conductor are, up to controlled powers of 2,

        Delta = 16 (abc)^2,        N = rad(abc),

so a bound of Szpiro type |Delta| << N^{6+eps} is, for this family, exactly an
abc bound.  This module computes the invariants exactly, runs enough of Tate's
algorithm to get the conductor of a semistable curve, and reports the Szpiro
ratio

        sigma(E) = log |Delta_E| / log N_E,

whose supremum over all elliptic curves over Q is conjectured to be 6.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Dict, Tuple

from .radicals import prime_factors, radical


@dataclass(frozen=True, slots=True)
class Weierstrass:
    """A Weierstrass model y^2 + a1 xy + a3 y = x^3 + a2 x^2 + a4 x + a6."""

    a1: int = 0
    a2: int = 0
    a3: int = 0
    a4: int = 0
    a6: int = 0

    # --- the standard quantities of Tate's formulary (Silverman, AEC III.1) --
    @property
    def b2(self) -> int:
        return self.a1 * self.a1 + 4 * self.a2

    @property
    def b4(self) -> int:
        return 2 * self.a4 + self.a1 * self.a3

    @property
    def b6(self) -> int:
        return self.a3 * self.a3 + 4 * self.a6

    @property
    def b8(self) -> int:
        return (self.a1 * self.a1 * self.a6
                - self.a1 * self.a3 * self.a4
                + 4 * self.a2 * self.a6
                + self.a2 * self.a3 * self.a3
                - self.a4 * self.a4)

    @property
    def c4(self) -> int:
        return self.b2 * self.b2 - 24 * self.b4

    @property
    def c6(self) -> int:
        return -(self.b2 ** 3) + 36 * self.b2 * self.b4 - 216 * self.b6

    @property
    def discriminant(self) -> int:
        b2, b4, b6, b8 = self.b2, self.b4, self.b6, self.b8
        return (-(b2 * b2) * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6)

    @property
    def j_numerator(self) -> int:
        return self.c4 ** 3

    def j_invariant(self) -> float:
        d = self.discriminant
        if d == 0:
            raise ZeroDivisionError("singular curve: Delta = 0")
        return self.c4 ** 3 / d

    def is_singular(self) -> bool:
        return self.discriminant == 0


def frey_curve(a: int, b: int, c: int) -> Weierstrass:
    """The Frey-Hellegouarch curve y^2 = x(x-a)(x+b) of an abc triple.

    Expanding, x(x-a)(x+b) = x^3 + (b-a) x^2 - ab x, so in Weierstrass form
    a1 = a3 = a6 = 0, a2 = b - a, a4 = -ab.
    """
    if a + b != c:
        raise ValueError(f"{a} + {b} != {c}")
    if gcd(a, b) != 1:
        raise ValueError("the triple must be coprime")
    return Weierstrass(a1=0, a2=b - a, a3=0, a4=-a * b, a6=0)


def frey_discriminant(a: int, b: int, c: int) -> int:
    """Delta(E_{a,b}) = 16 (abc)^2, computed from the model and checked."""
    e = frey_curve(a, b, c)
    d = e.discriminant
    expected = 16 * (a * b * c) ** 2
    if d != expected:
        raise AssertionError(f"Delta = {d}, expected 16(abc)^2 = {expected}")
    return d


# ---------------------------------------------------------------------------
# Reduction type and conductor
# ---------------------------------------------------------------------------

def _v(p: int, n: int) -> int:
    """The p-adic valuation of a nonzero integer."""
    if n == 0:
        return math.inf  # type: ignore[return-value]
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


def conductor_exponent(e: Weierstrass, p: int) -> int:
    """The exponent of p in the conductor.

    For p >= 5 the answer is tame and classical: after minimalisation at p,
    which for p >= 5 is decided by (v(c4), v(c6), v(Delta)) alone (Kraus's
    criterion), the exponent is 0 for good reduction, 1 for multiplicative
    reduction and 2 for additive reduction.

    For p in {2, 3} the inertia action can be wild, the exponent reaches 8
    resp. 5, and no formula in the valuations of the invariants suffices.
    Those two primes are delegated to the full Tate algorithm of
    :mod:`abctk.tate`, which returns the Kodaira type and the component count
    and validates its own output against Ogg's formula

        f_p = v_p(Delta_min) + 1 - m_p

    in the form proved in general by Saito.  Earlier versions of this module
    raised ``NotImplementedError`` here; that gap is now closed.
    """
    d = e.discriminant
    if d == 0:
        raise ValueError("singular curve")
    if p in (2, 3):
        from .tate import tate_algorithm
        return tate_algorithm(e, p).f
    vd = _v(p, d)
    if vd == 0:
        return 0                                   # good reduction
    vc4 = _v(p, e.c4) if e.c4 != 0 else math.inf
    if vc4 == 0:
        return 1                                   # multiplicative reduction
    from .tate import minimal_valuations
    v4, vdmin = minimal_valuations(e, p)
    if vdmin == 0:
        return 0
    return 1 if v4 == 0 else 2


def local_data(e: Weierstrass, p: int):
    """Full local invariants at p: Kodaira type, f_p, components, v(Delta_min).

    Available for every p at or below the residue-search limit of
    :mod:`abctk.tate`; in particular for the only two primes where the answer
    is delicate.
    """
    from .tate import tate_algorithm
    return tate_algorithm(e, p)


def minimal_discriminant(e: Weierstrass) -> int:
    """The minimal discriminant of the curve, as an integer with sign.

    Obtained prime by prime: at 2 and 3 from Tate's algorithm, at p >= 5 from
    Kraus's minimality criterion.  The sign is that of the given model, which
    is a Weierstrass invariant.
    """
    d = e.discriminant
    if d == 0:
        raise ValueError("singular curve")
    from .tate import tate_algorithm, minimal_valuations
    out = 1
    rest = abs(d)
    for p in prime_factors(abs(d)):
        if p in (2, 3):
            v = tate_algorithm(e, p).v_delta_min
        else:
            _, v = minimal_valuations(e, p)
        out *= p ** v
        while rest % p == 0:
            rest //= p
    return out if d > 0 else -out


def conductor(e: Weierstrass, primes: Tuple[int, ...] | None = None) -> int:
    """N_E = prod p^{f_p}.  Only the primes dividing Delta can contribute."""
    d = abs(e.discriminant)
    ps = tuple(prime_factors(d)) if primes is None else primes
    n = 1
    for p in ps:
        n *= p ** conductor_exponent(e, p)
    return n


def frey_conductor(a: int, b: int, c: int) -> int:
    """The conductor of the Frey curve of a triple.

    For the classical normalisation (a = -1 mod 4, b = 0 mod 16, which one may
    always arrange by permuting and sign-flipping the triple) the curve is
    semistable and N = rad(abc).  We do not assume that normalisation; we
    compute, at 2 and 3 by Tate's algorithm, elsewhere by the tame rule.
    """
    return conductor(frey_curve(a, b, c))


def szpiro_ratio(e: Weierstrass) -> float:
    """sigma = log|Delta_min| / log N, computed on the minimal model.

    Szpiro's conjecture is sup sigma = 6 over all elliptic curves over Q, and
    it is equivalent to abc up to epsilon.  The discriminant that occurs in it
    is the *minimal* one; using the discriminant of an arbitrary model would
    inflate the ratio by an arbitrary amount, since Delta scales by u^12.
    """
    n = conductor(e)
    if n <= 1:
        raise ValueError("conductor 1: no elliptic curve over Q has it")
    return math.log(abs(minimal_discriminant(e))) / math.log(n)


def minimal_invariants(e: Weierstrass) -> Tuple[int, int, int]:
    """(c4, c6, Delta) of a global minimal model.

    The scaling factor u is recovered from u^12 = Delta / Delta_min, which is
    an exact integer twelfth power; the invariants then scale as u^4 and u^6.
    No Weierstrass coefficients are needed, and none are produced: for the
    height and for the Szpiro ratios only (c4, c6, Delta) matter.
    """
    d = e.discriminant
    dmin = minimal_discriminant(e)
    ratio = abs(d) // abs(dmin)
    u = round(ratio ** (1.0 / 12.0))
    while u ** 12 < ratio:
        u += 1
    if u ** 12 != ratio:
        raise ArithmeticError(f"Delta/Delta_min = {ratio} is not a 12th power")
    return e.c4 // u ** 4, e.c6 // u ** 6, dmin


def modified_szpiro_ratio(e: Weierstrass) -> float:
    """sigma' = log max(|c4|^3, c6^2) / log N, on the minimal model.

    This is the form used in Nitaj's tables and the one that is equivalent to
    abc: sup sigma' = 6 is equivalent to the abc conjecture with exponent
    1 + eps, whereas sup sigma = 6 for the unmodified ratio is strictly
    weaker and yields only the exponent 3/2.
    """
    n = conductor(e)
    c4m, c6m, _ = minimal_invariants(e)
    m = max(abs(c4m) ** 3, c6m ** 2)
    if m == 0:
        raise ValueError("degenerate invariants")
    return math.log(m) / math.log(n)


def szpiro_report(a: int, b: int, c: int) -> Dict[str, object]:
    """A complete invariant report for the Frey curve of one triple."""
    e = frey_curve(a, b, c)
    r = radical(a) * radical(b) * radical(c)
    out: Dict[str, object] = {
        "a": a, "b": b, "c": c,
        "rad": r,
        "quality": math.log(c) / math.log(r),
        "discriminant": e.discriminant,
        "c4": e.c4,
        "c6": e.c6,
    }
    try:
        n = conductor(e)
        dmin = minimal_discriminant(e)
        out["conductor"] = n
        out["minimal_discriminant"] = dmin
        out["conductor_over_radical"] = Fraction(n, r)
        out["szpiro"] = math.log(abs(dmin)) / math.log(n)
        out["modified_szpiro"] = modified_szpiro_ratio(e)
        out["local"] = {p: str(local_data(e, p)) for p in (2, 3)
                        if e.discriminant % p == 0}
    except NotImplementedError as exc:
        out["conductor"] = None
        out["note"] = str(exc)
    return out
