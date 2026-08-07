print("SCRIPT STARTED")
from bs4 import BeautifulSoup
import feedparser
import sqlite3
import hashlib
from datetime import datetime, timezone
RSS_FEEDS = {
    "BBC Hindi": "https://feeds.bbci.co.uk/hindi/rss.xml",
    "Google News - Govt Scheme (Hindi)": "https://news.google.com/rss/search?q=sarkari+yojana&hl=hi&gl=IN&ceid=IN:hi",
    "Google News - Govt Scheme (English)": "https://news.google.com/rss/search?q=government+scheme+india&hl=en-IN&gl=IN&ceid=IN:en",
}
 
DB_PATH = "policy_data.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_records (
            id TEXT PRIMARY KEY,      -- hash of title+link, used for dedup
            source TEXT,
            title TEXT,
            summary TEXT,
            link TEXT,
            published TEXT,
            language TEXT,
            scraped_at TEXT
        )
    """)
    conn.commit()
    return conn
def make_id(title, link):
    """Create a stable unique ID from title+link so we can detect exact duplicates."""
    return hashlib.md5((title + link).encode("utf-8")).hexdigest()
 
def detect_language(text):
    """
    Very simple heuristic language tagger:
    - If text has a good number of Devanagari characters -> Hindi
    - Else if it has common Hinglish (Roman-script Hindi) words -> Hinglish
    - Else -> English
 
    This is intentionally simple for a first pass. Later you can swap this
    for a proper library (e.g. langdetect for Hindi/English, and a custom
    wordlist/classifier for Hinglish specifically).
    """
    devanagari_count = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    if devanagari_count > 5:
        return "hindi"
 
    hinglish_words = {
        "hai", "nahi", "kya", "aur", "hum", "aap", "kaise", "kar",
        "raha", "rahi", "sarkar", "yojana", "gaon", "shahar", "bhai"
    }
    words = set(text.lower().split())
    if words & hinglish_words:
        return "hinglish"
 
    return "english"
def clean_text(text):
    """Cleaning: strip HTML tags first, then whitespace, collapse newlines."""
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    return " ".join(text.split())
 
 
# ---------------------------------------------------------------------------
# STEP 4: Fetch, clean, tag, and store
# ---------------------------------------------------------------------------
def fetch_and_store(conn):
    cur = conn.cursor()
    new_count = 0
    skipped_duplicates = 0
 
    for source_name, url in RSS_FEEDS.items():
        print(f"Fetching: {source_name} ...")
        feed = feedparser.parse(url)
 
        if feed.bozo:  # feedparser sets this flag if something went wrong parsing
            print(f"  Warning: could not cleanly parse {source_name} ({feed.bozo_exception})")
 
        for entry in feed.entries:
            title = clean_text(entry.get("title", ""))
            summary = clean_text(entry.get("summary", ""))
            link = entry.get("link", "")
            published = entry.get("published", "")
 
            if not title:  # skip junk entries with no title
                continue
 
            record_id = make_id(title, link)
            lang = detect_language(title + " " + summary)
 
            try:
                cur.execute("""
                    INSERT INTO raw_records
                    (id, source, title, summary, link, published, language, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (record_id, source_name, title, summary, link, published,
                      lang, datetime.now(timezone.utc).isoformat()))
                new_count += 1
            except sqlite3.IntegrityError:
                # This ID already exists -> exact duplicate, skip it
                skipped_duplicates += 1
 
    conn.commit()
    return new_count, skipped_duplicates
 
 
# ---------------------------------------------------------------------------
# STEP 5: Run it
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    conn = init_db()
    new_count, skipped = fetch_and_store(conn)
    print(f"\nDone. Inserted {new_count} new records. Skipped {skipped} duplicates.")
 
    cur = conn.cursor()
    cur.execute("SELECT source, language, COUNT(*) FROM raw_records GROUP BY source, language")
    print("\nBreakdown by source and language:")
    for row in cur.fetchall():
        print(f"  {row[0]:35s} | {row[1]:10s} | {row[2]} records")
 
    conn.close()
 
