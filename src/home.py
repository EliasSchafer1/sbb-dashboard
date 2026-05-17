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

st.title("SBB Trains per Route")
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

# Linechart of monthly average of trains in 2025
st.subheader("Monthly train traffic")
st.write("This line chart shows the monthly train traffic per selected section for the selected year.")
# Summe oder Durchschnitt der ausgewählten Stationen, alle Stationen gleichzeitig
# Auswählen zwischen dtv, dtv_p oder dtv_g
col11, col12, col13, col14 = st.columns(4)
# User specifies the year
with col12:
    selected_year = st.selectbox(
        "Jahr auswählen",
        options=[2024, 2025],
        key="year_select_traffic"
    )
with col13:
    metrics = ["Separate", "Sum", "Mean"]
    metric = st.radio(
        "Metric",
        metrics
    )
train_types = ["All types", "Passenger trains", "Freight trains"]
types_to_prefix = {"All types":"dtv_", "Passenger trains":"dtv_p_", "Freight trains":"dtv_g_"}
with col14:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_traffic"
    )
data_sel = "bezugsmonat" if selected_year == 2025 else "vorjahresmonat"
data_sel = types_to_prefix[train_type]+data_sel
# User specifies the stations
with col11:
    valid_abschnitte = (
        trains_df.groupby("abschnitt")[data_sel]
        .filter(lambda x: x.notna().all())
        .index
    )
    selected_sections = st.multiselect(
        "Abschnitte auswählen",
        options=sorted(trains_df.loc[valid_abschnitte, "abschnitt"].unique()),
    )
filtered = trains_df[trains_df["abschnitt"].isin(selected_sections)].copy()
plot_args = {
    "x": "bezugsmonat",
    "y": "zuege_total",
    "markers": True
}
if metric == metrics[0]:
    compare_months = (
        filtered
        .groupby(["bezugsmonat", "abschnitt"])
        .agg(zuege_total=(data_sel, "sum"))
    ).reset_index()
    plot_args["color"] = "abschnitt"
else:
    compare_months = (
        filtered
        .groupby("bezugsmonat")
        .agg(zuege_total = (data_sel, metric.lower()))
    ).reset_index()
# Make plot
fig = px.line(compare_months, **plot_args)
st.plotly_chart(fig, width="stretch")

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


# Create map of all routes
st.subheader("Map of train routes")
st.write("This map contains the mean monthly traffic from the selected year")
# Auswählen zwischen dtv, dtv_p oder dtv_g
col11, col12 = st.columns(2)
# User specifies the year
with col11:
    selected_year = st.selectbox(
        "Jahr auswählen",
        options=[2024, 2025],
        key="year_select_map"
    )
train_types = ["All types", "Passenger trains", "Freight trains"]
types_to_prefix = {"All types":"dtv_", "Passenger trains":"dtv_p_", "Freight trains":"dtv_g_"}
with col12:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_map"
    )
data_sel = "bezugsmonat" if selected_year == 2025 else "vorjahresmonat"
data_sel = types_to_prefix[train_type]+data_sel
map_trains = draw_map(trains_df, data_sel=data_sel)
st_folium(map_trains, width=700)

#-----------------------------------
# input new data into the dataframe
#-----------------------------------

# return true if the bezeichnung is valid
def validate_strecke_bezeichnung(strecke_bezeichnung):
    if(len(strecke_bezeichnung)<2):
        return False, "Streckenbezeichnung muss mindestens 2 Buchstaben haben."
    if('.' in strecke_bezeichnung):
        return False, "Streckenbezeichnung darf keine Sonderzeichen enthalten." 
    return True, ""

#return true if it is a valid abschnitt
def validate_abschnitt(station_from, station_to):
    if station_from == station_to:
        return False, "Anfangs- und Endstation müssen verschieden sein."
    return True, ""

@st.dialog("New Train Line Added")
def success_dialog():
    st.write("Success! The new row was added to the dataframe.")
    last_row = trains_df.tail(1).copy()
    last_row["verbindung"] = last_row["verbindung"].astype(str)
    st.dataframe(last_row)
    if st.button('OK'):
        st.rerun()

st.subheader("Input Additional Data")

#specify the name of the line
strecke_bezeichnung = st.text_input('Strecke Bezeichnung', placeholder = "Solothurn - Olten")
if strecke_bezeichnung: 
    is_valid, message = validate_strecke_bezeichnung(strecke_bezeichnung=strecke_bezeichnung)
    if not is_valid:
        st.error(message)

#first row in the form: specify the line start and endpoints
col11, col12 = st.columns(2)
with col11:
    station_from = st.selectbox("Abschnitt von", stations_df)
    station_from_row = stations_df[stations_df["station"] == station_from]

with col12:
    station_to = st.selectbox("Abschnitt bis", stations_df)
    station_to_row = stations_df[stations_df["station"] == station_to]

if station_from and station_to:
    is_valid, message = validate_abschnitt(station_from, station_to)
    if not is_valid:
        st.error(message)

#second row in the form: month
monat = int(st.selectbox("Monat", list(range(1, 13))))

col31, col32 = st.columns(2)
#third row in the form: number of trains
with col31:
    dtv_p = st.number_input('Anzahl Personenverkehrszüge', min_value = 0)
with col32:
    dtv_g = st.number_input('Anzahl Güterverkehrszüge', min_value = 0)

#fourth row in the form: number of trains in the year before
hat_vorjahresmonat = st.checkbox("Vorjahresdaten vorhanden")
col41, col42 = st.columns(2)
with col41:
    dtv_p_vorjahr = st.number_input('Anzahl Personenerkehrszüge im Vorjahresmonat', min_value = 0, disabled = not hat_vorjahresmonat)
with col42:
    dtv_g_vorjahr = st.number_input('Anzahl Güterverkehrszüge im Vorjahresmonat', min_value = 0, disabled = not hat_vorjahresmonat)


if st.button("Submit"):
    #validate all fields
    validations = [
        validate_strecke_bezeichnung(strecke_bezeichnung),
        validate_abschnitt(station_from, station_to),
    ]
    if all(v[0] for v in validations):

        bezugsmonat = monat

        if(hat_vorjahresmonat):
            dtv_vorjahr = dtv_p_vorjahr + dtv_g_vorjahr
        else:
            dtv_p_vorjahr = pd.NA
            dtv_g_vorjahr = pd.NA
            dtv_vorjahr = pd.NA

        #arrays with the coordinates
        station_to_coordinates = [float(station_to_row.iloc[0]["longitude"]), float(station_to_row.iloc[0]["latitude"])]
        station_from_coordinates = [float(station_from_row.iloc[0]["longitude"]), float(station_from_row.iloc[0]["latitude"])]

        new_row = {"strecke_bezeichnung": strecke_bezeichnung,
                "abschnitt": "{} – {}".format(station_from, station_to),
                "abschnitt_von": station_from_row.iloc[0]["label"],
                "abschnitt_bis": station_to_row.iloc[0]["label"],
                "bezugsmonat": bezugsmonat,
                "dtv_bezugsmonat": dtv_p + dtv_g,
                "dtv_p_bezugsmonat": dtv_p,
                "dtv_g_bezugsmonat": dtv_g,
                "dtv_vorjahresmonat": dtv_vorjahr,
                "dtv_p_vorjahresmonat": dtv_p_vorjahr,
                "dtv_g_vorjahresmonat": dtv_g_vorjahr,
                "hat_vorjahresmonat": hat_vorjahresmonat,
                "verbindung": json.dumps({
                    "coordinates": [station_from_coordinates, station_to_coordinates], 
                    "type": "LineString"
                    })
                }
        
        trains_df = pd.concat([trains_df, pd.DataFrame([new_row])], ignore_index = True)
        trains_df = trains_df.convert_dtypes()
        st.session_state.trains_df = trains_df
        success_dialog()
    else:
        #show all error messages
        for valid, message in validations:
            if not valid:
                st.error(message)
