"""
integration.py
---------------
Data Integration step for the Local Policy Impact Analyzer project.

INPUT:  policy_data.db  (produced by Antra's rss_pipeline.py, table: raw_records)
OUTPUT: policy_data.db  (adds a new table: cleaned_records)
        cleaned_policy_data.csv (same data, exported as CSV for easy sharing/model use)

WHAT THIS DOES (your "Data Integration" role):
  1. Reads Antra's raw_records table.
  2. Parses the messy 'published' date strings into a real, sortable date format.
  3. Re-checks / improves the language tag (hindi / hinglish / english) using a
     slightly stronger rule than Antra's simple wordlist, and flags low-confidence
     tags so you can mention this in your presentation as a known limitation.
  4. Does near-duplicate detection on titles (catches near-identical articles from
     different feeds that Antra's exact-hash dedup would miss).
  5. Produces a final clean, merged table (cleaned_records) + CSV export that the
     model/backend teammate can use directly.

HOW TO RUN:
  1. Put this file in the SAME folder as policy_data.db
     (policy_data.db is created after you run Antra's rss_pipeline.py once)
  2. In terminal:  python integration.py
  3. It will print a summary. Two output files are created in the same folder:
       - policy_data.db        (now also has 'cleaned_records' table)
       - cleaned_policy_data.csv
"""

import sqlite3
import csv
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from difflib import SequenceMatcher

DB_PATH = "policy_data.db"
CSV_PATH = "cleaned_policy_data.csv"


# ---------------------------------------------------------------------------
# STEP 1: Load raw data
# ---------------------------------------------------------------------------
def load_raw_records(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, source, title, summary, link, published, language, scraped_at FROM raw_records")
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    return rows


# ---------------------------------------------------------------------------
# STEP 2: Fix dates
# ---------------------------------------------------------------------------
def parse_date(raw_date):
    """
    RSS feeds usually give dates like: 'Sun, 13 Sep 2026 10:30:00 GMT'
    This converts that into a clean ISO date: '2026-09-13'
    If parsing fails, returns None (so you can see how many failed).
    """
    if not raw_date:
        return None
    try:
        dt = parsedate_to_datetime(raw_date)
        return dt.date().isoformat()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# STEP 3: Improve language tagging
# ---------------------------------------------------------------------------
def refine_language(title, summary, original_lang):
    """
    Slightly stronger check than the original heuristic:
    - Counts Devanagari density as a ratio, not a raw count (fairer on short titles)
    - Keeps Antra's original tag as fallback, but flags confidence
    Returns (language, confidence)
    """
    text = f"{title} {summary}"
    total_chars = max(len(text.replace(" ", "")), 1)
    devanagari_chars = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    ratio = devanagari_chars / total_chars

    if ratio > 0.3:
        return "hindi", "high"
    elif ratio > 0.05:
        return "hinglish", "medium"
    elif original_lang == "hinglish":
        return "hinglish", "medium"
    else:
        return "english", "high"


# ---------------------------------------------------------------------------
# STEP 4: Clean text further (remove leftover HTML/junk)
# ---------------------------------------------------------------------------
HTML_TAG_RE = re.compile(r"<[^>]+>")

def deep_clean(text):
    if not text:
        return ""
    text = HTML_TAG_RE.sub("", text)          # strip any leftover HTML tags
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = " ".join(text.split())             # collapse whitespace
    return text.strip()


# ---------------------------------------------------------------------------
# STEP 5: Near-duplicate detection (catches same story from 2 feeds)
# ---------------------------------------------------------------------------
def is_near_duplicate(title_a, title_b, threshold=0.85):
    return SequenceMatcher(None, title_a.lower(), title_b.lower()).ratio() >= threshold


def remove_near_duplicates(records):
    """
    Keeps the first occurrence of near-duplicate titles, drops the rest.
    Records should already be in a stable order (e.g. by scraped_at).
    """
    kept = []
    dropped_count = 0
    for rec in records:
        duplicate_found = False
        for kept_rec in kept:
            if is_near_duplicate(rec["title_clean"], kept_rec["title_clean"]):
                duplicate_found = True
                break
        if duplicate_found:
            dropped_count += 1
        else:
            kept.append(rec)
    return kept, dropped_count


# ---------------------------------------------------------------------------
# STEP 6: Build cleaned_records table
# ---------------------------------------------------------------------------
def init_cleaned_table(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cleaned_records")
    cur.execute("""
        CREATE TABLE cleaned_records (
            id TEXT PRIMARY KEY,
            source TEXT,
            title_clean TEXT,
            summary_clean TEXT,
            link TEXT,
            published_date TEXT,      -- clean ISO date, may be NULL if parsing failed
            language TEXT,
            language_confidence TEXT,
            scraped_at TEXT
        )
    """)
    conn.commit()


def run_integration():
    conn = sqlite3.connect(DB_PATH)
    raw = load_raw_records(conn)
    print(f"Loaded {len(raw)} raw records from raw_records table.")

    processed = []
    failed_dates = 0
    for rec in raw:
        title_clean = deep_clean(rec["title"])
        summary_clean = deep_clean(rec["summary"])
        pub_date = parse_date(rec["published"])
        if pub_date is None:
            failed_dates += 1
        lang, confidence = refine_language(title_clean, summary_clean, rec["language"])

        processed.append({
            "id": rec["id"],
            "source": rec["source"],
            "title_clean": title_clean,
            "summary_clean": summary_clean,
            "link": rec["link"],
            "published_date": pub_date,
            "language": lang,
            "language_confidence": confidence,
            "scraped_at": rec["scraped_at"],
        })

    # sort by scraped_at so "first occurrence" dedup keeps the earliest scraped copy
    processed.sort(key=lambda r: r["scraped_at"] or "")

    deduped, dropped = remove_near_duplicates(processed)
    print(f"Removed {dropped} near-duplicate records (same story, different feed/wording).")
    print(f"{failed_dates} records had a date that could not be parsed (published_date = NULL).")

    init_cleaned_table(conn)
    cur = conn.cursor()
    for rec in deduped:
        cur.execute("""
            INSERT INTO cleaned_records
            (id, source, title_clean, summary_clean, link, published_date,
             language, language_confidence, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rec["id"], rec["source"], rec["title_clean"], rec["summary_clean"],
              rec["link"], rec["published_date"], rec["language"],
              rec["language_confidence"], rec["scraped_at"]))
    conn.commit()

    # export CSV too, for easy sharing with model/backend teammate
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(deduped[0].keys()) if deduped else [])
        writer.writeheader()
        writer.writerows(deduped)

    print(f"\nDone. cleaned_records table has {len(deduped)} rows.")
    print(f"Exported: {CSV_PATH}")

    # quick breakdown, useful for your presentation slide
    cur.execute("SELECT language, language_confidence, COUNT(*) FROM cleaned_records GROUP BY language, language_confidence")
    print("\nBreakdown by language and confidence:")
    for row in cur.fetchall():
        print(f"  {row[0]:10s} | confidence: {row[1]:8s} | {row[2]} records")

    conn.close()


if __name__ == "__main__":
    run_integration()
