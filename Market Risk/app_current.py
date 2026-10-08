from __future__ import annotations


import sys
from pathlib import Path
from turtle import st

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src.dashboard.stress_testing_dashboard import (
    show_stress_testing_dashboard,
)

from src.dashboard.model_comparison_dashboard import (
    show_model_comparison,
)
from src.dashboard.garch_dashboard import render_garch_dashboard
from src.dashboard.gjr_garch_dashboard import render_gjr_garch_dashboard
from src.dashboard.backtesting_dashboard import (
    render_backtesting_dashboard
)

selected_phase = st.sidebar.selectbox(
    "Select Phase",
    [
        "Phase 1 - Data Collection",
        "Phase 2 - Data Cleaning",
        "Phase 3 - Portfolio Construction",
        "Phase 4 - Historical VaR",
        "Phase 5 - EWMA",
        "Phase 6 - GARCH",
        "Phase 7 - GJR-GARCH",
        "Phase 8 - Backtesting",
        "Phase 9 - Model Comparison",
        "Phase 10 - Stress Testing",
    ],
)

selected_phase = st.sidebar.selectbox(
    "Select Phase",
    [
        "Portfolio Construction",
        "GARCH",
        "GJR-GARCH",
        "VaR Backtesting",
        "Model Comparison",
    ],
)

if selected_phase == "Model Comparison":
    show_model_comparison()

if selected_phase == "Phase 7 - GJR-GARCH":
    render_gjr_garch_dashboard()

elif selected_phase == "Phase 8 - VaR Backtesting":
    render_backtesting_dashboard()

elif selected_phase == "Phase 10 - Stress Testing":

    show_stress_testing_dashboard()
    

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )

from src.dashboard.charts import (
    render_cumulative_returns,
    render_drawdown_chart,
    render_price_chart,
    render_returns_chart,
)

from src.dashboard.layout import (
    render_header,
    render_selected_stocks,
)

from src.dashboard.metrics import (
    render_portfolio_metrics,
)

from src.dashboard.sidebar import (
    render_sidebar,
)

from src.data.data_loader import (
    load_selected_prices,
)

from src.data.universe import (
    load_stock_universe,
)


st.set_page_config(
    page_title="Portfolio Risk Engine",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(
    ttl="1h",
    show_spinner=False,
)
def cached_load_prices(
    tickers: tuple[str, ...],
    start: str,
    end: str,
    force_refresh: bool,
):

    return load_selected_prices(
        tickers=list(tickers),
        start=start,
        end=end,
        force_refresh=force_refresh,
    )


def main():

    render_header()

    universe = load_stock_universe()

    config = render_sidebar()

    if not config["selected_tickers"]:

        st.info(
            "Search and select at least one stock "
            "from the sidebar."
        )

        return

    render_selected_stocks(
        universe,
        config["selected_tickers"],
    )

    if not config["build"]:

        st.info(
            "Configure your portfolio and click "
            "**Build Portfolio**."
        )

        return

    if (
        config["start_date"]
        >= config["end_date"]
    ):

        st.error(
            "Start date must be before end date."
        )

        return

    tickers = tuple(
        config["selected_tickers"]
    )

    with st.spinner(
        "Downloading and preparing market data..."
    ):

        try:

            prices = cached_load_prices(
                tickers=tickers,
                start=str(
                    config["start_date"]
                ),
                end=str(
                    config["end_date"]
                ),
                force_refresh=config[
                    "force_refresh"
                ],
            )

        except Exception as exc:

            st.error(
                f"Data download failed: {exc}"
            )

            return

    if prices.empty:

        st.error(
            "No valid price data was returned."
        )

        return

    returns = prices.pct_change().dropna()

    # Equal-weight portfolio for now.
    # Your existing portfolio engine will
    # replace this section.
    portfolio_returns = returns.mean(
        axis=1
    )

    st.success(
        f"Portfolio built using "
        f"{len(tickers)} assets."
    )

    render_portfolio_metrics(
        returns=portfolio_returns,
        portfolio_value=config[
            "initial_value"
        ],
    )

    st.divider()

    render_price_chart(
        prices
    )

    render_cumulative_returns(
        portfolio_returns
    )

    render_drawdown_chart(
        portfolio_returns
    )

    render_returns_chart(
        returns
    )


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
from pathlib import Path

from src.dashboard.charts import (
    portfolio_value_chart,
    portfolio_returns_chart,
    pnl_chart,
    drawdown_chart,
    return_distribution_chart,
    volatility_comparison_chart,
    var_comparison_chart,
    scenario_loss_chart,
)


BASE_DIR = Path(__file__).resolve().parent

PORTFOLIO_FILE = (
    BASE_DIR
    / "data"
    / "portfolio"
    / "portfolio_daily.csv"
)

RISK_DIR = (
    BASE_DIR
    / "data"
    / "risk"
)

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)


@st.cache_data
def load_csv(path):

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"]
        )

    return df


portfolio_df = load_csv(
    PORTFOLIO_FILE
)


st.set_page_config(
    page_title="QFI Market Risk Dashboard",
    page_icon="📊",
    layout="wide",
)


st.title(
    "Quantitative Finance & Investment — Market Risk Dashboard"
)

st.caption(
    "Equity Portfolio Risk Management | VaR | Volatility | Backtesting | Stress Testing"
)


page = st.sidebar.selectbox(
    "Select Page",
    [
        "Portfolio",
        "VaR",
        "Volatility Scaling",
        "Backtesting",
        "Model Comparison",
        "Stress Testing",
        "Validation",
    ],
)


# ============================================================
# PORTFOLIO
# ============================================================

if page == "Portfolio":

    st.header("Portfolio Analytics")

    if portfolio_df.empty:

        st.error(
            "portfolio_daily.csv was not found."
        )

    else:

        col1, col2, col3, col4 = st.columns(4)

        initial_value = portfolio_df[
            "Portfolio Value"
        ].iloc[0]

        final_value = portfolio_df[
            "Portfolio Value"
        ].iloc[-1]

        total_return = (
            final_value / initial_value - 1
        )

        max_value = portfolio_df[
            "Portfolio Value"
        ].cummax()

        drawdown = (
            portfolio_df["Portfolio Value"]
            / max_value - 1
        )

        max_drawdown = drawdown.min()

        col1.metric(
            "Initial Portfolio",
            f"${initial_value:,.0f}",
        )

        col2.metric(
            "Current Portfolio",
            f"${final_value:,.0f}",
        )

        col3.metric(
            "Total Return",
            f"{total_return:.2%}",
        )

        col4.metric(
            "Maximum Drawdown",
            f"{max_drawdown:.2%}",
        )

        st.plotly_chart(
            portfolio_value_chart(
                portfolio_df
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            portfolio_returns_chart(
                portfolio_df
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            pnl_chart(
                portfolio_df
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            drawdown_chart(
                portfolio_df
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            return_distribution_chart(
                portfolio_df
            ),
            use_container_width=True,
        )


# ============================================================
# VAR
# ============================================================

elif page == "VaR":

    st.header("Value at Risk")

    confidence = st.selectbox(
        "Confidence Level",
        [0.90, 0.95, 0.99],
        index=1,
    )

    historical_var_file = (
        RISK_DIR
        / "historical_var_es.csv"
    )

    df = load_csv(
        historical_var_file
    )

    if df.empty:

        st.warning(
            "Historical VaR output not found."
        )

    else:

        st.dataframe(
            df.tail(20),
            use_container_width=True,
        )

        var_columns = [
            column
            for column in df.columns
            if "VaR" in column
        ]

        if var_columns:

            st.plotly_chart(
                var_comparison_chart(
                    df,
                    var_columns,
                ),
                use_container_width=True,
            )


# ============================================================
# VOLATILITY
# ============================================================

elif page == "Volatility Scaling":

    st.header(
        "Volatility Scaling Models"
    )

    rolling_file = (
        PROCESSED_DIR
        / "rolling_volatility.csv"
    )

    ewma_file = (
        RISK_DIR
        / "ewma_volatility.csv"
    )

    garch_file = (
        PROCESSED_DIR
        / "garch_volatility.csv"
    )

    gjr_file = (
        PROCESSED_DIR
        / "gjr_garch_volatility.csv"
    )

    rolling = load_csv(
        rolling_file
    )

    ewma = load_csv(
        ewma_file
    )

    garch = load_csv(
        garch_file
    )

    gjr = load_csv(
        gjr_file
    )

    st.plotly_chart(
        volatility_comparison_chart(
            rolling=rolling,
            ewma=ewma,
            garch=garch,
            gjr=gjr,
        ),
        use_container_width=True,
    )


# ============================================================
# BACKTESTING
# ============================================================

elif page == "Backtesting":

    st.header(
        "VaR Backtesting"
    )

    observations = load_csv(
        RISK_DIR
        / "backtest_observations.csv"
    )

    results = load_csv(
        RISK_DIR
        / "backtest_results.csv"
    )

    if not observations.empty:

        st.subheader(
            "Exception Timeline"
        )

        exception_columns = [
            c
            for c in observations.columns
            if "Exception" in c
        ]

        if exception_columns:

            for column in exception_columns:

                st.line_chart(
                    observations[
                        ["Date", column]
                    ].set_index("Date")
                )

    if not results.empty:

        st.subheader(
            "Backtesting Results"
        )

        st.dataframe(
            results,
            use_container_width=True,
        )


# ============================================================
# MODEL COMPARISON
# ============================================================

elif page == "Model Comparison":

    st.header(
        "Risk Model Comparison"
    )

    comparison = load_csv(
        RISK_DIR
        / "phase9_model_comparison.csv"
    )

    ranking = load_csv(
        RISK_DIR
        / "phase9_model_ranking.csv"
    )

    if not comparison.empty:

        st.subheader(
            "Model Comparison"
        )

        st.dataframe(
            comparison,
            use_container_width=True,
        )

    if not ranking.empty:

        st.subheader(
            "Model Ranking"
        )

        st.dataframe(
            ranking,
            use_container_width=True,
        )


# ============================================================
# STRESS TESTING
# ============================================================

elif page == "Stress Testing":

    st.header(
        "Stress Testing"
    )

    stress = load_csv(
        RISK_DIR
        / "phase10_stress_results.csv"
    )

    ranking = load_csv(
        RISK_DIR
        / "phase10_scenario_ranking.csv"
    )

    observations = load_csv(
        RISK_DIR
        / "phase10_stress_observations.csv"
    )

    if not stress.empty:

        st.subheader(
            "Stress Test Results"
        )

        st.dataframe(
            stress,
            use_container_width=True,
        )

    if not ranking.empty:

        st.subheader(
            "Scenario Ranking"
        )

        st.dataframe(
            ranking,
            use_container_width=True,
        )

    if not observations.empty:

        st.subheader(
            "Stress Observations"
        )

        st.dataframe(
            observations,
            use_container_width=True,
        )


# ============================================================
# VALIDATION
# ============================================================

elif page == "Validation":

    st.header(
        "Risk Model Validation"
    )

    if portfolio_df.empty:

        st.error(
            "Portfolio data unavailable."
        )

    else:

        st.success(
            "Portfolio data successfully loaded."
        )

        required_columns = [
            "Date",
            "Portfolio Return",
            "Portfolio Value",
            "Portfolio P&L",
        ]

        missing = [
            c
            for c in required_columns
            if c not in portfolio_df.columns
        ]

        if not missing:

            st.success(
                "Required portfolio columns present."
            )

        else:

            st.error(
                f"Missing columns: {missing}"
            )

        missing_returns = (
            portfolio_df[
                "Portfolio Return"
            ]
            .isna()
            .sum()
        )

        if missing_returns == 0:

            st.success(
                "No missing portfolio returns."
            )

        else:

            st.error(
                f"{missing_returns} missing returns."
            )

        duplicate_dates = (
            portfolio_df["Date"]
            .duplicated()
            .sum()
        )

        if duplicate_dates == 0:

            st.success(
                "No duplicate dates."
            )

        else:

            st.error(
                f"{duplicate_dates} duplicate dates."
            )