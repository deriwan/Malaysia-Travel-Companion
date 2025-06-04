import streamlit as st
import requests
import plotly.graph_objects as go
import datetime

st.set_page_config(page_title="Smart Malaysia Travel Companion", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #1E1E1E;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌴 Smart Malaysia Travel Companion</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your real-time travel assistant with local weather forecast.</p>", unsafe_allow_html=True)

# ============ SETTINGS ============
API_KEY = "15aee72fdd4a19cc0c56ea7607bf6af1"
DEFAULT_CITY = "Kuala Lumpur"
CITY_OPTIONS = [
    "Kuala Lumpur", "George Town", "Johor Bahru", "Kota Kinabalu", "Kuching",
    "Shah Alam", "Malacca", "Ipoh", "Alor Setar", "Seremban"
]

# ============ SIDEBAR ============
st.sidebar.header("📍 Pilih Lokasi")
use_auto = st.sidebar.checkbox("Guna Lokasi Automatik")

if use_auto:
    try:
        ipinfo_token = "5616c393bcf417"
        ipinfo_url = f"https://ipinfo.io/json?token={ipinfo_token}"
        ip_data = requests.get(ipinfo_url).json()
        city = ip_data.get("city", DEFAULT_CITY)
        loc = ip_data.get("loc", "3.139,101.6869")
    except:
        st.error("Gagal kesan lokasi automatik. Guna pilihan manual.")
        city = st.sidebar.selectbox("Pilih Bandar", CITY_OPTIONS, index=0)
        loc = "3.139,101.6869"
else:
    city = st.sidebar.selectbox("Pilih Bandar", CITY_OPTIONS, index=0)
    loc = "3.139,101.6869"  # fallback if auto not used

st.success(f"Lokasi: *{city}* ({loc})")

# ============ API REQUEST ============
def get_weather(city_name):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={API_KEY}"
    return requests.get(url).json()

def get_forecast(city_name):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&units=metric&appid={API_KEY}"
    return requests.get(url).json()

weather_data = get_weather(city)
forecast_data = get_forecast(city)

# ============ CURRENT WEATHER ============
if weather_data and "main" in weather_data:
    st.subheader("☁️ Cuaca Semasa")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Suhu", f"{weather_data['main']['temp']} °C")
        st.metric("Kelembapan", f"{weather_data['main']['humidity']}%")
    with col2:
        st.metric("Angin", f"{weather_data['wind']['speed']} m/s")
        st.metric("Keadaan", weather_data['weather'][0]['description'].title())
else:
    st.error("❌ Gagal mengambil data cuaca semasa.")

# ============ FORECAST CHART ============
def parse_daily_forecast(forecast):
    forecast_list = forecast.get("list", [])
    daily = {}
    for item in forecast_list:
        dt = datetime.datetime.fromtimestamp(item['dt'])
        if dt.hour == 12:
            date = dt.date()
            daily[str(date)] = item['main']['temp']
    return daily

daily_forecast = parse_daily_forecast(forecast_data)

if daily_forecast:
    st.subheader("📊 Simulasi Ramalan Cuaca Mingguan")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(daily_forecast.keys()),
        y=list(daily_forecast.values()),
        mode='lines+markers',
        name='Suhu (°C)',
        line=dict(color='deepskyblue', width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Tarikh",
        yaxis_title="Suhu (°C)",
        title="Ramalan Suhu Harian untuk 5 Hari",
        plot_bgcolor='#222',
        paper_bgcolor='#111',
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Tiada data ramalan tersedia.")
