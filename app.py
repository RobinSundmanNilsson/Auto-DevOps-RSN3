import requests as req
import pandas as pd
from datetime import datetime

# Default coordinates (Stockholm)
latitude = 59.3293
longitude = 18.0686


# ========== SMHI ==========
def get_smhi_data(lat=latitude, lon=longitude):
    smhi_api_url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

    try:
        smhi_weather_data = req.get(smhi_api_url, timeout=10)
        smhi_weather_data.raise_for_status()
    except req.exceptions.RequestException as e:
        return None, f"SMHI API request failed: {e}"
    
    try:
        data = smhi_weather_data.json()
        return data, "Success"
    except ValueError:
        return None, "Invalid JSON from SMHI"


def process_smhi_data(smhi_weather_forecast, lat, lon):
    forecast_data_smhi = []
    current_time = datetime.now()
    hours_collected = 0

    for data in smhi_weather_forecast.get("timeSeries", []):
        valid_time = data.get("validTime")
        if not valid_time:
            continue

        forecast_datetime = datetime.fromisoformat(valid_time[:-1])

        if forecast_datetime < current_time:
            continue
        if hours_collected >= 48:
            break

        forecast_date, forecast_hour = valid_time.split("T")
        parameters = {param["name"]: param["values"] for param in data.get("parameters", [])}

        forecast_temp = parameters.get("t", [None])[0]
        forecast_rain_or_snow = parameters.get("pcat", [None])[0]
        rain_or_snow_bool = True if forecast_rain_or_snow and forecast_rain_or_snow > 0 else False

        forecast_data_smhi.append({
            "Created": current_time,
            "Latitude": lat,
            "Longitude": lon,
            "Date": forecast_date,
            "Hour": forecast_hour[:5],
            "Temperature (°C)": round(forecast_temp),
            "Rain or Snow": rain_or_snow_bool,
            "Provider": "SMHI"
        })
        hours_collected += 1

    df = pd.DataFrame(forecast_data_smhi)
    return df, "Success"


def collect_smhi_data(lat=latitude, lon=longitude):
    smhi_data, get_status = get_smhi_data(lat, lon)
    if smhi_data is None:
        return None, get_status

    df_smhi, process_status = process_smhi_data(smhi_data, lat, lon)
    if df_smhi is None:
        return None, process_status

    return df_smhi, "Success"