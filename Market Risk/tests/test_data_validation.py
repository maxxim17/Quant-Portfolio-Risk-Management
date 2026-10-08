import pandas as pd

from src.validation.data_validation import (
    check_weights,
    check_returns_alignment,
)


def test_weights_sum_to_one():

    weights = {
        "AAPL": 0.25,
        "MSFT": 0.25,
        "NVDA": 0.25,
        "JPM": 0.25,
    }

    result = check_weights(weights)

    assert result["passed"]


def test_returns_have_no_missing_values():

    df = pd.DataFrame({
        "Portfolio Return": [
            0.01,
            -0.02,
            0.005,
        ]
    })

    result = check_returns_alignment(df)

    assert result["passed"]