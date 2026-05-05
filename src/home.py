import streamlit as st
import pandas as pd
from data_cleaning import load_data, clean_data
import matplotlib.pyplot as plt

# Pre processing
trains_raw_df = load_data()
trains_df = clean_data(trains_raw_df)

st.title("SBB Trains per Route")
st.write("Here you can explore a real-life dataset from SBB.")

st.subheader("Preview")
st.dataframe(trains_df)

st.subheader("Dataset information")
st.write("Rows:", trains_df.shape[0])
st.write("Columns:", trains_df.shape[1])
st.write(trains_df.dtypes)


st.header("Train Traffic Overview")
#Barplot of Trains per month
st.subheader("Passenger and Freight Trains in 2025")
st.write("This chart compares the monthly number of passenger and freight trains in 2025.")
total_trains_per_month = trains_df.groupby("bezugsmonat").agg(
    zuege_total_2025 = ("dtv_bezugsmonat", "sum"),
    personenzuege_2025 = ("dtv_p_bezugsmonat", "sum"),
    gueterzuege_2025 =("dtv_g_bezugsmonat", "sum")
).reset_index()
total_trains_per_month["Monate"] = (total_trains_per_month["bezugsmonat"].dt.to_timestamp().dt.month)
total_trains_per_month = total_trains_per_month.sort_values("Monate")
st.bar_chart(data=total_trains_per_month, x = "Monate", y = ["personenzuege_2025", "gueterzuege_2025"], stack = True)

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
compare_months["Monate"] = (compare_months["bezugsmonat"].dt.to_timestamp().dt.month)
compare_months = compare_months.sort_values("Monate")
st.line_chart(data=compare_months, x = "Monate", y = ["zuege_total_2025", "zuege_total_2024"])

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


#-------------------------------------------------

@st.dialog("New Train Line Added")
def add_data(strecke_bezeichnung):
    st.write("You added the new train line ", strecke_bezeichnung, " into the dataframe.")
    if st.button('OK'):
        st.rerun()

st.subheader("Input Additional Data")
with st.form("new_train_line"):
    st.write("Here you can add data from a new train line into the dataframe.")

    strecke_bezeichnung = st.text_input('Strecke Bezeichnung', key = "strecke")
    abschnitt = st.text_input('Abschnitt', key = "abschnitt")

    submitted = st.form_submit_button('Submit')

if(submitted):
    add_data(strecke_bezeichnung)


#Müll
#st.map(data=total_trains_per_month, latitude=None, longitude=None)
#fig, ax = plt.subplots()
#ax.bar("bezugsmonat", "dtv_bezugsmonat")


