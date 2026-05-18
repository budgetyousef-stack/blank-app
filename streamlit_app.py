import streamlit as st
import requests
import folium
import pandas as pd
import math
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
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');

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

/* شريط النشاط */
.activity-bar-wrap { background:#0A1628; border-radius:8px; height:16px; overflow:hidden; margin:10px 0 4px 0; }
.activity-bar-fill { height:100%; border-radius:8px; transition: width 0.5s ease; }
.activity-labels { display:flex; justify-content:space-between; font-size:0.72rem; color:#475569; direction:rtl; margin-top:3px; }

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

/* المخطط */
[data-testid="stVegaLiteChart"] { border-radius:12px !important; overflow:hidden !important; }

/* التنسيق الخاص بقوالب صفحة الويب */
.tide-event-chip {
    flex: 1;
    min-width: 100px;
    border-radius: 12px;
    padding: 9px 10px;
    text-align: center;
    border: 1px solid;
}
.tide-event-chip .ev-icon { font-size: 1.1rem; }
.tide-event-chip .ev-label { font-size: 0.68rem; color: #94A3B8; margin-top: 1px; }
.tide-event-chip .ev-time { font-size: 0.9rem; font-weight: 800; margin-top: 2px; }
.tide-event-chip .ev-height { font-size: 0.72rem; margin-top: 1px; font-weight: 600; }

/* الفوتر */
.footer { text-align:center; color:#1E3A5F; font-size:0.72rem; margin-top:24px; padding-top:16px; border-top:1px solid #1E293B; }

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
DAYS_AR = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

# ─── نموذج نشاط الأسماك ───────────────────────────────────────────────────────
def fish_activity_score(wind: float, wave: float, temp: float, swell: float = 0.0) -> dict:
    score = 100

    # تقييم الرياح
    if wind <= 10:
        w_status, w_label = "#10B981", "مثالي"
    elif wind <= 18:
        w_status, w_label = "#F59E0B", "مقبول"
        score -= 20
    else:
        w_status, w_label = "#EF4444", "شديد"
        score -= 50

    # تقييم الموج
    if wave <= 0.3:
        wv_status, wv_label = "#10B981", "هادئ"
    elif wave <= 0.7:
        wv_status, wv_label = "#F59E0B", "خفيف"
        score -= 15
    else:
        wv_status, wv_label = "#EF4444", "عالي"
        score -= 45

    # تقييم الحرارة
    if 22 <= temp <= 30:
        t_status, t_label = "#10B981", "مثالية"
    elif 18 <= temp <= 36:
        t_status, t_label = "#F59E0B", "مقبولة"
        score -= 5
    else:
        t_status, t_label = "#EF4444", "قاسية"
        score -= 20

    # تأثير التورم البحري
    if swell > 1.5:
        score -= 15

    score = max(0, min(100, score))

    if score >= 65:
        level, label, color = "high", "نشاط عالي 🎣", "#10B981"
        advice = "ظروف مثالية — الأسماك نشيطة وقريبة من السطح. أنسب وقت للمحادق وصيد السيف!"
    elif score >= 35:
        level, label, color = "medium", "نشاط متوسط 🐟", "#F59E0B"
        advice = "ظروف مقبولة — الأسماك نشيطة جزئياً. الصيد ممكن مع بعض الصبر."
    else:
        level, label, color = "low", "نشاط منخفض ⚠️", "#EF4444"
        advice = "ظروف صعبة — الأسماك في الأعماق والبحر غير مناسب حالياً."

    return {
        "level": level, "label": label, "color": color, "score": score, "advice": advice,
        "wind_status": w_status, "wind_label": w_label,
        "wave_status": wv_status, "wave_label": wv_label,
        "temp_status": t_status, "temp_label": t_label,
    }

# ─── تجميع ساعات جيدة متتالية في نطاقات زمنية ────────────────────────────────
def build_time_ranges(good_hours: list) -> list:
    if not good_hours:
        return []
    ranges = []
    start = good_hours[0]
    end = good_hours[0]
    for h in good_hours[1:]:
        if h == end + 1:
            end = h
        else:
            ranges.append((start, end))
            start = end = h
    ranges.append((start, end))

    chips = []
    for s, e in ranges:
        def fmt(h):
            period = "ص" if h < 12 else "م"
            h12 = h % 12 or 12
            return f"{h12}:00 {period}"
        if s == e:
            chips.append(fmt(s))
        else:
            chips.append(f"{fmt(s)} — {fmt(e + 1)}")
    return chips

# ─── نموذج المد والجزر التوافقي (Harmonic Tidal Model) ───────────────────────
def _tide_amplitudes(lat: float, lon: float) -> dict:
    in_gulf     = (23 <= lat <= 30) and (48 <= lon <= 57)   # Arabian Gulf
    in_red_sea  = (12 <= lat <= 28) and (32 <= lon <= 44)   # Red Sea
    in_oman     = (22 <= lat <= 26) and (57 <= lon <= 62)   # Gulf of Oman

    if in_gulf:
        return dict(M2=0.90, S2=0.28, K1=0.12, O1=0.08, M4=0.06, base=1.10)
    elif in_red_sea:
        return dict(M2=0.28, S2=0.10, K1=0.18, O1=0.12, M4=0.02, base=0.45)
    elif in_oman:
        return dict(M2=0.65, S2=0.22, K1=0.20, O1=0.14, M4=0.04, base=0.80)
    else:
        return dict(M2=0.60, S2=0.20, K1=0.18, O1=0.12, M4=0.03, base=0.75)


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


def find_tide_events(heights: list) -> dict:
    highs, lows = [], []
    for i in range(1, len(heights) - 1):
        prev, curr, nxt = heights[i - 1], heights[i], heights[i + 1]
        if curr >= prev and curr >= nxt and curr > heights[i - 1] + 0.01:
            highs.append((i, curr))
        elif curr <= prev and curr <= nxt and curr < heights[i - 1] - 0.01:
            lows.append((i, curr))
    return {"highs": highs, "lows": lows}


def fmt_tide_hour(h: int) -> str:
    period = "ص" if h < 12 else "م"
    h12 = h % 12 or 12
    return f"{h12}:00 {period}"


# ─── حساب طور القمر الفلكي ────────────────────────────────────────────────────
def get_moon_phase(date: datetime) -> dict:
    synodic = 29.53059
    ref_jdn  = 2451549.26

    y, m, d = date.year, date.month, date.day
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    jdn = (d + (153 * mm + 2) // 5 + 365 * yy
           + yy // 4 - yy // 100 + yy // 400 - 32045
           + (date.hour - 12) / 24.0)

    age = (jdn - ref_jdn) % synodic
    illumination = int(round((1 - math.cos(2 * math.pi * age / synodic)) / 2 * 100))

    days_to_full = (14.765 - age) % synodic
    days_to_new  = (synodic  - age) % synodic

    if age < 1.85:
        emoji, phase_ar = "🌑", "محاق — قمر جديد"
        tidal, tidal_c   = "مدّ ربيعي قوي 💪", "#10B981"
        tip = "أفضل وقت للصيد: المياه مظلمة والأسماك تتغذى بجرأة قرب السطح."
        tip_color = "#10B981"
    elif age < 7.38:
        emoji, phase_ar = "🌒", "هلال متصاعد"
        tidal, tidal_c   = "مدّ معتدل متصاعد", "#F59E0B"
        tip = "نشاط جيد: الأسماك في حالة بحث نشط عن الغذاء بعد المحاق."
        tip_color = "#F59E0B"
    elif age < 9.22:
        emoji, phase_ar = "🌓", "تربيع أول"
        tidal, tidal_c   = "مدّ محاقي ضعيف", "#94A3B8"
        tip = "نشاط متوسط: المدّ هادئ ومستقر، مناسب للصيد في الأعماق."
        tip_color = "#94A3B8"
    elif age < 14.76:
        emoji, phase_ar = "🌔", "أحدب متصاعد"
        tidal, tidal_c   = "مدّ متصاعد نحو الربيعي", "#F59E0B"
        tip = "نشاط متزايد: الأسماك تستعد لذروة نشاطها عند اكتمال البدر."
        tip_color = "#F59E0B"
    elif age < 16.61:
        emoji, phase_ar = "🌕", "بدر — قمر كامل"
        tidal, tidal_c   = "مدّ ربيعي قوي 💪", "#10B981"
        tip = "ذروة النشاط 🎣: أفضل ليلة للصيد! تيارات قوية والأسماك في أقصى نشاطها."
        tip_color = "#10B981"
    elif age < 22.15:
        emoji, phase_ar = "🌖", "أحدب متناقص"
        tidal, tidal_c   = "مدّ متناقص تدريجياً", "#F59E0B"
        tip = "نشاط جيد: القمر لا يزال مضيئاً والأسماك نشيطة."
        tip_color = "#F59E0B"
    elif age < 23.99:
        emoji, phase_ar = "🌗", "تربيع أخير"
        tidal, tidal_c   = "مدّ محاقي ضعيف", "#94A3B8"
        tip = "نشاط معتدل: المدّ محاقي هادئ، أفضل للصيد الصباحي الهادئ."
        tip_color = "#94A3B8"
    else:
        emoji, phase_ar = "🌘", "هلال متناقص"
        tidal, tidal_c   = "مدّ ضعيف يتراجع", "#64748B"
        tip = "نشاط منخفض: القمر في تراجعه الأخير نحو المحاق القادم."
        tip_color = "#64748B"

    return {
        "age": age, "illumination": illumination, "emoji": emoji,
        "phase_ar": phase_ar, "tidal": tidal, "tidal_color": tidal_c,
        "tip": tip, "tip_color": tip_color,
        "days_to_full": days_to_full, "days_to_new": days_to_new,
    }


# ─── جلب البيانات من الـ APIs بدقة عالية ─────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float):
    w_url = "https://api.open-meteo.com/v1/forecast"
    m_url = "https://marine-api.open-meteo.com/v1/marine"

    w_params = {
        "latitude": lat, "longitude": lon,
        "hourly": (
            "temperature_2m,apparent_temperature,"
            "windspeed_10m,winddirection_10m,"
            "windgusts_10m,precipitation_probability,"
            "visibility,cloudcover"
        ),
        "daily": (
            "windspeed_10m_max,windgusts_10m_max,"
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "wind_speed_unit": "kmh",
        "forecast_days": 7,
        "timezone": "Asia/Riyadh",
        "models": "best_match",
    }

    m_params = {
        "latitude": lat, "longitude": lon,
        "hourly": (
            "wave_height,wave_direction,wave_period,"
            "wind_wave_height,wind_wave_period,"
            "swell_wave_height,swell_wave_period,swell_wave_direction,"
            "sea_surface_temperature"
        ),
        "daily": (
            "wave_height_max,wave_period_max,"
            "swell_wave_height_max,wind_wave_height_max"
        ),
        "forecast_days": 7,
        "timezone": "Asia/Riyadh",
        "length_unit": "metric",
        "models": "best_match",
    }

    try:
        w_res = requests.get(w_url, params=w_params, timeout=12).json()
        m_res = requests.get(m_url, params=m_params, timeout=12).json()
        return w_res, m_res
    except Exception as e:
        return None, None

@st.cache_data(ttl=3600)
def get_location_name(lat: float, lon: float) -> str:
    try:
        res = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ar",
            headers={"User-Agent": "MarineTrackerPRO/2.0"},
            timeout=4
        ).json()
        addr = res.get("address", {})
        return (
            addr.get("city") or addr.get("town") or
            addr.get("village") or addr.get("state") or
            "منطقة بحرية مفتوحة"
        )
    except:
        return "منطقة بحرية"

# ─── واجهة المستخدم ───────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🌊 MARINE TRACKER</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">المرشد البحري الذكي لرحلات الصيد</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# إدارة حالة الجلسة
if "coords" not in st.session_state:
    st.session_state["coords"] = None
if "pending_coords" not in st.session_state:
    st.session_state["pending_coords"] = None

# معالجة التحديث المعلق
if st.session_state["pending_coords"] is not None:
    st.session_state["coords"] = st.session_state["pending_coords"]
    st.session_state["pending_coords"] = None

flat, flon = st.session_state["coords"] if st.session_state["coords"] else (26.85, 49.80)

# مربع الموقع
if st.session_state["coords"]:
    display_text = f"📍 الموقع المحدد: {get_location_name(flat, flon)} ({flat:.3f}°، {flon:.3f}°)"
else:
    display_text = "📍 انقر على الخريطة لتحديد موقعك البحري"

st.markdown(f'<div class="location-box">{display_text}</div>', unsafe_allow_html=True)

# ─── الخريطة ──────────────────────────────────────────────────────────────────
st.markdown('<div class="map-section-label">🗺️ خريطة الصيد التفاعلية</div>', unsafe_allow_html=True)

m = folium.Map(
    location=[flat, flon],
    zoom_start=9,
    tiles="CartoDB dark_matter",
    prefer_canvas=True,
)

# حقن CSS لإلغاء انعكاس الخريطة والمحافظة على الـ LTR فيها
m.get_root().html.add_child(folium.Element("""
<style>
html, body,
.leaflet-container,
.leaflet-pane,
.leaflet-map-pane,
.leaflet-tile-pane,
.leaflet-overlay-pane,
.leaflet-marker-pane,
.leaflet-popup-pane,
.leaflet-tooltip-pane,
.leaflet-tile {
    direction: ltr !important;
    text-align: left !important;
    unicode-bidi: normal !important;
}
</style>
"""))

if st.session_state["coords"]:
    folium.Marker(
        location=[flat, flon],
        icon=folium.Icon(color="blue", icon="anchor", prefix="fa"),
        tooltip="موقعك المحدد"
    ).add_to(m)
    folium.Circle(
        location=[flat, flon],
        radius=5000,
        color="#38BDF8",
        fill=True,
        fill_color="#38BDF8",
        fill_opacity=0.10,
        weight=2,
    ).add_to(m)

map_data = st_folium(m, height=400, use_container_width=True, key="marine_map", returned_objects=["last_clicked"])

# التقاط النقرات بشكل آمن
if map_data and map_data.get("last_clicked"):
    nl_lat = round(map_data["last_clicked"]["lat"], 5)
    nl_lng = round(map_data["last_clicked"]["lng"], 5)
    new_coords = (nl_lat, nl_lng)
    if st.session_state["coords"] != new_coords:
        st.session_state["pending_coords"] = new_coords
        st.rerun()

# ─── التحليلات ────────────────────────────────────────────────────────────────
if st.session_state["coords"]:
    w_res, m_res = fetch_weather(flat, flon)

    if w_res is None or m_res is None or "hourly" not in w_res or "hourly" not in m_res:
        st.error("⚠️ تعذّر جلب البيانات. يرجى اختيار نقطة داخل البحر أو المحاولة لاحقاً.")
    else:
        try:
            hw = w_res["hourly"]
            hm = m_res["hourly"]

            total_hours = len(hw.get("temperature_2m", []))
            curr_h = min(datetime.now().hour, total_hours - 1) if total_hours > 0 else 0

            def safe_get(lst, idx, default=0.0):
                try:
                    val = lst[idx]
                    return val if val is not None else default
                except (IndexError, TypeError):
                    return default

            t_now       = safe_get(hw.get("temperature_2m", []), curr_h)
            t_feels     = safe_get(hw.get("apparent_temperature", []), curr_h)
            wind_now    = safe_get(hw.get("windspeed_10m", []), curr_h)
            wind_gust   = safe_get(hw.get("windgusts_10m", []), curr_h)
            wind_dir    = safe_get(hw.get("winddirection_10m", []), curr_h)
            wave_now    = safe_get(hm.get("wave_height", []), curr_h)
            wave_period = safe_get(hm.get("wave_period", []), curr_h)
            swell_now   = safe_get(hm.get("swell_wave_height", []), curr_h)
            sst         = safe_get(hm.get("sea_surface_temperature", []), curr_h)
            precip_prob = safe_get(hw.get("precipitation_probability", []), curr_h)

            # تعديل: مسح الـ 24 ساعة بالكامل لصيد الفترتين الجيدتين للصيد
            look_ahead = min(curr_h + 24, total_hours)
            good_hours = [
                i for i in range(curr_h, look_ahead)
                if safe_get(hw.get("windspeed_10m", []), i) <= 15
                and safe_get(hm.get("wave_height", []), i) <= 0.7
                and safe_get(hw.get("precipitation_probability", []), i, 0) < 40
            ]
            time_ranges = build_time_ranges(good_hours)

            # تحديد الحالة
            if wind_now < 14 and wave_now < 0.5:
                status, badge = "excellent", "badge-excellent"
                adv = "الوضع ممتاز: بحر هادئ، الموج ساكن والرياح ركود. مثالي للصيد!"
            elif wind_now < 22 and wave_now < 0.9:
                status, badge = "good", "badge-good"
                adv = "الوضع جيد: حركة موج خفيفة. الصيد مناسب مع الحذر."
            else:
                status, badge = "bad", "badge-bad"
                adv = "الوضع صعب: موج عالٍ ورياح شديدة. يُنصح بتأجيل الرحلة."

            status_ar = {"excellent": "ممتاز", "good": "جيد", "bad": "محظور"}

            # ─── بطاقة الأحوال الحالية ────────────────────────────────────────
            st.markdown(f"""
            <div class="card">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                <div class="card-title" style="margin-bottom:0">📊 الأحوال الحالية</div>
                <span class="{badge}">{status_ar[status]}</span>
              </div>
              <div class="metric-row">
                <div class="metric-box">
                  <div class="metric-value">{t_now:.0f}°م</div>
                  <div class="metric-label">الحرارة</div>
                </div>
                <div class="metric-box">
                  <div class="metric-value">{t_feels:.0f}°م</div>
                  <div class="metric-label">الحرارة المحسوسة</div>
                </div>
                <div class="metric-box">
                  <div class="metric-value">{wind_now:.0f} كم/س</div>
                  <div class="metric-label">الرياح</div>
                </div>
                <div class="metric-box">
                  <div class="metric-value">{wind_gust:.0f} كم/س</div>
                  <div class="metric-label">أقصى هبّة</div>
                </div>
              </div>
              <div class="metric-row">
                <div class="metric-box">
                  <div class="metric-value">{wave_now:.1f} م</div>
                  <div class="metric-label">ارتفاع الموج</div>
                </div>
                <div class="metric-box">
                  <div class="metric-value">{wave_period:.0f} ث</div>
                  <div class="metric-label">دورة الموج</div>
                </div>
                <div class="metric-box">
                  <div class="metric-value">{swell_now:.1f} م</div>
                  <div class="metric-label">التورم البحري</div>
                </div>
                <div class="metric-box">
                  <div class="metric-value">{sst:.1f}°م</div>
                  <div class="metric-label">حرارة السطح</div>
                </div>
              </div>
              <p class="advice-{status}">{adv}</p>
            """, unsafe_allow_html=True)

            if time_ranges:
                chips_html = "".join(f'<span class="range-chip">{r}</span>' for r in time_ranges[:4])
                st.markdown(f"""
                <div style="border-top:1px solid #1E3A5F;padding-top:12px;margin-top:4px;">
                  <div style="color:#94A3B8;font-size:0.82rem;text-align:right;margin-bottom:6px;">
                    🕐 أفضل نطاقات الصيد القادمة:
                  </div>
                  <div style="direction:rtl;">{chips_html}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="border-top:1px solid #1E3A5F;padding-top:12px;margin-top:4px;
                            color:#EF4444;font-size:0.84rem;text-align:right;">
                  ⚠️ لا توجد ساعات مناسبة للصيد خلال الفترة القادمة.
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # ─── بطاقة مؤشر نشاط الأسماك ─────────────────────────────────────
            act = fish_activity_score(wind_now, wave_now, t_now, swell_now)
            st.markdown(f"""
            <div class="card">
              <div class="card-title">🐠 توقع نشاط الأسماك وحالة الضرب</div>
              <div style="text-align:center;padding:14px;background:rgba(255,255,255,0.04);
                          border-radius:12px;border:2px solid {act['color']};
                          color:{act['color']};font-size:1.5rem;font-weight:900;">
                {act['label']}
              </div>
              <div class="activity-labels">
                <span>منخفض 0%</span><span>متوسط 50%</span><span>100% عالي</span>
              </div>
              <div class="activity-bar-wrap">
                <div class="activity-bar-fill"
                     style="width:{act['score']}%;
                            background:linear-gradient(90deg,#EF4444,#F59E0B,#10B981);">
                </div>
              </div>
              <div style="text-align:center;color:#94A3B8;font-size:0.82rem;margin-bottom:10px;">
                مؤشر النشاط: <strong style="color:{act['color']}">{act['score']}%</strong>
              </div>
              <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:12px;
                          color:#CBD5E1;text-align:right;font-size:0.9rem;line-height:1.7;">
                {act['advice']}
              </div>
              <div class="factor-row">
                <div class="factor-box">
                  <div class="factor-value" style="color:{act['wind_status']}">{act['wind_label']}</div>
                  <div class="factor-label">الرياح</div>
                </div>
                <div class="factor-box">
                  <div class="factor-value" style="color:{act['wave_status']}">{act['wave_label']}</div>
                  <div class="factor-label">الموج</div>
                </div>
                <div class="factor-box">
                  <div class="factor-value" style="color:{act['temp_status']}">{act['temp_label']}</div>
                  <div class="factor-label">الحرارة</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ─── معالجة الحسابات للمنحنى (مع حذف عرض الأكواد الخربانة) ───
            try:
                now = datetime.now()
                tide_heights = compute_tide_profile(flat, flon, now)
                curr_tide_h  = min(curr_h, 24)

                # إنشاء مخطط منحنى المد خلال 24 ساعة
                tide_chart_data = pd.DataFrame(
                    {"المد (م)": [float(v) for v in tide_heights]},
                    index=list(range(25)),
                )

                st.markdown(
                    '<div class="map-section-label" style="margin-top:4px;">📉 منحنى المد والجزر — 24 ساعة</div>',
                    unsafe_allow_html=True
                )
                st.line_chart(
                    tide_chart_data,
                    height=175,
                    use_container_width=True,
                    color=["#38BDF8"],
                )
                st.markdown(
                    f'<div style="text-align:right;font-size:0.72rem;color:#475569;margin-top:2px;">'
                    f'المحور الأفقي: ساعات اليوم (0–24) &nbsp;|&nbsp; '
                    f'<span style="color:#38BDF8;">■</span> منسوب المد &nbsp;'
                    f'| الساعة الحالية: {fmt_tide_hour(curr_tide_h)}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            except Exception:
                pass

            # ─── بطاقة القمر ──────────────────────────────────────────────────
            try:
                moon = get_moon_phase(datetime.now())
                dtf  = round(moon["days_to_full"], 1)
                dtn  = round(moon["days_to_new"],  1)
                next_full_label = f"{dtf} يوم" if dtf > 1 else "الليلة!"
                next_new_label  = f"{dtn} يوم" if dtn > 1 else "الليلة!"

                st.markdown(f"""
                <div class="card">
                  <div class="card-title">🌙 حالة القمر وتأثيره على الصيد</div>
                  <div class="moon-row">
                    <div class="moon-emoji-wrap">{moon["emoji"]}</div>
                    <div class="moon-info">
                      <div class="moon-phase-name">{moon["phase_ar"]}</div>
                      <div class="moon-illum">
                        الإضاءة: <strong style="color:#F1F5F9;">{moon["illumination"]}%</strong>
                        &nbsp;|&nbsp; عمر القمر: <strong style="color:#F1F5F9;">{moon["age"]:.1f}</strong> يوم
                      </div>
                      <div style="margin-top:8px;">
                        <span style="background:{moon["tidal_color"]}22;color:{moon["tidal_color"]};
                                     border:1px solid {moon["tidal_color"]}55;border-radius:16px;
                                     padding:3px 12px;font-size:0.78rem;font-weight:800;">
                          {moon["tidal"]}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="moon-events-row">
                    <div class="moon-event-box">
                      <div class="moon-event-label">🌕 حتى البدر القادم</div>
                      <div class="moon-event-val">{next_full_label}</div>
                    </div>
                    <div class="moon-event-box">
                      <div class="moon-event-label">🌑 حتى المحاق القادم</div>
                      <div class="moon-event-val">{next_new_label}</div>
                    </div>
                    <div class="moon-event-box">
                      <div class="moon-event-label">📅 الدورة القمرية</div>
                      <div class="moon-event-val">29.5 يوم</div>
                    </div>
                  </div>
                  <div class="moon-tip" style="border-right-color:{moon["tip_color"]};">
                    {moon["tip"]}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass

            # ─── توقعات الأسبوع القادم ─────────────────────────────────────────
            try:
                dw  = w_res["daily"].get("windspeed_10m_max", [0]*7)
                dt  = w_res["daily"].get("temperature_2m_max", [0]*7)
                dwv = m_res["daily"].get("wave_height_max", [0]*7)
                dsw = m_res["daily"].get("swell_wave_height_max", [0]*7)

                lbls = [
                    "اليوم" if i == 0
                    else DAYS_AR[(datetime.now() + timedelta(days=i)).weekday() % 7]
                    for i in range(min(7, len(dw)))
                ]

                chart_data = pd.DataFrame({
                    "اليوم": lbls,
                    "الرياح (كم/س)":   [round(v) if v is not None else 0 for v in dw[:len(lbls)]],
                    "الأمواج (م)":     [round(v, 2) if v is not None else 0 for v in dwv[:len(lbls)]],
                    "الحرارة (°م)":    [round(v) if v is not None else 0 for v in dt[:len(lbls)]],
                    "التورم البحري (م)":[round(v, 2) if v is not None else 0 for v in dsw[:len(lbls)]],
                }).set_index("اليوم")

                st.markdown(
                    '<div class="map-section-label" style="margin-top:4px;">📈 توقعات الأسبوع القادم</div>',
                    unsafe_allow_html=True
                )
                st.line_chart(
                    chart_data,
                    height=220,
                    use_container_width=True,
                    color=["#38BDF8", "#10B981", "#F59E0B", "#A78BFA"]
                )
            except Exception:
                pass

        except Exception as e:
            st.error(f"⚠️ يرجى اختيار نقطة داخل البحر لتشغيل التحليلات.")

# ─── الفوتر ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Marine Tracker PRO • بيانات Open-Meteo • الخرائط OpenStreetMap
</div>
""", unsafe_allow_html=True)
