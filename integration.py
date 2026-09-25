"""
integration.py
---------------
Data Integration step for the Local Policy Impact Analyzer project.

INPUT:  policy_data.db  (produced by Antra's rss_pipeline.py, table: raw_records)
OUTPUT: policy_data.db  (adds/updates table: cleaned_records -- raw_records is
        NEVER modified)
        cleaned_policy_data.csv (cleaned_records exported as CSV)

PIPELINE: raw -> clean -> normalize -> deduplicate/flag -> cleaned database

This version does NOT delete or drop any source-level evidence:
  - Near-duplicate records (same story from different feeds, e.g. PIB vs BBC)
    are kept and grouped with a story_group_id + is_near_duplicate flag,
    instead of being removed. Different sources may frame the same policy
    differently, which matters for later impact analysis.
  - Records that look off-topic (e.g. general BBC Hindi news that isn't
    actually about a government scheme/policy) are also kept, and flagged
    with is_policy_relevant = 0/1, instead of being dropped. Anyone doing
    analysis can filter using this flag if they only want the "clean subset",
    but the underlying record is never destroyed.
  - Re-running this script updates cleaned_records (upsert by id) instead of
    dropping and rebuilding the table from scratch.

HOW TO RUN:
  1. Put this file in the SAME folder as policy_data.db
  2. In terminal:  python integration.py
"""

import csv
import html
import re
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime

DB_PATH = "policy_data.db"
CSV_PATH = "cleaned_policy_data.csv"

# Explicit column order for cleaned_records -- used for CREATE TABLE, INSERT,
# and CSV export, so the CSV schema never silently depends on whatever the
# first record happens to look like.
CLEANED_FIELDS = [
    "id",
    "source",
    "title_clean",
    "summary_clean",
    "link",
    "published_datetime",   # full ISO datetime + timezone offset, or NULL
    "language",
    "language_confidence",
    "scraped_at",
    "story_group_id",       # shared id for records judged to be the same story
    "is_near_duplicate",    # 0 = first/representative record of its group, 1 = other
    "is_policy_relevant",   # 0/1 -- flag only, record is NEVER dropped for this
]


# ---------------------------------------------------------------------------
# Load raw data (raw_records is read-only from this script's point of view)
# ---------------------------------------------------------------------------
def load_raw_records(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, source, title, summary, link, published, language, scraped_at "
        "FROM raw_records"
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def deep_clean(text):
    """
    Cleans a title/summary string:
      - Handles None/empty input safely (returns "")
      - Strips HTML tags (e.g. leftover <p>, <a href=...> from feed summaries)
      - Decodes HTML entities (&amp;, &nbsp;, &#39;, Hindi entities, etc.)
        via html.unescape, which is far more complete than manual replace()
      - Collapses all whitespace/newlines to single spaces
      - Preserves all Unicode text (Hindi/Devanagari, English) untouched --
        this function never transliterates or drops non-ASCII characters
    """
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)

    text = HTML_TAG_RE.sub(" ", text)    # strip tags (space so words don't merge)
    text = html.unescape(text)           # decode &amp; &nbsp; &#2360; etc. (Unicode-safe)
    text = WHITESPACE_RE.sub(" ", text)  # collapse whitespace/newlines
    return text.strip()


# ---------------------------------------------------------------------------
# Date/time handling
# ---------------------------------------------------------------------------
def parse_datetime(raw_date):
    """
    Parses an RSS-style date string (e.g. 'Sun, 13 Sep 2026 10:30:00 GMT')
    into a full ISO 8601 datetime string, preserving time-of-day and
    timezone offset where the source provides one (e.g.
    '2026-09-13T10:30:00+00:00').

    Returns None (-> stored as SQL NULL) if the date is missing or cannot
    be parsed -- this must never raise or break the pipeline.
    """
    if not raw_date:
        return None
    try:
        dt = parsedate_to_datetime(raw_date)
        return dt.isoformat()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Language refinement
# ---------------------------------------------------------------------------
def refine_language(title, summary, original_lang):
    """
    Returns (language, confidence).
      language:   "hindi" | "hinglish" | "english"
      confidence: "high" | "medium" | "low"

    Method: Devanagari character density (ratio, not raw count, so short
    titles aren't unfairly penalized), with Antra's original tag used as a
    fallback signal, and a "low" confidence tier for text too short/ambiguous
    to classify with real confidence.
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
        # Very short text (e.g. a bare title with no summary) -- classify
        # as english by default, since Devanagari test found nothing, but
        # flag low confidence since there's too little signal to be sure.
        return "english", "low"
    return "english", "high"


# ---------------------------------------------------------------------------
# Near-duplicate detection -- FLAG, never delete
# ---------------------------------------------------------------------------
def is_near_duplicate_title(title_a, title_b, threshold=0.85):
    return SequenceMatcher(None, title_a.lower(), title_b.lower()).ratio() >= threshold


def assign_story_groups(records):
    """
    Groups records that appear to be the same story (near-identical titles),
    WITHOUT removing any record.

    Returns two parallel lists (same order/length as `records`):
      story_group_ids: e.g. "group_0001" -- shared by every record judged
                        to be the same story
      is_near_duplicate_flags: 0 for the first/representative record seen
                        in a group, 1 for every subsequent record in that
                        same group (they're still kept in the output).
    """
    representatives = []  # list of (title_clean, group_id)
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
# Relevance flagging -- FLAG, never delete
# ---------------------------------------------------------------------------
# Keywords (English + Hindi) indicating a record is about a government
# policy/scheme. Only used to FLAG records, never to remove them.
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
    "sir revision", "uniform civil code", "ucc",
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


GENERAL_NEWS_SOURCES = {"BBC Hindi", "India Today"}


def is_policy_relevant(source, title, summary):
    """
    Returns True/False -- used only to SET a flag column, never to drop a row.

    Only sources in GENERAL_NEWS_SOURCES are filtered: these are broad news
    feeds (BBC Hindi's full feed, India Today's homepage feed) that pull ALL
    news, not just policy news. The Google News/PIB sources are already
    topic-targeted by their own search query (e.g. "sarkari yojana",
    "site:pib.gov.in") and are trusted as relevant by default.

    NOTE: if a teammate adds another general/homepage-style feed later,
    add its exact source name to GENERAL_NEWS_SOURCES above so it gets
    filtered too -- otherwise its general news will incorrectly pass
    through as "relevant".

    Uses WORD-BOUNDARY matching for English keywords (via regex \\b), not
    plain substring checks -- otherwise short keywords like "act", "bill",
    "tax", "fund", "grant", "wage" would wrongly match inside unrelated
    words like "actor", "billion", "taxi", "fundamental", "grantor",
    "wagering". (Caught this with a test case: "Bollywood actor wins
    award" was wrongly flagged relevant because "act" matched inside
    "actor" under plain substring matching.)
    """
    if source not in GENERAL_NEWS_SOURCES:
        return True

    text = f"{title} {summary}"
    text_lower = text.lower()

    for kw in POLICY_KEYWORDS_EN:
        if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
            return True
    # Hindi keywords: word-boundary regex doesn't work reliably across
    # Devanagari (no \b support the same way), but Hindi policy terms here
    # are mostly multi-character words/compounds, so plain substring
    # matching is safe enough in practice.
    if any(kw in text for kw in POLICY_KEYWORDS_HI):
        return True
    return False


# ---------------------------------------------------------------------------
# cleaned_records table -- created once, never dropped; updated via upsert
# ---------------------------------------------------------------------------
def ensure_cleaned_table(conn):
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS cleaned_records (
            id TEXT PRIMARY KEY,
            source TEXT,
            title_clean TEXT,
            summary_clean TEXT,
            link TEXT,
            published_datetime TEXT,
            language TEXT,
            language_confidence TEXT,
            scraped_at TEXT,
            story_group_id TEXT,
            is_near_duplicate INTEGER,
            is_policy_relevant INTEGER
        )
    """)
    conn.commit()


def upsert_cleaned_records(conn, records):
    """
    Inserts new records / updates existing ones by id (parameterized SQL,
    no string formatting of values). raw_records is never touched here.
    """
    placeholders = ", ".join("?" for _ in CLEANED_FIELDS)
    update_clause = ", ".join(f"{f}=excluded.{f}" for f in CLEANED_FIELDS if f != "id")
    sql = f"""
        INSERT INTO cleaned_records ({", ".join(CLEANED_FIELDS)})
        VALUES ({placeholders})
        ON CONFLICT(id) DO UPDATE SET {update_clause}
    """
    conn.executemany(sql, [tuple(r[f] for f in CLEANED_FIELDS) for r in records])
    conn.commit()


# ---------------------------------------------------------------------------
# CSV export -- explicit schema, safe on zero rows, Unicode-safe
# ---------------------------------------------------------------------------
def export_csv(records, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CLEANED_FIELDS)
        writer.writeheader()          # header is written even with 0 records
        for rec in records:
            writer.writerow({field: rec.get(field) for field in CLEANED_FIELDS})


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run_integration():
    conn = sqlite3.connect(DB_PATH)
    try:
        raw = load_raw_records(conn)
        print(f"Loaded {len(raw)} raw records from raw_records table.")

        processed = []
        failed_dates = 0
        for rec in raw:
            title_clean = deep_clean(rec["title"])
            summary_clean = deep_clean(rec["summary"])
            published_dt = parse_datetime(rec["published"])
            if published_dt is None:
                failed_dates += 1
            lang, confidence = refine_language(title_clean, summary_clean, rec["language"])

            processed.append({
                "id": rec["id"],
                "source": rec["source"],
                "title_clean": title_clean,
                "summary_clean": summary_clean,
                "link": rec["link"],
                "published_datetime": published_dt,
                "language": lang,
                "language_confidence": confidence,
                "scraped_at": rec["scraped_at"],
            })

        # Stable order (by scraped_at) so grouping/flagging is deterministic
        # across runs.
        processed.sort(key=lambda r: r["scraped_at"] or "")

        story_group_ids, dup_flags = assign_story_groups(processed)
        near_dup_count = sum(dup_flags)
        for rec, gid, flag in zip(processed, story_group_ids, dup_flags):
            rec["story_group_id"] = gid
            rec["is_near_duplicate"] = flag

        for rec in processed:
            rec["is_policy_relevant"] = int(
                is_policy_relevant(rec["source"], rec["title_clean"], rec["summary_clean"])
            )
        off_topic_count = sum(1 for r in processed if r["is_policy_relevant"] == 0)

        print(f"{failed_dates} records had a date that could not be parsed (published_datetime = NULL).")
        print(f"{near_dup_count} records flagged as near-duplicates of another record (kept, not deleted).")
        print(f"{off_topic_count} records flagged as likely off-topic/general news (kept, not deleted).")

        ensure_cleaned_table(conn)
        upsert_cleaned_records(conn, processed)

        export_csv(processed, CSV_PATH)

        print(f"\nDone. cleaned_records table has {len(processed)} rows (all raw records preserved).")
        print(f"Exported: {CSV_PATH}")
        print("Use is_near_duplicate=0 AND is_policy_relevant=1 to filter to the "
              "'clean subset' for analysis, without losing the original records.")

        cur = conn.execute(
            "SELECT language, language_confidence, COUNT(*) "
            "FROM cleaned_records GROUP BY language, language_confidence"
        )
        print("\nBreakdown by language and confidence:")
        for row in cur.fetchall():
            print(f"  {row[0]:10s} | confidence: {row[1]:6s} | {row[2]} records")

    finally:
        # Always close the connection, even if something above raised.
        conn.close()


if __name__ == "__main__":
    run_integration()
