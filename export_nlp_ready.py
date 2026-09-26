"""
export_nlp_ready.py
--------------------
Creates the NLP-ready clean table/CSV that the model/NLP teammate needs.

WHY THIS EXISTS:
integration.py (the main pipeline) keeps ALL 447 raw records in
cleaned_records, with flags (is_near_duplicate, is_policy_relevant) instead
of deleting anything -- this was required by Archita's review so no
source-level evidence is lost.

But that means cleaned_records is NOT directly usable by NLP work as-is --
someone doing NLP shouldn't have to know about flags or filter logic
themselves. This script creates the actual FILTERED, NLP-ready table:
only genuinely relevant, de-duplicated records, with just the text fields
NLP needs.

This does NOT replace cleaned_records or touch raw_records -- it just adds
one more clean table/CSV built FROM cleaned_records, specifically for NLP
consumption.

HOW TO RUN (after running integration.py first):
    python export_nlp_ready.py
"""

import csv
import sqlite3

DB_PATH = "policy_data.db"
CSV_PATH = "nlp_ready_data.csv"

NLP_FIELDS = [
    "id",
    "source",
    "title_clean",
    "summary_clean",
    "link",
    "published_datetime",
    "language",
    "story_group_id",
]


def build_nlp_ready_table():
    conn = sqlite3.connect(DB_PATH)
    try:
        # Create the NLP-ready table: only relevant, non-duplicate records.
        # is_near_duplicate = 0 -> keep just the first/representative record
        #                         of each story group (avoids feeding the
        #                         same story to the model multiple times)
        # is_policy_relevant = 1 -> exclude flagged off-topic/general news
        conn.execute("DROP TABLE IF EXISTS nlp_ready_records")
        conn.execute(f"""
            CREATE TABLE nlp_ready_records AS
            SELECT {", ".join(NLP_FIELDS)}
            FROM cleaned_records
            WHERE is_near_duplicate = 0
              AND is_policy_relevant = 1
        """)
        conn.commit()

        cur = conn.execute("SELECT COUNT(*) FROM nlp_ready_records")
        count = cur.fetchone()[0]
        print(f"Created nlp_ready_records table with {count} clean records.")

        # Export as CSV too, for easy handoff / use outside the DB.
        cur = conn.execute(f"SELECT {', '.join(NLP_FIELDS)} FROM nlp_ready_records")
        rows = cur.fetchall()
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(NLP_FIELDS)
            writer.writerows(rows)
        print(f"Exported: {CSV_PATH}")

    finally:
        conn.close()


if __name__ == "__main__":
    build_nlp_ready_table()
