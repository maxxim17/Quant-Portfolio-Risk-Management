"""
EWMA volatility estimation.

Phase 5:
Exponentially Weighted Moving Average volatility.

Model:
    sigma_t^2 =
        lambda * sigma_(t-1)^2
        + (1-lambda) * r_(t-1)^2
"""

from __future__ import annotations

import numpy as np
import pandas as pd


DEFAULT_LAMBDA = 0.94


def validate_returns(returns: pd.Series) -> pd.Series:
    """
    Validate and clean a return series.
    """

    if not isinstance(returns, pd.Series):
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
        raise ValueError("Returns series is empty.")

    return returns.astype(float)


def validate_lambda(lmbda: float) -> None:
    """
    Validate EWMA decay factor.
    """

    if not 0 < lmbda < 1:
        raise ValueError(
            "Lambda must be between 0 and 1."
        )


def calculate_ewma_variance(
    returns: pd.Series,
    lmbda: float = DEFAULT_LAMBDA,
) -> pd.Series:
    """
    Calculate EWMA variance.

    sigma_t^2 =
        lambda * sigma_(t-1)^2
        + (1-lambda) * r_(t-1)^2
    """

    returns = validate_returns(returns)
    validate_lambda(lmbda)

    variance = pd.Series(
        index=returns.index,
        dtype=float,
        name="EWMA Variance",
    )

    # Initial variance
    variance.iloc[0] = returns.var(
        ddof=1
    )

    for i in range(1, len(returns)):

        previous_variance = variance.iloc[i - 1]

        previous_return = returns.iloc[i - 1]

        variance.iloc[i] = (
            lmbda * previous_variance
            + (1 - lmbda)
            * previous_return ** 2
        )

    return variance


def calculate_ewma_volatility(
    returns: pd.Series,
    lmbda: float = DEFAULT_LAMBDA,
    annualize: bool = False,
    trading_days: int = 252,
) -> pd.Series:
    """
    Calculate EWMA volatility.

    Parameters
    ----------
    returns:
        Portfolio return series.

    lmbda:
        EWMA decay factor.

    annualize:
        Convert daily volatility to annualized volatility.

    trading_days:
        Number of trading days per year.
    """

    variance = calculate_ewma_variance(
        returns,
        lmbda=lmbda,
    )

    volatility = np.sqrt(variance)

    volatility.name = "EWMA Volatility"

    if annualize:
        volatility = (
            volatility
            * np.sqrt(trading_days)
        )

        volatility.name = (
            "Annualized EWMA Volatility"
        )

    return volatility