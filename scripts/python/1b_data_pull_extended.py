"""
Step 1b: Extended data pull
  - yfinance annual financials (goes back ~10 years for most tickers)
  - SEC EDGAR quarterly facts API (free, official, no key needed)
Output: amex_annual.csv, amex_edgar_quarterly.csv, competitors_annual.csv
"""

import yfinance as yf
import pandas as pd
import requests
import time
import warnings
warnings.filterwarnings("ignore")

TICKERS = {
    "AXP": "American Express",
    "V":   "Visa",
    "MA":  "Mastercard",
    "COF": "Capital One",
}

INCOME_COLS = [
    "Total Revenue", "Net Income", "Pretax Income", "Tax Provision",
    "Interest Expense", "Interest Income",
    "Selling General And Administration", "Diluted EPS", "Basic EPS",
]
BALANCE_COLS = [
    "Total Assets", "Total Debt", "Stockholders Equity",
    "Cash And Cash Equivalents",
]
CASHFLOW_COLS = [
    "Free Cash Flow", "Capital Expenditure", "Operating Cash Flow",
]
DOLLAR_COLS = INCOME_COLS[:8] + BALANCE_COLS + CASHFLOW_COLS


# ════════════════════════════════════════════════════════════════════════════
# PART 1 — yfinance ANNUAL data
# ════════════════════════════════════════════════════════════════════════════

def pull_annual(ticker_symbol, company_name):
    print(f"  [yfinance annual] {company_name} ({ticker_symbol})...")
    t = yf.Ticker(ticker_symbol)

    frames = []
    for stmt, cols in [
        (t.income_stmt,    INCOME_COLS),
        (t.balance_sheet,  BALANCE_COLS),
        (t.cashflow,       CASHFLOW_COLS),
    ]:
        if stmt is not None and not stmt.empty:
            df = stmt.T
            df.index = pd.to_datetime(df.index)
            keep = [c for c in cols if c in df.columns]
            frames.append(df[keep])

    if not frames:
        print(f"    WARNING: no data")
        return None

    merged = frames[0]
    for f in frames[1:]:
        merged = merged.join(f, how="outer")

    merged.index.name = "Year"
    merged.insert(0, "Company", company_name)
    merged.insert(1, "Ticker", ticker_symbol)
    merged = merged.sort_index()
    print(f"    {len(merged)} years  |  {merged.index.min().date()} → {merged.index.max().date()}")
    return merged


print("\n=== Part 1: yfinance ANNUAL data ===\n")
annual_frames = []
for sym, name in TICKERS.items():
    df = pull_annual(sym, name)
    if df is not None:
        annual_frames.append(df)

annual_combined = pd.concat(annual_frames).reset_index()
for col in DOLLAR_COLS:
    if col in annual_combined.columns:
        annual_combined[col] = pd.to_numeric(annual_combined[col], errors="coerce") / 1e9

annual_combined.to_csv("/Users/barbiejindal/Desktop/amex_project/amex_annual.csv", index=False)
print(f"\nSaved → amex_annual.csv  ({len(annual_combined)} rows total)")
print("\nAnnual row counts per company:")
print(annual_combined.groupby("Ticker")["Year"].count().to_string())


# ════════════════════════════════════════════════════════════════════════════
# PART 2 — SEC EDGAR quarterly facts (AXP only, 2015–2025)
# ════════════════════════════════════════════════════════════════════════════

# AXP CIK (Central Index Key) from SEC EDGAR
AXP_CIK = "0000004962"

EDGAR_BASE = "https://data.sec.gov/api/xbrl/companyfacts"
HEADERS = {"User-Agent": "amex-analysis barbiejindal03@gmail.com"}  # SEC requires this

# XBRL concept → friendly name mapping
CONCEPTS = {
    "Revenues":                                  "Total Revenue",
    "NetIncomeLoss":                             "Net Income",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "Pretax Income",
    "IncomeTaxExpenseBenefit":                   "Tax Provision",
    "InterestExpense":                           "Interest Expense",
    "InterestAndDividendIncomeOperating":        "Interest Income",
    "Assets":                                    "Total Assets",
    "LongTermDebt":                              "Long Term Debt",
    "StockholdersEquity":                        "Stockholders Equity",
    "EarningsPerShareDiluted":                   "Diluted EPS",
}

def fetch_concept(cik, concept, friendly_name):
    """Fetch a single XBRL concept time series from EDGAR."""
    url = f"{EDGAR_BASE}/CIK{cik}.json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"    EDGAR HTTP {r.status_code} for {concept}")
            return pd.Series(dtype=float, name=friendly_name)

        data = r.json()
        facts = data.get("facts", {})

        # Try us-gaap namespace first, then dei
        for ns in ["us-gaap", "dei"]:
            if concept in facts.get(ns, {}):
                entries = facts[ns][concept].get("units", {})
                # Financial values in USD
                unit_data = entries.get("USD", entries.get("shares", []))
                rows = []
                for e in unit_data:
                    # We want 10-Q (quarterly) filings; also accept 10-K for annual
                    if e.get("form") in ("10-Q", "10-K") and "end" in e:
                        rows.append({"date": e["end"], "value": e["val"],
                                     "form": e["form"], "accn": e.get("accn","")})
                if rows:
                    df = pd.DataFrame(rows)
                    df["date"] = pd.to_datetime(df["date"])
                    # Keep most recent filing per end date (drop amended duplicates)
                    df = df.sort_values("accn").drop_duplicates("date", keep="last")
                    df = df.set_index("date")["value"].rename(friendly_name)
                    return df

        print(f"    concept not found: {concept}")
        return pd.Series(dtype=float, name=friendly_name)

    except Exception as ex:
        print(f"    ERROR fetching {concept}: {ex}")
        return pd.Series(dtype=float, name=friendly_name)


print("\n=== Part 2: SEC EDGAR quarterly facts for AXP ===\n")

series_list = []
# Fetch one URL to get all facts (more efficient than per-concept calls)
print("  Fetching EDGAR company facts (one request)...")
edgar_url = f"{EDGAR_BASE}/CIK{AXP_CIK}.json"
try:
    resp = requests.get(edgar_url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    edgar_data = resp.json()
    print("  Got EDGAR data. Extracting concepts...")

    us_gaap = edgar_data.get("facts", {}).get("us-gaap", {})

    for concept, friendly in CONCEPTS.items():
        if concept not in us_gaap:
            print(f"    skip (not found): {concept}")
            continue

        entries = us_gaap[concept].get("units", {})
        unit_data = entries.get("USD", entries.get("shares", []))

        rows = []
        for e in unit_data:
            if e.get("form") in ("10-Q", "10-K") and "end" in e:
                rows.append({
                    "date":  e["end"],
                    "value": e["val"],
                    "form":  e["form"],
                    "accn":  e.get("accn", ""),
                })

        if not rows:
            print(f"    no rows: {concept}")
            continue

        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("accn").drop_duplicates("date", keep="last")
        s = df.set_index("date")["value"].rename(friendly)
        series_list.append(s)
        print(f"    {friendly}: {len(s)} data points  ({s.index.min().date()} → {s.index.max().date()})")

    if series_list:
        edgar_df = pd.concat(series_list, axis=1)
        # Filter 2010 onwards to keep it clean
        edgar_df = edgar_df[edgar_df.index >= "2010-01-01"].sort_index()
        edgar_df.index.name = "Quarter"
        edgar_df.insert(0, "Company", "American Express")
        edgar_df.insert(1, "Ticker", "AXP")

        # Convert dollar columns to billions
        for col in ["Total Revenue", "Net Income", "Pretax Income", "Tax Provision",
                    "Interest Expense", "Interest Income", "Total Assets",
                    "Long Term Debt", "Stockholders Equity"]:
            if col in edgar_df.columns:
                edgar_df[col] = edgar_df[col] / 1e9

        edgar_df.reset_index().to_csv(
            "/Users/barbiejindal/Desktop/amex_project/amex_edgar_quarterly.csv", index=False
        )
        print(f"\nSaved → amex_edgar_quarterly.csv  ({len(edgar_df)} rows)")
        print("\nPreview (last 6 quarters):")
        preview = ["Total Revenue", "Net Income", "Diluted EPS", "Total Assets"]
        preview = [c for c in preview if c in edgar_df.columns]
        print(edgar_df[preview].tail(6).to_string())
    else:
        print("  No EDGAR data extracted.")

except Exception as ex:
    print(f"  EDGAR fetch failed: {ex}")


# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
print("\n=== FILES SAVED ===")
print("  amex_annual.csv          — annual data for AXP, V, MA, COF")
print("  amex_edgar_quarterly.csv — quarterly data for AXP from SEC EDGAR")
print("\nNext: run 2_feature_eng.py to compute ratios and growth metrics")
