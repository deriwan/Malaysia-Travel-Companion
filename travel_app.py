import streamlit as st
import requests
import plotly.express as px

st.set_page_config(page_title="Smart Malaysia Travel Companion", layout="wide")

# ======================= Konfigurasi API =========================
IPINFO_API_KEY = "5616c393bcf417"
WEATHER_API_KEY = "15aee72fdd4a19cc0c56ea7607bf6af1"

# ======================= Fungsi Utiliti ==========================
def get_location_by_ip():
    try:
        res = requests.get(f"https://ipinfo.io/json?token={IPINFO_API_KEY}")
        data = res.json()
        loc = data.get("loc", "0,0").split(",")
        return {
            "city": data.get("city", "Unknown"),
            "lat": float(loc[0]),
            "lon": float(loc[1])
        }
    except:
        return {"city": "Unknown", "lat": 0.0, "lon": 0.0}

def get_weather_forecast(lat, lon):
    try:
        url = (
            f"https://api.openweathermap.org/data/3.0/onecall?"
            f"lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={WEATHER_API_KEY}"
        )
        res = requests.get(url)
        data = res.json()

        if "current" not in data:
            st.error(f"Gagal dapatkan data cuaca: {data.get('message', 'Tiada data')}")
            st.stop()

        return data
    except Exception as e:
        st.error(f"Ralat API: {str(e)}")
        st.stop()

# ======================= Antaramuka Streamlit ====================
st.markdown("""
    <h1 style='text-align: center; color: white;'>🌴 Smart Malaysia Travel Companion</h1>
    <p style='text-align: center;'>Your real-time travel assistant with local weather forecast.</p>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("📍 Pilih Lokasi")
    auto_loc = st.checkbox("Guna Lokasi Automatik")

    location = {}
    if auto_loc:
        location = get_location_by_ip()
        st.success(f"Lokasi anda: {location['city']}")
    else:
        city_coords = {
            "Kuala Lumpur": (3.139, 101.6869),
            "Penang": (5.4141, 100.3288),
            "Johor Bahru": (1.4927, 103.7414),
            "Kota Kinabalu": (5.9804, 116.0735),
            "Kuching": (1.5533, 110.3592)
        }
        city = st.selectbox("Pilih Bandar", list(city_coords.keys()))
        lat, lon = city_coords[city]
        location = {"city": city, "lat": lat, "lon": lon}

# ======================= Dapatkan Data Cuaca =====================
st.success(f"Lokasi: *{location['city']}* ({location['lat']}, {location['lon']})")
forecast = get_weather_forecast(location['lat'], location['lon'])

# DEBUGGING: Uncomment untuk lihat response
# st.write(forecast)

# ======================= Paparan Data ============================
current = forecast["current"]
daily = forecast["daily"]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🌡️ Suhu Sekarang", f"{current['temp']}°C")
with col2:
    st.metric("💧 Kelembapan", f"{current['humidity']}%")
with col3:
    st.metric("🌬️ Angin", f"{current['wind_speed']} m/s")

# ======================= Carta Ramalan Harian ====================
import datetime

hari = [datetime.datetime.fromtimestamp(day['dt']).strftime('%A') for day in daily]
suhu_maks = [day['temp']['max'] for day in daily]
suhu_min = [day['temp']['min'] for day in daily]

fig = px.line(x=hari, y=[suhu_maks, suhu_min], labels={'x': 'Hari', 'value': 'Suhu (°C)'},
              title="Ramalan Suhu Harian", template="plotly_dark")
fig.update_layout(
    legend_title_text='Suhu',
    legend=dict(itemsizing='constant', items=["Max", "Min"]),
    xaxis_title="Hari",
    yaxis_title="Suhu (°C)",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# ======================= Nota Tambahan ===========================
st.caption("Dikuasakan oleh OpenWeather & IPInfo APIs. 🇲🇾")
