import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
from google.oauth2 import service_account
import time
from google import genai
import os
from dotenv import load_dotenv
from pathlib import Path

# -------------------------
# BASE PATH
# -------------------------
BASE_PATH = Path(__file__).resolve().parent.parent

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv(BASE_PATH / ".env")
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ API key not loaded")
    st.stop()

# -------------------------
# GEMINI
# -------------------------
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=api_key)

client_ai = get_gemini_client()

def call_gemini(prompt, retries=3):
    for i in range(retries):
        try:
            response = client_ai.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception:
            if i < retries - 1:
                time.sleep(2)
            else:
                return "⚠️ AI unavailable."

# -------------------------
# BIGQUERY
# -------------------------
@st.cache_resource
def get_bq_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

bq = get_bq_client()

# -------------------------
# APP UI
# -------------------------
st.set_page_config(page_title="SaaS Analytics", layout="wide")
st.title("📊 SaaS Analytics Dashboard")

# -------------------------
# SIDEBAR FILTER
# -------------------------
st.sidebar.header("Filters")

# obtener rango de fechas
@st.cache_data
def get_date_range():
    query = """
        SELECT 
            MIN(event_date) AS min_date,
            MAX(event_date) AS max_date
        FROM `project-ecommerce-497614.saas_analytics.stg_events`
    """
    return bq.query(query).to_dataframe()

date_bounds = get_date_range()

min_date = date_bounds["min_date"][0]
max_date = date_bounds["max_date"][0]

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# ✅ VALIDACIÓN ROBUSTA (CLAVE)
if not date_range or len(date_range) != 2:
    st.warning("Please select a valid date range")
    st.stop()

start_date, end_date = date_range

# -------------------------
# LOAD DATA FROM BQ
# -------------------------
@st.cache_data
def load_data(start_date, end_date):

    query_events = f"""
        SELECT *
        FROM `project-ecommerce-497614.saas_analytics.stg_events`
        WHERE event_date BETWEEN '{start_date}' AND '{end_date}'
    """

    query_dau = f"""
        SELECT
            event_date,
            COUNT(DISTINCT user_id) AS active_users
        FROM `project-ecommerce-497614.saas_analytics.stg_events`
        WHERE event_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY event_date
        ORDER BY event_date
    """

    query_funnel = f"""
        SELECT
            event_type,
            COUNT(DISTINCT user_id) AS users
        FROM `project-ecommerce-497614.saas_analytics.stg_events`
        WHERE event_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY event_type
        ORDER BY users DESC
    """

    df_events = bq.query(query_events).to_dataframe()
    df_dau = bq.query(query_dau).to_dataframe()
    df_funnel = bq.query(query_funnel).to_dataframe()

    return df_events, df_dau, df_funnel


df_events, df_dau, funnel_counts = load_data(start_date, end_date)

# -------------------------
# KPIs
# -------------------------
col1, col2, col3 = st.columns(3)

total_users = df_events["user_id"].nunique()
avg_events = df_events.groupby("user_id").size().mean()

conversion = 0
if "create_project" in funnel_counts["event_type"].values:
    signup = funnel_counts.loc[funnel_counts["event_type"] == "signup", "users"].values
    create = funnel_counts.loc[funnel_counts["event_type"] == "create_project", "users"].values

    if len(signup) > 0:
        conversion = create[0] / signup[0]

col1.metric("Total Users", total_users)
col2.metric("Avg Events/User", round(avg_events, 2))
col3.metric("Activation Rate", f"{conversion:.2%}")

# -------------------------
# CHARTS
# -------------------------
st.subheader("📈 Daily Active Users")
st.plotly_chart(
    px.line(df_dau, x="event_date", y="active_users"),
    use_container_width=True
)

st.subheader("🔻 Funnel")
st.plotly_chart(
    px.bar(funnel_counts, x="event_type", y="users"),
    use_container_width=True
)

# -------------------------
# AI INSIGHTS
# -------------------------
st.subheader("🤖 AI Insights")

if st.button("Explain this dashboard"):
    prompt = f"""
    You are a senior product analyst.

    Funnel:
    {funnel_counts.to_string(index=False)}

    DAU:
    {df_dau.to_string(index=False)}

    Provide insights and recommendations.
    """

    with st.spinner("Analyzing..."):
        answer = call_gemini(prompt)

    st.write(answer)

# -------------------------
# CHAT
# -------------------------
st.subheader("💬 Ask your data")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    prompt = f"""
    You are a product analyst.

    Funnel:
    {funnel_counts.to_string(index=False)}

    DAU:
    {df_dau.to_string(index=False)}

    Question:
    {user_input}
    """

    with st.spinner("Thinking..."):
        answer = call_gemini(prompt)

    st.chat_message("assistant").write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})