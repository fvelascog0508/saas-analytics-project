import pandas as pd
import numpy as np

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("data/events_processed.csv")

# -------------------------
# BASIC CLEAN
# -------------------------
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# -------------------------
# USERS DERIVED
# -------------------------
df_users = df.groupby("user_id").agg(
    first_seen=("timestamp", "min"),
    last_seen=("timestamp", "max"),
    total_events=("event_type", "count")
).reset_index()

# -------------------------
# DAILY ACTIVE USERS (DAU)
# -------------------------
df_dau = df.groupby("date").agg(
    active_users=("user_id", "nunique"),
    events=("event_type", "count")
).reset_index()

# -------------------------
# EVENTS BY TYPE
# -------------------------
df_events_type = df.groupby("event_type").agg(
    total_events=("event_type", "count"),
    unique_users=("user_id", "nunique")
).reset_index()




# -------------------------
# ADD DIMENSION (SIMULATED)
# -------------------------
channels = ["organic", "paid_ads", "referral"]
df["channel"] = np.random.choice(channels, size=len(df))



# -------------------------
# FUNNEL ANALYSIS
# -------------------------
funnel_steps = ["signup", "login", "create_project"]

# Filtrar eventos del funnel
df_funnel = df[df["event_type"].isin(funnel_steps)]

# Eliminar duplicados por usuario y evento
df_funnel_unique = df_funnel.drop_duplicates(subset=["user_id", "event_type"])

# Contar usuarios únicos por paso
funnel_counts = df_funnel_unique.groupby("event_type")["user_id"].nunique().reset_index()

# Ordenar pasos del funnel correctamente
funnel_counts["event_type"] = pd.Categorical(
    funnel_counts["event_type"],
    categories=funnel_steps,
    ordered=True
)

funnel_counts = funnel_counts.sort_values("event_type")

# -------------------------
# CONVERSION RATE
# -------------------------
funnel_counts["conversion_rate"] = (
    funnel_counts["user_id"] / funnel_counts["user_id"].iloc[0]
)


# -------------------------
# FUNNEL BY CHANNEL
# -------------------------

funnel_segment = (
    df_funnel_unique
    .groupby(["channel", "event_type"])["user_id"]
    .nunique()
    .reset_index()
)




# coger baseline correcto (signup)
baseline = (
    funnel_segment[funnel_segment["event_type"] == "signup"]
    .set_index("channel")["user_id"]
)

# mapear baseline a todas las filas del mismo canal
funnel_segment["baseline"] = funnel_segment["channel"].map(baseline)

# calcular conversion
funnel_segment["conversion_rate"] = funnel_segment["user_id"] / funnel_segment["baseline"]





# Ordenar funnel correctamente
funnel_segment["event_type"] = pd.Categorical(
    funnel_segment["event_type"],
    categories=funnel_steps,
    ordered=True
)

funnel_segment = funnel_segment.sort_values(["channel", "event_type"])

print("\n✅ Funnel by channel")
print(funnel_segment)



# -------------------------
# COHORT ANALYSIS
# -------------------------

# ordenar por usuario y tiempo
df = df.sort_values(["user_id", "timestamp"])

# obtener fecha de primer evento (signup)
df["cohort_date"] = df.groupby("user_id")["timestamp"].transform("min")

# convertir a mes
df["cohort_month"] = df["cohort_date"].dt.to_period("M")
df["event_month"] = df["timestamp"].dt.to_period("M")



df["cohort_index"] = (
    (df["event_month"].dt.year - df["cohort_month"].dt.year) * 12 +
    (df["event_month"].dt.month - df["cohort_month"].dt.month)
)

cohort_data = df.groupby(["cohort_month", "cohort_index"]).agg(
    users=("user_id", "nunique")
).reset_index()


cohort_pivot = cohort_data.pivot(
    index="cohort_month",
    columns="cohort_index",
    values="users"
)


cohort_size = cohort_pivot.iloc[:, 0]

cohort_retention = cohort_pivot.divide(cohort_size, axis=0)


import matplotlib.pyplot as plt
import seaborn as sns



# -------------------------
# COHORT HEATMAP
# -------------------------

plt.figure(figsize=(10,6))

sns.heatmap(
    cohort_retention,
    annot=True,
    fmt=".2f",
    cmap="RdYlGn",  # rojo → verde
    linewidths=0.5
)

plt.title("Cohort Retention (%)")
plt.xlabel("Months since signup")
plt.ylabel("Cohort (signup month)")

plt.tight_layout()
# plt.show()

plt.savefig("data/cohort_heatmap.png")
plt.close()




# -------------------------
# SAVE
# -------------------------
df_users.to_csv("data/users_derived.csv", index=False)
df_dau.to_csv("data/dau.csv", index=False)
df_events_type.to_csv("data/events_summary.csv", index=False)
funnel_counts.to_csv("data/funnel.csv", index=False)
cohort_retention.to_csv("data/cohort_retention.csv")

# -------------------------
# PRINT
# -------------------------
print("\n✅ USERS")
print(df_users.head())

print("\n✅ DAU")
print(df_dau.head())

print("\n✅ EVENTS")
print(df_events_type.head())

print("\n✅ FUNNEL")
print(funnel_counts)

print("\n✅ Cohort retention")
print(cohort_retention.head())
