# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Exact finite computations in the Habiro completion.

The module uses low-to-high integer coefficient tuples for polynomials in
``q``.  A precision-``N`` Habiro element is represented by mixed-radix digits

    f = sum_{n=0}^{N-1} a_n(q) (q;q)_n,     deg(a_n) <= n.

This representation is canonical modulo ``(q;q)_N``.  It is deliberately
small and dependency-free: the algorithms are intended to be auditable in the
same source tree as the numerical claims printed in the book.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Sequence

Poly = tuple[int, ...]


def trim(poly: Iterable[int]) -> Poly:
    """Return a canonical low-to-high coefficient tuple."""
    out = list(poly)
    while out and out[-1] == 0:
        out.pop()
    return tuple(out)


def poly_add(a: Poly, b: Poly) -> Poly:
    out = [0] * max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += value
    return trim(out)


def poly_sub(a: Poly, b: Poly) -> Poly:
    out = [0] * max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] -= value
    return trim(out)


def poly_mul(a: Poly, b: Poly) -> Poly:
    if not a or not b:
        return ()
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def poly_shift(a: Poly, amount: int) -> Poly:
    if amount < 0:
        raise ValueError("shift must be non-negative")
    return (() if not a else (0,) * amount + a)


def poly_divmod(a: Poly, divisor: Poly) -> tuple[Poly, Poly]:
    """Divide by a polynomial with leading coefficient ``1`` or ``-1``."""
    a = trim(a)
    divisor = trim(divisor)
    if not divisor:
        raise ZeroDivisionError("polynomial division by zero")
    lead = divisor[-1]
    if lead not in (-1, 1):
        raise ValueError("divisor must have unit leading coefficient")
    if len(a) < len(divisor):
        return (), a
    rem = list(a)
    quotient = [0] * (len(a) - len(divisor) + 1)
    while rem and len(rem) >= len(divisor):
        offset = len(rem) - len(divisor)
        coeff = rem[-1] // lead
        quotient[offset] = coeff
        for i, value in enumerate(divisor):
            rem[offset + i] -= coeff * value
        while rem and rem[-1] == 0:
            rem.pop()
    return trim(quotient), trim(rem)


def poly_mod(a: Poly, modulus: Poly) -> Poly:
    return poly_divmod(a, modulus)[1]


def q_pochhammer(n: int) -> Poly:
    """Return ``(q;q)_n = product_{j=1}^n (1-q^j)`` exactly."""
    if n < 0:
        raise ValueError("n must be non-negative")
    out: Poly = (1,)
    for j in range(1, n + 1):
        out = poly_sub(out, poly_shift(out, j))
    return out


def q_pochhammer_stats(n: int) -> dict[str, int]:
    coeffs = q_pochhammer(n)
    return {
        "n": n,
        "degree": len(coeffs) - 1,
        "nonzero": sum(c != 0 for c in coeffs),
        "max_abs": max((abs(c) for c in coeffs), default=0),
        "l1": sum(abs(c) for c in coeffs),
    }


def _divisors(n: int) -> list[int]:
    small: list[int] = []
    large: list[int] = []
    for d in range(1, math.isqrt(n) + 1):
        if n % d == 0:
            small.append(d)
            if d * d != n:
                large.append(n // d)
    return small + large[::-1]


@lru_cache(maxsize=None)
def cyclotomic_polynomial(n: int) -> Poly:
    """Return the ``n``-th cyclotomic polynomial by exact factor removal."""
    if n < 1:
        raise ValueError("cyclotomic order must be positive")
    poly = (-1,) + (0,) * (n - 1) + (1,)
    for d in _divisors(n):
        if d == n:
            continue
        quotient, remainder = poly_divmod(poly, cyclotomic_polynomial(d))
        if remainder:
            raise ArithmeticError("cyclotomic division was not exact")
        poly = quotient
    return poly


def poly_mod_cyclotomic(poly: Poly, order: int) -> Poly:
    return poly_mod(poly, cyclotomic_polynomial(order))


def _remainder_mod_one_minus_qk(poly: Poly, k: int) -> Poly:
    """Reduce modulo ``1-q^k`` by folding exponents modulo ``k``."""
    if k < 1:
        raise ValueError("k must be positive")
    out = [0] * k
    for exponent, coeff in enumerate(poly):
        out[exponent % k] += coeff
    return trim(out)


def _divide_by_one_minus_qk(poly: Poly, k: int) -> Poly:
    divisor = (1,) + (0,) * (k - 1) + (-1,)
    quotient, remainder = poly_divmod(poly, divisor)
    if remainder:
        raise ArithmeticError("polynomial is not divisible by 1-q^k")
    return quotient


@dataclass(frozen=True)
class RootEvaluation:
    order: int
    residue: Poly
    certified: bool
    terms_used: int

    def complex_value(self) -> complex:
        zeta = cmath.exp(2j * math.pi / self.order)
        return sum(c * zeta**i for i, c in enumerate(self.residue))


@dataclass(frozen=True)
class HabiroElement:
    """Canonical Habiro digits through a finite cyclotomic precision."""

    digits: tuple[Poly, ...]

    def __post_init__(self) -> None:
        canonical = tuple(trim(d) for d in self.digits)
        for n, digit in enumerate(canonical):
            if len(digit) > n + 1:
                raise ValueError(f"digit {n} has degree greater than {n}")
        object.__setattr__(self, "digits", canonical)

    @property
    def precision(self) -> int:
        return len(self.digits)

    def to_residue(self) -> Poly:
        """Decode the canonical digits modulo ``(q;q)_precision``."""
        out: Poly = ()
        poch: Poly = (1,)
        for n, digit in enumerate(self.digits):
            out = poly_add(out, poly_mul(digit, poch))
            poch = poly_sub(poch, poly_shift(poch, n + 1))
        return out

    @classmethod
    def from_residue(cls, poly: Poly, precision: int) -> "HabiroElement":
        """Encode a polynomial residue in canonical mixed-radix digits."""
        if precision < 0:
            raise ValueError("precision must be non-negative")
        modulus = q_pochhammer(precision)
        current = poly_mod(trim(poly), modulus) if precision else ()
        digits: list[Poly] = []
        for n in range(precision):
            k = n + 1
            digit = _remainder_mod_one_minus_qk(current, k)
            digits.append(digit)
            current = _divide_by_one_minus_qk(poly_sub(current, digit), k)
        if current:
            raise ArithmeticError("mixed-radix encoding did not terminate")
        return cls(tuple(digits))

    def truncate(self, precision: int) -> "HabiroElement":
        if precision < 0:
            raise ValueError("precision must be non-negative")
        return HabiroElement(self.digits[:precision])

    def add(self, other: "HabiroElement", precision: int | None = None) -> "HabiroElement":
        if precision is None:
            precision = min(self.precision, other.precision)
        if precision > min(self.precision, other.precision):
            raise ValueError("requested precision exceeds an input precision")
        left = self.truncate(precision).digits
        right = other.truncate(precision).digits
        digits = []
        for n in range(precision):
            digits.append(poly_add(left[n], right[n]))
        return HabiroElement(tuple(digits))

    def multiply(
        self, other: "HabiroElement", precision: int | None = None
    ) -> "HabiroElement":
        if precision is None:
            precision = min(self.precision, other.precision)
        if precision > min(self.precision, other.precision):
            raise ValueError("requested precision exceeds an input precision")
        product = poly_mul(
            self.truncate(precision).to_residue(),
            other.truncate(precision).to_residue(),
        )
        return HabiroElement.from_residue(product, precision)

    def evaluate_root(self, order: int) -> RootEvaluation:
        """Evaluate in ``Z[q]/Phi_order``.

        If ``precision >= order``, every omitted Habiro term contains
        ``1-q^order`` and the value is independent of all unknown later digits.
        """
        if order < 1:
            raise ValueError("root order must be positive")
        terms = min(self.precision, order)
        partial = self.truncate(terms).to_residue()
        return RootEvaluation(
            order=order,
            residue=poly_mod_cyclotomic(partial, order),
            certified=self.precision >= order,
            terms_used=terms,
        )


def finite_tail_bound(
    q_value: complex, coefficient_bounds: Sequence[float], start: int
) -> float:
    """Bound a declared finite Habiro tail.

    ``coefficient_bounds[n]`` must be an external bound for
    ``|a_n(q_value)|``.  The result bounds only the supplied finite range; a
    caller claiming an infinite-tail bound must also certify convergence of
    the remaining majorant.
    """
    if start < 0 or start > len(coefficient_bounds):
        raise ValueError("invalid start index")
    product = 1.0
    total = 0.0
    for n, bound in enumerate(coefficient_bounds):
        if bound < 0:
            raise ValueError("coefficient bounds must be non-negative")
        if n >= start:
            total += bound * abs(product)
        product *= 1 - q_value ** (n + 1)
    return float(total)


def format_poly(poly: Poly, variable: str = "q") -> str:
    """Format an integer polynomial for reproducible chapter output."""
    if not poly:
        return "0"
    terms: list[str] = []
    for exponent in range(len(poly) - 1, -1, -1):
        coeff = poly[exponent]
        if coeff == 0:
            continue
        sign = "-" if coeff < 0 else "+"
        magnitude = abs(coeff)
        if exponent == 0:
            body = str(magnitude)
        elif exponent == 1:
            body = variable if magnitude == 1 else f"{magnitude}*{variable}"
        else:
            body = (
                f"{variable}^{exponent}"
                if magnitude == 1
                else f"{magnitude}*{variable}^{exponent}"
            )
        terms.append((sign, body))
    first_sign, first_body = terms[0]
    text = ("" if first_sign == "+" else "-") + first_body
    for sign, body in terms[1:]:
        text += f" {sign} {body}"
    return text
