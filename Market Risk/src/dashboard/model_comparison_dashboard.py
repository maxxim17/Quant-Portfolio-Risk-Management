"""
Phase 9 - Model Comparison Dashboard
"""

from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def load_phase9_data():

    root = Path(__file__).resolve().parents[2]

    risk_dir = (
        root
        / "data"
        / "risk"
    )

    comparison = pd.read_csv(
        risk_dir
        / "phase9_model_comparison.csv"
    )

    observations = pd.read_csv(
        risk_dir
        / "phase9_observations.csv"
    )

    ranking = pd.read_csv(
        risk_dir
        / "phase9_model_ranking.csv"
    )

    observations["Date"] = pd.to_datetime(
        observations["Date"]
    )

    return (
        comparison,
        observations,
        ranking,
    )


def show_model_comparison():

    st.header(
        "Phase 9 — VaR Model Comparison"
    )

    try:

        (
            comparison,
            observations,
            ranking,
        ) = load_phase9_data()

    except FileNotFoundError:

        st.error(
            "Phase 9 output files were not found. "
            "Run scripts/run_phase9.py first."
        )

        return

    # -------------------------------------------------------------
    # KPI section
    # -------------------------------------------------------------

    st.subheader(
        "Model Performance Summary"
    )

    best_model = ranking.iloc[0]["Model"]

    best_score = ranking.iloc[0]["Score"]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Best Overall Model",
            best_model,
        )

    with col2:

        st.metric(
            "Best Model Score",
            f"{best_score:.2f}",
        )

    # -------------------------------------------------------------
    # Comparison table
    # -------------------------------------------------------------

    st.subheader(
        "Model Comparison"
    )

    st.dataframe(
        comparison,
        use_container_width=True,
    )

    # -------------------------------------------------------------
    # VaR line chart
    # -------------------------------------------------------------

    st.subheader(
        "VaR Model Comparison"
    )

    fig = go.Figure()

    model_columns = {
        "Historical Simulation": "Historical VaR",
        "EWMA": "EWMA VaR",
        "GARCH": "GARCH VaR",
        "GJR-GARCH": "GJR-GARCH VaR",
    }

    for model, column in model_columns.items():

        fig.add_trace(
            go.Scatter(
                x=observations["Date"],
                y=observations[column],
                mode="lines",
                name=model,
            )
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="VaR",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # -------------------------------------------------------------
    # Actual loss vs VaR
    # -------------------------------------------------------------

    st.subheader(
        "Actual Portfolio Loss vs VaR"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=observations["Date"],
            y=-observations["Portfolio P&L"],
            mode="lines",
            name="Actual Loss",
        )
    )

    for model, column in model_columns.items():

        fig.add_trace(
            go.Scatter(
                x=observations["Date"],
                y=observations[column],
                mode="lines",
                name=model,
            )
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Loss / VaR",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # -------------------------------------------------------------
    # Exception overlay
    # -------------------------------------------------------------

    st.subheader(
        "Exceptions Overlay"
    )

    selected_model = st.selectbox(
        "Select VaR Model",
        list(model_columns.keys()),
    )

    var_column = model_columns[
        selected_model
    ]

    exception_column = (
        f"{selected_model} Exception"
    )

    exception_data = observations[
        observations[exception_column] == 1
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=observations["Date"],
            y=-observations["Portfolio P&L"],
            mode="lines",
            name="Actual Loss",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=observations["Date"],
            y=observations[var_column],
            mode="lines",
            name=f"{selected_model} VaR",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=exception_data["Date"],
            y=-exception_data["Portfolio P&L"],
            mode="markers",
            name="Exceptions",
            marker=dict(
                size=9,
                symbol="x",
            ),
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Loss / VaR",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # -------------------------------------------------------------
    # Exception bar chart
    # -------------------------------------------------------------

    st.subheader(
        "Backtesting Exception Comparison"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=comparison["Model"],
            y=comparison["Number of Exceptions"],
            name="Exceptions",
        )
    )

    fig.update_layout(
        xaxis_title="Model",
        yaxis_title="Number of Exceptions",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # -------------------------------------------------------------
    # Ranking
    # -------------------------------------------------------------

    st.subheader(
        "Model Ranking"
    )

    ranking_columns = [
        "Overall Rank",
        "Model",
        "Score",
        "Number of Exceptions",
        "Exception Ratio",
        "Average VaR",
        "VaR Volatility",
        "Expected Shortfall",
        "Kupiec p-value",
        "Traffic Light",
    ]

    st.dataframe(
        ranking[ranking_columns],
        use_container_width=True,
    )