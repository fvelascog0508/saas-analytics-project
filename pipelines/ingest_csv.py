import pandas as pd

# -------------------------
# LOAD RAW CSV
# -------------------------
df = pd.read_csv("data/raw/events.csv")

# -------------------------
# CLEAN / STANDARDIZE
# -------------------------
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["event_type"] = df["event_type"].str.lower()

# -------------------------
# SAVE TO PROCESSED
# -------------------------
df.to_csv("data/events_processed.csv", index=False)

print("✅ Data ingested and processed")
print(df.head())
