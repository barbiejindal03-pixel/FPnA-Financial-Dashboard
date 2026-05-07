"""
American Express FP&A Intelligence Dashboard
Streamlit + Plotly — Amex brand colours
Run: streamlit run 5_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AmEx FP&A Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# ── Amex Brand Colours ───────────────────────────────────────────────────────
NAVY   = "#00175A"   # primary Amex navy
BLUE   = "#006FCF"   # Amex blue
GOLD   = "#C9A84C"   # Amex card gold
LGOLD  = "#F0D060"   # light gold for highlights
WHITE  = "#FFFFFF"
LGRAY  = "#F4F6FB"
DGRAY  = "#2C2C2C"
GREEN  = "#00A651"
RED    = "#D0021B"

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── background ── */
  .stApp {{ background-color: {LGRAY}; }}

  /* ── sidebar ── */
  [data-testid="stSidebar"] {{
      background: linear-gradient(180deg, {NAVY} 0%, #001040 100%);
  }}
  [data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stSlider label {{ color: {LGOLD} !important; font-weight:600; }}

  /* ── top header bar ── */
  .amex-header {{
      background: linear-gradient(135deg, {NAVY} 0%, {BLUE} 60%, {GOLD} 100%);
      padding: 28px 36px 20px 36px;
      border-radius: 16px;
      margin-bottom: 24px;
  }}
  .amex-header h1 {{ color:{WHITE}; font-size:2.2rem; font-weight:800;
                     letter-spacing:0.02em; margin:0; }}
  .amex-header p  {{ color:{LGOLD}; margin:4px 0 0 0; font-size:1rem; }}

  /* ── KPI cards ── */
  .kpi-card {{
      background: {WHITE};
      border-radius: 14px;
      padding: 20px 24px;
      border-left: 5px solid {GOLD};
      box-shadow: 0 2px 12px rgba(0,23,90,0.10);
  }}
  .kpi-label {{ color:{NAVY}; font-size:0.78rem; font-weight:700;
                text-transform:uppercase; letter-spacing:0.08em; }}
  .kpi-value {{ color:{NAVY}; font-size:2rem; font-weight:800; margin:4px 0 2px 0; }}
  .kpi-delta-pos {{ color:{GREEN}; font-size:0.85rem; font-weight:600; }}
  .kpi-delta-neg {{ color:{RED};   font-size:0.85rem; font-weight:600; }}

  /* ── section headers ── */
  .section-title {{
      color:{NAVY}; font-size:1.15rem; font-weight:800;
      border-bottom: 3px solid {GOLD}; padding-bottom:6px;
      margin: 28px 0 16px 0; letter-spacing:0.03em;
  }}

  /* ── insight box ── */
  .insight-box {{
      background: linear-gradient(135deg, {NAVY}08, {BLUE}12);
      border: 1px solid {BLUE}40;
      border-radius: 10px;
      padding: 14px 18px;
      color: {NAVY};
      font-size: 0.88rem;
      line-height: 1.6;
  }}

  /* ── hide streamlit default chrome ── */
  #MainMenu, footer {{ visibility: hidden; }}
  /* keep sidebar toggle always visible */
  [data-testid="collapsedControl"] {{ display: block !important; visibility: visible !important; }}
  .block-container {{ padding-top: 1rem; }}
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────────────
import os
BASE = os.path.join(os.path.dirname(__file__), "data/processed/")

@st.cache_data
def load_data():
    feat = pd.read_csv(BASE + "amex_features.csv")
    feat["Quarter"] = pd.to_datetime(feat["Quarter"])
    feat = feat.sort_values("Quarter").reset_index(drop=True)

    try:
        fc = pd.read_csv(BASE + "forecast_results.csv")
        fc["Quarter"] = pd.to_datetime(fc["Quarter"])
    except Exception:
        fc = pd.DataFrame()

    try:
        comp = pd.read_csv(BASE + "amex_annual.csv")
        comp["Year"] = pd.to_datetime(comp["Year"])
    except Exception:
        comp = pd.DataFrame()

    return feat, fc, comp

df, fc_df, comp_df = load_data()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:10px 0 20px 0;'>
      <div style='font-size:2.8rem;'>💳</div>
      <div style='font-size:1.1rem; font-weight:800; color:#F0D060;
                  letter-spacing:0.1em;'>AMERICAN EXPRESS</div>
      <div style='font-size:0.72rem; color:#aac4ff; margin-top:2px;'>
           FP&A Intelligence Platform</div>
    </div>
    <hr style='border-color:#ffffff30; margin:0 0 20px 0;'>
    """, unsafe_allow_html=True)

    section = st.selectbox("Navigate", [
        "📊 Executive Overview",
        "📈 Revenue & Income Trends",
        "🤖 ML Model Insights",
        "🔮 ARIMA 2026 Forecast",
        "🏦 Competitor Benchmarking",
        "🎛️ Scenario Simulator",
    ])

    st.markdown("<hr style='border-color:#ffffff20;'>", unsafe_allow_html=True)

    # Date filter
    years = sorted(df["Quarter"].dt.year.unique())
    yr_range = st.slider("Year Range", int(min(years)), int(max(years)),
                         (int(min(years)), int(max(years))))
    df_filtered = df[df["Quarter"].dt.year.between(*yr_range)]

    st.markdown(f"""
    <div style='margin-top:40px; color:#aac4ff; font-size:0.72rem; text-align:center;'>
      Data: SEC EDGAR + yfinance<br>
      {len(df_filtered)} quarters selected
    </div>
    """, unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="amex-header">
  <h1>💳 American Express — FP&A Intelligence</h1>
  <p>Machine Learning · Time Series Forecasting · Financial Analytics &nbsp;|&nbsp;
     2016 – 2026 &nbsp;·&nbsp; 65 Quarters &nbsp;·&nbsp; SEC EDGAR</p>
</div>
""", unsafe_allow_html=True)


# ── KPI Cards (always visible) ───────────────────────────────────────────────
latest = df_filtered.dropna(subset=["Net Income"]).iloc[-1]
prev   = df_filtered.dropna(subset=["Net Income"]).iloc[-5] if len(df_filtered) > 5 else latest

def delta_html(val, prev_val, fmt=".1%"):
    if prev_val == 0:
        return ""
    d = (val - prev_val) / abs(prev_val)
    arrow = "▲" if d >= 0 else "▼"
    cls   = "kpi-delta-pos" if d >= 0 else "kpi-delta-neg"
    return f'<span class="{cls}">{arrow} {abs(d):{fmt}} YoY</span>'

rev_latest = df_filtered.dropna(subset=["Total Revenue"]).iloc[-1]["Total Revenue"]
rev_prev   = df_filtered.dropna(subset=["Total Revenue"]).iloc[-5]["Total Revenue"] if len(df_filtered.dropna(subset=["Total Revenue"])) > 5 else rev_latest

k1, k2, k3, k4, k5 = st.columns(5)
cards = [
    (k1, "Total Revenue",     f"${rev_latest:.2f}B",      delta_html(rev_latest, rev_prev, ".1%")),
    (k2, "Net Income",        f"${latest['Net Income']:.2f}B", delta_html(latest["Net Income"], prev["Net Income"])),
    (k3, "Net Margin",        f"{latest['Net Margin']*100:.1f}%" if pd.notna(latest.get('Net Margin')) else "N/A", ""),
    (k4, "Return on Equity",  f"{latest['ROE']*100:.1f}%" if pd.notna(latest.get('ROE')) else "N/A", ""),
    (k5, "Debt / Equity",     f"{latest['Debt to Equity']:.2f}x" if pd.notna(latest.get('Debt to Equity')) else "N/A", ""),
]
for col, label, value, delta in cards:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — EXECUTIVE OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
if section == "📊 Executive Overview":
    st.markdown('<div class="section-title">FINANCIAL PERFORMANCE OVERVIEW</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    # Revenue + Net Income dual-axis
    with col_l:
        # Inner join so Revenue bars and Net Income line share exact same quarters
        rev_d = df_filtered.dropna(subset=["Total Revenue"])[["Quarter","Total Revenue"]].copy()
        ni_d  = df_filtered.dropna(subset=["Net Income"])[["Quarter","Net Income"]].copy()
        both  = rev_d.merge(ni_d, on="Quarter")
        both["Quarter_str"] = both["Quarter"].dt.year.astype(str) + '-Q' + both["Quarter"].dt.quarter.astype(str)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=both["Quarter_str"], y=both["Total Revenue"],
            name="Revenue ($B)", marker_color=BLUE, opacity=0.85,
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=both["Quarter_str"], y=both["Net Income"],
            name="Net Income ($B)", line=dict(color=GOLD, width=3),
            mode="lines+markers", marker=dict(size=5),
        ), secondary_y=True)
        fig.update_layout(
            title=dict(text="Revenue & Net Income", font=dict(color=NAVY, size=14)),
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            legend=dict(orientation="h", y=-0.18),
            height=320,
        )
        fig.update_yaxes(title_text="Revenue ($B)", secondary_y=False, gridcolor="#eee")
        fig.update_yaxes(title_text="Net Income ($B)", secondary_y=True, gridcolor="#eee")
        st.plotly_chart(fig, use_container_width=True)

    # Margin trend
    with col_r:
        mg_d = df_filtered.dropna(subset=["Net Margin"])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=mg_d["Quarter"], y=mg_d["Net Margin"] * 100,
            fill="tozeroy", fillcolor=f"rgba(0,111,207,0.12)",
            line=dict(color=BLUE, width=2.5),
            name="Net Margin %",
        ))
        fig2.add_hline(y=mg_d["Net Margin"].mean()*100,
                       line_dash="dash", line_color=GOLD,
                       annotation_text=f"Avg {mg_d['Net Margin'].mean()*100:.1f}%",
                       annotation_font_color=GOLD)
        fig2.update_layout(
            title=dict(text="Net Margin Trend (%)", font=dict(color=NAVY, size=14)),
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            yaxis=dict(ticksuffix="%", gridcolor="#eee"),
            height=320, showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ROE + Debt/Equity
    col3, col4 = st.columns(2)
    with col3:
        roe_d = df_filtered.dropna(subset=["ROE"])
        fig3 = go.Figure(go.Scatter(
            x=roe_d["Quarter"], y=roe_d["ROE"] * 100,
            line=dict(color=GOLD, width=2.5),
            fill="tozeroy", fillcolor="rgba(201,168,76,0.12)",
        ))
        fig3.update_layout(
            title=dict(text="Return on Equity (%)", font=dict(color=NAVY, size=14)),
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            yaxis=dict(ticksuffix="%", gridcolor="#eee"),
            height=280, showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        de_d = df_filtered.dropna(subset=["Debt to Equity"]).copy()
        de_d["Quarter_str"] = de_d["Quarter"].dt.year.astype(str) + '-Q' + de_d["Quarter"].dt.quarter.astype(str)
        fig4 = go.Figure(go.Bar(
            x=de_d["Quarter_str"], y=de_d["Debt to Equity"],
            marker=dict(
                color=de_d["Debt to Equity"],
                colorscale=[[0, BLUE], [0.5, GOLD], [1, RED]],
                showscale=False,
            )
        ))
        fig4.update_layout(
            title=dict(text="Debt-to-Equity Ratio", font=dict(color=NAVY, size=14)),
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            yaxis=dict(gridcolor="#eee"),
            height=280, showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Insight box
    avg_margin = df_filtered["Net Margin"].mean()
    avg_roe    = df_filtered["ROE"].mean()
    st.markdown(f"""
    <div class="insight-box">
      <b>📌 Key Insights:</b><br>
      • Amex maintained an average net margin of <b>{avg_margin*100:.1f}%</b> across the selected period —
        reflecting disciplined cost management in a high-interest-rate environment.<br>
      • Return on Equity averaged <b>{avg_roe*100:.1f}%</b> per quarter, signalling strong shareholder value generation.<br>
      • Debt-to-Equity peaked during COVID (2020) as Amex drew on credit facilities, then normalised post-2022.
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — REVENUE & INCOME TRENDS
# ════════════════════════════════════════════════════════════════════════════
elif section == "📈 Revenue & Income Trends":
    st.markdown('<div class="section-title">REVENUE & INCOME DEEP DIVE</div>', unsafe_allow_html=True)

    metric = st.radio("Select Metric", ["Total Revenue", "Net Income", "Interest Income", "Total Assets"],
                      horizontal=True)

    d = df_filtered.dropna(subset=[metric])
    if d.empty:
        st.warning(f"No data for {metric} in selected range.")
    else:
        # Rolling average
        d = d.copy()
        d["Rolling_4Q"] = d[metric].rolling(4).mean()

        d["Quarter_str"] = d["Quarter"].dt.year.astype(str) + '-Q' + d["Quarter"].dt.quarter.astype(str)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=d["Quarter_str"], y=d[metric],
            name=metric, marker_color=BLUE, opacity=0.7,
        ))
        fig.add_trace(go.Scatter(
            x=d["Quarter_str"], y=d["Rolling_4Q"],
            name="4Q Rolling Avg",
            line=dict(color=GOLD, width=3, dash="dot"),
        ))
        fig.update_layout(
            title=dict(text=f"{metric} — Quarterly with 4Q Trend",
                       font=dict(color=NAVY, size=15)),
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            yaxis=dict(title="$B", gridcolor="#eee"),
            legend=dict(orientation="h", y=-0.15),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    # YoY growth
    col_a, col_b = st.columns(2)
    with col_a:
        yoy_d = df_filtered.dropna(subset=["Revenue YoY Growth"]).copy()
        yoy_d["Quarter_str"] = yoy_d["Quarter"].dt.year.astype(str) + '-Q' + yoy_d["Quarter"].dt.quarter.astype(str)
        fig5 = go.Figure(go.Bar(
            x=yoy_d["Quarter_str"],
            y=yoy_d["Revenue YoY Growth"] * 100,
            marker_color=[GREEN if v >= 0 else RED for v in yoy_d["Revenue YoY Growth"]],
        ))
        fig5.update_layout(
            title=dict(text="Revenue YoY Growth (%)", font=dict(color=NAVY, size=14)),
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            yaxis=dict(ticksuffix="%", gridcolor="#eee"),
            height=300,
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_b:
        ni_yoy = df_filtered.dropna(subset=["Net Income YoY Growth"]).copy()
        ni_yoy["Quarter_str"] = ni_yoy["Quarter"].dt.year.astype(str) + '-Q' + ni_yoy["Quarter"].dt.quarter.astype(str)
        fig6 = go.Figure(go.Bar(
            x=ni_yoy["Quarter_str"],
            y=ni_yoy["Net Income YoY Growth"] * 100,
            marker_color=[GREEN if v >= 0 else RED for v in ni_yoy["Net Income YoY Growth"]],
        ))
        fig6.update_layout(
            title=dict(text="Net Income YoY Growth (%)", font=dict(color=NAVY, size=14)),
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            yaxis=dict(ticksuffix="%", gridcolor="#eee"),
            height=300,
        )
        st.plotly_chart(fig6, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — ML MODEL INSIGHTS
# ════════════════════════════════════════════════════════════════════════════
elif section == "🤖 ML Model Insights":
    st.markdown('<div class="section-title">MACHINE LEARNING MODEL RESULTS</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📐 Linear Regression — Net Margin", "🌳 Decision Tree — Net Income"])

    with tab1:
        LR_FEATURES = ["Interest Coverage", "Asset Efficiency", "Debt to Equity",
                       "Equity Ratio", "ROA", "Revenue YoY Growth", "Tax Rate"]
        lr_df = df[LR_FEATURES + ["Net Margin"]].dropna()

        if len(lr_df) < 8:
            st.warning("Not enough complete rows for regression.")
        else:
            X = StandardScaler().fit_transform(lr_df[LR_FEATURES])
            y = lr_df["Net Margin"]
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression().fit(X_tr, y_tr)
            r2 = r2_score(y_te, model.predict(X_te))

            coef_df = pd.DataFrame({"Feature": LR_FEATURES,
                                    "Coefficient": model.coef_}
                                   ).sort_values("Coefficient", key=abs, ascending=True)

            col_m, col_c = st.columns([1, 2])
            with col_m:
                st.markdown(f"""
                <div class="kpi-card" style="margin-top:8px;">
                  <div class="kpi-label">Model R² Score</div>
                  <div class="kpi-value" style="color:{BLUE};">{r2:.3f}</div>
                  <span class="kpi-delta-pos">{'Excellent' if r2>0.9 else 'Good' if r2>0.7 else 'Fair'} Fit</span>
                </div>
                <br>
                <div class="insight-box">
                  <b>What this means:</b><br>
                  The model explains <b>{r2*100:.1f}%</b> of the variation
                  in Amex's net margin using 7 financial ratios.
                  ROA is by far the strongest predictor.
                </div>
                """, unsafe_allow_html=True)

            with col_c:
                fig7 = go.Figure(go.Bar(
                    x=coef_df["Coefficient"],
                    y=coef_df["Feature"],
                    orientation="h",
                    marker_color=[BLUE if v > 0 else RED for v in coef_df["Coefficient"]],
                    text=[f"{v:+.4f}" for v in coef_df["Coefficient"]],
                    textposition="outside",
                ))
                fig7.update_layout(
                    title="Feature Coefficients — Impact on Net Margin",
                    plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                    xaxis=dict(gridcolor="#eee"),
                    height=340,
                )
                st.plotly_chart(fig7, use_container_width=True)

            # Actual vs predicted
            y_pred_full = model.predict(X)
            fig8 = go.Figure()
            fig8.add_trace(go.Scatter(
                x=lr_df.index, y=y.values * 100,
                name="Actual", line=dict(color=NAVY, width=2),
            ))
            fig8.add_trace(go.Scatter(
                x=lr_df.index, y=y_pred_full * 100,
                name="Predicted", line=dict(color=GOLD, width=2, dash="dot"),
            ))
            fig8.update_layout(
                title="Actual vs Predicted Net Margin (%)",
                plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                yaxis=dict(ticksuffix="%", gridcolor="#eee"),
                height=280,
            )
            st.plotly_chart(fig8, use_container_width=True)

    with tab2:
        DT_FEATURES = ["Total Revenue", "Total Assets", "Long Term Debt",
                       "Stockholders Equity", "Interest Income", "Tax Provision",
                       "Debt to Equity", "Equity Ratio", "Asset Efficiency", "ROA"]
        dt_df2 = df[DT_FEATURES + ["Net Income"]].dropna()

        if len(dt_df2) < 8:
            st.warning("Not enough complete rows for decision tree.")
        else:
            X2 = dt_df2[DT_FEATURES]
            y2 = dt_df2["Net Income"]
            X_tr2, X_te2, y_tr2, y_te2 = train_test_split(X2, y2, test_size=0.2, random_state=42)
            dt = DecisionTreeRegressor(max_depth=4, random_state=42).fit(X_tr2, y_tr2)
            r2_dt = r2_score(y_te2, dt.predict(X_te2))

            imp_df = pd.DataFrame({"Feature": DT_FEATURES,
                                   "Importance": dt.feature_importances_}
                                  ).sort_values("Importance", ascending=True)
            imp_df = imp_df[imp_df["Importance"] > 0]

            col_dt1, col_dt2 = st.columns([1, 2])
            with col_dt1:
                st.markdown(f"""
                <div class="kpi-card" style="margin-top:8px;">
                  <div class="kpi-label">Model R² Score</div>
                  <div class="kpi-value" style="color:{BLUE};">{r2_dt:.3f}</div>
                  <span class="kpi-delta-pos">{'Excellent' if r2_dt>0.9 else 'Good' if r2_dt>0.7 else 'Fair'} Fit</span>
                </div>
                <br>
                <div class="insight-box">
                  <b>Top predictor:</b><br>
                  <b>Debt-to-Equity</b> drives 57% of Net Income predictions.
                  When D/E &lt; 1.92 and assets &gt; $271B, Net Income ≈ $2.99B/quarter.
                </div>
                """, unsafe_allow_html=True)

            with col_dt2:
                fig9 = go.Figure(go.Bar(
                    x=imp_df["Importance"] * 100,
                    y=imp_df["Feature"],
                    orientation="h",
                    marker=dict(
                        color=imp_df["Importance"],
                        colorscale=[[0, BLUE], [0.5, GOLD], [1, NAVY]],
                    ),
                    text=[f"{v*100:.1f}%" for v in imp_df["Importance"]],
                    textposition="outside",
                ))
                fig9.update_layout(
                    title="Feature Importance — Predicting Net Income",
                    plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                    xaxis=dict(ticksuffix="%", gridcolor="#eee"),
                    height=340,
                )
                st.plotly_chart(fig9, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ARIMA FORECAST
# ════════════════════════════════════════════════════════════════════════════
elif section == "🔮 ARIMA 2026 Forecast":
    st.markdown('<div class="section-title">ARIMA TIME SERIES FORECAST — 2026</div>', unsafe_allow_html=True)

    if fc_df.empty:
        st.error("forecast_results.csv not found. Run 4_arima_forecast.R first.")
    else:
        for metric_name, colour in [("Total Revenue", BLUE), ("Net Income", GOLD)]:
            fc_m = fc_df[fc_df["Metric"] == metric_name]
            hist = df.dropna(subset=[metric_name])

            fig_fc = go.Figure()

            # Historical line
            fig_fc.add_trace(go.Scatter(
                x=hist["Quarter"], y=hist[metric_name],
                name="Historical", line=dict(color=NAVY, width=2.5),
            ))

            # 95% CI band
            fig_fc.add_trace(go.Scatter(
                x=pd.concat([fc_m["Quarter"], fc_m["Quarter"][::-1]]),
                y=pd.concat([fc_m["Upper_95"], fc_m["Lower_95"][::-1]]),
                fill="toself",
                fillcolor=f"rgba(201,168,76,0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                name="95% CI",
            ))

            # 80% CI band
            fig_fc.add_trace(go.Scatter(
                x=pd.concat([fc_m["Quarter"], fc_m["Quarter"][::-1]]),
                y=pd.concat([fc_m["Upper_80"], fc_m["Lower_80"][::-1]]),
                fill="toself",
                fillcolor=f"rgba(201,168,76,0.30)",
                line=dict(color="rgba(0,0,0,0)"),
                name="80% CI",
            ))

            # Forecast line
            fig_fc.add_trace(go.Scatter(
                x=fc_m["Quarter"], y=fc_m["Forecast"],
                name="Forecast", line=dict(color=colour, width=3, dash="dash"),
                mode="lines+markers", marker=dict(size=8, symbol="diamond"),
            ))

            vline_x = hist["Quarter"].max().timestamp() * 1000
            fig_fc.add_vline(x=vline_x, line_dash="dot",
                             line_color=DGRAY, line_width=1,
                             annotation_text="Forecast start",
                             annotation_font_color=DGRAY)

            fig_fc.update_layout(
                title=dict(text=f"ARIMA Forecast: {metric_name} ($B)",
                           font=dict(color=NAVY, size=15)),
                plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                yaxis=dict(title="$B", gridcolor="#eee"),
                legend=dict(orientation="h", y=-0.18),
                height=350,
            )
            st.plotly_chart(fig_fc, use_container_width=True)

        # Summary table
        st.markdown('<div class="section-title">2026 QUARTERLY PROJECTIONS</div>', unsafe_allow_html=True)
        rev_fc = fc_df[fc_df["Metric"] == "Total Revenue"][["Quarter","Forecast","Lower_95","Upper_95"]].copy()
        ni_fc  = fc_df[fc_df["Metric"] == "Net Income"][["Forecast","Lower_95","Upper_95"]].copy()
        rev_fc.columns = ["Quarter","Revenue Fcst ($B)","Rev Lower","Rev Upper"]
        ni_fc.columns  = ["NI Fcst ($B)","NI Lower","NI Upper"]
        summary = pd.concat([rev_fc.reset_index(drop=True), ni_fc.reset_index(drop=True)], axis=1)
        summary["Quarter"] = summary["Quarter"].dt.year.astype(str) + ' Q' + summary["Quarter"].dt.quarter.astype(str)
        for col in ["Revenue Fcst ($B)","Rev Lower","Rev Upper","NI Fcst ($B)","NI Lower","NI Upper"]:
            summary[col] = summary[col].round(2)
        st.dataframe(summary, use_container_width=True, hide_index=True)

        annual_rev = fc_df[fc_df["Metric"]=="Total Revenue"]["Forecast"].sum()
        annual_ni  = fc_df[fc_df["Metric"]=="Net Income"]["Forecast"].sum()
        st.markdown(f"""
        <div class="insight-box" style="margin-top:12px;">
          <b>📌 2026 Full-Year Projection:</b><br>
          • <b>Revenue: ${annual_rev:.2f}B</b> &nbsp;|&nbsp;
            <b>Net Income: ${annual_ni:.2f}B</b> &nbsp;|&nbsp;
            <b>Implied Net Margin: {annual_ni/annual_rev*100:.1f}%</b><br>
          • ARIMA(0,1,0) with drift for Revenue: steady growth of ~$0.31B/quarter.<br>
          • ARIMA(0,1,1) for Net Income: moving-average smoothing captures earnings volatility.
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — COMPETITOR BENCHMARKING
# ════════════════════════════════════════════════════════════════════════════
elif section == "🏦 Competitor Benchmarking":
    st.markdown('<div class="section-title">COMPETITOR BENCHMARKING</div>', unsafe_allow_html=True)

    if comp_df.empty:
        st.warning("amex_annual.csv not found.")
    else:
        comp_df["Net Margin"] = comp_df["Net Income"] / comp_df["Total Revenue"]
        latest_comp = comp_df.groupby("Ticker").last().reset_index()

        col_cb1, col_cb2 = st.columns(2)
        with col_cb1:
            fig_cb1 = go.Figure(go.Bar(
                x=latest_comp["Ticker"], y=latest_comp["Total Revenue"],
                marker_color=[GOLD if t == "AXP" else BLUE for t in latest_comp["Ticker"]],
                text=latest_comp["Total Revenue"].round(1),
                textposition="outside",
            ))
            fig_cb1.update_layout(
                title="Annual Revenue ($B) — Latest Year",
                plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                yaxis=dict(gridcolor="#eee"), height=320,
            )
            st.plotly_chart(fig_cb1, use_container_width=True)

        with col_cb2:
            fig_cb2 = go.Figure(go.Bar(
                x=latest_comp["Ticker"], y=latest_comp["Net Margin"] * 100,
                marker_color=[GOLD if t == "AXP" else BLUE for t in latest_comp["Ticker"]],
                text=[f"{v:.1f}%" for v in latest_comp["Net Margin"]*100],
                textposition="outside",
            ))
            fig_cb2.update_layout(
                title="Net Margin (%) — Latest Year",
                plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                yaxis=dict(ticksuffix="%", gridcolor="#eee"), height=320,
            )
            st.plotly_chart(fig_cb2, use_container_width=True)

        # Revenue over time multi-line
        rev_time = comp_df.dropna(subset=["Total Revenue"])
        comp_colours = {"AXP": GOLD, "V": BLUE, "MA": NAVY, "COF": "#8B5CF6"}
        fig_cb3 = go.Figure()
        for ticker, grp in rev_time.groupby("Ticker"):
            fig_cb3.add_trace(go.Scatter(
                x=grp["Year"], y=grp["Total Revenue"],
                name=ticker, line=dict(color=comp_colours.get(ticker, BLUE),
                                       width=3 if ticker=="AXP" else 1.5),
            ))
        fig_cb3.update_layout(
            title="Revenue Trend: AXP vs Peers ($B)",
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            yaxis=dict(gridcolor="#eee"), height=320,
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig_cb3, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6 — SCENARIO SIMULATOR
# ════════════════════════════════════════════════════════════════════════════
elif section == "🎛️ Scenario Simulator":
    st.markdown('<div class="section-title">LIVE SCENARIO SIMULATOR</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
      Move the sliders below to change financial assumptions.
      The ML model re-predicts Net Income <b>in real time</b>.
    </div><br>
    """, unsafe_allow_html=True)

    # Train decision tree on full data
    DT_FEATURES = ["Total Assets", "Long Term Debt", "Stockholders Equity",
                   "Interest Income", "Tax Provision", "Debt to Equity",
                   "Equity Ratio", "Asset Efficiency", "ROA"]
    dt_df3 = df[DT_FEATURES + ["Net Income"]].dropna()
    dt_sim = DecisionTreeRegressor(max_depth=4, random_state=42)
    dt_sim.fit(dt_df3[DT_FEATURES], dt_df3["Net Income"])

    # Use latest quarter as defaults
    latest_full = dt_df3.iloc[-1]

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        total_assets = st.slider("Total Assets ($B)",
                                 100.0, 400.0, float(round(latest_full["Total Assets"], 1)), 5.0)
        long_term_debt = st.slider("Long Term Debt ($B)",
                                   10.0, 100.0, float(round(latest_full["Long Term Debt"], 1)), 1.0)
        equity = st.slider("Stockholders Equity ($B)",
                            10.0, 60.0, float(round(latest_full["Stockholders Equity"], 1)), 0.5)
    with col_s2:
        interest_income = st.slider("Interest Income ($B)",
                                    1.0, 15.0, float(round(latest_full["Interest Income"], 2)), 0.1)
        tax_provision = st.slider("Tax Provision ($B)",
                                  0.1, 2.0, float(round(latest_full["Tax Provision"], 2)), 0.05)
    with col_s3:
        # Derived
        de  = long_term_debt / equity
        er  = equity / total_assets
        ae  = interest_income / total_assets
        roa = 0.009  # keep near historical avg

        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">Computed Ratios</div>
          <div style="margin-top:8px; font-size:0.9rem; color:{NAVY};">
            <b>Debt/Equity:</b> {de:.2f}x<br>
            <b>Equity Ratio:</b> {er:.3f}<br>
            <b>Asset Efficiency:</b> {ae:.4f}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Predict
    input_row = np.array([[total_assets, long_term_debt, equity,
                            interest_income, tax_provision,
                            de, er, ae, roa]])
    predicted_ni = dt_sim.predict(input_row)[0]
    predicted_margin = predicted_ni / (interest_income * 2.7)  # rough proxy

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2_col, r3 = st.columns(3)
    r1.markdown(f"""
    <div class="kpi-card" style="border-left-color:{BLUE};">
      <div class="kpi-label">🤖 Predicted Net Income</div>
      <div class="kpi-value" style="color:{BLUE};">${predicted_ni:.3f}B</div>
      <span class="kpi-delta-pos">Decision Tree Output</span>
    </div>""", unsafe_allow_html=True)

    r2_col.markdown(f"""
    <div class="kpi-card" style="border-left-color:{GOLD};">
      <div class="kpi-label">📊 Annualised Run Rate</div>
      <div class="kpi-value" style="color:{GOLD};">${predicted_ni*4:.2f}B</div>
      <span class="kpi-delta-pos">4 × quarterly prediction</span>
    </div>""", unsafe_allow_html=True)

    r3.markdown(f"""
    <div class="kpi-card" style="border-left-color:{NAVY};">
      <div class="kpi-label">📈 Implied Margin</div>
      <div class="kpi-value" style="color:{NAVY};">{predicted_margin*100:.1f}%</div>
      <span class="kpi-delta-pos">vs 14.7% historical avg</span>
    </div>""", unsafe_allow_html=True)

    # Sensitivity chart
    st.markdown('<div class="section-title">SENSITIVITY: Assets vs Net Income</div>', unsafe_allow_html=True)
    asset_range = np.linspace(150, 400, 40)
    ni_range = []
    for a in asset_range:
        de_  = long_term_debt / equity
        er_  = equity / a
        ae_  = interest_income / a
        row_ = np.array([[a, long_term_debt, equity, interest_income,
                          tax_provision, de_, er_, ae_, roa]])
        ni_range.append(dt_sim.predict(row_)[0])

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(
        x=asset_range, y=ni_range,
        fill="tozeroy", fillcolor="rgba(0,111,207,0.10)",
        line=dict(color=BLUE, width=2.5),
    ))
    fig_sens.add_vline(x=total_assets, line_dash="dash", line_color=GOLD,
                       annotation_text=f"Current: ${total_assets:.0f}B",
                       annotation_font_color=GOLD)
    fig_sens.update_layout(
        title="Predicted Net Income vs Total Assets (all else equal)",
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        xaxis=dict(title="Total Assets ($B)", gridcolor="#eee"),
        yaxis=dict(title="Predicted Net Income ($B)", gridcolor="#eee"),
        height=300,
    )
    st.plotly_chart(fig_sens, use_container_width=True)
