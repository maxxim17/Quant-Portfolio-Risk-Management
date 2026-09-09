from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


CACHE_DIR = Path("data/raw/cache")


def _safe_filename(ticker: str) -> str:
    return (
        ticker
        .replace("/", "_")
        .replace("\\", "_")
        .replace(".", "_")
        .upper()
    )


def _cache_path(ticker: str) -> Path:
    return CACHE_DIR / f"{_safe_filename(ticker)}.csv"


def download_ticker_history(
    ticker: str,
    start: str,
    end: str,
    force_refresh: bool = False,
) -> pd.DataFrame:

    ticker = ticker.upper().strip()

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache_path = _cache_path(ticker)

    if cache_path.exists() and not force_refresh:

        cached = pd.read_csv(
            cache_path,
            index_col=0,
            parse_dates=True,
        )

        return cached

    data = yf.download(
        ticker,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if data.empty:
        raise ValueError(
            f"No historical data returned for {ticker}"
        )

    # yfinance may return a MultiIndex even for one ticker.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.index.name = "Date"

    data.to_csv(cache_path)

    return data


def download_selected_stocks(
    tickers: list[str],
    start: str,
    end: str,
    force_refresh: bool = False,
) -> dict[str, pd.DataFrame]:

    results: dict[str, pd.DataFrame] = {}

    errors: dict[str, str] = {}

    for ticker in tickers:

        try:

            results[ticker] = download_ticker_history(
                ticker=ticker,
                start=start,
                end=end,
                force_refresh=force_refresh,
            )

        except Exception as exc:

            errors[ticker] = str(exc)

    if errors:
        error_text = "\n".join(
            f"{ticker}: {error}"
            for ticker, error in errors.items()
        )

        print(
            "Some tickers failed:\n"
            + error_text
        )

    if not results:
        raise ValueError(
            "No selected tickers returned valid data."
        )

    return results