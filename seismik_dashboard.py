"""
╔══════════════════════════════════════════════════════╗
║     DASHBOARD SEISMIK INDONESIA — Streamlit App     ║
║     Jalankan: streamlit run seismik_dashboard.py    ║
╚══════════════════════════════════════════════════════╝

Install dulu:
    pip install streamlit pandas plotly folium streamlit-folium requests
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import random
import math
from datetime import datetime, timedelta

# ── PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Seismik Indonesia",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark theme override */
    .stApp { background-color: #080c14; }
    .main .block-container { padding-top: 1rem; max-width: 100%; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #0d1420;
        border: 1px solid #1e2d42;
        border-radius: 12px;
        padding: 16px 20px;
    }
    div[data-testid="metric-container"] label {
        color: #64748b !important;
        font-size: 11px !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
    }

    /* Header */
    .dashboard-header {
        background: #0d1420;
        border: 1px solid #1e2d42;
        border-left: 4px solid #f97316;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .dashboard-header h1 {
        color: #e2e8f0;
        font-size: 1.4rem;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .dashboard-header p {
        color: #64748b;
        font-size: 11px;
        margin: 2px 0 0;
        font-family: monospace;
    }
    .live-badge {
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.3);
        color: #ef4444;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        font-family: monospace;
    }

    /* Section titles */
    .section-title {
        color: #94a3b8;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: monospace;
        margin-bottom: 8px;
        border-left: 3px solid #f97316;
        padding-left: 10px;
    }

    /* Dataframe */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0d1420;
        border-right: 1px solid #1e2d42;
    }
    section[data-testid="stSidebar"] .stMarkdown { color: #94a3b8; }

    /* Hide streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── DATA GENERATOR ───────────────────────────────────────────────
@st.cache_data(ttl=60)
def generate_data(n=100):
    """Generate dummy seismic data untuk Indonesia."""
    random.seed(42)

    lokasi_data = [
        ("Banda Aceh, Aceh",           5.55,  95.32),
        ("Nias, Sumatera Utara",        1.20,  97.50),
        ("Padang, Sumatera Barat",     -0.90, 100.35),
        ("Bengkulu",                   -3.80, 102.27),
        ("Lampung Selatan",            -5.45, 104.55),
        ("Selat Sunda",                -6.10, 105.80),
        ("Pangandaran, Jawa Barat",    -7.68, 108.65),
        ("Yogyakarta",                 -7.80, 110.37),
        ("Malang, Jawa Timur",         -8.17, 112.91),
        ("Banyuwangi, Jawa Timur",     -8.22, 114.37),
        ("Lombok, NTB",                -8.65, 116.32),
        ("Flores, NTT",                -8.49, 121.79),
        ("Laut Banda",                 -5.50, 128.20),
        ("Maluku Tengah",              -3.40, 128.92),
        ("Ternate, Maluku Utara",       0.78, 127.37),
        ("Manokwari, Papua Barat",     -0.86, 134.08),
        ("Jayapura, Papua",            -2.54, 140.72),
        ("Sulawesi Utara",              1.47, 124.84),
        ("Palu, Sulawesi Tengah",      -0.90, 119.88),
        ("Makassar, Sulawesi Selatan", -5.14, 119.43),
        ("Kendari, Sulawesi Tenggara", -3.97, 122.51),
        ("Laut Jawa",                  -5.00, 110.50),
        ("Samudra Hindia (W. Sumatra)",-3.20,  94.70),
        ("Kalimantan Timur",            1.10, 117.20),
    ]

    wilayah_map = {
        "Aceh": "Sumatera", "Sumatera Utara": "Sumatera",
        "Sumatera Barat": "Sumatera", "Bengkulu": "Sumatera",
        "Lampung": "Sumatera", "Sumatra": "Sumatera",
        "Jawa Barat": "Jawa", "Yogyakarta": "Jawa",
        "Jawa Timur": "Jawa", "Sunda": "Jawa",
        "NTB": "NTT/NTB", "NTT": "NTT/NTB", "Flores": "NTT/NTB",
        "Lombok": "NTT/NTB",
        "Sulawesi": "Sulawesi", "Palu": "Sulawesi",
        "Makassar": "Sulawesi", "Kendari": "Sulawesi",
        "Banda": "Maluku", "Maluku": "Maluku", "Ternate": "Maluku",
        "Papua": "Papua", "Manokwari": "Papua",
        "Kalimantan": "Kalimantan", "Jawa": "Laut/Samudra",
        "Hindia": "Laut/Samudra",
    }

    def get_wilayah(nama):
        for k, v in wilayah_map.items():
            if k.lower() in nama.lower():
                return v
        return "Lainnya"

    records = []
    base_date = datetime.now()
    for i in range(n):
        lok = random.choice(lokasi_data)
        mag = round(random.uniform(1.5, 7.2), 1)
        depth = random.randint(5, 300)
        dt = base_date - timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        lat = round(lok[1] + random.uniform(-0.4, 0.4), 3)
        lon = round(lok[2] + random.uniform(-0.4, 0.4), 3)

        if mag >= 6.0:
            status = "🔴 KUAT"
        elif mag >= 4.0:
            status = "🟡 SEDANG"
        else:
            status = "🟢 LEMAH"

        records.append({
            "ID":          f"EQ{str(i+1).zfill(4)}",
            "Waktu":       dt.strftime("%d %b %Y %H:%M:%S"),
            "Lokasi":      lok[0],
            "Wilayah":     get_wilayah(lok[0]),
            "Lintang":     lat,
            "Bujur":       lon,
            "Kedalaman(km)": depth,
            "Magnitudo":   mag,
            "Status":      status,
            "_dt":         dt,
        })

    df = pd.DataFrame(records).sort_values("_dt", ascending=False).reset_index(drop=True)
    return df


# ── HELPERS ──────────────────────────────────────────────────────
def mag_color(m):
    if m >= 6.0: return "#ef4444"
    if m >= 5.0: return "#f97316"
    if m >= 4.0: return "#eab308"
    if m >= 3.0: return "#3b82f6"
    return "#22c55e"

def mag_label(m):
    if m >= 6.0: return "Kuat"
    if m >= 5.0: return "Sedang-Kuat"
    if m >= 4.0: return "Sedang"
    if m >= 3.0: return "Ringan"
    return "Sangat Ringan"


# ── LOAD DATA ────────────────────────────────────────────────────
df = generate_data(100)


# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌋 Filter Data")
    st.markdown("---")

    mag_range = st.slider(
        "Rentang Magnitudo",
        min_value=1.0, max_value=8.0,
        value=(1.0, 8.0), step=0.1
    )

    depth_range = st.slider(
        "Kedalaman (km)",
        min_value=0, max_value=300,
        value=(0, 300), step=10
    )

    wilayah_opts = ["Semua"] + sorted(df["Wilayah"].unique().tolist())
    wilayah_sel = st.selectbox("Wilayah", wilayah_opts)

    days_back = st.slider("Tampilkan N hari terakhir", 1, 30, 30)

    st.markdown("---")
    st.markdown("### 📡 Info Sistem")
    st.markdown(f"""
    <div style='font-family:monospace;font-size:11px;color:#64748b;line-height:2'>
    🟢 Stasiun aktif: 186/194<br>
    🕐 Update: {datetime.now().strftime('%H:%M:%S')}<br>
    📊 Total data: {len(df)} kejadian<br>
    🌐 Sumber: BMKG / USGS
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Dashboard Seismik Indonesia v1.0\nDibuat dengan Streamlit + Python")


# ── FILTER ───────────────────────────────────────────────────────
cutoff = datetime.now() - timedelta(days=days_back)
mask = (
    (df["Magnitudo"] >= mag_range[0]) &
    (df["Magnitudo"] <= mag_range[1]) &
    (df["Kedalaman(km)"] >= depth_range[0]) &
    (df["Kedalaman(km)"] <= depth_range[1]) &
    (df["_dt"] >= cutoff)
)
if wilayah_sel != "Semua":
    mask &= df["Wilayah"] == wilayah_sel
dff = df[mask].copy()


# ── HEADER ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="dashboard-header">
    <div style="font-size:2.5rem">🌋</div>
    <div style="flex:1">
        <h1>Dashboard Seismik Indonesia</h1>
        <p>BMKG · Real-time Monitoring · {datetime.now().strftime('%d %B %Y, %H:%M WIB')}</p>
    </div>
    <div class="live-badge">● LIVE</div>
</div>
""", unsafe_allow_html=True)


# ── METRIC CARDS ─────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("⚡ Total Gempa", len(dff), f"+{random.randint(2,8)} hari ini")
with c2:
    max_m = dff["Magnitudo"].max() if len(dff) else 0
    st.metric("📊 Mag. Tertinggi", f"M {max_m:.1f}", "Skala Richter")
with c3:
    avg_m = dff["Magnitudo"].mean() if len(dff) else 0
    st.metric("📈 Mag. Rata-rata", f"M {avg_m:.1f}", "30 hari terakhir")
with c4:
    kuat = len(dff[dff["Magnitudo"] >= 5])
    st.metric("🔴 Gempa Kuat (≥M5)", kuat, "perlu perhatian")
with c5:
    avg_d = dff["Kedalaman(km)"].mean() if len(dff) else 0
    st.metric("⬇️ Kedalaman Rata2", f"{avg_d:.0f} km", "hiposenter")

st.markdown("<br>", unsafe_allow_html=True)


# ── MAP + RECENT ─────────────────────────────────────────────────
col_map, col_recent = st.columns([2, 1])

with col_map:
    st.markdown('<div class="section-title">🗺️ Peta Sebaran Gempa</div>', unsafe_allow_html=True)

    m = folium.Map(
        location=[-2.5, 118],
        zoom_start=5,
        tiles="CartoDB dark_matter",
    )

    for _, row in dff.iterrows():
        color = mag_color(row["Magnitudo"])
        radius = max(4, row["Magnitudo"] * 4)
        folium.CircleMarker(
            location=[row["Lintang"], row["Bujur"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            weight=1.5,
            popup=folium.Popup(f"""
                <div style='font-family:monospace;font-size:12px;min-width:200px'>
                    <b style='color:{color};font-size:16px'>M {row['Magnitudo']}</b><br>
                    📍 {row['Lokasi']}<br>
                    ⬇️ Kedalaman: {row['Kedalaman(km)']} km<br>
                    🕐 {row['Waktu']}<br>
                    <b>{row['Status']}</b>
                </div>
            """, max_width=250),
            tooltip=f"M{row['Magnitudo']} — {row['Lokasi']}"
        ).add_to(m)

    st_folium(m, width=None, height=420, returned_objects=[])

with col_recent:
    st.markdown('<div class="section-title">⚡ Gempa Terkini</div>', unsafe_allow_html=True)

    recent = dff.head(10)
    for _, row in recent.iterrows():
        color = mag_color(row["Magnitudo"])
        label = mag_label(row["Magnitudo"])
        st.markdown(f"""
        <div style='background:#0d1420;border:1px solid #1e2d42;border-radius:10px;
                    padding:10px 14px;margin-bottom:8px;border-left:3px solid {color}'>
            <div style='display:flex;justify-content:space-between;align-items:center'>
                <span style='font-size:18px;font-weight:800;color:{color}'>M {row['Magnitudo']}</span>
                <span style='font-size:10px;color:#64748b;font-family:monospace'>{row['Kedalaman(km)']} km</span>
            </div>
            <div style='color:#e2e8f0;font-size:12px;font-weight:600;margin:3px 0'>{row['Lokasi']}</div>
            <div style='color:#64748b;font-size:10px;font-family:monospace'>{row['Waktu']}</div>
            <div style='margin-top:4px'>
                <span style='background:rgba({",".join(str(int(color.lstrip("#")[i:i+2],16)) for i in (0,2,4))},0.15);
                             color:{color};border-radius:4px;padding:2px 8px;font-size:10px'>{label}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ── CHARTS ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Analisis & Grafik</div>', unsafe_allow_html=True)
ch1, ch2, ch3 = st.columns(3)

# Chart 1: Frekuensi per Hari
with ch1:
    st.markdown("**Frekuensi Gempa per Hari**")
    if len(dff):
        dff["Tanggal"] = pd.to_datetime(dff["_dt"]).dt.date
        daily = dff.groupby("Tanggal").size().reset_index(name="Jumlah")
        fig1 = px.bar(
            daily, x="Tanggal", y="Jumlah",
            color="Jumlah",
            color_continuous_scale=["#3b82f6", "#f97316", "#ef4444"],
            template="plotly_dark",
        )
        fig1.update_layout(
            paper_bgcolor="#0d1420", plot_bgcolor="#0d1420",
            coloraxis_showscale=False, margin=dict(l=10,r=10,t=10,b=10),
            height=220,
        )
        fig1.update_traces(marker_line_width=0)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

# Chart 2: Distribusi Magnitudo
with ch2:
    st.markdown("**Distribusi Magnitudo**")
    if len(dff):
        bins = pd.cut(dff["Magnitudo"], bins=[0,2,3,4,5,6,10],
                      labels=["<2","2-3","3-4","4-5","5-6","≥6"])
        mag_dist = bins.value_counts().sort_index().reset_index()
        mag_dist.columns = ["Kelas","Jumlah"]
        colors_dist = ["#22c55e","#3b82f6","#eab308","#f97316","#ef4444","#dc2626"]
        fig2 = px.pie(
            mag_dist, names="Kelas", values="Jumlah",
            color_discrete_sequence=colors_dist,
            hole=0.55,
            template="plotly_dark",
        )
        fig2.update_layout(
            paper_bgcolor="#0d1420", plot_bgcolor="#0d1420",
            margin=dict(l=10,r=10,t=10,b=10), height=220,
            legend=dict(font=dict(size=10)),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# Chart 3: Per Wilayah
with ch3:
    st.markdown("**Gempa per Wilayah**")
    if len(dff):
        by_wil = dff.groupby("Wilayah").size().sort_values(ascending=True).reset_index(name="Jumlah")
        fig3 = px.bar(
            by_wil, x="Jumlah", y="Wilayah",
            orientation="h",
            color="Jumlah",
            color_continuous_scale=["#3b82f6","#f97316"],
            template="plotly_dark",
        )
        fig3.update_layout(
            paper_bgcolor="#0d1420", plot_bgcolor="#0d1420",
            coloraxis_showscale=False, margin=dict(l=10,r=10,t=10,b=10),
            height=220, yaxis_title=None,
        )
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ── WAVEFORM ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">📡 Simulasi Gelombang Seismik</div>', unsafe_allow_html=True)

import numpy as np
t = np.linspace(0, 60, 2000)
p_wave = np.sin(2 * math.pi * 2 * t) * np.exp(-0.05 * t) * 0.3
s_wave = np.sin(2 * math.pi * 1 * t) * np.exp(-0.03 * (t - 10)) * (t > 10)
noise  = np.random.normal(0, 0.03, len(t))
signal = p_wave + s_wave + noise

fig_wave = go.Figure()
fig_wave.add_trace(go.Scatter(
    x=t, y=signal,
    mode="lines",
    line=dict(color="#f97316", width=1),
    name="Sinyal Seismik",
    fill="tozeroy",
    fillcolor="rgba(249,115,22,0.05)",
))
fig_wave.add_vline(x=10, line=dict(color="#3b82f6", width=1.5, dash="dash"),
                   annotation_text="P-wave", annotation_font_color="#3b82f6")
fig_wave.add_vline(x=22, line=dict(color="#ef4444", width=1.5, dash="dash"),
                   annotation_text="S-wave", annotation_font_color="#ef4444")
fig_wave.update_layout(
    paper_bgcolor="#0d1420", plot_bgcolor="#0d1420",
    margin=dict(l=10,r=10,t=30,b=10), height=160,
    xaxis=dict(title="Waktu (detik)", color="#64748b", gridcolor="#1e2d42"),
    yaxis=dict(title="Amplitudo", color="#64748b", gridcolor="#1e2d42"),
    showlegend=False,
)
st.plotly_chart(fig_wave, use_container_width=True, config={"displayModeBar": False})


# ── SCATTER: Mag vs Kedalaman ─────────────────────────────────────
st.markdown('<div class="section-title">🔬 Hubungan Magnitudo vs Kedalaman</div>', unsafe_allow_html=True)

if len(dff):
    fig_sc = px.scatter(
        dff, x="Kedalaman(km)", y="Magnitudo",
        color="Magnitudo",
        size="Magnitudo",
        color_continuous_scale=["#22c55e","#3b82f6","#eab308","#f97316","#ef4444"],
        hover_data=["Lokasi","Waktu"],
        template="plotly_dark",
        labels={"Kedalaman(km)": "Kedalaman (km)", "Magnitudo": "Magnitudo (Richter)"},
    )
    fig_sc.update_layout(
        paper_bgcolor="#0d1420", plot_bgcolor="#0d1420",
        margin=dict(l=10,r=10,t=10,b=10), height=280,
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar": False})


# ── DATA TABLE ───────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Tabel Data Lengkap</div>', unsafe_allow_html=True)

col_search, col_export = st.columns([3,1])
with col_search:
    search = st.text_input("🔍 Cari lokasi...", placeholder="contoh: Aceh, Jawa, Sulawesi...")
with col_export:
    st.markdown("<br>", unsafe_allow_html=True)
    csv = dff.drop(columns=["_dt"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"seismik_indonesia_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

display_df = dff.drop(columns=["_dt"]).copy()
if search:
    display_df = display_df[display_df["Lokasi"].str.contains(search, case=False)]

st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
    column_config={
        "Magnitudo": st.column_config.ProgressColumn(
            "Magnitudo",
            min_value=0, max_value=8,
            format="M %.1f",
        ),
        "Kedalaman(km)": st.column_config.NumberColumn("Kedalaman (km)", format="%d km"),
        "Lintang": st.column_config.NumberColumn("Lintang", format="%.3f°"),
        "Bujur": st.column_config.NumberColumn("Bujur", format="%.3f°"),
    },
    hide_index=True,
)


# ── FOOTER ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#475569;font-size:11px;font-family:monospace;padding:8px'>
    Dashboard Seismik Indonesia · Data dummy untuk demonstrasi ·
    Sumber: BMKG & USGS · Dibuat dengan Streamlit + Python
</div>
""", unsafe_allow_html=True)
