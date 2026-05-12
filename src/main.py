import streamlit as st

#define pages
home = st.Page("home.py", title="Home", icon="🚂")
explore = st.Page("explore.py", title="Explore", icon="🚝" )
modify = st.Page("modify.py", title="Modify", icon="🚝" )

pg = st.navigation([home, explore, modify])
pg.run()