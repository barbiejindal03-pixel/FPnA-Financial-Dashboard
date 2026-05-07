"""
Fix: EDGAR income statement items include YTD cumulative entries.
Solution: use the 'start' date field — only keep entries where
          period length ≈ 90 days (true quarterly), not 180/270/365.
Output: amex_clean_v2.csv
"""
import requests
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

AXP_CIK = "0000004962"
HEADERS  = {"User-Agent": "amex-analysis barbiejindal03@gmail.com"}
START    = "2010-01-01"

CONCEPTS = {
    "RevenuesNetOfInterestExpense":   "Total Revenue",
    "NetIncomeLoss":                  "Net Income",
    "IncomeTaxExpenseBenefit":        "Tax Provision",
    "InterestExpense":                "Interest Expense",
    "InterestAndDividendIncomeOperating": "Interest Income",
}
# Balance sheet / point-in-time (no start date issue)
INSTANT_CONCEPTS = {
    "Assets":               "Total Assets",
    "LongTermDebt":         "Long Term Debt",
    "StockholdersEquity":   "Stockholders Equity",
}

print("Fetching AXP EDGAR facts...")
url  = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{AXP_CIK}.json"
resp = requests.get(url, headers=HEADERS, timeout=60)
resp.raise_for_status()
us_gaap = resp.json()["facts"]["us-gaap"]

# ── Income statement: filter to true quarterly periods (~90 days) ───────────
flow_series = []
print("\n[Income Statement — quarterly periods only]")
for concept, friendly in CONCEPTS.items():
    if concept not in us_gaap:
        print(f"  SKIP: {concept}")
        continue

    unit_data = us_gaap[concept].get("units", {}).get("USD", [])
    rows = []
    for e in unit_data:
        if "start" not in e or "end" not in e:
            continue
        start_dt = pd.to_datetime(e["start"])
        end_dt   = pd.to_datetime(e["end"])
        days     = (end_dt - start_dt).days
        # True quarter = 85–100 days; reject YTD cumulative (180, 270, 365)
        if 80 <= days <= 105 and e.get("form") in ("10-Q", "10-K"):
            rows.append({
                "date":  e["end"],
                "value": e["val"],
                "accn":  e.get("accn", ""),
            })
    if not rows:
        print(f"  no quarterly rows: {concept}")
        continue

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("accn").drop_duplicates("date", keep="last")
    s  = df.set_index("date")["value"].rename(friendly)
    # Filter to 2010+
    s  = s[s.index >= START]
    print(f"  {friendly}: {len(s)} quarters  ({s.index.min().date()} → {s.index.max().date()})")
    flow_series.append(s)

# ── Balance sheet: instant (point-in-time) — no filtering needed ────────────
balance_series = []
print("\n[Balance Sheet — instant values]")
for concept, friendly in INSTANT_CONCEPTS.items():
    if concept not in us_gaap:
        print(f"  SKIP: {concept}")
        continue

    unit_data = us_gaap[concept].get("units", {}).get("USD", [])
    rows = []
    for e in unit_data:
        if "end" not in e:
            continue
        rows.append({"date": e["end"], "value": e["val"], "accn": e.get("accn", "")})

    if not rows:
        continue

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("accn").drop_duplicates("date", keep="last")
    s  = df.set_index("date")["value"].rename(friendly)
    s  = s[s.index >= START]
    print(f"  {friendly}: {len(s)} entries  ({s.index.min().date()} → {s.index.max().date()})")
    balance_series.append(s)

# ── Combine ─────────────────────────────────────────────────────────────────
all_series = flow_series + balance_series
df = pd.concat(all_series, axis=1).sort_index()

# ── Add EPS from yfinance ────────────────────────────────────────────────────
try:
    import yfinance as yf
    axp = yf.Ticker("AXP")
    inc_q = axp.quarterly_income_stmt
    if inc_q is not None and not inc_q.empty:
        inc_q = inc_q.T
        inc_q.index = pd.to_datetime(inc_q.index)
        for col in ["Diluted EPS", "Basic EPS"]:
            if col in inc_q.columns:
                df = df.join(inc_q[[col]], how="outer")
        print(f"\n[yfinance] EPS added: {(~df['Diluted EPS'].isna()).sum()} quarters")
except Exception as ex:
    print(f"  EPS fetch skipped: {ex}")

# ── Convert $ → billions ─────────────────────────────────────────────────────
DOLLAR_COLS = ["Total Revenue", "Net Income", "Tax Provision",
               "Interest Expense", "Interest Income",
               "Total Assets", "Long Term Debt", "Stockholders Equity"]
for col in DOLLAR_COLS:
    if col in df.columns:
        df[col] = df[col] / 1e9

df.index.name = "Quarter"

# ── Save ─────────────────────────────────────────────────────────────────────
out = "/Users/barbiejindal/Desktop/amex_project/amex_clean_v2.csv"
df.reset_index().to_csv(out, index=False)

print(f"\n=== FINAL CLEAN DATASET ===")
print(f"Rows: {len(df)}  |  {df.index.min().date()} → {df.index.max().date()}")
print(f"\nMissing values per column:")
print(df.isna().sum().to_string())
print(f"\nLast 8 rows:")
print(df.tail(8).round(3).to_string())
print(f"\nSaved → {out}")
