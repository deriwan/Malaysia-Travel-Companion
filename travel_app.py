import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ======================= CONFIG =========================
WEATHER_API_KEY = "c5f793c96c8d51ad36c4b3be61b0fad0"
LOCATION_API_KEY = "5616c393bcf417"

# ================== LOCATION DETECTION ==================
def get_location_by_ip():
    try:
        res = requests.get(f"https://ipinfo.io/json?token={LOCATION_API_KEY}")
        data = res.json()
        loc = data.get("loc")
        city = data.get("city")

        if not loc or not city:
            raise Exception("Invalid IPInfo data")

        lat, lon = map(float, loc.split(","))
        return {
            "city": city,
            "latitude": lat,
            "longitude": lon
        }
    except Exception as e:
        print("Location error:", e)
        return {
            "city": "Kuala Lumpur",
            "latitude": 3.1390,
            "longitude": 101.6869
        }

# ==================== WEATHER DATA ======================
def get_weather_data(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={city}"
        f"&appid={WEATHER_API_KEY}&units=metric"
    )
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return None

# =================== STREAMLIT UI ========================
st.set_page_config(page_title="Smart Malaysia Travel Companion", layout="wide")
st.title("🇲🇾 Smart Malaysia Travel Companion")
st.write("Dapatkan maklumat lokasi & cuaca semasa anda di Malaysia!")

# Sidebar - Location
city_options = [
    "Kuala Lumpur", "George Town", "Johor Bahru", "Shah Alam",
    "Ipoh", "Kuantan", "Malacca", "Alor Setar", "Kota Bharu",
    "Kota Kinabalu", "Kuching", "Seremban"
]

st.sidebar.subheader("📌 Pilih Lokasi")
use_auto = st.sidebar.checkbox("Guna lokasi automatik", value=True)

if use_auto:
    loc = get_location_by_ip()
    city = loc["city"]
    lat = loc["latitude"]
    lon = loc["longitude"]
    st.success(f"Guna lokasi automatik: *{city}*")
else:
    city = st.sidebar.selectbox("Pilih bandar", city_options)
    # optional: set manual lat/lon via dict
    city_coords = {
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
    lat, lon = city_coords.get(city, (3.1390, 101.6869))
    st.info(f"Guna lokasi manual: *{city}*")

# Fetch weather
weather = get_weather_data(city)

# Show Weather Info
if weather:
    st.subheader(f"🌤️ Cuaca Terkini di {city}")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Suhu", f"{weather['main']['temp']}°C")
        st.metric("Kelembapan", f"{weather['main']['humidity']}%")

    with col2:
        st.metric("Tekanan Udara", f"{weather['main']['pressure']} hPa")
        st.metric("Keadaan", weather['weather'][0]['description'].title())

    # Map
    st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))

else:
    st.error("⚠️ Gagal dapatkan data cuaca. Cuba lagi nanti.")

# Weather Graph (optional simulation)
st.subheader("📊 Simulasi Ramalan Cuaca Mingguan (Contoh)")
dummy_data = pd.DataFrame({
    "Hari": ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"],
    "Suhu (°C)": [30, 32, 31, 29, 33, 34, 30]
})
fig = px.line(dummy_data, x="Hari", y="Suhu (°C)", markers=True)
st.plotly_chart(fig)
