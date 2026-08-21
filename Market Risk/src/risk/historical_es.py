"""
Historical Expected Shortfall engine.

Expected Shortfall measures the average loss
conditional on losses being beyond the VaR threshold.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .historical_var import (
    VALID_CONFIDENCE_LEVELS,
    VALID_WINDOWS,
    validate_var_inputs,
)


def calculate_historical_es(
    returns: pd.Series,
    confidence_level: float = 0.95,
    window: int = 250,
) -> float:
    """
    Calculate Historical Expected Shortfall.

    ES is the average historical loss beyond
    the Historical VaR threshold.

    Parameters
    ----------
    returns:
        Portfolio return series.

    confidence_level:
        Confidence level, e.g. 0.95.

    window:
        Historical lookback window.

    Returns
    -------
    float
        Historical Expected Shortfall as a decimal.
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

    tail_losses = losses[losses >= var]

    if tail_losses.empty:
        return float(var)

    es = tail_losses.mean()

    return float(es)


def calculate_es_table(
    returns: pd.Series,
) -> pd.DataFrame:
    """
    Calculate Expected Shortfall across
    all configured windows and confidence levels.
    """

    results: list[dict[str, float | int]] = []

    for window in VALID_WINDOWS:

        if len(returns) < window:
            continue

        for confidence in VALID_CONFIDENCE_LEVELS:

            es = calculate_historical_es(
                returns=returns,
                confidence_level=confidence,
                window=window,
            )

            results.append(
                {
                    "Window": window,
                    "Confidence": confidence,
                    "Expected Shortfall": es,
                }
            )

    result = pd.DataFrame(results)

    if result.empty:
        raise ValueError(
            "No Expected Shortfall results could be calculated."
        )

    return result