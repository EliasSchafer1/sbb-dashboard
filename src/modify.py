import streamlit as st
import pandas as pd
import json
from data_store import get_stations_df, get_trains_df
from layout import sbb_header

trains_df = get_trains_df()
stations_df = get_stations_df()

#display sbb header
sbb_header("Modify the Dataframe")

#-------------------------
#   helper methods
#-------------------------

#return true if it is a valid section
def validate_section(station_from, station_to):
    if station_from == station_to:
        return False, "Start and end stations must be different."
    return True, ""

#display a success dialog when the new data was entered into the df
@st.dialog("New Route Section Added")
def success_dialog():
    st.write("Success! The new route section was added to the dataframe.")
    last_row = trains_df.tail(1).copy()
    last_row["connection"] = last_row["connection"].astype(str)
    st.dataframe(last_row)
    if st.button('OK'):
        st.rerun()



#---------------------------------------
# display the fields to enter the data
#---------------------------------------

#header
st.subheader("Add a new route section to the dataframe")

#first row in the form: specify the section start and endpoints
col11, col12 = st.columns(2)
with col11:
    station_from = st.selectbox("Section from", stations_df)
    station_from_row = stations_df[stations_df["station"] == station_from]

with col12:
    station_to = st.selectbox("Section to", stations_df)
    station_to_row = stations_df[stations_df["station"] == station_to]

if station_from and station_to:
    is_valid, message = validate_section(station_from, station_to)
    if not is_valid:
        st.error(message)

#second row in the form: month
month_num = int(st.selectbox("Month", list(range(1, 13))))

month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
reference_month = month_names[month_num - 1]

col31, col32 = st.columns(2)
#third row in the form: number of trains
with col31:
    dtv_p = st.number_input('Number of Passenger Trains', min_value = 0)
with col32:
    dtv_g = st.number_input('Number of Freight Trains', min_value = 0)

#fourth row in the form: number of trains in the year before
has_previous_year_month = st.checkbox("Previous Year Data Available")
col41, col42 = st.columns(2)
with col41:
    dtv_p_previous_year = st.number_input('Number of Passenger Trains in Previous Year Month', min_value = 0, disabled = not has_previous_year_month)
with col42:
    dtv_g_previous_year = st.number_input('Number of Freight Trains in Previous Year Month', min_value = 0, disabled = not has_previous_year_month)


#-------------------------------------------------------------------
# submit process + add to dataframe (should be split up probably)
#--------------------------------------------------------------------

if st.button("Submit"):
    #validate all fields
    validations = [
        validate_section(station_from, station_to),
    ]
    if all(v[0] for v in validations):

        if(has_previous_year_month):
            dtv_previous_year = dtv_p_previous_year + dtv_g_previous_year
        else:
            dtv_p_previous_year = pd.NA
            dtv_g_previous_year = pd.NA
            dtv_previous_year = pd.NA

        #arrays with the coordinates
        station_to_coordinates = [float(station_to_row.iloc[0]["longitude"]), float(station_to_row.iloc[0]["latitude"])]
        station_from_coordinates = [float(station_from_row.iloc[0]["longitude"]), float(station_from_row.iloc[0]["latitude"])]

        new_row = {"section": "{} – {}".format(station_from, station_to),
                "section_from": station_from_row.iloc[0]["label"],
                "section_to": station_to_row.iloc[0]["label"],
                "reference_month": reference_month,
                "month_num": month_num,
                "dtv_reference_month": dtv_p + dtv_g,
                "dtv_p_reference_month": dtv_p,
                "dtv_g_reference_month": dtv_g,
                "dtv_previous_year_month": dtv_previous_year,
                "dtv_p_previous_year_month": dtv_p_previous_year,
                "dtv_g_previous_year_month": dtv_g_previous_year,
                "has_previous_year_month": has_previous_year_month,
                "connection": json.dumps({
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