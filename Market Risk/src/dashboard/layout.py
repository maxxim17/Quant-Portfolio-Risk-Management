from __future__ import annotations

import streamlit as st


def render_header():

    st.title(
        "Portfolio Construction & Risk Analytics"
    )

    st.caption(
        "Multi-asset portfolio construction, "
        "Historical VaR, Expected Shortfall, "
        "EWMA volatility scaling and advanced "
        "risk analytics."
    )


def render_selected_stocks(
    universe,
    tickers,
):

    st.subheader(
        "Selected Portfolio"
    )

    selected = universe[
        universe["ticker"].isin(tickers)
    ][
        [
            "ticker",
            "name",
            "exchange",
        ]
    ]

    st.dataframe(
        selected,
        hide_index=True,
        use_container_width=True,
    )