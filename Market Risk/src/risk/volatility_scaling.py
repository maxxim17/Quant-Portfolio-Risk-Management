"""
Volatility scaling for historical returns.

Phase 5.

Historical returns are rescaled so that their
volatility matches the current EWMA volatility.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


MIN_VOLATILITY = 1e-12


def scale_returns(
    returns: pd.Series,
    historical_volatility: pd.Series,
    current_volatility: float,
    minimum_volatility: float = MIN_VOLATILITY,
) -> pd.Series:
    """
    Rescale historical returns to current volatility.

    Formula:

        r_scaled =
            r *
            sigma_current /
            sigma_historical
    """

    if not isinstance(returns, pd.Series):
        returns = pd.Series(returns)

    if not isinstance(
        historical_volatility,
        pd.Series,
    ):
        historical_volatility = pd.Series(
            historical_volatility,
            index=returns.index,
        )

    returns = pd.to_numeric(
        returns,
        errors="coerce",
    )

    historical_volatility = pd.to_numeric(
        historical_volatility,
        errors="coerce",
    )

    aligned = pd.concat(
        [
            returns.rename("returns"),
            historical_volatility.rename("volatility"),
        ],
        axis=1,
    ).dropna()

    if aligned.empty:
        raise ValueError(
            "No overlapping valid returns and volatility."
        )

    if not np.isfinite(current_volatility):
        raise ValueError(
            "Current volatility must be finite."
        )

    safe_volatility = aligned[
        "volatility"
    ].clip(
        lower=minimum_volatility
    )

    scaled_returns = (
        aligned["returns"]
        * current_volatility
        / safe_volatility
    )

    scaled_returns.name = (
        "EWMA Scaled Return"
    )

    return scaled_returns