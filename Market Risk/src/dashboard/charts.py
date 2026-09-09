from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def render_price_chart(
    prices: pd.DataFrame,
):

    st.subheader("Portfolio Asset Prices")

    st.line_chart(
        prices,
        height=400,
    )


def render_returns_chart(
    returns: pd.DataFrame,
):

    st.subheader("Daily Returns")

    st.line_chart(
        returns,
        height=350,
    )


def render_cumulative_returns(
    portfolio_returns: pd.Series,
):

    cumulative = (
        1 + portfolio_returns
    ).cumprod()

    st.subheader(
        "Cumulative Portfolio Performance"
    )

    st.line_chart(
        cumulative,
        height=400,
    )


def render_drawdown_chart(
    portfolio_returns: pd.Series,
):

    cumulative = (
        1 + portfolio_returns
    ).cumprod()

    drawdown = (
        cumulative
        / cumulative.cummax()
        - 1
    )

    st.subheader("Portfolio Drawdown")

    st.area_chart(
        drawdown,
        height=300,
    )