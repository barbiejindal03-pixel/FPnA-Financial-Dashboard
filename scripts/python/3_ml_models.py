"""
Step 3: ML Models
Input:  amex_features.csv
Models: 1) Linear Regression  → which features drive Net Margin
        2) Decision Tree       → feature importance for predicting Net Income
Output: charts saved as PNG files + printed results
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # save to file instead of opening window
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

OUT = "/Users/barbiejindal/Desktop/amex_project/"

df = pd.read_csv(OUT + "amex_features.csv")
df["Quarter"] = pd.to_datetime(df["Quarter"])
print(f"Loaded: {len(df)} rows, {len(df.columns)} columns\n")


# ════════════════════════════════════════════════════════════════════════════
# MODEL 1 — LINEAR REGRESSION: What drives Net Margin?
# ════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("MODEL 1: LINEAR REGRESSION → predicting Net Margin")
print("=" * 60)

# Features available that correlate with margin
LR_FEATURES = [
    "Interest Coverage",
    "Asset Efficiency",
    "Debt to Equity",
    "Equity Ratio",
    "ROA",
    "Revenue YoY Growth",
    "Tax Rate",
]
LR_TARGET = "Net Margin"

# Drop rows where any of these columns is NaN
lr_df = df[LR_FEATURES + [LR_TARGET]].dropna()
print(f"Rows with complete data for regression: {len(lr_df)}")

X_lr = lr_df[LR_FEATURES]
y_lr = lr_df[LR_TARGET]

# Scale features (makes coefficients comparable)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_lr)

# Train/test split: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_lr, test_size=0.2, random_state=42
)

lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)

r2  = r2_score(y_test, y_pred_lr)
mae = mean_absolute_error(y_test, y_pred_lr)

print(f"\nModel Performance:")
print(f"  R² Score : {r2:.3f}  (1.0 = perfect, 0 = useless)")
print(f"  MAE      : {mae:.4f}  (avg error in net margin prediction)")

# Coefficients — which feature matters most
coef_df = pd.DataFrame({
    "Feature":     LR_FEATURES,
    "Coefficient": lr_model.coef_,
}).sort_values("Coefficient", key=abs, ascending=False)

print(f"\nFeature Coefficients (larger abs = more impact on Net Margin):")
print(coef_df.to_string(index=False))

# Plot: coefficient bar chart
fig, ax = plt.subplots(figsize=(9, 5))
colors = ["#2ecc71" if c > 0 else "#e74c3c" for c in coef_df["Coefficient"]]
ax.barh(coef_df["Feature"], coef_df["Coefficient"], color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Coefficient (impact on Net Margin)")
ax.set_title(f"Linear Regression: What Drives Amex Net Margin?\n(R² = {r2:.3f})")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(OUT + "chart_lr_coefficients.png", dpi=150)
print(f"\nChart saved → chart_lr_coefficients.png")


# ════════════════════════════════════════════════════════════════════════════
# MODEL 2 — DECISION TREE: What predicts Net Income?
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MODEL 2: DECISION TREE → predicting Net Income")
print("=" * 60)

DT_FEATURES = [
    "Total Revenue",
    "Total Assets",
    "Long Term Debt",
    "Stockholders Equity",
    "Interest Income",
    "Tax Provision",
    "Debt to Equity",
    "Equity Ratio",
    "Asset Efficiency",
    "ROA",
]
DT_TARGET = "Net Income"

dt_df = df[DT_FEATURES + [DT_TARGET]].dropna()
print(f"Rows with complete data for decision tree: {len(dt_df)}")

X_dt = dt_df[DT_FEATURES]
y_dt = dt_df[DT_TARGET]

X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X_dt, y_dt, test_size=0.2, random_state=42
)

dt_model = DecisionTreeRegressor(max_depth=4, random_state=42)
dt_model.fit(X_train2, y_train2)
y_pred_dt = dt_model.predict(X_test2)

r2_dt  = r2_score(y_test2, y_pred_dt)
mae_dt = mean_absolute_error(y_test2, y_pred_dt)

print(f"\nModel Performance:")
print(f"  R² Score : {r2_dt:.3f}")
print(f"  MAE      : {mae_dt:.3f}B  (avg error in Net Income prediction)")

# Feature importance
imp_df = pd.DataFrame({
    "Feature":    DT_FEATURES,
    "Importance": dt_model.feature_importances_,
}).sort_values("Importance", ascending=False)

print(f"\nFeature Importance (what the tree uses most to predict Net Income):")
print(imp_df.to_string(index=False))

# Plot: feature importance
fig2, ax2 = plt.subplots(figsize=(9, 5))
ax2.barh(imp_df["Feature"], imp_df["Importance"], color="#3498db")
ax2.set_xlabel("Importance Score")
ax2.set_title(f"Decision Tree: What Predicts Amex Net Income?\n(R² = {r2_dt:.3f})")
ax2.invert_yaxis()
plt.tight_layout()
plt.savefig(OUT + "chart_dt_importance.png", dpi=150)
print(f"\nChart saved → chart_dt_importance.png")

# Print tree rules (simplified)
print("\nDecision Tree Rules (top levels):")
tree_rules = export_text(dt_model, feature_names=DT_FEATURES, max_depth=3)
print(tree_rules)


# ════════════════════════════════════════════════════════════════════════════
# BONUS — Actual vs Predicted chart for both models
# ════════════════════════════════════════════════════════════════════════════
fig3, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5))

ax3.scatter(y_test, y_pred_lr, alpha=0.7, color="#2ecc71")
ax3.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--")
ax3.set_xlabel("Actual Net Margin")
ax3.set_ylabel("Predicted Net Margin")
ax3.set_title(f"Linear Regression\nActual vs Predicted  (R²={r2:.3f})")

ax4.scatter(y_test2, y_pred_dt, alpha=0.7, color="#3498db")
ax4.plot([y_test2.min(), y_test2.max()], [y_test2.min(), y_test2.max()], "r--")
ax4.set_xlabel("Actual Net Income ($B)")
ax4.set_ylabel("Predicted Net Income ($B)")
ax4.set_title(f"Decision Tree\nActual vs Predicted  (R²={r2_dt:.3f})")

plt.tight_layout()
plt.savefig(OUT + "chart_actual_vs_predicted.png", dpi=150)
print(f"\nChart saved → chart_actual_vs_predicted.png")

print("\n=== STEP 3 COMPLETE ===")
print("3 charts saved to amex_project folder")
print("Next: 4_arima_forecast.R  (your turn in R!)")
