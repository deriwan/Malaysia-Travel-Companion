import streamlit as st
import requests
import plotly.graph_objects as go
import datetime
import folium
from streamlit_folium import folium_static
from PIL import Image
import io

# ============ SETTINGS ============
st.set_page_config(page_title="Smart Malaysia Travel Companion", layout="wide", page_icon="🌴")

# Custom CSS for vibrant UI
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .sidebar .sidebar-content {
        background-color: #1A1C23;
    }
    h1 {
        color: #4F8BF9;
    }
    h2 {
        color: #FF4B4B;
    }
    .st-bb {
        background-color: transparent;
    }
    .st-at {
        background-color: #2D3746;
    }
    .stMetric {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ HEADER ============
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Flag_of_Malaysia.svg/1200px-Flag_of_Malaysia.svg.png", 
             width=100)
with col2:
    st.markdown("<h1 style='text-align: left;'>🌴 Smart Malaysia Travel Companion</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left; color: #A9A9A9;'>Your real-time travel assistant with weather forecast and interactive map</p>", unsafe_allow_html=True)

# ============ API KEYS ============
API_KEY = "15aee72fdd4a19cc0c56ea7607bf6af1"  # Free tier OpenWeatherMap
CITY_OPTIONS = [
    "Kuala Lumpur", "George Town", "Johor Bahru", "Kota Kinabalu", "Kuching",
    "Shah Alam", "Malacca", "Ipoh", "Alor Setar", "Seremban"
]

# City coordinates mapping (for map)
CITY_COORDS = {
    "Kuala Lumpur": (3.1390, 101.6869),
    "George Town": (5.4141, 100.3288),
    "Ipoh": (4.5975, 101.0901),
    "Shah Alam": (3.0733, 101.5185),
    "Seremban": (2.7259, 101.9424),
    "Malacca": (2.1896, 102.2501),
    "Johor Bahru": (1.4927, 103.7414),
    "Kuantan": (3.8077, 103.3260),
    "Kuala Terengganu": (5.3296, 103.1370),
    "Kota Bharu": (6.1256, 102.2432),
    "Alor Setar": (6.1214, 100.3695),
    "Kangar": (6.4414, 100.1986),
    "Kota Kinabalu": (5.9804, 116.0735),
    "Kuching": (1.5397, 110.3542),
    "Putrajaya": (2.9264, 101.6964),
    "Labuan": (5.2767, 115.2417)
}

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🗺️ Location Settings")
    use_auto = st.checkbox("Auto-detect my location", help="Uses your IP address to estimate location")
    
    if use_auto:
        try:
            ipinfo_token = "5616c393bcf417"  # Free tier token
            ipinfo_url = f"https://ipinfo.io/json?token={ipinfo_token}"
            ip_data = requests.get(ipinfo_url).json()
            city = ip_data.get("city", DEFAULT_CITY)
            if city not in CITY_OPTIONS:
                city = "Kuala Lumpur"
            st.success(f"Detected location: {city}")
        except:
            st.error("Auto-detection failed. Please select manually.")
            city = st.selectbox("Select City", CITY_OPTIONS, index=0)
    else:
        city = st.selectbox("Select City", CITY_OPTIONS, index=0)
    
    st.markdown("---")
    st.markdown("### 🌦️ Weather Settings")
    temp_unit = st.radio("Temperature Unit", ["°C", "°F"])
    st.markdown("---")
    st.markdown("### 📊 Display Options")
    show_map = st.checkbox("Show Interactive Map", value=True)
    show_forecast = st.checkbox("Show 5-Day Forecast", value=True)

# ============ WEATHER FUNCTIONS ============
def get_weather(city_name, unit='metric'):
    unit_param = 'metric' if unit == '°C' else 'imperial'
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units={unit_param}&appid={API_KEY}"
    return requests.get(url).json()

def get_forecast(city_name, unit='metric'):
    unit_param = 'metric' if unit == '°C' else 'imperial'
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&units={unit_param}&appid={API_KEY}"
    return requests.get(url).json()

def get_weather_icon(icon_code):
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

# ============ MAIN CONTENT ============
try:
    weather_data = get_weather(city, temp_unit)
    forecast_data = get_forecast(city, temp_unit)
    
    # ============ CURRENT WEATHER ============
    st.markdown(f"## ⛅ Current Weather in {city}")
    
    if weather_data and "main" in weather_data:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            st.markdown("### 🌡️ Temperature")
            temp = weather_data['main']['temp']
            st.markdown(f"<h1 style='color: #FF4B4B;'>{temp} {temp_unit}</h1>", unsafe_allow_html=True)
            st.markdown(f"Feels like: {weather_data['main']['feels_like']} {temp_unit}")
            
        with col2:
            st.markdown("### 📊 Conditions")
            weather_desc = weather_data['weather'][0]['description'].title()
            icon_code = weather_data['weather'][0]['icon']
            st.image(get_weather_icon(icon_code), width=70)
            st.markdown(f"**{weather_desc}**")
            st.markdown(f"Humidity: {weather_data['main']['humidity']}%")
            
        with col3:
            st.markdown("### 💨 Wind & Visibility")
            wind_speed = weather_data['wind']['speed']
            wind_dir = weather_data['wind'].get('deg', 'N/A')
            st.markdown(f"**Wind:** {wind_speed} {'m/s' if temp_unit == '°C' else 'mph'} ({wind_dir}°)")
            visibility = weather_data.get('visibility', 'N/A')
            if visibility != 'N/A':
                visibility = f"{visibility/1000} km" if temp_unit == '°C' else f"{visibility/1609:.1f} miles"
            st.markdown(f"**Visibility:** {visibility}")
            pressure = weather_data['main']['pressure']
            st.markdown(f"**Pressure:** {pressure} hPa")
    else:
        st.error("Failed to fetch current weather data")
    
    # ============ INTERACTIVE MAP ============
    if show_map and city in CITY_COORDS:
        st.markdown("## 🗺️ Interactive Map")
        map_center = CITY_COORDS[city]
        m = folium.Map(location=map_center, zoom_start=12)
        
        # Add marker for the city
        folium.Marker(
            location=map_center,
            popup=f"Weather in {city}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add circle for visibility (if available)
        if weather_data and 'visibility' in weather_data and weather_data['visibility'] != 'N/A':
            folium.Circle(
                location=map_center,
                radius=weather_data['visibility'],
                color='#3186cc',
                fill=True,
                fill_color='#3186cc'
            ).add_to(m)
        
        folium_static(m, width=900, height=400)
    
    # ============ FORECAST CHART ============
    if show_forecast:
        st.markdown("## 📆 5-Day Weather Forecast")
        
        if forecast_data and 'list' in forecast_data:
            # Process forecast data
            forecast_days = {}
            for item in forecast_data['list']:
                date = datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                if date not in forecast_days:
                    forecast_days[date] = {
                        'temps': [],
                        'icons': [],
                        'descriptions': []
                    }
                forecast_days[date]['temps'].append(item['main']['temp'])
                forecast_days[date]['icons'].append(item['weather'][0]['icon'])
                forecast_days[date]['descriptions'].append(item['weather'][0]['description'])
            
            # Calculate daily averages
            dates = []
            avg_temps = []
            icons = []
            descriptions = []
            
            for date, data in forecast_days.items():
                dates.append(date)
                avg_temps.append(round(sum(data['temps'])/len(data['temps']), 1))
                # Get most frequent icon/description for the day
                icons.append(max(set(data['icons']), key=data['icons'].count))
                descriptions.append(max(set(data['descriptions']), key=data['descriptions'].count))
            
            # Create forecast chart
            fig = go.Figure()
            
            # Temperature line
            fig.add_trace(go.Scatter(
                x=dates,
                y=avg_temps,
                mode='lines+markers',
                name='Temperature',
                line=dict(color='#FF7043', width=3),
                marker=dict(size=10, color='#FF7043'),
                hovertemplate='%{y}' + temp_unit
            ))
            
            # Weather icons
            for i, (date, icon) in enumerate(zip(dates, icons)):
                fig.add_layout_image(
                    dict(
                        source=get_weather_icon(icon),
                        xref="x",
                        yref="y",
                        x=date,
                        y=max(avg_temps) + (max(avg_temps)-min(avg_temps))*0.2,
                        sizex=0.8,
                        sizey=0.8,
                        xanchor="center",
                        yanchor="middle"
                    )
                )
            
            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title=f"Temperature ({temp_unit})",
                hovermode="x unified",
                plot_bgcolor='#1E293B',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast details in columns
            st.markdown("### Daily Forecast Details")
            cols = st.columns(len(dates))
            for i, col in enumerate(cols):
                with col:
                    st.markdown(f"**{dates[i]}**")
                    st.image(get_weather_icon(icons[i]), width=50)
                    st.markdown(f"**{avg_temps[i]} {temp_unit}**")
                    st.markdown(f"{descriptions[i].title()}")
        else:
            st.warning("Forecast data not available")
            
except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #A9A9A9;">
        <p>Smart Malaysia Travel Companion • Data from OpenWeatherMap</p>
        <p>Map data © OpenStreetMap contributors</p>
    </div>
""", unsafe_allow_html=True)
