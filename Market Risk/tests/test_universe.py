import pandas as pd

from src.data.universe import search_stocks


def sample_universe():

    return pd.DataFrame(
        {
            "ticker": [
                "AAPL",
                "MSFT",
                "NVDA",
            ],
            "name": [
                "Apple Inc.",
                "Microsoft Corporation",
                "NVIDIA Corporation",
            ],
            "exchange": [
                "NASDAQ",
                "NASDAQ",
                "NASDAQ",
            ],
            "asset_type": [
                "Equity",
                "Equity",
                "Equity",
            ],
            "status": [
                "Active",
                "Active",
                "Active",
            ],
        }
    )


def test_search_by_ticker():

    universe = sample_universe()

    result = search_stocks(
        universe,
        "NVDA",
    )

    assert len(result) == 1
    assert result.iloc[0]["ticker"] == "NVDA"


def test_search_by_company_name():

    universe = sample_universe()

    result = search_stocks(
        universe,
        "Microsoft",
    )

    assert len(result) == 1
    assert result.iloc[0]["ticker"] == "MSFT"


def test_empty_search_returns_all():

    universe = sample_universe()

    result = search_stocks(
        universe,
        "",
    )

    assert len(result) == 3