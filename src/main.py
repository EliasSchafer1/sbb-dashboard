import streamlit as st
from data_store import get_stations_df, get_trains_df

# set page layout before any other Streamlit output
st.set_page_config(layout="wide")

#import the font style (similar to sbb)
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#define pages
home = st.Page("overview.py", title="Overview", icon="🚂")
explore = st.Page("explore.py", title="Explore", icon="🚝" )
modify = st.Page("modify.py", title="Modify", icon="🚝" )

trains_df = get_trains_df()
stations_df = get_stations_df()

#start the navigation
pg = st.navigation([home, explore, modify],
    position = "top")
pg.run()