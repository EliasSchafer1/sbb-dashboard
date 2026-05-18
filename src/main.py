import streamlit as st
from data_cleaning import load_data, clean_data
from preprocessing import extract_stations_df

#import the font style (similar to sbb)
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#define pages
home = st.Page("home.py", title="Home", icon="🚂")
explore = st.Page("explore.py", title="Explore", icon="🚝" )
modify = st.Page("modify.py", title="Modify", icon="🚝" )

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

#start the navigation
pg = st.navigation([home, explore, modify],
    position = "top")
pg.run()