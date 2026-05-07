"""
Build final clean quarterly dataset for AXP (2010–2025)
Sources: SEC EDGAR (primary) + yfinance quarterly (EPS supplement)
Output: amex_clean.csv  — ready for feature engineering
"""
import requests
import pandas as pd
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

AXP_CIK  = "0000004962"
HEADERS  = {"User-Agent": "amex-analysis barbiejindal03@gmail.com"}
START    = "2010-01-01"

# ── EDGAR concepts to pull ──────────────────────────────────────────────────
CONCEPTS = {
    "RevenuesNetOfInterestExpense":   "Total Revenue",
    "NetIncomeLoss":                  "Net Income",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "Pretax Income",
    "IncomeTaxExpenseBenefit":        "Tax Provision",
    "InterestExpense":                "Interest Expense",
    "InterestAndDividendIncomeOperating": "Interest Income",
    "Assets":                         "Total Assets",
    "LongTermDebt":                   "Long Term Debt",
    "StockholdersEquity":             "Stockholders Equity",
}

print("Fetching AXP EDGAR facts (one request)...")
url  = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{AXP_CIK}.json"
resp = requests.get(url, headers=HEADERS, timeout=60)
resp.raise_for_status()
us_gaap = resp.json()["facts"]["us-gaap"]

# ── Extract each concept ────────────────────────────────────────────────────
series_list = []
for concept, friendly in CONCEPTS.items():
    if concept not in us_gaap:
        print(f"  SKIP (not found): {concept}")
        continue

    unit_data = us_gaap[concept].get("units", {}).get("USD", [])
    rows = []
    for e in unit_data:
        if e.get("form") in ("10-Q", "10-K") and "end" in e:
            rows.append({"date": e["end"], "value": e["val"],
                         "form": e["form"], "accn": e.get("accn", "")})
    if not rows:
        print(f"  no rows: {concept}")
        continue

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    # Keep the most recent amendment per period end date
    df = df.sort_values("accn").drop_duplicates("date", keep="last")
    s  = df.set_index("date")["value"].rename(friendly)
    print(f"  {friendly}: {len(s)} pts  ({s.index.min().date()} → {s.index.max().date()})")
    series_list.append(s)

edgar_df = pd.concat(series_list, axis=1).sort_index()

# ── Filter to 2010 onwards; keep only quarterly-ish dates ──────────────────
edgar_df = edgar_df[edgar_df.index >= START]
# EDGAR mixes annual and quarterly entries; annual = Dec 31 of year
# We keep ALL of them (quarterly + annual fill-in), deduplicated by date

# ── Add Diluted EPS from yfinance quarterly ─────────────────────────────────
print("\nFetching Diluted EPS from yfinance...")
axp   = yf.Ticker("AXP")
inc_q = axp.quarterly_income_stmt
if inc_q is not None and not inc_q.empty:
    inc_q = inc_q.T
    inc_q.index = pd.to_datetime(inc_q.index)
    if "Diluted EPS" in inc_q.columns:
        edgar_df = edgar_df.join(inc_q[["Diluted EPS"]], how="outer")
        print(f"  EPS: {(~edgar_df['Diluted EPS'].isna()).sum()} quarters")

# ── Convert dollar columns to billions ─────────────────────────────────────
DOLLAR = ["Total Revenue", "Net Income", "Pretax Income", "Tax Provision",
          "Interest Expense", "Interest Income", "Total Assets",
          "Long Term Debt", "Stockholders Equity"]
for col in DOLLAR:
    if col in edgar_df.columns:
        edgar_df[col] = edgar_df[col] / 1e9

edgar_df.index.name = "Quarter"

# ── Save ────────────────────────────────────────────────────────────────────
out_path = "/Users/barbiejindal/Desktop/amex_project/amex_clean.csv"
edgar_df.reset_index().to_csv(out_path, index=False)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n=== FINAL DATASET ===")
print(f"Rows: {len(edgar_df)}   |   {edgar_df.index.min().date()} → {edgar_df.index.max().date()}")
print(f"Columns: {list(edgar_df.columns)}")
print(f"\nMissing values per column:")
print(edgar_df.isna().sum().to_string())
print(f"\nLast 8 rows:")
print(edgar_df.tail(8).round(3).to_string())
print(f"\nSaved → {out_path}")
print("\nNext step: run 2_feature_eng.py")
