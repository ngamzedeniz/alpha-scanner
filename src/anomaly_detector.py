"""
anomaly_detector.py
Detects anomalies in climate indices and classifies regimes.

(İklim indekslerindeki anomalileri tespit eder ve rejim sınıflandırır.)

Thresholds based on NOAA standardized index conventions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ─────────────────────────────────────────────────────────────────
# Threshold Configuration
# ─────────────────────────────────────────────────────────────────

THRESHOLDS = {
    "nao": {
        "strong_positive": 1.0,
        "strong_negative": -1.0,
    },
    "ao": {
        "strong_positive": 1.5,
        "strong_negative": -1.5,
    },
    "oni": {
        "el_nino": 0.5,
        "la_nina": -0.5,
        "strong_el_nino": 1.5,
        "strong_la_nina": -1.5,
    },
}


# ─────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────

@dataclass
class IndexState:
    """Current state of a single climate index.

    (Tek bir iklim indeksinin mevcut durumu.)
    """
    name: str
    current_value: float
    regime: str  # e.g. "Strong NAO-", "El Niño", "Neutral"
    severity: str  # "extreme" | "strong" | "moderate" | "neutral"
    market_impact: str  # plain-English description
    color: str  # hex color for dashboard


# ─────────────────────────────────────────────────────────────────
# NAO classification
# ─────────────────────────────────────────────────────────────────

def classify_nao(value: float) -> IndexState:
    """Classify NAO state.

    NAO+ → mild, windy → BEARISH for power
    NAO- → cold, still → BULLISH for power
    """
    t = THRESHOLDS["nao"]

    if value >= t["strong_positive"] * 2:
        return IndexState(
            name="NAO",
            current_value=value,
            regime="Extreme NAO+",
            severity="extreme",
            market_impact="Mild & extremely windy winter — strong renewable supply, BEARISH power",
            color="#10B981",  # green
        )
    elif value >= t["strong_positive"]:
        return IndexState(
            name="NAO",
            current_value=value,
            regime="Strong NAO+",
            severity="strong",
            market_impact="Mild & windy winter — high wind generation, BEARISH power",
            color="#34D399",
        )
    elif value <= t["strong_negative"] * 2:
        return IndexState(
            name="NAO",
            current_value=value,
            regime="Extreme NAO-",
            severity="extreme",
            market_impact="Cold winter, blocking risk — Dunkelflaute setup, STRONGLY BULLISH power",
            color="#DC2626",  # red
        )
    elif value <= t["strong_negative"]:
        return IndexState(
            name="NAO",
            current_value=value,
            regime="Strong NAO-",
            severity="strong",
            market_impact="Cold winter signal — heating demand up, BULLISH power",
            color="#F87171",
        )
    else:
        return IndexState(
            name="NAO",
            current_value=value,
            regime="Neutral",
            severity="neutral",
            market_impact="No strong signal — market follows base case",
            color="#6B7280",  # gray
        )


# ─────────────────────────────────────────────────────────────────
# AO classification
# ─────────────────────────────────────────────────────────────────

def classify_ao(value: float) -> IndexState:
    """Classify Arctic Oscillation state.

    AO- → polar vortex weak → cold air outbreaks (Beast from the East)
    AO+ → polar vortex strong → cold confined to Arctic
    """
    t = THRESHOLDS["ao"]

    if value <= t["strong_negative"] * 1.3:
        return IndexState(
            name="AO",
            current_value=value,
            regime="Extreme AO-",
            severity="extreme",
            market_impact="Polar vortex collapse — Arctic air outbreak imminent (1-3 weeks)",
            color="#DC2626",
        )
    elif value <= t["strong_negative"]:
        return IndexState(
            name="AO",
            current_value=value,
            regime="Strong AO-",
            severity="strong",
            market_impact="Polar vortex disrupted — cold air spilling south",
            color="#F87171",
        )
    elif value >= t["strong_positive"]:
        return IndexState(
            name="AO",
            current_value=value,
            regime="Strong AO+",
            severity="strong",
            market_impact="Strong polar vortex — cold confined to Arctic, mild Europe",
            color="#34D399",
        )
    else:
        return IndexState(
            name="AO",
            current_value=value,
            regime="Neutral",
            severity="neutral",
            market_impact="Polar vortex stable — no extreme risk",
            color="#6B7280",
        )


# ─────────────────────────────────────────────────────────────────
# ENSO/ONI classification
# ─────────────────────────────────────────────────────────────────

def classify_oni(value: float) -> IndexState:
    """Classify ENSO state from ONI.

    El Niño → tends to mild winter in Europe (NAO+ tendency)
    La Niña → tends to cold winter in Europe (NAO- tendency)
    """
    t = THRESHOLDS["oni"]

    if value >= t["strong_el_nino"]:
        return IndexState(
            name="ENSO/ONI",
            current_value=value,
            regime="Strong El Niño",
            severity="strong",
            market_impact="Tends to favor NAO+ → mild European winter (3-month lead)",
            color="#10B981",
        )
    elif value >= t["el_nino"]:
        return IndexState(
            name="ENSO/ONI",
            current_value=value,
            regime="El Niño",
            severity="moderate",
            market_impact="Mild European winter tendency, but signal noisy",
            color="#34D399",
        )
    elif value <= t["strong_la_nina"]:
        return IndexState(
            name="ENSO/ONI",
            current_value=value,
            regime="Strong La Niña",
            severity="strong",
            market_impact="Tends to favor NAO- → cold European winter (3-month lead)",
            color="#DC2626",
        )
    elif value <= t["la_nina"]:
        return IndexState(
            name="ENSO/ONI",
            current_value=value,
            regime="La Niña",
            severity="moderate",
            market_impact="Cold European winter tendency, but signal noisy",
            color="#F87171",
        )
    else:
        return IndexState(
            name="ENSO/ONI",
            current_value=value,
            regime="Neutral",
            severity="neutral",
            market_impact="No strong ENSO signal",
            color="#6B7280",
        )


# ─────────────────────────────────────────────────────────────────
# Aggregate detector
# ─────────────────────────────────────────────────────────────────

def detect_all() -> dict[str, IndexState]:
    """Read latest data from CSVs and classify all indices.

    (CSV'lerden son verileri okur ve tüm indeksleri sınıflandırır.)
    """
    results = {}

    # NAO
    nao_path = DATA_DIR / "nao_daily.csv"
    if nao_path.exists():
        df = pd.read_csv(nao_path)
        # 7-day average for stability (Stabilite için 7-gün ortalama)
        latest_nao = df["nao_index"].tail(7).mean()
        results["nao"] = classify_nao(latest_nao)

    # AO
    ao_path = DATA_DIR / "ao_monthly.csv"
    if ao_path.exists():
        df = pd.read_csv(ao_path)
        latest_ao = df["ao_index"].iloc[-1]
        results["ao"] = classify_ao(latest_ao)

    # ONI
    oni_path = DATA_DIR / "enso_oni.csv"
    if oni_path.exists():
        df = pd.read_csv(oni_path)
        latest_oni = df["oni_anomaly"].iloc[-1]
        results["oni"] = classify_oni(latest_oni)

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 ALPHA SCANNER — Anomaly Detection")
    print("=" * 60)
    print()

    states = detect_all()

    if not states:
        print("⚠️  No data found. Run: python -m src.data_fetcher first")
    else:
        for key, state in states.items():
            print(f"📊 {state.name}")
            print(f"   Current value: {state.current_value:+.2f}")
            print(f"   Regime: {state.regime}")
            print(f"   Severity: {state.severity}")
            print(f"   Impact: {state.market_impact}")
            print()
