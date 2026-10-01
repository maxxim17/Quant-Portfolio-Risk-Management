"""
Phase 6 - GARCH Volatility Scaling

Implements:

1. GARCH(1,1) model fitting
2. Conditional volatility estimation
3. 1-day-ahead volatility forecasting
4. Standardized residual calculation
5. GARCH volatility scaling
6. GARCH-scaled Historical VaR

Returns are assumed to be decimal returns.

Example:
    0.01 = +1%
    -0.02 = -2%
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from arch import arch_model


# ============================================================
# Result container
# ============================================================

@dataclass
class GARCHResult:
    """Container for GARCH analysis results."""

    model: object
    conditional_volatility: pd.Series
    forecast_volatility: float
    standardized_residuals: pd.Series
    scaled_returns: pd.Series
    scaling_factor: pd.Series
    var_90: float
    var_95: float
    var_99: float


# ============================================================
# Validation
# ============================================================

def validate_returns(returns: pd.Series) -> pd.Series:
    """
    Validate and clean portfolio returns.

    Parameters
    ----------
    returns : pd.Series
        Portfolio daily returns.

    Returns
    -------
    pd.Series
        Cleaned returns.
    """

    if returns is None:
        raise ValueError("Returns cannot be None.")

    if not isinstance(returns, pd.Series):
        returns = pd.Series(returns)

    returns = returns.copy()

    returns = pd.to_numeric(
        returns,
        errors="coerce"
    )

    returns = returns.replace(
        [np.inf, -np.inf],
        np.nan
    )

    returns = returns.dropna()

    if returns.empty:
        raise ValueError("Returns series is empty.")

    if len(returns) < 100:
        raise ValueError(
            "At least 100 observations are recommended "
            "for GARCH estimation."
        )

    if returns.std() == 0:
        raise ValueError(
            "Returns have zero variance."
        )

    return returns


# ============================================================
# Fit GARCH(1,1)
# ============================================================

def fit_garch_model(
    returns: pd.Series,
    p: int = 1,
    q: int = 1,
    mean: str = "Constant",
    dist: str = "normal",
):
    """
    Fit a GARCH(p,q) model.

    The returns are multiplied by 100 before fitting.
    This puts the model input in percentage units.

    Parameters
    ----------
    returns : pd.Series
        Decimal daily returns.

    p : int
        ARCH order.

    q : int
        GARCH order.

    mean : str
        Mean model.

    dist : str
        Error distribution.

    Returns
    -------
    ARCHModelResult
        Fitted GARCH model.
    """

    returns = validate_returns(returns)

    # Convert decimal returns to percentage returns.
    # Example:
    # 0.01 -> 1.0
    scaled_returns = returns * 100.0

    model = arch_model(
        scaled_returns,
        mean=mean,
        vol="GARCH",
        p=p,
        q=q,
        dist=dist,
        rescale=False,
    )

    result = model.fit(
        disp="off"
    )

    return result


# ============================================================
# Conditional volatility
# ============================================================

def get_conditional_volatility(
    model_result,
    index: pd.Index | None = None,
) -> pd.Series:
    """
    Extract conditional volatility from fitted GARCH model.

    Returns volatility in decimal return units.

    Example:
        0.015 = 1.5%
    """

    volatility = model_result.conditional_volatility.copy()

    # Model was fitted using percentage returns,
    # therefore divide by 100 to return to decimal units.
    volatility = volatility / 100.0

    if index is not None:
        volatility.index = index

    volatility.name = "conditional_volatility"

    return volatility


# ============================================================
# One-day-ahead forecast
# ============================================================

def forecast_garch_volatility(
    model_result,
) -> float:
    """
    Forecast one-day-ahead volatility.

    Returns
    -------
    float
        Forecast volatility in decimal return units.

    Example:
        0.018 = 1.8%
    """

    forecast = model_result.forecast(
        horizon=1,
        method="analytic",
        reindex=False,
    )

    forecast_variance = forecast.variance.iloc[-1, 0]

    forecast_volatility = np.sqrt(
        forecast_variance
    )

    # Convert percentage volatility back to decimal.
    forecast_volatility /= 100.0

    return float(forecast_volatility)


# ============================================================
# Standardized residuals
# ============================================================

def get_standardized_residuals(
    model_result,
    index: pd.Index | None = None,
) -> pd.Series:
    """
    Calculate standardized GARCH residuals.

    z_t = epsilon_t / sigma_t
    """

    residuals = model_result.std_resid.copy()

    if index is not None:
        residuals.index = index

    residuals = residuals.replace(
        [np.inf, -np.inf],
        np.nan
    )

    residuals.name = "standardized_residual"

    return residuals


# ============================================================
# GARCH volatility scaling
# ============================================================

def scale_returns_garch(
    returns: pd.Series,
    conditional_volatility: pd.Series,
    forecast_volatility: float,
) -> tuple[pd.Series, pd.Series]:
    """
    Scale historical returns using GARCH volatility.

    Scaling formula:

        scaled_return_t =
            return_t *
            (forecast_volatility / conditional_volatility_t)

    This transforms historical returns toward the current
    forecast volatility regime.

    Parameters
    ----------
    returns : pd.Series
        Historical portfolio returns.

    conditional_volatility : pd.Series
        GARCH conditional volatility.

    forecast_volatility : float
        Current one-day-ahead forecast volatility.

    Returns
    -------
    scaled_returns : pd.Series
    scaling_factor : pd.Series
    """

    returns = validate_returns(returns)

    conditional_volatility = conditional_volatility.reindex(
        returns.index
    )

    # Avoid division by zero.
    safe_volatility = conditional_volatility.replace(
        0,
        np.nan
    )

    scaling_factor = (
        forecast_volatility /
        safe_volatility
    )

    scaled_returns = (
        returns *
        scaling_factor
    )

    scaled_returns = scaled_returns.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    scaling_factor = scaling_factor.reindex(
        scaled_returns.index
    )

    scaled_returns.name = "garch_scaled_return"
    scaling_factor.name = "garch_scaling_factor"

    return scaled_returns, scaling_factor


# ============================================================
# Historical VaR
# ============================================================

def calculate_historical_var(
    returns: pd.Series,
    confidence: float,
) -> float:
    """
    Calculate one-day Historical VaR.

    VaR is returned as a positive loss number.

    Example:
        0.025 = 2.5% VaR
    """

    if not 0 < confidence < 1:
        raise ValueError(
            "Confidence must be between 0 and 1."
        )

    returns = validate_returns(returns)

    quantile = returns.quantile(
        1.0 - confidence
    )

    # Convert negative return quantile into
    # positive VaR.
    var = -float(quantile)

    return max(var, 0.0)


# ============================================================
# Complete GARCH analysis
# ============================================================

def run_garch_analysis(
    returns: pd.Series,
) -> GARCHResult:
    """
    Run the complete Phase 6 GARCH pipeline.

    Returns
    -------
    GARCHResult
    """

    returns = validate_returns(returns)

    # --------------------------------------------------------
    # 1. Fit GARCH(1,1)
    # --------------------------------------------------------

    model_result = fit_garch_model(
        returns,
        p=1,
        q=1,
    )

    # --------------------------------------------------------
    # 2. Conditional volatility
    # --------------------------------------------------------

    conditional_volatility = (
        get_conditional_volatility(
            model_result,
            index=returns.index,
        )
    )

    # --------------------------------------------------------
    # 3. Forecast volatility
    # --------------------------------------------------------

    forecast_volatility = (
        forecast_garch_volatility(
            model_result
        )
    )

    # --------------------------------------------------------
    # 4. Standardized residuals
    # --------------------------------------------------------

    standardized_residuals = (
        get_standardized_residuals(
            model_result,
            index=returns.index,
        )
    )

    # --------------------------------------------------------
    # 5. GARCH scaling
    # --------------------------------------------------------

    scaled_returns, scaling_factor = (
        scale_returns_garch(
            returns,
            conditional_volatility,
            forecast_volatility,
        )
    )

    # --------------------------------------------------------
    # 6. GARCH-scaled VaR
    # --------------------------------------------------------

    var_90 = calculate_historical_var(
        scaled_returns,
        0.90,
    )

    var_95 = calculate_historical_var(
        scaled_returns,
        0.95,
    )

    var_99 = calculate_historical_var(
        scaled_returns,
        0.99,
    )

    return GARCHResult(
        model=model_result,
        conditional_volatility=conditional_volatility,
        forecast_volatility=forecast_volatility,
        standardized_residuals=standardized_residuals,
        scaled_returns=scaled_returns,
        scaling_factor=scaling_factor,
        var_90=var_90,
        var_95=var_95,
        var_99=var_99,
    )