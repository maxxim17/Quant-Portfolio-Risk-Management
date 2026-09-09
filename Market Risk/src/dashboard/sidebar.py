from __future__ import annotations

from datetime import date

import streamlit as st

from src.data.universe import load_stock_universe


def render_sidebar():

    universe = load_stock_universe()

    st.sidebar.title(
        "Portfolio Configuration"
    )

    st.sidebar.caption(
        f"{len(universe):,} stocks available"
    )

    selected = st.sidebar.multiselect(
        "Search & select stocks",
        options=universe["ticker"].tolist(),
        default=["AAPL", "MSFT", "NVDA"],
        format_func=lambda ticker: (
            f"{ticker} — "
            f"{universe.loc[universe['ticker'] == ticker, 'name'].iloc[0]}"
        ),
        max_selections=30,
        placeholder="Search ticker or company...",
        filter_mode="contains",
    )

    st.sidebar.divider()

    col1, col2 = st.sidebar.columns(2)

    with col1:
        start_date = st.date_input(
            "Start date",
            value=date(2021, 1, 1),
        )

    with col2:
        end_date = st.date_input(
            "End date",
            value=date.today(),
        )

    initial_value = st.sidebar.number_input(
        "Initial portfolio value ($)",
        min_value=1_000.0,
        value=100_000.0,
        step=10_000.0,
    )

    rebalance_frequency = st.sidebar.selectbox(
        "Rebalancing frequency",
        [
            "none",
            "daily",
            "weekly",
            "monthly",
            "quarterly",
        ],
        index=3,
    )

    transaction_cost_bps = st.sidebar.number_input(
        "Transaction cost (bps)",
        min_value=0.0,
        value=5.0,
        step=0.5,
    )

    rolling_window = st.sidebar.slider(
        "Rolling volatility window",
        min_value=5,
        max_value=252,
        value=21,
    )

    st.sidebar.divider()

    st.sidebar.subheader(
        "Risk Parameters"
    )

    confidence_level = st.sidebar.selectbox(
        "Confidence Level",
        [0.90, 0.95, 0.99],
        index=1,
        format_func=lambda x: f"{x:.0%}",
    )

    lookback_window = st.sidebar.selectbox(
        "Rolling Lookback Window (Days)",
        [250, 500, 750],
        index=0,
    )

    st.sidebar.divider()

    st.sidebar.subheader(
        "Portfolio Scheme"
    )

    weighting_method = st.sidebar.radio(
        "Weighting method",
        [
            "Equal-weighted",
            "User-defined weights",
            "Market-cap weighted",
            "Long-short",
        ],
    )

    build = st.sidebar.button(
        "Build Portfolio",
        type="primary",
        use_container_width=True,
    )

    force_refresh = st.sidebar.checkbox(
        "Force fresh data download"
    )

    return {
        "selected_tickers": selected,
        "start_date": start_date,
        "end_date": end_date,
        "initial_value": initial_value,
        "rebalance_frequency": rebalance_frequency,
        "transaction_cost_bps": transaction_cost_bps,
        "rolling_window": rolling_window,
        "confidence_level": confidence_level,
        "lookback_window": lookback_window,
        "weighting_method": weighting_method,
        "build": build,
        "force_refresh": force_refresh,
    }