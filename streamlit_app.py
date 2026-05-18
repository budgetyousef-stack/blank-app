import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

# إعدادات الصفحة الأساسية للتطبيق
st.set_page_config(page_title="Marine Tracker PRO", page_icon="⚓", layout="centered")

# تصميم واجهة عصرية متناسقة (Dark Mode)
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

# إعداد الخريطة التفاعلية والتركيز الافتراضي على ساحل المنطقة الشرقية
MAP_START_LAT = 26.85
MAP_START_LON = 49.80

st.subheader("🗺️ خريطة الصيد التفاعلية:")
st.info("💡 قم بتكبير الخريطة واضغط على أي مكان في البحر لتحديده فوراً.")

m = folium.Map(location=[MAP_START_LAT, MAP_START_LON], zoom_start=8, control_scale=True)
m.add_child(folium.LatLngPopup())

map_data = st_folium(m, height=450, width=700)

clicked_lat = None
clicked_lon = None

if map_data and map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]

if clicked_lat and clicked_lon:
    st.success(f"📍 تم التقاط الإحداثية بنجاح! | Lat: {clicked_lat:.4f} | Lon: {clicked_lon:.4f}")
    
    w_url = "https://api.open-meteo.com/v1/forecast"
    m_url = "https://marine-api.open-meteo.com/v1/marine"
    
    w_payload = {"latitude": clicked_lat, "longitude": clicked_lon, "hourly": "temperature_2m,windspeed_10m", "forecast_days": 1}
    m_payload = {"latitude": clicked_lat, "longitude": clicked_lon, "hourly": "wave_height", "forecast_days": 1}

    try:
        w_res = requests.get(w_url, params=w_payload).json()["hourly"]
        m_res = requests.get(m_url, params=m_payload).json()["hourly"]
        
        current_hour = datetime.now().hour
        
        temp_now = w_res["temperature_2m"][current_hour]
        wind_now = w_res["windspeed_10m"][current_hour]
        wave_now = m_res["wave_height"][current_hour]
        
        best_hours = []
        for i in range(current_hour, min(current_hour + 12, 24)):
            if w_res["windspeed_10m"][i] <= 15 and m_res["wave_height"][i] <= 0.6:
                dt = datetime.strptime(w_res["time"][i], "%Y-%m-%dT%H:%M")
                best_hours.append(dt.strftime("%I:%00 %p"))

        if wind_now < 12 and wave_now < 0.4:
            fish_status = "Very High (90%) - ممتاز جداً"
            fish_class = "success-text"
            fish_advice = "السمك في قمة نشاطه وقريب من السطح! وقت مثالي للمجرور (Trolling) والكاستنج الشاطئي."
            advice = "الوضع ممتاز جداً: بحر سياح، الموج ساكن والهوا ركود في هذه الإحداثية."
            status_class = "success-text"
        elif wind_now < 18 and wave_now < 0.7:
            fish_status = "Medium (60%) - متوسط"
            fish_class = "warning-text"
            fish_advice = "نشاط السمك متوسط بسبب حركة الموج الخفيفة. ينصح بالصيد في القاع بالحية أو الميد."
            advice = "الوضع جيد: حركة موج خفيفة (يوش) في الموقع، الصيد مقدور عليه وجلب مناسب."
            status_class = "warning-text"
        else:
            fish_status = "Low (20%) - ضعيف"
            fish_class = "danger-text"
            fish_advice = "بسبب خبطة البحر والرياح، السمك رابض في القاع وواقف عن الأكل تماماً."
            advice = "بحر ضربة في هذه المنطقة: الموج عالي والهوا تارس. لا ينصح بالنزول سلامتك أهم! ⚠️"
            status_class = "danger-text"

        st.markdown(f"""
            <div class="report-card">
                <h4 style="color: #38BDF8; margin-top:0; text-align:right;">📊 التقرير البحري للموقع المحدد:</h4>
                <p style="text-align:right;">🌡️ <b>درجة الحرارة الحالية:</b> {temp_now} °C</p>
                <p style="text-align:right;">💨 <b>سرعة الرياح الحالية:</b> {wind_now} كم/ساعة</p>
                <p style="text-align:right;">🌊 <b>ارتفاع الموج الحالي:</b> {wave_now} متر</p>
                <p style="text-align:right;">💡 <b>حالة البحر العامة:</b> <span class="{status_class}">{advice}</span></p>
                <hr style="border-color: #334155;">
                <h4 style="color: #10B981; text-align:right; margin-bottom:10px;">🐟 توقعات نشاط السمك (Fish Activity):</h4>
                <p style="text-align:right;">📈 <b>مؤشر نشاط الضرب:</b> <span class="{fish_class}">{fish_status}</span></p>
                <p style="text-align:right;">🎣 <b>نصيحة الحداق:</b> {fish_advice}</p>
                <hr style="border-color: #334155;">
                <p style="text-align:right;">⏱️ <b>أفضل الساعات القادمة للمحادق في هذا الموقع:</b></p>
                <p style="color: #E2E8F0; font-size: 18px; text-align:center;"><b>» {', '.join(best_hours[:4]) if best_hours else 'لا توجد فترات مثالية حالياً'} «</b></p>
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error("حدث خطأ أثناء سحب البيانات. تأكد من الضغط على نقطة داخل البحر.")
