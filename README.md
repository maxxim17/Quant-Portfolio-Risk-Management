# Quantitative Finance & Investment — Market Risk Management System

> **An end-to-end quantitative market risk platform for equity portfolios, covering Historical Simulation VaR, Expected Shortfall, EWMA, GARCH, GJR-GARCH, VaR backtesting, model comparison, stress testing, and interactive risk visualization.**

---

## 📊 Project Overview

This project implements a complete **equity portfolio market-risk management framework** using Python.

The system is designed to simulate a practical quantitative risk workflow used in financial institutions, asset managers, risk consulting, and quantitative research environments.

The project starts with historical market data and progresses through:

```text
Market Data
     ↓
Data Cleaning & Validation
     ↓
Portfolio Construction
     ↓
Historical Simulation VaR
     ↓
Expected Shortfall
     ↓
EWMA Volatility Scaling
     ↓
GARCH(1,1)
     ↓
GJR-GARCH
     ↓
VaR Backtesting
     ↓
Model Comparison
     ↓
Stress Testing
     ↓
Interactive Risk Dashboard
```

The objective is not only to calculate VaR, but to build a complete framework for understanding **how portfolio risk changes across models, market conditions, volatility regimes, and stress scenarios**.

---

# 🎯 Project Objectives

The main objectives of this project are to:

- Build a reproducible equity portfolio risk pipeline
- Collect and process historical market data
- Construct customizable equity portfolios
- Calculate Historical Simulation VaR
- Calculate Expected Shortfall
- Implement EWMA volatility scaling
- Implement GARCH(1,1) volatility modeling
- Implement GJR-GARCH asymmetric volatility modeling
- Backtest VaR forecasts
- Implement Kupiec's unconditional coverage test
- Implement Christoffersen's conditional coverage test
- Apply Basel-style traffic-light classification
- Compare multiple risk models
- Perform historical and hypothetical stress testing
- Build an interactive Streamlit dashboard
- Implement automated validation checks
- Develop unit tests for the risk engine
- Present the results through professional charts and analytics

---

# 🧠 Risk Models Implemented

## 1. Historical Simulation VaR

Historical Simulation VaR estimates portfolio risk directly from the empirical distribution of historical portfolio returns.

The framework supports multiple confidence levels:

- 90%
- 95%
- 99%

The historical return distribution is used without assuming a specific parametric distribution.

---

## 2. Expected Shortfall

Expected Shortfall (ES), also known as Conditional VaR, measures the average loss beyond the VaR threshold.

It provides information about the **severity of losses once VaR has been breached**.

The project uses Expected Shortfall alongside VaR to provide a more complete view of tail risk.

---

## 3. EWMA Volatility

Exponentially Weighted Moving Average volatility gives greater weight to recent observations.

The EWMA model uses:

\[
\sigma_t^2 =
\lambda\sigma_{t-1}^2
+
(1-\lambda)r_{t-1}^2
\]

where:

- \(r_t\) = portfolio return
- \(\sigma_t^2\) = conditional variance
- \(\lambda\) = decay factor

The default implementation uses:

```text
λ = 0.94
```

while allowing the parameter to be configured.

---

## 4. GARCH(1,1)

The GARCH model captures volatility clustering in financial returns.

The implemented model is:

\[
\sigma_t^2 =
\omega
+
\alpha\epsilon_{t-1}^2
+
\beta\sigma_{t-1}^2
\]

The system provides:

- Conditional volatility
- One-day-ahead volatility forecast
- Volatility-scaled historical returns
- GARCH-scaled VaR
- Standardized residuals

---

## 5. GJR-GARCH

GJR-GARCH extends GARCH by incorporating an asymmetric response to positive and negative shocks.

The model captures the **leverage effect**, where negative equity-market returns can have a larger effect on future volatility than positive returns of similar magnitude.

The implementation provides:

- Conditional volatility
- Leverage-effect parameter
- One-day-ahead volatility forecast
- Scaled returns
- GJR-GARCH-scaled VaR
- Comparison against standard GARCH

---

# 🔬 VaR Backtesting

A risk model should not only produce VaR estimates; its forecasts must also be tested against realized portfolio outcomes.

The project therefore implements VaR backtesting using realized portfolio returns/P&L.

## Backtesting Components

### Exception Analysis

A VaR exception occurs when the realized loss exceeds the predicted VaR.

The framework analyzes:

- Total exceptions
- Exception rate
- Expected exception rate
- Exception timeline
- Exception clustering

---

## Kupiec Unconditional Coverage Test

The Kupiec test evaluates whether the observed number of VaR exceptions is statistically consistent with the expected exception probability.

It tests the unconditional coverage property of the VaR model.

---

## Christoffersen Conditional Coverage Test

Christoffersen's test evaluates both:

1. Correct exception frequency
2. Independence of exceptions

This helps identify whether VaR breaches are clustered over time.

---

## Basel Traffic-Light Framework

The project also provides a Basel-style classification of VaR model performance.

Models can be categorized into:

- 🟢 Green zone
- 🟡 Yellow zone
- 🔴 Red zone

based on the number of observed exceptions.

---

# 📈 Model Comparison

The project compares multiple risk models:

| Model | Volatility Treatment | Risk Estimate |
|---|---|---|
| Historical Simulation | None | Historical VaR |
| EWMA | Exponentially weighted | EWMA-scaled VaR |
| GARCH | Conditional volatility | GARCH-scaled VaR |
| GJR-GARCH | Asymmetric conditional volatility | GJR-GARCH-scaled VaR |

The comparison framework evaluates model behavior using metrics such as:

- VaR magnitude
- Exception frequency
- Backtesting performance
- Model stability
- Volatility responsiveness
- Tail-risk behavior

The objective is to understand **which model provides the most useful representation of portfolio risk under different market conditions**.

---

# 💥 Stress Testing

The project includes a dedicated stress-testing framework to evaluate portfolio behavior under severe market scenarios.

Stress testing complements VaR by examining losses under predefined adverse conditions.

The framework supports:

- Scenario-based shocks
- Portfolio stress losses
- Stress VaR comparison
- Scenario ranking
- Sector-level shock analysis
- Worst-loss identification

Example scenarios include:

- Broad market sell-off
- High-volatility shock
- Sector-specific shock
- Individual asset shock
- Combined market stress

---

# 📊 Dashboard

The project includes an interactive **Streamlit + Plotly** risk dashboard.

## Dashboard Pages

### 1. Portfolio

Displays:

- Portfolio value
- Total return
- Daily returns
- Daily P&L
- Drawdown
- Return distribution

### 2. VaR

Provides:

- Confidence-level selection
- Historical VaR
- Expected Shortfall
- Rolling VaR
- VaR model comparison
- VaR vs actual losses

### 3. Volatility Scaling

Displays:

- Rolling volatility
- EWMA volatility
- GARCH volatility
- GJR-GARCH volatility
- Volatility regime comparison

### 4. Backtesting

Displays:

- VaR exception timeline
- Exceptions by model
- Actual P&L vs VaR
- Kupiec test
- Christoffersen test
- Basel traffic-light classification
- Expected vs actual exceptions

### 5. Model Comparison

Displays:

- Model performance
- VaR comparison
- Exception rates
- Model ranking
- Risk-model diagnostics

### 6. Stress Testing

Displays:

- Scenario selector
- Stress loss
- Stress VaR
- Scenario comparison
- Sector shock impact
- Worst-loss ranking

### 7. Validation

Displays and verifies:

- Missing dates
- Duplicate dates
- Missing returns
- Weight consistency
- P&L consistency
- VaR properties
- Backtesting validation

---

# 📉 Charts & Visual Analytics

The project includes interactive Plotly visualizations for:

## Portfolio Analytics

- Portfolio value over time
- Daily portfolio returns
- Daily portfolio P&L
- Drawdown
- Return distribution

## VaR Analytics

- Rolling Historical VaR
- EWMA-scaled VaR
- GARCH-scaled VaR
- GJR-GARCH-scaled VaR
- VaR vs actual loss
- VaR vs Expected Shortfall

## Volatility Analytics

- Rolling volatility
- EWMA volatility
- GARCH volatility
- GJR-GARCH volatility
- Volatility regime comparison

## Backtesting Analytics

- Exception timeline
- Exceptions by model
- Actual P&L vs VaR
- Expected vs actual exceptions
- Basel traffic-light visualization

## Stress Analytics

- Scenario loss
- Stress VaR comparison
- Sector shock impact
- Worst-loss ranking

---

# 🏗️ Project Architecture

```text
Market Risk/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw/
│   │   ├── prices.csv
│   │   ├── returns.csv
│   │   ├── market.csv
│   │   └── sectors.csv
│   │
│   ├── processed/
│   │   ├── clean_prices.csv
│   │   ├── clean_returns.csv
│   │   ├── portfolio_returns.csv
│   │   ├── rolling_volatility.csv
│   │   ├── garch_volatility.csv
│   │   ├── garch_scaled_returns.csv
│   │   ├── garch_var.csv
│   │   ├── gjr_garch_volatility.csv
│   │   ├── gjr_garch_scaled_returns.csv
│   │   └── gjr_garch_var.csv
│   │
│   ├── portfolio/
│   │   ├── portfolio_daily.csv
│   │   └── portfolio_weights.csv
│   │
│   ├── risk/
│   │   ├── historical_var_es.csv
│   │   ├── rolling_var.csv
│   │   ├── ewma_volatility.csv
│   │   ├── ewma_scaled_returns.csv
│   │   ├── ewma_var.csv
│   │   ├── backtest_observations.csv
│   │   ├── backtest_results.csv
│   │   ├── phase9_model_comparison.csv
│   │   ├── phase9_observations.csv
│   │   ├── phase9_model_ranking.csv
│   │   ├── phase10_stress_results.csv
│   │   ├── phase10_scenario_ranking.csv
│   │   └── phase10_stress_observations.csv
│   │
│   └── universe/
│       └── us_equities.csv
│
├── notebooks/
│   ├── phase_1.ipynb
│   ├── phase_2.ipynb
│   ├── phase_3.ipynb
│   ├── phase_4.ipynb
│   ├── phase_5.ipynb
│   ├── phase_6.ipynb
│   ├── phase_7.ipynb
│   ├── phase_8.ipynb
│   ├── phase_9.ipynb
│   └── phase_10.ipynb
│
├── scripts/
│   ├── build_universe.py
│   ├── run_phase9.py
│   └── run_phase10.py
│
├── src/
│   ├── dashboard/
│   │   ├── layout.py
│   │   ├── sidebar.py
│   │   ├── metrics.py
│   │   ├── charts.py
│   │   ├── garch_dashboard.py
│   │   ├── gjr_garch_dashboard.py
│   │   ├── backtesting_dashboard.py
│   │   ├── model_comparison_dashboard.py
│   │   └── stress_testing_dashboard.py
│   │
│   ├── risk/
│   │   ├── historical_var.py
│   │   ├── historical_es.py
│   │   ├── ewma.py
│   │   ├── volatility_scaling.py
│   │   ├── ewma_var.py
│   │   ├── garch.py
│   │   ├── gjr_garch.py
│   │   ├── backtesting.py
│   │   ├── model_comparison.py
│   │   └── stress_testing.py
│   │
│   └── validation/
│       ├── data_validation.py
│       ├── risk_validation.py
│       └── backtesting_validation.py
│
└── tests/
    ├── test_universe.py
    ├── test_downloader.py
    ├── test_historical_var.py
    ├── test_ewma.py
    ├── test_volatility_scaling.py
    ├── test_ewma_var.py
    ├── test_garch.py
    ├── test_gjr_garch.py
    ├── test_backtesting.py
    ├── test_model_comparison.py
    ├── test_stress_testing.py
    ├── test_data_validation.py
    ├── test_risk_validation.py
    └── test_backtesting_validation.py
```

---

# 🔄 End-to-End Workflow

The complete pipeline is organized into ten phases.

## Phase 1 — Data Collection

Collect historical equity prices, market benchmark data, and sector information.

The project supports a large US equity universe through:

```text
data/universe/us_equities.csv
```

---

## Phase 2 — Data Cleaning

Perform:

- Missing-value handling
- Date alignment
- Return calculation
- Duplicate removal
- Data consistency checks

---

## Phase 3 — Portfolio Construction

Construct portfolios using configurable:

- Ticker selection
- Portfolio weights
- Initial portfolio value
- Long-only or long-short configurations

The portfolio engine produces daily portfolio value and P&L.

---

## Phase 4 — Historical VaR & Expected Shortfall

Calculate:

- Historical VaR
- Multiple confidence levels
- Rolling VaR
- Expected Shortfall

---

## Phase 5 — EWMA Volatility Scaling

Implement:

- EWMA conditional volatility
- Volatility-scaled returns
- EWMA-scaled VaR

---

## Phase 6 — GARCH Volatility Scaling

Implement:

- GARCH(1,1)
- Conditional volatility
- One-day-ahead forecast
- Scaled historical returns
- GARCH-scaled VaR

---

## Phase 7 — GJR-GARCH Volatility Scaling

Implement:

- GJR-GARCH
- Asymmetric volatility
- Leverage effect
- Conditional volatility
- One-day-ahead forecast
- GJR-GARCH-scaled VaR

---

## Phase 8 — VaR Backtesting

Implement:

- VaR exceptions
- Exception rate
- Kupiec test
- Christoffersen test
- Basel traffic-light classification

---

## Phase 9 — Model Comparison

Compare:

- Historical Simulation
- EWMA
- GARCH
- GJR-GARCH

The framework produces model comparison tables and rankings.

---

## Phase 10 — Stress Testing

Evaluate portfolio losses under adverse scenarios.

Outputs include:

- Stress losses
- Stress VaR
- Scenario ranking
- Sector impacts
- Worst-case observations

---

# 🧪 Validation Framework

The project contains a dedicated validation layer.

## Data Validation

The system checks:

- Missing dates
- Duplicate dates
- Missing returns
- Infinite values
- Portfolio-weight consistency
- Portfolio P&L consistency
- Return alignment

---

## VaR Validation

The system checks whether:

- VaR is represented as a positive loss
- Higher confidence levels produce larger VaR
- Expected Shortfall is greater than or equal to VaR
- Multi-day VaR exceeds one-day VaR
- VaR responds appropriately to higher volatility

---

## Backtesting Validation

The system checks:

- Observed vs expected exception rates
- Exception clustering
- Kupiec test structure
- Christoffersen test structure

---

# 🧪 Unit Testing

The project uses `pytest` for automated testing.

Tests cover:

```text
Universe
Downloader
Historical VaR
EWMA
Volatility Scaling
EWMA VaR
GARCH
GJR-GARCH
Backtesting
Model Comparison
Stress Testing
Data Validation
Risk Validation
Backtesting Validation
```

Run the complete test suite with:

```powershell
& "C:\Program Files\Python314\python.exe" -m pytest -v
```

---

# ⚙️ Installation

## Requirements

Recommended environment:

- Python 3.14+
- Windows 10/11
- 8 GB+ RAM
- Internet connection for market-data collection

---

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "Market Risk"
```

---

## 2. Install Dependencies

Using the configured Python interpreter:

```powershell
& "C:\Program Files\Python314\python.exe" -m pip install -r requirements.txt
```

---

# ▶️ Running the Project

## Run Phase 9

```powershell
& "C:\Program Files\Python314\python.exe" scripts/run_phase9.py
```

---

## Run Phase 10

```powershell
& "C:\Program Files\Python314\python.exe" scripts/run_phase10.py
```

---

## Run Tests

```powershell
& "C:\Program Files\Python314\python.exe" -m pytest -v
```

---

## Launch Dashboard

```powershell
& "C:\Program Files\Python314\python.exe" -m streamlit run app.py
```

The dashboard will normally be available at:

```text
http://localhost:8501
```

---

# 📌 Key Output Files

The major outputs generated by the project include:

### Portfolio

```text
data/portfolio/portfolio_daily.csv
data/portfolio/portfolio_weights.csv
```

### Historical VaR

```text
data/risk/historical_var_es.csv
data/risk/rolling_var.csv
```

### EWMA

```text
data/risk/ewma_volatility.csv
data/risk/ewma_scaled_returns.csv
data/risk/ewma_var.csv
```

### GARCH

```text
data/processed/garch_volatility.csv
data/processed/garch_scaled_returns.csv
data/processed/garch_var.csv
```

### GJR-GARCH

```text
data/processed/gjr_garch_volatility.csv
data/processed/gjr_garch_scaled_returns.csv
data/processed/gjr_garch_var.csv
```

### Backtesting

```text
data/risk/backtest_observations.csv
data/risk/backtest_results.csv
```

### Model Comparison

```text
data/risk/phase9_model_comparison.csv
data/risk/phase9_observations.csv
data/risk/phase9_model_ranking.csv
```

### Stress Testing

```text
data/risk/phase10_stress_results.csv
data/risk/phase10_scenario_ranking.csv
data/risk/phase10_stress_observations.csv
```

---

# 📐 Portfolio & Risk Assumptions

The initial framework uses an equity portfolio with configurable portfolio weights.

Core assumptions include:

```text
Initial Portfolio Value: $1,000,000
Risk-Free Rate: 4.5%
Trading Days: 252
EWMA Lambda: 0.94
Confidence Levels: 90%, 95%, 99%
```

The portfolio framework can be extended to support:

- Custom portfolios
- Market-cap weighted portfolios
- Equal-weighted portfolios
- Long-short portfolios
- Alternative benchmarks
- Different confidence levels
- Different volatility models

---

# 🛡️ Risk Management Considerations

The project follows several important risk-management principles:

### No Look-Ahead Bias

Risk estimates must only use information available at the time of the forecast.

### Return Alignment

Historical returns and VaR forecasts must be correctly aligned with realized portfolio outcomes.

### Positive VaR Convention

VaR is represented as a positive loss amount.

### Tail-Risk Awareness

Expected Shortfall is included because VaR alone does not describe the severity of losses beyond the VaR threshold.

### Volatility Clustering

EWMA, GARCH, and GJR-GARCH models account for changing volatility conditions.

### Asymmetric Risk

GJR-GARCH captures the possibility that negative equity shocks have a stronger impact on future volatility.

---

# 📊 Example Risk Workflow

A typical analysis follows:

```text
Select Portfolio
      ↓
Calculate Daily Returns
      ↓
Calculate Historical VaR
      ↓
Calculate Expected Shortfall
      ↓
Estimate EWMA Volatility
      ↓
Estimate GARCH Volatility
      ↓
Estimate GJR-GARCH Volatility
      ↓
Generate Scaled VaR
      ↓
Backtest VaR
      ↓
Apply Kupiec Test
      ↓
Apply Christoffersen Test
      ↓
Compare Models
      ↓
Perform Stress Testing
      ↓
Analyze Dashboard
```

---

# 🧮 Mathematical Framework

## Historical VaR

For confidence level \(c\):

\[
VaR_c = -Q_{1-c}(R)
\]

where:

- \(R\) = portfolio return
- \(Q\) = empirical quantile
- \(c\) = confidence level

---

## Expected Shortfall

\[
ES_c =
-E[R \mid R \leq -VaR_c]
\]

Expected Shortfall measures the expected loss conditional on losses exceeding VaR.

---

## EWMA

\[
\sigma_t^2 =
\lambda\sigma_{t-1}^2
+
(1-\lambda)r_{t-1}^2
\]

---

## GARCH(1,1)

\[
\sigma_t^2 =
\omega
+
\alpha\epsilon_{t-1}^2
+
\beta\sigma_{t-1}^2
\]

---

## GJR-GARCH

A simplified GJR-GARCH specification is:

\[
\sigma_t^2 =
\omega
+
\alpha\epsilon_{t-1}^2
+
\gamma I_{\{\epsilon_{t-1}<0\}}
\epsilon_{t-1}^2
+
\beta\sigma_{t-1}^2
\]

where \(\gamma\) captures the asymmetric response to negative shocks.

---

# 🔍 Limitations

Although the framework is designed to resemble a professional market-risk workflow, several limitations remain.

### Historical Dependence

Historical Simulation VaR relies heavily on the selected historical sample.

### Model Risk

GARCH and GJR-GARCH results depend on model specification and estimation assumptions.

### Parameter Sensitivity

Different:

- confidence levels
- volatility windows
- EWMA decay factors
- GARCH specifications

can produce different risk estimates.

### Stress Scenario Dependence

Stress-test results depend on the selected scenarios and shock magnitudes.

### Market Data Quality

Risk estimates are only as reliable as the underlying market data.

### Limited Asset Classes

The current framework primarily focuses on equity portfolios.

Future versions can incorporate:

- Fixed income
- FX
- Commodities
- Options
- Credit instruments
- Multi-asset portfolios

---

# 🚀 Future Improvements

Potential extensions include:

- Monte Carlo VaR
- Parametric VaR
- EVT-based tail-risk models
- Multivariate GARCH
- DCC-GARCH
- Copula-based dependence modeling
- Liquidity-adjusted VaR
- Transaction-cost modeling
- Option Greeks
- Incremental VaR
- Marginal VaR
- Component VaR
- Risk decomposition
- Portfolio optimization
- Black-Litterman allocation
- Risk parity
- Maximum diversification
- Machine-learning volatility forecasting
- Real-time market-data ingestion
- Cloud deployment
- Database-backed historical data
- Automated risk reports
- Email/alert-based risk monitoring

---

# 🏦 Industry Relevance

The concepts implemented in this project are commonly encountered in quantitative risk management workflows across:

### Investment Banks

- JPMorgan Chase
- Goldman Sachs
- Morgan Stanley
- Bank of America
- Citigroup

### Asset Managers

- BlackRock
- PIMCO
- Vanguard

### Consulting & Professional Services

- Deloitte
- PwC
- EY
- KPMG

The project is intended as an educational and research implementation of concepts used in professional market-risk environments.

---

# 🎓 Learning Outcomes

This project provides practical experience in:

- Quantitative finance
- Market risk management
- Equity portfolio analytics
- Probability and statistics
- Time-series analysis
- Volatility modeling
- Value at Risk
- Expected Shortfall
- EWMA
- GARCH
- GJR-GARCH
- Statistical backtesting
- Kupiec testing
- Christoffersen testing
- Basel risk concepts
- Stress testing
- Python software engineering
- Unit testing
- Data engineering
- Interactive visualization
- Streamlit application development
- Plotly analytics

---

# 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| NumPy | Numerical computing |
| Pandas | Data manipulation |
| SciPy | Statistical calculations |
| yfinance | Market data |
| ARCH | GARCH-family models |
| Plotly | Interactive visualization |
| Streamlit | Dashboard |
| Pytest | Unit testing |
| Jupyter | Research & experimentation |
| Git | Version control |

---

# 📁 Development Philosophy

The project follows a modular architecture:

```text
Data Layer
     ↓
Risk Engine
     ↓
Validation Layer
     ↓
Dashboard Layer
     ↓
Testing Layer
```

The objective is to keep:

- Data processing
- Risk calculations
- Visualization
- Validation
- Testing

separated from each other.

This makes the project easier to maintain, test, extend, and deploy.

---

# 🔐 Disclaimer

This project is intended for **educational, research, and software-development purposes**.

The risk estimates produced by this system should not be interpreted as investment advice or as a guarantee of future portfolio losses.

Market-risk models are subject to:

- Data risk
- Model risk
- Parameter risk
- Estimation error
- Structural breaks
- Extreme-event uncertainty

Actual portfolio losses may differ significantly from model estimates.

---

# 👨‍💻 Author

**Harshal Yadav**

Quantitative Finance & Investment Project

Areas of interest:

- Quantitative Finance
- Market Risk
- Algorithmic Trading
- Machine Learning
- Artificial Intelligence
- Time-Series Modeling
- Financial Engineering

---

# ⭐ Project Status

```text
Phase 1  — Data Collection              ✅
Phase 2  — Data Cleaning                ✅
Phase 3  — Portfolio Construction       ✅
Phase 4  — Historical VaR & ES          ✅
Phase 5  — EWMA Volatility Scaling      ✅
Phase 6  — GARCH Volatility Scaling     ✅
Phase 7  — GJR-GARCH                    ✅
Phase 8  — VaR Backtesting              ✅
Phase 9  — Model Comparison             ✅
Phase 10 — Stress Testing               ✅
Validation Framework                    🚧
Interactive Dashboard                   🚧
Final Testing                           🚧
Documentation                           🚧
Presentation                            🚧
```

> **Project goal:** Build a complete, modular, testable, and interactive quantitative market-risk platform for equity portfolios.