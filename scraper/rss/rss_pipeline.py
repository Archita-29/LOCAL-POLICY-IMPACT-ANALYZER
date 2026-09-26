"""
rss_pipeline.py (refactored)
-----------------------------
RSS feed scraper for the Local Policy Impact Analyzer project.

Scrapes government scheme and policy-related news from RSS feeds,
detects language, deduplicates entries, and stores them using SQLAlchemy
into the shared project database.

Original standalone version by Antra (rss_pipeline.py in repo root).
This refactored version uses SQLAlchemy instead of raw sqlite3.

Sources:
  - BBC Hindi (direct RSS)
  - Google News - Govt Scheme Hindi (search: sarkari yojana)
  - Google News - Govt Scheme English (search: government scheme india)
  - PIB via Google News (search: site:pib.gov.in)

Usage:
    # As a module:
    from scraper.rss.rss_pipeline import run_rss_scrape
    new_count, skipped = run_rss_scrape()

    # As a standalone script:
    python -m scraper.rss.rss_pipeline
"""

import hashlib
import os
from datetime import datetime, timezone

import feedparser
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scraper.rss.models import Base, RawRecord
from scraper.rss.config import get_database_url

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE_URL = get_database_url()

RSS_FEEDS = {
    "BBC Hindi": "https://feeds.bbci.co.uk/hindi/rss.xml",
    "Google News - Govt Scheme (Hindi)": (
        "https://news.google.com/rss/search?q=sarkari+yojana&hl=hi&gl=IN&ceid=IN:hi"
    ),
    "Google News - Govt Scheme (English)": (
        "https://news.google.com/rss/search?q=government+scheme+india&hl=en-IN&gl=IN&ceid=IN:en"
    ),
    "PIB via Google News": (
        "https://news.google.com/rss/search?q=site:pib.gov.in&hl=en-IN&gl=IN&ceid=IN:en"
    ),
}


# ---------------------------------------------------------------------------
# Helper functions (unchanged from Antra's original)
# ---------------------------------------------------------------------------
def make_id(title: str, link: str) -> str:
    """Create a stable unique ID from title+link for exact-duplicate detection."""
    return hashlib.md5((title + link).encode("utf-8")).hexdigest()


def detect_language(text: str) -> str:
    """
    Simple heuristic language tagger:
    - If text has >5 Devanagari characters -> Hindi
    - Else if it contains common Hinglish words -> Hinglish
    - Else -> English

    This is intentionally simple. A proper NLP classifier (e.g. langdetect,
    MuRIL) can replace this later.
    """
    devanagari_count = sum(1 for ch in text if "\u0900" <= ch <= "\u097F")
    if devanagari_count > 5:
        return "hindi"

    hinglish_words = {
        "hai", "nahi", "kya", "aur", "hum", "aap", "kaise", "kar",
        "raha", "rahi", "sarkar", "yojana", "gaon", "shahar", "bhai",
    }
    words = set(text.lower().split())
    if words & hinglish_words:
        return "hinglish"

    return "english"


def clean_text(text: str) -> str:
    """Strip HTML tags, collapse whitespace."""
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    return " ".join(text.split())


# ---------------------------------------------------------------------------
# Core scrape function
# ---------------------------------------------------------------------------
def run_rss_scrape(db_url: str | None = None) -> tuple[int, int]:
    """
    Fetch all RSS feeds, clean entries, and insert new records into the
    raw_records table via SQLAlchemy.

    Args:
        db_url: Optional SQLAlchemy database URL. Defaults to DATABASE_URL.

    Returns:
        Tuple of (new_records_inserted, duplicates_skipped).
    """
    url = db_url or DATABASE_URL
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)
    Base.metadata.create_all(engine)  # Ensures raw_records table exists
    Session = sessionmaker(bind=engine)
    session = Session()

    new_count = 0
    skipped_duplicates = 0

    try:
        for source_name, feed_url in RSS_FEEDS.items():
            print(f"Fetching: {source_name} ...")
            feed = feedparser.parse(feed_url)

            if feed.bozo and not feed.entries:
                print(f"  Warning: could not cleanly parse {source_name} ({feed.bozo_exception})")

            for entry in feed.entries:
                title = clean_text(entry.get("title", ""))
                summary = clean_text(entry.get("summary", ""))
                link = entry.get("link", "")
                published = entry.get("published", "")

                if not title:
                    continue

                record_id = make_id(title, link)

                # Check if this ID already exists (exact duplicate)
                existing = session.query(RawRecord).filter(RawRecord.id == record_id).first()
                if existing:
                    skipped_duplicates += 1
                    continue

                lang = detect_language(title + " " + summary)

                record = RawRecord(
                    id=record_id,
                    source=source_name,
                    title=title,
                    summary=summary,
                    link=link,
                    published=published,
                    language=lang,
                    scraped_at=datetime.now(timezone.utc).isoformat(),
                )
                session.add(record)
                new_count += 1

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(f"\nDone. Inserted {new_count} new records. Skipped {skipped_duplicates} duplicates.")
    return new_count, skipped_duplicates


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    new_count, skipped = run_rss_scrape()

    # Print breakdown
    url = DATABASE_URL
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        from sqlalchemy import func
        rows = (
            session.query(RawRecord.source, RawRecord.language, func.count())
            .group_by(RawRecord.source, RawRecord.language)
            .all()
        )
        print("\nBreakdown by source and language:")
        for source, lang, count in rows:
            print(f"  {source:35s} | {lang:10s} | {count} records")
    finally:
        session.close()
