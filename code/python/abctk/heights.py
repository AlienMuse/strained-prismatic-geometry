# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk.heights — heights, log-volumes, and the shape of the master inequality.

The abc conjecture is a height inequality, and this module fixes the
normalisations the book uses so that no chapter can silently disagree with
another about a factor of 2 or a log.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Tuple

from .radicals import prime_factors, radical


def naive_height(a: int, b: int, c: int) -> float:
    """h(a:b:c) = log max(|a|,|b|,|c|) for the point (a:b:c) in P^2(Q).

    For an abc triple with a, b > 0 and a + b = c this is simply log c.
    """
    return math.log(max(abs(a), abs(b), abs(c)))


def log_radical(n: int) -> float:
    """log rad(n) = sum_{p | n} log p."""
    return sum(math.log(p) for p in prime_factors(abs(n)))


def log_conductor_of_triple(a: int, b: int, c: int) -> float:
    """log rad(abc), the 'ramification' term of the master inequality."""
    seen = set()
    for n in (a, b, c):
        seen.update(prime_factors(abs(n)))
    return sum(math.log(p) for p in seen)


def abc_slack(a: int, b: int, c: int, epsilon: float, const: float = 0.0) -> float:
    """The signed slack in  log c <= (1+eps) log rad(abc) + const.

    A negative value would be a violation of the stated instance of abc for
    that epsilon and constant.  This is the quantity the falsification harness
    of Part IX monitors: the framework predicts it is non-negative for every
    triple once the constant is chosen as the framework prescribes, and a
    single certified negative value refutes the framework.
    """
    return (1.0 + epsilon) * log_conductor_of_triple(a, b, c) + const - math.log(c)


def szpiro_slack(delta: int, conductor_value: int, exponent: float = 6.0,
                 const: float = 0.0) -> float:
    """The signed slack in  log|Delta| <= exponent * log N + const."""
    return exponent * math.log(conductor_value) + const - math.log(abs(delta))


# ---------------------------------------------------------------------------
# Log-volumes
# ---------------------------------------------------------------------------

def local_log_volume(p: int, valuation: int) -> float:
    """The log-volume of the p-adic ball of radius p^{-valuation}.

    Normalised so that the ring of integers Z_p has log-volume 0, hence
    log-vol(p^n Z_p) = -n log p.  With this normalisation the product formula
    reads: the sum of local log-volumes of a principal adele vanishes.
    """
    return -valuation * math.log(p)


def archimedean_log_volume(radius: float) -> float:
    """log-vol of the real interval of the given radius, normalised to [-1,1].

    The archimedean place is the one every classical treatment handles by
    hand.  The framework's requirement is that it be a place like any other,
    and fixing this normalisation here is the first, humblest instance of
    that requirement.
    """
    if radius <= 0:
        raise ValueError("radius must be positive")
    return math.log(radius)


def adelic_log_volume(valuations: Dict[int, int], arch_radius: float) -> float:
    """The total log-volume of an adelic box.

    sum_p log-vol_p  +  log-vol_infty.  For a principal idele this is zero,
    which is the product formula; the book's master inequality is obtained by
    applying a *non-principal* deformation and measuring the defect.
    """
    total = sum(local_log_volume(p, v) for p, v in valuations.items())
    return total + archimedean_log_volume(arch_radius)


def product_formula_defect(n: int) -> float:
    """For a nonzero rational integer n, sum_p v_p(n) log p - log|n|, which is 0.

    A sanity check on the normalisations above; it must return 0.0 up to
    floating error for every n, and the test-suite asserts it.
    """
    s = sum(e * math.log(p) for p, e in prime_factors(abs(n)).items())
    return s - math.log(abs(n))


def quality_from_heights(a: int, b: int, c: int) -> float:
    """q = h / log rad, restated in the height language of Part V."""
    return math.log(c) / log_conductor_of_triple(a, b, c)


def predicted_bound_rst(rad_value: float) -> float:
    """Robert-Stewart-Tenenbaum's conjectured sharp bound on log c.

    log c  <=  log rad + 4 sqrt(3) sqrt( log rad / log log rad ) (1 + o(1)).

    Returned as a bound on log c rather than on c, so that it can be compared
    directly with the framework's own prediction on the same scale.
    """
    if rad_value < 16:
        raise ValueError("asymptotic meaningless for tiny radicals")
    lr = math.log(rad_value)
    llr = math.log(lr)
    return lr + 4.0 * math.sqrt(3.0) * math.sqrt(lr / llr)


def extremal_framework_report(a: int, b: int, c: int,
                              epsilon: float = 0.1) -> Dict[str, object]:
    """Compute the numerical interfaces available before substrate descent.

    ``theta_model`` is one sixth of the logarithm of the discriminant of the
    displayed Frey model, ``16(abc)^2``.  It is deliberately not called the
    categorical strain trace: minimalisation, the exact conductor, the global
    gauge, and the comparison with that trace are not implemented.
    """
    if a <= 0 or b <= 0 or a + b != c or math.gcd(a, b) != 1:
        raise ValueError("expected a coprime positive triple a + b = c")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    log_c = math.log(c)
    log_rad = log_conductor_of_triple(a, b, c)
    model_discriminant = 16 * (a * b * c) ** 2
    log_model_discriminant = math.log(model_discriminant)
    theta_model = log_model_discriminant / 6.0
    theorem_a_main = (1.0 + epsilon) * log_rad

    return {
        "a": a,
        "b": b,
        "c": c,
        "epsilon": epsilon,
        "log_c": log_c,
        "log_rad": log_rad,
        "quality": log_c / log_rad,
        "abc_excess": log_c - log_rad,
        "abc_required_constant": log_c - theorem_a_main,
        "frey_model_discriminant": model_discriminant,
        "log_frey_model_discriminant": log_model_discriminant,
        "theta_model": theta_model,
        "theorem_a_main": theorem_a_main,
        "theta_model_required_constant": theta_model - theorem_a_main,
        "categorical_trace": None,
        "minimal_conductor": None,
        "comparison_status": (
            "proxy only: categorical trace, minimal conductor, and "
            "trace-comparison proof obligations are unavailable"
        ),
    }
