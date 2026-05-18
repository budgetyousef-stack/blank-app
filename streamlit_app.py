import streamlit as st
import requests
import folium
import pandas as pd
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Marine Tracker PRO",
    page_icon="🌊",
    layout="centered", # ممتاز وجاهز لشاشات الجوال
    initial_sidebar_state="collapsed"
)

# 2. تصميم الواجهة الاحترافي بالـ CSS الموزون
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; direction: rtl; }
    .stApp { background-color: #0F172A; }
    
    /* تثبيت حاوية الخريطة بعرض الجوال لمنع التشويه والبياض */
    .stFoliumMap, iframe { width: 100% !important; border-radius: 16px !important; border: 1px solid #334155 !important; }
    
    .main-title { color: #38BDF8; text-align: center; font-size: 2.2rem; font-weight: 800; margin-bottom: 0; }
    .sub-title { color: #64748B; text-align: center; font-size: 1rem; font-weight: 600; margin-top: 4px; }
    .divider { width: 60px; height: 4px; background: linear-gradient(90deg, #38BDF8, #0ea5e9); border-radius: 4px; margin: 0 auto 24px auto; }
    
    /* مستطيل العنوان الفردي الفخم */
    .location-box { background-color: #1E293B; border: 2px solid #38BDF8; border-radius: 14px; padding: 14px; text-align: center; color: #F1F5F9; font-size: 1.1rem; font-weight: 700; margin-bottom: 24px; }
    .card { background-color: #1E293B; border: 1px solid #334155; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
    .card-title { color: #38BDF8; font-size: 1.1rem; font-weight: 700; margin-bottom: 16px; text-align: right; }
    
    .metric-row { display: flex; gap: 10px; margin-bottom: 16px; direction: rtl; }
    .metric-box { flex: 1; background: rgba(255,255,255,0.04); border-radius: 12px; padding: 12px 8px; text-align: center; }
    .metric-value { font-size: 1.15rem; font-weight: 700; color: #F1F5F9; }
    .metric-label { font-size: 0.75rem; color: #64748B; }
    
    .badge-excellent { background: #10B981; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
    .badge-good      { background: #F59E0B; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
    .badge-bad       { background: #EF4444; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
    
    .activity-bar-wrap { background: #0F172A; border-radius: 8px; height: 14px; overflow: hidden; margin: 8px 0 4px 0; }
    .activity-bar-fill { height: 100%; border-radius: 8px; }
    .activity-labels { display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748B; direction: rtl; }
    
    .hour-chip { display: inline-block; background: #0ea5e9; color: #0F172A; font-weight: 700; font-size: 0.8rem; padding: 4px 12px; border-radius: 20px; margin: 3px 0 3px 4px; }
    .advice-excellent { color: #10B981; font-weight: 600; text-align: right; }
    .advice-good      { color: #F59E0B; font-weight: 600; text-align: right; }
    .advice-bad       { color: #EF4444; font-weight: 600; text-align: right; }
    
    .factor-row { display: flex; gap: 8px; margin-top: 14px; direction: rtl; }
    .factor-box { flex: 1; background: rgba(255,255,255,0.03); border-radius: 10px; padding: 10px 6px; text-align: center; }
    .footer { text-align: center; color: #334155; font-size: 0.75rem; margin-top: 32px; }
    </style>
""", unsafe_allow_html=True)

DAYS_AR = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

# 3. نموذج تحليل نشاط السمك الحسابي الذكي
def fish_activity_score(wind: float, wave: float, temp: float) -> dict:
    score = 100
    w_status, w_label = ("#10B981", "مثالي") if wind <= 10 else (("#F59E0B", "مقبول") if wind <= 18 else ("#EF4444", "شديد"))
    wv_status, wv_label = ("#10B981", "هادئ") if wave <= 0.3 else (("#F59E0B", "خفيف") if wave <= 0.6 else ("#EF4444", "عالي"))
    t_status, t_label = ("#10B981", "مثالية") if 22 <= temp <= 30 else (("#F59E0B", "مقبولة") if 18 <= temp <= 36 else ("#EF4444", "قاسية"))
    
    if wind > 10: score -= 20 if wind <= 18 else 50
    if wave > 0.3: score -= 15 if wave <= 0.6 else 45
    score = max(0, min(100, score))
    
    if score >= 65: level, label, color, advice = "high", "نشاط عالي 🎣", "#10B981", "ظروف مثالية — الأسماك نشيطة وقريبة من السطح. أنسب وقت للمحادق وصيد السيف!"
    elif score >= 35: level, label, color, advice = "medium", "نشاط متوسط 🐟", "#F59E0B", "ظروف مقبولة — الأسماك نشيطة جزئياً. الصيد ممكن مع بعض الصبر."
    else: level, label, color, advice = "low", "نشاط منخفض ⚠️", "#EF4444", "ظروف صعبة — الأسماك في الأعماق والبحر غير مناسب حالياً."
    
    return {"level": level, "label": label, "color": color, "score": score, "advice": advice, "wind_status": w_status, "wind_label": w_label, "wave_status": wv_status, "wave_label": wv_label, "temp_status": t_status, "temp_label": t_label}

# 4. جلب البيانات من الـ APIs
@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float):
    w_url = "https://api.open-meteo.com/v1/forecast"
    m_url = "https://marine-api.open-meteo.com/v1/marine"
    w_params = {"latitude": lat, "longitude": lon, "hourly": "temperature_2m,windspeed_10m", "daily": "windspeed_10m_max,temperature_2m_max", "forecast_days": 7, "timezone": "Asia/Riyadh"}
    m_params = {"latitude": lat, "longitude": lon, "hourly": "wave_height", "daily": "wave_height_max", "forecast_days": 7, "timezone": "Asia/Riyadh"}
    return requests.get(w_url, params=w_params, timeout=10).json(), requests.get(m_url, params=m_params, timeout=10).json()

@st.cache_data(ttl=3600)
def get_location_name(lat: float, lon: float) -> str:
    try:
        res = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ar", headers={'User-Agent': 'MarineBot/1.0'}, timeout=3).json()
        addr = res.get("address", {})
        return addr.get("city") or addr.get("town") or addr.get("village") or addr.get("state") or "منطقة بحرية مفتوحة"
    except: return "منطقة بحرية"

# ─── الواجهة البرمجية ──────────────────────────────────────────────────────────

st.markdown('<h1 class="main-title">🌊 MARINE TRACKER</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">المرشد البحري الذكي لرحلات الصيد</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# إدارة حالة الإحداثيات في الجلسة لمنع إعادة التحميل العشوائي
if "coords" not in st.session_state: 
    st.session_state["coords"] = None

# خريطة البداية الافتراضية للشرقية (الجبيل)
flat, flon = st.session_state["coords"] if st.session_state["coords"] else (26.85, 49.80)

# مربع العنوان الفردي الذكي والوحيد (تم مسح المستطيل الزائد)
if st.session_state["coords"]:
    display_text = f"📍 الموقع المحدد: {get_location_name(flat, flon)} ({flat:.3f}, {flon:.3f})"
else: 
    display_text = "📍 الرجاء اختيار موقع من الخريطة بالأسفل لتحديده"

st.markdown(f'<div class="location-box">{display_text}</div>', unsafe_allow_html=True)

# بطاقة الخريطة
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🗺️ خريطة الصيد التفاعلية</div>', unsafe_allow_html=True)

m = folium.Map(location=[flat, flon], zoom_start=9, tiles="CartoDB dark_matter")

if st.session_state["coords"]:
    folium.Marker(location=[flat, flon], icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)
    folium.Circle(location=[flat, flon], radius=4000, color="#38BDF8", fill=True, fill_opacity=0.15).add_to(m)

# عرض الخريطة الآمن والمستقر
map_data = st_folium(m, height=400, use_container_width=True, key="marine_map")

# التقاط النقرات بعمق لمنع أخطاء الـ Rerun اللاهوائي
if map_data and map_data.get("last_clicked"):
    nl_lat, nl_lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    if st.session_state["coords"] != (nl_lat, nl_lng):
        st.session_state["coords"] = (nl_lat, nl_lng)
        st.rarun() # تحديث الصفحة بشكل مستقر وآمن برمجياً
st.markdown('</div>', unsafe_allow_html=True)

# بطاقات التحليلات والتقارير عند اختيار الموقع
if st.session_state["coords"]:
    try:
        w_res, m_res = fetch_weather(flat, flon)
        hw, hm = w_res["hourly"], m_res["hourly"]
        curr_h = datetime.now().hour
        
        t_now = hw["temperature_2m"][curr_h]
        wind_now = hw["windspeed_10m"][curr_h]
        wave_now = hm["wave_height"][curr_h]
        
        best_hours = [f"{i%12 or 12}:00 {'ص' if i<12 else 'م'}" for i in range(curr_h, min(curr_h+12, 24)) if hw["windspeed_10m"][i] <= 15 and hm["wave_height"][i] <= 0.6]
        
        status, badge, adv = ("excellent", "badge-excellent", "الوضع ممتاز جداً: بحر سياح، الموج ساكن والهوا ركود.") if wind_now < 14 and wave_now < 0.5 else (("good", "badge-good", "الوضع جيد: جلب مناسب، حركة موج خفيفة.") if wind_now < 20 and wave_now < 0.8 else ("bad", "badge-bad", "الوضع صعب: ضربة بحر موج عالي وهوا تارس."))
        status_ar = {"excellent": "ممتاز", "good": "جيد", "bad": "محظور"}
        
        # بطاقة الأحوال الحالية
        st.markdown(f'<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;"><div class="card-title" style="margin-bottom:0">📊 الأحوال الحالية في الموقع</div><span class="{badge}">{status_ar[status]}</span></div><div class="metric-row"><div class="metric-box"><div class="metric-value">{t_now:.0f}°م</div><div class="metric-label">الحرارة</div></div><div class="metric-box"><div class="metric-value">{wind_now:.0f} كم/س</div><div class="metric-label">الرياح</div></div><div class="metric-box"><div class="metric-value">{wave_now:.1f} م</div><div class="metric-label">الموج</div></div></div><p class="advice-{status}">{adv}</p>', unsafe_allow_html=True)
        if best_hours: st.markdown(f'<div style="border-top:1px solid #334155;padding-top:12px;"><div style="color:#94A3B8;font-size:0.82rem;text-align:right;">أفضل ساعات الصيد اليوم:</div>' + "".join(f'<span class="hour-chip">{h}</span>' for h in best_hours[:5]) + '</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # بطاقة مؤشر السمك
        act = fish_activity_score(wind_now, wave_now, t_now)
        st.markdown(f'<div class="card"><div class="card-title">🐠 توقع نشاط الأسماك وحالة الضرب</div><div style="text-align:center;padding:12px;background:rgba(255,255,255,0.04);border-radius:12px;border:2px solid {act["color"]};color:{act["color"]};font-size:1.4rem;font-weight:800;">{act["label"]}</div><div class="activity-labels"><span>منخفض</span><span>متوسط</span><span>عالي</span></div><div class="activity-bar-wrap"><div class="activity-bar-fill" style="width:{act["score"]}%;background:linear-gradient(90deg,#10B981,#F59E0B)"></div></div><div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:12px;margin-top:10px;color:#CBD5E1;text-align:right;">{act["advice"]}</div><div class="factor-row"><div class="factor-box"><div style="color:{act["wind_status"]};font-weight:700;">{act["wind_label"]}</div><div class="factor-label">الرياح</div></div><div class="factor-box"><div style="color:{act["wave_status"]};font-weight:700;">{act["wave_label"]}</div><div class="factor-label">الموج</div></div><div class="factor-box"><div style="color:{act["temp_status"]};font-weight:700;">{act["temp_label"]}</div><div class="factor-label">الحرارة</div></div></div></div>', unsafe_allow_html=True)
        
        # بطاقة رسم بياني 7 أيام
        dw, dt, dwv = w_res["daily"]["windspeed_10m_max"], w_res["daily"]["temperature_2m_max"], m_res["daily"]["wave_height_max"]
        lbls = [DAYS_AR[(datetime.now() + timedelta(days=i)).weekday() % 7] if i > 0 else "اليوم" for i in range(7)]
        st.markdown('<div class="card"><div class="card-title">📈 توقعات السبعة أيام القادمة للمنطقة</div>', unsafe_allow_html=True)
        st.line_chart(pd.DataFrame({"اليوم": lbls, "الرياح (كم/س)": [round(v) for v in dw], "الأمواج (م)": [round(v,2) for v in dwv], "الحرارة (°م)": [round(v) for v in dt]}).set_index("اليوم"), height=210, use_container_width=True, color=["#38BDF8", "#10B981", "#F59E0B"])
        st.markdown('</div>', unsafe_allow_html=True)
    except: 
        st.error("يرجى التأكد من اختيار نقطة داخل البحر لتشغيل التحليلات.")
