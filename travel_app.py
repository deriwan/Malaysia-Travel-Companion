import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# ============ API KEYS ============
WEATHER_API_KEY = "15aee72fdd4a19cc0c56ea7607bf6af1"
LOCATION_API_KEY = "5616c393bcf417"

# ============ GET LOCATION ============
def get_location_by_ip():
    try:
        res = requests.get(f"https://ipinfo.io/json?token={LOCATION_API_KEY}")
        data = res.json()
        loc = data.get("loc")
        city = data.get("city")
        if not loc or not city:
            raise Exception("Invalid IPInfo data")
        lat, lon = map(float, loc.split(","))
        return {"city": city, "latitude": lat, "longitude": lon}
    except:
        return {"city": "Kuala Lumpur", "latitude": 3.1390, "longitude": 101.6869}

# ============ GET WEATHER ============
def get_weather_forecast(lat, lon):
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/onecall?"
            f"lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={WEATHER_API_KEY}"
        )
        res = requests.get(url)
        data = res.json()
        return data
    except:
        return None

# ============ PAGE SETUP ============
st.set_page_config(page_title="Smart Malaysia Travel Companion", layout="centered")
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f9ff;
    }
    .big-font {
        font-size: 24px !important;
    }
    .weather-box {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("🌴 Smart Malaysia Travel Companion")
st.markdown("Your real-time travel assistant with local weather forecast.")

# ============ SIDEBAR LOCATION ============
city_list = {
    "Kuala Lumpur": (3.1390, 101.6869),
    "George Town": (5.4141, 100.3288),
    "Johor Bahru": (1.4927, 103.7414),
    "Shah Alam": (3.0738, 101.5183),
    "Ipoh": (4.5975, 101.0901),
    "Kuantan": (3.8046, 103.3256),
    "Malacca": (2.1896, 102.2501),
    "Alor Setar": (6.1248, 100.3677),
    "Kota Bharu": (6.1254, 102.2381),
    "Kota Kinabalu": (5.9804, 116.0735),
    "Kuching": (1.5533, 110.3592),
    "Seremban": (2.7297, 101.9381)
}

st.sidebar.subheader("📍 Pilih Lokasi")
use_auto = st.sidebar.checkbox("Guna Lokasi Automatik", value=True)

if use_auto:
    location = get_location_by_ip()
    city = location["city"]
    lat, lon = location["latitude"], location["longitude"]
else:
    city = st.sidebar.selectbox("Pilih Bandar", list(city_list.keys()))
    lat, lon = city_list[city]

st.success(f"Lokasi: *{city}* ({lat}, {lon})")

# ============ FETCH WEATHER ============
forecast = get_weather_forecast(lat, lon)

if forecast:
    current = forecast["current"]
    daily = forecast["daily"]

    st.markdown("### ☁️ Cuaca Terkini")
    st.markdown(
        f"""
        <div class="weather-box">
        <h3>{city}</h3>
        <p class="big-font">🌡️ {current['temp']}°C</p>
        <p>{current['weather'][0]['description'].title()}</p>
        <p>💧 Kelembapan: {current['humidity']}% | 💨 Angin: {current['wind_speed']} m/s</p>
        </div>
        """, unsafe_allow_html=True
    )

    # ============ GRAPH ============
    st.markdown("### 📊 Ramalan Suhu Mingguan")

    dates = []
    temps = []
    icons = []

    for day in daily[:7]:
        dt = datetime.fromtimestamp(day["dt"]).strftime("%A")
        temp = day["temp"]["day"]
        icon = day["weather"][0]["icon"]
        dates.append(dt)
        temps.append(temp)
        icons.append(icon)

    df = pd.DataFrame({
        "Hari": dates,
        "Suhu (°C)": temps
    })

    fig = px.bar(df, x="Hari", y="Suhu (°C)", color="Suhu (°C)",
                 color_continuous_scale="Blues", height=400)
    st.plotly_chart(fig)

else:
    st.error("Gagal dapatkan data cuaca.")
