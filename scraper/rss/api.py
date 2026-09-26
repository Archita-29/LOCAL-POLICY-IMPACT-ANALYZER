"""
api.py
------
FastAPI router for triggering the RSS pipeline via HTTP.

To use: import this router in the main backend's app/main.py and include it.
Example:
    from scraper.rss.api import rss_router
    app.include_router(rss_router, prefix="/api/scraper")
"""

from fastapi import APIRouter

rss_router = APIRouter(tags=["RSS Scraper"])


@rss_router.post("/rss/run")
def trigger_rss_pipeline():
    """
    Trigger the full RSS pipeline: scrape → clean → bridge to mentions.
    Returns a summary of what was processed.
    """
    from scraper.rss.rss_pipeline import run_rss_scrape
    from scraper.rss.integration import run_integration
    from scraper.rss.mention_bridge import bridge_to_mentions

    # Step 1: Scrape
    new_count, skipped = run_rss_scrape()

    # Step 2: Clean
    run_integration()

    # Step 3: Bridge
    bridge_stats = bridge_to_mentions()

    return {
        "status": "success",
        "scrape": {
            "new_records": new_count,
            "duplicates_skipped": skipped,
        },
        "bridge": bridge_stats,
        "message": "RSS pipeline completed. New mentions may now appear in the dashboard.",
    }
