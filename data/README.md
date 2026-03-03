# Data Documentation

This folder contains the source financial data used to build the FP&A Financial Performance Dashboard.

The dataset supports a structured financial performance analysis covering fiscal years 2023–2025.

## Files in This Folder

### 1. financial_data_Amex.xlsx

This Excel file contains the structured financial dataset used for modeling and dashboard development.

It includes base financial statement metrics such as:

- Revenue  
- Total Expenses  
- Pretax Income  
- Net Income  
- Provision Data  

Derived financial metrics (margins, growth rates, leverage) were calculated using this file as the base modeling layer.

The structure follows a standardized tabular format organized by fiscal year.

### 2. amex_2025_source.pdf

This PDF represents the original financial source reference used to construct the dataset.

It serves as a documentation and validation layer to ensure financial accuracy and transparency.

All modeled values in the Excel file were reconciled against this source.

## Financial Modeling Structure

The dataset supports a layered financial modeling approach:

### Base Metrics Layer
Core financial values organized by year.

### Derived KPI Layer
The following metrics were calculated from base values:

- Net Margin  
- Pretax Margin  
- Expense Ratio  
- Provision Ratio  
- Year-over-Year Growth  
- Operating Leverage  

All ratios were computed programmatically using financial logic rather than hard-coded values.

## Data Flow Design

The financial workflow followed a linear structure:

Source PDF → Excel Model → KPI Calculations → Tableau Dashboard

This unidirectional flow:

- Prevents circular references  
- Maintains audit integrity  
- Ensures reproducibility  
- Mirrors simplified FP&A modeling practices  

## Integrity Note

The Excel file represents a structured modeling layer derived from publicly available financial disclosures.

All dashboard outputs can be independently validated against the source PDF.
