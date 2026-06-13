import streamlit as st

from data_cleaning import clean_data, load_data
from preprocessing import extract_stations_df


def get_trains_df():
    if "trains_df" not in st.session_state:
        st.session_state.trains_df = clean_data(load_data())
    return st.session_state.trains_df


def get_stations_df():
    if "stations_df" not in st.session_state:
        st.session_state.stations_df = extract_stations_df(
            trains_df=get_trains_df()
        )
    return st.session_state.stations_df