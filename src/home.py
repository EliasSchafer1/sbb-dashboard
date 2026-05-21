from datetime import date
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px
from layout import sbb_header
from main import trains_df

#display sbb header
sbb_header("Home SBB Trains per Month")

# web page
st.set_page_config(layout="wide")
st.write("Welcome on the Dashbord of the Project SBB Trains Per Month! " \
"Here you can explore a real-life dataset from SBB " \
"containing the number of passenger and freight trains for each train line in Switzerland. " \
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
    total_trains_per_month = trains_df.groupby("bezugsmonat").agg(
        zuege_total_2025 = ("dtv_bezugsmonat", "sum"),
        personenzuege_2025 = ("dtv_p_bezugsmonat", "sum"),
        gueterzuege_2025 =("dtv_g_bezugsmonat", "sum")
    ).reset_index()
    total_trains_per_month = total_trains_per_month.sort_values("bezugsmonat")
    fig = px.bar(total_trains_per_month, x = "bezugsmonat", y = ["personenzuege_2025", "gueterzuege_2025"], barmode="stack", color_discrete_map={
        "personenzuege_2025": "#F67469", "gueterzuege_2025": "#D50000"
    })
    st.plotly_chart(fig, width="stretch")

#Barplot of Trains per month 2024
with c2: 
    st.subheader("Passenger and Freight Trains in 2024")
    st.write("This chart compares the monthly number of passenger and freight trains in 2024.")
    total_trains_per_month = trains_df.groupby("bezugsmonat").agg(
        zuege_total_2024 = ("dtv_bezugsmonat", "sum"),
        personenzuege_2024 = ("dtv_p_bezugsmonat", "sum"),
        gueterzuege_2024 =("dtv_g_bezugsmonat", "sum")
    ).reset_index()
    total_trains_per_month = total_trains_per_month.sort_values("bezugsmonat")
    fig = px.bar(total_trains_per_month, x = "bezugsmonat", y = ["personenzuege_2024", "gueterzuege_2024"], barmode="stack", color_discrete_map={
        "personenzuege_2024": "#F67469", "gueterzuege_2024": "#D50000"
    })
    st.plotly_chart(fig, width="stretch")

with c1:
    #Barplot of Trains of top_10_lines
    st.subheader("Top 10 lines")
    st.write("This chart shows the distribution of passenger and freight trains on the ten busiest routes in 2025.")
    top_10_lines = trains_df.groupby("strecke_bezeichnung").agg(
        zuege_total_2025 = ("dtv_bezugsmonat", "sum"),
        personenzuege_2025 = ("dtv_p_bezugsmonat", "sum"),
        gueterzuege_2025 = ("dtv_g_bezugsmonat", "sum")
    ).reset_index()
    top_10_lines = top_10_lines.sort_values("zuege_total_2025", ascending=False).head(10)
    top_10_lines = top_10_lines.rename(columns={"strecke_bezeichnung": "Top_10_Strecken"})
    fig = px.bar(top_10_lines, x = "Top_10_Strecken", y= ["personenzuege_2025", "gueterzuege_2025"],  barmode="stack", color_discrete_map={
        "personenzuege_2025": "#F67469", "gueterzuege_2025": "#D50000"
    })
    st.plotly_chart(fig, width="stretch")
    st.space("large")

with c2:
    #Histogramm distribution of average number trains per line
    st.subheader("Average Number of Trains per Route")
    st.write("This chart shows the average number of trains per route in 2025.")
    avg_number_trains_per_line = trains_df.groupby("strecke_bezeichnung")["dtv_bezugsmonat"].mean().reset_index()
    avg_number_trains_per_line = avg_number_trains_per_line.rename(columns = {"strecke_bezeichnung": "Strecken", "dtv_bezugsmonat": "zuege_total_2025"})
    fig = px.bar(avg_number_trains_per_line, x = "Strecken", y = "zuege_total_2025", color_discrete_sequence=["#D50000"])
    st.plotly_chart(fig, width="stretch")


st.subheader("Handle Missing Values")

# fill missing previous-year train counts with column mean
if st.button("Fill missing previous-year values (mean)"):
    cols = [
        "dtv_vorjahresmonat",
        "dtv_p_vorjahresmonat",
        "dtv_g_vorjahresmonat",
    ]

    for col in cols:
        trains_df[col] = trains_df[col].fillna(
            trains_df[col].mean()
        )

    st.success("Missing values filled")
    st.rerun()

st.dataframe(trains_df.dtypes.astype(str))