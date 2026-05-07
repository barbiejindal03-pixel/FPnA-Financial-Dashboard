# R Script

### 4_arima_forecast.R — Time Series Forecast

This script takes the engineered features dataset and builds ARIMA models to forecast Amex's revenue and net income through the end of 2026.

ARIMA (AutoRegressive Integrated Moving Average) is the standard approach for financial time series forecasting. The script uses `auto.arima()` from the R forecast package, which automatically searches for the best model structure rather than requiring manual parameter selection.

For each metric it:
- Runs an Augmented Dickey-Fuller test to check whether the series is stationary
- Fits the best ARIMA model
- Validates residuals with a Ljung-Box test
- Forecasts four quarters ahead with 80% and 95% confidence intervals
- Saves the results to `data/processed/forecast_results.csv`
- Saves forecast charts to the `charts/` folder

```bash
Rscript scripts/r/4_arima_forecast.R
```

Required R packages (install once):
```r
install.packages(c("forecast", "ggplot2", "dplyr", "readr", "tseries"))
```
