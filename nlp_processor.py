import sqlite3
import pandas as pd
from transformers import pipeline

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

def init_sentiment_model():
    """Initializes multilingual sentiment pipeline."""
    # Multilingual model suitable for English + Hindi + Hinglish
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment")

def analyze_sentiment(df):
    model = init_sentiment_model()
    results = []
    
    for _, row in df.iterrows():
        text = f"{row['title_clean']} {row['summary_clean']}"[:512]
        if not text.strip():
            continue
        
        res = model(text)[0]
        results.append({
            "id": row["id"],
            "sentiment_label": res["label"],
            "sentiment_score": round(res["score"], 4)
        })
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = load_cleaned_data()
    print(f"Loaded {len(df)} records for NLP processing.")