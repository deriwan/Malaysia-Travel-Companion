import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ✅ API Keys (yang kau bagi)
WEATHER_API_KEY = '15aee72fdd4a19cc0c56ea7607bf6af1'
LOCATION_API_KEY = '5616c393bcf417'

def get_location_by_ip():
    try:
        res = requests.get("https://ipinfo.io/json?token=" + LOCATION_API_KEY)
        data = res.json()
        loc = data.get("loc", "3.1390,101.6869")  # fallback KL
        lat, lon = map(float, loc.split(","))
        return {
            "city": data.get("city", "Kuala Lumpur"),
            "latitude": lat,
            "longitude": lon
        }
    except Exception as e:
        print("Error getting location:", e)
        return None

def get_weather_data(city):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},MY&limit=1&appid={WEATHER_API_KEY}"
        geo_res = requests.get(geo_url).json()
        if not geo_res:
            return None
        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

        weather_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=metric&exclude=minutely,hourly,alerts&appid={WEATHER_API_KEY}"
        weather_res = requests.get(weather_url).json()

        current = weather_res["current"]
        daily = weather_res["daily"][:7]

        forecast_days = []
        forecast_temps = []

        from datetime import datetime
        for day in daily:
            dt = datetime.utcfromtimestamp(day["dt"]).strftime("%a")
            forecast_days.append(dt)
            forecast_temps.append(day["temp"]["day"])

        return {
            "current_temp": round(current["temp"], 1),
            "description": current["weather"][0]["description"],
            "forecast_days": forecast_days,
            "forecast_temps": forecast_temps
        }
    except Exception as e:
        print("Error getting weather data:", e)
        return None

# ---------- UI Starts Here ----------
st.set_page_config(page_title="Smart Malaysia Travel Companion", layout="wide")
st.title("🇲🇾 Smart Malaysia Travel Companion")
st.markdown("Welcome to your intelligent travel assistant for exploring Malaysia!")

location_data = get_location_by_ip()
if location_data:
    city = location_data.get("city", "Kuala Lumpur")
    lat = location_data.get("latitude", 3.139)
    lon = location_data.get("longitude", 101.6869)
else:
    st.warning("Could not detect your location. Defaulting to Kuala Lumpur.")
    city = "Kuala Lumpur"
    lat, lon = 3.139, 101.6869

st.subheader(f"📍 Current Location: {city}")
m = folium.Map(location=[lat, lon], zoom_start=12)
folium.Marker([lat, lon], tooltip="You are here").add_to(m)
st_data = st_folium(m, width=700, height=400)

weather_data = get_weather_data(city)
if weather_data:
    st.subheader("🌦️ Current Weather & Forecast")
    st.write(f"*Temperature Now:* {weather_data['current_temp']} °C")
    st.write(f"*Condition:* {weather_data['description'].title()}")

    df = pd.DataFrame({
        "Day": weather_data["forecast_days"],
        "Temperature (°C)": weather_data["forecast_temps"]
    })
    fig = px.line(df, x="Day", y="Temperature (°C)", title="7-Day Temperature Forecast", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Failed to fetch weather data.")