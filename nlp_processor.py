import sqlite3
import pandas as pd
from transformers import AutoTokenizer, pipeline

DB_PATH = "policy_data.db"
CSV_PATH = "nlp_policy_impact_results.csv"


def load_cleaned_data():
    """Loads clean policy records from the nlp_ready_records table."""
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='nlp_ready_records'"
    )
    if not cursor.fetchone():
        conn.close()
        raise RuntimeError(
            "Error: 'nlp_ready_records' table not found!\n"
            "Please run 'python export_nlp_ready.py' first before running NLP processing."
        )

    query = """
        SELECT id, source, title_clean, summary_clean, language, story_group_id
        FROM nlp_ready_records
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


from transformers import AutoTokenizer, pipeline


def init_sentiment_model():
    """Initializes multilingual sentiment pipeline with SentencePiece tokenizer."""
    model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

    # Load slow tokenizer directly using sentencepiece
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

    return pipeline(
        "sentiment-analysis",
        model=model_name,
        tokenizer=tokenizer,
        truncation=True,
        max_length=512,
    )

def compute_impact_score(label, score):
    """Calculates ground-level impact score (0 to 100)."""
    label_lower = str(label).lower()

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

    print(f"Running batch sentiment inference on {len(texts)} records...")
    predictions = model(texts, batch_size=batch_size)

    results = []
    for idx, res in enumerate(predictions):
        row = df.iloc[idx]
        raw_label = res["label"]
        confidence = res["score"]

        clean_label = label_map.get(raw_label, raw_label)
        impact_score = compute_impact_score(clean_label, confidence)

        results.append(
            {
                "id": row["id"],
                "source": row["source"],
                "language": row["language"],
                "story_group_id": row["story_group_id"],
                "sentiment_label": clean_label,
                "sentiment_score": round(confidence, 4),
                "impact_score": impact_score,
            }
        )

    return pd.DataFrame(results)


def save_nlp_results(df):
    """Saves output to SQLite table and exports CSV."""
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("nlp_processed_records", conn, if_exists="replace", index=False)
    conn.close()

    df.to_csv(CSV_PATH, index=False)


def main():
    print("Step 1: Loading clean NLP-ready data...")
    df = load_cleaned_data()
    print(f"Loaded {len(df)} records for NLP processing.")

    print("\nStep 2: Processing Sentiment Analysis & Impact Scores...")
    nlp_df = analyze_sentiment(df)

    print("\nStep 3: Saving output to SQLite & CSV...")
    save_nlp_results(nlp_df)

    print(
        f"\nProcessing complete! Output saved to table 'nlp_processed_records' and '{CSV_PATH}'."
    )


if __name__ == "__main__":
    main()