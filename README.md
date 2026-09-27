# LOCAL-POLICY-IMPACT-ANALYZER

## Overview

RSS-based data collection and integration pipeline for the Local Policy Impact Analyzer project.

This module scrapes government scheme news from RSS feeds, cleans and normalizes the data, and bridges it into the main project's `Mention` table for impact scoring.

## Architecture

```
scraper/rss/
├── __init__.py
├── models.py           # SQLAlchemy models for raw_records + cleaned_records
├── rss_pipeline.py     # RSS scraper (feedparser-based)
├── integration.py      # Data cleaning, dedup flagging, relevance flagging
├── mention_bridge.py   # Bridge: cleaned_records → backend Mention table
├── run_rss_pipeline.py # CLI runner for full pipeline
└── api.py              # FastAPI endpoint to trigger pipeline via HTTP
```

## Data Sources

`rss_pipeline.py` scrapes government scheme and policy-related news from RSS feeds, 
detects language, deduplicates entries, and stores them in a local SQLite database 
(`policy_data.db`).
### Sources
| Source | Method | Notes |
|---|---|---|
| BBC Hindi | Direct RSS | Stable, general news (filtered for relevance) |
| Google News - Govt Scheme (Hindi) | Google News RSS search | Query: `sarkari yojana` |
| Google News - Govt Scheme (English) | Google News RSS search | Query: `government scheme india` |
| PIB via Google News | Google News RSS search (`site:pib.gov.in`) | Workaround for broken PIB RSS |

## Pipeline Stages

1. **Scrape** (`rss_pipeline.py`): Fetch RSS feeds → `raw_records` table
2. **Clean** (`integration.py`): Text cleaning, date normalization, language refinement, near-duplicate grouping, policy relevance flagging → `cleaned_records` table
3. **Bridge** (`mention_bridge.py`): Match cleaned records to schemes by name → `mentions` table

## Running

### CLI (standalone)
```bash
pip install -r requirements.txt
python -m scraper.rss.run_rss_pipeline
```

### API (via FastAPI)
```bash
# From the repository root:
uvicorn backend.app.main:app --reload
```
The dashboard API reads the existing cleaned/NLP tables or CSV exports. See
[`backend/README.md`](backend/README.md) for the read endpoints, configuration,
and the model integration seam. The existing scraper trigger router can also
be mounted separately when live scraping is needed.

## Known Limitations

- **Language detection is heuristic-based**, not a proper NLP classifier
- **Deduplication is title-similarity-based** (SequenceMatcher ≥ 0.85 threshold)
- **Scheme matching is substring-based** — may miss schemes with very short/generic names
- **Sentiment scores are NOT filled** by this pipeline — the ML sentiment model (Phase 3) handles that

## Original Files

The original standalone scripts are preserved in the repo root:
- `rss_pipeline.py` — original by Antra
- `integration.py` — original, later improved in code review
- `query.py` — debug query script
