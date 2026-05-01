# 🚀 DEPLOYMENT GUIDE — GitHub + Streamlit Cloud

## *(GitHub ve Streamlit Cloud'a Deployment Rehberi)*

This guide takes you from zero to a live URL in ~30 minutes.

*(Bu rehber sıfırdan canlı URL'ye ~30 dakikada götürür.)*

---

## 📋 Prerequisites (Ön Gereksinimler)

- [ ] GitHub account ([github.com](https://github.com))
- [ ] Git installed on your computer (`git --version` to check)
- [ ] Python 3.10+ installed (`python --version` to check)

---

## STEP 1 — Local Test First (Önce Yerel Test) ⏱️ ~10 min

Before pushing anything, make sure it works on your machine.

```bash
# 1. Navigate to the project folder
cd alpha-scanner

# 2. Create a virtual environment (recommended)
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Fetch data (this will hit NOAA — should work from your network)
python -m src.data_fetcher

# 5. Run the dashboard
streamlit run src/dashboard.py
```

✅ **Expected:** Browser opens at `http://localhost:8501` showing the dashboard.

If NOAA URLs are blocked (rare), the system auto-falls back to mock data.

---

## STEP 2 — Create GitHub Repository (GitHub Repo Oluştur) ⏱️ ~5 min

### 2.1 Create the repo on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Repository name: **`alpha-scanner`**
3. Description: *"European energy trading signal detector — combining meteorological anomalies with market expectations"*
4. **Public** (so recruiters can see it!) *(Public yap ki recruiters görsin!)*
5. ❌ Do NOT check "Add a README" (we already have one)
6. ❌ Do NOT add .gitignore or license (we already have them)
7. Click **Create repository**

### 2.2 Push your code

```bash
# Initialize git (if not already)
git init

# Stage all files
git add .

# First commit
git commit -m "Initial commit: Alpha Scanner v0.1"

# Set main branch
git branch -M main

# Connect to GitHub (REPLACE YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/alpha-scanner.git

# Push
git push -u origin main
```

✅ **Expected:** Refresh your GitHub page — you should see all files.

---

## STEP 3 — Deploy to Streamlit Cloud (Canlı Yayına Al) ⏱️ ~5 min

This is the magic step. **Free** hosting for Streamlit apps.

*(Bu sihirli adım. Streamlit uygulamaları için ÜCRETSİZ hosting.)*

### 3.1 Sign up

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **Sign up** (or **Sign in**)
3. Choose **Continue with GitHub** (easiest)
4. Authorize Streamlit to access your repos

### 3.2 Deploy your app

1. Click **New app** (top right)
2. Fill in:
   - **Repository:** `YOUR_USERNAME/alpha-scanner`
   - **Branch:** `main`
   - **Main file path:** `src/dashboard.py`
   - **App URL:** `your-username-alpha-scanner` *(or pick custom)*
3. Click **Deploy!**

### 3.3 Wait

- First deploy takes 2-4 minutes (installing dependencies)
- You'll see live build logs
- When ready: live URL like `https://your-username-alpha-scanner.streamlit.app/`

✅ **Expected:** Dashboard loads at your live URL.

---

## STEP 4 — Personalize (Kişiselleştir) ⏱️ ~10 min

### 4.1 Update README.md

Replace placeholders:
- `[Your Name]` → your actual name
- `your.email@example.com` → your email
- `linkedin.com/in/yourprofile` → your LinkedIn
- `YOUR_USERNAME` → your GitHub username (everywhere)

### 4.2 Update LICENSE

Replace `[Your Name]` with your name.

### 4.3 Add the live URL to README

In README.md, find:
```
🌐 **[View Live Dashboard](https://YOUR_USERNAME-alpha-scanner.streamlit.app/)**
```

Replace with your actual deployed URL.

### 4.4 Commit & push

```bash
git add .
git commit -m "Personalize: add author info and live demo URL"
git push
```

Streamlit Cloud auto-redeploys when you push! *(Her push'ta otomatik redeploy olur.)*

---

## 🎯 INTERVIEW PRESENTATION TIPS

### What to show during the interview:

**1. Open the live URL** *(Canlı URL aç)*
   - "Here's a working demo I built to think about how a meteorologist adds value to a trading desk."

**2. Walk through the Master Signal section** *(Master Signal bölümünü göster)*
   - "The system aggregates three independent indices and outputs a unified trading signal with confidence scores."

**3. Show the Index Status cards** *(Index Status kartlarını göster)*
   - "Each index has classified thresholds. NAO below -1.0 is significant."

**4. Show historical charts** *(Geçmiş grafikleri göster)*
   - "I track each index against NOAA standardized thresholds — so the dashboard shows context, not just current values."

**5. Open the GitHub repo** *(GitHub repo'yu aç)*
   - "Code is modular: data_fetcher, anomaly_detector, signal_generator, dashboard. Each ~150 lines. Adding a new index like SSW or MJO takes about 2 hours."

### Key talking points:

- **"This is v0.1 — 3 indices.** The architecture supports 40+ from the original framework."
- **"The signal isn't 'buy power'. It's 'where is the market wrong?'** That's the alpha."
- **"All data is free, public, no API keys.** NOAA, ECMWF Open Data, ENTSO-E."
- **"Refresh button hits NOAA in real-time** — the dashboard isn't a demo, it's live infrastructure."

---

## 🐛 Troubleshooting

### Issue: NOAA returns 403 from your local machine

Most networks allow it. If yours blocks:
- Try a different network (mobile hotspot)
- Mock data fallback will kick in automatically for testing

### Issue: Streamlit Cloud build fails

- Check `requirements.txt` has all packages
- Check Python version compatibility
- Check build logs for the specific error

### Issue: Dashboard shows "missing data files"

- Click "Refresh Data" in sidebar (it'll fetch from NOAA)
- Or run `python -m src.data_fetcher` locally first

### Issue: I want to update the code

```bash
# Make changes locally
git add .
git commit -m "Description of change"
git push

# Streamlit Cloud auto-redeploys in 1-2 min
```

---

## 🎓 EXTENDING THE PROJECT (Bonus)

Once the basic version is live, consider adding:

1. **SSW detection** — fetch 10hPa wind from NOAA stratosphere page
2. **ECMWF integration** — pull GFS or AIFS forecast data
3. **ENTSO-E real-time** — show actual European generation mix
4. **Backtest module** — verify signals against historical price moves
5. **Email alerts** — push notifications when confidence > 80%

Each feature = 1 PR = stronger portfolio.

*(Her özellik = 1 PR = daha güçlü portföy.)*

---

## ✅ FINAL CHECKLIST

Before the interview:

- [ ] Live URL works
- [ ] README has your name and contact info
- [ ] Live URL added to README
- [ ] Repository is **public**
- [ ] You can explain every file's purpose in 30 seconds
- [ ] You've practiced the 5-minute walkthrough
- [ ] You can answer: *"How would you add SSW detection to this?"*

---

**Good luck! You've got this. 🚀**

*(İyi şanslar! Yapacaksın!)*
