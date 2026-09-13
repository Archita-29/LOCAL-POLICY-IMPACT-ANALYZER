import sqlite3

conn = sqlite3.connect("policy_data.db")

print("--- ENGLISH RECORDS ---")
for row in conn.execute("SELECT source, language, title FROM raw_records WHERE language='english' LIMIT 10"):
    print(row)

print("--- HINGLISH RECORDS ---")
for row in conn.execute("SELECT source, language, title FROM raw_records WHERE language='hinglish' LIMIT 10"):
    print(row)

conn.close()