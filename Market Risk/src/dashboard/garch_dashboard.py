"""
GARCH Dashboard Components
Phase 6 - Quantitative Portfolio Risk Management
"""

from pathlib import Path

import pandas as pd
import streamlit as st


def load_garch_data(project_root: Path):
    """
    Load Phase 6 GARCH output files.
    """

    processed_dir = (
        project_root
        / "data"
        / "processed"
    )

    volatility_file = (
        processed_dir
        / "garch_volatility.csv"
    )

    scaled_returns_file = (
        processed_dir
        / "garch_scaled_returns.csv"
    )

    var_file = (
        processed_dir
        / "garch_var.csv"
    )

    missing_files = []

    for file in [
        volatility_file,
        scaled_returns_file,
        var_file,
    ]:
        if not file.exists():
            missing_files.append(str(file))

    if missing_files:
        raise FileNotFoundError(
            "Missing GARCH output files:\n"
            + "\n".join(missing_files)
        )

    volatility_df = pd.read_csv(
        volatility_file,
        index_col=0,
        parse_dates=True,
    )

    scaled_returns_df = pd.read_csv(
        scaled_returns_file,
        index_col=0,
        parse_dates=True,
    )

    var_df = pd.read_csv(
        var_file
    )

    return (
        volatility_df,
        scaled_returns_df,
        var_df,
    )


def render_garch_dashboard(
    project_root: Path,
):
    """
    Render the complete GARCH dashboard.
    """

    st.header(
        "Phase 6 — GARCH Volatility Scaling"
    )

    # ========================================================
    # Load data
    # ========================================================

    try:
        (
            volatility_df,
            scaled_returns_df,
            var_df,
        ) = load_garch_data(
            project_root
        )

    except FileNotFoundError as error:

        st.error(str(error))

        st.info(
            "Run notebooks/phase_6.ipynb first "
            "to generate the GARCH output files."
        )

        return

    # ========================================================
    # Latest values
    # ========================================================

    latest_volatility = (
        volatility_df[
            "Conditional Volatility"
        ].dropna().iloc[-1]
    )

    latest_forecast = (
        var_df[
            "1-Day Forecast Volatility"
        ].iloc[0]
    )

    # ========================================================
    # VaR selection
    # ========================================================

    confidence = st.selectbox(
        "VaR Confidence Level",
        [90, 95, 99],
        index=1,
    )

    confidence_decimal = confidence / 100

    selected_var = var_df.loc[
        var_df["Confidence"]
        == confidence_decimal,
        "GARCH Scaled VaR",
    ]

    if selected_var.empty:
        st.warning(
            "Selected VaR confidence level "
            "was not found."
        )
        return

    selected_var = selected_var.iloc[0]

    # ========================================================
    # KPI cards
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Latest GARCH Volatility",
            f"{latest_volatility:.2%}",
        )

    with col2:
        st.metric(
            "1-Day Forecast Volatility",
            f"{latest_forecast:.2%}",
        )

    with col3:
        st.metric(
            f"GARCH VaR ({confidence}%)",
            f"{selected_var:.2%}",
        )

    st.divider()

    # ========================================================
    # Conditional volatility chart
    # ========================================================

    st.subheader(
        "GARCH Conditional Volatility"
    )

    st.line_chart(
        volatility_df[
            "Conditional Volatility"
        ]
    )

    # ========================================================
    # Forecast volatility
    # ========================================================

    st.subheader(
        "GARCH 1-Day Forecast Volatility"
    )

    forecast_chart = volatility_df[
        ["Conditional Volatility"]
    ].copy()

    forecast_chart[
        "1-Day Forecast"
    ] = latest_forecast

    st.line_chart(
        forecast_chart
    )

    # ========================================================
    # VaR comparison
    # ========================================================

    st.subheader(
        "Historical VaR vs GARCH-Scaled VaR"
    )

    var_chart = var_df.copy()

    var_chart["Confidence"] = (
        var_chart["Confidence"]
        .astype(str)
    )

    var_chart = var_chart.set_index(
        "Confidence"
    )

    var_chart = var_chart[
        [
            "Historical VaR",
            "GARCH Scaled VaR",
        ]
    ]

    st.bar_chart(
        var_chart
    )

    # ========================================================
    # Standardized residuals
    # ========================================================

    st.subheader(
        "GARCH Standardized Residuals"
    )

    residual_chart = (
        volatility_df[
            "Standardized Residual"
        ]
    )

    st.line_chart(
        residual_chart
    )

    # ========================================================
    # Volatility clustering
    # ========================================================

    st.subheader(
        "Volatility Clustering"
    )

    clustering_df = pd.DataFrame({
        "Absolute Portfolio Returns":
            scaled_returns_df[
                "Portfolio Return"
            ].abs(),

        "GARCH Conditional Volatility":
            scaled_returns_df[
                "Conditional Volatility"
            ],
    })

    st.line_chart(
        clustering_df
    )

    # ========================================================
    # Scaled returns
    # ========================================================

    st.subheader(
        "GARCH-Scaled Historical Returns"
    )

    st.dataframe(
        scaled_returns_df.tail(100),
        use_container_width=True,
    )

    # ========================================================
    # VaR table
    # ========================================================

    st.subheader(
        "GARCH VaR Summary"
    )

    display_var = var_df.copy()

    display_var[
        "Historical VaR"
    ] *= 100

    display_var[
        "GARCH Scaled VaR"
    ] *= 100

    display_var[
        "1-Day Forecast Volatility"
    ] *= 100

    st.dataframe(
        display_var,
        use_container_width=True,
    )