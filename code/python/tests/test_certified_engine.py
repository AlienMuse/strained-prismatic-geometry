# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Executable numerical claims for Chapters 50 and 51."""

from __future__ import annotations

import math
import sqlite3
import sys
from decimal import Decimal, localcontext
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from abctk import certified, engine, triples


def test_outward_interval_arithmetic_contains_exact_values():
    one_third = certified.Interval.rational(1, 3, precision=24)
    two_sevenths = certified.Interval.rational(2, 7, precision=24)
    product = one_third * two_sevenths
    exact = Decimal(2) / Decimal(21)
    assert product.contains(exact)
    quotient = product / two_sevenths
    assert quotient.contains(Decimal(1) / Decimal(3))


def test_log_interval_contains_binary_reference():
    enclosure = certified.log_rational(2, precision=30)
    with localcontext() as context:
        context.prec = 60
        reference = Decimal(2).ln()
    assert enclosure.contains(reference)
    assert enclosure.width < Decimal("1e-27")


def test_log_gauge_integral_encloses_closed_form():
    certificate = certified.certified_log_gauge_integral(
        1, 2, panels=2048, precision=30
    )
    # Integral_0^1 -log(1-x/2) dx = 1 - log(2).
    reference = Decimal(1) - Decimal(2).ln()
    assert certificate.enclosure.contains(reference)
    assert certificate.errors.modelling.startswith("unbounded")


def test_tate_q_product_tail_is_certified():
    short = certified.certified_tate_q_product(
        1, 10, terms=12, precision=30
    )
    long = certified.certified_tate_q_product(
        1, 10, terms=40, precision=45
    )
    assert short.enclosure.contains(long.enclosure.midpoint)
    assert short.errors.truncation > 0
    assert long.errors.truncation < short.errors.truncation


def test_interval_newton_proves_unique_sqrt_two():
    certificate = certified.interval_newton_sqrt(
        2, "1.4", "1.5", iterations=8, precision=40
    )
    with localcontext() as context:
        context.prec = 60
        reference = Decimal(2).sqrt()
    assert certificate.enclosure.contains(reference)
    assert certificate.unique
    assert certificate.enclosure.width < Decimal("1e-35")


def test_frey_finite_trace_matches_exact_ratio():
    certificate = certified.certified_finite_frey_trace(1, 8, 9, precision=35)
    with localcontext() as context:
        context.prec = 60
        reference = (
            Decimal(abs(certificate.minimal_discriminant)).ln()
            - Decimal(certificate.conductor).ln()
        )
    assert certificate.enclosure.contains(reference)
    assert certificate.errors.truncation == 0


def test_certified_slack_decides_reyssat_at_two_tolerances():
    triple = triples.known_records()[0]
    small = certified.certified_abc_slack(
        triple.a, triple.b, triple.c, 1, 10, precision=32
    )
    large = certified.certified_abc_slack(
        triple.a, triple.b, triple.c, 2, 3, precision=32
    )
    assert small.hi < 0
    assert large.lo > 0


def test_engine_schema_and_record_are_deterministic():
    connection = sqlite3.connect(":memory:")
    engine.initialise_database(connection)
    assert engine.schema_tables(connection) == (
        "curves",
        "factorisations",
        "gauge_terms",
        "ledger",
        "local_data",
        "reports",
        "runs",
        "triples",
    )
    triple = triples.Triple(1, 8, 9)
    first = engine.build_record(triple, precision=30)
    second = engine.build_record(triple, precision=30)
    assert first.artifact_hash == second.artifact_hash
    assert first.triple_id == second.triple_id
    assert first.assumptions == ("PO-087", "PO-088", "PO-089")


def test_store_record_is_transactional_and_hash_addressed():
    connection = sqlite3.connect(":memory:")
    engine.initialise_database(connection)
    connection.execute(
        "INSERT INTO runs "
        "(run_id,created_utc,package_version,python_version,source_hash,"
        "config_json,status) VALUES (?,?,?,?,?,?,?)",
        ("run-test", "2026-01-01T00:00:00Z", "1.1.0", "3", "abc", "{}", "complete"),
    )
    record = engine.build_record(triples.Triple(1, 8, 9), precision=30)
    with connection:
        report_id = engine.store_record(connection, "run-test", record)
    stored = connection.execute(
        "SELECT artifact_hash FROM reports WHERE report_id = ?", (report_id,)
    ).fetchone()
    assert stored == (record.artifact_hash,)
