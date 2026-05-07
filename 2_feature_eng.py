"""
Step 2: Feature Engineering
Input:  amex_clean_v2.csv  (65 quarters, raw numbers)
Output: amex_features.csv  (same rows + new ratio columns)
"""

import pandas as pd
import numpy as np

df = pd.read_csv("/Users/barbiejindal/Desktop/amex_project/amex_clean_v2.csv")
df["Quarter"] = pd.to_datetime(df["Quarter"])
df = df.sort_values("Quarter").reset_index(drop=True)

print(f"Loaded: {len(df)} rows")
print(f"Columns: {list(df.columns)}\n")

# ── 1. NET MARGIN ────────────────────────────────────────────────────────────
# How many cents of profit per dollar of revenue
# High margin = efficient company
df["Net Margin"] = df["Net Income"] / df["Total Revenue"]

# ── 2. TAX RATE ──────────────────────────────────────────────────────────────
# What % of pre-tax income goes to taxes
df["Tax Rate"] = df["Tax Provision"] / (df["Net Income"] + df["Tax Provision"])

# ── 3. INTEREST SPREAD ───────────────────────────────────────────────────────
# Interest earned minus interest paid (core banking profitability)
df["Interest Spread"] = df["Interest Income"] - df["Interest Expense"]

# ── 4. INTEREST COVERAGE ─────────────────────────────────────────────────────
# How many times can Amex pay its interest from earnings
# Higher = safer, less risk of default
df["Interest Coverage"] = df["Interest Income"] / df["Interest Expense"]

# ── 5. ASSET EFFICIENCY ───────────────────────────────────────────────────────
# Revenue generated per dollar of assets owned
# Higher = working assets harder
df["Asset Efficiency"] = df["Total Revenue"] / df["Total Assets"]

# ── 6. DEBT-TO-EQUITY ────────────────────────────────────────────────────────
# How leveraged is Amex (debt vs own money)
# Higher = more risk
df["Debt to Equity"] = df["Long Term Debt"] / df["Stockholders Equity"]

# ── 7. EQUITY RATIO ──────────────────────────────────────────────────────────
# What % of assets are funded by equity (not debt)
df["Equity Ratio"] = df["Stockholders Equity"] / df["Total Assets"]

# ── 8. RETURN ON EQUITY (ROE) ────────────────────────────────────────────────
# Net income generated per dollar of shareholder equity
# Key metric investors watch
df["ROE"] = df["Net Income"] / df["Stockholders Equity"]

# ── 9. RETURN ON ASSETS (ROA) ────────────────────────────────────────────────
# Net income per dollar of total assets
df["ROA"] = df["Net Income"] / df["Total Assets"]

# ── 10. YoY REVENUE GROWTH ───────────────────────────────────────────────────
# Compare to same quarter last year (not last quarter — avoids seasonal noise)
df["Revenue YoY Growth"] = df["Total Revenue"].pct_change(periods=4)

# ── 11. YoY NET INCOME GROWTH ────────────────────────────────────────────────
df["Net Income YoY Growth"] = df["Net Income"].pct_change(periods=4)

# ── 12. ASSET GROWTH ─────────────────────────────────────────────────────────
# How fast is Amex growing its balance sheet
df["Asset YoY Growth"] = df["Total Assets"].pct_change(periods=4)

# ── Clean up: replace inf values (division by zero) with NaN ─────────────────
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "/Users/barbiejindal/Desktop/amex_project/amex_features.csv"
df.to_csv(out, index=False)

# ── Summary ───────────────────────────────────────────────────────────────────
print("=== NEW FEATURES CREATED ===\n")
new_cols = ["Net Margin", "Tax Rate", "Interest Spread", "Interest Coverage",
            "Asset Efficiency", "Debt to Equity", "Equity Ratio",
            "ROE", "ROA", "Revenue YoY Growth", "Net Income YoY Growth", "Asset YoY Growth"]

for col in new_cols:
    valid = df[col].notna().sum()
    mean  = df[col].mean()
    print(f"  {col:25s}  {valid:2d} valid rows  |  avg = {mean:.3f}")

print(f"\nSaved → {out}")
print(f"Total columns now: {len(df.columns)}  (was 10, added {len(new_cols)})")

print("\n=== LAST 6 QUARTERS PREVIEW ===")
preview = ["Quarter", "Total Revenue", "Net Income", "Net Margin", "ROE", "Debt to Equity"]
print(df[preview].tail(6).round(3).to_string(index=False))

print("\nNext: run 3_ml_models.py")
