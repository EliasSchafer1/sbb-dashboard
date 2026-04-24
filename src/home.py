import streamlit as st
import pandas as pd
from data_cleaning import load_data, clean_data

df = load_data()
df = clean_data(df)

st.write("Hello World")
# TODO: Add more information for the user to explore, e.g.:
st.title("SBB Trains per Route")
st.subheader("Preview")
st.dataframe(df)
st.subheader("Dataset information")
st.write("Rows:", df.shape[0])
st.write("Columns:", df.shape[1])
st.write(df.dtypes)
