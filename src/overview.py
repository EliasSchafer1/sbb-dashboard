from datetime import date
import streamlit as st
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px
from layout import sbb_header
from data_store import get_trains_df

trains_df = get_trains_df()

sbb_header("Home SBB Trains per Month")
st.write("This dashboard provides an overview of daily train frequencies across SBB route sections in Switzerland, "\
    "based on official SBB open data. Explore monthly averages for passenger and freight trains in 2024 and 2025.")
st.space("large")

c1, c2, c3 = st.columns(3)
c1.metric("Rows", trains_df.shape[0])
c2.metric("Columns", trains_df.shape[1])
c3.metric("Missing values", trains_df.isna().sum().sum())
st.space("large")

# Dataframe preview
st.subheader("Preview")
st.dataframe(trains_df)

# Handling missing values
c1, c2 = st.columns(2, gap = "large")
with c1:
    st.subheader("Missing Values")
    missing = trains_df.isna().sum().reset_index()
    missing.columns = ["Column", "Missing Values"]
    st.dataframe(missing)
with c2:
    st.subheader("Impute Missing Values")
    st.write("Missing values in previous-year columns indicate route sections without 2024 data for that month, "\
        "due to construction, service interruptions, or changes in the route network.")
    # fill missing previous-year values
    if "filled" not in st.session_state:
        st.session_state.filled = False

    if st.session_state.filled:
        st.info(f"Missing values have been imputed with the column {st.session_state.method.lower()}.")
    else:
        option = st.radio("Imputation method:", ["Mean", "Median"])
        if st.button(f"Fill missing previous-year values ({option.lower()})"):
            cols = [
                "daily_trains_py",
                "daily_passenger_trains_py",
                "daily_freight_trains_py",
            ]
            for col in cols:
                fill_value = trains_df[col].mean() if option == "Mean" else trains_df[col].median()
                trains_df[col] = trains_df[col].fillna(fill_value)
            st.session_state.filled = True
            st.session_state.method = option
            st.rerun()
st.space("large")


years = [2025, 2024]
daily_trains_cols = ["daily_trains", "daily_trains_py"]
daily_passenger_trains_cols = ["daily_passenger_trains", "daily_passenger_trains_py"]
daily_freight_trains_cols = ["daily_freight_trains", "daily_freight_trains_py"]

# Barplots per month
st.subheader("Passenger and Freight Trains by Month")
st.write("This chart shows the monthly average of daily trains across all route sections, split by passenger and freight.")
c1, c2 = st.columns(2, gap="large")
for i, col in enumerate([c1, c2]):
    with col:
        st.markdown(f"**{years[i]}**")
        avg_per_month = trains_df.groupby("reference_month").agg(
            passenger_trains=(daily_passenger_trains_cols[i], "mean"),
            freight_trains=(daily_freight_trains_cols[i], "mean")
        ).reset_index()
        fig = px.bar(avg_per_month, x="reference_month", y=["passenger_trains", "freight_trains"],
                     barmode="stack",
                     labels={"reference_month":"Month","value": "Average Daily Trains", "variable": "Train Type"},
                     color_discrete_map={"passenger_trains": "#F67469", "freight_trains": "#D50000"})
        st.plotly_chart(fig, width="stretch")

# Top 10 Route Sections
st.subheader("Top 10 Route Sections by Average Daily Trains")
st.write("This chart shows the average daily number of passenger and freight trains on the ten busiest route sections.")
c3, c4 = st.columns(2, gap="large")
for i, col in enumerate([c3, c4]):
    with col:
        st.markdown(f"**{years[i]}**")
        top_10 = trains_df.groupby("section").agg(
            avg_trains=(daily_trains_cols[i], "mean"),
            passenger_trains=(daily_passenger_trains_cols[i], "mean"),
            freight_trains=(daily_freight_trains_cols[i], "mean")
        ).reset_index()
        top_10 = top_10.sort_values("avg_trains", ascending=False).head(10)
        fig = px.bar(top_10, x="section", y=["passenger_trains", "freight_trains"],
                     barmode="stack",
                     labels={"value": "Average Daily Trains", "variable": "Train Type", "section": "Section"},
                     color_discrete_map={"passenger_trains": "#F67469", "freight_trains": "#D50000"})
        st.plotly_chart(fig, width="stretch")

# Distribution of Average Daily Trains
st.subheader("Distribution of Average Daily Trains")
st.write("This histogram shows the distribution of average daily trains across all route sections.")
# Option for log, since data-distribution is right-skewed
log_scale = st.toggle("Log scale (x-axis)")
c5, c6 = st.columns(2, gap="large")
for i, col in enumerate([c5, c6]):
    with col:
        st.markdown(f"**{years[i]}**")
        avg_per_section = trains_df.groupby("section")[daily_trains_cols[i]].mean().reset_index()
        
        if log_scale:
            avg_per_section["log_value"] = np.log1p(avg_per_section[daily_trains_cols[i]])
            fig = px.histogram(avg_per_section, x="log_value",
                               nbins=60,
                               color_discrete_sequence=["#D50000"],
                               labels={"log_value": "Average Daily Trains"})
            # Set tick labels to real values
            tick_vals = [0, 10, 20, 50, 100, 200, 500, 1000, 2000]
            tick_log = [np.log1p(v) for v in tick_vals]
            fig.update_traces(hovertemplate="Route Sections: %{y}<extra></extra>") # Only show count, not bins because of log-values of bins
            fig.update_xaxes(tickvals=tick_log, ticktext=[str(v) for v in tick_vals])
        else:
            fig = px.histogram(avg_per_section, x=daily_trains_cols[i],
                           nbins=60,
                           color_discrete_sequence=["#D50000"],
                           labels={daily_trains_cols[i]: "Average Daily Trains"})
            fig.update_traces(xbins=dict(start=0, size=30)) # Fixed size bins anchored at zero
            fig.update_xaxes(range=[0, avg_per_section[daily_trains_cols[i]].max() * 1.05], dtick=100)
        fig.update_yaxes(title_text="Number of Route Sections")
        st.plotly_chart(fig, width="stretch")