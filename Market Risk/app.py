from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

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