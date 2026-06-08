# American Express — Earning Performance Analysis

Live Demo: [amex-dashboard.streamlit.app](https://amex-dashboard.streamlit.app)

---

## Why American Express?

American Express is one of those companies that has always stood out to me. Founded in 1850, it started as an express mail business and quietly became one of the most powerful financial brands in the world. Today, over 130 million people carry an Amex card.

What makes Amex different from every other card company is something called the closed-loop network. Visa and Mastercard just process payments — they never actually touch the money. Amex does everything itself: it issues the card, processes the payment, and lends the money. That means it takes on more risk than its competitors, but it also earns far more per customer and has a much deeper relationship with the people who use it.

I wanted to understand this business from the inside. Not through a news article or an investor presentation, but by pulling the actual numbers Amex files with regulators, building models on top of them, and seeing what the data says about how this company really works. That's what this project is.

---

## The Concept

The idea was to build the kind of analysis that a financial analyst at a bank or consulting firm would do internally — but entirely from publicly available data and open source tools.

The pipeline goes in five stages:

1. Pull 10 years of quarterly filings directly from the SEC
2. Turn raw numbers into financial ratios that actually mean something
3. Train machine learning models to find what drives profitability
4. Forecast 2026 revenue and net income using time series analysis
5. Put everything into a live interactive dashboard anyone can explore

The result is a full FP&A platform — built on real data, real models, and a real understanding of the business.

---

## About the Data

Every public company in the United States is legally required to file quarterly and annual financial reports with the SEC. These filings are stored in a database called EDGAR and are completely free to access. No API key, no subscription, no middleman.

The data was pulled directly from the SEC EDGAR XBRL API — the same source regulators, institutional investors, and research firms use. The response comes back as JSON, and the pipeline extracts the specific financial metrics needed, cleans them, and saves them as CSVs.

The trickiest part was a quirk in how EDGAR stores income statement data. Some filings report year-to-date cumulative totals rather than just that quarter's numbers. A Q3 filing might show nine months of revenue instead of three. The pipeline handles this by checking the length of each reporting period — anything outside the 80 to 105 day range of a real quarter gets dropped.

What ended up in the dataset:

| File | Rows | What it contains |
|---|---|---|
| amex_clean_v2.csv | 65 quarters | Core financials for AXP, 2010 to 2026 |
| amex_features.csv | 65 quarters | All raw data plus 12 engineered ratios |
| amex_annual.csv | 20 rows | Annual data for AXP, Visa, Mastercard, Capital One |
| competitors_full.csv | 28 rows | Recent quarterly data across all four companies |
| forecast_results.csv | 8 rows | ARIMA quarterly forecasts for 2026 |

---

## Feature Engineering

Raw numbers alone cannot teach a model anything useful. Telling a model that revenue was $17 billion in one quarter means nothing on its own. What matters is the relationship between numbers — how efficiently that revenue was generated, how much of it turned into profit, and how much debt was taken on to get there.

Feature engineering creates those relationships. Twelve new metrics were computed from the raw data:

| Feature | How it is calculated | What it tells you |
|---|---|---|
| Net Margin | Net Income divided by Revenue | Of every dollar Amex earns, how many cents become profit |
| Tax Rate | Tax Provision divided by Pretax Income | What share of earnings go to taxes |
| Interest Spread | Interest Income minus Interest Expense | How much Amex earns from lending after paying its own borrowing costs |
| Interest Coverage | Interest Income divided by Interest Expense | How comfortably Amex can cover its debt obligations |
| Asset Efficiency | Revenue divided by Total Assets | How hard Amex's assets are working to generate revenue |
| Debt to Equity | Long Term Debt divided by Stockholders Equity | How much of the business is funded by debt versus its own money |
| Equity Ratio | Equity divided by Total Assets | What share of Amex's asset base is owned outright |
| ROE | Net Income divided by Equity | How much profit shareholders get for every dollar they have invested |
| ROA | Net Income divided by Total Assets | How efficiently the entire asset base turns into profit |
| Revenue YoY Growth | Current quarter versus same quarter last year | Whether growth is accelerating or slowing |
| Net Income YoY Growth | Same comparison for earnings | Whether profitability is improving year over year |
| Asset YoY Growth | Same comparison for total assets | How fast Amex is expanding its balance sheet |

---

## The Models

Three different modelling approaches were used, each answering a different question.

### Linear Regression

The question this model answers is: which financial ratios actually drive Amex's net margin?

Linear regression fits a mathematical relationship between a set of input features and an output. Each input gets a coefficient — a number that says how much that feature moves the output when it changes. Features were standardised before fitting so the coefficients can be compared fairly against each other.

The model was trained on seven ratios and tested on data it had never seen. It explained 97.7% of all variation in Amex's net margin across the dataset (R² = 0.977), which is an unusually strong result.

The main finding was that ROA — return on assets — is by far the most powerful predictor of margin. When Amex generates strong returns from its asset base, margins follow almost automatically. Tax rate and asset efficiency also matter, but considerably less. Debt levels and interest coverage have a smaller but measurable effect.

### Decision Tree

The question here is: what predicts how much net income Amex will earn in a given quarter?

A decision tree learns a set of if-then rules from the data. It keeps splitting the dataset on whichever feature best separates high and low net income outcomes until it arrives at a prediction. The result is a tree of conditions that can be followed step by step, which makes it one of the most interpretable ML models available.

The model explained 72.3% of net income variation (R² = 0.723).

The most important finding was that Debt-to-Equity is the single strongest predictor, accounting for 57% of the tree's decisions. When leverage is below 1.92 and total assets exceed $271 billion, the model predicts net income of around $2.99 billion for that quarter. ROA is the second most important signal at 26%, followed by long term debt at 12%.

### ARIMA Time Series

The question here is: where will revenue and net income be in 2026?

ARIMA is the industry standard model for financial time series forecasting. It works by studying how a variable has moved over time — its trend, its momentum, and how it recovers from unexpected shocks — and then projecting that behaviour forward.

The R forecast package's auto.arima function was used, which automatically searches for the best model structure rather than requiring manual selection.

For revenue, the best model was ARIMA(0,1,0) with drift. This means revenue follows a random walk with a consistent upward push of about $0.31 billion per quarter. No complex seasonal patterns were found — revenue just grows steadily.

For net income, the best model was ARIMA(0,1,1). The moving average term absorbs one-period earnings shocks — things like the COVID quarters where earnings collapsed and then snapped back. This makes the net income forecast smoother and more realistic than a naive trend projection.

Both models passed the Ljung-Box test, confirming that the residuals are random noise. That means the models captured everything meaningful in the historical data.

---

## The Dashboard

The dashboard was built with Streamlit and Plotly using Amex's actual brand colours — navy, blue, and gold. It is designed so that someone with no finance background can open it and understand what they are looking at.

Here is what each section shows and how to read it.

### Executive Overview

This is the starting point. Five cards at the top show the most recent quarter's headline numbers — revenue, net income, margin, return on equity, and the debt-to-equity ratio. Below that are four charts covering the full historical period.

The revenue and net income chart shows both metrics together. Revenue is shown as bars because it is the foundation — the total amount Amex brought in. Net income is shown as a line on top because it is what remained after all costs. When the line follows the bars upward consistently, the business is healthy. When the line dips while the bars stay flat — as happened in 2020 — costs rose faster than revenue.

The net margin chart has a gold dotted line showing the long-run average of 14.7%. Quarters above that line were more profitable than usual. The sharp dip to negative margins in mid-2020 was COVID — Amex's cardholders spend heavily on travel and dining, both of which stopped almost entirely.

The debt-to-equity chart uses colour to show risk levels. Blue bars are low leverage. As bars turn gold and then red, Amex is taking on more debt relative to its equity. The spike in 2020 reflects emergency credit lines drawn during the pandemic, which were gradually paid down through 2022 and 2023.

### Revenue and Income Trends

This section lets you look at any single metric in detail across the full date range. The gold dotted line is a four-quarter rolling average — it smooths out the noise so you can see the underlying trend more clearly. When individual bars sit consistently above the rolling average, growth is accelerating. When they drop below it, momentum is slowing.

The YoY growth charts below show whether each quarter was better or worse than the same quarter the previous year. Green bars mean growth, red means contraction. The cluster of red bars in 2020 shows the pandemic impact. The explosive green bars in 2021 and 2022 show the recovery — in some quarters Amex's net income grew over 100% year over year as spending came back faster than anyone expected.

### ML Model Insights

This section shows what the two machine learning models found.

The linear regression tab shows a bar chart of coefficients. Each bar represents one financial ratio. The length of the bar shows how strongly that ratio influences net margin. A bar pointing right means higher values of that ratio push margin up. A bar pointing left means they pull it down. The actual vs predicted chart at the bottom shows how closely the model tracks reality — the two lines should overlap closely, and for this model they do.

The decision tree tab shows feature importance — essentially how often each variable was used by the tree when making its predictions. A variable with 57% importance means more than half of all predictions relied on that feature as a key decision point.

### ARIMA 2026 Forecast

The navy line is the historical data — what actually happened. The dashed coloured line is the forecast. The shaded bands show uncertainty — the darker band represents 80% confidence, meaning the model expects the true value to land inside that range eight times out of ten. The lighter outer band is the 95% confidence range.

The bands get wider as the forecast goes further into the future, which is honest — uncertainty grows over time. Revenue bands are narrower than net income bands because revenue is more predictable. Net income is more sensitive to interest rates, credit losses, and one-time charges, so the model acknowledges that by expressing more uncertainty.

### Competitor Benchmarking

This section places Amex alongside Visa, Mastercard, and Capital One. The comparison shows that Amex has lower revenue than Visa and Mastercard, which might seem surprising given its profile. The reason is the business model difference. Visa and Mastercard run payment networks — they collect a small fee on every transaction but never hold any money or extend any credit. Their margins are extremely high as a result. Amex actually lends money, which means costs are higher but so is the revenue per customer. Capital One is the fairest comparison because it also issues cards and carries credit risk.

### Scenario Simulator

This is the most interactive part of the dashboard. It lets you change financial assumptions using sliders and watch the decision tree model re-run its prediction in real time.

Move the total assets slider up and the model predicts what net income would look like if Amex grew its balance sheet to that size. Move the interest income slider to simulate a higher interest rate environment. Move the long term debt slider up to see how increased leverage would affect the earnings prediction.

The sensitivity chart at the bottom shows how predicted net income responds across the full range of total asset values, with everything else held constant. The flat sections in the chart are the decision tree's thresholds — points where the model's rule changes and it jumps to a new prediction range.

---

## Key Results

| Metric | Value |
|---|---|
| Linear Regression R² | 0.977 |
| Decision Tree R² | 0.723 |
| Top net margin driver | Return on Assets |
| Top net income predictor | Debt-to-Equity ratio |
| 2026 Revenue forecast | $78.7B |
| 2026 Net Income forecast | $11.3B |
| Implied 2026 Net Margin | 14.4% |
| Historical average net margin | 14.7% |

---

## Project Structure

```
FPnA-Financial-Dashboard/
│
├── 5_dashboard.py              # Streamlit dashboard — run this
├── requirements.txt
│
├── scripts/
│   ├── python/
│   │   ├── 1e_clean_edgar.py   # Pull data from SEC EDGAR
│   │   ├── 2_feature_eng.py    # Compute 12 financial ratios
│   │   └── 3_ml_models.py      # Linear Regression + Decision Tree
│   └── r/
│       └── 4_arima_forecast.R  # ARIMA 2026 forecast
│
├── data/
│   ├── raw/                    # Original files from SEC EDGAR
│   └── processed/              # Cleaned and engineered datasets
│
└── charts/                     # Saved output charts
```

---

## How to Run Locally

```bash
git clone https://github.com/barbiejindal03-pixel/FPnA-Financial-Dashboard.git
cd FPnA-Financial-Dashboard
pip install -r requirements.txt
streamlit run 5_dashboard.py
```

For the ARIMA forecast, open R and run:
```r
install.packages(c("forecast", "ggplot2", "dplyr", "readr", "tseries"))
source("scripts/r/4_arima_forecast.R")
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.14 | Data engineering, feature engineering, ML |
| SEC EDGAR XBRL API | 10 years of official quarterly filings |
| pandas, numpy | Data cleaning and transformation |
| scikit-learn | Linear Regression, Decision Tree |
| R, forecast package | ARIMA time series forecasting |
| Streamlit | Interactive dashboard |
| Plotly | Charts and visualisations |

---

For educational and analytical purposes only. Not financial advice.
