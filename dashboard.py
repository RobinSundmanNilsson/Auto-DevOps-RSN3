import streamlit as st
import pandas as pd
from app import collect_smhi_data, load_saved_data

st.set_page_config(page_title="SMHI Weather Forecast", page_icon="🌦️", layout="wide")
st.title("🌦️ SMHI Weather Forecast Dashboard")

st.write("Fetch and view 48-hour weather forecast from **SMHI** API.")

# Coordinates section
st.sidebar.header("Location Settings")
latitude = st.sidebar.number_input("Latitude", value=59.309965, format="%.6f")
longitude = st.sidebar.number_input("Longitude", value=18.021515, format="%.6f")

# Fetch data
if st.button("Fetch SMHI Weather Data"):
    df_smhi, msg = collect_smhi_data(lat=latitude, lon=longitude)
    if df_smhi is not None:
        st.success("✅ SMHI forecast fetched successfully")
        st.dataframe(df_smhi)
    else:
        st.error(msg)

st.divider()
st.header("📂 View Saved Forecasts")

if st.button("Show Saved SMHI Data"):
    df = load_saved_data("smhi")
    if df is not None:
        st.dataframe(df)
    else:
        st.warning("No saved SMHI forecast found.")