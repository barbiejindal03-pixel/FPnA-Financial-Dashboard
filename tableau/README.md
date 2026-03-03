# Tableau Dashboard Documentation

This folder contains the Tableau workbook used to visualize Net Margin performance across fiscal years.

## File Included

### amex_financial_year_evaluation.twbx

This packaged workbook contains a structured financial visualization focused on margin evaluation.

The workbook is self-contained and can be opened directly in Tableau Desktop.

## Dashboard Scope

The Tableau file evaluates financial performance through Net Margin trend analysis for fiscal years 2023–2025.

The visualization uses:

- Year as the primary time dimension
- Net Margin % as the key performance indicator
- Line chart format for trend evaluation
- Year-based filtering

## Calculation Implemented

The only calculated field used in this workbook is:

**Net Margin % = SUM([Net Income]) / SUM([Revenue])**

This calculation aggregates financial data by year to determine profitability efficiency.

No additional derived metrics or layered calculations are implemented within Tableau.

_NOTE: All other financial preparation and structuring was handled in the Excel modeling layer_

## Analytical Interpretation

The Net Margin trend reveals:

- Improvement from 2023 to 2024
- Slight compression in 2025

This indicates that while revenue continued to grow, profitability efficiency declined marginally in the most recent fiscal period.

The trend suggests increased cost pressure relative to revenue expansion.


## Modeling Structure

The workflow followed a structured linear flow:

Source Data → Excel Model → Tableau Visualization

Tableau is used strictly as the visualization layer.

Financial logic remains centralized within the structured dataset.


## Design Principle

The dashboard emphasizes:

- Clarity over complexity
- Clean aggregation logic
- Transparent calculation methodology
- Focused KPI analysis

_This approach ensures the visualization reflects accurate financial logic without circular dependencies or hard-coded metrics_
