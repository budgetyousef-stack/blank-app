import streamlit as st
import requests
import folium
import pandas as pd
import math
import plotly.graph_objects as go
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# ─── إعدادات الصفحة ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Marine Tracker PRO",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CSS احترافي متجاوب ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700;800;900&display=swap');

*, html, body { box-sizing: border-box; }
html, body, [class*="css"], .stApp, .block-container {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
}
.stApp { background-color: #0A1628 !important; }
.block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 720px !important; }

/* إخفاء شريط Streamlit */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

/* تسمية قسم الخريطة */
.map-section-label {
    color: #38BDF8;
    font-size: clamp(0.95rem, 2.8vw, 1.1rem);
    font-weight: 800;
    text-align: right;
    margin-bottom: 8px;
    padding: 0 2px;
}

/* Force map containers to stay LTR and prevent mirroring */
.stFoliumMap, div[data-testid="stIFrame"], iframe, .leaflet-container, .leaflet-pane, .leaflet-tile-pane, .leaflet-tile {
    direction: ltr !important;
    text-align: left !important;
    transform: none !important;
}
/* حافة ومظهر إطار الخريطة */
.stFoliumMap {
    border-radius: 14px !important;
    overflow: hidden !important;
}
iframe[title="st_folium.frontend"] {
    border-radius: 14px !important;
    border: 1px solid #1E3A5F !important;
    width: 100% !important;
}

/* بطاقة القمر */
.moon-row {
    display: flex;
    align-items: center;
    gap: 18px;
    direction: rtl;
    margin-bottom: 16px;
}
.moon-emoji-wrap {
    font-size: 3.8rem;
    line-height: 1;
    text-align: center;
    min-width: 64px;
    filter: drop-shadow(0 0 16px rgba(148,163,184,0.45));
}
.moon-info { flex: 1; text-align: right; }
.moon-phase-name {
    font-size: clamp(1rem, 3vw, 1.25rem);
    font-weight: 900;
    color: #F1F5F9;
    line-height: 1.3;
}
.moon-illum {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 4px;
}
.moon-events-row {
    display: flex;
    gap: 8px;
    direction: rtl;
    margin-bottom: 12px;
    flex-wrap: wrap;
}
.moon-event-box {
    flex: 1;
    min-width: 90px;
    background: rgba(148,163,184,0.06);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 12px;
    padding: 10px 8px;
    text-align: center;
}
.moon-event-label { font-size: 0.7rem; color: #64748B; }
.moon-event-val   { font-size: 1rem; font-weight: 800; color: #F1F5F9; margin-top: 3px; }
.moon-tip {
    background: rgba(148,163,184,0.06);
    border-right: 3px solid #94A3B8;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px 10px 10px;
    color: #CBD5E1;
    font-size: 0.88rem;
    line-height: 1.7;
    text-align: right;
}

/* العنوان الرئيسي */
.main-title {
    color: #38BDF8;
    text-align: center;
    font-size: clamp(1.6rem, 5vw, 2.4rem);
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.5px;
    text-shadow: 0 0 40px rgba(56,189,248,0.3);
}
.sub-title {
    color: #64748B;
    text-align: center;
    font-size: clamp(0.85rem, 2.5vw, 1rem);
    font-weight: 600;
    margin-top: 6px;
}
.divider {
    width: 50px; height: 4px;
    background: linear-gradient(90deg, #38BDF8, #0EA5E9);
    border-radius: 4px;
    margin: 12px auto 20px auto;
}

/* مربع الموقع */
.location-box {
    background: linear-gradient(135deg, #1E293B 0%, #0F2137 100%);
    border: 2px solid #38BDF8;
    border-radius: 14px;
    padding: 14px 18px;
    text-align: center;
    color: #F1F5F9;
    font-size: clamp(0.9rem, 2.8vw, 1.05rem);
    font-weight: 700;
    margin-bottom: 16px;
    box-shadow: 0 0 20px rgba(56,189,248,0.12);
}

/* البطاقات */
.card {
    background: linear-gradient(145deg, #1E293B 0%, #162032 100%);
    border: 1px solid #1E3A5F;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.card-title {
    color: #38BDF8;
    font-size: clamp(0.95rem, 2.8vw, 1.1rem);
    font-weight: 800;
    margin-bottom: 14px;
    text-align: right;
}

/* صف المقاييس */
.metric-row {
    display: flex;
    gap: 10px;
    margin-bottom: 14px;
    direction: rtl;
    flex-wrap: wrap;
}
.metric-box {
    flex: 1;
    min-width: 80px;
    background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 12px;
    padding: 12px 6px;
    text-align: center;
}
.metric-value {
    font-size: clamp(1rem, 3vw, 1.2rem);
    font-weight: 800;
    color: #F1F5F9;
}
.metric-label {
    font-size: clamp(0.68rem, 2vw, 0.78rem);
    color: #64748B;
    margin-top: 3px;
}

/* الشارات */
.badge-excellent { background: linear-gradient(135deg,#059669,#10B981); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:800; }
.badge-good      { background: linear-gradient(135deg,#D97706,#F59E0B); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:800; }
.badge-bad       { background: linear-gradient(135deg,#DC2626,#EF4444); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:800; }

/* شرائح ساعات الصيد */
.range-chip {
    display: inline-block;
    background: linear-gradient(135deg, #0369A1, #0EA5E9);
    color: white;
    font-weight: 800;
    font-size: clamp(0.75rem, 2.2vw, 0.85rem);
    padding: 5px 14px;
    border-radius: 22px;
    margin: 4px 0 4px 6px;
    box-shadow: 0 2px 8px rgba(14,165,233,0.35);
    white-space: nowrap;
}

/* النصائح */
.advice-excellent { color:#10B981; font-weight:700; text-align:right; font-size:0.9rem; margin-top:10px; line-height:1.6; }
.advice-good      { color:#F59E0B; font-weight:700; text-align:right; font-size:0.9rem; margin-top:10px; line-height:1.6; }
.advice-bad       { color:#EF4444; font-weight:700; text-align:right; font-size:0.9rem; margin-top:10px; line-height:1.6; }

/* صف العوامل */
.factor-row { display:flex; gap:8px; margin-top:14px; direction:rtl; flex-wrap:wrap; }
.factor-box { flex:1; min-width:70px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:10px 6px; text-align:center; }
.factor-label { font-size:0.72rem; color:#64748B; margin-top:4px; }
.factor-value { font-size:0.9rem; font-weight:800; }

/* مؤشر النشاط الدائري Premium */
.act-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px 10px 10px 10px;
}
.act-ring-inner {
    position: relative;
    width: 160px;
    height: 160px;
}
.act-ring-inner svg { transform: rotate(-90deg); }
.act-ring-center {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    pointer-events: none;
}
.act-ring-score {
    font-size: 2.4rem;
    font-weight: 900;
    color: #F1F5F9;
    line-height: 1;
}
.act-ring-label {
    font-size: 0.72rem;
    color: #64748B;
    margin-top: 4px;
}
.act-ring-stars {
    font-size: 1.1rem;
    margin-top: 10px;
    letter-spacing: 3px;
}
.act-ring-status {
    font-size: 1rem;
    font-weight: 800;
    margin-top: 6px;
}

/* مخطط نشاط ساعي */
.chart-label {
    color: #38BDF8;
    font-size: clamp(0.95rem, 2.8vw, 1.1rem);
    font-weight: 800;
    text-align: right;
    margin: 16px 0 6px 0;
}
.chart-legend {
    display: flex;
    gap: 14px;
    direction: rtl;
    margin-bottom: 6px;
    font-size: 0.75rem;
    color: #64748B;
}
.chart-legend span { display:flex; align-items:center; gap:5px; }
.chart-legend i { display:inline-block; width:12px; height:3px; border-radius:2px; }

/* أوقات الصيد السولونار */
.solunar-wrap {
    display: flex;
    gap: 12px;
    direction: rtl;
    margin-bottom: 16px;
}
.solunar-col {
    flex: 1;
    border-radius: 16px;
    padding: 16px 14px;
}
.solunar-major { background: linear-gradient(145deg, #0c2a4a, #0a1e38); border: 1px solid rgba(56,189,248,0.35); }
.solunar-minor { background: linear-gradient(145deg, #1a1f35, #111827); border: 1px solid rgba(167,139,250,0.25); }
.solunar-heading {
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
    text-align: center;
}
.solunar-major .solunar-heading { color: #38BDF8; }
.solunar-minor .solunar-heading { color: #A78BFA; }
.solunar-icon { font-size: 1.6rem; text-align: center; margin-bottom: 8px; }
.sol-chip {
    border-radius: 10px;
    padding: 9px 10px;
    margin: 7px 0;
    text-align: center;
    font-weight: 700;
    font-size: 0.88rem;
    line-height: 1.4;
}
.sol-chip-major { background: rgba(56,189,248,0.12); border: 1px solid rgba(56,189,248,0.3); color: #E0F2FE; }
.sol-chip-minor { background: rgba(167,139,250,0.10); border: 1px solid rgba(167,139,250,0.25); color: #EDE9FE; }
.sol-chip-label { font-size: 0.65rem; color: #64748B; margin-top: 3px; }

/* الاستجابة للجوال */
@media (max-width: 480px) {
    .block-container { padding: 0.6rem 0.6rem 2rem 0.6rem !important; }
    .card { padding: 14px 12px; border-radius: 14px; }
    .metric-row { gap: 6px; }
    .factor-row { gap: 6px; }
}
</style>
""", unsafe_allow_html=True)

# ─── ثوابت ────────────────────────────────────────────────────────────────────
DAYS_AR   = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
MONTHS_AR = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
             "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]

def _day_option_label(offset: int) -> str:
    d = datetime.now() + timedelta(days=offset)
    day_str = f"{d.day} {MONTHS_AR[d.month - 1]}"
    if offset == 0:
        return f"اليوم ({day_str})"
    else:
        return f"{DAYS_AR[(d.weekday() + 1) % 7]} ({day_str})"

# ─── نموذج نشاط الأسماك ───────────────────────────────────────────────────────
def fish_activity_score(wind: float, wave: float, temp: float, swell: float = 0.0) -> dict:
    score = 100
    if wind <= 10: w_status, w_label = "#10B981", "مثالي"
    elif wind <= 18: w_status, w_label = "#F59E0B", "مقبول"; score -= 20
    else: w_status, w_label = "#EF4444", "شديد"; score -= 50

    if wave <= 0.3: wv_status, wv_label = "#10B981", "هادئ"
    elif wave <= 0.7: wv_status, wv_label = "#F59E0B", "خفيف"; score -= 15
    else: wv_status, wv_label = "#EF4444", "عالي"; score -= 45

    if 22 <= temp <= 30: t_status, t_label = "#10B981", "مثالية"
    elif 18 <= temp <= 36: t_status, t_label = "#F59E0B", "مقبولة"; score -= 5
    else: t_status, t_label = "#EF4444", "قاسية"; score -= 20

    if swell > 1.5: score -= 15
    score = max(0, min(100, score))

    if score >= 65:
        level, label, color = "high", "نشاط عالي 🎣", "#10B981"
        advice = "ظروف مثالية — الأسماك نشيطة وقريبة من السطح. أنسب وقت للمحادق وصيد السيف!"
    elif score >= 35:
        level, label, color = "medium", "نشاط متوسط 🐟", "#F59E0B"
        advice = "ظروف مقبولة — الأسماك نشيطة جزئياً. الص الصيد ممكن مع بعض الصبر."
    else:
        level, label, color = "low", "نشاط منخفض ⚠️", "#EF4444"
        advice = "ظروف صعبة — الأسماك في الأعماق والبحر غير مناسب حالياً."

    return {
        "level": level, "label": label, "color": color, "score": score, "advice": advice,
        "wind_status": w_status, "wind_label": w_label,
        "wave_status": wv_status, "wave_label": wv_label,
        "temp_status": t_status, "temp_label": t_label,
    }

# ─── تجميع الساعات ───────────────────────────────────────────────────────────
def build_time_ranges(good_hours: list) -> list:
    if not good_hours: return []
    ranges = []
    start = good_hours[0]
    end = good_hours[0]
    for h in good_hours[1:]:
        if h == end + 1: end = h
        else:
            ranges.append((start, end))
            start = end = h
    ranges.append((start, end))

    chips = []
    for s, e in ranges:
        def fmt(h):
            h_wrapped = h % 24
            period = "ص" if h_wrapped < 12 else "م"
            h12 = h_wrapped % 12 or 12
            return f"{h12}:00 {period}"
        if s == e: chips.append(fmt(s))
        else: chips.append(f"{fmt(s)} — {fmt(e + 1)}")
    return chips

# ─── نموذج المد والجزر التوافقي ───────────────────────────────────────────────
def _tide_amplitudes(lat: float, lon: float) -> dict:
    结构_gulf = (23 <= lat <= 30) and (48 <= lon <= 57)
    结构_red_sea = (12 <= lat <= 28) and (32 <= lon <= 44)
    结构_oman = (22 <= lat <= 26) and (57 <= lon <= 62)

    if 结构_gulf: return dict(M2=0.90, S2=0.28, K1=0.12, O1=0.08, M4=0.06, base=1.10)
    elif 结构_red_sea: return dict(M2=0.28, S2=0.10, K1=0.18, O1=0.12, M4=0.02, base=0.45)
    elif 结构_oman: return dict(M2=0.65, S2=0.22, K1=0.20, O1=0.14, M4=0.04, base=0.80)
    else: return dict(M2=0.60, S2=0.20, K1=0.18, O1=0.12, M4=0.03, base=0.75)

def compute_tide_profile(lat: float, lon: float, for_date: datetime) -> list:
    amp = _tide_amplitudes(lat, lon)
    ref = datetime(2000, 1, 1, 0, 0, 0)
    midnight = for_date.replace(hour=0, minute=0, second=0, microsecond=0)
    t0 = (midnight - ref).total_seconds() / 3600.0

    periods = dict(M2=12.4206, S2=12.0000, K1=23.9345, O1=25.8194, M4=6.2103)
    phases  = dict(M2=0.0, S2=1.05, K1=0.80, O1=0.55, M4=2.20)

    heights = []
    for h in range(25):
        t = t0 + h
        level = amp["base"]
        for name, period in periods.items():
            omega = 2.0 * math.pi / period
            level += amp[name] * math.cos(omega * t - phases[name])
        heights.append(round(max(0.0, level), 3))
    return heights

# ─── جلب البيانات من الـ APIs ────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float):
    w_url, m_url = "https://api.open-meteo.com/v1/forecast", "https://marine-api.open-meteo.com/v1/marine"
    w_params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,apparent_temperature,windspeed_10m,winddirection_10m,windgusts_10m,precipitation_probability",
        "wind_speed_unit": "kmh", "forecast_days": 7, "timezone": "Asia/Riyadh"
    }
    m_params = {
        "latitude": lat, "longitude": lon,
        "hourly": "wave_height,wave_period,swell_wave_height,sea_surface_temperature",
        "forecast_days": 7, "timezone": "Asia/Riyadh"
    }
    try:
        return requests.get(w_url, params=w_params, timeout=12).json(), requests.get(m_url, params=m_params, timeout=12).json()
    except: return None, None

@st.cache_data(ttl=3600)
def get_location_name(lat: float, lon: float) -> str:
    try:
        res = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ar", headers={"User-Agent": "MarineTrackerPRO/2.0"}, timeout=4).json()
        addr = res.get("address", {})
        return addr.get("city") or addr.get("town") or addr.get("state") or "منطقة بحرية مفتوحة"
    except: return "منطقة بحرية"

def get_moon_phase(date: datetime) -> dict:
    synodic, ref_jdn = 29.53059, 2451549.26
    y, m, d = date.year, date.month, date.day
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    jdn = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045 + (date.hour - 12) / 24.0
    age = (jdn - ref_jdn) % synodic
    illumination = int(round((1 - math.cos(2 * math.pi * age / synodic)) / 2 * 100))
    
    if age < 1.85: emoji, phase_ar, tip = "🌑", "محاق", "أفضل وقت للصيد: المياه مظلمة والأسماك تتغذى بجرأة."
    elif age < 7.38: emoji, phase_ar, tip = "🌒", "هلال متصاعد", "نشاط جيد: الأسماك تبحث عن الغذاء."
    elif age < 9.22: emoji, phase_ar, tip = "🌓", "تربيع أول", "نشاط متوسط: المد مستقر مناسب للصيد في الأعماق."
    elif age < 14.76: emoji, phase_ar, tip = "🌔", "أحدب متصاعد", "نشاط متزايد: الأسماك تستعد لذروة نشاطها."
    elif age < 16.61: emoji, phase_ar, tip = "🌕", "بدر كامل", "ذروة النشاط 🎣: أفضل ليلة صيد! تيارات قوية."
    elif age < 22.15: emoji, phase_ar, tip = "🌖", "أحدب متناقص", "نشاط جيد: القمر لا يزال مضيئاً."
    elif age < 23.99: emoji, phase_ar, tip = "🌗", "تربيع أخير", "نشاط معتدل: مد محاقي هادئ."
    else: emoji, phase_ar, tip = "🌘", "هلال متناقص", "نشاط منخفض تراجع القمر."

    return {"age": age, "illumination": illumination, "emoji": emoji, "phase_ar": phase_ar, "tip": tip, "tidal_color": "#10B981", "tidal": "مد وجزر ربيعي"}

def compute_solunar_times(moon_age: float, lon: float) -> dict:
    synodic = 29.53059
    moon_transit_local = (12.0 + moon_age * (24.0 * 50.0 / (60.0 * synodic)) + 3 + lon / 15.0) % 24.0
    
    def fmt_h(h):
        h = h % 24; period = "ص" if h < 12 else "م"; h12 = int(h) % 12 or 12
        return f"{h12}:{int(round((h % 1) * 60)):02d} {period}"
    def time_range(center, dur): return f"{fmt_h(center - dur/2)} — {fmt_h(center + dur/2)}"
    
    return {
        "major": [time_range(moon_transit_local, 2), time_range(moon_transit_local + 12.417, 2)],
        "minor": [time_range(moon_transit_local + 6.208, 1), time_range(moon_transit_local + 18.625, 1)]
    }

# ─── واجهة المستخدم ───────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🌊 MARINE TRACKER</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">المرشد البحري الذكي لرحلات الصيد</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if "coords" not in st.session_state: st.session_state["coords"] = (26.9239, 49.8681)
if "pending_coords" not in st.session_state: st.session_state["pending_coords"] = None

if st.session_state["pending_coords"] is not None:
    st.session_state["coords"] = st.session_state["pending_coords"]
    st.session_state["pending_coords"] = None

flat, flon = st.session_state["coords"]
display_text = f"📍 الموقع المحدد: {get_location_name(flat, flon)} ({flat:.3f}°، {flon:.3f}°)"
st.markdown(f'<div class="location-box">{display_text}</div>', unsafe_allow_html=True)

_day_options = [_day_option_label(i) for i in range(7)]
_selected_day = st.segmented_control(label="اختر اليوم", options=_day_options, default=_day_options[0], label_visibility="collapsed")
day_offset = _day_options.index(_selected_day) if _selected_day in _day_options else 0

st.markdown('<div class="map-section-label">🗺️ خريطة الصيد التفاعلية</div>', unsafe_allow_html=True)
m = folium.Map(location=[26.9239, 49.8681], zoom_start=11, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri World Imagery", prefer_canvas=True)

if st.session_state["coords"]:
    folium.Marker(location=[flat, flon], icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)
    folium.Circle(location=[flat, flon], radius=5000, color="#38BDF8", fill=True, fill_opacity=0.10, weight=2).add_to(m)

map_data = st_folium(m, height=350, use_container_width=True, key="marine_map", returned_objects=["last_clicked"])
if map_data and map_data.get("last_clicked"):
    new_coords = (round(map_data["last_clicked"]["lat"], 5), round(map_data["last_clicked"]["lng"], 5))
    if st.session_state["coords"] != new_coords:
        st.session_state["pending_coords"] = new_coords
        st.rerun()

if st.session_state["coords"]:
    w_res, m_res = fetch_weather(flat, flon)
    if w_res is None or "hourly" not in w_res:
        st.error("⚠️ تعذّر جلب البيانات. يرجى اختيار نقطة بحرية صحيحة.")
    else:
        hw, hm = w_res["hourly"], m_res["hourly"]
        total_hours = len(hw.get("temperature_2m", []))
        curr_h = datetime.now().hour
        data_idx = min((day_offset * 24) + curr_h, total_hours - 1)

        def safe_get(l, idx, default=0.0):
            try: return l[idx] if l[idx] is not None else default
            except: return default

        t_now = safe_get(hw.get("temperature_2m", []), data_idx)
        t_feels = safe_get(hw.get("apparent_temperature", []), data_idx)
        wind_now = safe_get(hw.get("windspeed_10m", []), data_idx)
        wave_now = safe_get(hm.get("wave_height", []), data_idx)
        wave_period = safe_get(hm.get("wave_period", []), data_idx)
        swell_now = safe_get(hm.get("swell_wave_height", []), data_idx)
        sst = safe_get(hm.get("sea_surface_temperature", []), data_idx)

        # النطاقات الزمنية الجيدة للصيد
        look_ahead = min(data_idx + 24, total_hours)
        good_hours = [i for i in range(data_idx, look_ahead) if safe_get(hw.get("windspeed_10m", []), i) <= 15 and safe_get(hm.get("wave_height", []), i) <= 0.7]
        time_ranges = build_time_ranges(good_hours)

        if wind_now < 14 and wave_now < 0.5: status, badge, adv = "excellent", "badge-excellent", "الوضع ممتاز: بحر هادئ، الموج ساكن والرياح ركود. مثالي للصيد!"
        elif wind_now < 22 and wave_now < 0.9: status, badge, adv = "good", "badge-good", "الوضع جيد: حركة موج خفيفة. الصيد مناسب مع الحذر."
        else: status, badge, adv = "bad", "badge-bad", "الوضع صعب: موج عالٍ ورياح شديدة. يُنصح بتأجيل الرحلة."

        status_ar = {"excellent": "ممتاز", "good": "جيد", "bad": "محظور"}

        # ─── بطاقة الأحوال الحالية ────────────────────────────────────────────
        st.markdown(f"""
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <div class="card-title" style="margin-bottom:0">📊 الأحوال الحالية</div>
            <span class="{badge}">{status_ar[status]}</span>
          </div>
          <div class="metric-row">
            <div class="metric-box"><div class="metric-value">{t_now:.0f}°م</div><div class="metric-label">الحرارة</div></div>
            <div class="metric-box"><div class="metric-value">{t_feels:.0f}°م</div><div class="metric-label">المحسوسة</div></div>
            <div class="metric-box"><div class="metric-value">{wind_now:.0f} ك/س</div><div class="metric-label">الرياح</div></div>
            <div class="metric-box"><div class="metric-value">{wave_now:.1f} م</div><div class="metric-label">الموج</div></div>
          </div>
          <p class="advice-{status}">{adv}</p>
        </div>
        """, unsafe_allow_html=True)

        if time_ranges:
            chips_html = "".join(f'<span class="range-chip">{r}</span>' for r in time_ranges[:4])
            st.markdown(f'<div style="margin-top:-8px; margin-bottom:16px; direction:rtl; text-align:right;"><span style="color:#94A3B8; font-size:0.85rem; margin-left:8px;">🕐 أفضل فترات الصيد القادمة:</span>{chips_html}</div>', unsafe_allow_html=True)

        # ─── بطاقة مؤشر النشاط الدائري ──────────────────────────────────────────
        act = fish_activity_score(wind_now, wave_now, t_now, swell_now)
        score, color = act["score"], act["color"]
        radius = 68; circ = 2 * math.pi * radius; filled = circ * score / 100
        stars_html = "★" * int(round(score / 20)) + "☆" * (5 - int(round(score / 20)))
        st.markdown(f"""
        <div class="card">
          <div class="card-title">🐠 مؤشر نشاط الأسماك</div>
          <div style="display:flex;align-items:center;gap:24px;direction:rtl;flex-wrap:wrap;">
            <div class="act-ring-wrap" style="flex:0 0 auto;">
              <div class="act-ring-inner">
                <svg width="160" height="160" viewBox="0 0 160 160">
                  <circle cx="80" cy="80" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="14"/>
                  <circle cx="80" cy="80" r="{radius}" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{filled:.1f} {circ:.1f}"/>
                </svg>
                <div class="act-ring-center"><div class="act-ring-score">{score}</div><div class="act-ring-label">/ 100</div></div>
              </div>
              <div class="act-ring-stars" style="color:#F59E0B;">{stars_html}</div>
              <div class="act-ring-status" style="color:{color};">{act['label']}</div>
            </div>
            <div style="flex:1;min-width:160px;text-align:right;">
              <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:12px;color:#CBD5E1;font-size:0.9rem;line-height:1.8;margin-bottom:12px;">{act['advice']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── 📉 منحنى المد والجزر المتقدم (تنسيق 12 ساعة + النهار والليل) ───────
        try:
            target_date = datetime.now() + timedelta(days=day_offset)
            tide_heights = compute_tide_profile(flat, flon, target_date)

            # تجهيز مسميات نظام الـ 12 ساعة للمحور الأفقي
            hours_12_labels = []
            for h in range(25):
                h_wrapped = h % 24
                if h_wrapped == 0: labels = "12 AM"
                elif h_wrapped == 12: labels = "12 NOON"
                elif h_wrapped < 12: labels = f"{h_wrapped} AM"
                else: labels = f"{h_wrapped - 12} PM"
                hours_12_labels.append(labels)

            # إنشاء مخطط الرسم البياني عبر Plotly
            fig = go.Figure()

            # رسم خلفية تلوين فترات الليل والنهار (مثل الصورة المرفقة)
            # فترة ما قبل الشروق (ليل) 12 AM إلى 5 AM
            fig.add_vrect(x0=0, x1=5, fillcolor="#0A1628", opacity=0.4, line_width=0)
            # فترة النهار (6 AM إلى 6 PM)
            fig.add_vrect(x0=5, x1=18, fillcolor="#ECEFF1", opacity=0.15, line_width=0)
            # فترة ما بعد الغروب (ليل) 6 PM إلى 12 AM
            fig.add_vrect(x0=18, x1=24, fillcolor="#0A1628", opacity=0.4, line_width=0)

            # إضافة منحنى المد
            fig.add_trace(go.Scatter(
                x=list(range(25)),
                y=tide_heights,
                mode='lines',
                line=dict(color='#38BDF8', width=3, shape='spline'),
                name='منسوب المد',
                hovertemplate='<b>الساعة:</b> %{text}<br><b>الارتفاع:</b> %{y} م<extra></extra>',
                text=hours_12_labels
            ))

            # إذا كان الاختيار على اليوم الحالي، نرسم الخط الأحمر الرأسي للوقت الحالي
            if day_offset == 0:
                # خط طولي أحمر
                fig.add_vline(x=curr_h, line_width=2, line_dash="solid", line_color="#EF4444")
                # شارة علوية تعرض الارتفاع اللحظي الحالي
                curr_tide_val = tide_heights[min(curr_h, 24)]
                fig.add_annotation(
                    x=curr_h, y=curr_tide_val + 0.15,
                    text=f"{curr_tide_val:.2f} م ↓",
                    showarrow=True, arrowhead=1,
                    arrowcolor="#EF4444", bordercolor="#EF4444",
                    bgcolor="#1E293B", font=dict(color="#F1F5F9", size=11)
                )

            # إعدادات مظهر المحاور والتنسيق العام الشبيه بالهاتف
            fig.update_layout(
                margin=dict(l=20, r=20, t=10, b=10),
                height=240,
                backgroundColor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(
                    tickmode='array',
                    tickvals=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                    ticktext=['AM', '2', '4', '6', '8', '10', 'NOON', '2', '4', '6', '8', '10', 'PM'],
                    gridcolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='#64748B', size=11),
                    fixedrange=True
                ),
                yaxis=dict(
                    ticksuffix=" m",
                    gridcolor='rgba(255,255,255,0.08)',
                    tickfont=dict(color='#64748B', size=11),
                    fixedrange=True,
                    side="left"
                )
            )

            st.markdown('<div class="map-section-label" style="margin-top:12px;">📉 منحنى المد والجزر (تنسيق 12 ساعة)</div>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # استخراج أوقات أعلى مد وأدنى جزر حسابياً لعرضها أسفل المخطط
            highs_list = []
            lows_list = []
            for i in range(1, 24):
                if tide_heights[i] >= tide_heights[i-1] and tide_heights[i] >= tide_heights[i+1]:
                    highs_list.append((i, tide_heights[i]))
                elif tide_heights[i] <= tide_heights[i-1] and tide_heights[i] <= tide_heights[i+1]:
                    lows_list.append((i, tide_heights[i]))

            def fmt_h_am_pm(h):
                p = "AM" if h < 12 else "PM"; h12 = h % 12 or 12
                return f"{h12}:00 {p}"

            # تصميم الجزء السفلي للبطاقة لعرض القيم الرقمية للمد والجزر
            st.markdown('<div style="background: rgba(30,41,59,0.5); padding: 12px; border-radius: 12px; margin-top: 5px;">', unsafe_allow_html=True)
            col_low, col_high = st.columns(2)
            with col_low:
                st.markdown("<p style='color:#94A3B8; font-size:0.8rem; margin:0;'>Low Tides (أدنى جزر):</p>", unsafe_allow_html=True)
                for h_idx, v in lows_list[:2]:
                    st.markdown(f"<p style='color:#ECEFF1; font-size:0.9rem; font-weight:700; margin:3px 0;'>{v:.1f} m @ {fmt_h_am_pm(h_idx)}</p>", unsafe_allow_html=True)
            with col_high:
                st.markdown("<p style='color:#38BDF8; font-size:0.8rem; margin:0;'>High Tides (أعلى مد):</p>", unsafe_allow_html=True)
                for h_idx, v in highs_list[:2]:
                    st.markdown(f"<p style='color:#ECEFF1; font-size:0.9rem; font-weight:700; margin:3px 0;'>{v:.1f} m @ {fmt_h_am_pm(h_idx)}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            pass

        # ─── بطاقة القمر ──────────────────────────────────────────────────────
        try:
            moon = get_moon_phase(datetime.now() + timedelta(days=day_offset))
            st.markdown(f"""
            <div class="card" style="margin-top:16px;">
              <div class="card-title">🌙 حالة القمر وتأثيره على الصيد</div>
              <div class="moon-row">
                <div class="moon-emoji-wrap">{moon["emoji"]}</div>
                <div class="moon-info">
                  <div class="moon-phase-name">{moon["phase_ar"]}</div>
                  <div class="moon-illum">الإضاءة: <strong style="color:#F1F5F9;">{moon["illumination"]}%</strong> | عمر القمر: <strong style="color:#F1F5F9;">{moon["age"]:.1f}</strong> يوم</div>
                </div>
              </div>
              <div class="moon-tip">{moon["tip"]}</div>
            </div>
            """, unsafe_allow_html=True)
        except: pass
