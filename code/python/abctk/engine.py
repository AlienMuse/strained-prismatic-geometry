# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vincent Liu, WiseMotif.ai
"""Architecture and provenance kernel for the abc verification engine.

The module supplies the concrete SQLite schema, canonical serialisation, and
end-to-end records used in Chapter 51.  It stores integers and Decimal
endpoints as text so that neither database drivers nor JSON encoders silently
round arithmetic data.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sqlite3
import sys
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import frey
from .certified import certified_finite_frey_trace
from .radicals import prime_factors
from .triples import Triple


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    created_utc TEXT NOT NULL,
    package_version TEXT NOT NULL,
    python_version TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    config_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'complete', 'failed'))
);

CREATE TABLE IF NOT EXISTS triples (
    triple_id TEXT PRIMARY KEY,
    a TEXT NOT NULL,
    b TEXT NOT NULL,
    c TEXT NOT NULL,
    radical TEXT NOT NULL,
    quality_lo TEXT NOT NULL,
    quality_hi TEXT NOT NULL,
    source TEXT NOT NULL,
    UNIQUE (a, b, c)
);

CREATE TABLE IF NOT EXISTS factorisations (
    triple_id TEXT NOT NULL REFERENCES triples(triple_id),
    operand TEXT NOT NULL CHECK (operand IN ('a', 'b', 'c')),
    prime TEXT NOT NULL,
    exponent INTEGER NOT NULL CHECK (exponent > 0),
    method TEXT NOT NULL,
    certificate_hash TEXT,
    PRIMARY KEY (triple_id, operand, prime)
);

CREATE TABLE IF NOT EXISTS curves (
    curve_id TEXT PRIMARY KEY,
    triple_id TEXT NOT NULL UNIQUE REFERENCES triples(triple_id),
    a1 TEXT NOT NULL,
    a2 TEXT NOT NULL,
    a3 TEXT NOT NULL,
    a4 TEXT NOT NULL,
    a6 TEXT NOT NULL,
    discriminant TEXT NOT NULL,
    minimal_discriminant TEXT NOT NULL,
    conductor TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS local_data (
    curve_id TEXT NOT NULL REFERENCES curves(curve_id),
    prime TEXT NOT NULL,
    kodaira TEXT NOT NULL,
    conductor_exponent INTEGER NOT NULL,
    components INTEGER NOT NULL,
    delta_valuation INTEGER NOT NULL,
    certificate_json TEXT NOT NULL,
    PRIMARY KEY (curve_id, prime)
);

CREATE TABLE IF NOT EXISTS gauge_terms (
    gauge_id TEXT PRIMARY KEY,
    curve_id TEXT NOT NULL REFERENCES curves(curve_id),
    place TEXT NOT NULL,
    model TEXT NOT NULL,
    value_lo TEXT NOT NULL,
    value_hi TEXT NOT NULL,
    rounding_error TEXT NOT NULL,
    truncation_error TEXT NOT NULL,
    modelling_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ledger (
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    obligation_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('proved', 'assumed', 'open', 'failed')),
    evidence_hash TEXT,
    note TEXT NOT NULL,
    PRIMARY KEY (run_id, obligation_id)
);

CREATE TABLE IF NOT EXISTS reports (
    report_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    triple_id TEXT NOT NULL REFERENCES triples(triple_id),
    canonical_json TEXT NOT NULL,
    artifact_hash TEXT NOT NULL,
    status TEXT NOT NULL
);
"""


def _normalise(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if is_dataclass(value):
        return _normalise(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): _normalise(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalise(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    """Canonical UTF-8 JSON: sorted keys, compact separators, no NaN."""

    return json.dumps(
        _normalise(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_identifier(prefix: str, value: Any) -> str:
    return f"{prefix}-{sha256_text(canonical_json(value))[:24]}"


def initialise_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_SQL)


def schema_tables(connection: sqlite3.Connection) -> Sequence[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return tuple(row[0] for row in rows)


@dataclass(frozen=True, slots=True)
class EngineRecord:
    triple_id: str
    curve_id: str
    triple: Mapping[str, Any]
    factorisations: Mapping[str, Mapping[int, int]]
    curve: Mapping[str, Any]
    local: Mapping[int, Mapping[str, Any]]
    finite_trace: Mapping[str, Any]
    assumptions: Sequence[str]
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triple_id": self.triple_id,
            "curve_id": self.curve_id,
            "triple": dict(self.triple),
            "factorisations": {
                key: dict(value) for key, value in self.factorisations.items()
            },
            "curve": dict(self.curve),
            "local": {
                str(prime): dict(value) for prime, value in self.local.items()
            },
            "finite_trace": dict(self.finite_trace),
            "assumptions": list(self.assumptions),
            "status": self.status,
        }

    @property
    def artifact_hash(self) -> str:
        return sha256_text(canonical_json(self.to_dict()))


def _quality_interval(triple: Triple, precision: int) -> Dict[str, str]:
    from .certified import log_rational

    numerator = log_rational(triple.c, precision=precision)
    denominator = log_rational(triple.rad, precision=precision)
    quality = numerator / denominator
    return quality.to_strings()


def build_record(
    triple: Triple,
    precision: int = 40,
    source: str = "abctk",
) -> EngineRecord:
    """Build a deterministic arithmetic record for one abc triple."""

    curve = frey.frey_curve(triple.a, triple.b, triple.c)
    finite = certified_finite_frey_trace(
        triple.a, triple.b, triple.c, precision
    )
    triple_payload = {
        "a": triple.a,
        "b": triple.b,
        "c": triple.c,
        "radical": triple.rad,
        "quality": _quality_interval(triple, precision),
        "source": source,
    }
    triple_id = stable_identifier(
        "triple", {"a": triple.a, "b": triple.b, "c": triple.c}
    )
    curve_payload = {
        "a1": curve.a1,
        "a2": curve.a2,
        "a3": curve.a3,
        "a4": curve.a4,
        "a6": curve.a6,
        "discriminant": curve.discriminant,
        "minimal_discriminant": finite.minimal_discriminant,
        "conductor": finite.conductor,
    }
    local_payload: Dict[int, Dict[str, Any]] = {}
    delta_factors = prime_factors(abs(finite.minimal_discriminant))
    conductor_factors = prime_factors(finite.conductor)
    for prime in sorted(set(delta_factors) | set(conductor_factors)):
        try:
            datum = frey.local_data(curve, prime)
            local_payload[prime] = {
                "kodaira": datum.kodaira,
                "conductor_exponent": datum.f,
                "components": datum.m,
                "delta_valuation": datum.v_delta_min,
                "method": "Tate algorithm with Ogg check",
            }
        except NotImplementedError:
            conductor_exponent = conductor_factors.get(prime, 0)
            delta_valuation = delta_factors.get(prime, 0)
            local_payload[prime] = {
                "kodaira": (
                    f"I{delta_valuation}"
                    if conductor_exponent == 1
                    else "additive-tame"
                ),
                "conductor_exponent": conductor_exponent,
                "components": (
                    delta_valuation
                    if conductor_exponent == 1
                    else delta_valuation + 1 - conductor_exponent
                ),
                "delta_valuation": delta_valuation,
                "method": "tame valuation classification",
            }
    curve_id = stable_identifier(
        "curve", {"triple_id": triple_id, **curve_payload}
    )
    return EngineRecord(
        triple_id=triple_id,
        curve_id=curve_id,
        triple=triple_payload,
        factorisations={
            "a": prime_factors(triple.a),
            "b": prime_factors(triple.b),
            "c": prime_factors(triple.c),
        },
        curve=curve_payload,
        local=local_payload,
        finite_trace=finite.to_dict(),
        assumptions=("PO-087", "PO-088", "PO-089"),
        status="arithmetic-certified/model-conditional",
    )


def provenance_snapshot(source_files: Iterable[Path]) -> Dict[str, str]:
    """Hash source files and record the interpreter used for a run."""

    paths = [path.resolve() for path in source_files]
    if not paths:
        raise ValueError("at least one source file is required")
    base = Path(os.path.commonpath([str(path.parent) for path in paths]))
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        digest.update(path.relative_to(base).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source_hash": digest.hexdigest(),
    }


def store_record(
    connection: sqlite3.Connection,
    run_id: str,
    record: EngineRecord,
) -> str:
    """Store one record atomically and return its report identifier."""

    with connection:
        return _store_record_rows(connection, run_id, record)


def _store_record_rows(
    connection: sqlite3.Connection,
    run_id: str,
    record: EngineRecord,
) -> str:
    """Insert rows inside the transaction owned by :func:`store_record`."""

    triple = record.triple
    quality = triple["quality"]
    connection.execute(
        "INSERT OR IGNORE INTO triples "
        "(triple_id,a,b,c,radical,quality_lo,quality_hi,source) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            record.triple_id,
            str(triple["a"]),
            str(triple["b"]),
            str(triple["c"]),
            str(triple["radical"]),
            quality["lo"],
            quality["hi"],
            str(triple["source"]),
        ),
    )
    for operand, factors in record.factorisations.items():
        for prime, exponent in factors.items():
            connection.execute(
                "INSERT OR IGNORE INTO factorisations "
                "(triple_id,operand,prime,exponent,method,certificate_hash) "
                "VALUES (?,?,?,?,?,?)",
                (
                    record.triple_id,
                    operand,
                    str(prime),
                    exponent,
                    "exact trial division",
                    None,
                ),
            )
    curve = record.curve
    connection.execute(
        "INSERT OR IGNORE INTO curves "
        "(curve_id,triple_id,a1,a2,a3,a4,a6,discriminant,"
        "minimal_discriminant,conductor,status) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            record.curve_id,
            record.triple_id,
            str(curve["a1"]),
            str(curve["a2"]),
            str(curve["a3"]),
            str(curve["a4"]),
            str(curve["a6"]),
            str(curve["discriminant"]),
            str(curve["minimal_discriminant"]),
            str(curve["conductor"]),
            record.status,
        ),
    )
    for prime, datum in record.local.items():
        connection.execute(
            "INSERT OR REPLACE INTO local_data "
            "(curve_id,prime,kodaira,conductor_exponent,components,"
            "delta_valuation,certificate_json) VALUES (?,?,?,?,?,?,?)",
            (
                record.curve_id,
                str(prime),
                str(datum["kodaira"]),
                int(datum["conductor_exponent"]),
                int(datum["components"]),
                int(datum["delta_valuation"]),
                canonical_json(datum),
            ),
        )
    finite = record.finite_trace
    gauge_id = stable_identifier(
        "gauge",
        {
            "curve_id": record.curve_id,
            "model": "finite logarithmic trace benchmark",
        },
    )
    connection.execute(
        "INSERT OR REPLACE INTO gauge_terms "
        "(gauge_id,curve_id,place,model,value_lo,value_hi,"
        "rounding_error,truncation_error,modelling_status) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (
            gauge_id,
            record.curve_id,
            "finite",
            "log|Delta_min|-log N",
            finite["enclosure"]["lo"],
            finite["enclosure"]["hi"],
            finite["errors"]["rounding"],
            finite["errors"]["truncation"],
            finite["errors"]["modelling"],
        ),
    )
    for obligation in record.assumptions:
        connection.execute(
            "INSERT OR IGNORE INTO ledger "
            "(run_id,obligation_id,status,evidence_hash,note) "
            "VALUES (?,?,?,?,?)",
            (
                run_id,
                obligation,
                "open",
                None,
                "required to identify certified benchmark arithmetic "
                "with the SPG strain trace",
            ),
        )
    payload = canonical_json(record.to_dict())
    report_id = stable_identifier(
        "report", {"run_id": run_id, "artifact_hash": record.artifact_hash}
    )
    connection.execute(
        "INSERT OR REPLACE INTO reports "
        "(report_id,run_id,triple_id,canonical_json,artifact_hash,status) "
        "VALUES (?,?,?,?,?,?)",
        (
            report_id,
            run_id,
            record.triple_id,
            payload,
            record.artifact_hash,
            record.status,
        ),
    )
    return report_id
