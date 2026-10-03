from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


def load_gjr_volatility():
    file = (
        PROCESSED_DIR
        / "gjr_garch_volatility.csv"
    )

    return pd.read_csv(
        file,
        parse_dates=["Date"],
    )


def load_gjr_scaled_returns():
    file = (
        PROCESSED_DIR
        / "gjr_garch_scaled_returns.csv"
    )

    return pd.read_csv(
        file,
        parse_dates=["Date"],
    )


def load_gjr_var():
    file = (
        PROCESSED_DIR
        / "gjr_garch_var.csv"
    )

    return pd.read_csv(file)


def render_gjr_garch_dashboard():
    st.header(
        "Phase 7 — GJR-GARCH Volatility Scaling"
    )

    # -------------------------------------------------------------
    # Load data
    # -------------------------------------------------------------

    volatility = load_gjr_volatility()
    scaled_returns = load_gjr_scaled_returns()
    var = load_gjr_var()

    # -------------------------------------------------------------
    # Model metrics
    # -------------------------------------------------------------

    latest_row = var.iloc[0]

    gamma = latest_row["Gamma"]
    forecast_volatility = latest_row[
        "Forecast Volatility"
    ]

    st.subheader("GJR-GARCH Model Parameters")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Alpha",
        f"{latest_row['Alpha']:.6f}",
    )

    col2.metric(
        "Gamma / Leverage",
        f"{gamma:.6f}",
    )

    col3.metric(
        "Beta",
        f"{latest_row['Beta']:.6f}",
    )

    col4.metric(
        "Forecast Volatility",
        f"{forecast_volatility:.4%}",
    )

    # -------------------------------------------------------------
    # GJR-GARCH volatility
    # -------------------------------------------------------------

    st.subheader(
        "GJR-GARCH Conditional Volatility"
    )

    st.line_chart(
        volatility.set_index("Date")[
            "GJR-GARCH Conditional Volatility"
        ]
    )

    # -------------------------------------------------------------
    # Standardized residuals
    # -------------------------------------------------------------

    st.subheader(
        "Standardized Residuals"
    )

    st.line_chart(
        volatility.set_index("Date")[
            "Standardized Residual"
        ]
    )

    # -------------------------------------------------------------
    # Leverage effect
    # -------------------------------------------------------------

    st.subheader(
        "Leverage Effect"
    )

    st.write(
        f"Estimated Gamma (γ): **{gamma:.6f}**"
    )

    if gamma > 0:
        st.info(
            "The estimated gamma parameter is positive, "
            "so the fitted GJR-GARCH model assigns an "
            "additional variance contribution to negative shocks."
        )
    else:
        st.info(
            "The estimated gamma parameter is non-positive "
            "in this fitted model."
        )

    # -------------------------------------------------------------
    # Scaled returns
    # -------------------------------------------------------------

    st.subheader(
        "GJR-GARCH Scaled Returns"
    )

    st.line_chart(
        scaled_returns.set_index("Date")[
            "GJR-GARCH Scaled Return"
        ]
    )

    # -------------------------------------------------------------
    # VaR
    # -------------------------------------------------------------

    st.subheader(
        "GJR-GARCH Scaled Historical VaR"
    )

    display_var = var[
        [
            "Confidence",
            "VaR",
        ]
    ].copy()

    st.dataframe(
        display_var,
        use_container_width=True,
    )

    st.bar_chart(
        display_var.set_index("Confidence")[
            "VaR"
        ]
    )