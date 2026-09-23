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

def compute_impact_score(label, score):
    """Calculates ground-level impact score (0 to 100)."""
    label_lower = label.lower()
    
    # Label_2 / Positive: High Impact
    if label_lower in ["positive", "label_2"]:
        return round(50 + (score * 50), 2)
    # Label_0 / Negative: Concerns / Low Impact Score
    elif label_lower in ["negative", "label_0"]:
        return round(50 - (score * 50), 2)
    # Neutral: Baseline
    else:
        return 50.00

def analyze_sentiment(df):
    model = init_sentiment_model()
    results = []

    # Map raw HuggingFace labels to clean text
    label_map = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive",
    }

    for _, row in df.iterrows():
        text = f"{row['title_clean']} {row['summary_clean']}".strip()
        if not text:
            continue

        res = model(text[:512])[0]
        raw_label = res["label"]
        confidence = res["score"]

        clean_label = label_map.get(raw_label, raw_label)
        impact_score = compute_impact_score(clean_label, confidence)

        results.append(
            {
                "id": row["id"],
                "sentiment_label": clean_label,
                "sentiment_score": round(confidence, 4),
                "impact_score": impact_score,
            }
        )
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = load_cleaned_data()
    print(f"Loaded {len(df)} records for NLP processing.")