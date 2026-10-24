# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Certified real enclosures used by Chapters 50 and 51.

The module deliberately implements a small, inspectable kernel rather than
wrapping binary floating point.  Decimal endpoints are rounded outwards for
the four arithmetic operations.  Transcendental evaluations are performed at
guard precision, rounded to the requested precision, and enlarged by one
unit in the last place.

The functions below certify the arithmetic of explicit benchmark models.
They do not certify that a benchmark is the SPG strain trace; that unresolved
comparison is reported separately as modelling status.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    Decimal,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_HALF_EVEN,
    localcontext,
)
from fractions import Fraction
from typing import Dict, Mapping

from . import frey
from .radicals import prime_factors
from .triples import Triple


def _decimal(value: int | str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)


def _rounded(value: Decimal, precision: int, rounding: str) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = precision
        ctx.rounding = rounding
        return +value


def _binary(
    left: Decimal,
    right: Decimal,
    precision: int,
    rounding: str,
    operation: str,
) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = precision
        ctx.rounding = rounding
        if operation == "add":
            return left + right
        if operation == "sub":
            return left - right
        if operation == "mul":
            return left * right
        if operation == "div":
            return left / right
    raise ValueError(operation)


@dataclass(frozen=True, slots=True)
class Interval:
    """Closed Decimal interval with outward-rounded elementary operations."""

    lo: Decimal
    hi: Decimal
    precision: int = 40

    def __post_init__(self) -> None:
        if self.precision < 8:
            raise ValueError("precision must be at least 8 decimal digits")
        if self.lo.is_nan() or self.hi.is_nan() or self.lo > self.hi:
            raise ValueError(f"invalid interval [{self.lo}, {self.hi}]")

    @classmethod
    def point(
        cls, value: int | str | Decimal, precision: int = 40
    ) -> "Interval":
        x = _decimal(value)
        return cls(x, x, precision)

    @classmethod
    def rational(
        cls, numerator: int, denominator: int, precision: int = 40
    ) -> "Interval":
        if denominator == 0:
            raise ZeroDivisionError("zero denominator")
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        n, d = Decimal(numerator), Decimal(denominator)
        lo = _binary(n, d, precision, ROUND_FLOOR, "div")
        hi = _binary(n, d, precision, ROUND_CEILING, "div")
        return cls(lo, hi, precision)

    @property
    def width(self) -> Decimal:
        return _binary(
            self.hi, self.lo, self.precision, ROUND_CEILING, "sub"
        )

    @property
    def midpoint(self) -> Decimal:
        total = _binary(
            self.lo, self.hi, self.precision, ROUND_HALF_EVEN, "add"
        )
        return _binary(
            total, Decimal(2), self.precision, ROUND_HALF_EVEN, "div"
        )

    def contains(self, value: int | str | Decimal) -> bool:
        x = _decimal(value)
        return self.lo <= x <= self.hi

    def interior_contains(self, other: "Interval") -> bool:
        return self.lo < other.lo and other.hi < self.hi

    def intersection(self, other: "Interval") -> "Interval":
        lo, hi = max(self.lo, other.lo), min(self.hi, other.hi)
        if lo > hi:
            raise ValueError("disjoint intervals")
        return Interval(lo, hi, max(self.precision, other.precision))

    def __neg__(self) -> "Interval":
        return Interval(-self.hi, -self.lo, self.precision)

    def __add__(self, other: "Interval") -> "Interval":
        precision = max(self.precision, other.precision)
        return Interval(
            _binary(self.lo, other.lo, precision, ROUND_FLOOR, "add"),
            _binary(self.hi, other.hi, precision, ROUND_CEILING, "add"),
            precision,
        )

    def __sub__(self, other: "Interval") -> "Interval":
        precision = max(self.precision, other.precision)
        return Interval(
            _binary(self.lo, other.hi, precision, ROUND_FLOOR, "sub"),
            _binary(self.hi, other.lo, precision, ROUND_CEILING, "sub"),
            precision,
        )

    def __mul__(self, other: "Interval") -> "Interval":
        precision = max(self.precision, other.precision)
        lower = [
            _binary(a, b, precision, ROUND_FLOOR, "mul")
            for a in (self.lo, self.hi)
            for b in (other.lo, other.hi)
        ]
        upper = [
            _binary(a, b, precision, ROUND_CEILING, "mul")
            for a in (self.lo, self.hi)
            for b in (other.lo, other.hi)
        ]
        return Interval(min(lower), max(upper), precision)

    def reciprocal(self) -> "Interval":
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError("interval contains zero")
        one = Decimal(1)
        return Interval(
            _binary(one, self.hi, self.precision, ROUND_FLOOR, "div"),
            _binary(one, self.lo, self.precision, ROUND_CEILING, "div"),
            self.precision,
        )

    def __truediv__(self, other: "Interval") -> "Interval":
        return self * other.reciprocal()

    def scale(self, numerator: int, denominator: int = 1) -> "Interval":
        return self * Interval.rational(
            numerator, denominator, self.precision
        )

    def to_strings(self) -> Dict[str, str]:
        return {"lo": str(self.lo), "hi": str(self.hi)}


def _ln_decimal(value: Decimal, precision: int, lower: bool) -> Decimal:
    if value <= 0:
        raise ValueError("logarithm requires a positive argument")
    with localcontext() as work:
        work.prec = precision + 16
        work.rounding = ROUND_HALF_EVEN
        approximation = value.ln()
    rounding = ROUND_FLOOR if lower else ROUND_CEILING
    with localcontext() as target:
        target.prec = precision
        target.rounding = rounding
        rounded = +approximation
        return (
            target.next_minus(rounded)
            if lower
            else target.next_plus(rounded)
        )


def log_interval(value: Interval) -> Interval:
    """Natural logarithm, enlarged outwards by one target-precision ulp."""

    if value.lo <= 0:
        raise ValueError("logarithm requires a positive interval")
    return Interval(
        _ln_decimal(value.lo, value.precision, True),
        _ln_decimal(value.hi, value.precision, False),
        value.precision,
    )


def log_rational(
    numerator: int, denominator: int = 1, precision: int = 40
) -> Interval:
    return log_interval(Interval.rational(numerator, denominator, precision))


def _fraction_upper(value: Fraction, precision: int) -> Decimal:
    return _binary(
        Decimal(value.numerator),
        Decimal(value.denominator),
        precision,
        ROUND_CEILING,
        "div",
    )


@dataclass(frozen=True, slots=True)
class ErrorBudget:
    """Numerical error classes kept distinct in every certificate."""

    rounding: Decimal
    truncation: Decimal
    modelling: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "rounding": str(self.rounding),
            "truncation": str(self.truncation),
            "modelling": self.modelling,
        }


@dataclass(frozen=True, slots=True)
class GaugeCertificate:
    model: str
    parameter: str
    work_units: int
    partial: Interval
    enclosure: Interval
    errors: ErrorBudget

    def to_dict(self) -> Dict[str, object]:
        return {
            "model": self.model,
            "parameter": self.parameter,
            "work_units": self.work_units,
            "partial": self.partial.to_strings(),
            "enclosure": self.enclosure.to_strings(),
            "errors": self.errors.to_dict(),
        }


def certified_log_gauge_integral(
    q_numerator: int,
    q_denominator: int,
    panels: int = 4096,
    precision: int = 40,
) -> GaugeCertificate:
    r"""Enclose ``integral_0^1 -log(1-qx) dx`` by monotone rectangles.

    The logarithmic kernel is a concrete polarised-line benchmark for the
    archimedean gauge.  It is not asserted to equal the SPG strain trace.
    """

    q = Fraction(q_numerator, q_denominator)
    if not 0 < q < 1:
        raise ValueError("q must lie strictly between zero and one")
    if panels <= 0:
        raise ValueError("panels must be positive")
    lower = Interval.point(0, precision)
    upper = Interval.point(0, precision)
    width = Interval.rational(1, panels, precision)
    for i in range(panels):
        left_arg = Fraction(1) - q * Fraction(i, panels)
        right_arg = Fraction(1) - q * Fraction(i + 1, panels)
        f_left = -log_rational(
            left_arg.numerator, left_arg.denominator, precision
        )
        f_right = -log_rational(
            right_arg.numerator, right_arg.denominator, precision
        )
        lower = lower + f_left * width
        upper = upper + f_right * width
    enclosure = Interval(lower.lo, upper.hi, precision)
    rounding = lower.width + upper.width
    discretisation = max(
        Decimal(0),
        _binary(
            enclosure.width,
            rounding,
            precision,
            ROUND_CEILING,
            "sub",
        ),
    )
    return GaugeCertificate(
        model="logarithmic polarised-line gauge integral",
        parameter=f"{q.numerator}/{q.denominator}",
        work_units=panels,
        partial=enclosure,
        enclosure=enclosure,
        errors=ErrorBudget(
            rounding=rounding,
            truncation=discretisation,
            modelling=(
                "unbounded until PO-087 identifies this benchmark with the "
                "archimedean strain-trace integrand"
            ),
        ),
    )


def certified_tate_q_product(
    q_numerator: int,
    q_denominator: int,
    terms: int = 32,
    precision: int = 40,
) -> GaugeCertificate:
    r"""Enclose a Tate-cusp metric benchmark and its infinite product tail.

    The benchmark is

        -log(q)/12 - 2 sum_{n>=1} log(1-q^n),   0 < q < 1.

    Its omitted tail is at most ``2*q^(N+1)/(1-q)^2``.
    """

    q = Fraction(q_numerator, q_denominator)
    if not 0 < q < 1:
        raise ValueError("q must lie strictly between zero and one")
    if terms <= 0:
        raise ValueError("terms must be positive")
    partial = -log_rational(q.numerator, q.denominator, precision).scale(
        1, 12
    )
    for n in range(1, terms + 1):
        argument = Fraction(1) - q**n
        partial = partial - log_rational(
            argument.numerator, argument.denominator, precision
        ).scale(2)
    tail = Fraction(2) * q ** (terms + 1) / (Fraction(1) - q) ** 2
    tail_upper = _fraction_upper(tail, precision)
    enclosure = Interval(
        partial.lo,
        _binary(
            partial.hi,
            tail_upper,
            precision,
            ROUND_CEILING,
            "add",
        ),
        precision,
    )
    return GaugeCertificate(
        model="Tate q-product metric benchmark",
        parameter=f"{q.numerator}/{q.denominator}",
        work_units=terms,
        partial=partial,
        enclosure=enclosure,
        errors=ErrorBudget(
            rounding=partial.width,
            truncation=tail_upper,
            modelling=(
                "unbounded until PO-087 identifies the q-product metric with "
                "the archimedean strain-trace contribution"
            ),
        ),
    )


@dataclass(frozen=True, slots=True)
class FiniteTraceCertificate:
    coefficients: Mapping[int, int]
    enclosure: Interval
    errors: ErrorBudget
    conductor: int
    minimal_discriminant: int

    def to_dict(self) -> Dict[str, object]:
        return {
            "coefficients": {
                str(p): exponent for p, exponent in self.coefficients.items()
            },
            "enclosure": self.enclosure.to_strings(),
            "errors": self.errors.to_dict(),
            "conductor": str(self.conductor),
            "minimal_discriminant": str(self.minimal_discriminant),
        }


def _factor_exponents(n: int) -> Dict[int, int]:
    return dict(prime_factors(abs(n)))


def certified_finite_frey_trace(
    a: int, b: int, c: int, precision: int = 40
) -> FiniteTraceCertificate:
    r"""Certify ``log|Delta_min| - log N`` prime by prime for a Frey curve."""

    curve = frey.frey_curve(a, b, c)
    conductor = frey.conductor(curve)
    delta = frey.minimal_discriminant(curve)
    d_factors = _factor_exponents(delta)
    n_factors = _factor_exponents(conductor)
    primes = sorted(set(d_factors) | set(n_factors))
    coefficients = {
        p: d_factors.get(p, 0) - n_factors.get(p, 0) for p in primes
    }
    result = Interval.point(0, precision)
    for p, coefficient in coefficients.items():
        result = result + log_rational(p, precision=precision).scale(
            coefficient
        )
    return FiniteTraceCertificate(
        coefficients=coefficients,
        enclosure=result,
        errors=ErrorBudget(
            rounding=result.width,
            truncation=Decimal(0),
            modelling=(
                "unbounded until PO-088 proves that these local logarithms "
                "are the finite strain-trace summands"
            ),
        ),
        conductor=conductor,
        minimal_discriminant=delta,
    )


def certified_abc_slack(
    a: int,
    b: int,
    c: int,
    epsilon_numerator: int,
    epsilon_denominator: int,
    constant_numerator: int = 1,
    constant_denominator: int = 1,
    precision: int = 40,
) -> Interval:
    r"""Enclose ``(1+epsilon) log rad(abc) + log C - log c``."""

    triple = Triple(min(a, b), max(a, b), c)
    if epsilon_denominator <= 0 or epsilon_numerator < 0:
        raise ValueError("epsilon must be a non-negative rational")
    if constant_numerator <= 0 or constant_denominator <= 0:
        raise ValueError("the multiplicative constant must be positive")
    main = log_rational(triple.rad, precision=precision).scale(
        epsilon_denominator + epsilon_numerator, epsilon_denominator
    )
    constant = log_rational(
        constant_numerator, constant_denominator, precision
    )
    return main + constant - log_rational(triple.c, precision=precision)


@dataclass(frozen=True, slots=True)
class NewtonCertificate:
    radicand: int
    initial: Interval
    enclosure: Interval
    iterations: int
    unique: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "radicand": self.radicand,
            "initial": self.initial.to_strings(),
            "enclosure": self.enclosure.to_strings(),
            "iterations": self.iterations,
            "unique": self.unique,
        }


def interval_newton_sqrt(
    radicand: int,
    lower: int | str | Decimal,
    upper: int | str | Decimal,
    iterations: int = 8,
    precision: int = 40,
) -> NewtonCertificate:
    """A posteriori interval-Newton certificate for ``x^2-radicand=0``."""

    if radicand <= 0:
        raise ValueError("radicand must be positive")
    current = Interval(_decimal(lower), _decimal(upper), precision)
    initial = current
    unique = False
    completed = 0
    for completed in range(1, iterations + 1):
        if current.lo <= 0:
            raise ValueError("the initial interval must be positive")
        midpoint = Interval.point(current.midpoint, precision)
        value = midpoint * midpoint - Interval.point(radicand, precision)
        derivative = current.scale(2)
        newton_image = midpoint - value / derivative
        next_interval = current.intersection(newton_image)
        unique = unique or current.interior_contains(newton_image)
        current = next_interval
        if current.width == 0:
            break
    return NewtonCertificate(
        radicand=radicand,
        initial=initial,
        enclosure=current,
        iterations=completed,
        unique=unique,
    )
