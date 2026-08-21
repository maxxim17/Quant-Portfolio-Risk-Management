"""
Historical Simulation Value-at-Risk engine.

This module implements:

1. Historical loss calculation
2. Historical Simulation VaR
3. Monetary VaR
4. VaR + Expected Shortfall summary table
5. Rolling Historical VaR

Phase 4 model:
- Windows: 250, 500, 750 trading days
- Confidence levels: 95%, 99%, 99.5%

The model is non-parametric and does not assume a normal
distribution for portfolio returns.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd


VALID_WINDOWS: Final[tuple[int, ...]] = (
    250,
    500,
    750,
)

VALID_CONFIDENCE_LEVELS: Final[tuple[float, ...]] = (
    0.95,
    0.99,
    0.995,
)


def validate_returns(returns: pd.Series) -> None:
    """
    Validate a portfolio return series.

    Parameters
    ----------
    returns:
        Portfolio return series.

    Raises
    ------
    TypeError
        If returns is not a pandas Series.
    ValueError
        If the series is empty, contains NaN/infinite values,
        or has an invalid index.
    """

    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series.")

    if returns.empty:
        raise ValueError("Returns series is empty.")

    if returns.isna().any():
        raise ValueError("Returns contain NaN values.")

    if not np.isfinite(returns.to_numpy()).all():
        raise ValueError("Returns contain infinite values.")

    if returns.index.has_duplicates:
        raise ValueError("Returns index contains duplicate dates.")

    if isinstance(returns.index, pd.DatetimeIndex):
        if not returns.index.is_monotonic_increasing:
            raise ValueError("Returns dates must be sorted ascending.")


def validate_var_inputs(
    returns: pd.Series,
    window: int,
    confidence_level: float,
) -> None:
    """
    Validate inputs required for Historical Simulation VaR.
    """

    validate_returns(returns)

    if window not in VALID_WINDOWS:
        raise ValueError(
            f"Invalid window: {window}. "
            f"Expected one of {VALID_WINDOWS}."
        )

    if confidence_level not in VALID_CONFIDENCE_LEVELS:
        raise ValueError(
            f"Invalid confidence level: {confidence_level}. "
            f"Expected one of {VALID_CONFIDENCE_LEVELS}."
        )

    if len(returns) < window:
        raise ValueError(
            f"At least {window} observations are required. "
            f"Received {len(returns)}."
        )


def calculate_historical_losses(
    returns: pd.Series,
) -> pd.Series:
    """
    Convert portfolio returns into historical losses.

    Loss = -Return

    Examples
    --------
    +2% return -> -2% loss
    -2% return -> +2% loss
    """

    validate_returns(returns)

    losses = -returns.copy()
    losses.name = "Loss"

    return losses


def calculate_historical_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
    window: int = 250,
) -> float:
    """
    Calculate one-day Historical Simulation VaR.

    Parameters
    ----------
    returns:
        Historical portfolio returns.

    confidence_level:
        VaR confidence level.

    window:
        Historical lookback window.

    Returns
    -------
    float
        Percentage VaR expressed as a decimal.

    Example
    -------
    0.025 = 2.5% VaR
    """

    validate_var_inputs(
        returns=returns,
        window=window,
        confidence_level=confidence_level,
    )

    historical_returns = returns.iloc[-window:]

    losses = -historical_returns

    var = np.quantile(
        losses.to_numpy(),
        confidence_level,
    )

    return float(var)


def calculate_monetary_var(
    var_percentage: float,
    portfolio_value: float,
) -> float:
    """
    Convert percentage VaR into monetary VaR.

    Monetary VaR = Percentage VaR × Portfolio Value
    """

    if not np.isfinite(var_percentage):
        raise ValueError("var_percentage must be finite.")

    if not np.isfinite(portfolio_value):
        raise ValueError("portfolio_value must be finite.")

    if var_percentage < 0:
        raise ValueError("VaR percentage cannot be negative.")

    if portfolio_value <= 0:
        raise ValueError("Portfolio value must be positive.")

    return float(var_percentage * portfolio_value)


def var_column_name(
    confidence: float,
    window: int,
) -> str:
    """
    Generate a consistent rolling VaR column name.
    """

    labels = {
        0.95: "95",
        0.99: "99",
        0.995: "99_5",
    }

    try:
        confidence_label = labels[confidence]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported confidence level: {confidence}"
        ) from exc

    return f"VaR_{confidence_label}_{window}D"


def calculate_var_es_table(
    returns: pd.Series,
    portfolio_value: float | None = None,
) -> pd.DataFrame:
    """
    Calculate Historical VaR and Expected Shortfall
    for every configured window/confidence combination.

    Parameters
    ----------
    returns:
        Portfolio return series.

    portfolio_value:
        Optional current portfolio value.

    Returns
    -------
    pandas.DataFrame
        One row for each window/confidence combination.
    """

    validate_returns(returns)

    from .historical_es import calculate_historical_es

    results: list[dict[str, float | int]] = []

    for window in VALID_WINDOWS:

        if len(returns) < window:
            continue

        for confidence in VALID_CONFIDENCE_LEVELS:

            var = calculate_historical_var(
                returns=returns,
                confidence_level=confidence,
                window=window,
            )

            es = calculate_historical_es(
                returns=returns,
                confidence_level=confidence,
                window=window,
            )

            row: dict[str, float | int] = {
                "Window": window,
                "Confidence": confidence,
                "VaR": var,
                "Expected Shortfall": es,
            }

            if portfolio_value is not None:
                row["VaR Amount"] = calculate_monetary_var(
                    var_percentage=var,
                    portfolio_value=portfolio_value,
                )

                row["ES Amount"] = calculate_monetary_var(
                    var_percentage=es,
                    portfolio_value=portfolio_value,
                )

            results.append(row)

    result = pd.DataFrame(results)

    if result.empty:
        raise ValueError(
            "No VaR/ES results could be calculated. "
            "Insufficient observations."
        )

    # Mathematical validation:
    # ES should be >= VaR.
    invalid_es = (
        result["Expected Shortfall"] < result["VaR"]
    )

    if invalid_es.any():
        raise ValueError(
            "Expected Shortfall must be greater than "
            "or equal to VaR."
        )

    return result


def calculate_rolling_var(
    returns: pd.Series,
    window: int = 250,
    confidence_level: float = 0.95,
) -> pd.Series:
    """
    Calculate rolling Historical Simulation VaR.
    """

    validate_var_inputs(
        returns=returns,
        window=window,
        confidence_level=confidence_level,
    )

    losses = -returns

    rolling_var = (
        losses
        .rolling(
            window=window,
            min_periods=window,
        )
        .quantile(confidence_level)
    )

    rolling_var.name = var_column_name(
        confidence=confidence_level,
        window=window,
    )

    return rolling_var


def calculate_all_rolling_var(
    returns: pd.Series,
) -> pd.DataFrame:
    """
    Calculate rolling Historical VaR for all
    configured windows and confidence levels.

    Output columns:

    VaR_95_250D
    VaR_99_250D
    VaR_99_5_250D
    VaR_95_500D
    ...
    """

    validate_returns(returns)

    results = pd.DataFrame(index=returns.index)

    for window in VALID_WINDOWS:

        if len(returns) < window:
            continue

        for confidence in VALID_CONFIDENCE_LEVELS:

            column = var_column_name(
                confidence=confidence,
                window=window,
            )

            results[column] = (
                (-returns)
                .rolling(
                    window=window,
                    min_periods=window,
                )
                .quantile(confidence)
            )

    return results