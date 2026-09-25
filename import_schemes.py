import pandas as pd
import sqlite3

CSV_PATH = "updated_data.csv"
DB_PATH = "policy_data.db"

df = pd.read_csv(CSV_PATH)

print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")

conn = sqlite3.connect(DB_PATH)
df.to_sql("scheme_reference", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

print(f"Done. Inserted {len(df)} rows into 'scheme_reference' table.")