import streamlit as st
import requests
import folium
import pandas as pd
from streamlit_folium import st_folium
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Marine Tracker",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }
    .stApp { background-color: #0F172A; }

    /* Header */
    .main-title {
        color: #38BDF8;
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 0;
        font-family: 'Cairo', sans-serif;
    }
    .sub-title {
        color: #64748B;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 6px;
        font-family: 'Cairo', sans-serif;
    }
    .divider {
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #38BDF8, #0ea5e9);
        border-radius: 4px;
        margin: 0 auto 32px auto;
    }

    /* Cards */
    .card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .card-title {
        color: #38BDF8;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 16px;
        font-family: 'Cairo', sans-serif;
    }

    /* Metric boxes */
    .metric-row { display: flex; gap: 12px; margin-bottom: 16px; }
    .metric-box {
        flex: 1;
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
    }
    .metric-icon { font-size: 1.8rem; margin-bottom: 4px; }
    .metric-value { font-size: 1.3rem; font-weight: 700; color: #F1F5F9; }
    .metric-label { font-size: 0.75rem; color: #64748B; margin-top: 2px; }

    /* Status badges */
    .badge-excellent { background: #10B981; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
    .badge-good      { background: #F59E0B; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
    .badge-bad       { background: #EF4444; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }

    /* Activity level bar */
    .activity-bar-wrap { background: #0F172A; border-radius: 8px; height: 14px; overflow: hidden; margin: 8px 0 4px 0; }
    .activity-bar-fill { height: 100%; border-radius: 8px; transition: width 0.6s; }
    .activity-labels { display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748B; }

    /* Best hours chips */
    .hour-chip {
        display: inline-block;
        background: #0ea5e9;
        color: #0F172A;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px 4px 3px 0;
    }

    /* Advice text */
    .advice-excellent { color: #10B981; font-weight: 600; font-size: 0.97rem; line-height: 1.8; font-family: 'Cairo', sans-serif; }
    .advice-good      { color: #F59E0B; font-weight: 600; font-size: 0.97rem; line-height: 1.8; font-family: 'Cairo', sans-serif; }
    .advice-bad       { color: #EF4444; font-weight: 600; font-size: 0.97rem; line-height: 1.8; font-family: 'Cairo', sans-serif; }

    /* Factor boxes */
    .factor-row { display: flex; gap: 10px; margin-top: 14px; }
    .factor-box {
        flex: 1;
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 10px 8px;
        text-align: center;
    }
    .factor-label { font-size: 0.7rem; color: #64748B; margin-top: 4px; }

    /* Day cards in forecast */
    .day-cards { display: flex; gap: 8px; margin-top: 14px; }
    .day-card {
        flex: 1;
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 8px 4px;
        text-align: center;
        font-size: 0.78rem;
        color: #CBD5E1;
    }
    .day-card-name { font-weight: 700; margin-bottom: 4px; }

    /* Footer */
    .footer { text-align: center; color: #334155; font-size: 0.75rem; margin-top: 32px; padding-bottom: 24px; }

    /* Streamlit overrides */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0ea5e9, #38BDF8) !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px !important;
        font-family: 'Cairo', sans-serif !important;
    }
    .stButton > button:hover { opacity: 0.9 !important; }
    </style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────

DAYS_AR = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
MAP_START_LAT = 26.85
MAP_START_LON = 49.80

# ─── Fish Activity Model ──────────────────────────────────────────────────────

def fish_activity_score(wind: float, wave: float, temp: float) -> dict:
    score = 100

    # Wind penalty
    if wind <= 10:
        wind_status, wind_label = "#10B981", "مثالي"
    elif wind <= 18:
        score -= 20
        wind_status, wind_label = "#F59E0B", "مقبول"
    elif wind <= 25:
        score -= 45
        wind_status, wind_label = "#F97316", "مرتفع"
    else:
        score -= 70
        wind_status, wind_label = "#EF4444", "شديد"

    # Wave penalty
    if wave <= 0.3:
        wave_status, wave_label = "#10B981", "هادئ"
    elif wave <= 0.6:
        score -= 15
        wave_status, wave_label = "#F59E0B", "خفيف"
    elif wave <= 1.0:
        score -= 35
        wave_status, wave_label = "#F97316", "متوسط"
    else:
        score -= 60
        wave_status, wave_label = "#EF4444", "عالي"

    # Temperature bonus/penalty
    if 22 <= temp <= 30:
        temp_status, temp_label = "#10B981", "مثالية"
    elif 18 <= temp < 22 or 30 < temp <= 36:
        score -= 10
        temp_status, temp_label = "#F59E0B", "مقبولة"
    else:
        score -= 20
        temp_status, temp_label = "#EF4444", "قاسية"

    score = max(0, min(100, score))

    if score >= 65:
        level  = "high"
        label  = "نشاط عالي 🎣"
        color  = "#10B981"
        advice = "ظروف مثالية — الأسماك نشيطة وقريبة من السطح. أنسب وقت للمحادق وصيد السيف!"
    elif score >= 35:
        level  = "medium"
        label  = "نشاط متوسط 🐟"
        color  = "#F59E0B"
        advice = "ظروف مقبولة — الأسماك نشيطة جزئياً. الصيد ممكن مع بعض الصبر."
    else:
        level  = "low"
        label  = "نشاط منخفض ⚠️"
        color  = "#EF4444"
        advice = "ظروف صعبة — الأسماك في الأعماق والبحر غير مناسب. يُفضل الانتظار."

    return {
        "level": level, "label": label, "color": color,
        "score": score, "bar_pct": score, "advice": advice,
        "wind_status": wind_status, "wind_label": wind_label,
        "wave_status": wave_status, "wave_label": wave_label,
        "temp_status": temp_status, "temp_label": temp_label,
    }

# ─── API Fetch ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float):
    w_url = "https://api.open-meteo.com/v1/forecast"
    m_url = "https://marine-api.open-meteo.com/v1/marine"

    w_params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,windspeed_10m",
        "daily": "windspeed_10m_max,temperature_2m_max",
        "forecast_days": 7, "timezone": "Asia/Riyadh",
    }
    m_params = {
        "latitude": lat, "longitude": lon,
        "hourly": "wave_height",
        "daily": "wave_height_max",
        "forecast_days": 7, "timezone": "Asia/Riyadh",
    }

    w_res = requests.get(w_url, params=w_params, timeout=10).json()
    m_res = requests.get(m_url, params=m_params, timeout=10).json()
    return w_res, m_res

# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown('<h1 class="main-title">🌊 MARINE TRACKER</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">المرشد البحري الذكي لرحلات الصيد</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─── Layout: two columns ──────────────────────────────────────────────────────

col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ خريطة الصيد التفاعلية</div>', unsafe_allow_html=True)
    st.info("💡 قم بتكبير الخريطة بيدك واضغط على أي موقع في البحر لوضع الدبوس وتحليله فوراً.")
    
    # بناء الخريطة الحرة المستقرة
    m = folium.Map(
        location=[MAP_START_LAT, MAP_START_LON],
        zoom_start=9,
        tiles="CartoDB dark_matter",
        width="100%"
    )
    m.add_child(folium.LatLngPopup())
    
    # التحقق من الموقع المختار ووضع الدبوس والمربع الشفاف حوله
    map_data = st_folium(m, height=450, use_container_width=True, key="marine_map")
    
    clicked_lat = None
    clicked_lon = None
    
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]
        
        # إعادة بناء الخريطة لإظهار الدبوس والمربع فوراً عند النقر
        m2 = folium.Map(location=[clicked_lat, clicked_lon], zoom_start=10, tiles="CartoDB dark_matter")
        
        # وضع الدبوس (Pin)
        folium.Marker(
            location=[clicked_lat, clicked_lon],
            icon=folium.Icon(color="blue", icon="anchor", prefix="fa")
        ).add_to(m2)
        
        # وضع نطاق مربع التحديد الشفاف (Circle Area)
        folium.Circle(
            location=[clicked_lat, clicked_lon],
            radius=4000,
            color="#38BDF8",
            fill=True,
            fill_color="#38BDF8",
            fill_opacity=0.12,
            weight=2
        ).add_to(m2)
        
        # تحديث العرض بالدبوس الجديد
        st.experimental_rerun if not st.session_state.get("data_loaded") else None
        
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if clicked_lat and clicked_lon:
        try:
            with st.spinner("جاري التقاط الإحداثيات وتحليل الطقس البحري..."):
                w_res, m_res = fetch_weather(clicked_lat, clicked_lon)

            hourly_w = w_res["hourly"]
            hourly_m = m_res["hourly"]
            current_hour = datetime.now().hour

            temp_now = hourly_w["temperature_2m"][current_hour]
            wind_now = hourly_w["windspeed_10m"][current_hour]
            wave_now = hourly_m["wave_height"][current_hour]

            best_hours = []
            for i in range(current_hour, min(current_hour + 12, 24)):
                if hourly_w["windspeed_10m"][i] <= 15 and hourly_m["wave_height"][i] <= 0.6:
                    h = i % 12 or 12
                    period = "ص" if i < 12 else "م"
                    best_hours.append(f"{h}:00 {period}")

            if wind_now < 14 and wave_now < 0.5:
                status, badge, advice_text = "excellent", "badge-excellent", (
                    "الوضع ممتاز جداً: بحر سياح، الموج ساكن والهوا ركود في هذه الإحداثية. "
                    "أنسب وقت للمحادق وصيد السيف! 🎣"
                )
            elif wind_now < 20 and wave_now < 0.8:
                status, badge, advice_text = "good", "badge-good", (
                    "الوضع جيد: جلب مناسب، حركة موج خفيفة (يوش) في الموقع "
                    "لكن الصيد مقدور عليه وبإذن الله توفق. 👍"
                )
            else:
                status, badge, advice_text = "bad", "badge-bad", (
                    "الوضع صعب: ضربة بحر في هذه المنطقة، الموج عالي والهوا تارس. "
                    "يُنصح بعدم النزول لسلامتك. ⛔"
                )

            status_ar = {"excellent": "ممتاز", "good": "جيد", "bad": "محظور"}

            # ── Current conditions card ───────────────────────────────────
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">'
                f'<div class="card-title" style="margin-bottom:0">📊 تقرير الإحداثية الحالية</div>'
                f'<span class="{badge}">{status_ar[status]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="color:#64748B; font-size:0.85rem; margin-top:-10px; margin-bottom:14px;">'
                f'Lat: {clicked_lat:.4f} | Lon: {clicked_lon:.4f}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metric-row">'
                f'<div class="metric-box"><div class="metric-icon">🌡️</div>'
                f'<div class="metric-value">{temp_now:.0f}°م</div>'
                f'<div class="metric-label">الحرارة</div></div>'
                f'<div class="metric-box"><div class="metric-icon">💨</div>'
                f'<div class="metric-value">{wind_now:.0f} كم/س</div>'
                f'<div class="metric-label">الرياح</div></div>'
                f'<div class="metric-box"><div class="metric-icon">🌊</div>'
                f'<div class="metric-value">{wave_now:.1f} م</div>'
                f'<div class="metric-label">الموج</div></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown(f'<p class="advice-{status}">{advice_text}</p>', unsafe_allow_html=True)
            
            if best_hours:
                chips = "".join(f'<span class="hour-chip">{h}</span>' for h in best_hours)
                st.markdown(
                    f'<div style="border-top:1px solid #334155;padding-top:12px;margin-top:8px">'
                    f'<div style="color:#94A3B8;font-size:0.82rem;margin-bottom:6px">أفضل ساعات الصيد اليوم في هذا الموقع:</div>'
                    f'{chips}</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Fish Activity Prediction card ─────────────────────────────
            act = fish_activity_score(wind_now, wave_now, temp_now)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🐠 توقع نشاط الأسماك وحالة الضرب</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="text-align:center;padding:12px;background:rgba(255,255,255,0.04);'
                f'border-radius:12px;border:2px solid {act["color"]};margin-bottom:12px">'
                f'<div style="font-size:1.4rem;font-weight:800;color:{act["color"]}">{act["label"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="activity-labels"><span>منخفض</span><span>متوسط</span><span>عالي</span></div>'
                f'<div class="activity-bar-wrap">'
                f'<div class="activity-bar-fill" style="width:{act["bar_pct"]}%;'
                f'background:linear-gradient(90deg,#10B981,{act["color"]})"></div>'
                f'</div>'
                f'<div style="text-align:left;font-size:0.7rem;color:#64748B;margin-bottom:10px">'
                f'مؤشر النشاط: {act["score"]}/100</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:12px;'
                f'font-size:0.92rem;color:#CBD5E1;line-height:1.8;font-family:Cairo,sans-serif;">'
                f'{act["advice"]}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="factor-row">'
                f'<div class="factor-box">'
                f'<div style="font-weight:700;color:{act["wind_status"]}">{act["wind_label"]}</div>'
                f'<div class="factor-label">الرياح</div></div>'
                f'<div class="factor-box">'
                f'<div style="font-weight:700;color:{act["wave_status"]}">{act["wave_label"]}</div>'
                f'<div class="factor-label">الموج</div></div>'
                f'<div class="factor-box">'
                f'<div style="font-weight:700;color:{act["temp_status"]}">{act["temp_label"]}</div>'
                f'<div class="factor-label">الحرارة</div></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # ── 7-Day Forecast Chart ──────────────────────────────────────
            daily_wind = w_res["daily"]["windspeed_10m_max"]
            daily_temp = w_res["daily"]["temperature_2m_max"]
            daily_wave = m_res["daily"]["wave_height_max"]

            today = datetime.now()
            days_labels = []
            for i in range(7):
                d = today + timedelta(days=i)
                days_labels.append(DAYS_AR[d.weekday() % 7] if i > 0 else "اليوم")

            chart_df = pd.DataFrame({
                "اليوم":          days_labels,
                "الرياح (كم/س)":  [round(v, 1) for v in daily_wind],
                "الأمواج (م)":    [round(v, 2) for v in daily_wave],
                "الحرارة (°م)":   [round(v, 1) for v in daily_temp],
            }).set_index("اليوم")

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📈 توقعات السبعة أيام القادمة لهذه المنطقة</div>', unsafe_allow_html=True)
            st.line_chart(chart_df, height=210, use_container_width=True, color=["#38BDF8", "#10B981", "#F59E0B"])
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("حدث خطأ أثناء سحب بيانات الطقس البحري. تأكد من تحديد نقطة داخل نطاق البحر.")
    else:
        st.markdown(
            '<div class="card" style="text-align:center;padding:78px 24px">'
            '<div style="font-size:3.5rem;margin-bottom:12px">⚓</div>'
            '<div style="color:#64748B;font-size:1.05rem;font-family:Cairo,sans-serif">'
            'يرجى الضغط على أي مكان في البحر على الخريطة لعرض التقارير والتحليلات مباشرة'
            '</div></div>',
            unsafe_allow_html=True
        )

st.markdown('<div class="footer">Marine Tracker PRO — بيانات الطقس متصلة بـ Open-Meteo API</div>', unsafe_allow_html=True)
