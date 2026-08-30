
# Quantitative Portfolio Risk Management

A Python-based quantitative risk management system for an equity portfolio.

The project progressively builds a portfolio analytics and market risk engine, starting from historical market data and portfolio construction and extending to Historical Simulation VaR, Expected Shortfall, and EWMA volatility-scaled VaR.

---

## Project Objective

The objective of this project is to build a modular and testable quantitative portfolio risk management system capable of:

- Collecting historical market data
- Cleaning and validating financial time series
- Constructing an equity portfolio
- Calculating portfolio returns and P&L
- Measuring historical market risk
- Calculating Value at Risk (VaR)
- Calculating Expected Shortfall (ES)
- Estimating volatility using EWMA
- Scaling historical returns according to current volatility
- Comparing traditional Historical VaR with EWMA-scaled VaR
- Preparing the system for advanced volatility models and VaR backtesting

The project is designed with a modular architecture so that additional risk models such as GARCH, GJR-GARCH, and statistical backtesting can be added without restructuring the existing system.

---

# Project Pipeline

```text
Market Data
     │
     ▼
┌─────────────────────────┐
│ Phase 1                 │
│ Data Collection         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Phase 2                 │
│ Data Cleaning           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Phase 3                 │
│ Portfolio Construction  │
└────────────┬────────────┘
             │
             ▼
      Portfolio Returns
             │
             ▼
┌─────────────────────────┐
│ Phase 4                 │
│ Historical VaR + ES     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Phase 5                 │
│ EWMA Volatility Scaling │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Phase 6                 │
│ GARCH / GJR-GARCH       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Phase 7                 │
│ VaR Backtesting         │
└─────────────────────────┘
Current Project Status
Phase	Description	Status
Phase 1	Data Collection	Complete
Phase 2	Data Cleaning	Complete
Phase 3	Portfolio Construction	Complete
Phase 4	Historical VaR + ES	Complete
Phase 5	EWMA Volatility Scaling	Complete
Phase 6	GARCH / GJR-GARCH	Planned
Phase 7	VaR Backtesting	Planned
Phase 1 — Data Collection

The first phase collects historical market data required for portfolio construction and risk analysis.

Data collected
Historical equity prices
Historical returns
Market benchmark data
Sector information

The system is designed to work with multiple financial data sources. The current implementation uses downloaded historical market data and stores the raw data separately from processed data.

Raw Data
data/raw/
├── prices.csv
├── returns.csv
├── market.csv
└── sectors.csv
Phase 2 — Data Cleaning

The second phase prepares the raw financial data for quantitative analysis.

Main tasks
Date alignment
Missing value handling
Duplicate date removal
Price validation
Return calculation
Log-return calculation
Stale price detection
Rolling volatility calculation

The cleaned datasets are stored separately from the raw data.

Processed Data
data/processed/
├── clean_prices.csv
├── clean_returns.csv
├── portfolio_returns.csv
└── rolling_volatility.csv
Phase 3 — Portfolio Construction

The third phase converts individual asset returns into portfolio-level returns and P&L.

Features
Portfolio weight validation
Equal-weight portfolios
User-defined portfolio weights
Portfolio value calculation
Daily P&L calculation
Daily portfolio returns
Portfolio rebalancing support
Portfolio outputs
data/portfolio/
├── portfolio_daily.csv
└── portfolio_weights.csv

The main portfolio series used by the risk models is the daily portfolio return series.

Phase 4 — Historical VaR and Expected Shortfall

Phase 4 introduces historical simulation risk measurement.

Historical VaR

Historical Simulation VaR estimates the potential loss by using the empirical distribution of historical portfolio returns.

For a confidence level \(c\):

$$ VaR_c = -Q_{1-c}(R) $$

where:

\(R\) = portfolio return distribution
\(Q\) = empirical quantile
\(c\) = confidence level

The project supports:

250-day Historical VaR
500-day Historical VaR
750-day Historical VaR
Expected Shortfall

Expected Shortfall measures the average loss beyond the VaR threshold.

$$ ES_c = E[L \mid L > VaR_c] $$

where \(L\) represents portfolio losses.

Phase 4 outputs
data/risk/
├── historical_var_es.csv
└── rolling_var.csv
Phase 5 — EWMA Volatility Scaling

Phase 5 introduces a volatility-sensitive Historical VaR model.

The objective is to make historical risk estimates more responsive to changing volatility regimes.

EWMA Model

The Exponentially Weighted Moving Average model gives greater importance to recent observations.

The EWMA variance is calculated as:

$$ \sigma_t^2 = \lambda\sigma_{t-1}^2 + (1-\lambda)r_{t-1}^2 $$

where:

\(r_t\) = portfolio return
\(\sigma_t^2\) = EWMA variance
\(\lambda\) = decay factor

The project uses:

$$ \lambda = 0.94 $$

which is a commonly used daily decay factor.

EWMA Volatility

Volatility is calculated as:

$$ \sigma_t = \sqrt{\sigma_t^2} $$

The system can also convert daily volatility into annualized volatility:

$$ \sigma_{annual} = \sigma_{daily}\sqrt{252} $$
Volatility Scaling

Traditional Historical VaR treats historical returns equally regardless of the volatility regime in which they occurred.

EWMA volatility scaling adjusts historical returns to the current volatility level.

The scaled return is:

$$ r_i^{scaled} = r_i \frac{\sigma_t}{\sigma_i} $$

where:

\(r_i\) = historical return
\(\sigma_i\) = historical EWMA volatility
\(\sigma_t\) = current EWMA volatility

This allows historical returns to be expressed at today's volatility level.

EWMA-Scaled Historical VaR

The workflow is:

Historical Portfolio Returns
            │
            ▼
      EWMA Variance
            │
            ▼
      EWMA Volatility
            │
            ▼
   Historical Volatility
            │
            ▼
     Current Volatility
            │
            ▼
   Volatility Scaling
            │
            ▼
 Scaled Historical Returns
            │
            ▼
       Historical VaR

This approach should react more quickly when market volatility increases.

Phase 5 Risk Outputs

Phase 5 produces:

data/risk/
├── historical_var_es.csv
├── rolling_var.csv
├── ewma_volatility.csv
├── ewma_scaled_returns.csv
└── ewma_var.csv
Risk Model Architecture

The risk engine is organized into independent modules.

src/risk/
│
├── __init__.py
├── historical_var.py
├── historical_es.py
├── ewma.py
├── volatility_scaling.py
└── ewma_var.py
historical_var.py

Contains Historical Simulation VaR functionality.

historical_es.py

Contains Expected Shortfall calculations.

ewma.py

Responsible for:

EWMA variance
EWMA volatility
volatility_scaling.py

Responsible for:

Rescaling historical returns
Matching historical volatility to current volatility
ewma_var.py

Combines EWMA volatility and volatility scaling to calculate:

EWMA-scaled Historical VaR
Monetary EWMA VaR
Rolling EWMA VaR
Project Structure
Market Risk/
│
├── data/
│   │
│   ├── portfolio/
│   │   ├── portfolio_daily.csv
│   │   └── portfolio_weights.csv
│   │
│   ├── processed/
│   │   ├── clean_prices.csv
│   │   ├── clean_returns.csv
│   │   ├── portfolio_returns.csv
│   │   └── rolling_volatility.csv
│   │
│   ├── raw/
│   │   ├── market.csv
│   │   ├── prices.csv
│   │   ├── returns.csv
│   │   └── sectors.csv
│   │
│   └── risk/
│       ├── historical_var_es.csv
│       ├── rolling_var.csv
│       ├── ewma_volatility.csv
│       ├── ewma_scaled_returns.csv
│       └── ewma_var.csv
│
├── notebooks/
│   ├── phase_1.ipynb
│   ├── phase_2.ipynb
│   ├── phase_3.ipynb
│   ├── phase_4.ipynb
│   └── phase_5.ipynb
│
├── src/
│   │
│   ├── data/
│   │   ├── data_loader.py
│   │   └── metrics.py
│   │
│   ├── portfolio/
│   │   ├── portfolio_engine.py
│   │   ├── rebalancing.py
│   │   ├── validation.py
│   │   └── weights.py
│   │
│   ├── risk/
│   │   ├── __init__.py
│   │   ├── historical_var.py
│   │   ├── historical_es.py
│   │   ├── ewma.py
│   │   ├── volatility_scaling.py
│   │   └── ewma_var.py
│   │
│   └── utils/
│       └── plotting.py
│
├── tests/
│   ├── test_historical_var.py
│   ├── test_historical_es.py
│   ├── test_ewma.py
│   ├── test_volatility_scaling.py
│   └── test_ewma_var.py
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
Testing

The project uses pytest for automated testing.

Tests cover:

Historical VaR
Expected Shortfall
EWMA variance
EWMA volatility
Volatility scaling
EWMA VaR
Rolling EWMA VaR
Invalid parameters
Insufficient observations

Run all tests with:

py -m pytest -v

Run only Phase 5 tests:

py -m pytest tests/test_ewma.py tests/test_volatility_scaling.py tests/test_ewma_var.py -v
Data Requirements

The risk models require a sufficiently long portfolio return history.

The project targets:

≥ 750 portfolio return observations

This allows the system to calculate:

250-day risk measures
500-day risk measures
750-day risk measures

Using multiple historical windows allows the effect of the estimation horizon to be compared.

Phase 5 Visualizations

Phase 5 includes the following analysis charts.

1. EWMA Volatility

Shows how estimated portfolio volatility changes through time.

2. Raw Returns vs EWMA-Scaled Returns

Shows the effect of volatility scaling on historical observations.

3. Historical VaR vs EWMA-Scaled VaR

Compares the traditional Historical Simulation VaR with the volatility-adjusted model.

4. VaR Exception Comparison

Compares actual portfolio losses with the risk thresholds generated by both models.

Technology Stack
Python
NumPy
Pandas
Matplotlib
Pytest
Jupyter Notebook
VS Code
Git / GitHub
Design Principles

The project follows several software engineering principles:

Modularity

Each quantitative model has a dedicated module.

Separation of concerns

Data processing, portfolio construction, risk models, plotting, and testing are separated.

Reusability

Core calculations are implemented in src/ and reused by notebooks.

Testability

Risk calculations are accompanied by automated unit tests.

No look-ahead bias

Risk forecasts are designed so that future returns are not used to estimate current risk.

Reproducibility

Raw, processed, portfolio, and risk outputs are stored separately.

Future Development

The next stages of the project will introduce more advanced volatility and risk models.

Phase 6 — GARCH

Planned models:

GARCH(1,1)
Conditional volatility
GARCH-based VaR
Volatility forecasting
Phase 7 — GJR-GARCH

The GJR-GARCH model will capture asymmetric volatility responses to positive and negative returns.

Phase 8 — VaR Backtesting

Planned tests include:

VaR exception analysis
Exception frequency
Kupiec Proportion of Failures test
Christoffersen Independence test
Conditional Coverage analysis
Final Model Comparison

The final system will compare:

Historical VaR
       │
       ├── 250D
       ├── 500D
       └── 750D

EWMA VaR
       │
       ├── 250D
       ├── 500D
       └── 750D

GARCH VaR
       │
       └── Volatility Forecast

GJR-GARCH VaR
       │
       └── Asymmetric Volatility

             ↓

       VaR Backtesting
             ↓
       Model Comparison


Author

Harshal Yadav

Quantitative Finance / Risk Management Project


---
