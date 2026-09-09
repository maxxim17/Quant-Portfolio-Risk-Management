from __future__ import annotations

import pandas as pd


def validate_price_data(
    prices: pd.DataFrame,
) -> None:

    if prices.empty:
        raise ValueError(
            "Price dataframe is empty."
        )

    if prices.columns.duplicated().any():
        duplicates = prices.columns[
            prices.columns.duplicated()
        ].tolist()

        raise ValueError(
            f"Duplicate tickers found: {duplicates}"
        )

    if not prices.index.is_monotonic_increasing:
        raise ValueError(
            "Price index must be sorted by date."
        )

    if prices.isna().all().any():
        invalid = prices.columns[
            prices.isna().all()
        ].tolist()

        raise ValueError(
            f"No valid observations for: {invalid}"
        )