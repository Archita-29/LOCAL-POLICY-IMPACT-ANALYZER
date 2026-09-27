# Local Policy Impact Analyzer

Local Policy Impact Analyzer collects public reporting about Indian
government schemes and policies, organizes the material, and analyzes the
sentiment expressed in those reports. The project is intended to help people
explore public discussion and surface signals about policy implementation.

The current repository contains an RSS collection and cleaning pipeline,
NLP processing scripts and sample exports, plus a FastAPI read API for a
dashboard. It does **not** currently contain a web frontend.

> **Interpretation:** Online posts and news coverage are signals about public
> discussion, not a direct measurement of whether a scheme reached its
> beneficiaries or achieved its goals. Sentiment scores should not be treated
> as an official or unbiased audit. Platform access, language, geography,
> demographics, source quality, and coordinated activity can all affect what
> the collected data represents.

## What the project does

1. Collects articles from configured RSS feeds.
2. Cleans text, normalizes dates, estimates language, groups similar headlines,
   and flags likely policy relevance.
3. Exports records for NLP processing.
4. Stores sentiment labels and impact scores produced by NLP processing.
5. Serves the saved records and summaries through a REST API for a dashboard.

The intended next stage is to associate each article with a stable government
scheme identifier, then aggregate results by scheme. The current CSV exports
do not contain that association, so the API reports article-level results and
source-level aggregates instead of claiming scheme-level impact.

## Repository contents

| Path | Purpose |
|---|---|
| `scraper/rss/rss_pipeline.py` | Refactored RSS collector using SQLAlchemy |
| `scraper/rss/integration.py` | Refactored cleaner and record flagger |
| `scraper/rss/mention_bridge.py` | Optional integration with a separate backend's Scheme and Mention models |
| `scraper/rss/sentiment.py` | Current lexicon-based multilingual sentiment helper |
| `scraper/rss/api.py` | Optional endpoint to trigger the refactored RSS pipeline |
| `rss_pipeline.py` | Original standalone RSS collector using SQLite |
| `integration.py` | Original standalone cleaning and export script |
| `export_nlp_ready.py` | Builds an NLP-ready SQLite table and CSV from `cleaned_records` |
| `nlp_processor.py` | Loads the XLM-RoBERTa sentiment model and saves NLP outputs |
| `cleaned_policy_data.csv` | Cleaned article records with relevance and duplicate flags |
| `nlp_ready_data.csv` | Filtered records prepared for NLP |
| `nlp_policy_impact_results.csv` | Sample/persisted sentiment and impact results |
| `backend/app/` | FastAPI read API and future model-provider interface |
| `import_schemes.py` | Optional importer for an external `updated_data.csv` file |

## Requirements

- Python 3.10 or newer is recommended.
- Internet access is needed to fetch live RSS feeds and download the NLP model
  on its first run.
- The `requirements.txt` file includes the API, scraper, data-processing, and
  NLP packages. PyTorch and Transformers can require a large download.

## Setup

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Start the API

With the virtual environment active, from the repository root run:

```bash
uvicorn backend.app.main:app --reload
```

Then open:

- API documentation: <http://127.0.0.1:8000/docs>
- Health status: <http://127.0.0.1:8000/health>
- Dashboard summary: <http://127.0.0.1:8000/api/v1/dashboard/summary>

The API reads available records from SQLite and supplements them with the
repository's CSV exports. It does not trigger scraping or run model inference
when a dashboard request arrives. If no database exists, the checked-in CSV
files can still provide data.

By default, the API looks for `policy_impact.db`. The original root-level
scripts write to `policy_data.db`; to make the API read that database, set
this before starting Uvicorn:

```bash
export POLICY_ANALYZER_DB="$PWD/policy_data.db"
uvicorn backend.app.main:app --reload
```

Alternatively, set `DATABASE_URL` to a `sqlite:///...` URL. The API currently
supports SQLite data sources.

### API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API and data-source status |
| `GET` | `/api/v1/dashboard/summary` | Record counts, sentiment counts, and average scores |
| `GET` | `/api/v1/records` | Search and filter article records with pagination |
| `GET` | `/api/v1/records/{record_id}` | Fetch one record by its ID |
| `GET` | `/api/v1/impact` | Persisted article-score aggregates by source |

`/api/v1/records` accepts `q`, `source`, `language`, `sentiment`,
`policy_relevant`, `scored_only`, `limit`, and `offset` query parameters. For
example:

```bash
curl "http://127.0.0.1:8000/api/v1/records?language=hindi&scored_only=true&limit=20"
```

For local dashboard development, CORS allows requests from any origin by
default. Set `CORS_ORIGINS` to a comma-separated list of allowed dashboard
origins when deploying.

## Data pipeline

### Scrape and clean

The refactored pipeline can be run from the repository root:

```bash
python -m scraper.rss.rss_pipeline
python -m scraper.rss.integration
```

It collects into `raw_records`, then creates or updates `cleaned_records`.
Near duplicates and likely off-topic records are retained with flags; they are
not discarded by the cleaner. The refactored modules use SQLAlchemy and
`scraper/rss/config.py` to select a database. Set `DATABASE_URL` to a
SQLAlchemy database URL to choose the database explicitly; otherwise the
default SQLite file is `policy_impact.db` in the current working directory.

To build NLP-ready records from the refactored database, use the Python
function `build_nlp_ready_table()` in `export_nlp_ready.py` after configuring
that script for the same database. The root-level export script currently
uses `policy_data.db` directly, so its database path must be aligned before
mixing it with the refactored pipeline.

### Original standalone scripts

The original scripts use a separate SQLite database named `policy_data.db` in
the current working directory:

```bash
python rss_pipeline.py
python integration.py
python export_nlp_ready.py
python nlp_processor.py
```

`nlp_processor.py` downloads/loads
`cardiffnlp/twitter-xlm-roberta-base-sentiment` and writes
`nlp_processed_records` to `policy_data.db`, as well as
`nlp_policy_impact_results.csv`. Its input table must already exist; run the
scrape, clean, and export steps first. The model can take time and disk space
to download.

> The refactored `scraper/rss/run_rss_pipeline.py` also calls
> `mention_bridge.py`, which imports `Scheme`, `Mention`, and `ImpactScore`
> models from a separate `backend` project expected next to this repository.
> That external project is not included here, so the full scrape-clean-bridge
> command is not standalone until those dependencies are provided. The FastAPI
> read API documented above does not depend on that bridge.

## Data fields and score meaning

Cleaned records include fields such as `id`, `source`, `title_clean`,
`summary_clean`, `link`, `published_datetime`, `language`, `story_group_id`,
`is_near_duplicate`, and `is_policy_relevant`.

NLP output includes `id`, `source`, `language`, `story_group_id`,
`sentiment_label`, `sentiment_score`, and `impact_score`. In the current NLP
processor, `impact_score` maps model sentiment confidence onto a 0–100 scale
centered around 50. It is a derived article sentiment measure; it is not a
validated measure of program effectiveness or beneficiary outcomes.

The model-provider interface is in `backend/app/model_provider.py`. The API
currently serves saved NLP outputs and does not call this interface. When a
trained model is ready, connect it through this seam and persist its output
under the existing record IDs. Missing model results should remain unscored.

## Current limitations and next steps

- **No frontend is included.** Build a dashboard separately and connect it to
  the API endpoints above.
- **No stable scheme-to-article mapping is present in the supplied exports.**
  Add a scheme ID and matching evidence to the pipeline before presenting
  scheme-level aggregates.
- **Online coverage is not representative of all citizens.** RSS feeds do not
  cover every social network or community, and the current collector does not
  provide a complete cross-platform view of public opinion.
- **The root and refactored pipelines use different database conventions.**
  Align the database URL/path when moving records between them.
- **The older scheme importer expects `updated_data.csv`.** That input file is
  not included in this repository.
- **The separate backend models needed by `mention_bridge.py` are absent.**
  The bridge needs that project before it can run end-to-end.

Useful follow-up work is to define a canonical scheme catalog and record
matching schema, persist source and matching evidence, evaluate sentiment
quality across languages, and build a frontend that clearly communicates
coverage and uncertainty.

## License

See [LICENSE](LICENSE).
