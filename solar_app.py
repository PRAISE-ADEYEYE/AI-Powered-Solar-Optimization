import matplotlib.pyplot as plt
import numpy as np
import requests
import streamlit as st


# Function to get weather data from OpenWeatherMap API
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"] != 200:
        st.error(f"Error fetching data: {data['message']}")
        return None
    temp = data["main"]["temp"]
    irr = data["clouds"]["all"]  # Using clouds data for simplicity; you can use irradiance if available
    return temp, irr


# Function to calculate energy output using real-time weather data
def predict_energy_output(temp, irradiance, tilt, panel_eff):
    base_output = irradiance * panel_eff * np.cos(np.radians(90 - tilt))
    temp_loss = max(0, (temp - 25) * 0.005)
    adjusted_output = base_output * (1 - temp_loss)
    return round(adjusted_output / 1000, 2)  # kWh


# UI Setup
st.set_page_config(page_title="SolarIQ - Solar Optimization", layout="wide")
st.title("☀️ SolarIQ: AI-Powered Solar Optimization")

# Sidebar Inputs
st.sidebar.header("📋 Enter Your Details")
api_key = "ef6d7708983ac168642092b48053c983"  # Replace with your own API key

city = st.sidebar.text_input("📍 Location", "Lagos")
panel_type = st.sidebar.selectbox("🔋 Panel Type", ["Monocrystalline", "Polycrystalline", "Thin-Film"])
panel_eff = {"Monocrystalline": 0.22, "Polycrystalline": 0.18, "Thin-Film": 0.12}[panel_type]

tilt_angle = st.sidebar.slider("📐 Tilt Angle (°)", 0, 90, 30)
budget = st.sidebar.number_input("💵 Budget (₦)", 100000, 5000000, 1000000, step=100000)

# Get real-time weather data
weather_data = get_weather_data(city, api_key)
if weather_data:
    temperature, cloud_cover = weather_data

    # Display the fetched weather data
    st.subheader(f"Current Weather in {city}")
    st.write(f"🌡️ Temperature: {temperature}°C")
    st.write(f"☁️ Cloud Cover: {cloud_cover}%")

    # Prediction based on live data
    predicted_energy = predict_energy_output(temperature, cloud_cover, tilt_angle, panel_eff)

    # Calculating savings and payback time
    savings = predicted_energy * 100  # ₦100 per kWh assumed
    payback_time = round(budget / (savings * 365 + 1), 1)

    col1, col2, col3 = st.columns(3)
    col1.metric("⚡ Estimated Daily Output", f"{predicted_energy} kWh")
    col2.metric("💸 Daily Savings", f"₦{int(savings)}")
    col3.metric("📆 Estimated Payback Time", f"{payback_time} years")

    # Graph: Predicted Output over Months
    st.markdown("### 📈 Predicted Monthly Output (kWh)")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    seasonal_factor = np.array([0.9, 1.0, 1.1, 1.1, 1.2, 1.0, 0.9, 0.95, 1.05, 1.1, 1.0, 0.9])
    monthly_output = seasonal_factor * predicted_energy * 30

    fig, ax = plt.subplots()
    ax.bar(months, monthly_output, color='orange')
    ax.set_ylabel("Energy (kWh)")
    ax.set_title("Predicted Solar Output per Month")
    st.pyplot(fig)

    # Maintenance Schedule (dummy example)
    st.markdown("### 🛠️ Solar Panel Maintenance")
    maintenance_reminder = f"Recommended to clean your panels every 6 months."
    st.write(maintenance_reminder)

    # Footer with source info
    st.markdown("---")
    st.markdown("Built by Praise Adeyeye with ❤️ using Python + Streamlit | Data from OpenWeatherMap | Powered by AI ☀️")
    st.markdown(
        "👨‍💻 [Connect on LinkedIn](https://www.linkedin.com/in/praise-adeyeye/) | 🌍 [Deployed on Streamlit Cloud]("
        "https://streamlit.io)")

else:
    st.error("Couldn't fetch weather data. Please check your location or API key.")
