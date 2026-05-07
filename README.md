# 💳 American Express — FP&A Intelligence Dashboard

> **Machine Learning · ARIMA Time Series Forecasting · Interactive Financial Analytics**  
> Built with Python, R, Streamlit, and Plotly using 10 years of official SEC EDGAR filings.

🚀 **Live Demo:** [amex-dashboard.streamlit.app](https://amex-dashboard.streamlit.app)

---

## 📌 Project Overview

An end-to-end Financial Planning & Analysis (FP&A) platform for **American Express (AXP)** that combines:
- Official SEC EDGAR data extraction (2010–2026)
- Feature engineering of 12 financial ratios
- Machine learning models to identify profitability drivers
- ARIMA time series forecasting for 2026 projections
- A live interactive dashboard with Amex brand design

---

## 🚀 Live Dashboard Preview

| Section | Description |
|---|---|
| 📊 Executive Overview | KPI cards + Revenue, Margin, ROE, Debt trends |
| 📈 Revenue & Income Trends | Quarterly deep dive with YoY growth analysis |
| 🤖 ML Model Insights | Linear Regression + Decision Tree results |
| 🔮 ARIMA 2026 Forecast | Time series forecast with confidence bands |
| 🏦 Competitor Benchmarking | AXP vs Visa, Mastercard, Capital One |
| 🎛️ Scenario Simulator | Live sliders → ML model re-predicts in real time |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.14** | Data engineering, feature engineering, ML |
| **SEC EDGAR API** | 10 years of official quarterly filings (free) |
| **yfinance** | Supplementary financial data |
| **pandas / numpy** | Data cleaning and transformation |
| **scikit-learn** | Linear Regression + Decision Tree models |
| **R (forecast package)** | ARIMA time series forecasting |
| **Streamlit** | Interactive web dashboard |
| **Plotly** | Interactive charts |

---

## 📁 Project Structure

```
FPnA-Financial-Dashboard/
│
├── 1e_clean_edgar.py        # Data pull: SEC EDGAR → clean quarterly CSV
├── 2_feature_eng.py         # Feature engineering: 12 financial ratios
├── 3_ml_models.py           # ML models: Linear Regression + Decision Tree
├── 4_arima_forecast.R       # ARIMA forecast: 2026 Revenue + Net Income
├── 5_dashboard.py           # Streamlit dashboard (run this)
│
├── amex_clean_v2.csv        # Clean quarterly data (65 quarters, 2010–2026)
├── amex_features.csv        # Engineered features dataset
├── amex_annual.csv          # Annual data: AXP, Visa, Mastercard, Capital One
├── competitors_full.csv     # Competitor quarterly data
├── forecast_results.csv     # ARIMA 2026 quarterly forecasts
│
└── charts/
    ├── chart_lr_coefficients.png
    ├── chart_dt_importance.png
    ├── chart_actual_vs_predicted.png
    ├── chart_arima_Total Revenue.png
    └── chart_arima_Net Income.png
```

---

## ⚙️ How to Run

### 1. Install Python dependencies
```bash
pip install streamlit plotly pandas numpy scikit-learn yfinance seaborn requests
```

### 2. Install R dependencies
```r
install.packages(c("forecast", "ggplot2", "dplyr", "readr", "tseries"))
```

### 3. Pull fresh data from SEC EDGAR
```bash
python3 1e_clean_edgar.py
```

### 4. Engineer features
```bash
python3 2_feature_eng.py
```

### 5. Run ML models
```bash
python3 3_ml_models.py
```

### 6. Run ARIMA forecast (R)
```bash
Rscript 4_arima_forecast.R
```

### 7. Launch dashboard
```bash
streamlit run 5_dashboard.py
```
Open `http://localhost:8501` in your browser.

---

## 📊 Key Results

| Metric | Value |
|---|---|
| Linear Regression R² | **0.977** (97.7% of margin variance explained) |
| Decision Tree R² | **0.723** |
| Top margin driver | **Return on Assets (ROA)** |
| Top income predictor | **Debt-to-Equity ratio** |
| 2026 Revenue forecast | **$78.7B** |
| 2026 Net Income forecast | **$11.3B** |
| Implied 2026 Net Margin | **14.4%** |

---

## 📡 Data Source

All financial data sourced from:
- **[SEC EDGAR XBRL API](https://data.sec.gov/api/xbrl/)** — free, official, no API key required
- **[Yahoo Finance via yfinance](https://pypi.org/project/yfinance/)** — supplementary data

AXP CIK: `0000004962`

---

## 🎨 Design

Dashboard built with Amex brand colours:
- Navy `#00175A` · Blue `#006FCF` · Gold `#C9A84C`

---

*Data is for educational and analytical purposes only. Not financial advice.*
