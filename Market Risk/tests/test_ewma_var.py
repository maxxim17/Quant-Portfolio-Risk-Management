import numpy as np
import pandas as pd
import pytest

from src.risk.ewma_var import (
    calculate_ewma_var,
    calculate_ewma_monetary_var,
    calculate_rolling_ewma_var,
)


def create_returns(n=800):

    rng = np.random.default_rng(42)

    dates = pd.date_range(
        "2020-01-01",
        periods=n,
        freq="B",
    )

    return pd.Series(
        rng.normal(
            0,
            0.01,
            n,
        ),
        index=dates,
    )


def test_ewma_var():

    returns = create_returns()

    var = calculate_ewma_var(
        returns,
        confidence_level=0.95,
        window=250,
        lmbda=0.94,
    )

    assert isinstance(
        var,
        float,
    )

    assert var >= 0


def test_monetary_var():

    returns = create_returns()

    var = calculate_ewma_monetary_var(
        returns,
        portfolio_value=1_000_000,
        confidence_level=0.95,
        window=250,
        lmbda=0.94,
    )

    assert var >= 0


def test_rolling_var():

    returns = create_returns()

    var = calculate_rolling_ewma_var(
        returns,
        confidence_level=0.95,
        window=250,
        lmbda=0.94,
    )

    assert var.iloc[:250].isna().all()

    assert var.iloc[250:].notna().all()


def test_insufficient_data():

    returns = create_returns(100)

    with pytest.raises(ValueError):

        calculate_ewma_var(
            returns,
            window=250,
        )