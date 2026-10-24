# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk.masonstothers — the function-field abc, proved and verified.

This module exists for one reason: it is the *control experiment* of the whole
book.  Over k[t] the abc conjecture is a theorem with a three-line proof, and
any framework claiming to explain abc over Z must reproduce that proof exactly
when the base is a function field.  A framework that cannot recover
Mason-Stothers is refuted before it starts.

THEOREM (Stothers 1981, Mason 1984).  Let k be a field of characteristic 0 and
let a, b, c in k[t] be coprime, not all constant, with a + b = c.  Then

        max(deg a, deg b, deg c)  <=  deg rad(abc) - 1,

where rad(f) is the product of the distinct monic irreducible factors of f.

The proof is the Wronskian identity.  Everything the book does over Spec Z is
an attempt to manufacture the object that makes these three lines work: a
derivation, and hence a Wronskian, and hence a Riemann-Hurwitz count.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

Poly = Tuple[float, ...]        # coefficients, lowest degree first


# ---------------------------------------------------------------------------
# A minimal exact polynomial arithmetic over Q (fractions keep it exact).
# ---------------------------------------------------------------------------
from fractions import Fraction


def trim(p: Sequence[Fraction]) -> List[Fraction]:
    q = list(p)
    while q and q[-1] == 0:
        q.pop()
    return q


def deg(p: Sequence[Fraction]) -> int:
    q = trim(p)
    return len(q) - 1 if q else -1        # deg 0 polynomial is -1 by convention


def add(p: Sequence[Fraction], q: Sequence[Fraction]) -> List[Fraction]:
    n = max(len(p), len(q))
    return trim([(p[i] if i < len(p) else Fraction(0))
                 + (q[i] if i < len(q) else Fraction(0)) for i in range(n)])


def mul(p: Sequence[Fraction], q: Sequence[Fraction]) -> List[Fraction]:
    if not trim(p) or not trim(q):
        return []
    out = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        if x == 0:
            continue
        for j, y in enumerate(q):
            out[i + j] += x * y
    return trim(out)


def divmod_poly(p: Sequence[Fraction],
                q: Sequence[Fraction]) -> Tuple[List[Fraction], List[Fraction]]:
    p, q = trim(p), trim(q)
    if not q:
        raise ZeroDivisionError("division by the zero polynomial")
    out = [Fraction(0)] * max(0, len(p) - len(q) + 1)
    r = list(p)
    while trim(r) and len(trim(r)) >= len(q):
        r = trim(r)
        k = len(r) - len(q)
        coef = r[-1] / q[-1]
        out[k] = coef
        for i, y in enumerate(q):
            r[i + k] -= coef * y
        r = trim(r)
    return trim(out), trim(r)


def gcd_poly(p: Sequence[Fraction], q: Sequence[Fraction]) -> List[Fraction]:
    a, b = trim(p), trim(q)
    while b:
        _, r = divmod_poly(a, b)
        a, b = b, trim(r)
    if a and a[-1] != 0:                     # make monic
        lead = a[-1]
        a = [x / lead for x in a]
    return a


def derivative(p: Sequence[Fraction]) -> List[Fraction]:
    """d/dt.  THE object that Spec Z does not have."""
    return trim([p[i] * i for i in range(1, len(p))])


def radical_poly(p: Sequence[Fraction]) -> List[Fraction]:
    """rad(f) = f / gcd(f, f'), the squarefree kernel.

    In characteristic 0 this is exact and is the whole content of the
    'separability' hypothesis: it is precisely where characteristic p breaks
    Mason-Stothers, and it is the exact analogue of the difficulty at the
    ramified primes over Z.
    """
    p = trim(p)
    if not p:
        raise ValueError("rad(0) undefined")
    g = gcd_poly(p, derivative(p))
    q, r = divmod_poly(p, g)
    if trim(r):
        raise AssertionError("gcd(f, f') did not divide f")
    return q


def wronskian(p: Sequence[Fraction], q: Sequence[Fraction]) -> List[Fraction]:
    """W(a, b) = a b' - a' b.

    This single expression is the entire proof.  W vanishes identically iff
    a and b are linearly dependent, its degree is at most deg a + deg b - 1,
    and every repeated root of a, b or c divides it to high order.  Comparing
    those two facts gives the theorem.
    """
    return add(mul(p, derivative(q)), [-x for x in mul(derivative(p), q)])


def mason_stothers_check(a: Sequence[Fraction],
                         b: Sequence[Fraction]) -> dict:
    """Verify the inequality for one instance, returning the whole audit.

    Given coprime a, b (not both constant), set c = a + b and check

        max(deg a, deg b, deg c) <= deg rad(abc) - 1.
    """
    a, b = trim(a), trim(b)
    c = add(a, b)
    if not trim(c):
        raise ValueError("a + b = 0 is excluded")
    g = gcd_poly(a, b)
    if deg(g) > 0:
        raise ValueError(f"a and b are not coprime: gcd has degree {deg(g)}")
    if deg(a) <= 0 and deg(b) <= 0:
        raise ValueError("a, b, c may not all be constant")

    abc = mul(mul(a, b), c)
    rad = radical_poly(abc)
    lhs = max(deg(a), deg(b), deg(c))
    rhs = deg(rad) - 1
    w = wronskian(a, b)

    return {
        "deg_a": deg(a), "deg_b": deg(b), "deg_c": deg(c),
        "deg_rad_abc": deg(rad),
        "lhs": lhs, "rhs": rhs,
        "holds": lhs <= rhs,
        "deg_wronskian": deg(w),
        "wronskian_vanishes": not trim(w),
    }


def demo_instances() -> List[Tuple[str, List[Fraction], List[Fraction]]]:
    """A small suite of instances used by the book's tables.

    Each is a genuinely different phenomenon: the generic case, the case of
    equality (which is what makes the -1 sharp), and a high-power case that is
    the function-field shadow of a high-quality abc triple.
    """
    F = Fraction

    def P(*cs: int) -> List[Fraction]:
        return trim([F(x) for x in cs])

    out: List[Tuple[str, List[Fraction], List[Fraction]]] = []
    # t + 1 = (t) + (1): the trivial instance.
    out.append(("t + 1", P(0, 1), P(1)))
    # (t^2 - 1) = (t - 1)(t + 1): a squarefree case.
    out.append(("t^2 + (-1)", P(0, 0, 1), P(-1)))
    # The equality case: a = t^n, b = 1, c = t^n + 1 with t^n+1 squarefree.
    out.append(("t^3 + 1", P(0, 0, 0, 1), P(1)))
    # The function-field analogue of a powerful triple:
    # (t^2)^2 + (t^4 + 2t^2) ... constructed so that abc has repeated factors.
    out.append(("t^4 + (2t^2 + 1) = (t^2+1)^2", P(0, 0, 0, 0, 1), P(1, 0, 2)))
    return out
