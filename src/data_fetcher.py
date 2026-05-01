"""
data_fetcher.py
Fetches climate indices from NOAA Climate Prediction Center (CPC).

Indices fetched:
- NAO (North Atlantic Oscillation) - daily
- AO (Arctic Oscillation) - monthly
- ONI (Oceanic Niño Index / ENSO) - 3-month rolling

(NOAA Climate Prediction Center'dan iklim indekslerini çeker.
NAO günlük, AO aylık, ONI 3-aylık hareketli ortalama.)

Usage:
    python -m src.data_fetcher
"""

from __future__ import annotations

import io
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# Configuration (Yapılandırma)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# NOAA CPC URLs (Public domain, no API key needed)
URLS = {
    "nao_daily": "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.daily.nao.cdas.z500.20060101_current.csv",
    "ao_monthly": "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii.table",
    "oni": "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
}

# HTTP headers — some servers require User-Agent (Bazı sunucular User-Agent ister)
HEADERS = {
    "User-Agent": "AlphaScanner/0.1 (Educational/Portfolio Project)"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# NAO (North Atlantic Oscillation) — Daily
# ─────────────────────────────────────────────────────────────────

def fetch_nao_daily() -> pd.DataFrame:
    """Fetch daily NAO index from NOAA CPC.

    Returns DataFrame with columns: date, nao_index
    (NOAA CPC'den günlük NAO indeksini çeker.)
    """
    log.info("Fetching NAO daily from NOAA CPC...")
    response = requests.get(URLS["nao_daily"], headers=HEADERS, timeout=30)
    response.raise_for_status()

    # CSV format: year,month,day,value
    df = pd.read_csv(io.StringIO(response.text), header=0)
    df.columns = ["year", "month", "day", "nao_index"]
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df = df[["date", "nao_index"]].sort_values("date").reset_index(drop=True)

    output = DATA_DIR / "nao_daily.csv"
    df.to_csv(output, index=False)
    log.info(f"NAO saved: {len(df)} rows, latest = {df['nao_index'].iloc[-1]:+.2f}")
    return df


# ─────────────────────────────────────────────────────────────────
# AO (Arctic Oscillation) — Monthly
# ─────────────────────────────────────────────────────────────────

def fetch_ao_monthly() -> pd.DataFrame:
    """Fetch monthly AO index from NOAA CPC.

    The source format is a text table: year jan feb mar ... dec
    (Kaynak text tablosu: yıl ve 12 aylık değerler.)
    """
    log.info("Fetching AO monthly from NOAA CPC...")
    response = requests.get(URLS["ao_monthly"], headers=HEADERS, timeout=30)
    response.raise_for_status()

    rows = []
    for line in response.text.strip().split("\n")[1:]:  # skip header
        parts = line.split()
        if len(parts) < 13:
            continue
        try:
            year = int(parts[0])
            for month in range(1, 13):
                value_str = parts[month]
                if value_str in ("-99.90", "-99.9", "-999"):
                    continue
                value = float(value_str)
                rows.append({
                    "date": pd.Timestamp(year=year, month=month, day=15),
                    "ao_index": value,
                })
        except (ValueError, IndexError):
            continue

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    output = DATA_DIR / "ao_monthly.csv"
    df.to_csv(output, index=False)
    log.info(f"AO saved: {len(df)} rows, latest = {df['ao_index'].iloc[-1]:+.2f}")
    return df


# ─────────────────────────────────────────────────────────────────
# ONI (Oceanic Niño Index) — ENSO regime indicator
# ─────────────────────────────────────────────────────────────────

def fetch_oni() -> pd.DataFrame:
    """Fetch ONI (Oceanic Niño Index) from NOAA CPC.

    Format: SEAS YR TOTAL ANOM (DJF, JFM, FMA, etc.)
    El Niño: ONI > +0.5  |  La Niña: ONI < -0.5
    (DJF = Aralık-Ocak-Şubat 3-aylık ortalama, vb.)
    """
    log.info("Fetching ONI (ENSO) from NOAA CPC...")
    response = requests.get(URLS["oni"], headers=HEADERS, timeout=30)
    response.raise_for_status()

    season_to_month = {
        "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
        "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
    }

    rows = []
    for line in response.text.strip().split("\n")[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            season = parts[0]
            year = int(parts[1])
            sst = float(parts[2])
            anomaly = float(parts[3])

            month = season_to_month.get(season)
            if month is None:
                continue

            rows.append({
                "date": pd.Timestamp(year=year, month=month, day=15),
                "season": season,
                "sst": sst,
                "oni_anomaly": anomaly,
            })
        except (ValueError, IndexError):
            continue

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    output = DATA_DIR / "enso_oni.csv"
    df.to_csv(output, index=False)

    last = df.iloc[-1]
    state = "EL NIÑO" if last["oni_anomaly"] > 0.5 else \
            "LA NIÑA" if last["oni_anomaly"] < -0.5 else "NEUTRAL"
    log.info(f"ONI saved: {len(df)} rows, latest = {last['oni_anomaly']:+.2f} ({state})")
    return df


# ─────────────────────────────────────────────────────────────────
# Mock Data Fallback (for offline testing)
# ─────────────────────────────────────────────────────────────────

def generate_mock_data() -> dict:
    """Generate realistic mock data when NOAA is unreachable.

    Used for local testing or when NOAA URLs are blocked.
    (NOAA erişilemezse gerçekçi mock veri üretir. Sadece test için.)
    """
    log.warning("⚠️  Using MOCK data — replace with real NOAA fetch in production")

    rng = np.random.default_rng(seed=42)
    today = datetime.now()

    # NAO: 365 days of AR(1) noise, recent 30 days biased negative
    days = pd.date_range(end=today, periods=365, freq="D")
    nao = np.zeros(365)
    nao[0] = rng.normal(0, 1)
    for i in range(1, 365):
        nao[i] = 0.85 * nao[i - 1] + 0.5 * rng.normal()
    nao[-30:] -= 1.5  # Cold signal in recent month
    nao_df = pd.DataFrame({"date": days, "nao_index": nao})
    nao_df.to_csv(DATA_DIR / "nao_daily.csv", index=False)

    # AO: 120 monthly values
    months = pd.date_range(end=today, periods=120, freq="ME")
    ao = rng.normal(0, 1.2, len(months))
    ao[-3:] -= 2.0  # Recent polar disruption
    ao_df = pd.DataFrame({"date": months, "ao_index": ao})
    ao_df.to_csv(DATA_DIR / "ao_monthly.csv", index=False)

    # ONI: 10 years of seasonal data
    seasons = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ",
               "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]
    oni_rows = []
    for year in range(today.year - 10, today.year + 1):
        for i, season in enumerate(seasons):
            month = i + 1
            if year == today.year and month > today.month:
                break
            phase = np.sin((year - 2000) * 2 * np.pi / 5)
            anomaly = phase * 1.5 + rng.normal(0, 0.3)
            oni_rows.append({
                "date": pd.Timestamp(year=year, month=month, day=15),
                "season": season,
                "sst": 27.0 + anomaly,
                "oni_anomaly": anomaly,
            })
    oni_df = pd.DataFrame(oni_rows)
    # Force recent La Niña for demo (Demo için son aylar La Niña)
    oni_df.loc[oni_df.index[-3:], "oni_anomaly"] = [-0.8, -0.9, -1.0]
    oni_df.to_csv(DATA_DIR / "enso_oni.csv", index=False)

    log.info("Mock data generated.")
    return {"nao": nao_df, "ao": ao_df, "oni": oni_df}


# ─────────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────────

def fetch_all(use_mock_on_failure: bool = True) -> dict:
    """Fetch all indices. Falls back to mock data if NOAA unreachable.

    (Tüm indeksleri çeker. NOAA erişilemezse mock data'ya geçer.)
    """
    results = {}
    failures = 0

    for name, fetch_fn in [
        ("nao", fetch_nao_daily),
        ("ao", fetch_ao_monthly),
        ("oni", fetch_oni),
    ]:
        try:
            results[name] = fetch_fn()
        except Exception as e:
            log.error(f"❌ {name.upper()} fetch failed: {e}")
            failures += 1

    if failures > 0 and use_mock_on_failure:
        log.warning(f"{failures} fetches failed. Generating mock data for testing.")
        results = generate_mock_data()

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("🌍 ALPHA SCANNER — Data Fetcher")
    print(f"   Run time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    fetch_all()

    print()
    print("=" * 60)
    print(f"✅ Done. Data saved to: {DATA_DIR}")
    print("=" * 60)
