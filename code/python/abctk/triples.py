# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk.triples — abc triples, their quality, and the search for good ones.

An *abc triple* is a triple (a, b, c) of positive integers with

        a + b = c,      gcd(a, b) = 1,      a < b.

Its *radical* is rad(abc) and its *quality* is

        q(a, b, c) = log c / log rad(abc).

The abc conjecture of Masser and Oesterle asserts that for every eps > 0 there
are only finitely many triples with q > 1 + eps.  Equivalently: q(a,b,c) has
lim sup exactly 1.  Triples with q > 1 exist and are the objects of study;
the largest known quality is 1.6299, from

        2 + 3^10 * 109 = 23^5,

found by Eric Reyssat.  That single triple has resisted improvement since
1987 despite exhaustive searches to c < 2^63 by the ABC@Home project.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from math import gcd
from typing import Dict, Iterator, List, Optional, Sequence

from .radicals import prime_factors, radical, radical_sieve


@dataclass(frozen=True, slots=True)
class Triple:
    """An abc triple together with its derived invariants."""

    a: int
    b: int
    c: int

    def __post_init__(self) -> None:
        if self.a <= 0 or self.b <= 0:
            raise ValueError("a and b must be positive")
        if self.a + self.b != self.c:
            raise ValueError(f"not a triple: {self.a} + {self.b} != {self.c}")
        if gcd(self.a, self.b) != 1:
            raise ValueError(f"not coprime: gcd({self.a},{self.b}) != 1")

    @property
    def rad(self) -> int:
        """rad(abc).  Since gcd(a,b)=1 the three radicals are coprime."""
        return radical(self.a) * radical(self.b) * radical(self.c)

    @property
    def quality(self) -> float:
        """q = log c / log rad(abc).  The conjecture says lim sup q = 1."""
        return math.log(self.c) / math.log(self.rad)

    @property
    def merit(self) -> float:
        """merit = (q - 1)^2 * log rad * log log rad.

        The de Smit / ABC@Home ranking statistic.  It is designed so that a
        triple of modest quality but enormous size can still be recognised as
        exceptional; quality alone favours small triples.
        """
        lr = math.log(self.rad)
        if lr <= math.e:
            return 0.0
        return (self.quality - 1.0) ** 2 * lr * math.log(lr)

    @property
    def size(self) -> float:
        """log c, the natural measure of how far out the triple lies."""
        return math.log(self.c)

    def __str__(self) -> str:
        return (f"{self.a} + {self.b} = {self.c}   "
                f"rad={self.rad}  q={self.quality:.6f}  m={self.merit:.4f}")


# ---------------------------------------------------------------------------
# The record triples.  These are the empirical facts any framework must
# reproduce, and they are the reason the conjecture is believed to be sharp
# at exponent 1 and false at exponent 1 with a constant.
# ---------------------------------------------------------------------------

#: The twenty highest-quality abc triples in the de Smit table, in decreasing
#: quality (table update 2019-03-02).
#: Source: the ABC@Home / Reken mee met ABC tables (Bart de Smit).
RECORD_TRIPLES: Sequence[tuple[int, int, int, str]] = (
    (2, 3 ** 10 * 109, 23 ** 5, "E. Reyssat, 1987"),
    (11 ** 2, 3 ** 2 * 5 ** 6 * 7 ** 3, 2 ** 21 * 23, "B. de Weger, 1987"),
    (19 * 1307, 7 * 29 ** 2 * 31 ** 8, 2 ** 8 * 3 ** 22 * 5 ** 4, "J. Browkin, J. Brzezinski, 1994"),
    (283, 5 ** 11 * 13 ** 2, 2 ** 8 * 3 ** 8 * 17 ** 3, "J. Browkin, J. Brzezinski, 1994"),
    (1, 2 * 3 ** 7, 5 ** 4 * 7, "B. de Weger, 1987"),
    (7 ** 3, 3 ** 10, 2 ** 11 * 29, "J. Browkin, J. Brzezinski, 1994"),
    (7 ** 2 * 41 ** 2 * 311 ** 3, 11 ** 16 * 13 ** 2 * 79,
     2 * 3 ** 3 * 5 ** 23 * 953, "A. Nitaj, 1993"),
    (5 ** 3, 2 ** 9 * 3 ** 17 * 13 ** 2,
     11 ** 5 * 17 * 31 ** 3 * 137, "A. Nitaj, 1993"),
    (13 * 19 ** 6, 2 ** 30 * 5, 3 ** 13 * 11 ** 2 * 31, "B. de Weger, 1987"),
    (3 ** 18 * 23 * 2269, 17 ** 3 * 29 * 31 ** 8,
     2 ** 10 * 5 ** 2 * 7 ** 15, "A. Nitaj, 1993"),
    (13 ** 10 * 37 ** 2, 3 ** 7 * 19 ** 5 * 71 ** 4 * 223,
     2 ** 26 * 5 ** 12 * 1873, "T. Dokchitser, 2003"),
    (2 ** 7 * 23 ** 8, 19 ** 9 * 857 ** 2,
     3 ** 22 * 13 * 47 ** 2 * 263, "de Smit table"),
    (239, 5 ** 8 * 17 ** 3, 2 ** 10 * 37 ** 4,
     "J. Browkin, J. Brzezinski, A. Nitaj"),
    (5 ** 2 * 7937, 7 ** 13, 2 ** 18 * 3 ** 7 * 13 ** 2,
     "B. de Weger, 1988"),
    (2 ** 2 * 11, 3 ** 2 * 13 ** 10 * 17 * 151 * 4423,
     5 ** 9 * 139 ** 6, "A. Nitaj, 1993"),
    (73, 2 ** 13 * 7 ** 7 * 941 ** 2,
     3 ** 16 * 103 ** 3 * 127, "A. Nitaj, 1993"),
    (2 ** 24, 11 ** 7 * 19 * 29 ** 2,
     3 ** 11 * 5 ** 3 * 7 ** 3 * 41, "A. Nitaj, 1993"),
    (11 ** 2, 3 ** 9 * 13, 2 ** 11 * 5 ** 3, "B. de Weger, 1988"),
    (37, 2 ** 15, 3 ** 8 * 5, "B. de Weger, 1988"),
    (5 ** 14 * 19, 2 ** 5 * 3 * 7 ** 13,
     11 ** 7 * 37 ** 2 * 353, "A. Nitaj, 1993"),
)

#: Published ABC@Home census totals used in Chapter 47.
ABC_CENSUS: Dict[str, int] = {
    "complete_below_10_18": 14_482_065,
    "additional_10_18_to_2_63": 9_345_651,
    "known_quality_at_least_1_4": 241,
}


def known_records() -> List[Triple]:
    """Return all published records, sorted by computed quality.

    Invalid source data raise immediately.  Silently dropping a transcription
    error would make a printed numerical table look complete when it is not.
    """
    out = [
        Triple(min(a, b), max(a, b), c)
        for a, b, c, _who in RECORD_TRIPLES
    ]
    return sorted(out, key=lambda t: t.quality, reverse=True)


def latex_factorisation(n: int) -> str:
    """Return the exact prime factorisation of ``n`` as a LaTeX expression."""
    factors = prime_factors(n)
    if not factors:
        return "1"
    terms = [
        str(p) if exponent == 1 else f"{p}^{{{exponent}}}"
        for p, exponent in factors.items()
    ]
    return r"\cdot ".join(terms)


def record_report() -> List[Dict[str, object]]:
    """Return machine-derived fields for the published top-twenty table."""
    rows: List[Dict[str, object]] = []
    for rank, (a, b, c, discoverer) in enumerate(RECORD_TRIPLES, start=1):
        triple = Triple(min(a, b), max(a, b), c)
        rows.append({
            "rank": rank,
            "a": triple.a,
            "b": triple.b,
            "c": triple.c,
            "a_factorisation": latex_factorisation(triple.a),
            "b_factorisation": latex_factorisation(triple.b),
            "c_factorisation": latex_factorisation(triple.c),
            "rad": triple.rad,
            "quality": triple.quality,
            "merit": triple.merit,
            "discoverer": discoverer,
        })
    return rows


def census_report() -> Dict[str, int]:
    """Return the published census counts and their arithmetic total."""
    out = dict(ABC_CENSUS)
    out["archived_total"] = (
        out["complete_below_10_18"] + out["additional_10_18_to_2_63"]
    )
    return out


# ---------------------------------------------------------------------------
# Exhaustive search
# ---------------------------------------------------------------------------

def search(limit: int, min_quality: float = 1.0) -> Iterator[Triple]:
    """Enumerate every abc triple with c <= limit and quality >= min_quality.

    Algorithm.  Sieve all radicals up to ``limit`` once (O(N log log N)), then
    loop over c and a < c/2.  The inner test is three array lookups, a gcd and
    a logarithm, so the whole search is O(N^2) in time but with a very small
    constant and only O(N) memory.

    This deliberately simple quadratic loop is suitable for tests and small
    demonstrations only.  ABC@Home used a substantially stronger
    radical-ordered block sieve.  The pruning below illustrates one necessary
    condition: for quality >= Q we need rad(abc) <= c^(1/Q), and
    rad(a)rad(b)rad(c) >= rad(c), so any c whose own radical exceeds c^(1/Q)
    can be skipped outright.
    """
    if limit < 3:
        return
    rad = radical_sieve(limit)
    for c in range(3, limit + 1):
        # Prune on c alone: rad(abc) >= rad(c), so q <= log c / log rad(c).
        rc = rad[c]
        if rc > 1 and math.log(c) < min_quality * math.log(rc):
            continue
        half = c // 2
        for a in range(1, half + 1):
            b = c - a
            if gcd(a, b) != 1:
                continue
            r = rad[a] * rad[b] * rc
            if r >= c:
                continue                     # q < 1, not of interest
            if math.log(c) >= min_quality * math.log(r):
                yield Triple(a, b, c)


def best_by_quality(limit: int, top: int = 20) -> List[Triple]:
    """The ``top`` highest-quality triples with c <= limit."""
    found = sorted(search(limit, 1.0), key=lambda t: t.quality, reverse=True)
    return found[:top]


def count_above(limit: int, threshold: float) -> int:
    """How many triples with c <= limit have quality > threshold.

    The conjecture predicts this count is bounded as limit -> infinity for
    every threshold > 1.  Watching it flatten is the most direct numerical
    evidence available.
    """
    return sum(1 for _ in search(limit, threshold))


def robert_stewart_tenenbaum(rad_value: float) -> float:
    """The conjectured sharp form of abc.

    Robert, Stewart and Tenenbaum predict

        c < rad * exp( 4 sqrt(3) * sqrt( log rad / log log rad ) * (1 + o(1)) )

    which is strictly stronger information than abc itself: it says the
    exponent 1 + eps is right but that the true correction is a sub-power
    factor of this precise shape.  Returned as the bound on c.
    """
    if rad_value < 16:
        raise ValueError("the asymptotic is meaningless for tiny radicals")
    lr = math.log(rad_value)
    llr = math.log(lr)
    return rad_value * math.exp(4.0 * math.sqrt(3.0) * math.sqrt(lr / llr))


def stewart_yu_bound(rad_value: float, kappa: float = 1.0) -> float:
    """The best unconditional bound known, in shape.

    Stewart and Yu (2001), by Baker's theory of linear forms in logarithms:

        log c  <<  rad(abc)^(1/3 + eps).

    This is exponentially weaker than abc, and the gap between this and the
    truth is the whole subject.  ``kappa`` stands for the ineffective implied
    constant; the function returns the bound on log c, not on c, precisely to
    make that gap visible.
    """
    return kappa * rad_value ** (1.0 / 3.0)
