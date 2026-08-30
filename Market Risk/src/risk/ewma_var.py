"""
EWMA volatility-scaled Historical VaR.

Phase 5.

Combines:
    1. EWMA volatility
    2. Historical return distribution
    3. Volatility scaling
    4. Historical VaR
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .ewma import (
    calculate_ewma_volatility,
)
from .volatility_scaling import (
    scale_returns,
)


DEFAULT_LAMBDA = 0.94
DEFAULT_CONFIDENCE_LEVEL = 0.95


VALID_WINDOWS = (
    250,
    500,
    750,
)


def validate_returns(
    returns: pd.Series,
) -> pd.Series:

    if not isinstance(
        returns,
        pd.Series,
    ):
        returns = pd.Series(returns)

    returns = pd.to_numeric(
        returns,
        errors="coerce",
    )

    returns = returns.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    returns = returns.dropna()

    if returns.empty:
        raise ValueError(
            "Returns series is empty."
        )

    return returns.astype(float)


def validate_confidence_level(
    confidence_level: float,
) -> None:

    if not 0 < confidence_level < 1:
        raise ValueError(
            "Confidence level must be between 0 and 1."
        )


def validate_window(
    window: int,
) -> None:

    if window not in VALID_WINDOWS:
        raise ValueError(
            f"Window must be one of {VALID_WINDOWS}."
        )


def calculate_ewma_var(
    returns: pd.Series,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    window: int = 250,
    lmbda: float = DEFAULT_LAMBDA,
) -> float:
    """
    Calculate EWMA volatility-scaled Historical VaR.

    VaR is returned as a positive loss percentage.
    """

    returns = validate_returns(returns)

    validate_confidence_level(
        confidence_level
    )

    validate_window(window)

    if len(returns) < window + 1:
        raise ValueError(
            f"At least {window + 1} "
            "observations are required."
        )

    ewma_volatility = (
        calculate_ewma_volatility(
            returns,
            lmbda=lmbda,
        )
    )

    historical_returns = (
        returns.iloc[-window:]
    )

    historical_volatility = (
        ewma_volatility.iloc[-window:]
    )

    current_volatility = (
        ewma_volatility.iloc[-1]
    )

    scaled_returns = scale_returns(
        historical_returns,
        historical_volatility,
        current_volatility,
    )

    losses = -scaled_returns

    var = np.quantile(
        losses,
        confidence_level,
    )

    return float(var)


def calculate_ewma_monetary_var(
    returns: pd.Series,
    portfolio_value: float,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    window: int = 250,
    lmbda: float = DEFAULT_LAMBDA,
) -> float:
    """
    Calculate EWMA VaR in monetary terms.
    """

    if portfolio_value <= 0:
        raise ValueError(
            "Portfolio value must be positive."
        )

    var = calculate_ewma_var(
        returns=returns,
        confidence_level=confidence_level,
        window=window,
        lmbda=lmbda,
    )

    return float(
        var * portfolio_value
    )


def calculate_rolling_ewma_var(
    returns: pd.Series,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    window: int = 250,
    lmbda: float = DEFAULT_LAMBDA,
) -> pd.Series:
    """
    Calculate rolling EWMA volatility-scaled VaR.

    VaR_t is calculated using the previous
    `window` observations and the EWMA volatility
    available at time t.
    """

    returns = validate_returns(returns)

    validate_confidence_level(
        confidence_level
    )

    validate_window(window)

    ewma_volatility = (
        calculate_ewma_volatility(
            returns,
            lmbda=lmbda,
        )
    )

    var_series = pd.Series(
        index=returns.index,
        dtype=float,
        name="EWMA VaR",
    )

    for i in range(
        window,
        len(returns),
    ):

        historical_returns = (
            returns.iloc[
                i - window:i
            ]
        )

        historical_volatility = (
            ewma_volatility.iloc[
                i - window:i
            ]
        )

        current_volatility = (
            ewma_volatility.iloc[i]
        )

        scaled_returns = scale_returns(
            historical_returns,
            historical_volatility,
            current_volatility,
        )

        losses = -scaled_returns

        var_series.iloc[i] = np.quantile(
            losses,
            confidence_level,
        )

    return var_series