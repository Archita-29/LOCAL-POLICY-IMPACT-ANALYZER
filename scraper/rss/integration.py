"""
integration.py (refactored)
-----------------------------
Data Integration step for the Local Policy Impact Analyzer project.

INPUT:  raw_records table (produced by rss_pipeline.py)
OUTPUT: cleaned_records table (added/updated via upsert; raw_records is NEVER modified)
        cleaned_policy_data.csv (optional CSV export)

PIPELINE: raw -> clean -> normalize -> deduplicate/flag -> cleaned database

Key design decisions (preserved from Antra's original):
  - Near-duplicate records are KEPT and flagged, never deleted
  - Off-topic records are KEPT and flagged, never deleted
  - Re-running updates via upsert, never drops the table

Original standalone version by Antra (integration.py in repo root).
This refactored version uses SQLAlchemy instead of raw sqlite3.

Usage:
    from scraper.rss.integration import run_integration
    run_integration()
"""

import csv
import html
import os
import re
from datetime import datetime
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scraper.rss.models import Base, RawRecord, CleanedRecord

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///policy_impact.db")
CSV_PATH = "cleaned_policy_data.csv"

# Explicit column order for CSV export
CLEANED_FIELDS = [
    "id", "source", "title_clean", "summary_clean", "link",
    "published_datetime", "language", "language_confidence", "scraped_at",
    "story_group_id", "is_near_duplicate", "is_policy_relevant",
]


# ---------------------------------------------------------------------------
# Text cleaning (unchanged from original)
# ---------------------------------------------------------------------------
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def deep_clean(text):
    """
    Cleans a title/summary string:
      - Handles None/empty input safely (returns "")
      - Strips HTML tags
      - Decodes HTML entities via html.unescape (Unicode-safe)
      - Collapses all whitespace/newlines to single spaces
      - Preserves all Unicode text (Hindi/Devanagari) untouched
    """
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Date/time handling (unchanged from original)
# ---------------------------------------------------------------------------
def parse_datetime(raw_date):
    """
    Parses an RSS-style date string into ISO 8601 datetime string.
    Returns None if unparseable — never raises.
    """
    if not raw_date:
        return None
    try:
        dt = parsedate_to_datetime(raw_date)
        return dt.isoformat()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Language refinement (unchanged from original)
# ---------------------------------------------------------------------------
def refine_language(title, summary, original_lang):
    """
    Returns (language, confidence).
      language:   "hindi" | "hinglish" | "english"
      confidence: "high" | "medium" | "low"
    """
    text = f"{title} {summary}".strip()
    letters_only = text.replace(" ", "")
    total_chars = len(letters_only)

    if total_chars == 0:
        return original_lang or "english", "low"

    devanagari_chars = sum(1 for ch in text if "\u0900" <= ch <= "\u097F")
    ratio = devanagari_chars / total_chars

    if ratio > 0.3:
        return "hindi", "high"
    if ratio > 0.05:
        return "hinglish", "medium"
    if original_lang == "hinglish":
        return "hinglish", "medium"
    if total_chars < 8:
        return "english", "low"
    return "english", "high"


# ---------------------------------------------------------------------------
# Near-duplicate detection (unchanged from original)
# ---------------------------------------------------------------------------
def is_near_duplicate_title(title_a, title_b, threshold=0.85):
    return SequenceMatcher(None, title_a.lower(), title_b.lower()).ratio() >= threshold


def assign_story_groups(records):
    """
    Groups records that appear to be the same story (near-identical titles),
    WITHOUT removing any record. Returns parallel lists of group IDs and flags.
    """
    representatives = []
    story_group_ids = []
    is_near_duplicate_flags = []
    next_group_num = 1

    for rec in records:
        title = rec["title_clean"]
        matched_group_id = None
        for rep_title, gid in representatives:
            if is_near_duplicate_title(title, rep_title):
                matched_group_id = gid
                break

        if matched_group_id is not None:
            story_group_ids.append(matched_group_id)
            is_near_duplicate_flags.append(1)
        else:
            gid = f"group_{next_group_num:04d}"
            next_group_num += 1
            representatives.append((title, gid))
            story_group_ids.append(gid)
            is_near_duplicate_flags.append(0)

    return story_group_ids, is_near_duplicate_flags


# ---------------------------------------------------------------------------
# Relevance flagging (unchanged from original)
# ---------------------------------------------------------------------------
POLICY_KEYWORDS_EN = [
    "scheme", "yojana", "policy", "government", "govt", "ministry", "cabinet",
    "subsidy", "welfare", "pension", "ration", "aadhaar", "pib", "parliament",
    "budget", "tax", "reform", "act", "bill", "notification", "circular",
    "regulation", "grant", "fund", "compensation", "eligibility", "beneficiary",
    "collectorate", "district magistrate", "panchayat", "municipal",
    "farmer", "kisan", "crop", "msp", "agriculture", "irrigation",
    "health scheme", "hospital scheme", "ayushman", "insurance scheme",
    "vaccination", "healthcare policy",
    "scholarship", "education policy", "school scheme", "skill development",
    "employment scheme", "mgnrega", "labour", "epfo", "esic", "wage",
    "awas yojana", "housing scheme", "highway project", "infrastructure project",
    "smart city",
    "election commission", "voter list", "special intensive revision", "evm",
    "sir revision",
]
POLICY_KEYWORDS_HI = [
    "योजना", "सरकार", "मंत्रालय", "कैबिनेट", "सब्सिडी", "बजट", "कर",
    "अधिनियम", "विधेयक", "अधिसूचना", "पेंशन", "राशन", "आधार", "संसद",
    "कलेक्ट्रेट", "जिलाधिकारी", "पंचायत", "नगर निगम",
    "किसान", "फसल", "कृषि", "सिंचाई",
    "स्वास्थ्य", "अस्पताल", "आयुष्मान", "बीमा", "टीकाकरण",
    "छात्रवृत्ति", "शिक्षा नीति", "कौशल विकास",
    "रोजगार", "मनरेगा", "मजदूरी",
    "आवास योजना", "राजमार्ग", "स्मार्ट सिटी",
    "मतदाता", "चुनाव आयोग", "एसआईआर",
    "आयुष", "सड़क", "सड़कें", "नदी", "नदियों", "गंगा", "जल शक्ति", "पर्यावरण",
]


def is_policy_relevant(source, title, summary):
    """
    Returns True/False. Only BBC Hindi is filtered (it's a general news feed).
    Google News/PIB feeds are topic-targeted and trusted as relevant.
    """
    if source != "BBC Hindi":
        return True
    text = f"{title} {summary}"
    text_lower = text.lower()
    if any(kw in text_lower for kw in POLICY_KEYWORDS_EN):
        return True
    if any(kw in text for kw in POLICY_KEYWORDS_HI):
        return True
    return False


# ---------------------------------------------------------------------------
# CSV export (unchanged from original)
# ---------------------------------------------------------------------------
def export_csv(records, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CLEANED_FIELDS)
        writer.writeheader()
        for rec in records:
            writer.writerow({field: rec.get(field) for field in CLEANED_FIELDS})


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run_integration(db_url: str | None = None, csv_path: str | None = None):
    """
    Run the full integration pipeline:
      1. Load raw records from raw_records table
      2. Clean text, normalize dates, refine language
      3. Assign story groups and near-duplicate flags
      4. Flag policy relevance
      5. Upsert into cleaned_records table
      6. Export CSV

    Args:
        db_url: Optional SQLAlchemy database URL. Defaults to DATABASE_URL.
        csv_path: Optional CSV export path. Defaults to CSV_PATH.
    """
    url = db_url or DATABASE_URL
    out_csv = csv_path or CSV_PATH

    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Load raw records
        raw_rows = session.query(RawRecord).all()
        print(f"Loaded {len(raw_rows)} raw records from raw_records table.")

        # 2. Clean and normalize
        processed = []
        failed_dates = 0
        for row in raw_rows:
            title_clean = deep_clean(row.title)
            summary_clean = deep_clean(row.summary)
            published_dt = parse_datetime(row.published)
            if published_dt is None:
                failed_dates += 1
            lang, confidence = refine_language(title_clean, summary_clean, row.language)

            processed.append({
                "id": row.id,
                "source": row.source,
                "title_clean": title_clean,
                "summary_clean": summary_clean,
                "link": row.link,
                "published_datetime": published_dt,
                "language": lang,
                "language_confidence": confidence,
                "scraped_at": row.scraped_at,
            })

        # 3. Sort for deterministic grouping
        processed.sort(key=lambda r: r["scraped_at"] or "")

        # 4. Story groups and near-duplicate flags
        story_group_ids, dup_flags = assign_story_groups(processed)
        near_dup_count = sum(dup_flags)
        for rec, gid, flag in zip(processed, story_group_ids, dup_flags):
            rec["story_group_id"] = gid
            rec["is_near_duplicate"] = flag

        # 5. Policy relevance flags
        for rec in processed:
            rec["is_policy_relevant"] = int(
                is_policy_relevant(rec["source"], rec["title_clean"], rec["summary_clean"])
            )
        off_topic_count = sum(1 for r in processed if r["is_policy_relevant"] == 0)

        print(f"{failed_dates} records had unparseable dates (published_datetime = NULL).")
        print(f"{near_dup_count} records flagged as near-duplicates (kept, not deleted).")
        print(f"{off_topic_count} records flagged as likely off-topic (kept, not deleted).")

        # 6. Upsert into cleaned_records via SQLAlchemy merge
        for rec in processed:
            cleaned = CleanedRecord(**rec)
            session.merge(cleaned)  # INSERT or UPDATE by primary key
        session.commit()

        # 7. Export CSV
        export_csv(processed, out_csv)

        print(f"\nDone. cleaned_records has {len(processed)} rows (all raw records preserved).")
        print(f"Exported: {out_csv}")
        print("Use is_near_duplicate=0 AND is_policy_relevant=1 for the 'clean subset'.")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_integration()
