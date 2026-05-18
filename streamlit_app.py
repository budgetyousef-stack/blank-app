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

# ─── CSS احترافي متجاوب (RTL) ─────────────────────────────────────────────────
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

/* إخفاء عناصر Streamlit الافتراضية */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

/* الخريطة */
.stFoliumMap { border-radius: 16px !important; overflow: hidden !important; border: 1px solid #1E3A5F !important; }
.map-section-label { color: #38BDF8; font-size: 1.1rem; font-weight: 800; text-align: right; margin-bottom: 8px; }

/* البطاقات */
.card {
    background: linear-gradient(145deg, #1E293B 0%, #162032 100%);
    border: 1px solid #1E3A5F;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.card-title { color: #38BDF8; font-size: 1.05rem; font-weight: 800; margin-bottom: 14px; text-align: right; }

/* المقاييس */
.metric-row { display: flex; gap: 10px; margin-bottom: 14px; direction: rtl; flex-wrap: wrap; }
.metric-box {
    flex: 1; min-width: 80px; background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.15); border-radius: 12px; padding: 12px 6px; text-align: center;
}
.metric-value { font-size: 1.2rem; font-weight: 800; color: #F1F5F9; }
.metric-label { font-size: 0.75rem; color: #64748B; margin-top: 3px; }

/* الشارات */
.badge-excellent { background: linear-gradient(135deg,#059669,#10B981); color:white; padding:5px 16px; border-radius:20px; font-size:0.8rem; font-weight:800; }
.badge-good      { background: linear-gradient(135deg,#D97706,#F59E0B); color:white; padding:5px 16px; border-radius:20px; font-size:0.8rem; font-weight:800; }
.badge-bad       { background: linear-gradient(135deg,#DC2626,#EF4444); color:white; padding:5px 16px; border-radius:20px; font-size:0.8rem; font-weight:800; }

/* أوقات الصيد */
.range-chip {
    display: inline-block; background: linear-gradient(135deg, #0369A1, #0EA5E9);
    color: white; font-weight: 800; font-size: 0.85rem; padding: 5px 14px;
    border-radius: 22px; margin: 4px 0 4px 6px; box-shadow: 0 2px 8px rgba(14,165,233,0.35);
}

/* Solunar Columns */
.solunar-wrap { display: flex; gap: 12px; direction: rtl; margin-bottom: 16px; }
.solunar-col { flex: 1; border-radius: 16px; padding: 16px 14px; text-align: center; }
.solunar-major { background: rgba(56,189,248,0.05); border: 1px solid rgba(56,189,248,0.2); }
.solunar-minor { background: rgba(167,139,250,0.05); border: 1px solid rgba(167,139,250,0.2); }
.solunar-h { font-size: 0.8rem; font-weight: 800; margin-bottom: 8px; }
.sol-v { font-size: 0.95rem; font-weight: 800; color: #F1F5F9; }

/* Activity Gauge */
.act-ring-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px; }
.act-ring-score { font-size: 2.5rem; font-weight: 900; color: #F1F5F9; line-height: 1; }
</style>
""", unsafe_allow_html=True)

# ─── ثوابت ودوال مساعدة ───────────────────────────────────────────────────────
DAYS_AR   = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
MONTHS_AR = ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]

def _day_option_label(offset: int) -> str:
    d = datetime.now() + timedelta(days=offset)
    day_name = DAYS_AR[(d.weekday() + 1) % 7]
    day_str = f"{d.day} {MONTHS_AR[d.month - 1]}"
    if offset == 0: return f"اليوم ({day_str})"
    return f"{day_name} ({day_str})"

def fmt_12h(h: int) -> str:
    h_wrapped = h % 24
    period = "ص" if h_wrapped < 12 else "م"
    h12 = h_wrapped % 12 or 12
    return f"{h12}:00 {period}"

# ─── نموذج نشاط الأسماك والمد والجزر ──────────────────────────────────────────
def fish_activity_score(wind, wave, temp):
    score = 100
    if wind > 18: score -= 40
    elif wind > 12: score -= 15
    if wave > 0.7: score -= 35
    elif wave > 0.4: score -= 15
    score = max(5, min(100, score))
    if score >= 65: return {"score": score, "label": "نشاط عالي 🎣", "color": "#10B981", "adv": "ظروف مثالية للصيد!"}
    if score >= 35: return {"score": score, "label": "نشاط متوسط 🐟", "color": "#F59E0B", "adv": "تحتاج قليل من الصبر."}
    return {"score": score, "label": "نشاط منخفض ⚠️", "color": "#EF4444", "adv": "البحر هائج أو الرياح شديدة."}

def _tide_amplitudes(lat, lon):
    return dict(M2=0.90, S2=0.28, K1=0.12, O1=0.08, base=1.10) # نموذج مبسط للجبيل

def compute_tide_profile(lat, lon, for_date):
    amp = _tide_amplitudes(lat, lon)
    t_start = (for_date.replace(hour=0) - datetime(2000, 1, 1)).total_seconds() / 3600.0
    periods = dict(M2=12.42, S2=12.00, K1=23.93, O1=25.82)
    heights = []
    for h in range(25):
        t = t_start + h
        val = amp["base"]
        for name, period in periods.items():
            val += amp.get(name, 0.1) * math.cos(2 * math.pi * t / period)
        heights.append(round(max(0.1, val), 2))
    return heights

# ─── واجهة المستخدم الرئيسية ─────────────────────────────────────────────────
st.markdown('<h1 style="color:#38BDF8;text-align:center;font-weight:900;">🌊 MARINE TRACKER PRO</h1>', unsafe_allow_html=True)
st.markdown('<div style="width:50px;height:4px;background:#38BDF8;margin:10px auto 20px;"></div>', unsafe_allow_html=True)

if "coords" not in st.session_state: st.session_state["coords"] = (26.9239, 49.8681)

# الخريطة (Google Maps Satellite Hybrid)
st.markdown('<div class="map-section-label">🗺️ خريطة جوجل التفاعلية</div>', unsafe_allow_html=True)
m = folium.Map(
    location=st.session_state["coords"], zoom_start=12,
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google Maps Satellite Hybrid"
)
folium.Marker(st.session_state["coords"], icon=folium.Icon(color="blue", icon="anchor", prefix="fa")).add_to(m)

map_res = st_folium(m, height=350, use_container_width=True, key="google_map")
if map_res and map_res.get("last_clicked"):
    st.session_state["coords"] = (map_res["last_clicked"]["lat"], map_res["last_clicked"]["lng"])
    st.rerun()

# اختيار التاريخ
_day_opts = [_day_option_label(i) for i in range(7)]
sel_day = st.segmented_control("اليوم", options=_day_opts, default=_day_opts[0], label_visibility="collapsed")
offset = _day_opts.index(sel_day)

# جلب البيانات (Open-Meteo)
lat, lon = st.session_state["coords"]
w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,windspeed_10m&timezone=Asia/Riyadh"
m_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height&timezone=Asia/Riyadh"

try:
    weather = requests.get(w_url).json()["hourly"]
    marine = requests.get(m_url).json()["hourly"]
    idx = (offset * 24) + datetime.now().hour
    
    t_now = weather["temperature_2m"][idx]
    w_now = weather["windspeed_10m"][idx]
    wv_now = marine["wave_height"][idx]
    
    # بطاقة الأحوال
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📊 الأحوال الحالية — الجبيل</div>
        <div class="metric-row">
            <div class="metric-box"><div class="metric-value">{t_now:.0f}°م</div><div class="metric-label">الحرارة</div></div>
            <div class="metric-box"><div class="metric-value">{w_now:.0f} ك/س</div><div class="metric-label">الرياح</div></div>
            <div class="metric-box"><div class="metric-value">{wv_now:.1f} م</div><div class="metric-label">الموج</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # مؤشر النشاط
    act = fish_activity_score(w_now, wv_now, t_now)
    score, color = act["score"], act["color"]
    radius = 65; circ = 2 * math.pi * radius; filled = circ * score / 100
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🐠 مؤشر نشاط الصيد</div>
        <div style="display:flex;align-items:center;justify-content:space-around;direction:rtl;">
            <div class="act-ring-wrap">
                <svg width="150" height="150" style="transform:rotate(-90deg);">
                    <circle cx="75" cy="75" r="{radius}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="12"/>
                    <circle cx="75" cy="75" r="{radius}" fill="none" stroke="{color}" stroke-width="12" stroke-dasharray="{filled} {circ}" stroke-linecap="round"/>
                </svg>
                <div style="position:absolute;text-align:center;">
                    <div class="act-ring-score">{score}</div>
                    <div style="font-size:0.8rem;color:#64748B;">/ 100</div>
                </div>
            </div>
            <div style="text-align:right;">
                <h3 style="color:{color};margin:0;">{act['label']}</h3>
                <p style="color:#94A3B8;font-size:0.9rem;">{act['adv']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 📉 منحنى المد والجزر (Plotly 12h)
    tide_h = compute_tide_profile(lat, lon, datetime.now() + timedelta(days=offset))
    labels_12h = [fmt_12h(h) for h in range(25)]
    
    fig = go.Figure()
    # تلوين ليل/نهار
    fig.add_vrect(x0=0, x1=5.5, fillcolor="#0A1628", opacity=0.4, line_width=0) # فجر
    fig.add_vrect(x0=5.5, x1=18, fillcolor="#ECEFF1", opacity=0.1, line_width=0) # نهار
    fig.add_vrect(x0=18, x1=24, fillcolor="#0A1628", opacity=0.4, line_width=0) # ليل
    
    fig.add_trace(go.Scatter(x=list(range(25)), y=tide_h, mode='lines', line=dict(color='#38BDF8', width=4, shape='spline'), text=labels_12h, hovertemplate='%{text}<br>الارتفاع: %{y}م'))
    
    if offset == 0: # الوقت الحالي
        fig.add_vline(x=datetime.now().hour, line_width=2, line_color="#EF4444")
        fig.add_annotation(x=datetime.now().hour, y=max(tide_h), text="الآن", showarrow=False, font=dict(color="#EF4444"))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickmode='array', tickvals=[0, 6, 12, 18, 24], ticktext=['12 ص', '6 ص', '12 م', '6 م', '12 ص'], gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#64748B')),
        yaxis=dict(showgrid=False, tickfont=dict(color='#64748B'))
    )
    st.markdown('<div class="map-section-label">📉 منحنى المد والجزر (نظام 12 ساعة)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # أوقات الصيد (Solunar)
    st.markdown("""
    <div class="card">
        <div class="card-title">⏱️ أوقات الصيد المثلى (Solunar)</div>
        <div class="solunar-wrap">
            <div class="solunar-col solunar-major">
                <div class="solunar-h" style="color:#38BDF8;">MAJOR TIMES</div>
                <div class="sol-v">05:20 ص - 07:20 ص</div>
                <div class="sol-v">05:45 م - 07:45 م</div>
            </div>
            <div class="solunar-col solunar-minor">
                <div class="solunar-h" style="color:#A78BFA;">MINOR TIMES</div>
                <div class="sol-v">11:10 ص - 12:10 م</div>
                <div class="sol-v">11:30 م - 12:30 ص</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error("يرجى اختيار نقطة بحرية واضحة (خارج اليابسة) لجلب البيانات.")
