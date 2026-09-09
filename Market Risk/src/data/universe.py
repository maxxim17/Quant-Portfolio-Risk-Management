from __future__ import annotations

from pathlib import Path

import pandas as pd


UNIVERSE_PATH = Path("data/universe/us_equities.csv")


def load_stock_universe(
    path: str | Path = UNIVERSE_PATH,
) -> pd.DataFrame:
    """
    Load the stock universe used by the dashboard.

    Expected columns:
        ticker
        name
        exchange
        asset_type
        status
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Stock universe not found: {path}. "
            "Run scripts/build_universe.py first."
        )

    universe = pd.read_csv(path)

    required_columns = {
        "ticker",
        "name",
        "exchange",
        "asset_type",
        "status",
    }

    missing = required_columns - set(universe.columns)

    if missing:
        raise ValueError(
            f"Universe is missing required columns: {sorted(missing)}"
        )

    universe["ticker"] = (
        universe["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    universe["name"] = (
        universe["name"]
        .astype(str)
        .str.strip()
    )

    universe = universe.drop_duplicates(
        subset="ticker"
    )

    universe = universe.sort_values(
        ["name", "ticker"]
    ).reset_index(drop=True)

    return universe


def search_stocks(
    universe: pd.DataFrame,
    query: str,
) -> pd.DataFrame:
    """
    Search stocks by ticker or company name.
    """

    query = str(query).strip().lower()

    if not query:
        return universe.copy()

    ticker_match = universe["ticker"].str.lower().str.contains(
        query,
        regex=False,
        na=False,
    )

    name_match = universe["name"].str.lower().str.contains(
        query,
        regex=False,
        na=False,
    )

    return universe[
        ticker_match | name_match
    ].copy()