import numpy as np
import pandas as pd
import pytest
import pytest

from src.risk import calculate_historical_losses, calculate_historical_var


def deterministic_returns():
    return pd.Series(np.linspace(-0.05, 0.05, 250))


def test_historical_losses():
    returns = pd.Series(
        [0.01, -0.02, 0.03]
    )

    losses = calculate_historical_losses(returns)

    expected = pd.Series(
        [-0.01, 0.02, -0.03],
        name="Loss",
    )

    pd.testing.assert_series_equal(
        losses,
        expected,
    )




def test_var_requires_enough_observations():
    returns = pd.Series(np.zeros(100))

    with pytest.raises(ValueError):
        calculate_historical_var(
            returns,
     gel=0.95,
            window=250,
        )


def test_invalid_window():
    returns = deterministic_returns()

    with pytest.raises(ValueError):
        calculate_historical_var(
            returns,
            confidence_level=0.95,
            window=100,
        )


def test_invalid_confidence_level():
    returns = deterministic_returns()

    with pytest.raises(ValueError):
        calculate_historical_var(
            returns,
            confidence_level=0.90,
            window=250,
        )


def test_nan_returns_are_rejected():
    returns = deterministic_returns()
    returns.iloc[10] = np.nan

    with pytest.raises(ValueError):
        calculate_historical_var(
            returns,
            confidence_level=0.95,
            window=250,
        )


def test_var_is_non_negative():
    returns = deterministic_returns()

    var = calculate_historical_var(
        returns,
        confidence_level=0.95,
        window=250,
    )

    assert var >= 0


def test_var_increases_with_confidence():
    returns = deterministic_returns()

    var_95 = calculate_historical_var(
        returns,
        confidence_level=0.95,
        window=250,
    )

    var_99 = calculate_historical_var(
        returns,
        confidence_level=0.99,
        window=250,
    )

    var_995 = calculate_historical_var(
        returns,
        confidence_level=0.995,
        window=250,
    )

    assert var_99 >= var_95
    assert var_995 >= var_99