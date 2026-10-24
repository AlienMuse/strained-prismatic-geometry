# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Finite arithmetic used by the computational prismatic chapters.

This is not a general prismatic cohomology engine.  It implements the pieces
that admit finite exact presentations: p-typical Witt arithmetic over
integers, Frobenius and Verschiebung on truncated vectors, elementary
Nygaard divisibility tests, split filtered-Frobenius certificates, and small
elliptic reduction summaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Sequence

Matrix = tuple[tuple[int, ...], ...]
Vector = tuple[int, ...]


def _is_prime(p: int) -> bool:
    if p < 2:
        return False
    d = 2
    while d * d <= p:
        if p % d == 0:
            return p == d
        d += 1 if d == 2 else 2
    return True


def p_typical_truncation_set(p: int, length: int) -> tuple[int, ...]:
    if not _is_prime(p):
        raise ValueError("p must be prime")
    if length < 0:
        raise ValueError("length must be non-negative")
    return tuple(p**i for i in range(length))


def ghost_components(p: int, vector: Sequence[int]) -> Vector:
    """Return p-typical ghost components."""
    if not _is_prime(p):
        raise ValueError("p must be prime")
    out = []
    for k in range(len(vector)):
        value = 0
        for i in range(k + 1):
            value += p**i * int(vector[i]) ** (p ** (k - i))
        out.append(value)
    return tuple(out)


def _from_ghost(p: int, ghosts: Sequence[int]) -> Vector:
    coords: list[int] = []
    for k, ghost in enumerate(ghosts):
        lower = sum(
            p**i * coords[i] ** (p ** (k - i)) for i in range(k)
        )
        numerator = int(ghost) - lower
        denominator = p**k
        quotient, remainder = divmod(numerator, denominator)
        if remainder:
            raise ArithmeticError("ghost tuple is not an integral Witt vector")
        coords.append(quotient)
    return tuple(coords)


def _same_length(a: Sequence[int], b: Sequence[int]) -> None:
    if len(a) != len(b):
        raise ValueError("Witt vectors must have equal length")


def _reduce(vector: Vector, modulus: int | None) -> Vector:
    if modulus is None:
        return vector
    if modulus < 1:
        raise ValueError("modulus must be positive")
    return tuple(x % modulus for x in vector)


def witt_add(
    p: int, a: Sequence[int], b: Sequence[int], modulus: int | None = None
) -> Vector:
    """Add p-typical Witt vectors through their ghost components."""
    _same_length(a, b)
    ga = ghost_components(p, a)
    gb = ghost_components(p, b)
    return _reduce(_from_ghost(p, tuple(x + y for x, y in zip(ga, gb))), modulus)


def witt_mul(
    p: int, a: Sequence[int], b: Sequence[int], modulus: int | None = None
) -> Vector:
    """Multiply p-typical Witt vectors through their ghost components."""
    _same_length(a, b)
    ga = ghost_components(p, a)
    gb = ghost_components(p, b)
    return _reduce(_from_ghost(p, tuple(x * y for x, y in zip(ga, gb))), modulus)


def witt_frobenius(
    p: int, vector: Sequence[int], modulus: int | None = None
) -> Vector:
    """Frobenius ``W_{n+1}(Z) -> W_n(Z)`` by shifting ghost components."""
    if not vector:
        return ()
    ghosts = ghost_components(p, vector)
    return _reduce(_from_ghost(p, ghosts[1:]), modulus)


def witt_verschiebung(vector: Sequence[int], length: int | None = None) -> Vector:
    """Verschiebung by a zero coordinate shift."""
    if length is None:
        length = len(vector) + 1
    if length < 0:
        raise ValueError("length must be non-negative")
    return tuple((0,) + tuple(int(x) for x in vector[: max(0, length - 1)]))[:length]


def delta_integer(x: int, p: int, modulus: int | None = None) -> int:
    """Canonical p-derivation on Z_p: ``delta(x)=(x-x^p)/p``."""
    if not _is_prime(p):
        raise ValueError("p must be prime")
    numerator = int(x) - int(x) ** p
    quotient, remainder = divmod(numerator, p)
    if remainder:
        raise ArithmeticError("Fermat divisibility failed")
    return quotient if modulus is None else quotient % modulus


def p_adic_valuation(value: int, p: int, cap: int | None = None) -> int:
    if not _is_prime(p):
        raise ValueError("p must be prime")
    if value == 0:
        return cap if cap is not None else 10**9
    n = abs(int(value))
    valuation = 0
    while n % p == 0:
        valuation += 1
        n //= p
        if cap is not None and valuation >= cap:
            return cap
    return valuation


def matvec(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> Vector:
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix and vector dimensions do not match")
    return tuple(sum(int(a) * int(b) for a, b in zip(row, vector)) for row in matrix)


def nygaard_level(
    matrix: Sequence[Sequence[int]],
    vector: Sequence[int],
    p: int,
    cap: int,
) -> int:
    """Largest ``r <= cap`` for which ``Fv`` is componentwise divisible by p^r."""
    image = matvec(matrix, vector)
    return min((p_adic_valuation(x, p, cap) for x in image), default=cap)


def divided_frobenius(
    matrix: Sequence[Sequence[int]],
    vector: Sequence[int],
    p: int,
    level: int,
    modulus: int | None = None,
) -> Vector:
    image = matvec(matrix, vector)
    divisor = p**level
    out = []
    for value in image:
        quotient, remainder = divmod(value, divisor)
        if remainder:
            raise ValueError("vector does not lie in the requested Nygaard step")
        out.append(quotient if modulus is None else quotient % modulus)
    return tuple(out)


def determinant(matrix: Sequence[Sequence[int]]) -> int:
    """Bareiss determinant for an integral square matrix."""
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("determinant requires a square matrix")
    if n == 0:
        return 1
    a = [list(map(int, row)) for row in matrix]
    sign = 1
    previous = 1
    for k in range(n - 1):
        if a[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if a[i][k]), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign *= -1
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                a[i][j] = numerator // previous
        previous = pivot
    return sign * a[-1][-1]


@dataclass(frozen=True)
class FGaugeRecord:
    """A split finite filtered-Frobenius presentation.

    ``weights[j]`` means that the basis vector ``e_j`` enters the decreasing
    filtration at that weight.  Column ``j`` of ``frobenius`` is the image of
    ``e_j`` before dividing by ``p**weights[j]``.
    """

    p: int
    precision: int
    basis: tuple[str, ...]
    weights: tuple[int, ...]
    frobenius: Matrix
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        rank = len(self.basis)
        if not _is_prime(self.p):
            raise ValueError("p must be prime")
        if self.precision < 1:
            raise ValueError("precision must be positive")
        if len(self.weights) != rank or any(w < 0 for w in self.weights):
            raise ValueError("weights must be non-negative and match the basis")
        if len(self.frobenius) != rank or any(len(row) != rank for row in self.frobenius):
            raise ValueError("Frobenius matrix must be square of the gauge rank")

    def normalised_frobenius(self) -> Matrix:
        rank = len(self.basis)
        rows = [[0] * rank for _ in range(rank)]
        for j, weight in enumerate(self.weights):
            divisor = self.p**weight
            for i in range(rank):
                value = self.frobenius[i][j]
                quotient, remainder = divmod(value, divisor)
                if remainder:
                    raise ValueError(f"column {j} is not divisible by p^{weight}")
                rows[i][j] = quotient
        return tuple(tuple(row) for row in rows)

    def strong_divisibility_certificate(self) -> dict[str, Any]:
        try:
            normalised = self.normalised_frobenius()
        except ValueError as exc:
            return {"strongly_divisible": False, "reason": str(exc)}
        det = determinant(normalised)
        return {
            "strongly_divisible": det % self.p != 0,
            "normalised_frobenius": normalised,
            "determinant": det,
            "determinant_mod_p": det % self.p,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "p": self.p,
            "precision": self.precision,
            "basis": list(self.basis),
            "weights": list(self.weights),
            "frobenius": [list(row) for row in self.frobenius],
            "certificate": self.strong_divisibility_certificate(),
            "metadata": dict(sorted(self.metadata.items())),
        }


def tate_curve_data(p: int, q_valuation: int, split: bool = True) -> dict[str, Any]:
    """Classical finite data for a Tate curve with ``v_p(q)>0``."""
    if not _is_prime(p):
        raise ValueError("p must be prime")
    if q_valuation <= 0:
        raise ValueError("a Tate parameter must have positive valuation")
    return {
        "p": p,
        "reduction": "split multiplicative" if split else "non-split multiplicative",
        "kodaira": f"I_{q_valuation}",
        "minimal_discriminant_valuation": q_valuation,
        "conductor_exponent": 1,
        "hodge_tate_weights": [0, 1],
        "computed_object": "semistable reduction summary, not a full log-prismatic complex",
    }


_ADDITIVE_VALUATIONS = {
    "II": 2,
    "III": 3,
    "IV": 4,
    "I0*": 6,
    "IV*": 8,
    "III*": 9,
    "II*": 10,
}


def elliptic_reduction_data(p: int, symbol: str) -> dict[str, Any]:
    """Kodaira-symbol invariants, with wild cases rejected rather than guessed."""
    if not _is_prime(p):
        raise ValueError("p must be prime")
    symbol = symbol.upper().replace("_", "")
    if symbol == "I0":
        return {
            "p": p,
            "kodaira": "I0",
            "reduction": "good",
            "minimal_discriminant_valuation": 0,
            "conductor_exponent": 0,
        }
    match = re.fullmatch(r"I(\d+)", symbol)
    if match and int(match.group(1)) > 0:
        n = int(match.group(1))
        return {
            "p": p,
            "kodaira": f"I_{n}",
            "reduction": "multiplicative",
            "minimal_discriminant_valuation": n,
            "conductor_exponent": 1,
        }
    star = re.fullmatch(r"I(\d+)\*", symbol)
    if star:
        if p < 5:
            raise NotImplementedError("wild additive reduction at p=2,3 is not inferred")
        n = int(star.group(1))
        return {
            "p": p,
            "kodaira": f"I_{n}^*",
            "reduction": "additive potentially multiplicative",
            "minimal_discriminant_valuation": n + 6,
            "conductor_exponent": 2,
        }
    if symbol in _ADDITIVE_VALUATIONS:
        if p < 5:
            raise NotImplementedError("wild additive reduction at p=2,3 is not inferred")
        return {
            "p": p,
            "kodaira": symbol.replace("0", "_0").replace("*", "^*"),
            "reduction": "additive potentially good",
            "minimal_discriminant_valuation": _ADDITIVE_VALUATIONS[symbol],
            "conductor_exponent": 2,
        }
    raise ValueError(f"unsupported Kodaira symbol: {symbol}")


def elliptic_point_count(p: int, a: int, b: int) -> int:
    """Count points on ``y^2=x^3+a*x+b`` over F_p by exhaustive residues."""
    if not _is_prime(p):
        raise ValueError("p must be prime")
    discriminant = (-16 * (4 * a**3 + 27 * b**2)) % p
    if discriminant == 0:
        raise ValueError("the reduced cubic is singular")
    count = 1
    squares = {y * y % p for y in range(p)}
    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        if rhs == 0:
            count += 1
        elif rhs in squares:
            count += 2
    return count


def elliptic_frobenius_data(p: int, a: int, b: int) -> dict[str, Any]:
    points = elliptic_point_count(p, a, b)
    trace = p + 1 - points
    return {
        "p": p,
        "points": points,
        "trace": trace,
        "characteristic_polynomial": [1, -trace, p],
        "hodge_tate_weights": [0, 1],
        "warning": "the characteristic polynomial does not determine an integral F-gauge",
    }
