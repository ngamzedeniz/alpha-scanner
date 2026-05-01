"""
dashboard.py
Streamlit dashboard for Alpha Scanner.

(Alpha Scanner için Streamlit dashboard.)

Run with:
    streamlit run src/dashboard.py
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.anomaly_detector import detect_all
from src.signal_generator import generate_signal
from src.data_fetcher import fetch_all

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ─────────────────────────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Alpha Scanner | EU Energy Trading",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polish (Profesyonel görünüm için CSS)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        color: #9CA3AF;
        font-size: 1.1rem;
        margin-top: 0;
    }
    .signal-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: #1A1F2E;
        border-left: 6px solid;
        margin: 1rem 0;
    }
    .index-card {
        padding: 1.2rem;
        border-radius: 10px;
        background: #1A1F2E;
        border-left: 4px solid;
        height: 100%;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }
    .metric-label {
        color: #9CA3AF;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] {
        background: #1A1F2E;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">🌍 Alpha Scanner</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">European Energy Trading Signal Detector</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f"**Last update:**  \n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")


# ─────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Controls")

    if st.button("🔄 Refresh Data", use_container_width=True):
        with st.spinner("Fetching latest from NOAA..."):
            fetch_all()
        st.success("Data refreshed!")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📚 About")
    st.markdown("""
    **Alpha Scanner** detects divergence between:
    - 📈 Market expectations
    - 🌤️ Weather forecasts
    - 🌪️ Atmospheric anomalies

    *Built as a portfolio piece for energy meteorology roles.*
    """)

    st.markdown("---")
    st.markdown("### 🔗 Data Sources")
    st.markdown("""
    - [NOAA CPC NAO](https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/nao.shtml)
    - [NOAA CPC AO](https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/ao_index.html)
    - [NOAA CPC ONI](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt)
    """)


# ─────────────────────────────────────────────────────────────────
# Check data availability
# ─────────────────────────────────────────────────────────────────

required_files = ["nao_daily.csv", "ao_monthly.csv", "enso_oni.csv"]
missing = [f for f in required_files if not (DATA_DIR / f).exists()]

if missing:
    st.warning(f"⚠️  Missing data files: {missing}. Click 'Refresh Data' in the sidebar.")
    st.stop()


# ─────────────────────────────────────────────────────────────────
# Load data and generate signal
# ─────────────────────────────────────────────────────────────────

states = detect_all()
signal = generate_signal(states)


# ─────────────────────────────────────────────────────────────────
# Section 1: Master Trading Signal
# ─────────────────────────────────────────────────────────────────

st.markdown("## 📡 Master Signal")

st.markdown(
    f"""
    <div class="signal-box" style="border-left-color: {signal.color};">
        <h2 style="margin: 0; color: {signal.color};">{signal.headline}</h2>
        <p style="color: #9CA3AF; margin: 0.5rem 0 0 0;">
            <strong>Horizon:</strong> {signal.horizon}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Two columns: Rationale + Risks
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("#### 📋 Rationale")
    if signal.rationale:
        for r in signal.rationale:
            st.markdown(f"- {r}")
    else:
        st.markdown("*No active rationale.*")

with col_b:
    st.markdown("#### ⚠️ Risk Factors")
    if signal.risk_factors:
        for r in signal.risk_factors:
            st.markdown(f"- {r}")
    else:
        st.markdown("*None identified.*")

st.markdown("---")


# ─────────────────────────────────────────────────────────────────
# Section 2: Index Status Cards
# ─────────────────────────────────────────────────────────────────

st.markdown("## 📊 Index Status")

cols = st.columns(len(states))
for col, (key, state) in zip(cols, states.items()):
    with col:
        st.markdown(
            f"""
            <div class="index-card" style="border-left-color: {state.color};">
                <p class="metric-label">{state.name}</p>
                <p class="metric-value" style="color: {state.color};">
                    {state.current_value:+.2f}
                </p>
                <p style="margin: 0; font-weight: 600;">{state.regime}</p>
                <p style="color: #9CA3AF; font-size: 0.85rem; margin-top: 0.5rem;">
                    {state.market_impact}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")


# ─────────────────────────────────────────────────────────────────
# Section 3: Time Series Charts
# ─────────────────────────────────────────────────────────────────

st.markdown("## 📈 Historical Trends")

tabs = st.tabs(["NAO (Daily)", "AO (Monthly)", "ENSO/ONI"])

# NAO chart
with tabs[0]:
    nao_df = pd.read_csv(DATA_DIR / "nao_daily.csv")
    nao_df["date"] = pd.to_datetime(nao_df["date"])
    nao_recent = nao_df.tail(180)  # Son 6 ay

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=nao_recent["date"], y=nao_recent["nao_index"],
        mode="lines", name="NAO",
        line=dict(color="#FF6B35", width=2),
    ))
    fig.add_hline(y=1.0, line_dash="dash", line_color="#34D399",
                  annotation_text="Strong NAO+ threshold")
    fig.add_hline(y=-1.0, line_dash="dash", line_color="#F87171",
                  annotation_text="Strong NAO- threshold")
    fig.add_hline(y=0, line_color="#4B5563")

    fig.update_layout(
        title="North Atlantic Oscillation — Last 180 Days",
        xaxis_title="Date",
        yaxis_title="NAO Index",
        template="plotly_dark",
        height=450,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

# AO chart
with tabs[1]:
    ao_df = pd.read_csv(DATA_DIR / "ao_monthly.csv")
    ao_df["date"] = pd.to_datetime(ao_df["date"])
    ao_recent = ao_df.tail(60)  # 5 yıl

    fig = go.Figure()
    colors = ["#F87171" if v < -1.5 else "#34D399" if v > 1.5 else "#6B7280"
              for v in ao_recent["ao_index"]]
    fig.add_trace(go.Bar(
        x=ao_recent["date"], y=ao_recent["ao_index"],
        marker_color=colors, name="AO",
    ))
    fig.add_hline(y=1.5, line_dash="dash", line_color="#34D399")
    fig.add_hline(y=-1.5, line_dash="dash", line_color="#F87171")

    fig.update_layout(
        title="Arctic Oscillation — Last 5 Years (Monthly)",
        xaxis_title="Date",
        yaxis_title="AO Index",
        template="plotly_dark",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

# ONI chart
with tabs[2]:
    oni_df = pd.read_csv(DATA_DIR / "enso_oni.csv")
    oni_df["date"] = pd.to_datetime(oni_df["date"])
    oni_recent = oni_df.tail(60)  # 5 yıl

    fig = go.Figure()
    colors = ["#DC2626" if v < -0.5 else "#10B981" if v > 0.5 else "#6B7280"
              for v in oni_recent["oni_anomaly"]]
    fig.add_trace(go.Bar(
        x=oni_recent["date"], y=oni_recent["oni_anomaly"],
        marker_color=colors, name="ONI",
    ))
    fig.add_hline(y=0.5, line_dash="dash", line_color="#10B981",
                  annotation_text="El Niño threshold")
    fig.add_hline(y=-0.5, line_dash="dash", line_color="#DC2626",
                  annotation_text="La Niña threshold")

    fig.update_layout(
        title="ENSO / Oceanic Niño Index — Last 5 Years",
        xaxis_title="Date",
        yaxis_title="ONI Anomaly (°C)",
        template="plotly_dark",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    """
    <p style="text-align: center; color: #6B7280; font-size: 0.85rem;">
    Built with ❤️ for energy meteorology. Data: NOAA CPC (public domain).<br>
    <em>"The job of an energy meteorologist isn't to forecast the weather.
    It's to forecast where the market is wrong about the weather."</em>
    </p>
    """,
    unsafe_allow_html=True,
)
