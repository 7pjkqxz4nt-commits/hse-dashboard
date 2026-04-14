import pandas as pd
import streamlit as st
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("Fatalities.xlsx")

# Clean
df["Year"] = df["Year\n[Note 1]"].astype(str)
df["Year"] = df["Year"].str.replace("p", "", regex=False)
df["Year_num"] = df["Year"].str.extract(r'(\d{4})').astype(int)

df.rename(columns={
    "Top-level Industry (SIC section)\n[Note 5]": "Industry"
}, inplace=True)

# ==============================
# TITLE
# ==============================
st.title("📊 Executive HSE Dashboard")

# ==============================
# KPI SECTION (BIG STYLE)
# ==============================
trend = df.groupby("Year_num").size().sort_index()

total = len(df)
avg = int(trend.mean())
max_val = trend.max()
max_year = trend.idxmax()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Fatalities", total)
col2.metric("Average / Year", avg)
col3.metric("Peak Year", f"{max_year}")
col4.metric("Max Fatalities", max_val)

st.markdown("---")

# ==============================
# CHARTS IN COLUMNS
# ==============================

col1, col2 = st.columns(2)

# Trend
with col1:
    st.subheader("📈 Trend")

    trend_df = trend.reset_index()
    trend_df.columns = ["Year", "Fatalities"]

    fig = px.line(trend_df, x="Year", y="Fatalities", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# Pie
with col2:
    st.subheader("🥧 Industry Distribution")

    industry_df = df["Industry"].value_counts().reset_index()
    industry_df.columns = ["Industry", "Count"]

    fig = px.pie(industry_df, names="Industry", values="Count")
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# SECOND ROW
# ==============================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Authority")

    auth_df = df["Enforcing authority [Note 3]"].value_counts().reset_index()
    auth_df.columns = ["Authority", "Count"]

    fig = px.bar(auth_df, x="Authority", y="Count")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⚠️ Accident Types")

    acc_df = df["Kind of accident"].value_counts().reset_index()
    acc_df.columns = ["Accident", "Count"]

    fig = px.bar(acc_df, x="Accident", y="Count")
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# EXECUTIVE INSIGHT
# ==============================
st.markdown("---")
st.subheader("🤖 Executive Insight")

if trend.iloc[-1] > trend.iloc[0]:
    st.error("🚨 Fatalities trend is increasing — Immediate action required")
else:
    st.success("✅ Fatalities trend is improving")

top_industry = industry_df.iloc[0]["Industry"]
st.warning(f"⚠️ Highest risk industry: {top_industry}")
