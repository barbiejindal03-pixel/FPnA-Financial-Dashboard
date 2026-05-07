# Processed Data

These are the clean, analysis-ready files produced by the Python pipeline. The dashboard and models read from this folder.

| File | Rows | Description |
|---|---|---|
| amex_clean_v2.csv | 65 | Core quarterly financials for AXP, 2010 to 2026. True standalone quarters only — cumulative YTD entries removed. |
| amex_features.csv | 65 | Everything in amex_clean_v2 plus 12 engineered financial ratios. This is the main dataset for ML. |
| amex_annual.csv | 20 | Annual data for AXP, Visa, Mastercard, and Capital One across 5 years. Used for competitor benchmarking. |
| competitors_full.csv | 28 | Recent quarterly data across all four companies. |
| forecast_results.csv | 8 | ARIMA quarterly forecasts for 2026 — revenue and net income with confidence intervals. |
