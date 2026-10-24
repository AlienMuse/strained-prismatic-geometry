# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Exact tests for the computational content of Chapters 48 and 49."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from abctk import habiro, prismatic, qcalc


def test_q_pochhammer_small_values():
    assert habiro.q_pochhammer(0) == (1,)
    assert habiro.q_pochhammer(1) == (1, -1)
    assert habiro.q_pochhammer(2) == (1, -1, -1, 1)
    assert habiro.q_pochhammer_stats(2)["degree"] == 3


def test_cyclotomic_polynomials():
    assert habiro.cyclotomic_polynomial(1) == (-1, 1)
    assert habiro.cyclotomic_polynomial(2) == (1, 1)
    assert habiro.cyclotomic_polynomial(3) == (1, 1, 1)
    assert habiro.cyclotomic_polynomial(4) == (1, 0, 1)
    assert habiro.cyclotomic_polynomial(6) == (1, -1, 1)


def test_habiro_mixed_radix_roundtrip():
    for precision in range(1, 7):
        modulus_degree = precision * (precision + 1) // 2
        poly = tuple((3 * i * i - 2 * i + 1) % 11 - 5 for i in range(modulus_degree))
        encoded = habiro.HabiroElement.from_residue(poly, precision)
        assert encoded.to_residue() == habiro.poly_mod(poly, habiro.q_pochhammer(precision))


def test_habiro_multiplication_matches_residue_product():
    left = habiro.HabiroElement(((1,), (1, -1), (0, 2, 1), (1, 0, 0, -1)))
    right = habiro.HabiroElement(((2,), (0, 1), (1, 0, -1), (0, 1, -1, 1)))
    product = left.multiply(right)
    expected = habiro.poly_mod(
        habiro.poly_mul(left.to_residue(), right.to_residue()),
        habiro.q_pochhammer(4),
    )
    assert product.to_residue() == expected


def test_root_evaluation_stabilises_at_the_order():
    prefix = ((1,), (0, 1), (1, -1, 1))
    a = habiro.HabiroElement(prefix + ((5, 4, 3, 2),))
    b = habiro.HabiroElement(prefix + ((-7, 0, 9, 1),))
    eva = a.evaluate_root(3)
    evb = b.evaluate_root(3)
    assert eva.certified and evb.certified
    assert eva.residue == evb.residue
    assert eva.terms_used == 3


def test_q_pochhammer_vanishes_cyclotomically():
    for order in range(1, 13):
        assert habiro.poly_mod_cyclotomic(habiro.q_pochhammer(order), order) == ()


def test_q_derivative_jet_has_classical_constant_term():
    coefficients = (7, -4, 0, 1)
    jet = qcalc.q_derivative_jet(coefficients, 3)
    assert jet[(0, 0)] == -4
    assert jet[(2, 0)] == 3
    assert jet[(2, 1)] == 3
    assert jet[(2, 2)] == 1


def test_witt_addition_and_multiplication_have_correct_ghosts():
    p = 3
    a = (1, 2, 1, 0)
    b = (2, 1, 0, 1)
    total = prismatic.witt_add(p, a, b)
    product = prismatic.witt_mul(p, a, b)
    ga = prismatic.ghost_components(p, a)
    gb = prismatic.ghost_components(p, b)
    assert prismatic.ghost_components(p, total) == tuple(x + y for x, y in zip(ga, gb))
    assert prismatic.ghost_components(p, product) == tuple(x * y for x, y in zip(ga, gb))


def test_witt_frobenius_shifts_ghosts():
    vector = (1, 2, 1, 0)
    ghosts = prismatic.ghost_components(3, vector)
    frobenius = prismatic.witt_frobenius(3, vector)
    assert prismatic.ghost_components(3, frobenius) == ghosts[1:]


def test_verschiebung_ghost_identity():
    vector = (2, 1, 3)
    shifted = prismatic.witt_verschiebung(vector)
    gv = prismatic.ghost_components(5, shifted)
    ga = prismatic.ghost_components(5, vector)
    assert gv[0] == 0
    assert gv[1:] == tuple(5 * x for x in ga)


def test_delta_integer_identity():
    value = prismatic.delta_integer(10, 3)
    assert value == -330
    assert 10**3 + 3 * value == 10


def test_nygaard_level_and_divided_frobenius():
    matrix = ((1, 0), (0, 5))
    assert prismatic.nygaard_level(matrix, (1, 0), 5, 8) == 0
    assert prismatic.nygaard_level(matrix, (0, 1), 5, 8) == 1
    assert prismatic.nygaard_level(matrix, (0, 5), 5, 8) == 2
    assert prismatic.divided_frobenius(matrix, (0, 5), 5, 2) == (0, 1)


def test_f_gauge_strong_divisibility_certificate():
    gauge = prismatic.FGaugeRecord(
        p=5,
        precision=8,
        basis=("e0", "e1"),
        weights=(0, 1),
        frobenius=((1, 0), (0, 5)),
    )
    certificate = gauge.strong_divisibility_certificate()
    assert certificate["strongly_divisible"]
    assert certificate["normalised_frobenius"] == ((1, 0), (0, 1))
    assert certificate["determinant_mod_p"] == 1


def test_reduction_type_tables_reject_wild_guessing():
    assert prismatic.elliptic_reduction_data(5, "I7")["conductor_exponent"] == 1
    assert prismatic.elliptic_reduction_data(5, "II")["minimal_discriminant_valuation"] == 2
    try:
        prismatic.elliptic_reduction_data(3, "II")
    except NotImplementedError:
        pass
    else:
        raise AssertionError("wild additive reduction was guessed")


def test_tate_curve_and_good_elliptic_examples():
    tate = prismatic.tate_curve_data(5, 7)
    assert tate["kodaira"] == "I_7"
    assert tate["conductor_exponent"] == 1
    good = prismatic.elliptic_frobenius_data(5, -1, 0)
    assert good["points"] == 8
    assert good["trace"] == -2
    assert good["characteristic_polynomial"] == [1, 2, 5]
