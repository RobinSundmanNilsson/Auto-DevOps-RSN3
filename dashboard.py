import streamlit as st
import pandas as pd
from app import collect_smhi_data
import plotly.express as px

st.set_page_config(page_title="SMHI Weather Forecast", page_icon="🌦️", layout="wide")
st.title("🌦️ SMHI Weather Forecast Dashboard")

st.write("Se den senaste 48-timmarsprognosen från **SMHI**.")

# ---------------- Sidebar ----------------

st.sidebar.header("Plats")

cities = [
    ("Stockholm",   59.3293, 18.0686),
    ("Göteborg",    57.7089, 11.9746),
    ("Malmö",       55.6050, 13.0038),
    ("Uppsala",     59.8586, 17.6389),
    ("Västerås",    59.6099, 16.5448),
    ("Örebro",      59.2741, 15.2066),
    ("Linköping",   58.4109, 15.6216),
    ("Helsingborg", 56.0465, 12.6945),
    ("Jönköping",   57.7826, 14.1618),
    ("Norrköping",  58.5877, 16.1924),
]

city_names = [c[0] for c in cities]
selected_city = st.sidebar.selectbox("Välj stad (topp 10)", city_names, index=0)

city_lat, city_lon = next((lat, lon) for name, lat, lon in cities if name == selected_city)

latitude = city_lat
longitude = city_lon

# ---------------- Hämta data ----------------

with st.spinner("Hämtar prognos från SMHI..."):
    df_smhi, msg = collect_smhi_data(lat=latitude, lon=longitude)

if df_smhi is None:
    st.error(msg)
    st.stop()

st.success(f" Prognos hämtad för {selected_city} ({latitude:.4f}, {longitude:.4f})")

df_smhi["Datetime"] = pd.to_datetime(df_smhi["Date"] + " " + df_smhi["Hour"])
df_smhi = df_smhi.sort_values("Datetime")

df_48 = df_smhi.head(48)
df_24 = df_48.head(24)

# ---------------- Temperaturtrend 48h ----------------

st.subheader(f"{selected_city} - Temperaturtrend kommande 48h")

fig = px.line(
    df_48,
    x="Datetime",
    y="Temperature (°C)",
    markers=True,
    title=None,
)

fig.update_traces(
    hovertemplate="%{x|%b %d, %H:%M}<br>%{y:.0f}°C"
)

fig.update_layout(
    template="plotly_white",
    height=350,
    margin=dict(l=20, r=20, t=40, b=20),
)

fig.update_xaxes(title_text="Date & Time")
fig.update_yaxes(title_text="Temp. (°C)")

st.plotly_chart(fig, width="stretch")

# ---------------- Nyckelvärden 24h ----------------

st.subheader("Nyckelvärden kommande 24h")

if not df_24.empty:
    col1, col2, col3, col4 = st.columns(4)

    current_temp = df_24.iloc[0]["Temperature (°C)"]
    max_temp_24 = df_24["Temperature (°C)"].max()
    min_temp_24 = df_24["Temperature (°C)"].min()

    precip_24 = df_24[df_24["Rain or Snow"] == True]

    col1.metric("Nuvarande temp", f"{current_temp:.0f} °C")
    col2.metric("Max (24h)", f"{max_temp_24:.0f} °C")
    col3.metric("Min (24h)", f"{min_temp_24:.0f} °C")

    if precip_24.empty:
        precip_value = "0 h"
        precip_delta = "ingen nederbörd"
    else:
        hours_with_precip = len(precip_24)
        first_precip_time = precip_24.iloc[0]["Datetime"]

        precip_value = f"{hours_with_precip} h"
        precip_delta = f"start {first_precip_time:%H:%M}"

    col4.metric("Nederbörd (24h)", precip_value, precip_delta)

else:
    st.info("Ingen 24h-prognos tillgänglig.")

# ---------------- Rådata ----------------

st.subheader("Rådata från SMHI")

with st.expander("Visa tabell"):
    st.dataframe(df_smhi, width="stretch")