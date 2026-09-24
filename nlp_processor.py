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
    # Truncation ensures texts over model max length do not crash inference
    return pipeline(
        "sentiment-analysis", 
        model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
        truncation=True,
        max_length=512
    )

def compute_impact_score(label, score):
    """Calculates ground-level impact score (0 to 100)."""
    label_lower = label.lower()
    
    if label_lower in ["positive", "label_2"]:
        return round(50 + (score * 50), 2)
    elif label_lower in ["negative", "label_0"]:
        return round(50 - (score * 50), 2)
    else:
        return 50.00

def analyze_sentiment(df, batch_size=32):
    """Runs batch sentiment analysis and maps scores."""
    if df.empty:
        print("Warning: Input DataFrame is empty.")
        return pd.DataFrame()

    model = init_sentiment_model()
    
    # Prepare combined text inputs
    texts = (
        (df["title_clean"].fillna("") + " " + df["summary_clean"].fillna(""))
        .str.strip()
        .str[:512]
        .tolist()
    )

    label_map = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive",
    }

    # Batch processing for significantly faster execution
    predictions = model(texts, batch_size=batch_size)

    results = []
    for record_id, res in zip(df["id"], predictions):
        raw_label = res["label"]
        confidence = res["score"]

        clean_label = label_map.get(raw_label, raw_label)
        impact_score = compute_impact_score(clean_label, confidence)

        results.append({
            "id": record_id,
            "sentiment_label": clean_label,
            "sentiment_score": round(confidence, 4),
            "impact_score": impact_score,
        })

    return pd.DataFrame(results)

def save_nlp_results(df):
    """Saves output to SQLite table and CSV export."""
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("nlp_processed_records", conn, if_exists="replace", index=False)
    conn.close()
    df.to_csv("nlp_policy_impact_results.csv", index=False)

def main():
    print("Step 1: Loading clean policy data...")
    df = load_cleaned_data()
    print(f"Loaded {len(df)} records for NLP processing.")
    
    if df.empty:
        print("No records found to process. Exiting.")
        return

    print("Step 2: Processing Sentiment & Impact Scores...")
    nlp_df = analyze_sentiment(df)
    
    print("Step 3: Saving output to SQLite & CSV...")
    save_nlp_results(nlp_df)
    print("Processing complete!")

if __name__ == "__main__":
    main()