import numpy as np
import pandas as pd
import pytest

from src.risk.ewma import (
    calculate_ewma_variance,
    calculate_ewma_volatility,
)


def deterministic_returns(n=100):

    dates = pd.date_range(
        "2020-01-01",
        periods=n,
        freq="B",
    )

    return pd.Series(
        np.linspace(
            -0.02,
            0.02,
            n,
        ),
        index=dates,
    )


def test_ewma_variance_length():

    returns = deterministic_returns()

    variance = calculate_ewma_variance(
        returns,
        lmbda=0.94,
    )

    assert len(variance) == len(returns)


def test_ewma_variance_non_negative():

    returns = deterministic_returns()

    variance = calculate_ewma_variance(
        returns,
    )

    assert (variance >= 0).all()


def test_ewma_volatility():

    returns = deterministic_returns()

    variance = calculate_ewma_variance(
        returns,
    )

    volatility = calculate_ewma_volatility(
        returns,
    )

    np.testing.assert_allclose(
        volatility.values,
        np.sqrt(variance.values),
    )


def test_invalid_lambda():

    returns = deterministic_returns()

    with pytest.raises(ValueError):

        calculate_ewma_variance(
            returns,
            lmbda=1.5,
        )