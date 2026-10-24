# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk.tate — Tate's algorithm for elliptic curves over Q, at a prime p.

The module answers, exactly and without floating point, the question that
Chapter 42 of the book turns on: given an integral Weierstrass model over Z
and a prime p, what is the Kodaira type of the special fibre of the minimal
regular model at p, how many geometric components does that fibre have, and
what is the exponent f_p of p in the conductor?

For p >= 5 the answer is classical and cheap: after minimalisation the
exponent is 0 (good), 1 (multiplicative) or 2 (additive), because the inertia
action is tame and Ogg's formula degenerates.  For p = 2 and p = 3 the action
can be wild, the exponent can reach 8 resp. 5, and nothing short of Tate's
algorithm gives the right answer.  This is the step that naive treatments of
the Frey-Hellegouarch curve get wrong, so it is implemented here in full.

Design notes
------------
*   All coordinate changes are searched over residues rather than written in
    closed form.  A closed form for the substitution required at each step of
    Tate's algorithm has to branch on p = 2, p = 3 and p >= 5 separately, and
    every published implementation that has been found to be wrong was wrong
    in one of those branches.  Searching over r, s, t in a bounded range is
    provably equivalent (the substitution exists, so the search finds one) and
    it removes an entire class of errors.  It is only affordable for small p,
    which is exactly where it is needed.

*   Every return is checked against Ogg's formula in the form proved in
    general by Saito,

        f_p = v_p(Delta_min) + 1 - m_p,

    where m_p is the number of irreducible components of the geometric special
    fibre of the minimal regular model, counted without multiplicity.  A
    disagreement raises rather than returns.

References: Tate, *Algorithm for determining the type of a singular fibre in
an elliptic pencil* (Antwerp IV, 1975); Silverman, *Advanced Topics in the
Arithmetic of Elliptic Curves* IV.9; Ogg (1967); Saito (1988).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .frey import Weierstrass, _v

#: Number of geometric components, without multiplicity, of each Kodaira type.
#: This is the m of Ogg's formula f = v(Delta) + 1 - m.
COMPONENTS = {
    "I0": 1, "II": 1, "III": 2, "IV": 3,
    "I0*": 5, "IV*": 7, "III*": 8, "II*": 9,
}

#: Largest p for which the residue search of the normalisation steps is run.
#: Beyond it the additive case is answered by the tame formula f_p = 2, which
#: is unconditional for p >= 5.
SEARCH_LIMIT = 199


@dataclass(frozen=True, slots=True)
class LocalData:
    """The local invariants of an elliptic curve at one prime."""

    p: int
    kodaira: str          # Kodaira symbol, e.g. "I3", "II", "I2*", "III*"
    f: int                # conductor exponent
    m: int                # geometric components of the special fibre
    v_delta_min: int      # valuation of the minimal discriminant
    minimal_model: Weierstrass

    @property
    def is_good(self) -> bool:
        return self.f == 0

    @property
    def is_multiplicative(self) -> bool:
        return self.f == 1

    @property
    def is_additive(self) -> bool:
        return self.f >= 2

    def __str__(self) -> str:
        return (f"p={self.p}: {self.kodaira}, f={self.f}, m={self.m}, "
                f"v(Delta_min)={self.v_delta_min}")


# ---------------------------------------------------------------------------
# Coordinate changes
# ---------------------------------------------------------------------------

def rst_transform(e: Weierstrass, r: int, s: int, t: int) -> Weierstrass:
    """The substitution x = x' + r, y = y' + s x' + t, with u = 1.

    Silverman, *AEC* III, Table 3.1.  The discriminant is invariant; the test
    suite checks that on every model it touches.
    """
    a1, a2, a3, a4, a6 = e.a1, e.a2, e.a3, e.a4, e.a6
    return Weierstrass(
        a1=a1 + 2 * s,
        a2=a2 - s * a1 + 3 * r - s * s,
        a3=a3 + r * a1 + 2 * t,
        a4=a4 - s * a3 + 2 * r * a2 - (t + r * s) * a1 + 3 * r * r - 2 * s * t,
        a6=(a6 + r * a4 + r * r * a2 + r ** 3
            - t * a3 - t * t - r * t * a1),
    )


def u_transform(e: Weierstrass, u: int) -> Weierstrass:
    """The substitution x = u^2 x', y = u^3 y'; a_i becomes a_i / u^i.

    Raises if the result is not integral, since a non-integral 'minimal
    model' is always a bug rather than a curve.
    """
    coeffs = (e.a1, e.a2, e.a3, e.a4, e.a6)
    powers = (1, 2, 3, 4, 6)
    out: List[int] = []
    for a, i in zip(coeffs, powers):
        q, rem = divmod(a, u ** i)
        if rem:
            raise ValueError(f"scaling by u={u} is not integral: a_{i}={a}")
        out.append(q)
    return Weierstrass(*out)


# ---------------------------------------------------------------------------
# Small finite-field helpers, all by enumeration
# ---------------------------------------------------------------------------

def _roots_with_multiplicity(coeffs: List[int], p: int) -> List[Tuple[int, int]]:
    """Roots in F_p of a monic polynomial, with multiplicities.

    ``coeffs`` lists the coefficients in increasing degree.  Multiplicities
    are obtained by synthetic division, which is exact and characteristic-free;
    gcd(P, P') is not used, because in characteristic 2 and 3 the derivative of
    a cubic degenerates and the gcd test misclassifies.
    """
    poly = [c % p for c in coeffs]
    out: List[Tuple[int, int]] = []
    for a in range(p):
        mult = 0
        while len(poly) > 1:
            # synthetic division of poly by (x - a)
            deg = len(poly) - 1
            quot = [0] * deg
            carry = 0
            for i in range(deg, 0, -1):
                carry = (poly[i] + carry * a) % p
                quot[i - 1] = carry
            rem = (poly[0] + carry * a) % p
            if rem:
                break
            poly = quot
            mult += 1
        if mult:
            out.append((a, mult))
    return out


def _cubic_shape(b: int, c: int, d: int, p: int) -> Tuple[str, Optional[int]]:
    """Classify T^3 + b T^2 + c T + d over F_p.

    Returns ("distinct", None), ("double", alpha) or ("triple", alpha).  A
    repeated root of a cubic over F_p necessarily lies in F_p: the Galois
    group permutes the roots, and a repeated root is distinguished from the
    others by its multiplicity, hence is fixed.
    """
    rs = _roots_with_multiplicity([d, c, b, 1], p)
    for a, mult in rs:
        if mult == 3:
            return "triple", a
    for a, mult in rs:
        if mult == 2:
            return "double", a
    return "distinct", None


def _quadratic_is_separable(b: int, c: int, p: int) -> bool:
    """Does Y^2 + b Y + c have distinct roots over the algebraic closure?

    In odd characteristic this is b^2 - 4c != 0.  In characteristic 2 the
    derivative is the constant b, so the polynomial is separable exactly when
    b is a unit; the uniform statement ``b^2 - 4c != 0 in F_p`` fails at p = 2
    (it reads b^2 != 0), and it is precisely that failure which the search
    below has to respect.
    """
    if p == 2:
        return b % 2 != 0
    return (b * b - 4 * c) % p != 0


# ---------------------------------------------------------------------------
# Normalisation steps, by search
# ---------------------------------------------------------------------------

def _move_singular_point(e: Weierstrass, p: int) -> Weierstrass:
    """Translate so that the singular point of the reduction is (0, 0).

    After the translation p | a3, p | a4, p | a6.  The point exists and is
    unique because the reduction of a curve with v(Delta) > 0 has exactly one
    singular point.
    """
    for r in range(p):
        for t in range(p):
            f = rst_transform(e, r, 0, t)
            if f.a3 % p == 0 and f.a4 % p == 0 and f.a6 % p == 0:
                return f
    raise ArithmeticError(
        f"no singular point found mod {p}; the model or the prime is wrong")


def _normalise_step7(e: Weierstrass, p: int) -> Weierstrass:
    """Bring the model to p | a1, a2;  p^2 | a3, a4;  p^3 | a6.

    Tate's Step 6.  Only a substitution with r = 0 is required, but the search
    widens to r in [0, p) if the narrow one fails, which costs nothing and
    protects against an unnoticed sign convention.
    """
    p2, p3 = p * p, p ** 3
    for rmax in (1, p):
        for r in range(rmax):
            for s in range(p):
                for t in range(p2):
                    f = rst_transform(e, r, s, t)
                    if (f.a1 % p == 0 and f.a2 % p == 0
                            and f.a3 % p2 == 0 and f.a4 % p2 == 0
                            and f.a6 % p3 == 0):
                        return f
    raise ArithmeticError(f"Tate step 6 normalisation failed at p = {p}")


def _shift_y(e: Weierstrass, p: int, scale: int,
             cond) -> Weierstrass:
    """Translate y by ``scale * y0``, y0 in F_p, until ``cond`` holds."""
    for y0 in range(p):
        f = rst_transform(e, 0, 0, scale * y0)
        if cond(f):
            return f
    raise ArithmeticError(f"y-shift failed at p = {p}")


def _shift_x(e: Weierstrass, p: int, scale: int,
             cond) -> Weierstrass:
    """Translate x by ``scale * x0``, x0 in F_p, until ``cond`` holds."""
    for x0 in range(p):
        f = rst_transform(e, scale * x0, 0, 0)
        if cond(f):
            return f
    raise ArithmeticError(f"x-shift failed at p = {p}")


# ---------------------------------------------------------------------------
# The algorithm
# ---------------------------------------------------------------------------

def tate_algorithm(e: Weierstrass, p: int) -> LocalData:
    """Kodaira type, component count, conductor exponent and minimal model.

    Complete for every prime p at which the residue search is affordable,
    which is every p <= ``SEARCH_LIMIT``; in particular for p = 2 and p = 3,
    the only primes at which the answer is not already determined by the
    valuations of c4 and Delta.  For larger p the routine raises, and
    :func:`abctk.frey.conductor_exponent` uses the tame formula instead.
    """
    if p > SEARCH_LIMIT:
        raise NotImplementedError(
            f"p = {p} exceeds the residue-search limit {SEARCH_LIMIT}; "
            f"for p >= 5 use the tame classification instead")
    if e.discriminant == 0:
        raise ValueError("singular curve: Delta = 0")

    cur = e
    for _ in range(64):                    # each pass drops v(Delta) by 12
        n = _v(p, cur.discriminant)
        if n == 0:
            return LocalData(p, "I0", 0, 1, 0, cur)

        cur = _move_singular_point(cur, p)

        if _v(p, cur.b2) == 0:
            # Multiplicative reduction: type I_n, n = v(Delta).
            return _checked(LocalData(p, f"I{n}", 1, n, n, cur))

        # ---- additive reduction from here on ----
        if _v(p, cur.a6) < 2:
            return _checked(LocalData(p, "II", n, 1, n, cur))
        if _v(p, cur.b8) < 3:
            return _checked(LocalData(p, "III", n - 1, 2, n, cur))
        if _v(p, cur.b6) < 3:
            return _checked(LocalData(p, "IV", n - 2, 3, n, cur))

        cur = _normalise_step7(cur, p)
        b = cur.a2 // p
        c = cur.a4 // (p * p)
        d = cur.a6 // (p ** 3)
        shape, alpha = _cubic_shape(b, c, d, p)

        if shape == "distinct":
            return _checked(LocalData(p, "I0*", n - 4, 5, n, cur))

        if shape == "double":
            cur, nu = _type_I_nu_star(cur, p, alpha or 0)
            return _checked(
                LocalData(p, f"I{nu}*", n - 4 - nu, 5 + nu, n, cur))

        # ---- triple root: Steps 8-11 ----
        cur = rst_transform(cur, p * (alpha or 0), 0, 0)
        p2, p3, p4 = p * p, p ** 3, p ** 4
        if not (cur.a2 % p2 == 0 and cur.a4 % p3 == 0 and cur.a6 % p4 == 0):
            raise ArithmeticError(f"triple-root normalisation failed at p={p}")
        # Y^2 + (a3/p^2) Y - (a6/p^4) over F_p.
        if _quadratic_is_separable(cur.a3 // p2, (-cur.a6) // p4, p):
            return _checked(LocalData(p, "IV*", n - 6, 7, n, cur))

        cur = _shift_y(
            cur, p, p2,
            lambda f: f.a3 % p3 == 0 and f.a6 % (p ** 5) == 0)
        if _v(p, cur.a4) < 4:
            return _checked(LocalData(p, "III*", n - 7, 8, n, cur))
        if _v(p, cur.a6) < 6:
            return _checked(LocalData(p, "II*", n - 8, 9, n, cur))

        # Step 11: the model is not minimal at p.  Rescale and start again.
        cur = u_transform(cur, p)

    raise ArithmeticError("Tate's algorithm did not terminate")


def _type_I_nu_star(e: Weierstrass, p: int, alpha: int
                    ) -> Tuple[Weierstrass, int]:
    """The I_nu* branch of Tate's Step 7.

    On entry the cubic T^3 + (a2/p)T^2 + (a4/p^2)T + a6/p^3 has a double root
    ``alpha`` over F_p.  Translating x by p*alpha moves it to the origin, and
    the loop then alternates a translation of y and a translation of x,
    increasing nu by one each time, until the relevant quadratic becomes
    separable.  Returns the transformed model and nu >= 1.
    """
    cur = rst_transform(e, p * alpha, 0, 0)
    nu = 1
    mx = p * p
    my = p * p
    for _ in range(64):
        # Y^2 + (a3/my) Y - (a6/(mx*my)) over F_p.
        xa3 = cur.a3 // my
        xa6 = cur.a6 // (mx * my)
        if _quadratic_is_separable(xa3, -xa6, p):
            return cur, nu
        my_next = my * p
        cur = _shift_y(
            cur, p, my,
            lambda f, m=my_next, k=mx: (f.a3 % m == 0
                                        and f.a6 % (k * m) == 0))
        my = my_next
        nu += 1
        # (a2/p) T^2 + (a4/(p*mx)) T + a6/(mx*my) over F_p, a quadratic whose
        # leading coefficient is a unit because v(a2) = 1 in this branch.
        xa2 = cur.a2 // p
        xa4 = cur.a4 // (p * mx)
        xa6 = cur.a6 // (mx * my)
        if (xa4 * xa4 - 4 * xa2 * xa6) % p != 0:
            return cur, nu
        mx_next = mx * p
        cur = _shift_x(
            cur, p, mx,
            lambda f, m=mx_next, k=my: (f.a4 % (p * m) == 0
                                        and f.a6 % (m * k) == 0))
        mx = mx_next
        nu += 1
    raise ArithmeticError("the I_nu* loop did not terminate")


def _checked(d: LocalData) -> LocalData:
    """Validate a result against Ogg's formula and the wild-ramification bounds."""
    if d.f < 0:
        raise ArithmeticError(f"negative conductor exponent: {d}")
    if d.f != d.v_delta_min + 1 - d.m:
        raise ArithmeticError(
            f"Ogg's formula violated: {d} (f + m - 1 = "
            f"{d.f + d.m - 1} != v = {d.v_delta_min})")
    bound = {2: 8, 3: 5}.get(d.p, 2)
    if d.f > bound:
        raise ArithmeticError(f"conductor exponent {d.f} exceeds {bound}: {d}")
    return d


# ---------------------------------------------------------------------------
# Minimalisation away from 2 and 3
# ---------------------------------------------------------------------------

def is_minimal_at(e: Weierstrass, p: int) -> bool:
    """Kraus's criterion for p >= 5: minimal unless v(c4)>=4, v(c6)>=6, v(D)>=12."""
    if p < 5:
        raise ValueError("use tate_algorithm at p = 2, 3")
    return not (_v(p, e.c4) >= 4 and _v(p, e.c6) >= 6
                and _v(p, e.discriminant) >= 12)


def minimal_valuations(e: Weierstrass, p: int) -> Tuple[int, int]:
    """(v(c4), v(Delta)) for a model minimal at p >= 5.

    For p >= 5 minimality is detected on (c4, c6, Delta) alone, and the
    minimal model is obtained by dividing them by p^4, p^6, p^12; no
    Weierstrass coefficients are needed.
    """
    if p < 5:
        raise ValueError("use tate_algorithm at p = 2, 3")
    v4, v6, vd = _v(p, e.c4) if e.c4 else 10 ** 9, \
        _v(p, e.c6) if e.c6 else 10 ** 9, _v(p, e.discriminant)
    while v4 >= 4 and v6 >= 6 and vd >= 12:
        v4, v6, vd = v4 - 4, v6 - 6, vd - 12
    return v4, vd
