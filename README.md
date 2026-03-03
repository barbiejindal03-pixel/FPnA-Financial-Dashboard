# FPnA Financial Dashboard
Executive-level financial performance analysis evaluating revenue growth, profitability trends, and cost dynamics across fiscal years 
2023-2025 for american express. 

link: https://ir.americanexpress.com/financials/earnings-and-sec-filings/default.aspx

## Project Overview
This project analyzes financial performance using a structured Excel modeling layer and a focused Tableau visualization.

The objective is to evaluate:
- Revenue generation strength  
- Profitability efficiency  
- Expense acceleration impact  
- Net Margin trend behavior  

The analysis reflects simplified FP&A monitoring principles used in corporate finance environments.

## Business Context (2025 Focus)

#### Revenue Performance
- Revenue growth in 2025 remained strong, primarily driven by **Total Non-Interest Revenue (54,865 USD)**.

- Within this category, **Discount Revenue (37,401 USD)** was the largest contributor, indicating that transaction-based revenue streams
  remain the core driver of financial expansion.

This suggests the company’s revenue base is structurally supported by operating activity rather than one-time gains.

#### Net Margin Performance (~15%)

- Net Margin in 2025 was approximately **15%**, reflecting solid profitability relative to revenue.
However, the margin remained stable rather than expanding.
While profitability levels are healthy, they did not scale proportionally with revenue growth.

#### Net Income Growth (6.95%)
- Net Income increased by **6.95%** in 2025.
Although positive, this growth rate represents a moderation compared to prior-year expansion.

This indicates that incremental revenue is translating into earnings at a reduced efficiency rate.

#### Expense Acceleration
- Expense growth increased at a faster pace in 2025 compared to the previous year.
- The acceleration in operating costs absorbed a significant portion of revenue gains, limiting profit expansion.

**Margin expansion was constrained by accelerated expense growth.**

## Financial Interpretation

From a performance standpoint:

- Top-line growth remains strong and structurally supported.
- Core revenue drivers are stable and transaction-based.
- Profitability remains healthy at ~15% margin.
- Earnings growth is moderating due to rising cost pressure.
- Expense acceleration is reducing operating leverage efficiency.

#### Strategic Insight

2025 reflects strong revenue generation driven by non-interest income; however, accelerating expenses constrained earnings growth, resulting in stable but non-expanding margins.

If expense growth continues to outpace revenue growth, future profitability gains will depend more heavily on cost discipline than revenue acceleration.

## Technical Structure

#### Data Layer
- Source financial reference: `data/amex_2025_source.pdf`
- Structured financial dataset: `data/financial_data_Amex.xlsx`

#### Visualization Layer
- Tableau Workbook: `tableau/amex_financial_year_evaluation.twbx`

#### Key Calculation Implemented in Tableau

Net Margin % = SUM([Net Income]) / SUM([Revenue])

_**All additional structuring and preparation was performed in Excel**_


## Demonstration
A short walkthrough of the dashboard is available in:
`assets/FPnA_Financial_Performance_Walkthrough.mov`

## Repository Structure
```
FPnA-Financial-Dashboard/
│
├── assets/
│   ├── dashboard_preview.png
│   ├── FPnA_Financial_Performance_Walkthrough.mov
│   └── README.md
│
├── data/
│   ├── amex_2025_source.pdf
│   ├── financial_data_Amex.xlsx
│   └── README.md
│
├── tableau/
│   ├── amex_financial_year_evaluation.twbx
│   └── README.md
│
└── README.md
```

