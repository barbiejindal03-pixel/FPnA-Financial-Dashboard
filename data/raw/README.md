# Raw Data

These are the original files pulled directly from SEC EDGAR and Yahoo Finance before any cleaning or processing. They are kept here for reference and reproducibility.

| File | Source | Description |
|---|---|---|
| amex_quarterly.csv | yfinance | Initial pull, limited to recent quarters |
| amex_full.csv | yfinance | Expanded pull across multiple tickers |
| amex_clean.csv | SEC EDGAR | First EDGAR extract, before YTD fix |
| amex_edgar_quarterly.csv | SEC EDGAR | EDGAR extract with cumulative entries still included |
| competitor_data.csv | yfinance | Raw competitor revenue and net income |

Do not use these files for analysis. The cleaned versions in `data/processed/` are what the scripts and dashboard actually use.
