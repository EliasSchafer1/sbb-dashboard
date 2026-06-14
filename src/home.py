from datetime import date
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px
from layout import sbb_header
from data_store import get_trains_df

trains_df = get_trains_df()

#display sbb header
sbb_header("Home SBB Trains per Month")
st.write("Welcome on the Dashboard of the Project SBB Trains Per Month! " \
"Here you can explore a real-life dataset from SBB " \
"containing the number of passenger and freight trains for each route section in Switzerland. " \
"The data is up to date with full information about 2025 and partial information about 2024. " \
"Have fun!")
st.space("large")

c1, c2, c3 = st.columns(3)
c1.metric("Rows", trains_df.shape[0])
c2.metric("Columns", trains_df.shape[1])
c3.metric("Missing values", trains_df.isna().sum().sum())
st.space("large")


c1, c2 = st.columns([3, 1], gap = "large")
with c1:
    st.subheader("Preview")
    st.dataframe(trains_df)
with c2:
    st.subheader("Missing Values")
    st.write(trains_df.isna().sum())
st.space("large")


c1, c2 = st.columns(2, gap = "large")
#Barplot of Trains per month 2025
with c1: 
    st.subheader("Passenger and Freight Trains in 2025")
    st.write("This chart compares the monthly number of passenger and freight trains in 2025.")
    total_trains_per_month = trains_df.groupby("reference_month").agg(
        total_trains_2025 = ("dtv_reference_month", "sum"),
        passenger_trains_2025 = ("dtv_p_reference_month", "sum"),
        freight_trains_2025 =("dtv_g_reference_month", "sum")
    ).reset_index()
    total_trains_per_month = total_trains_per_month.sort_values("reference_month")
    fig = px.bar(total_trains_per_month, x = "reference_month", y = ["passenger_trains_2025", "freight_trains_2025"], barmode="stack", color_discrete_map={
        "passenger_trains_2025": "#F67469", "freight_trains_2025": "#D50000"
    })
    st.plotly_chart(fig, width="stretch")

#Barplot of Trains per month 2024
with c2: 
    st.subheader("Passenger and Freight Trains in 2024")
    st.write("This chart compares the monthly number of passenger and freight trains in 2024.")
    total_trains_per_month = trains_df.groupby("reference_month").agg(
        total_trains_2024 = ("dtv_previous_year_month", "sum"),
        passenger_trains_2024 = ("dtv_p_previous_year_month", "sum"),
        freight_trains_2024 =("dtv_g_previous_year_month", "sum")
    ).reset_index()
    total_trains_per_month = total_trains_per_month.sort_values("reference_month")
    fig = px.bar(total_trains_per_month, x = "reference_month", y = ["passenger_trains_2024", "freight_trains_2024"], barmode="stack", color_discrete_map={
        "passenger_trains_2024": "#F67469", "freight_trains_2024": "#D50000"
    })
    st.plotly_chart(fig, width="stretch")

with c1:
    #Barplot of Trains of top_10_sections
    st.subheader("Top 10 Route Sections")
    st.write("This chart shows the distribution of passenger and freight trains on the ten busiest route sections in 2025.")
    top_10_sections = trains_df.groupby("section").agg(
        total_trains_2025 = ("dtv_reference_month", "sum"),
        passenger_trains_2025 = ("dtv_p_reference_month", "sum"),
        freight_trains_2025 = ("dtv_g_reference_month", "sum")
    ).reset_index()
    top_10_sections = top_10_sections.sort_values("total_trains_2025", ascending=False).head(10)
    top_10_sections = top_10_sections.rename(columns={"section": "Top_10_Sections"})
    fig = px.bar(top_10_sections, x = "Top_10_Sections", y= ["passenger_trains_2025", "freight_trains_2025"],  barmode="stack", color_discrete_map={
        "passenger_trains_2025": "#F67469", "freight_trains_2025": "#D50000"
    })
    st.plotly_chart(fig, width="stretch")
    st.space("large")

with c2:
    #Histogramm distribution of average number trains per section
    st.subheader("Average Number of Trains per Route Section")
    st.write("This chart shows the average number of trains per route section in 2025.")
    avg_number_trains_per_section = trains_df.groupby("section")["dtv_reference_month"].mean().reset_index()
    avg_number_trains_per_section = avg_number_trains_per_section.rename(columns = {"section": "Sections", "dtv_reference_month": "total_trains_2025"})
    fig = px.bar(avg_number_trains_per_section, x = "Sections", y = "total_trains_2025", color_discrete_sequence=["#D50000"])
    st.plotly_chart(fig, width="stretch")


st.subheader("Handle Missing Values")

# fill missing previous-year train counts with column mean
if st.button("Fill missing previous-year values (mean)"):
    cols = [
        "dtv_previous_year_month",
        "dtv_p_previous_year_month",
        "dtv_g_previous_year_month",
    ]

    for col in cols:
        trains_df[col] = trains_df[col].fillna(
            trains_df[col].mean()
        )

    st.success("Missing values filled")
    st.rerun()

st.dataframe(trains_df.dtypes.astype(str))