"""FastAPI read API for Local Policy Impact Analyzer dashboard data."""

from __future__ import annotations

import os
from collections import Counter, defaultdict
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .data import data_status, load_records


app = FastAPI(
    title="Local Policy Impact Analyzer API",
    version="1.0.0",
    description=(
        "Read endpoints for the scraper and NLP pipeline outputs. Scores are "
        "reported only when present in persisted NLP results."
    ),
)

# Set CORS_ORIGINS to a comma-separated list in deployment. Wildcard is useful
# for local dashboard development; credentials are intentionally disabled.
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [row for row in records if row.get("impact_score") is not None]
    scores = [row["impact_score"] for row in scored]
    sentiments = Counter((row.get("sentiment_label") or "unknown").lower() for row in scored)
    sources: dict[str, list[float]] = defaultdict(list)
    for row in scored:
        if row.get("source"):
            sources[str(row["source"])].append(row["impact_score"])
    return {
        "record_count": len(records),
        "scored_record_count": len(scored),
        "unscored_record_count": len(records) - len(scored),
        "average_impact_score": round(sum(scores) / len(scores), 2) if scores else None,
        "sentiment_counts": dict(sentiments),
        "source_impact": [
            {
                "source": source,
                "scored_count": len(values),
                "average_impact_score": round(sum(values) / len(values), 2),
            }
            for source, values in sorted(sources.items())
        ],
        "data": data_status(),
    }


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {"name": "Local Policy Impact Analyzer API", "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["System"])
def health() -> dict[str, Any]:
    return {"status": "ok", "data": data_status()}


@app.get("/api/v1/dashboard/summary", tags=["Dashboard"])
def dashboard_summary() -> dict[str, Any]:
    """Return totals, sentiment distribution, and source-level score averages."""
    return _summary(load_records())


@app.get("/api/v1/records", tags=["Records"])
def list_records(
    q: str | None = Query(default=None, description="Search title and summary text"),
    source: str | None = None,
    language: str | None = None,
    sentiment: str | None = None,
    policy_relevant: bool | None = None,
    scored_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """List article records with optional filters and stable pagination."""
    rows = load_records()
    if q:
        term = q.casefold()
        rows = [
            r
            for r in rows
            if term
            in f"{r.get('title_clean') or ''} {r.get('summary_clean') or ''}".casefold()
        ]
    if source:
        rows = [r for r in rows if (r.get("source") or "").casefold() == source.casefold()]
    if language:
        rows = [r for r in rows if (r.get("language") or "").casefold() == language.casefold()]
    if sentiment:
        rows = [r for r in rows if (r.get("sentiment_label") or "").casefold() == sentiment.casefold()]
    if policy_relevant is not None:
        rows = [r for r in rows if r.get("is_policy_relevant") is policy_relevant]
    if scored_only:
        rows = [r for r in rows if r.get("impact_score") is not None]
    return {"total": len(rows), "limit": limit, "offset": offset, "items": rows[offset : offset + limit]}


@app.get("/api/v1/records/{record_id}", tags=["Records"])
def get_record(record_id: str) -> dict[str, Any]:
    for record in load_records():
        if record["id"] == record_id:
            return record
    raise HTTPException(status_code=404, detail="Record not found")


@app.get("/api/v1/impact", tags=["Dashboard"])
def impact_by_source() -> dict[str, Any]:
    """Return score aggregates by source; this is not a scheme-level score."""
    summary = _summary(load_records())
    return {
        "scope": "article_mentions_by_source",
        "average_impact_score": summary["average_impact_score"],
        "scored_record_count": summary["scored_record_count"],
        "groups": summary["source_impact"],
    }
