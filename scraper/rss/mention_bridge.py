"""
mention_bridge.py
-----------------
Bridge module: reads cleaned RSS records and inserts matching ones
as Mention rows in the main backend's mentions table.

This connects Antra's RSS pipeline output to the main project's
impact scoring system. Without this bridge, scraped news would
sit in cleaned_records but never appear in the dashboard.

HOW MATCHING WORKS:
  For each cleaned record, we check if any Scheme.name appears as a
  case-insensitive substring in the record's title or summary.
  If yes, we create a Mention linked to that scheme.
  If no scheme matches, the record is skipped (logged but not lost).

DEDUPLICATION:
  We skip insertion if a Mention with the same URL already exists
  for that scheme (same logic as the Scrapy pipeline's SQLAlchemyPipeline).

Usage:
    from scraper.rss.mention_bridge import bridge_to_mentions
    stats = bridge_to_mentions()
    print(stats)  # {"inserted": 12, "skipped_no_match": 45, "skipped_duplicate": 3}
"""

import os
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the main project's backend to sys.path so we can import its models.
# This is the same pattern used by scraper/run_etl.py in the main project.
_this_dir = os.path.dirname(os.path.abspath(__file__))
_backend_path = os.path.abspath(os.path.join(_this_dir, "..", "..", "..", "backend"))
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

from scraper.rss.models import Base as RSSBase, CleanedRecord

# These imports come from the MAIN PROJECT's backend
from app.core.database import Base as BackendBase
from app.models.models import Scheme, Mention

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///policy_impact.db")


def bridge_to_mentions(db_url: str | None = None) -> dict:
    """
    Read cleaned_records and insert matching rows as Mention records.

    Args:
        db_url: Optional database URL. Defaults to DATABASE_URL.

    Returns:
        Dict with counts: {"inserted": N, "skipped_no_match": N, "skipped_duplicate": N}
    """
    url = db_url or DATABASE_URL
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)

    # Ensure all tables exist
    RSSBase.metadata.create_all(engine)
    BackendBase.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    stats = {"inserted": 0, "skipped_no_match": 0, "skipped_duplicate": 0}

    try:
        # 1. Load all schemes (for name matching)
        schemes = session.query(Scheme).all()
        if not schemes:
            print("WARNING: No schemes found in database. Run backend seed.py first.")
            print("Cannot bridge RSS data to mentions without schemes to match against.")
            return stats

        print(f"Loaded {len(schemes)} schemes for matching.")

        # 2. Load the clean subset of RSS records
        cleaned_rows = (
            session.query(CleanedRecord)
            .filter(CleanedRecord.is_policy_relevant == 1)
            .filter(CleanedRecord.is_near_duplicate == 0)
            .all()
        )
        print(f"Found {len(cleaned_rows)} cleaned records (relevant, non-duplicate).")

        # 3. For each cleaned record, try to match to a scheme
        for row in cleaned_rows:
            search_text = f"{row.title_clean or ''} {row.summary_clean or ''}".lower()

            matched_scheme = None
            for scheme in schemes:
                # Case-insensitive substring match on scheme name
                if scheme.name.lower() in search_text:
                    matched_scheme = scheme
                    break

            if not matched_scheme:
                stats["skipped_no_match"] += 1
                continue

            # 4. Check for duplicate by URL
            if row.link:
                existing = (
                    session.query(Mention)
                    .filter(Mention.scheme_id == matched_scheme.id)
                    .filter(Mention.url == row.link)
                    .first()
                )
                if existing:
                    stats["skipped_duplicate"] += 1
                    continue

            # 5. Map RSS language codes to Mention language codes
            lang_map = {"hindi": "hi", "english": "en", "hinglish": "hi-en"}
            mention_lang = lang_map.get(row.language, "hi")

            # 6. Create the Mention
            mention = Mention(
                scheme_id=matched_scheme.id,
                source=f"RSS: {row.source}" if row.source else "RSS",
                raw_text=row.title_clean or "",
                language=mention_lang,
                published_date=datetime.fromisoformat(row.published_datetime)
                if row.published_datetime
                else datetime.utcnow(),
                url=row.link,
                # sentiment_score and sentiment_label are left NULL —
                # the ML sentiment pipeline (Phase 3) will fill these later
            )
            session.add(mention)
            stats["inserted"] += 1

        session.commit()
        print(f"\nBridge complete: {stats}")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return stats


if __name__ == "__main__":
    bridge_to_mentions()
