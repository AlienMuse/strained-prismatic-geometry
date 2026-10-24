# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Generate every numerical datum printed in Chapters 50 and 51."""

from __future__ import annotations

import argparse
import json
import platform
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "python"))

from abctk import __version__, certified, engine, radicals, triples  # noqa: E402


def timed(function, *args, **kwargs):
    start = perf_counter()
    value = function(*args, **kwargs)
    return value, perf_counter() - start


def generate() -> dict:
    integral = certified.certified_log_gauge_integral(
        1, 2, panels=4096, precision=32
    )
    tate = certified.certified_tate_q_product(
        1, 10, terms=24, precision=32
    )
    newton = certified.interval_newton_sqrt(
        2, "1.4", "1.5", iterations=8, precision=40
    )

    examples = (
        ("small", triples.Triple(1, 8, 9)),
        ("reyssat", triples.known_records()[0]),
        ("de-weger", triples.known_records()[1]),
    )
    records = {
        name: engine.build_record(triple, precision=32).to_dict()
        | {
            "artifact_hash": engine.build_record(
                triple, precision=32
            ).artifact_hash
        }
        for name, triple in examples
    }
    reyssat = triples.known_records()[0]
    slack = {
        "epsilon_1_10": certified.certified_abc_slack(
            reyssat.a, reyssat.b, reyssat.c, 1, 10, precision=32
        ).to_strings(),
        "epsilon_2_3": certified.certified_abc_slack(
            reyssat.a, reyssat.b, reyssat.c, 2, 3, precision=32
        ).to_strings(),
    }

    sieve, sieve_seconds = timed(radicals.radical_sieve, 100_000)
    found, search_seconds = timed(
        lambda: list(triples.search(5_000, 1.0))
    )

    connection = sqlite3.connect(":memory:")
    engine.initialise_database(connection)
    tables = engine.schema_tables(connection)
    source_files = [
        ROOT / "code" / "python" / "abctk" / name
        for name in (
            "certified.py",
            "engine.py",
            "frey.py",
            "radicals.py",
            "tate.py",
            "triples.py",
        )
    ]
    provenance = engine.provenance_snapshot(source_files)

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "package_version": __version__,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "source_hash": provenance["source_hash"],
        "certificates": {
            "log_gauge_integral": integral.to_dict(),
            "tate_q_product": tate.to_dict(),
            "interval_newton": newton.to_dict(),
            "frey_records": records,
            "reyssat_slack": slack,
        },
        "database": {"table_count": len(tables), "tables": list(tables)},
        "benchmark": {
            "radical_sieve": {
                "limit": 100_000,
                "seconds": sieve_seconds,
                "last_value": sieve[-1],
            },
            "triple_search": {
                "limit": 5_000,
                "minimum_quality": 1.0,
                "records_returned": len(found),
                "seconds": search_seconds,
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("ch50_51_results.json"),
    )
    args = parser.parse_args()
    payload = generate()
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
