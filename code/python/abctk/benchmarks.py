# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Reproducible reports for Chapters 48 and 49.

Run from ``code/python`` with

    python -m abctk.benchmarks

The timings are descriptive wall-clock measurements, not regression
thresholds.  All mathematical values in the report are exact except the
explicit floating-point root residual and elapsed times.
"""

from __future__ import annotations

import json
import platform
import statistics
import time
from typing import Any, Callable

from . import habiro, prismatic, qcalc


def _median_time(
    fn: Callable[[], object], repeats: int = 7, iterations: int = 1
) -> float:
    values = []
    for _ in range(repeats):
        start = time.perf_counter()
        for _j in range(iterations):
            fn()
        values.append((time.perf_counter() - start) / iterations)
    return statistics.median(values)


def _deterministic_habiro(precision: int) -> habiro.HabiroElement:
    digits = []
    for n in range(precision):
        digits.append(tuple(((n + 2 * i) % 5) - 2 for i in range(n + 1)))
    return habiro.HabiroElement(tuple(digits))


def _environment() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or "unspecified",
    }


def chapter48_report() -> dict[str, Any]:
    sample = habiro.HabiroElement(
        (
            (1,),
            (0, 1),
            (1, -1, 1),
            (2, 0, -1, 1),
            (0, 1, 0, -1, 1),
            (1, 0, 0, 0, 0, 1),
        )
    )
    evaluations = []
    for order in range(1, 7):
        ev = sample.evaluate_root(order)
        evaluations.append(
            {
                "order": order,
                "residue": list(ev.residue),
                "certified": ev.certified,
                "terms_used": ev.terms_used,
            }
        )

    root_order = 11
    zeta = __import__("cmath").exp(2j * __import__("math").pi / root_order)
    direct = 1 + 0j
    for j in range(1, root_order + 1):
        direct *= 1 - zeta**j

    pochhammer_timings = []
    for n in (20, 40, 80):
        elapsed = _median_time(lambda n=n: habiro.q_pochhammer(n))
        pochhammer_timings.append({"n": n, "milliseconds": 1000 * elapsed})

    multiplication_timings = []
    for precision in (8, 12, 16):
        element = _deterministic_habiro(precision)
        elapsed = _median_time(lambda e=element: e.multiply(e))
        multiplication_timings.append(
            {"precision": precision, "milliseconds": 1000 * elapsed}
        )

    jet = qcalc.q_derivative_jet((0, 7, 0, -2, 0, 1), 3)
    return {
        "environment": _environment(),
        "sample_digits": [list(d) for d in sample.digits],
        "sample_residue": list(sample.to_residue()),
        "root_evaluations": evaluations,
        "q_pochhammer_6": list(habiro.q_pochhammer(6)),
        "coefficient_growth": [
            habiro.q_pochhammer_stats(n) for n in (4, 8, 12, 20, 30, 40, 60)
        ],
        "floating_zero_test": {
            "order": root_order,
            "exact_cyclotomic_remainder": list(
                habiro.poly_mod_cyclotomic(
                    habiro.q_pochhammer(root_order), root_order
                )
            ),
            "direct_complex_absolute_value": abs(direct),
        },
        "q_derivative_jet": {
            f"x^{x_degree}u^{u_degree}": str(coeff)
            for (x_degree, u_degree), coeff in sorted(jet.items())
        },
        "timings": {
            "q_pochhammer": pochhammer_timings,
            "habiro_square": multiplication_timings,
        },
    }


def chapter49_report() -> dict[str, Any]:
    p = 3
    a = (1, 2, 1, 0)
    b = (2, 1, 0, 1)
    gauge = prismatic.FGaugeRecord(
        p=5,
        precision=8,
        basis=("e_0", "e_1"),
        weights=(0, 1),
        frobenius=((1, 0), (0, 5)),
        metadata={"model": "split ordinary rank-two example"},
    )
    matrix = ((1, 0), (0, 5))
    vectors = ((1, 0), (0, 1), (5, 1), (25, 5))

    witt_timings = []
    for length in (2, 3, 4, 5):
        left = tuple((i % 3) + 1 for i in range(length))
        right = tuple(((2 * i) % 3) + 1 for i in range(length))
        elapsed = _median_time(
            lambda left=left, right=right: prismatic.witt_mul(2, left, right),
            iterations=1000,
        )
        witt_timings.append({"length": length, "milliseconds": 1000 * elapsed})

    nygaard_timings = []
    for rank in (8, 16, 32):
        matrix_rank = tuple(
            tuple((5 if i == j and i % 2 else 1 if i == j else 0) for j in range(rank))
            for i in range(rank)
        )
        vector_rank = tuple(i + 1 for i in range(rank))
        elapsed = _median_time(
            lambda matrix_rank=matrix_rank, vector_rank=vector_rank: prismatic.nygaard_level(
                matrix_rank, vector_rank, 5, 8
            ),
            iterations=1000,
        )
        nygaard_timings.append({"rank": rank, "milliseconds": 1000 * elapsed})

    gauge_timings = []
    for rank in (4, 8, 12):
        weights = tuple(i % 2 for i in range(rank))
        frobenius = tuple(
            tuple((5 ** weights[j] if i == j else 0) for j in range(rank))
            for i in range(rank)
        )
        record = prismatic.FGaugeRecord(
            p=5,
            precision=8,
            basis=tuple(f"e_{i}" for i in range(rank)),
            weights=weights,
            frobenius=frobenius,
        )
        elapsed = _median_time(
            record.strong_divisibility_certificate, iterations=200
        )
        gauge_timings.append({"rank": rank, "milliseconds": 1000 * elapsed})

    point_timings = []
    for prime, iterations in ((101, 200), (1009, 20), (5003, 5)):
        elapsed = _median_time(
            lambda prime=prime: prismatic.elliptic_point_count(prime, -1, 0),
            iterations=iterations,
        )
        point_timings.append({"p": prime, "milliseconds": 1000 * elapsed})

    return {
        "environment": _environment(),
        "truncation_set_p3_length4": list(prismatic.p_typical_truncation_set(3, 4)),
        "witt": {
            "p": p,
            "a": list(a),
            "b": list(b),
            "ghost_a": list(prismatic.ghost_components(p, a)),
            "ghost_b": list(prismatic.ghost_components(p, b)),
            "sum": list(prismatic.witt_add(p, a, b)),
            "product": list(prismatic.witt_mul(p, a, b)),
            "frobenius_a": list(prismatic.witt_frobenius(p, a)),
            "verschiebung": list(prismatic.witt_verschiebung(a, 4)),
        },
        "delta": {"p": 3, "x": 10, "value": prismatic.delta_integer(10, 3)},
        "nygaard": [
            {
                "vector": list(v),
                "level": prismatic.nygaard_level(matrix, v, 5, 8),
            }
            for v in vectors
        ],
        "gauge": gauge.to_dict(),
        "tate_curve": prismatic.tate_curve_data(5, 7),
        "reduction_I7": prismatic.elliptic_reduction_data(5, "I7"),
        "reduction_II": prismatic.elliptic_reduction_data(5, "II"),
        "elliptic_good": prismatic.elliptic_frobenius_data(5, -1, 0),
        "timings": {
            "witt_multiplication_p2": witt_timings,
            "nygaard_dense": nygaard_timings,
            "gauge_certificate": gauge_timings,
            "elliptic_point_count": point_timings,
        },
    }


def main() -> int:
    print("CHAPTER 48")
    print(json.dumps(chapter48_report(), indent=2, sort_keys=True))
    print("CHAPTER 49")
    print(json.dumps(chapter49_report(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
