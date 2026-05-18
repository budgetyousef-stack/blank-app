import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="Marine Tracker PRO", page_icon="⚓", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0F172A; }
    h1 { color: #38BDF8; text-align: center; font-family: 'Cairo', sans-serif; font-weight: bold; }
    .report-card { background-color: #1E293B; padding: 22px; border-radius: 18px; border: 1px solid #334155; margin-top: 15px; }
    .success-text { color: #10B981; font-weight: bold; font-size: 16px; }
    .warning-text { color: #F59E0B; font-weight: bold; font-size: 16px; }
    .danger-text { color: #EF4444; font-weight: bold; font-size: 16px; }
    .stButton>button { background-color: #0284C7; color: white; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚓ MARINE TRACKER PRO")
st.markdown("<p style='text-align: center; color: #64748B;'>تطبيق الملاحة وتحليل نشاط السمك الذكي</p>", unsafe_allow_html=True)

MAP_START_LAT = 26.85
MAP_START_LON = 49.80

st.subheader("🗺️ خريطة الصيد التفاعلية:")
st.info("💡 قم بتكبير الخريطة واضغط على أي مكان في البحر لتحديده فوراً.")

m = folium.Map(location=[MAP_START_LAT, MAP_START_LON], zoom_start=8, control_scale=True)
m.add_child(folium.LatLngPopup())

map_data = st_folium(m, height=450, width=700)

clicked_lat = None
clicked_lon = None
