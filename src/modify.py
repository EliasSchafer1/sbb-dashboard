import streamlit as st
import pandas as pd
import json
from data_store import get_stations_df, get_trains_df
from layout import sbb_header
import calendar

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

def save_to_session(trains_df, new_row, mask=None):
    if mask is not None:
        trains_df = trains_df[~mask]
    trains_df = pd.concat([trains_df, pd.DataFrame([new_row])], ignore_index=True)
    trains_df = trains_df.convert_dtypes()
    trains_df["reference_month"] = pd.Categorical(trains_df["reference_month"], categories=month_names, ordered=True)
    st.session_state.trains_df = trains_df
    return trains_df

#display a success dialog when the new data was entered into the df
@st.dialog("Route Section Saved")
def success_dialog(trains_df):
    st.write("Success! The route section was saved to the dataframe.")
    last_row = trains_df.tail(1).copy()
    last_row["connection"] = last_row["connection"].astype(str)
    st.dataframe(last_row)
    if st.button("OK"):
        st.rerun()



#---------------------------------------
# display the fields to enter the data
#---------------------------------------

st.subheader("Add a new route section")
st.caption("Input is per month: average number of daily trains within the selected month.")

# First row in the form: specify the section start and endpoints
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

# Second row in the form: month
month_names = list(calendar.month_name)[1:]  # ['January', 'February', ...]
reference_month = st.selectbox("Month", month_names)
month_num = list(calendar.month_name).index(reference_month)

col31, col32 = st.columns(2)
# Third row in the form: number of trains
with col31:
    daily_passenger_trains = st.number_input('Passenger Trains (2025)', min_value = 0)
with col32:
    daily_freight_trains = st.number_input('Freight Trains (2025)', min_value = 0)

#fourth row in the form: number of trains in the year before
has_previous_year_month = st.checkbox("Previous Year Data Available")
col41, col42 = st.columns(2)
with col41:
    daily_passenger_trains_py = st.number_input('Passenger Trains (2024)', min_value = 0, disabled = not has_previous_year_month)
with col42:
    daily_freight_trains_py = st.number_input('Freight Trains (2024)', min_value = 0, disabled = not has_previous_year_month)


#-------------------------------------------------------------------
# submit process + add to dataframe (should be split up probably)
#--------------------------------------------------------------------

if "pending_row" not in st.session_state:
    st.session_state.pending_row = None

if "pending_row" not in st.session_state:
    st.session_state.pending_row = None

if st.button("Submit"):
    validations = [validate_section(station_from, station_to)]
    if all(v[0] for v in validations):
        # Check for duplicates
        duplicate_mask = (
            (trains_df["section"] == "{} – {}".format(station_from, station_to)) &
            (trains_df["reference_month"] == reference_month)
        )
        is_duplicate = duplicate_mask.any()

        if has_previous_year_month:
            daily_trains_py = daily_passenger_trains_py + daily_freight_trains_py
        elif is_duplicate:
            py_vals = trains_df.loc[duplicate_mask, ["daily_trains_py", "daily_passenger_trains_py", "daily_freight_trains_py"]].iloc[0]
            daily_trains_py, daily_passenger_trains_py, daily_freight_trains_py = py_vals
        else:
            daily_trains_py = daily_passenger_trains_py = daily_freight_trains_py = pd.NA

        station_from_coordinates = [float(station_from_row.iloc[0]["longitude"]), float(station_from_row.iloc[0]["latitude"])]
        station_to_coordinates = [float(station_to_row.iloc[0]["longitude"]), float(station_to_row.iloc[0]["latitude"])]

        new_row = {
            "section": "{} – {}".format(station_from, station_to),
            "section_from": station_from_row.iloc[0]["label"],
            "section_to": station_to_row.iloc[0]["label"],
            "reference_month": reference_month,
            "month_num": month_num,
            "daily_trains": daily_passenger_trains + daily_freight_trains,
            "daily_passenger_trains": daily_passenger_trains,
            "daily_freight_trains": daily_freight_trains,
            "daily_trains_py": daily_trains_py,
            "daily_passenger_trains_py": daily_passenger_trains_py,
            "daily_freight_trains_py": daily_freight_trains_py,
            "connection": json.dumps({
                "coordinates": [station_from_coordinates, station_to_coordinates],
                "type": "LineString"
            })
        }

        if is_duplicate:
            st.session_state.pending_row = {"row": new_row, "mask": duplicate_mask}
        else:
            trains_df = save_to_session(trains_df, new_row)
            success_dialog(trains_df)
    else:
        for valid, message in validations:
            if not valid:
                st.error(message)

# Overwrite confirmation
@st.dialog("Duplicate Entry")
def confirm_overwrite_dialog(trains_df):
    new_row = st.session_state.pending_row["row"]
    mask = st.session_state.pending_row["mask"]
    st.warning(f"An entry for this route section in {new_row['reference_month']} already exists. Do you want to overwrite it?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Overwrite"):
            trains_df = save_to_session(trains_df, new_row, mask)
            st.session_state.pending_row = None
            st.session_state.show_success = True
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.session_state.pending_row = None
            st.rerun()

if st.session_state.pending_row is not None:
    confirm_overwrite_dialog(trains_df)

if st.session_state.get("show_success"):
    st.session_state.show_success = False
    success_dialog(trains_df)