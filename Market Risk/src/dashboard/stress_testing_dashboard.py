"""
Phase 10 - Stress Testing Dashboard
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[2]

RESULTS_FILE = (
    ROOT
    / "data"
    / "risk"
    / "phase10_stress_results.csv"
)

RANKING_FILE = (
    ROOT
    / "data"
    / "risk"
    / "phase10_scenario_ranking.csv"
)


def show_stress_testing_dashboard():

    st.title("Phase 10 - Stress Testing")

    st.markdown(
        """
        Stress testing evaluates portfolio vulnerability
        under historical crises and hypothetical market shocks.
        """
    )

    if not RESULTS_FILE.exists():

        st.warning(
            "Phase 10 results not found. "
            "Run scripts/run_phase10.py first."
        )

        return

    results = pd.read_csv(
        RESULTS_FILE
    )

    ranking = pd.read_csv(
        RANKING_FILE
    )

    # ========================================================
    # Top metrics
    # ========================================================

    worst_scenario = ranking.iloc[0]

    worst_loss = (
        worst_scenario[
            "Worst-Case Loss"
        ]
    )

    worst_var = (
        results["Stressed VaR"]
        .max()
    )

    worst_es = (
        results["Stressed Expected Shortfall"]
        .max()
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Worst-Case Loss",
            f"{worst_loss:.2%}",
        )

    with col2:

        st.metric(
            "Maximum Stressed VaR",
            f"{worst_var:.2%}",
        )

    with col3:

        st.metric(
            "Maximum Stressed ES",
            f"{worst_es:.2%}",
        )

    st.divider()

    # ========================================================
    # Scenario ranking
    # ========================================================

    st.subheader(
        "Scenario Ranking"
    )

    st.dataframe(
        ranking,
        use_container_width=True,
    )

    # ========================================================
    # Scenario loss comparison
    # ========================================================

    st.subheader(
        "Stressed Portfolio Loss"
    )

    fig_loss = px.bar(
        ranking.sort_values(
            "Worst-Case Loss",
            ascending=True,
        ),
        x="Worst-Case Loss",
        y="Scenario",
        color="Scenario Type",
        orientation="h",
        title="Worst-Case Loss by Scenario",
    )

    fig_loss.update_layout(
        xaxis_tickformat=".1%",
    )

    st.plotly_chart(
        fig_loss,
        use_container_width=True,
    )

    # ========================================================
    # VaR comparison
    # ========================================================

    st.subheader(
        "Stressed VaR"
    )

    var_df = results.sort_values(
        "Stressed VaR",
        ascending=True,
    )

    fig_var = px.bar(
        var_df,
        x="Stressed VaR",
        y="Scenario",
        color="Scenario Type",
        orientation="h",
        title="Stressed VaR by Scenario",
    )

    fig_var.update_layout(
        xaxis_tickformat=".1%",
    )

    st.plotly_chart(
        fig_var,
        use_container_width=True,
    )

    # ========================================================
    # Expected Shortfall
    # ========================================================

    st.subheader(
        "Stressed Expected Shortfall"
    )

    es_df = results.sort_values(
        "Stressed Expected Shortfall",
        ascending=True,
    )

    fig_es = px.bar(
        es_df,
        x="Stressed Expected Shortfall",
        y="Scenario",
        color="Scenario Type",
        orientation="h",
        title="Stressed Expected Shortfall",
    )

    fig_es.update_layout(
        xaxis_tickformat=".1%",
    )

    st.plotly_chart(
        fig_es,
        use_container_width=True,
    )

    # ========================================================
    # Historical vs Hypothetical
    # ========================================================

    st.subheader(
        "Historical vs Hypothetical Stress"
    )

    comparison = (
        results
        .groupby("Scenario Type")[
            [
                "Stressed Portfolio Loss",
                "Stressed VaR",
                "Stressed Expected Shortfall",
                "Worst-Case Loss",
            ]
        ]
        .max()
        .reset_index()
    )

    st.dataframe(
        comparison,
        use_container_width=True,
    )

    # ========================================================
    # Detailed scenario selector
    # ========================================================

    st.subheader(
        "Scenario Details"
    )

    selected_scenario = st.selectbox(
        "Select Scenario",
        results["Scenario"].tolist(),
    )

    selected = results[
        results["Scenario"]
        == selected_scenario
    ]

    if not selected.empty:

        row = selected.iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Portfolio Loss",
                f"{row['Stressed Portfolio Loss']:.2%}",
            )

        with c2:
            st.metric(
                "Stressed VaR",
                f"{row['Stressed VaR']:.2%}",
            )

        with c3:
            st.metric(
                "Stressed ES",
                f"{row['Stressed Expected Shortfall']:.2%}",
            )

        with c4:
            st.metric(
                "Worst Loss",
                f"{row['Worst-Case Loss']:.2%}",
            )