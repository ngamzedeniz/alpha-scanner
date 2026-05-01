# 🌍 Alpha Scanner — European Energy Trading Signal Detector

> **Detect market alpha by combining meteorological anomalies with energy market expectations.**
>
> *(Piyasanın bilmediği meteorolojik anomalileri tespit ederek trading sinyali üretir.)*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 The Problem

European energy traders need to predict price movements **2-21 days ahead**. By the time weather signals reach mainstream forecasts, prices have already moved.

**The opportunity:** Detect upper-atmosphere anomalies (NAO, AO, SSW, ENSO) **before** they propagate to the surface — and **before** the market prices them in.

*(Avrupa enerji trader'ları fiyat hareketlerini 2-21 gün önceden tahmin etmeli. Hava sinyalleri ana akım tahminlere ulaştığında, fiyatlar zaten hareket etmiş oluyor. Fırsat: Anomalileri erken tespit etmek = piyasadan önce pozisyon almak.)*

---

## 💡 The Approach

Alpha Scanner monitors three layers and detects divergence:

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  LAYER 1:        │   │  LAYER 2:        │   │  LAYER 3:        │
│  MARKET          │   │  WEATHER         │   │  ATMOSPHERIC     │
│  EXPECTATION     │   │  FORECAST        │   │  ANOMALY         │
│  (EPEX, ENTSO-E) │   │  (ECMWF)         │   │  (NOAA CPC)      │
└────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
         │                      │                      │
         └──────────────┬───────┴──────────────────────┘
                        ▼
            ┌──────────────────────┐
            │  DIVERGENCE ENGINE   │
            │  Compare 3 layers    │
            └──────────┬───────────┘
                       ▼
              ┌─────────────────┐
              │  ALPHA SIGNAL   │
              │  LONG / SHORT   │
              └─────────────────┘
```

**Alpha = Information the market doesn't have yet.**
*(Alpha = Piyasanın henüz sahip olmadığı bilgi.)*

---

## 📊 Currently Monitored Indices

| Index | Source | Update | Lead Time | What It Tells Us |
|-------|--------|--------|-----------|------------------|
| **NAO** (North Atlantic Oscillation) | NOAA CPC | Daily | 2-6 weeks | Winter regime: mild & windy vs cold & still |
| **AO** (Arctic Oscillation) | NOAA CPC | Monthly | 2-4 weeks | Polar vortex strength → cold air outbreaks |
| **ENSO/ONI** (El Niño / La Niña) | NOAA CPC | Monthly | 3-6 months | Seasonal regime over Europe |

> **Note:** Architecture is modular. Adding new indices (SSW, MJO, IOD, blocking patterns) requires ~2 hours per index.
>
> *(Mimari modüler. Yeni indeks eklemek indeks başına ~2 saat.)*

---

## 🚀 Quick Start

### Local Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/alpha-scanner.git
cd alpha-scanner

# Install dependencies
pip install -r requirements.txt

# Fetch latest data from NOAA
python -m src.data_fetcher

# Run the dashboard
streamlit run src/dashboard.py
```

Dashboard opens at `http://localhost:8501`

### Live Demo

🌐 **[View Live Dashboard](https://YOUR_USERNAME-alpha-scanner.streamlit.app/)**

*(Deploy edildikten sonra gerçek URL buraya gelecek.)*

---

## 📁 Project Structure

```
alpha-scanner/
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py        # Pulls data from NOAA CPC
│   ├── anomaly_detector.py    # Detects regime anomalies
│   ├── signal_generator.py    # Generates trading signals
│   └── dashboard.py           # Streamlit dashboard
├── data/                      # Auto-populated CSV cache
├── .streamlit/
│   └── config.toml            # Dashboard theme
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 🔬 Methodology

### Anomaly Detection Thresholds

Based on NOAA's standardized index conventions:

| Signal | Threshold | Interpretation |
|--------|-----------|----------------|
| Strong NAO+ | > +1.0 | Mild & windy winter (bearish power) |
| Strong NAO- | < -1.0 | Cold winter (bullish power) |
| Polar disruption | AO < -1.5 | Beast from the East risk |
| El Niño | ONI > +0.5 | Mild European winter |
| La Niña | ONI < -0.5 | Cold European winter |

### Signal Generation Logic

The engine combines indices with **weighted voting**:

```python
if NAO < -1.0 AND AO < -1.5:
    signal = "STRONG LONG POWER"
    confidence = 85%
    horizon = "2-4 weeks"
elif NAO < -1.0 OR AO < -1.5:
    signal = "LONG POWER"
    confidence = 65%
elif NAO > 1.0:
    signal = "SHORT POWER"
    confidence = 70%
else:
    signal = "NEUTRAL"
```

---

## 🌐 Data Sources (All Free, Public)

| Source | URL | License |
|--------|-----|---------|
| NOAA CPC NAO | [Link](https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/nao.shtml) | Public Domain |
| NOAA CPC AO | [Link](https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/ao_index.html) | Public Domain |
| NOAA CPC ONI | [Link](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt) | Public Domain |

*All NOAA data is in the public domain. (Tüm NOAA verileri kamu malıdır.)*

---

## 🎓 Background & Motivation


**Core thesis:** A meteorologist's value to a trading desk isn't producing forecasts — it's identifying when the meteorological reality diverges from market expectations. That divergence is alpha.

*( Temel tez: Bir meteorolog'un trading desk'e değeri tahmin üretmek değil, meteorolojik gerçeğin piyasa beklentisinden ne zaman saptığını tespit etmektir. Bu sapma = alpha.)*

---

## 📈 Roadmap

- [x] **v0.1** — NAO, AO, ENSO monitoring
- [ ] **v0.2** — SSW (Sudden Stratospheric Warming) detection
- [ ] **v0.3** — ECMWF Open Data integration
- [ ] **v0.4** — ENTSO-E real-time generation data
- [ ] **v0.5** — EPEX SPOT price comparison
- [ ] **v1.0** — Full 40-event coverage with backtesting

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

Built by **[N Gamze Deniz]** as a portfolio project.

**Contact:** [ngamzedeniz@gmail.com](mailto:ngamzedeniz@.com)
**LinkedIn:** [linkedin.com/in/ngamzedeniz](https://linkedin.com/in/ngamzedeniz)

---

*"The job of an energy meteorologist isn't to forecast the weather. It's to forecast where the market is wrong about the weather."*
