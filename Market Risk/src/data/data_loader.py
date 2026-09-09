from pathlib import Path

import pandas as pd

from src.data.downloader import download_ticker_history


def load_selected_prices(
    tickers: list[str],
    start: str,
    end: str,
    force_refresh: bool = False,
) -> pd.DataFrame:

    price_series = []

    for ticker in tickers:

        data = download_ticker_history(
            ticker=ticker,
            start=start,
            end=end,
            force_refresh=force_refresh,
        )

        if "Close" not in data.columns:
            raise ValueError(
                f"Close price unavailable for {ticker}"
            )

        series = data["Close"].rename(
            ticker
        )

        price_series.append(series)

    prices = pd.concat(
        price_series,
        axis=1,
    )

    prices.index.name = "Date"

    return prices.sort_index()