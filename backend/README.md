# FastAPI backend

This API serves the cleaned article records and persisted NLP outputs already
produced by this repository. It does not run scraping or model inference from
dashboard requests.

## Run locally

From the repository root:

```bash
python -m pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

The API reads SQLite tables (`cleaned_records`, `nlp_ready_records`, and
`nlp_processed_records`) from `policy_impact.db` and supplements missing rows
from the corresponding CSV exports. Set `POLICY_ANALYZER_DB` to a SQLite file
path, or set `DATABASE_URL` to a `sqlite:///...` URL, to select another DB.
When the database has no data yet, the checked-in CSV files make the endpoints
usable immediately.

## Endpoints

- `GET /health`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/records` — supports `q`, `source`, `language`, `sentiment`,
  `policy_relevant`, `scored_only`, `limit`, and `offset`
- `GET /api/v1/records/{record_id}`
- `GET /api/v1/impact` — groups persisted article scores by source

Set `CORS_ORIGINS` to comma-separated dashboard origins in deployment. The
development default allows browser requests from any origin.

## Model integration seam

`backend/app/model_provider.py` defines the future `ModelProvider` contract.
The read API deliberately uses scores saved by the NLP pipeline; it returns
`null`/unscored status when a result is missing. Wire the trained model there
when available, and persist its outputs using the existing
`nlp_processed_records` columns (`id`, `sentiment_label`, `sentiment_score`,
`impact_score`).

## Current data boundary

The supplied artifacts identify news articles and their sentiment/impact
scores, but do not identify a government scheme per record or contain a scheme
catalog export. Therefore `/api/v1/impact` reports article-level aggregates by
source. A defensible scheme-level dashboard requires the scheme matching data
and a stable scheme identifier to be added to the pipeline output.
