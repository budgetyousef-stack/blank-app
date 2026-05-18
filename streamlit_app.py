import streamlit as st
import requests
import folium
import pandas as pd
import math
import altair as alt
import json
import os
import time
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

#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

.map-section-label { color: #38BDF8; font-size: clamp(0.95rem, 2.8vw, 1.1rem); font-weight: 800; text-align: right; margin-bottom: 8px; padding: 0 2px; }
.stFoliumMap { border-radius: 14px !important; overflow: hidden !important; }
iframe[title="st_folium.frontend"] { border-radius: 14px !important; border: 1px solid #1E3A5F !important; width: 100% !important; }

.location-box { background: linear-gradient(135deg, #1E293B 0%, #0F2137 100%); border: 2px solid #38BDF8; border-radius: 14px; padding: 14px 18px; text-align: center; color: #F1F5F9; font-size: clamp(0.9rem, 2.8vw, 1.05rem); font-weight: 700; margin-bottom: 16px; box-shadow: 0 0 20px rgba(56,189,248,0.12); }
.card { background: linear-gradient(145deg, #1E293B 0%, #162032 100%); border: 1px solid #1E3A5F; border-radius: 18px; padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.3); }
.card-title { color: #38BDF8; font-size: clamp(0.95rem, 2.8vw, 1.1rem); font-weight: 800; margin-bottom: 14px; text-align: right; }

.metric-row { display: flex; gap: 10px; margin-bottom: 14px; direction: rtl; flex-wrap: wrap; }
.metric-box { flex: 1; min-width: 80px; background: rgba(56,189,248,0.06); border: 1px solid rgba(56,189,248,0.15); border-radius: 12px; padding: 12px 6px; text-align: center; }
.metric-value { font-size: clamp(1rem, 3vw, 1.2rem); font-weight: 800; color: #F1F5F9; }
.metric-label { font-size: clamp(0.68rem, 2vw, 0.78rem); color: #64748B; margin-top: 3px; }

.badge-excellent { background: linear-gradient(135deg,#059669,#10B981); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:800; }
.badge-good      { background: linear-gradient(135deg,#D97706,#F59E0B); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:800; }
.badge-bad       { background: linear-gradient(135deg,#DC2626,#EF4444); color:white; padding:5px 16px; border-radius:20px; font-size:0.82rem; font-weight:800; }

.advice-excellent { color:#10B981; font-weight:700; text-align:right; font-size:0.9rem; margin-top:10px; line-height:1.6; }
.advice-good      { color:#F59E0B; font-weight:700; text-align:right; font-size:0.9rem; margin-top:10px; line-height:1.6; }
.advice-bad       { color:#EF4444; font-weight:700; text-align:right; font-size:0.9rem; margin-top:10px; line-height:1.6; }

.act-ring-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px 10px 10px 10px; }
.act-ring-inner { position: relative; width: 160px; height: 160px; }
.act-ring-inner svg { transform: rotate(-90deg); }
.act-ring-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; pointer-events: none; }
.act-ring-score { font-size: 2.4rem; font-weight: 900; color: #F1F5F9; line-height: 1; }
.act-ring-label { font-size: 0.72rem; color: #64748B; margin-top: 4px; }
.act-ring-stars { font-size: 1.1rem; margin-top: 10px; letter-spacing: 3px; }
.act-ring-status { font-size: 1rem; font-weight: 800; margin-top: 6px; }

.solunar-wrap { display: flex; gap: 12px; direction: rtl; margin-bottom: 16px; }
.solunar-col { flex: 1; border-radius: 16px; padding: 16px 14px; }
.solunar-major { background: linear-gradient(145deg, #0c2a4a, #0a1e38); border: 1px solid rgba(56,189,248,0.35); }
.solunar-minor { background: linear-gradient(145deg, #1a1f35, #111827); border: 1px solid rgba(167,139,250,0.25); }
.solunar-heading { font-size: 0.78rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px; text-align: center; }
.solunar-major .solunar-heading { color: #38BDF8; }
.solunar-minor .solunar-heading { color: #A78BFA; }
.solunar-icon { font-size: 1.6rem; text-align: center; margin-bottom: 8px; }
.sol-chip { border-radius: 10px; padding: 9px 10px; margin: 7px 0; text-align: center; font-weight: 700; font-size: 0.88rem; line-height: 1.4; }
.sol-chip-major { background: rgba(56,189,248,0.12); border: 1px solid rgba(56,189,248,0.3); color: #E0F2FE; }
.sol-chip-minor { background: rgba(167,139,250,0.10); border: 1px solid rgba(167,139,250,0.25); color: #EDE9FE; }
.sol-chip-label { font-size: 0.65rem; color: #64748B; margin-top: 3px; }
.tide-details-box { background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.05); padding: 14px; border-radius: 14px; margin-top: -10px; margin-bottom: 16px; }

.cache-status-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 800; margin-bottom: 12px; background: rgba(56,189,248,0.08); border: 1px solid rgba(56,189,248,0.2); color: #38BDF8; }

@media (max-width: 480px) { .block-container { padding: 0.6rem 0.6rem 2rem 0.6rem !important; } .card { padding: 14px 12px; border-radius: 14px; } .metric-row { gap: 6px; } }
</style>
""", unsafe_allow_html=True)

# ─── ثوابت ودوال ──────────────────────────────────────────────────────────────
DAYS_AR   = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
MONTHS_AR = ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]

def _day_option_label(offset: int) -> str:
    d = datetime.now() + timedelta(days=offset)
    day_str = f"{d.day} {MONTHS_AR[d.month - 1]}"
    if offset == 0: return f"اليوم ({day_str})"
    else: return f"{DAYS_AR[(d.weekday() + 1) % 7]} ({day_str})"

def fish_activity_score(wind: float, wave: float, temp: float, swell: float = 0.0) -> dict:
    score = 100
    if wind <= 10: w_status, w_label = "#10B981", "مثالي"
    elif wind <= 18: w_status, w_label = "#F59E0B", "مقبول"; score -= 20
    else: w_status, w_label = "#EF4444", "شديد"; score -= 50

    if wave <= 0.3: wv_status, wv_label = "#10B981", "هادئ"
    elif wave <= 0.7: wv_status, wv_label = "#F59E0B", "خفيف"; score -= 15
    else: wv_status, wv_label = "#EF4444", "عالي"; score -= 45

    if swell > 1.5: score -= 15
    score = max(5, min(100, score))

    if score >= 65: return {"label": "نشاط عالي 🎣", "color": "#10B981", "score": score, "advice": "ظروف مثالية — الأسماك نشيطة وقريبة من السطح. أنسب وقت للمحادق!"}
    elif score >= 35: return {"label": "نشاط متوسط 🐟", "color": "#F59E0B", "score": score, "advice": "ظروف مقبولة — الأسماك نشيطة جزئياً. الصيد ممكن مع بعض الصبر."}
    else: return {"label": "نشاط منخفض ⚠️", "color": "#EF4444", "score": score, "advice": "ظروف صعبة — البحر غير مناسب حالياً."}

def _tide_amplitudes(lat: float, lon: float) -> dict:
    if (23 <= lat <= 30) and (48 <= lon <= 57): return dict(M2=0.88, S2=0.26, K1=0.15, O1=0.09, base=1.05)
    return dict(M2=0.60, S2=0.20, K1=0.18, O1=0.12, base=0.75)

def compute_tide_profile(lat: float, lon: float, for_date: datetime) -> list:
    amp = _tide_amplitudes(lat, lon)
    t0 = (for_date.replace(hour=0, minute=0) - datetime(2000, 1, 1)).total_seconds() / 3600.0
    periods = dict(M2=12.4206, S2=12.0000, K1=23.9345, O1=25.8194)
    heights = []
    for h in range(25):
        t = t0 + h; level = amp["base"]
        for name, p in periods.items(): level += amp[name] * math.cos(2.0 * math.pi * t / p - 0.5)
        heights.append(round(max(0.05, level), 2))
    return heights

def find_tide_events(heights: list) -> dict:
    highs, lows = [], []
    for i in range(1, len(heights) - 1):
        y1, y2, y3 = heights[i - 1], heights[i], heights[i + 1]
        denom = y1 - 2*y2 + y3
        if denom != 0: dx = (y1 - y3) / (2 * denom); val = y2 - ((y1 - y3)**2) / (8 * denom)
        else: dx, val = 0, y2
        exact_h = i + dx
        val = round(max(0.0, val), 2)
        if y2 >= y1 and y2 >= y3: highs.append((exact_h, val))
        elif y2 <= y1 and y2 <= y3: lows.append((exact_h, val))
    return {"highs": highs, "lows": lows}

def get_moon_phase(date: datetime) -> dict:
    synodic, ref_jdn = 29.53059, 2451549.26
    y, m, d = date.year, date.month, date.day
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    jdn = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045 + (date.hour - 12) / 24.0
    age = (jdn - ref_jdn) % synodic
    if age < 1.85: return {"emoji": "🌑", "phase_ar": "محاق — قمر جديد", "tip": "المياه مظلمة والأسماك تتغذى بجرأة قرب السطح.", "age": age}
    elif age < 7.38: return {"emoji": "🌒", "phase_ar": "هلال متصاعد", "tip": "تيارات جيدة وبداية حركة ممتازة للأسماك.", "age": age}
    elif age < 16.61: return {"emoji": "🌕", "phase_ar": "بدر — قمر كامل", "tip": "ذروة تيار الحمل الفعال! الأسماك في أقصى نشاطها العالي.", "age": age}
    else: return {"emoji": "🌘", "phase_ar": "هلال متناقص", "tip": "النشاط يقل تدريجياً ويفضل الصيد الساحلي الهادئ.", "age": age}

def compute_solunar_times(moon_age: float, lon: float) -> dict:
    synodic = 29.53059
    moon_transit_local = (12.0 + moon_age * (24.0 * 50.0 / (60.0 * synodic)) + 3 + lon / 15.0) % 24.0
    def fmt_h(h):
        h = h % 24; period = "ص" if h < 12 else "م"
        return f"{int(h)%12 or 12}:{int(round((h%1)*60)):02d} {period}"
    return {
        "major": [f"{fmt_h(moon_transit_local-1)} — {fmt_h(moon_transit_local+1)}", f"{fmt_h(moon_transit_local+11.4)} — {fmt_h(moon_transit_local+13.4)}"],
        "minor": [f"{fmt_h(moon_transit_local+5.2)} — {fmt_h(moon_transit_local+6.2)}", f"{fmt_h(moon_transit_local+17.6)} — {fmt_h(moon_transit_local+18.6)}"]
    }

def fetch_weather_live(lat: float, lon: float):
    w_url, m_url = "https://api.open-meteo.com/v1/forecast", "https://marine-api.open-meteo.com/v1/marine"
    w_params = {"latitude": lat, "longitude": lon, "hourly": "temperature_2m,apparent_temperature,windspeed_10m,winddirection_10m", "forecast_days": 7, "timezone": "Asia/Riyadh"}
    m_params = {"latitude": lat, "longitude": lon, "hourly": "wave_height,wave_period,swell_wave_height,sea_surface_temperature", "forecast_days": 7, "timezone": "Asia/Riyadh"}
    try: 
        w_res = requests.get(w_url, params=w_params, timeout=10).json()
        m_res = requests.get(m_url, params=m_params, timeout=10).json()
        return w_res, m_res
    except: 
        return None, None

def get_cached_marine_data(lat: float, lon: float):
    cache_file = "marine_data_cache.json"
    current_time = time.time()
    one_week_seconds = 7 * 24 * 3600
    loc_key = f"{round(lat, 2)},{round(lon, 2)}"
    
    cache_data = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f: cache_data = json.load(f)
        except: cache_data = {}
            
    if loc_key in cache_data:
        saved_item = cache_data[loc_key]
        if current_time - saved_item.get("timestamp", 0) < one_week_seconds:
            return saved_item["w_res"], saved_item["m_res"], "LOCAL_CACHE"
            
    w_res, m_res = fetch_weather_live(lat, lon)
    if w_res and "hourly" in w_res and m_res and "hourly" in m_res:
        cache_data[loc_key] = {"timestamp": current_time, "w_res": w_res, "m_res": m_res}
        try:
            with open(cache_file, "w", encoding="utf-8") as f: json.dump(cache_data, f, ensure_ascii=False, indent=4)
        except: pass
        return w_res, m_res, "LIVE_UPDATED"
        
    return None, None, "ERROR"

@st.cache_data(ttl=86400)
def get_location_name(lat: float, lon: float) -> str:
    try:
        res = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ar", headers={"User-Agent": "MarineTrackerPRO/2.0"}).json()
        addr = res.get("address", {})
        return addr.get("city") or addr.get("town") or addr.get("state") or "منطقة بحرية مفتوحة"
    except: return "منطقة بحرية"

def get_safe(lst, idx, default=0.0):
    try: return float(lst[idx]) if lst[idx] is not None else default
    except: return default

# ─── واجهة المستخدم ───────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🌊 MARINE TRACKER</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">المرشد البحري الذكي لرحلات الصيد</p>', unsafe_allow_html=True)

if "coords" not in st.session_state: st.session_state["coords"] = (26.9239, 49.8681)

flat, flon = st.session_state["coords"]
st.markdown(f'<div class="location-box">📍 الموقع الحالي: {get_location_name(flat, flon)} ({flat:.3f}°، {flon:.3f}°)</div>', unsafe_allow_html=True)

_day_options = [_day_option_label(i) for i in range(7)]
_selected_day = st.segmented_control(label="اختر اليوم", options=_day_options, default=_day_options[0], label_visibility="collapsed")
day_offset = _day_options.index(_selected_day) if _selected_day in _day_options else 0

st.markdown('<div class="map-section-label">🗺️ خريطة قوقل مابس التفاعلية (انقر لاختيار مكان الصيد الجديد)</div>', unsafe_allow_html=True)
m = folium.Map(location=[flat, flon], zoom_start=11, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Maps Satellite Hybrid")
folium.Marker(location=[flat, flon], icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)

map_data = st_folium(m, height=350, use_container_width=True, key="google_maps_satellite")
if map_data and map_data.get("last_clicked"):
    new_coords = (round(map_data["last_clicked"]["lat"], 5), round(map_data["last_clicked"]["lng"], 5))
    if st.session_state["coords"] != new_coords:
        st.session_state["coords"] = new_coords
        st.rerun()

w_res, m_res, source_info = get_cached_marine_data(flat, flon)

if w_res and m_res:
    hw, hm = w_res["hourly"], m_res["hourly"]
    max_idx = min(len(hw.get("temperature_2m", [])) - 1, len(hm.get("wave_height", [])) - 1)
    
    start_idx = day_offset * 24
    end_idx = min(start_idx + 24, max_idx + 1)
    
    # 💡 النظام الذكي لتغيير العناوين والمسميات بناءً على اليوم المختار
    if day_offset == 0:
        curr_h = datetime.now().hour
        data_idx = min((day_offset * 24) + curr_h, max_idx) if max_idx >= 0 else 0
        
        t_val = get_safe(hw.get("temperature_2m", []), data_idx)
        wind_val = get_safe(hw.get("windspeed_10m", []), data_idx)
        wind_dir = get_safe(hw.get("winddirection_10m", []), data_idx)
        wave_val = get_safe(hm.get("wave_height", []), data_idx)
        swell_val = get_safe(hm.get("swell_wave_height", []), data_idx)
        sst_val = get_safe(hm.get("sea_surface_temperature", []), data_idx)
        
        card_title = "📊 القياسات الحيوية (الآن)"
        t_label, w_label, wv_label, sst_label = "الحرارة الحالية", "الرياح اللحظية", "الموج الحالي", "حرارة البحر"
    else:
        t_vals = [get_safe(hw.get("temperature_2m", []), i) for i in range(start_idx, end_idx)]
        wind_vals = [get_safe(hw.get("windspeed_10m", []), i) for i in range(start_idx, end_idx)]
        wave_vals = [get_safe(hm.get("wave_height", []), i) for i in range(start_idx, end_idx)]
        swell_vals = [get_safe(hm.get("swell_wave_height", []), i) for i in range(start_idx, end_idx)]
        sst_vals = [get_safe(hm.get("sea_surface_temperature", []), i) for i in range(start_idx, end_idx)]
        
        t_val = max(t_vals) if t_vals else 0.0
        wind_val = max(wind_vals) if wind_vals else 0.0
        wave_val = max(wave_vals) if wave_vals else 0.0
        swell_val = max(swell_vals) if swell_vals else 0.0
        sst_val = (sum(sst_vals) / len(sst_vals)) if sst_vals else 0.0
        wind_dir = get_safe(hw.get("winddirection_10m", []), start_idx + 12)
        
        card_title = f"📊 التوقعات العظمى لليوم المختار"
        t_label, w_label, wv_label, sst_label = "أعلى حرارة", "أقصى سرعة رياح", "أعلى موج", "متوسط حرارة البحر"

    arrow_style = f"transform: rotate({wind_dir}deg); display: inline-block; font-size: 1.1rem; color: #38BDF8;"
    if wind_val < 14 and wave_val < 0.5: status, badge, adv = "excellent", "badge-excellent", "الوضع ممتاز: بحر هادئ تماماً وحركة مريحة للصيد."
    elif wind_val < 22 and wave_val < 0.9: status, badge, adv = "good", "badge-good", "الوضع جيد: بحر خفيف ومناسب للمحادق الساحلية مع أخذ الحيطة."
    else: status, badge, adv = "bad", "badge-bad", "الوضع محظور: رياح نشطة وموج عالي، يفضل تأجيل الكشتة البحرية."

    st.markdown(f"""
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <div class="card-title" style="margin-bottom:0">{card_title}</div>
        <span class="{badge}">جو {_selected_day.split()[0]}</span>
      </div>
      <div class="metric-row">
        <div class="metric-box"><div class="metric-value">{t_val:.0f}°م</div><div class="metric-label">{t_label}</div></div>
        <div class="metric-box"><div class="metric-value">{wind_val:.0f} كم/س</div><div class="metric-label">{w_label} <span style="{arrow_style}">↑</span></div></div>
        <div class="metric-box"><div class="metric-value">{wave_val:.1f} م</div><div class="metric-label">{wv_label}</div></div>
        <div class="metric-box"><div class="metric-value">{sst_val:.1f}°م</div><div class="metric-label">{sst_label}</div></div>
      </div>
      <p class="advice-{status}">💡 {adv}</p>
    </div>
    """, unsafe_allow_html=True)

    act = fish_activity_score(wind_val, wave_val, t_val, swell_val)
    score, color = act["score"], act["color"]
    radius = 68; circ = 2 * math.pi * radius; filled = circ * score / 100
    stars_html = "★" * int(round(score / 20)) + "☆" * (5 - int(round(score / 20)))
    
    st.markdown(f"""
    <div class="card">
      <div class="card-title">🐠 كفاءة الصيد السطحي والقاعي</div>
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
          <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:12px;color:#CBD5E1;font-size:0.9rem;line-height:1.8;">{act['advice']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── 📉 منحنى المد والجزر (ALTAIR) ───
    try:
        target_date = datetime.now() + timedelta(days=day_offset)
        tide_heights = compute_tide_profile(flat, flon, target_date)
        events = find_tide_events(tide_heights)

        labels_12h = []
        for h in range(25):
            p = "ص" if h < 12 or h == 24 else "م"
            labels_12h.append(f"{h % 12 or 12}:00 {p}")

        tide_df = pd.DataFrame({"hour": list(range(25)), "height": tide_heights, "label": labels_12h})

        chart = alt.Chart(tide_df).mark_area(
            line={'color': '#38BDF8', 'strokeWidth': 3},
            color=alt.Gradient(
                gradient='linear', stops=[alt.GradientStop(color='rgba(56,189,248,0.6)', offset=0), alt.GradientStop(color='rgba(56,189,248,0.0)', offset=1)],
                x1=1, x2=1, y1=0, y2=1
            ),
            interpolate='monotone'
        ).encode(
            x=alt.X('hour:Q', axis=alt.Axis(
                values=[0, 4, 8, 12, 16, 20, 24],
                labelExpr="datum.value == 0 ? '12 ص' : datum.value == 12 ? '12 م' : datum.value == 24 ? '12 ص' : datum.value < 12 ? datum.value + ' ص' : (datum.value - 12) + ' م'",
                labelColor="#94A3B8", gridColor="rgba(255,255,255,0.05)", title=None, labelFont="Cairo", labelFontSize=11
            )),
            y=alt.Y('height:Q', scale=alt.Scale(domain=[min(tide_heights)-0.2, max(tide_heights)+0.2]), axis=alt.Axis(
                title=None, labelColor="#94A3B8", gridColor="rgba(255,255,255,0.05)", labelFont="Cairo", format=".1f"
            )),
            tooltip=[alt.Tooltip('label:N', title='الوقت'), alt.Tooltip('height:Q', title='الارتفاع (م)')]
        ).properties(height=200).configure_view(strokeWidth=0)

        st.markdown('<div class="map-section-label" style="margin-top:12px;">📉 حركة المد والجزر السلسة (نظام 12 ساعة)</div>', unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)

        st.markdown('<div class="tide-details-box">', unsafe_allow_html=True)
        c_low, c_high = st.columns(2)
        
        def fmt_exact_time(h_float):
            if h_float < 0: h_float += 24
            h_int = int(h_float) % 24
            m_int = int(round((h_float % 1) * 60))
            if m_int == 60: h_int = (h_int + 1) % 24; m_int = 0
            p = "ص" if h_int < 12 else "م"
            return f"{h_int % 12 or 12:02d}:{m_int:02d} {p}"
            
        with c_low:
            st.markdown("<div style='color:#94A3B8; font-size:0.85rem; font-weight:700; margin-bottom:8px;'>🌊 Low Tides (أدنى جزر):</div>", unsafe_allow_html=True)
            for h_exact, val in events["lows"][:2]:
                st.markdown(f"<div style='color:#E2E8F0; font-size:1rem; font-weight:700; margin-bottom:4px;'>{val:.2f} م <span style='color:#64748B; font-weight:400; font-size:0.85rem;'>عند</span> {fmt_exact_time(h_exact)}</div>", unsafe_allow_html=True)
        with c_high:
            st.markdown("<div style='color:#38BDF8; font-size:0.85rem; font-weight:700; margin-bottom:8px;'>🌊 High Tides (أعلى مد):</div>", unsafe_allow_html=True)
            for h_exact, val in events["highs"][:2]:
                st.markdown(f"<div style='color:#38BDF8; font-size:1rem; font-weight:700; margin-bottom:4px;'>{val:.2f} م <span style='color:#64748B; font-weight:400; font-size:0.85rem;'>عند</span> {fmt_exact_time(h_exact)}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception: pass

    # ─── أوقات الصيد المثلى (Solunar) ───
    try:
        moon = get_moon_phase(datetime.now() + timedelta(days=day_offset))
        sol = compute_solunar_times(moon["age"], flon)
        st.markdown(f"""
        <div class="card">
          <div class="card-title">⏱️ فترات الصيد الذهبية (حسب الجذب الفلكي)</div>
          <div class="solunar-wrap">
            <div class="solunar-col solunar-major">
              <div class="solunar-icon">🌊</div>
              <div class="solunar-heading">MAJOR TIMES</div>
              <div class="sol-chip sol-chip-major">{sol["major"][0]}<div class="sol-chip-label">حركة أسماك كثيفة</div></div>
              <div class="sol-chip sol-chip-major">{sol["major"][1]}<div class="sol-chip-label">حركة أسماك كثيفة</div></div>
            </div>
            <div class="solunar-col solunar-minor">
              <div class="solunar-icon">🌙</div>
              <div class="solunar-heading">MINOR TIMES</div>
              <div class="sol-chip sol-chip-minor">{sol["minor"][0]}<div class="sol-chip-label">نشاط مرصود وجيز</div></div>
              <div class="sol-chip sol-chip-minor">{sol["minor"][1]}<div class="sol-chip-label">نشاط مرصود وجيز</div></div>
            </div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 10px; font-size: 0.85rem; color: #CBD5E1; text-align: right;">
            <strong>وضع القمر الحالي {moon['emoji']} ({moon['phase_ar']}):</strong> {moon['tip']}
          </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception: pass
else:
    st.error("⚠️ لم نتمكن من جلب بيانات الطقس من السيرفر. يرجى المحاولة لاحقاً.")
