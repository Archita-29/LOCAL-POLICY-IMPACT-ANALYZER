"""Read the existing scraper/NLP outputs without coupling the API to a model."""

from __future__ import annotations

import csv
import os
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _database_path() -> Path:
    configured = os.getenv("POLICY_ANALYZER_DB")
    if configured:
        return Path(configured).expanduser()
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("sqlite:///"):
        return Path(url.removeprefix("sqlite:///"))
    return PROJECT_ROOT / "policy_impact.db"


def _csv_rows(name: str) -> list[dict[str, Any]]:
    path = PROJECT_ROOT / name
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _sqlite_tables() -> dict[str, list[dict[str, Any]]]:
    path = _database_path()
    if not path.is_file():
        return {}
    conn = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        result = {}
        for table in ("cleaned_records", "nlp_ready_records", "nlp_processed_records"):
            if table in names:
                # Table names are selected from the fixed allowlist above.
                result[table] = [dict(row) for row in conn.execute(f'SELECT * FROM "{table}"')]
        return result
    finally:
        conn.close()


def _by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["id"]): row for row in rows if row.get("id") is not None}


def load_records() -> list[dict[str, Any]]:
    """Merge cleaned article metadata and NLP output, preferring the live DB."""
    db = _sqlite_tables()
    cleaned = _by_id(db.get("cleaned_records", []))
    ready = _by_id(db.get("nlp_ready_records", []))
    scores = _by_id(db.get("nlp_processed_records", []))

    # CSV exports let the API run before a local SQLite database is populated.
    for row in _csv_rows("cleaned_policy_data.csv"):
        cleaned.setdefault(str(row.get("id", "")), row)
    for row in _csv_rows("nlp_ready_data.csv"):
        ready.setdefault(str(row.get("id", "")), row)
    for row in _csv_rows("nlp_policy_impact_results.csv"):
        scores.setdefault(str(row.get("id", "")), row)

    ids = set(cleaned) | set(ready) | set(scores)
    records: list[dict[str, Any]] = []
    for record_id in ids:
        row = {**cleaned.get(record_id, {}), **ready.get(record_id, {}), **scores.get(record_id, {})}
        row["id"] = record_id
        row["is_near_duplicate"] = _as_bool_or_none(row.get("is_near_duplicate"))
        row["is_policy_relevant"] = _as_bool_or_none(row.get("is_policy_relevant"))
        row["sentiment_score"] = _as_float_or_none(row.get("sentiment_score"))
        row["impact_score"] = _as_float_or_none(row.get("impact_score"))
        records.append(row)
    records.sort(key=lambda row: row.get("published_datetime") or "", reverse=True)
    return records


def _as_float_or_none(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _as_bool_or_none(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    return str(value).strip().lower() in {"1", "true", "yes"}


def data_status() -> dict[str, Any]:
    db_path = _database_path()
    tables = _sqlite_tables()
    has_csv_scores = (PROJECT_ROOT / "nlp_policy_impact_results.csv").is_file()
    return {
        "database_configured": db_path.is_file(),
        "database_path": str(db_path),
        "cleaned_records_available": bool(tables.get("cleaned_records") or _csv_rows("cleaned_policy_data.csv")),
        "nlp_scores_available": bool(tables.get("nlp_processed_records") or has_csv_scores),
    }
