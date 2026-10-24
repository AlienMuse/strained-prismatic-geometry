# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk.qcalc — q-integers, the q-derivative, and the q-Wronskian.

The strategic bet of this book is that the derivation missing from Spec Z can
be supplied by a q-deformation.  The reason is elementary and is worth stating
in code, because it is easy to lose sight of in the categorical machinery:

    the q-derivative

        (nabla_q f)(x) = ( f(qx) - f(x) ) / ( qx - x )

    is a genuine, exactly computable operator on Z[q^{+-1}][x]; it satisfies a
    Leibniz rule; it specialises to d/dx as q -> 1; and, crucially, it makes
    sense simultaneously for every prime, because q is a single formal
    parameter rather than a choice of place.

That last property is what no p-derivation delta_p has: delta_p sees one prime
at a time.  The Habiro-ring philosophy is that evaluating q at roots of unity
of all orders recovers all the p-adic information at once, and this module is
the concrete, finite, checkable shadow of that idea.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Dict, List, Sequence, Tuple

# A q-polynomial is a dict {(i, j): coeff} meaning coeff * q^j * x^i, with
# integer coefficients.  Exactness matters here: the whole point is that these
# identities hold on the nose, not numerically.
QPoly = Dict[Tuple[int, int], Fraction]


def qpoly(terms: Sequence[Tuple[int, int, int]]) -> QPoly:
    """Build a q-polynomial from (x-exponent, q-exponent, coefficient) triples."""
    out: QPoly = {}
    for i, j, c in terms:
        out[(i, j)] = out.get((i, j), Fraction(0)) + Fraction(c)
    return {k: v for k, v in out.items() if v != 0}


def qadd(p: QPoly, r: QPoly) -> QPoly:
    out = dict(p)
    for k, v in r.items():
        out[k] = out.get(k, Fraction(0)) + v
    return {k: v for k, v in out.items() if v != 0}


def qscale(p: QPoly, c: Fraction) -> QPoly:
    return {k: v * c for k, v in p.items() if v * c != 0}


def qmul(p: QPoly, r: QPoly) -> QPoly:
    out: QPoly = {}
    for (i1, j1), c1 in p.items():
        for (i2, j2), c2 in r.items():
            k = (i1 + i2, j1 + j2)
            out[k] = out.get(k, Fraction(0)) + c1 * c2
    return {k: v for k, v in out.items() if v != 0}


def q_integer(n: int) -> QPoly:
    """[n]_q = 1 + q + ... + q^{n-1}.  Note [n]_1 = n."""
    if n < 0:
        raise ValueError("q-integers are defined for n >= 0 here")
    return qpoly([(0, j, 1) for j in range(n)])


def q_factorial(n: int) -> QPoly:
    out = qpoly([(0, 0, 1)])
    for k in range(1, n + 1):
        out = qmul(out, q_integer(k))
    return out


def q_derivative(p: QPoly) -> QPoly:
    """nabla_q applied to a q-polynomial in x.

    On the monomial x^i the definition collapses to

        nabla_q (x^i) = [i]_q x^{i-1},

    which is the identity that makes the operator exact and integral: no
    denominators appear, because (q^i - 1)/(q - 1) = [i]_q is a polynomial.
    This is the precise sense in which the q-world has a derivation with
    integral structure, and it is why the deformation is the natural candidate
    for the object Spec Z lacks.
    """
    out: QPoly = {}
    for (i, j), c in p.items():
        if i == 0:
            continue
        for term, cc in q_integer(i).items():
            k = (i - 1, j + term[1])
            out[k] = out.get(k, Fraction(0)) + c * cc
    return {k: v for k, v in out.items() if v != 0}


def q_wronskian(p: QPoly, r: QPoly) -> QPoly:
    """W_q(a, b) = a * nabla_q b - (nabla_q a) * b.

    The q-analogue of the object that proves Mason-Stothers.  It is NOT true
    that W_q vanishes exactly when a and b are proportional --- the q-Leibniz
    rule carries a shift, so the correct statement involves a(qx) rather than
    a(x) --- and tracking that shift is precisely the technical content of the
    q-deformed Riemann-Hurwitz estimate the book requires.  The discrepancy is
    exposed by :func:`q_leibniz_defect`.
    """
    return qadd(qmul(p, q_derivative(r)), qscale(qmul(q_derivative(p), r), Fraction(-1)))


def q_shift(p: QPoly) -> QPoly:
    """The substitution x -> qx, i.e. f(x) |-> f(qx)."""
    return {(i, j + i): c for (i, j), c in p.items()}


def q_leibniz_defect(p: QPoly, r: QPoly) -> QPoly:
    """nabla_q(fg) - [ f nabla_q g + (nabla_q f) g ].

    The exact q-Leibniz rule is

        nabla_q(fg)(x) = f(qx) nabla_q g(x) + (nabla_q f)(x) g(x),

    so the naive symmetric rule fails by exactly (f(qx) - f(x)) nabla_q g.
    This function returns that defect, and the book's central technical
    estimate is a bound on its 'size' after the q -> 1 and cyclotomic
    specialisations.  Returning it explicitly, rather than assuming it away,
    is the discipline this whole module exists to enforce.
    """
    lhs = q_derivative(qmul(p, r))
    rhs = qadd(qmul(p, q_derivative(r)), qmul(q_derivative(p), r))
    return qadd(lhs, qscale(rhs, Fraction(-1)))


def q_leibniz_exact(p: QPoly, r: QPoly) -> QPoly:
    """The residue of the CORRECT q-Leibniz rule; must be identically zero."""
    lhs = q_derivative(qmul(p, r))
    rhs = qadd(qmul(q_shift(p), q_derivative(r)), qmul(q_derivative(p), r))
    return qadd(lhs, qscale(rhs, Fraction(-1)))


def specialise_q(p: QPoly, q_value: Fraction) -> List[Fraction]:
    """Evaluate the q-variable, returning an ordinary polynomial in x."""
    maxdeg = max((i for (i, _j) in p), default=-1)
    out = [Fraction(0)] * (maxdeg + 1)
    for (i, j), c in p.items():
        out[i] += c * q_value ** j
    while out and out[-1] == 0:
        out.pop()
    return out


def q_to_one(p: QPoly) -> List[Fraction]:
    """The classical limit q -> 1.  nabla_q becomes d/dx and [n]_q becomes n."""
    return specialise_q(p, Fraction(1))


def cyclotomic_specialisation_orders(bound: int) -> List[int]:
    """The orders at which the Habiro philosophy evaluates q.

    The Habiro ring of Z is the completion of Z[q] with respect to the ideals
    generated by (q;q)_n, and its defining virtue is that evaluation at *every*
    root of unity is defined and that these evaluations jointly determine an
    element.  This helper simply lists the orders used in the book's finite
    experiments; it is not itself the Habiro ring.
    """
    return list(range(1, bound + 1))


def q_derivative_jet(
    coefficients: Sequence[int | Fraction], order: int
) -> Dict[Tuple[int, int], Fraction]:
    """Return the ``u=q-1`` jet of ``nabla_q f`` through ``u^order``.

    The output key ``(i, r)`` denotes the coefficient of ``x^i u^r``.
    The exact identity

        [n]_{1+u} = sum_{r=0}^{n-1} binom(n, r+1) u^r

    makes the computation integral for integer input.
    """
    if order < 0:
        raise ValueError("jet order must be non-negative")
    out: Dict[Tuple[int, int], Fraction] = {}
    for n, coeff in enumerate(coefficients):
        coeff = Fraction(coeff)
        if n == 0 or coeff == 0:
            continue
        for r in range(min(order, n - 1) + 1):
            out[(n - 1, r)] = out.get((n - 1, r), Fraction(0)) + coeff * comb(
                n, r + 1
            )
    return {key: value for key, value in out.items() if value}


def format_q_jet(jet: Dict[Tuple[int, int], Fraction]) -> str:
    """Format a truncated ``x,u`` polynomial deterministically."""
    if not jet:
        return "0"
    pieces = []
    for (x_degree, u_degree), coeff in sorted(
        jet.items(), key=lambda item: (item[0][1], item[0][0]), reverse=True
    ):
        pieces.append(f"{coeff}*x^{x_degree}*u^{u_degree}")
    return " + ".join(pieces).replace("+ -", "- ")
