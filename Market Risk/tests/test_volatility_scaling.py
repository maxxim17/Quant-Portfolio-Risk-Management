import numpy as np
import pandas as pd
import pytest

from src.risk.volatility_scaling import (
    scale_returns,
)


def test_scaling():

    returns = pd.Series(
        [-0.01, 0.02, -0.03]
    )

    volatility = pd.Series(
        [0.01, 0.02, 0.03]
    )

    current_volatility = 0.02

    scaled = scale_returns(
        returns,
        volatility,
        current_volatility,
    )

    expected = (
        returns
        * current_volatility
        / volatility
    )

    np.testing.assert_allclose(
        scaled.values,
        expected.values,
    )


def test_zero_volatility_is_handled():

    returns = pd.Series(
        [-0.01, 0.02]
    )

    volatility = pd.Series(
        [0.0, 0.02]
    )

    scaled = scale_returns(
        returns,
        volatility,
        0.02,
    )

    assert np.isfinite(
        scaled
    ).all()