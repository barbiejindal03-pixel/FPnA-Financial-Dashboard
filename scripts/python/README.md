# Python Scripts

These scripts run in order, each feeding into the next. You only need to re-run them if you want to refresh the data or rebuild the models from scratch.

---

### 1e_clean_edgar.py — Data Pull

Connects to the SEC EDGAR XBRL API and downloads 10 years of American Express quarterly filings. It filters out cumulative year-to-date entries (keeping only true 90-day quarters), converts dollar figures to billions, and saves a clean CSV.

Run this first. Output goes to `data/processed/amex_clean_v2.csv`.

```bash
python3 scripts/python/1e_clean_edgar.py
```

The scripts 1_data_pull.py through 1d_build_final_dataset.py are earlier iterations kept for reference. 1e is the final working version.

---

### 2_feature_eng.py — Feature Engineering

Takes the clean quarterly data and computes 12 financial ratios — things like net margin, return on equity, debt-to-equity, and year-over-year growth rates. These ratios are what the ML models actually learn from, rather than raw dollar amounts.

Output goes to `data/processed/amex_features.csv`.

```bash
python3 scripts/python/2_feature_eng.py
```

---

### 3_ml_models.py — Machine Learning Models

Trains two models on the engineered features:

- Linear Regression on net margin — finds which ratios drive profitability
- Decision Tree on net income — learns a set of if-then rules for predicting quarterly earnings

Saves five charts to the `charts/` folder and prints results to the terminal.

```bash
python3 scripts/python/3_ml_models.py
```
