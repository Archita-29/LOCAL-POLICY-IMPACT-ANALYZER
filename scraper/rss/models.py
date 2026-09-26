"""
SQLAlchemy models for the RSS scraper pipeline tables.

These models represent the raw_records and cleaned_records tables that were
originally created by Antra's rss_pipeline.py and integration.py using raw
sqlite3. By defining them as SQLAlchemy models, they can share the same
database engine and session as the main backend (policy_impact.db), instead
of living in a separate policy_data.db file.

Usage:
    from scraper.rss.models import RawRecord, CleanedRecord
"""

import datetime
from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.ext.declarative import declarative_base

# We define a standalone Base here rather than importing from the backend,
# because this code lives in the subfolder repo (Archita-29) which may not
# have the backend on its Python path. When integrated into the main project,
# the backend's create_all() or Alembic migration will pick up these tables.
Base = declarative_base()


class RawRecord(Base):
    """
    Mirrors the raw_records table from rss_pipeline.py.
    Stores unprocessed RSS feed entries exactly as scraped.
    """
    __tablename__ = "raw_records"

    id = Column(Text, primary_key=True)              # MD5 hash of title+link
    source = Column(Text, nullable=False)             # Feed name (e.g. "BBC Hindi")
    title = Column(Text, nullable=True)               # Article title
    summary = Column(Text, nullable=True)             # Article summary/snippet
    link = Column(Text, nullable=True)                # Original article URL
    published = Column(Text, nullable=True)           # Raw publish date string from feed
    language = Column(Text, nullable=True)            # "hindi", "hinglish", or "english"
    scraped_at = Column(Text, nullable=True)          # UTC ISO timestamp of scrape time


class CleanedRecord(Base):
    """
    Mirrors the cleaned_records table from integration.py.
    Stores processed/cleaned versions of raw_records with additional
    quality flags (near-duplicate detection, policy relevance).
    """
    __tablename__ = "cleaned_records"

    id = Column(Text, primary_key=True)               # Same ID as raw_records
    source = Column(Text, nullable=True)
    title_clean = Column(Text, nullable=True)          # HTML-stripped, whitespace-normalized title
    summary_clean = Column(Text, nullable=True)        # HTML-stripped, whitespace-normalized summary
    link = Column(Text, nullable=True)
    published_datetime = Column(Text, nullable=True)   # ISO 8601 datetime with timezone
    language = Column(Text, nullable=True)             # Refined language tag
    language_confidence = Column(Text, nullable=True)  # "high", "medium", or "low"
    scraped_at = Column(Text, nullable=True)
    story_group_id = Column(Text, nullable=True)       # Shared ID for near-duplicate stories
    is_near_duplicate = Column(Integer, nullable=True)  # 0 = representative, 1 = duplicate
    is_policy_relevant = Column(Integer, nullable=True) # 0 = off-topic, 1 = policy-related
