from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


def render_portfolio_metrics(
    returns: pd.Series,
    portfolio_value: float,
):

    if returns.empty:
        return

    cumulative_return = (
        (1 + returns).prod() - 1
    )

    annualized_return = (
        (1 + cumulative_return)
        ** (252 / len(returns))
        - 1
    )

    annualized_volatility = (
        returns.std() * np.sqrt(252)
    )

    sharpe = (
        annualized_return
        / annualized_volatility
        if annualized_volatility > 0
        else np.nan
    )

    cumulative = (
        1 + returns
    ).cumprod()

    drawdown = (
        cumulative
        / cumulative.cummax()
        - 1
    )

    max_drawdown = drawdown.min()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Portfolio Return",
        f"{cumulative_return:.2%}",
    )

    col2.metric(
        "Annualized Return",
        f"{annualized_return:.2%}",
    )

    col3.metric(
        "Annualized Volatility",
        f"{annualized_volatility:.2%}",
    )

    col4.metric(
        "Sharpe Ratio",
        f"{sharpe:.2f}",
    )

    col5.metric(
        "Max Drawdown",
        f"{max_drawdown:.2%}",
    )