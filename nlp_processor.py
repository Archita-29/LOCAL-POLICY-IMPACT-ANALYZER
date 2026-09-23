import sqlite3
import pandas as pd

DB_PATH = "policy_data.db"

def load_cleaned_data():
    """Loads clean policy records from SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, source, title_clean, summary_clean, language, story_group_id
        FROM cleaned_records
        WHERE is_policy_relevant = 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    df = load_cleaned_data()
    print(f"Loaded {len(df)} records for NLP processing.")