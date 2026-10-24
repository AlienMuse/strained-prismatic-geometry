# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
Test suite for abctk.

These are not unit tests in the software sense.  Each one asserts a statement
that the book prints, so that no number reaches the page without having been
checked by the machine that produced it.  Run with:

    python -m pytest code/python/tests -q
or  python code/python/tests/test_abctk.py
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from abctk import frey, heights, masonstothers as ms, qcalc, radicals, tate, triples


# ---------------------------------------------------------------------------
# Radicals
# ---------------------------------------------------------------------------

def test_radical_basics():
    assert radicals.radical(1) == 1
    assert radicals.radical(2) == 2
    assert radicals.radical(8) == 2
    assert radicals.radical(12) == 6
    assert radicals.radical(1729) == 1729          # 7 * 13 * 19, squarefree
    assert radicals.radical(2 ** 21 * 23) == 46


def test_radical_sieve_agrees_with_factorisation():
    N = 5000
    sieve = radicals.radical_sieve(N)
    for n in range(1, N + 1):
        assert sieve[n] == radicals.radical(n), f"rad({n}) disagrees"


def test_powerful_part():
    assert radicals.powerful_part(8) == 8
    assert radicals.powerful_part(12) == 4         # 2^2, the 3 has exponent 1
    assert radicals.powerful_part(30) == 1


# ---------------------------------------------------------------------------
# Triples
# ---------------------------------------------------------------------------

def test_reyssat_is_the_record():
    """2 + 3^10 * 109 = 23^5, quality 1.6299 (Reyssat 1987)."""
    t = triples.Triple(2, 3 ** 10 * 109, 23 ** 5)
    assert t.c == 6436343
    assert t.rad == 2 * 3 * 109 * 23
    assert abs(t.quality - 1.62991) < 1e-4, t.quality


def test_record_table_is_internally_consistent():
    """Every entry of RECORD_TRIPLES must be a genuine coprime triple."""
    bad = []
    for a, b, c, who in triples.RECORD_TRIPLES:
        lo, hi = min(a, b), max(a, b)
        if lo + hi != c or math.gcd(lo, hi) != 1:
            bad.append((lo, hi, c, who))
    assert not bad, f"table contains non-triples: {bad}"


def test_record_table_has_verified_top_twenty():
    rows = triples.record_report()
    assert len(rows) == 20
    assert [row["rank"] for row in rows] == list(range(1, 21))
    assert all(row["quality"] > 1.0 for row in rows)
    qualities = [row["quality"] for row in rows]
    assert qualities == sorted(qualities, reverse=True)
    assert abs(qualities[0] - 1.6299116841) < 1e-10
    assert abs(qualities[-1] - 1.4813222565) < 1e-10


def test_record_report_factorisations_reconstruct_integers():
    for row in triples.record_report():
        assert radicals.radical(row["a"]) * radicals.radical(row["b"]) * \
            radicals.radical(row["c"]) == row["rad"]


def test_published_census_totals():
    census = triples.census_report()
    assert census["complete_below_10_18"] == 14_482_065
    assert census["additional_10_18_to_2_63"] == 9_345_651
    assert census["archived_total"] == 23_827_716
    assert census["known_quality_at_least_1_4"] == 241


def test_all_records_have_quality_above_one():
    for t in triples.known_records():
        assert t.quality > 1.0, str(t)


def test_search_finds_the_small_records():
    """Exhaustive search to 1000 must find the classical small examples.

    The two canonical ones are 1 + 8 = 9, of quality log 9 / log 6 =
    1.22629, and 5 + 27 = 32, of quality log 32 / log 30 = 1.01898.  The
    two are separated by the search threshold, so running the search at
    two thresholds also tests that the threshold is honoured rather than
    ignored.
    """
    high = {(t.a, t.b, t.c) for t in triples.search(1000, 1.2)}
    assert (1, 8, 9) in high
    assert (5, 27, 32) not in high

    low = {(t.a, t.b, t.c) for t in triples.search(1000, 1.0)}
    assert (1, 8, 9) in low
    assert (5, 27, 32) in low
    assert (1, 48, 49) in low
    assert (32, 49, 81) in low


def test_quality_of_one_eight_nine():
    t = triples.Triple(1, 8, 9)
    assert t.rad == 6
    assert abs(t.quality - math.log(9) / math.log(6)) < 1e-12


# ---------------------------------------------------------------------------
# The Frey curve
# ---------------------------------------------------------------------------

def test_frey_discriminant_identity():
    """Delta(y^2 = x(x-a)(x+b)) = 16 (abc)^2, for every triple."""
    for a, b in ((1, 8), (5, 27), (1, 63), (2, 3 ** 10 * 109)):
        c = a + b
        assert frey.frey_discriminant(a, b, c) == 16 * (a * b * c) ** 2


def test_frey_c4():
    """c4 = 16(a^2 + ab + b^2) for the Frey model."""
    for a, b in ((1, 8), (5, 27), (3, 125)):
        e = frey.frey_curve(a, b, a + b)
        assert e.c4 == 16 * (a * a + a * b + b * b)


def test_szpiro_ratio_is_finite_and_positive():
    e = frey.frey_curve(1, 8, 9)
    d = e.discriminant
    assert d != 0
    rep = frey.szpiro_report(1, 8, 9)
    assert rep["discriminant"] == 16 * (1 * 8 * 9) ** 2
    assert rep["conductor"] is not None
    assert rep["szpiro"] > 0


# ---------------------------------------------------------------------------
# Tate's algorithm at the delicate primes
# ---------------------------------------------------------------------------

#: (a-invariants, conductor).  Curves whose conductor is classical and which
#: between them exercise every branch of Tate's algorithm at 2 and at 3:
#: good, multiplicative, II, III, IV, I_n*, IV*, III*, and non-minimality.
KNOWN_CONDUCTORS = (
    ((0, -1, 1, -10, -20), 11),        # 11a1, I5 at 11
    ((0, 0, 1, -1, 0), 37),            # 37a1, good away from 37
    ((0, 0, 1, 0, 0), 27),             # 27a1, type II at 3, f_3 = 3
    ((0, 0, 0, 0, 16), 27),            # type II at 3, good at 2
    ((0, 0, 0, 0, -432), 27),          # Fermat cubic, type IV* at 3, f_3 = 3
    ((0, 0, 0, 0, 1), 36),             # IV at 2 and III at 3, f = 2 at both
    ((0, 0, 0, -1, 0), 32),            # congruent-number curve, III at 2, f=5
    ((0, 0, 0, 4, 0), 32),             # its 2-isogenous partner, I3* at 2
    ((0, 0, 0, 1, 0), 64),             # type II at 2, f_2 = 6
    ((1, 0, 1, 4, -6), 14),            # I6 at 2
    ((1, 1, 1, -10, -10), 15),         # I4 at 3
    ((0, 1, 1, -2, 0), 389),           # 389a1
    ((0, 0, 1, -7, 6), 5077),          # 5077a1
)


def test_tate_reproduces_known_conductors():
    for ai, N in KNOWN_CONDUCTORS:
        e = frey.Weierstrass(*ai)
        assert frey.conductor(e) == N, (ai, frey.conductor(e), N)


def test_conductor_exponent_no_longer_raises_at_two_and_three():
    """The gap that earlier versions of abctk.frey declared is closed."""
    for ai, _ in KNOWN_CONDUCTORS:
        e = frey.Weierstrass(*ai)
        for p in (2, 3):
            f = frey.conductor_exponent(e, p)
            assert 0 <= f <= (8 if p == 2 else 5)


def test_oggs_formula_holds_on_every_local_datum():
    """f_p = v_p(Delta_min) + 1 - m_p, in the form proved by Saito."""
    for ai, _ in KNOWN_CONDUCTORS:
        e = frey.Weierstrass(*ai)
        for p in (2, 3):
            if e.discriminant % p:
                continue
            d = tate.tate_algorithm(e, p)
            assert d.f == d.v_delta_min + 1 - d.m, str(d)


def test_rst_transform_preserves_the_discriminant():
    e = frey.Weierstrass(1, -1, 1, -3, 3)
    for r in range(-2, 3):
        for s in range(-2, 3):
            for t in range(-2, 3):
                f = tate.rst_transform(e, r, s, t)
                assert f.discriminant == e.discriminant
                assert f.c4 == e.c4 and f.c6 == e.c6


def _v2(n: int) -> int:
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def _predicted_local_2(a: int, b: int, c: int):
    """Theorem 42.5.x: the 2-adic reduction type of the Frey curve.

    Put the even member of {a, b, c} in the middle slot of the Frey
    presentation, let v be its 2-adic valuation and let ``odd`` be the
    first-slot entry of that presentation; the type depends only on v and on
    ``odd`` mod 4.
    """
    if b % 2 == 0:
        v, odd = _v2(b), a
    elif a % 2 == 0:
        v, odd = _v2(a), -c
    else:
        v, odd = _v2(c), -a
    good_class = (odd % 4) == 3
    if v == 1:
        return 5, "III", 6
    if v == 2:
        return (3, "I1*", 8) if good_class else (4, "I0*", 8)
    if v == 3:
        return (3, "III*", 10) if good_class else (4, "I2*", 10)
    if v == 4:
        return (0, "I0", 0) if good_class else (4, "I4*", 12)
    return ((1, "I%d" % (2 * v - 8), 2 * v - 8) if good_class
            else (4, "I%d*" % (2 * v - 4), 4 + 2 * v))


def test_frey_two_adic_classification():
    """Every coprime triple with c < 250 realises the predicted 2-adic type."""
    n = 0
    for c in range(3, 250):
        for a in range(1, c):
            b = c - a
            if math.gcd(a, b) != 1:
                continue
            d = tate.tate_algorithm(frey.frey_curve(a, b, c), 2)
            assert (d.f, d.kodaira, d.v_delta_min) == _predicted_local_2(a, b, c), \
                (a, b, c, str(d))
            n += 1
    assert n > 5000


def test_frey_is_semistable_after_normalisation():
    """a = 3 mod 4 and 16 | b force N = rad(abc) or rad(abc)/2, and
    |Delta_min| = (abc)^2 / 2^8."""
    n = 0
    for c in range(3, 900):
        for a in range(1, c):
            b = c - a
            if math.gcd(a, b) != 1 or b % 16 or a % 4 != 3:
                continue
            e = frey.frey_curve(a, b, c)
            r = radicals.radical(a) * radicals.radical(b) * radicals.radical(c)
            expected = r if _v2(b) >= 5 else r // 2
            assert frey.conductor(e) == expected, (a, b, c)
            assert abs(frey.minimal_discriminant(e)) == (a * b * c) ** 2 // 2 ** 8
            n += 1
    assert n > 200


def test_frey_conductor_is_within_a_factor_of_sixteen_of_the_radical():
    """rad(abc)/2 <= N <= 16 rad(abc), and both ends are attained."""
    seen = set()
    for c in range(3, 300):
        for a in range(1, c):
            b = c - a
            if math.gcd(a, b) != 1:
                continue
            e = frey.frey_curve(a, b, c)
            r = radicals.radical(a) * radicals.radical(b) * radicals.radical(c)
            ratio = Fraction(frey.conductor(e), r)
            assert Fraction(1, 2) <= ratio <= 16
            seen.add(ratio)
    assert Fraction(1, 2) in seen and Fraction(16) in seen


def test_frey_is_multiplicative_at_every_odd_bad_prime():
    """v_p(c4) = 0 for every odd p | abc, so f_p = 1 there; only 2 is hard."""
    for a, b in ((1, 8), (5, 27), (2, 3 ** 10 * 109), (121, 48234375)):
        c = a + b
        e = frey.frey_curve(a, b, c)
        for p in radicals.prime_factors(a * b * c):
            if p == 2:
                continue
            assert frey.conductor_exponent(e, p) == 1, (a, b, p)


def test_reyssat_frey_curve_invariants():
    """The numbers printed in Chapter 43 for the record triple."""
    a, b, c = 2, 3 ** 10 * 109, 23 ** 5
    e = frey.frey_curve(a, b, c)
    assert e.discriminant == 16 * (a * b * c) ** 2
    assert frey.conductor(e) == 240672
    assert frey.conductor(e) == 16 * (2 * 3 * 109 * 23)
    d = tate.tate_algorithm(e, 2)
    assert d.kodaira == "III" and d.f == 5 and d.v_delta_min == 6
    assert abs(frey.szpiro_ratio(e) - 5.396476) < 1e-5
    assert abs(frey.modified_szpiro_ratio(e) - 8.262531) < 1e-5


# ---------------------------------------------------------------------------
# Mason-Stothers: the control experiment
# ---------------------------------------------------------------------------

def _P(*cs: int):
    return ms.trim([Fraction(x) for x in cs])


def test_wronskian_vanishes_iff_proportional():
    a = _P(1, 2, 3)
    assert not ms.trim(ms.wronskian(a, [Fraction(5) * x for x in a]))
    assert ms.trim(ms.wronskian(a, _P(0, 1)))


def test_q_derivative_limit_is_the_derivative():
    """nabla_q -> d/dx as q -> 1, on the nose."""
    p = qcalc.qpoly([(3, 0, 1), (1, 0, -4), (0, 0, 7)])      # x^3 - 4x + 7
    got = qcalc.q_to_one(qcalc.q_derivative(p))
    want = ms.derivative(_P(7, -4, 0, 1))                     # 3x^2 - 4
    assert got == want, (got, want)


def test_mason_stothers_holds_on_the_suite():
    for name, a, b in ms.demo_instances():
        rep = ms.mason_stothers_check(a, b)
        assert rep["holds"], f"{name}: {rep}"


def test_mason_stothers_equality_case():
    """a = t^3, b = 1, c = t^3 + 1: deg = 3 and deg rad(abc) - 1 = 3.

    rad(abc) = t * 1 * (t^3+1) has degree 4, so the bound is attained.  The
    sharpness of the -1 is what the book's arithmetic analogue must reproduce.
    """
    rep = ms.mason_stothers_check(_P(0, 0, 0, 1), _P(1))
    assert rep["lhs"] == 3
    assert rep["deg_rad_abc"] == 4
    assert rep["rhs"] == 3
    assert rep["holds"]


def test_radical_poly_is_squarefree():
    """rad((t^2+1)^2) = t^2 + 1."""
    sq = ms.mul(_P(1, 0, 1), _P(1, 0, 1))
    assert ms.radical_poly(sq) == _P(1, 0, 1)


# ---------------------------------------------------------------------------
# q-calculus
# ---------------------------------------------------------------------------

def test_q_integer_specialises_to_n():
    for n in range(0, 8):
        assert qcalc.q_to_one(qcalc.q_integer(n)) == ([Fraction(n)] if n else [])


def test_q_derivative_of_monomial():
    """nabla_q x^n = [n]_q x^{n-1}."""
    for n in range(1, 6):
        p = qcalc.qpoly([(n, 0, 1)])
        got = qcalc.q_derivative(p)
        want = {(n - 1, j): c for (i, j), c in qcalc.q_integer(n).items()}
        assert got == want, (n, got, want)


def test_exact_q_leibniz_holds():
    """nabla_q(fg) = f(qx) nabla_q g + (nabla_q f) g, identically."""
    f = qcalc.qpoly([(2, 0, 1), (0, 0, 3)])
    g = qcalc.qpoly([(3, 1, 2), (1, 0, -1)])
    assert qcalc.q_leibniz_exact(f, g) == {}


def test_naive_q_leibniz_fails():
    """The symmetric rule genuinely fails; the defect is not zero.

    This is the honest statement of the difficulty: the q-world has a
    derivation, but its Leibniz rule is twisted, and every estimate in the
    book has to carry that twist.
    """
    f = qcalc.qpoly([(2, 0, 1)])
    g = qcalc.qpoly([(3, 0, 1)])
    assert qcalc.q_leibniz_defect(f, g) != {}


# ---------------------------------------------------------------------------
# Heights
# ---------------------------------------------------------------------------

def test_product_formula():
    for n in (2, 3, 60, 1729, 2 ** 21 * 23):
        assert abs(heights.product_formula_defect(n)) < 1e-9


def test_quality_agrees_with_triples_module():
    t = triples.Triple(2, 3 ** 10 * 109, 23 ** 5)
    assert abs(heights.quality_from_heights(t.a, t.b, t.c) - t.quality) < 1e-12


def test_abc_slack_positive_for_reyssat_at_epsilon_two_thirds():
    """The record triple has quality 1.63, so eps = 2/3 must leave slack."""
    t = triples.Triple(2, 3 ** 10 * 109, 23 ** 5)
    assert heights.abc_slack(t.a, t.b, t.c, 2.0 / 3.0) > 0


def test_abc_slack_negative_for_reyssat_at_small_epsilon():
    """...and eps = 0.1 must not: the record beats it.  A framework that
    predicted otherwise would be refuted by this one triple."""
    t = triples.Triple(2, 3 ** 10 * 109, 23 ** 5)
    assert heights.abc_slack(t.a, t.b, t.c, 0.1) < 0


def test_extremal_framework_report_is_an_honest_proxy():
    t = triples.Triple(2, 3 ** 10 * 109, 23 ** 5)
    rep = heights.extremal_framework_report(t.a, t.b, t.c, epsilon=0.1)
    assert abs(rep["quality"] - t.quality) < 1e-12
    assert rep["frey_model_discriminant"] == 16 * (t.a * t.b * t.c) ** 2
    assert abs(rep["theta_model"] -
               math.log(rep["frey_model_discriminant"]) / 6.0) < 1e-12
    assert rep["categorical_trace"] is None
    assert rep["minimal_conductor"] is None
    assert rep["abc_required_constant"] > 0


# ---------------------------------------------------------------------------

def _run_all() -> int:
    fns = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in fns:
        try:
            fn()
            print(f"  PASS  {name}")
        except Exception as exc:                      # noqa: BLE001
            failed += 1
            print(f"  FAIL  {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
