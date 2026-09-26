"""
scraper.rss
-----------
RSS-based government scheme news scraper, data cleaner, and mention bridge.
"""

from scraper.rss.models import RawRecord, CleanedRecord
from scraper.rss.rss_pipeline import run_rss_scrape
from scraper.rss.integration import run_integration
from scraper.rss.mention_bridge import bridge_to_mentions
from scraper.rss.sentiment import predict_sentiment
from scraper.rss.config import get_database_url

__all__ = [
    "RawRecord",
    "CleanedRecord",
    "run_rss_scrape",
    "run_integration",
    "bridge_to_mentions",
    "predict_sentiment",
    "get_database_url",
]
