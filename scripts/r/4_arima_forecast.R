# ============================================================
# Step 4: ARIMA Time Series Forecast
# Input:  amex_features.csv
# Models: ARIMA on Total Revenue + Net Income
# Output: forecast_results.csv + 2 PNG charts
# ============================================================

# ── Install packages if missing ──────────────────────────────
packages <- c("forecast", "ggplot2", "dplyr", "readr", "tseries")
for (pkg in packages) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
    library(pkg, character.only = TRUE)
  }
}

OUT <- "/Users/barbiejindal/Desktop/amex_project/"

# ── Load data ────────────────────────────────────────────────
df <- read_csv(paste0(OUT, "amex_features.csv"), show_col_types = FALSE)
df$Quarter <- as.Date(df$Quarter)
df <- df[order(df$Quarter), ]

cat("Loaded:", nrow(df), "rows\n")
cat("Date range:", format(min(df$Quarter)), "to", format(max(df$Quarter)), "\n\n")


# ════════════════════════════════════════════════════════════
# HELPER: run ARIMA on one metric, return forecast
# ════════════════════════════════════════════════════════════
run_arima <- function(series_name, label, unit) {

  cat(rep("=", 55), "\n", sep = "")
  cat("ARIMA FORECAST:", label, "\n")
  cat(rep("=", 55), "\n", sep = "")

  # Pull non-NA values
  raw <- df[[series_name]]
  dates <- df$Quarter[!is.na(raw)]
  vals  <- raw[!is.na(raw)]

  cat("Non-NA quarters available:", length(vals), "\n")
  cat("Range:", format(min(dates)), "to", format(max(dates)), "\n\n")

  # ── Convert to quarterly time series object ──────────────
  # Find start year + quarter
  start_yr <- as.integer(format(min(dates), "%Y"))
  start_q  <- ceiling(as.integer(format(min(dates), "%m")) / 3)
  ts_data  <- ts(vals, start = c(start_yr, start_q), frequency = 4)

  # ── Stationarity test (ADF) ──────────────────────────────
  cat("Augmented Dickey-Fuller Test (checks if series is stationary):\n")
  adf <- adf.test(ts_data, alternative = "stationary")
  cat("  p-value:", round(adf$p.value, 4),
      "→", ifelse(adf$p.value < 0.05, "STATIONARY (good)", "NON-STATIONARY (will auto-difference)"), "\n\n")

  # ── Fit ARIMA — auto.arima picks best p,d,q automatically ─
  cat("Fitting ARIMA model (auto-selecting best parameters)...\n")
  model <- auto.arima(
    ts_data,
    seasonal     = TRUE,   # capture quarterly seasonality
    stepwise     = FALSE,  # search more models (slower but better)
    approximation = FALSE,
    trace        = FALSE
  )

  cat("Best model selected:", as.character(model), "\n")
  cat("\nModel Summary:\n")
  print(summary(model))

  # ── Residual check ───────────────────────────────────────
  cat("\nLjung-Box Test (residuals should be white noise, p > 0.05):\n")
  lb <- Box.test(residuals(model), lag = 8, type = "Ljung-Box")
  cat("  p-value:", round(lb$p.value, 4),
      "→", ifelse(lb$p.value > 0.05, "GOOD (residuals random)", "WARNING (some pattern left)"), "\n\n")

  # ── Forecast 4 quarters ahead (full 2026) ────────────────
  fc <- forecast(model, h = 4)

  # Build result table
  future_dates <- seq(max(dates) + 90, by = "quarter", length.out = 4)
  fc_df <- data.frame(
    Quarter   = future_dates,
    Metric    = label,
    Forecast  = as.numeric(fc$mean),
    Lower_80  = as.numeric(fc$lower[, 1]),
    Upper_80  = as.numeric(fc$upper[, 1]),
    Lower_95  = as.numeric(fc$lower[, 2]),
    Upper_95  = as.numeric(fc$upper[, 2])
  )

  cat("2026 Quarterly Forecast (", unit, "):\n", sep = "")
  tmp <- fc_df[, c("Quarter", "Forecast", "Lower_95", "Upper_95")]
  tmp[, c("Forecast","Lower_95","Upper_95")] <- round(tmp[, c("Forecast","Lower_95","Upper_95")], 3)
  print(tmp)

  # ── Plot ─────────────────────────────────────────────────
  png(paste0(OUT, "chart_arima_", series_name, ".png"),
      width = 1200, height = 600, res = 120)

  plot(fc,
       main  = paste("ARIMA Forecast:", label, "(2026)"),
       xlab  = "Year",
       ylab  = paste(label, "(", unit, ")"),
       col   = "steelblue",
       fcol  = "firebrick",
       shadecols = c("#f8c8c8", "#f09090"),
       lwd   = 2)
  abline(v = time(ts_data)[length(ts_data)], lty = 2, col = "gray40")
  legend("topleft",
         legend = c("Historical", "Forecast", "80% CI", "95% CI"),
         col    = c("steelblue", "firebrick", "#f8c8c8", "#f09090"),
         lty    = c(1, 1, NA, NA),
         pch    = c(NA, NA, 15, 15),
         bty    = "n")

  dev.off()
  cat("Chart saved → chart_arima_", series_name, ".png\n\n", sep = "")

  return(fc_df)
}


# ════════════════════════════════════════════════════════════
# RUN ON BOTH METRICS
# ════════════════════════════════════════════════════════════
rev_forecast <- run_arima("Total Revenue", "Total Revenue", "$B")
ni_forecast  <- run_arima("Net Income",    "Net Income",    "$B")


# ════════════════════════════════════════════════════════════
# COMBINED SUMMARY TABLE
# ════════════════════════════════════════════════════════════
all_forecasts <- rbind(rev_forecast, ni_forecast)
write_csv(all_forecasts, paste0(OUT, "forecast_results.csv"))

cat(rep("=", 55), "\n", sep = "")
cat("FORECAST SUMMARY — 2026 Full Year\n")
cat(rep("=", 55), "\n", sep = "")

annual_rev <- sum(rev_forecast$Forecast)
annual_ni  <- sum(ni_forecast$Forecast)
annual_margin <- annual_ni / annual_rev

cat(sprintf("Projected 2026 Annual Revenue  : $%.2f B\n", annual_rev))
cat(sprintf("Projected 2026 Annual Net Income: $%.2f B\n", annual_ni))
cat(sprintf("Implied Net Margin              : %.1f%%\n",  annual_margin * 100))

cat("\nAll results saved to forecast_results.csv\n")
cat("Charts: chart_arima_Total Revenue.png, chart_arima_Net Income.png\n")
