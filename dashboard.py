import pandas as pd
import streamlit as st
import plotly.express as px

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("Fatalities.xlsx")

# ==============================
# CLEAN DATA
# ==============================
df["Year"] = df["Year\n[Note 1]"].astype(str)
df["Year"] = df["Year"].str.replace("p", "", regex=False)

# Extract numeric year
df["Year_num"] = df["Year"].str.extract(r'(\d{4})').astype(int)

df.rename(columns={
    "Top-level Industry (SIC section)\n[Note 5]": "Industry"
}, inplace=True)

# ==============================
# TITLE
# ==============================
st.title("🚨 HSE Fatalities AI Dashboard")

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filters")

years = st.sidebar.multiselect("Year", df["Year"].unique(), df["Year"].unique())
regions = st.sidebar.multiselect("Region", df["Region"].dropna().unique(), df["Region"].dropna().unique())
authorities = st.sidebar.multiselect("Authority", df["Enforcing authority [Note 3]"].dropna().unique(), df["Enforcing authority [Note 3]"].dropna().unique())
industries = st.sidebar.multiselect("Industry", df["Industry"].dropna().unique(), df["Industry"].dropna().unique())
accidents = st.sidebar.multiselect("Accident Type", df["Kind of accident"].dropna().unique(), df["Kind of accident"].dropna().unique())

# ==============================
# APPLY FILTERS
# ==============================
filtered_df = df[
    (df["Year"].isin(years)) &
    (df["Region"].isin(regions)) &
    (df["Enforcing authority [Note 3]"].isin(authorities)) &
    (df["Industry"].isin(industries)) &
    (df["Kind of accident"].isin(accidents))
].copy()

# ==============================
# KPI SECTION
# ==============================
st.subheader("📊 Key Metrics")

trend = filtered_df.groupby("Year_num").size().sort_index()

total = len(filtered_df)
avg = int(trend.mean()) if len(trend) > 0 else 0
max_val = trend.max() if len(trend) > 0 else 0
max_year = trend.idxmax() if len(trend) > 0 else "N/A"

if len(trend) > 1 and trend.iloc[0] != 0:
    change = ((trend.iloc[-1] - trend.iloc[0]) / trend.iloc[0]) * 100
else:
    change = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Fatalities", total)
col2.metric("Avg / Year", avg)
col3.metric("Peak Year", f"{max_year} ({max_val})")
col4.metric("Trend %", f"{change:.1f}%")

# ==============================
# DATA PREVIEW
# ==============================
st.subheader("📊 Data Preview")
st.dataframe(filtered_df.head())

# ==============================
# 📈 INTERACTIVE CHARTS
# ==============================

# Trend
st.subheader("📈 Fatalities Trend")

if len(trend) > 0:
    trend_df = trend.reset_index()
    trend_df.columns = ["Year", "Fatalities"]

    fig = px.line(trend_df, x="Year", y="Fatalities", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# Authority
st.subheader("🏢 Authority Distribution")

auth_df = filtered_df["Enforcing authority [Note 3]"].value_counts().reset_index()
auth_df.columns = ["Authority", "Count"]

fig = px.bar(auth_df, x="Authority", y="Count")
st.plotly_chart(fig, use_container_width=True)

# Region
st.subheader("🌍 Regions")

region_df = filtered_df["Region"].value_counts().reset_index()
region_df.columns = ["Region", "Count"]

fig = px.bar(region_df, x="Region", y="Count")
st.plotly_chart(fig, use_container_width=True)

# Industry
st.subheader("🏭 Industries")

industry_df = filtered_df["Industry"].value_counts().reset_index()
industry_df.columns = ["Industry", "Count"]

fig = px.bar(industry_df, x="Industry", y="Count")
st.plotly_chart(fig, use_container_width=True)

# Accident
st.subheader("⚠️ Accident Types")

accident_df = filtered_df["Kind of accident"].value_counts().reset_index()
accident_df.columns = ["Accident", "Count"]

fig = px.bar(accident_df, x="Accident", y="Count")
st.plotly_chart(fig, use_container_width=True)

# Pie
st.subheader("🥧 Industry Distribution")

fig = px.pie(industry_df, names="Industry", values="Count")
st.plotly_chart(fig, use_container_width=True)

# ==============================
# AI INSIGHTS
# ==============================
st.subheader("🤖 AI Insights")

if len(trend) > 1:
    if change > 0:
        st.error("🚨 Increasing trend — Action required")
    else:
        st.success("✅ Decreasing trend — Good performance")

if len(industry_df) > 0:
    st.warning(f"Top Industry: {industry_df.iloc[0]['Industry']}")

if len(accident_df) > 0:
    st.warning(f"Top Accident Type: {accident_df.iloc[0]['Accident']}")

# ==============================
# MAP
# ==============================
st.subheader("🗺️ Map")

map_data = filtered_df["Region"].value_counts().reset_index()
map_data.columns = ["Region", "Fatalities"]

coords = {
    "London": [51.5074, -0.1278],
    "North West": [53.4808, -2.2426],
    "Scotland": [55.9533, -3.1883]
}

map_data["lat"] = map_data["Region"].map(lambda x: coords.get(x, [None, None])[0])
map_data["lon"] = map_data["Region"].map(lambda x: coords.get(x, [None, None])[1])

map_data = map_data.dropna()

st.map(map_data.rename(columns={"lat": "latitude", "lon": "longitude"}))
