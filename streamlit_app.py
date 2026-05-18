import streamlit as st
import requests
import folium
import pandas as pd
import math
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# ─── إعدادات الصفحة ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BAHAR PRO",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CSS احترافي متجاوب ويصلح الخريطة 100% ───────────────────────────────────
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

/* إخفاء شريط Streamlit المزعج */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

.map-section-label {
    color: #38BDF8;
    font-size: clamp(0.95rem, 2.8vw, 1.1rem);
    font-weight: 800;
    text-align: right;
    margin-bottom: 8px;
    padding: 0 2px;
}

/* حل مشكلة انعكاس الخريطة الصارم */
div[data-testid="stIFrame"], iframe, .stFoliumMap, .leaflet-container { 
    direction: ltr !important; 
    text-align: left !important;
}

.stFoliumMap { border-radius: 14px !important; overflow: hidden !important; }
iframe[title="st_folium.frontend"] { border-radius: 14px !important; border: 1px solid #1E3A5F !important; width: 100% !important; }

/* بطاقة القمر والفترات */
.moon-row { display: flex; align-items: center; gap: 18px; direction: rtl; margin-bottom: 16px; }
.moon-emoji-wrap { font-size: 3.5rem; line-height: 1; text-align: center; filter: drop-shadow(0 0 16px rgba(148,163,184,0.45)); }
.moon-info { flex: 1; text-align: right; }
.moon-phase-name { font-size: 1.2rem; font-weight: 900; color: #F1F5F9; }
.moon-illum { font-size: 0.8rem; color: #94A3B8; margin-top: 4px; }

.moon-events-row { display: flex; gap: 8px; direction: rtl; margin-bottom: 12px; flex-wrap: wrap; }
.moon-event-box { flex: 1; min-width: 90px; background: rgba(148,163,184,0.06); border: 1px solid rgba(148,163,184,0.15); border-radius: 12px; padding: 10px 8px; text-align: center; }
.moon-event-label { font-size: 0.7rem; color: #64748B; }
.moon-event-val   { font-size: 0.95rem; font-weight: 800; color: #F1F5F9; margin-top: 3px; }

.moon-tip { background: rgba(148,163,184,0.06); border-right: 3px solid #94A3B8; border-radius: 0 10px 10px 0; padding: 10px 14px; color: #CBD5E1; font-size: 0.85rem; text-align: right; line-height: 1.6; }

.main-title { color: #38BDF8; text-align: center; font-size: 2.2rem; font-weight: 900; margin: 0; text-shadow: 0 0 40px rgba(56,189,248,0.3); }
.sub-title { color: #64748B; text-align: center; font-size: 1rem; font-weight: 600; margin-top: 6px; }
.divider { width: 50px; height: 4px; background: linear-gradient(90deg, #38BDF8, #0EA5E9); border-radius: 4px; margin: 12px auto 20px auto; }

.location-box { background: linear-gradient(135deg, #1E293B 0%, #0F2137 100%); border: 2px solid #38BDF8; border-radius: 14px; padding: 14px 18px; text-align: center; color: #F1F5F9; font-size: 1rem; font-weight: 700; margin-bottom: 16px; }

.card { background: linear-gradient(145deg, #1E293B 0%, #162032 100%); border: 1px solid #1E3A5F; border-radius: 18px; padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.3); }
.card-title { color: #38BDF8; font-size: 1.05rem; font-weight: 800; margin-bottom: 14px; text-align: right; }

.metric-row { display: flex; gap: 10px; margin-bottom: 14px; direction: rtl; flex-wrap: wrap; }
.metric-box { flex: 1; min-width: 80px; background: rgba(56,189,248,0.06); border: 1px solid rgba(56,189,248,0.15); border-radius: 12px; padding: 12px 6px; text-align: center; }
.metric-value { font-size: 1.15rem; font-weight: 800; color: #F1F5F9; }
.metric-label { font-size: 0.75rem; color: #64748B; margin-top: 3px; }

.badge-excellent { background: linear-gradient(135deg,#059669,#10B981); color:white; padding:5px 16px; border-radius:20px; font-size:0.8rem; font-weight:800; }
.badge-good      { background: linear-gradient(135deg,#D97706,#F59E0B); color:white; padding:5px 16px; border-radius:20px; font-size:0.8rem; font-weight:800; }
.badge-bad       { background: linear-gradient(135deg,#DC2626,#EF4444); color:white; padding:5px 16px; border-radius:20px; font-size:0.8rem; font-weight:800; }

.activity-bar-wrap { background:#0A1628; border-radius:8px; height:16px; overflow:hidden; margin:10px 0 4px 0; }
.activity-bar-fill { height:100%; border-radius:8px; }
.activity-labels { display:flex; justify-content:space-between; font-size:0.72rem; color:#475569; direction:rtl; }

.range-chip { display: inline-block; background: linear-gradient(135deg, #0369A1, #0EA5E9); color: white; font-weight: 800; font-size: 0.8rem; padding: 5px 14px; border-radius: 22px; margin: 4px 0 4px 6px; white-space: nowrap; }

.advice-excellent { color:#10B981; font-weight:700; text-align:right; font-size:0.9rem; }
.advice-good      { color:#F59E0B; font-weight:700; text-align:right; font-size:0.9rem; }
.advice-bad       { color:#EF4444; font-weight:700; text-align:right; font-size:0.9rem; }

.factor-row { display:flex; gap:8px; margin-top:14px; direction:rtl; }
.factor-box { flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:10px 6px; text-align:center; }
.factor-label { font-size:0.72rem; color:#64748B; }
.factor-value { font-size:0.9rem; font-weight:800; }
</style>
""", unsafe_allow_html=True)

DAYS_AR = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

# ─── النماذج البرمجية للعمليات ───────────────────────────────────────────────
def fish_activity_score(wind, wave, temp):
    score = 100
    w_status, w_label = ("#10B981", "مثالي") if wind <= 10 else (("#F59E0B", "مقبول") if wind <= 18 else ("#EF4444", "شديد"))
    wv_status, wv_label = ("#10B981", "هادئ") if wave <= 0.3 else (("#F59E0B", "خفيف") if wave <= 0.7 else ("#EF4444", "عالي"))
    t_status, t_label = ("#10B981", "مثالية") if 22 <= temp <= 30 else (("#F59E0B", "مقبولة") if 18 <= temp <= 36 else ("#EF4444", "قاسية"))
    
    if wind > 10: score -= 20 if wind <= 18 else 50
    if wave > 0.3: score -= 15 if wave <= 0.7 else 45
    score = max(0, min(100, score))
    
    if score >= 65: label, color, adv = "نشاط عالي 🎣", "#10B981", "ظروف مثالية — الأسماك نشيطة وقريبة من السطح. وقت ممتاز للمحادق!"
    elif score >= 35: label, color, adv = "نشاط متوسط 🐟", "#F59E0B", "ظروف مقبولة — الأسماك نشيطة جزئياً مع بعض الصبر."
    else: label, color, adv = "نشاط منخفض ⚠️", "#EF4444", "ظروف صعبة — الأسماك في الأعماق والبحر ضربة."
    
    return {"label": label, "color": color, "score": score, "advice": adv, "wind_status": w_status, "wind_label": w_label, "wave_status": wv_status, "wave_label": wv_label, "temp_status": t_status, "temp_label": t_label}

def build_time_ranges(good_hours):
    if not good_hours: return []
    ranges, start, end = [], good_hours[0], good_hours[0]
    for h in good_hours[1:]:
        if h == end + 1: end = h
        else:
            ranges.append((start, end))
            start = end = h
    ranges.append((start, end))
    
    chips = []
    for s, e in ranges:
        f = lambda h: f"{h % 12 or 12}:00 {'ص' if h < 12 else 'م'}"
        chips.append(f(s) if s == e else f"{f(s)} — {f(e + 1)}")
    return chips

def get_moon_phase():
    days = (datetime.now() - datetime(2000, 1, 6)).days
    age = (days / 29.530588853 % 1) * 29.530588853
    illumination = int(round((1 - math.cos(2 * math.pi * age / 29.530588853)) / 2 * 100))
    
    if age < 1.85: return "🌑", "محاق — قمر جديد", "مدّ ربيعي قوي 💪", "#10B981", "أفضل وقت للصيد: المياه مظلمة والأسماك تتغذى بجرأة."
    elif age < 7.38: return "🌒", "هلال متصاعد", "مدّ معتدل", "#F59E0B", "نشاط جيد: الأسماك تبدأ بالتحرك والبحث النشط."
    elif age < 9.22: return "🌓", "تربيع أول", "مدّ محاقي ضعيف (فساد)", "#94A3B8", "المدّ هادئ ومستقر جداً، ومناسب لصيد القاع."
    elif age < 14.76: return "🌔", "أحدب متصاعد", "مدّ متصاعد", "#F59E0B", "نشاط ممتاز ومتزايد مع زيادة ضوء القمر."
    elif age < 16.61: return "🌕", "بدر — قمر كامل", "مدّ ربيعي قوي (حمل) 💪", "#10B981", "ذروة النشاط 🎣: أفضل ليلة صيد! التيارات قوية والضرب حامي."
    elif age < 22.15: return "🌖", "أحدب متناقص", "مدّ متناقص", "#F59E0B", "الضرب لا يزال ممتازاً والقمر يضيء الماء."
    else: return "🌗", "تربيع أخير", "مدّ ضعيف", "#64748B", "نشاط متوسط إلى هادئ، مناسب للصيد الصباحي."

# ─── جلب البيانات ───────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_weather(lat, lon):
    w_url, m_url = "https://api.open-meteo.com/v1/forecast", "https://marine-api.open-meteo.com/v1/marine"
    w_p = {"latitude": lat, "longitude": lon, "hourly": "temperature_2m,windspeed_10m", "daily": "windspeed_10m_max,temperature_2m_max", "forecast_days": 7, "timezone": "Asia/Riyadh"}
    m_p = {"latitude": lat, "longitude": lon, "hourly": "wave_height", "daily": "wave_height_max", "forecast_days": 7, "timezone": "Asia/Riyadh"}
    try: return requests.get(w_url, params=w_p, timeout=10).json(), requests.get(m_url, params=m_p, timeout=10).json()
    except: return None, None

@st.cache_data(ttl=3600)
def get_location_name(lat, lon):
    try:
        res = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ar", headers={"User-Agent": "BaharBot/2.0"}, timeout=4).json()
        return res.get("address", {}).get("city") or res.get("address", {}).get("state") or "منطقة بحرية مفتوحة"
    except: return "منطقة بحرية"

# ─── الواجهة البرمجية المباشرة ─────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🌊 BAHAR PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">المرشد البحري الذكي لرحلات الصيد والملاحة</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if "coords" not in st.session_state: st.session_state["coords"] = None
flat, flon = st.session_state["coords"] if st.session_state["coords"] else (26.85, 49.80)

display_text = f"📍 الموقع المحدد: {get_location_name(flat, flon)} ({flat:.3f}°، {flon:.3f}°)" if st.session_state["coords"] else "📍 انقر على الخريطة لتحديد موقعك البحري"
st.markdown(f'<div class="location-box">{display_text}</div>', unsafe_allow_html=True)

st.markdown('<div class="map-section-label">🗺️ خريطة الصيد التفاعلية</div>', unsafe_allow_html=True)

m = folium.Map(location=[flat, flon], zoom_start=9, tiles="CartoDB dark_matter")
m.get_root().html.add_child(folium.Element("<style>.leaflet-container, .leaflet-tile { direction: ltr !important; text-align: left !important; }</style>"))

if st.session_state["coords"]:
    folium.Marker(location=[flat, flon], icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)

map_data = st_folium(m, height=400, use_container_width=True, key="marine_map", returned_objects=["last_clicked"])

if map_data and map_data.get("last_clicked"):
    nl = (round(map_data["last_clicked"]["lat"], 5), round(map_data["last_clicked"]["lng"], 5))
    if st.session_state["coords"] != nl:
        st.session_state["coords"] = nl
        st.rerun()

# عرض التقارير الفخمة فقط إذا تم اختيار موقع
if st.session_state["coords"]:
    w_res, m_res = fetch_weather(flat, flon)
    if w_res and "hourly" in w_res:
        hw, hm = w_res["hourly"], m_res.get("hourly", {})
        curr_h = min(datetime.now().hour, len(hw.get("temperature_2m", [])) - 1)
        
        t_now = hw["temperature_2m"][curr_h]
        wind_now = hw["windspeed_10m"][curr_h]
        wave_now = hm.get("wave_height", [0]*24)[curr_h]
        
        good_hours = [i for i in range(curr_h, min(curr_h + 12, len(hw["windspeed_10m"]))) if hw["windspeed_10m"][i] <= 15 and hm.get("wave_height", [0]*24)[i] <= 0.7]
        time_ranges = build_time_ranges(good_hours)
        
        status, badge, adv = ("excellent", "badge-excellent", "البحر سياح والموج ساكن ركود!") if wind_now < 14 and wave_now < 0.5 else (("good", "badge-good", "الوضع جيد ومناسب للصيد.") if wind_now < 21 and wave_now < 0.9 else ("bad", "badge-bad", "ضربة بحر وموج عالي، خطر!"))
        status_ar = {"excellent": "ممتاز", "good": "جيد", "bad": "محظور"}
        
        # 1. بطاقة الأحوال
        st.markdown(f"""
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                <div class="card-title" style="margin-bottom:0">📊 الأحوال الحالية</div>
                <span class="{badge}">{status_ar[status]}</span>
            </div>
            <div class="metric-row">
                <div class="metric-box"><div class="metric-value">{t_now:.0f}°م</div><div class="metric-label">الحرارة</div></div>
                <div class="metric-box"><div class="metric-value">{wind_now:.0f} كم/س</div><div class="metric-label">الرياح</div></div>
                <div class="metric-box"><div class="metric-value">{wave_now:.1f} م</div><div class="metric-label">ارتفاع الموج</div></div>
            </div>
            <p class="advice-{status}">{adv}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if time_ranges:
            st.markdown(f'<div style="text-align:right;margin:-10px 0 15px 0;">' + "".join(f'<span class="range-chip">🕐 {r}</span>' for r in time_ranges[:3]) + '</div>', unsafe_allow_html=True)

        # 2. بطاقة الأسماك
        act = fish_activity_score(wind_now, wave_now, t_now)
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🐠 توقع نشاط الأسماك وحالة الضرب</div>
            <div style="text-align:center;padding:12px;background:rgba(255,255,255,0.04);border-radius:12px;border:2px solid {act['color']};color:{act['color']};font-size:1.4rem;font-weight:900;">{act['label']}</div>
            <div class="activity-bar-wrap"><div class="activity-bar-fill" style="width:{act['score']}%;background:linear-gradient(90deg,#EF4444,#F59E0B,#10B981);"></div></div>
            <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:10px;color:#CBD5E1;text-align:right;font-size:0.85rem;margin-top:8px;">{act['advice']}</div>
        </div>
        """, unsafe_allow_html=True)

        # 3. بطاقة القمر (بدون أكواد خربانة)
        emoji, name, tide, t_color, tip = get_moon_phase()
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🌙 حالة القمر وحركة المايه</div>
            <div class="moon-row">
                <div class="moon-emoji-wrap">{emoji}</div>
                <div class="moon-info">
                    <div class="moon-phase-name">{name}</div>
                    <div style="margin-top:6px;"><span style="background:{t_color}22;color:{t_color};border:1px solid {t_color}55;border-radius:16px;padding:3px 12px;font-size:0.8rem;font-weight:800;">{tide}</span></div>
                </div>
            </div>
            <div class="moon-tip" style="border-right-color:{t_color};">{tip}</div>
        </div>
        """, unsafe_allow_html=True)
