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




import plotly.graph_objects as go
import plotly.express as px


def portfolio_value_chart(df):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Portfolio Value"],
            mode="lines",
            name="Portfolio Value",
        )
    )

    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value",
        template="plotly_white",
    )

    return fig


def portfolio_returns_chart(df):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Portfolio Return"],
            mode="lines",
            name="Daily Return",
        )
    )

    fig.update_layout(
        title="Daily Portfolio Returns",
        xaxis_title="Date",
        yaxis_title="Return",
        template="plotly_white",
    )

    return fig

import plotly.graph_objects as go



def render_cumulative_returns(
    df: pd.DataFrame,
    return_column: str = "Portfolio Return",
    date_column: str = "Date",
):
    """
    Render cumulative portfolio returns.

    Parameters
    ----------
    df : pd.DataFrame
        Portfolio dataframe.
    return_column : str
        Column containing daily portfolio returns.
    date_column : str
        Column containing dates.
    """

    if df is None or df.empty:
        st.info("No portfolio return data available.")
        return

    data = df.copy()

    if return_column not in data.columns:
        st.warning(
            f"Column '{return_column}' was not found in the portfolio data."
        )
        return

    if date_column in data.columns:
        data[date_column] = pd.to_datetime(
            data[date_column],
            errors="coerce"
        )

    data[return_column] = pd.to_numeric(
        data[return_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[return_column]
    ).copy()

    if data.empty:
        st.info("No valid return observations available.")
        return

    data = data.sort_values(date_column)

    # Cumulative return:
    # (1+r1)(1+r2)...(1+rn) - 1
    data["Cumulative Return"] = (
        (1 + data[return_column]).cumprod() - 1
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data[date_column],
            y=data["Cumulative Return"] * 100,
            mode="lines",
            name="Cumulative Return",
            hovertemplate=(
                "%{x|%d %b %Y}"
                "<br>Cumulative Return: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=0,
        line_width=1,
        line_dash="dash",
    )

    fig.update_layout(
        title="Cumulative Portfolio Returns",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        hovermode="x unified",
        template="plotly_white",
        height=450,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

def pnl_chart(df):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Portfolio P&L"],
            name="P&L",
        )
    )

    fig.update_layout(
        title="Daily Portfolio P&L",
        xaxis_title="Date",
        yaxis_title="P&L",
        template="plotly_white",
    )

    return fig


def drawdown_chart(df):

    values = df["Portfolio Value"]

    running_max = values.cummax()

    drawdown = (
        values / running_max - 1
    ) * 100

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=drawdown,
            mode="lines",
            name="Drawdown",
            fill="tozeroy",
        )
    )

    fig.update_layout(
        title="Portfolio Drawdown",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_white",
    )

    return fig


def return_distribution_chart(df):

    fig = px.histogram(
        df,
        x="Portfolio Return",
        nbins=60,
        title="Portfolio Return Distribution",
    )

    fig.update_layout(
        template="plotly_white",
    )

    return fig


def volatility_comparison_chart(
    rolling=None,
    ewma=None,
    garch=None,
    gjr=None,
):

    fig = go.Figure()

    if rolling is not None:
        fig.add_trace(
            go.Scatter(
                x=rolling["Date"],
                y=rolling["Rolling Volatility"],
                name="Rolling",
            )
        )

    if ewma is not None:
        fig.add_trace(
            go.Scatter(
                x=ewma["Date"],
                y=ewma["EWMA Volatility"],
                name="EWMA",
            )
        )

    if garch is not None:
        fig.add_trace(
            go.Scatter(
                x=garch["Date"],
                y=garch["Conditional Volatility"],
                name="GARCH",
            )
        )

    if gjr is not None:
        fig.add_trace(
            go.Scatter(
                x=gjr["Date"],
                y=gjr["GJR-GARCH Conditional Volatility"],
                name="GJR-GARCH",
            )
        )

    fig.update_layout(
        title="Volatility Regime Comparison",
        xaxis_title="Date",
        yaxis_title="Volatility",
        template="plotly_white",
    )

    return fig


def var_comparison_chart(
    df,
    columns,
):

    fig = go.Figure()

    for column in columns:

        if column in df.columns:

            fig.add_trace(
                go.Scatter(
                    x=df["Date"],
                    y=df[column],
                    mode="lines",
                    name=column,
                )
            )

    fig.update_layout(
        title="VaR Model Comparison",
        xaxis_title="Date",
        yaxis_title="VaR",
        template="plotly_white",
    )

    return fig


def actual_vs_var_chart(
    df,
    actual_column,
    var_column,
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[actual_column],
            mode="lines",
            name="Actual",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[var_column],
            mode="lines",
            name="VaR",
        )
    )

    fig.update_layout(
        title="Actual Loss vs VaR",
        xaxis_title="Date",
        yaxis_title="Loss",
        template="plotly_white",
    )

    return fig


def scenario_loss_chart(df):

    fig = px.bar(
        df,
        x="Scenario",
        y="Stress Loss",
        title="Stress Scenario Loss",
    )

    fig.update_layout(
        template="plotly_white",
    )

    return fig


def exception_timeline_chart(
    df,
    exception_column="Exception",
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[exception_column].astype(int),
            mode="markers",
            name="Exceptions",
        )
    )

    fig.update_layout(
        title="VaR Exception Timeline",
        xaxis_title="Date",
        yaxis_title="Exception",
        template="plotly_white",
    )

    return fig