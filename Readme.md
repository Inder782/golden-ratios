# Golden Ratios — Stock Analysis Dashboard

> A data-driven Streamlit application for pairwise stock comparison using quantitative finance metrics.

---

## Live Demo

🔗 [Launch App](https://your-app-link.streamlit.app)

---

## Overview

**Golden Ratios** is an interactive financial analytics dashboard built with Python and Streamlit. It lets you compare any three stocks side-by-side using industry-standard risk-adjusted return metrics — no spreadsheets, no manual calculations.

Pick your stocks, choose a time period or custom date range, and instantly get a full quantitative breakdown across all three pairs.

---

## UI Preview

![App Screenshot](assets\ui.png)

---

## What It Computes

For each pairwise combination of the three stocks (A vs B, B vs C, A vs C):

| Metric                        | Description                                            |
| ----------------------------- | ------------------------------------------------------ |
| **Beta**                      | Sensitivity of one stock's returns relative to another |
| **Alpha**                     | Excess return not explained by market movement         |
| **Jensen's Alpha**            | Risk-adjusted excess return vs. expected return        |
| **Sharpe Ratio**              | Return per unit of total risk (volatility)             |
| **Treynor Ratio**             | Return per unit of systematic risk (beta)              |
| **Correlation**               | Degree of co-movement between the two stocks           |
| **Daily & Yearly Volatility** | Log-return based volatility estimates                  |

---

## Tech Stack

| Layer                    | Tools                     |
| ------------------------ | ------------------------- |
| **Frontend**             | Streamlit                 |
| **Data Fetching**        | yfinance                  |
| **Data Processing**      | pandas, numpy             |
| **Statistical Analysis** | scipy (linear regression) |
| **Language**             | Python 3.x                |

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/Inder782/golden-ratios
cd golden-ratios

# Create and activate virtual environment
python -m venv env
.\env\Scripts\activate       # Windows
source env/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```
