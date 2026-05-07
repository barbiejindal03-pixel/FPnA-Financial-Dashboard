"""
Step 1: Pull 10 years of quarterly financial data for Amex + competitors
Companies: AXP (Amex), V (Visa), MA (Mastercard), COF (Capital One), DFS (Discover)
Source: yfinance (Yahoo Finance) — free, no API key needed
Output: amex_full.csv, competitors_full.csv
"""

import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# ── Companies to pull ────────────────────────────────────────────────────────
TICKERS = {
    "AXP": "American Express",
    "V":   "Visa",
    "MA":  "Mastercard",
    "COF": "Capital One",
    "DFS": "Discover",
}

# ── Which columns we want from the income statement ─────────────────────────
INCOME_COLS = [
    "Total Revenue",
    "Net Income",
    "Pretax Income",
    "Tax Provision",
    "Interest Expense",
    "Interest Income",
    "Selling General And Administration",
    "Diluted EPS",
    "Basic EPS",
]

# ── Which columns we want from the balance sheet ────────────────────────────
BALANCE_COLS = [
    "Total Assets",
    "Total Debt",
    "Stockholders Equity",
    "Cash And Cash Equivalents",
]

# ── Which columns we want from cash flow ────────────────────────────────────
CASHFLOW_COLS = [
    "Free Cash Flow",
    "Capital Expenditure",
    "Operating Cash Flow",
]


def pull_ticker(ticker_symbol, company_name):
    """Pull quarterly financials for one ticker and return a merged DataFrame."""
    print(f"  Pulling {company_name} ({ticker_symbol})...")
    t = yf.Ticker(ticker_symbol)

    # --- Income Statement ---
    inc = t.quarterly_income_stmt
    if inc is None or inc.empty:
        print(f"    WARNING: No income data for {ticker_symbol}")
        return None

    # Transpose so dates are rows, metrics are columns
    inc = inc.T
    inc.index = pd.to_datetime(inc.index)

    # Keep only columns that exist in this dataset
    inc_keep = [c for c in INCOME_COLS if c in inc.columns]
    inc = inc[inc_keep]

    # --- Balance Sheet ---
    bal = t.quarterly_balance_sheet
    if bal is not None and not bal.empty:
        bal = bal.T
        bal.index = pd.to_datetime(bal.index)
        bal_keep = [c for c in BALANCE_COLS if c in bal.columns]
        bal = bal[bal_keep]
    else:
        bal = pd.DataFrame(index=inc.index)

    # --- Cash Flow ---
    cf = t.quarterly_cashflow
    if cf is not None and not cf.empty:
        cf = cf.T
        cf.index = pd.to_datetime(cf.index)
        cf_keep = [c for c in CASHFLOW_COLS if c in cf.columns]
        cf = cf[cf_keep]
    else:
        cf = pd.DataFrame(index=inc.index)

    # --- Merge all three on date index ---
    merged = inc.join(bal, how="outer").join(cf, how="outer")
    merged.index.name = "Quarter"
    merged.insert(0, "Company", company_name)
    merged.insert(1, "Ticker", ticker_symbol)

    # Sort oldest → newest
    merged = merged.sort_index()

    print(f"    Got {len(merged)} quarters  |  {merged.index.min().date()} → {merged.index.max().date()}")
    return merged


# ── Pull all tickers ─────────────────────────────────────────────────────────
print("\n=== Pulling quarterly financials ===\n")

all_frames = []
for sym, name in TICKERS.items():
    df = pull_ticker(sym, name)
    if df is not None:
        all_frames.append(df)

# ── Combine ──────────────────────────────────────────────────────────────────
combined = pd.concat(all_frames)
combined.reset_index(inplace=True)

# Convert dollar columns from raw units to billions (easier to read)
dollar_cols = [
    "Total Revenue", "Net Income", "Pretax Income", "Tax Provision",
    "Interest Expense", "Interest Income", "Selling General And Administration",
    "Total Assets", "Total Debt", "Stockholders Equity", "Cash And Cash Equivalents",
    "Free Cash Flow", "Capital Expenditure", "Operating Cash Flow",
]
for col in dollar_cols:
    if col in combined.columns:
        combined[col] = combined[col] / 1e9   # → billions

# ── Split: Amex-only vs all companies ───────────────────────────────────────
amex_df = combined[combined["Ticker"] == "AXP"].copy()
comp_df = combined.copy()

# ── Save ─────────────────────────────────────────────────────────────────────
amex_path = "/Users/barbiejindal/Desktop/amex_project/amex_full.csv"
comp_path = "/Users/barbiejindal/Desktop/amex_project/competitors_full.csv"

amex_df.to_csv(amex_path, index=False)
comp_df.to_csv(comp_path, index=False)

print(f"\n=== Done ===")
print(f"Amex data  → {amex_path}  ({len(amex_df)} rows)")
print(f"All companies → {comp_path}  ({len(comp_df)} rows)")

# ── Quick preview ────────────────────────────────────────────────────────────
print("\n--- Amex preview (last 4 quarters) ---")
preview_cols = ["Quarter", "Total Revenue", "Net Income", "Diluted EPS", "Total Assets"]
preview_cols = [c for c in preview_cols if c in amex_df.columns]
print(amex_df[preview_cols].tail(4).to_string(index=False))

print("\n--- All companies: row count per ticker ---")
print(combined.groupby("Ticker")["Quarter"].count().to_string())
