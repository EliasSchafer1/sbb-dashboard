import streamlit as st

#import the font style (similar to sbb)
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


#define pages
home = st.Page("home.py", title="Home", icon="🚂")
explore = st.Page("explore.py", title="Explore", icon="🚝" )
modify = st.Page("modify.py", title="Modify", icon="🚝" )

pg = st.navigation([home, explore, modify],
    position = "top")
pg.run()