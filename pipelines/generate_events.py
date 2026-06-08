import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# -------------------------
# CONFIG
# -------------------------
N_USERS = 1000
START_DATE = datetime(2024, 1, 1)

events = []

funnel_steps = ["signup", "login", "create_project"]

# -------------------------
# GENERATE DATA
# -------------------------
for user_id in range(1, N_USERS + 1):

    # signup siempre existe
    signup_date = START_DATE + timedelta(days=random.randint(0, 60))
    events.append((user_id, "signup", signup_date))

    # probabilidad de login
    if random.random() < 0.8:
        login_date = signup_date + timedelta(days=random.randint(0, 5))
        events.append((user_id, "login", login_date))

        # probabilidad de crear proyecto
        if random.random() < 0.5:
            create_date = login_date + timedelta(days=random.randint(0, 5))
            events.append((user_id, "create_project", create_date))

    # eventos adicionales (ruido realista)
    extra_events = ["invite_user", "upload_file"]
    for _ in range(random.randint(0, 3)):
        event_date = signup_date + timedelta(days=random.randint(0, 30))
        events.append((user_id, random.choice(extra_events), event_date))

# -------------------------
# CREATE DF
# -------------------------
df = pd.DataFrame(events, columns=["user_id", "event_type", "timestamp"])

# ordenar por fecha
df = df.sort_values("timestamp")

# -------------------------
# SAVE
# -------------------------
df.to_csv("data/raw/events.csv", index=False)

print("✅ Dataset realista generado")
print(df.head())