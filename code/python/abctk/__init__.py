# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""
abctk — the certified arithmetic kernel of
*Strained Prismatic Geometry — Deformation over the Absolute Base and the abc Conjecture* (WiseMotif Monograph of Mathematical Intelligence, Series 06).
Vincent Liu, WiseMotif.ai.

This package is not a demonstration.  Every table of numbers printed in the
book is produced by it, and every claim the book makes about a computation is
reproducible by running it.  It is deliberately dependency-light: the core
requires nothing but the standard library, so that a reader can check the
book's arithmetic on any machine with Python 3.10 or later.

Layout
------
    abctk.radicals       integer radicals, squarefree kernels, sieving
    abctk.triples        abc triples: quality, merit, search, the known extrema
    abctk.frey           the Frey-Hellegouarch curve; discriminant, conductor,
                         Tate's algorithm, the Szpiro ratio
    abctk.masonstothers  the function-field abc, proved and verified
    abctk.qcalc          q-integers, the q-derivative, the q-Wronskian
    abctk.habiro         exact Habiro digits and cyclotomic evaluation
    abctk.prismatic      truncated Witt, Nygaard, and F-gauge arithmetic
    abctk.heights        naive heights, log-volumes, the master inequality
    abctk.certified      outward-rounded intervals and trace certificates
    abctk.engine         database schema, provenance, canonical reports
"""

__version__ = "1.1.0"
__author__ = "Vincent Liu"
__affiliation__ = "WiseMotif.ai"

from . import (  # noqa: F401
    certified,
    engine,
    frey,
    habiro,
    heights,
    masonstothers,
    prismatic,
    qcalc,
    radicals,
    tate,
    triples,
)

__all__ = [
    "radicals",
    "triples",
    "frey",
    "tate",
    "masonstothers",
    "qcalc",
    "habiro",
    "prismatic",
    "heights",
    "certified",
    "engine",
]
