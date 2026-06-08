from google.cloud import bigquery
import pandas as pd

# -------------------------
# INIT CLIENT
# -------------------------
client = bigquery.Client()

# -------------------------
# LOAD CSV
# -------------------------
df = pd.read_csv("data/events_processed.csv")

# -------------------------
# DESTINATION TABLE
# -------------------------
table_id = "project-ecommerce-497614.saas_analytics.events_raw"

# -------------------------
# LOAD TO BIGQUERY
# -------------------------
job = client.load_table_from_dataframe(df, table_id)
job.result()

print("✅ Data loaded to BigQuery successfully")