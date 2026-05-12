from datetime import date
import streamlit as st
import pandas as pd
import json
from data_cleaning import load_data, clean_data
import matplotlib.pyplot as plt
from preprocessing import extract_stations_df
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px

#layout
from pathlib import Path
import base64
import streamlit as st

def image_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

train_img = image_to_base64("src/train.png")

st.markdown(
    f"""
    <style>
    .sbb-hero {{
        height: 120px;
        background: #e00000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
        margin: -48px -48px 32px -48px;
        color: white;
    }}

    .sbb-hero h1 {{
        font-size: 34px;
        margin: 0;
        font-weight: 700;
    }}

    .sbb-hero img {{
        height: 95px;
        object-fit: contain;
        transform: translateY(5.8px);
    }}
    </style>

    <div class="sbb-hero">
        <h1>SBB Trains per Route</h1>
        <img src="data:image/png;base64,{train_img}" alt="Train">
    </div>
    """,
    unsafe_allow_html=True,
)


# Pre-processing
# Store cleaned dataframe in session_state so user changes such as 
# added rows or imputed values are kept during the current session.
trains_raw_df = load_data()

if "trains_df" not in st.session_state:
    st.session_state.trains_df = clean_data(trains_raw_df)
trains_df = st.session_state.trains_df

if "stations_df" not in st.session_state:
    st.session_state.stations_df = extract_stations_df(trains_df = st.session_state.trains_df)  
stations_df = st.session_state.stations_df


# web page


st.write("Here you can explore a real-life dataset from SBB.")

st.subheader("Preview")
st.dataframe(trains_df)

st.subheader("Dataset information")
st.write("Rows:", trains_df.shape[0])
st.write("Columns:", trains_df.shape[1])

st.subheader("Missing values per column")   #show data that the user might want to impute
st.write(trains_df.isna().sum())

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

st.header("Train Traffic Overview")
#Barplot of Trains per month
st.subheader("Passenger and Freight Trains in 2025")
st.write("This chart compares the monthly number of passenger and freight trains in 2025.")
total_trains_per_month = trains_df.groupby("bezugsmonat").agg(
    zuege_total_2025 = ("dtv_bezugsmonat", "sum"),
    personenzuege_2025 = ("dtv_p_bezugsmonat", "sum"),
    gueterzuege_2025 =("dtv_g_bezugsmonat", "sum")
).reset_index()
total_trains_per_month = total_trains_per_month.sort_values("bezugsmonat")
st.bar_chart(data=total_trains_per_month, x = "bezugsmonat", y = ["personenzuege_2025", "gueterzuege_2025"], stack = True)

#Histogramm distribution of average number trains per line
st.subheader("Average Number of Trains per Route")
st.write("This chart shows the average number of trains per route in 2025.")
avg_number_trains_per_line = trains_df.groupby("strecke_bezeichnung")["dtv_bezugsmonat"].mean().reset_index()
avg_number_trains_per_line = avg_number_trains_per_line.rename(columns = {"strecke_bezeichnung": "Strecken", "dtv_bezugsmonat": "zuege_total_2025"})
st.bar_chart(data=avg_number_trains_per_line, x = "Strecken", y = "zuege_total_2025")

#Linediagram of trains_2025 compare to trains_2024
st.subheader("Train Traffic Comparison: 2025 vs. 2024")
st.write("This line chart compares the total number of trains per month in 2025 with the same months in 2024.")
compare_months = trains_df.groupby("bezugsmonat").agg(
    zuege_total_2025 = ("dtv_bezugsmonat", "sum"),
    zuege_total_2024 = ("dtv_vorjahresmonat", "sum")
).reset_index()
compare_months = compare_months.sort_values("bezugsmonat")
st.line_chart(data=compare_months, x = "bezugsmonat", y = ["zuege_total_2025", "zuege_total_2024"])


#Barplot of Trains of top_10_lines
st.subheader("Passenger and Freight Trains on the Top 10 Routes")
st.write("This chart shows the distribution of passenger and freight trains on the ten busiest routes in 2025.")
top_10_lines = trains_df.groupby("strecke_bezeichnung").agg(
    zuege_total_2025 = ("dtv_bezugsmonat", "sum"),
    personenzuege_2025 = ("dtv_p_bezugsmonat", "sum"),
    gueterzuege_2025 = ("dtv_g_bezugsmonat", "sum")
).reset_index()
top_10_lines = top_10_lines.sort_values("zuege_total_2025", ascending=False).head(10)
top_10_lines = top_10_lines.rename(columns={"strecke_bezeichnung": "Top_10_Strecken"})
st.bar_chart(data=top_10_lines, x = "Top_10_Strecken", y= ["personenzuege_2025", "gueterzuege_2025"], stack=True)


