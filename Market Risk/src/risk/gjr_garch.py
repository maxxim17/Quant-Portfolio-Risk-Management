"""
GJR-GARCH Volatility Scaling

Phase 7 - Quant Portfolio Risk Management

Implements:
    - GJR-GARCH(1,1)
    - Conditional volatility
    - 1-day-ahead volatility forecast
    - Standardized residuals
    - Volatility scaling
    - GJR-GARCH-scaled Historical VaR
    - Leverage/asymmetry parameter
"""

from pathlib import Path

import numpy as np
import pandas as pd
from arch import arch_model


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DEFAULT_CONFIDENCE_LEVELS = (0.90, 0.95, 0.99)


# ---------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------

def load_portfolio_returns(
    file_path: str | Path,
    return_column: str = "Portfolio Return",
) -> pd.Series:
    """
    Load portfolio returns from portfolio_daily.csv.

    Parameters
    ----------
    file_path:
        Path to portfolio_daily.csv.

    return_column:
        Column containing portfolio returns.

    Returns
    -------
    pd.Series
        Clean portfolio return series.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Portfolio return file not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if return_column not in df.columns:
        raise ValueError(
            f"Column '{return_column}' not found in {file_path}. "
            f"Available columns: {list(df.columns)}"
        )

    returns = pd.to_numeric(df[return_column], errors="coerce")

    returns = returns.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()

    if len(returns) < 100:
        raise ValueError(
            "At least 100 valid observations are required "
            "to fit the GJR-GARCH model."
        )

    returns.index = (
        pd.to_datetime(df.loc[returns.index, "Date"])
        if "Date" in df.columns
        else returns.index
    )

    return returns.astype(float)


# ---------------------------------------------------------------------
# GJR-GARCH Model
# ---------------------------------------------------------------------

def fit_gjr_garch(
    returns: pd.Series,
    p: int = 1,
    o: int = 1,
    q: int = 1,
    mean: str = "Constant",
    dist: str = "normal",
):
    """
    Fit a GJR-GARCH(p,o,q) model.

    For Phase 7 the default is GJR-GARCH(1,1):

        sigma_t^2 =
            omega
            + alpha * epsilon_(t-1)^2
            + gamma * I(epsilon_(t-1)<0) * epsilon_(t-1)^2
            + beta * sigma_(t-1)^2

    Returns
    -------
    ARCHModelResult
        Fitted model result.
    """

    if not isinstance(returns, pd.Series):
        returns = pd.Series(returns)

    returns = returns.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()

    if len(returns) < 100:
        raise ValueError(
            "At least 100 observations are required."
        )

    # arch works conveniently with percentage returns.
    scaled_returns = returns * 100.0

    model = arch_model(
        scaled_returns,
        mean=mean,
        vol="GARCH",
        p=p,
        o=o,
        q=q,
        dist=dist,
        rescale=False,
    )

    result = model.fit(
        disp="off",
        show_warning=False,
    )

    return result


# ---------------------------------------------------------------------
# Model Parameters
# ---------------------------------------------------------------------

def get_gjr_parameters(result) -> dict:
    """
    Extract GJR-GARCH parameters.
    """

    params = result.params

    omega = float(params.get("omega", np.nan))
    alpha = float(params.get("alpha[1]", np.nan))
    gamma = float(params.get("gamma[1]", np.nan))
    beta = float(params.get("beta[1]", np.nan))

    return {
        "omega": omega,
        "alpha": alpha,
        "gamma": gamma,
        "beta": beta,
        "persistence": alpha + (0.5 * gamma) + beta,
    }


# ---------------------------------------------------------------------
# Conditional Volatility
# ---------------------------------------------------------------------

def get_conditional_volatility(
    result,
    returns: pd.Series,
) -> pd.Series:
    """
    Extract conditional volatility from fitted GJR-GARCH model.

    Returns volatility in decimal-return units.
    """

    volatility = result.conditional_volatility / 100.0

    volatility = pd.Series(
        volatility,
        index=returns.index,
        name="GJR-GARCH Conditional Volatility",
    )

    return volatility


# ---------------------------------------------------------------------
# Standardized Residuals
# ---------------------------------------------------------------------

def get_standardized_residuals(
    result,
    returns: pd.Series,
) -> pd.Series:
    """
    Calculate standardized residuals:

        z_t = epsilon_t / sigma_t
    """

    residuals = result.resid / 100.0
    volatility = result.conditional_volatility / 100.0

    standardized = residuals / volatility

    standardized = pd.Series(
        standardized,
        index=returns.index,
        name="Standardized Residual",
    )

    return standardized.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()


# ---------------------------------------------------------------------
# 1-Day Forecast
# ---------------------------------------------------------------------

def forecast_next_day_volatility(result) -> float:
    """
    Forecast next-day conditional volatility.

    Returns
    -------
    float
        Forecast volatility in decimal-return units.
    """

    forecast = result.forecast(
        horizon=1,
        reindex=False,
    )

    variance = float(
        forecast.variance.iloc[-1, 0]
    )

    if variance < 0:
        raise ValueError(
            "Forecast variance cannot be negative."
        )

    volatility = np.sqrt(variance) / 100.0

    return float(volatility)


# ---------------------------------------------------------------------
# Volatility Scaling
# ---------------------------------------------------------------------

def scale_returns(
    returns: pd.Series,
    conditional_volatility: pd.Series,
    forecast_volatility: float,
) -> pd.Series:
    """
    Scale historical returns using GJR-GARCH volatility.

    Formula:

        scaled_return_t =
            return_t
            * forecast_volatility
            / conditional_volatility_t

    This transforms historical observations so that their
    volatility is approximately aligned with current/forecast
    volatility.
    """

    aligned_returns, aligned_volatility = returns.align(
        conditional_volatility,
        join="inner",
    )

    if forecast_volatility <= 0:
        raise ValueError(
            "Forecast volatility must be positive."
        )

    if (aligned_volatility <= 0).any():
        raise ValueError(
            "Conditional volatility must be positive."
        )

    scaled = (
        aligned_returns
        * forecast_volatility
        / aligned_volatility
    )

    scaled.name = "GJR-GARCH Scaled Return"

    return scaled.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()


# ---------------------------------------------------------------------
# Historical VaR
# ---------------------------------------------------------------------

def calculate_historical_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    """
    Calculate one-day Historical VaR.

    VaR is returned as a positive loss magnitude.

    Example:
        0.025 means approximately 2.5% one-day VaR.
    """

    if not 0 < confidence_level < 1:
        raise ValueError(
            "confidence_level must be between 0 and 1."
        )

    clean_returns = pd.Series(returns).dropna()

    if clean_returns.empty:
        raise ValueError(
            "No valid returns available for VaR."
        )

    quantile = np.quantile(
        clean_returns,
        1.0 - confidence_level,
    )

    return float(-quantile)


def calculate_gjr_var_table(
    scaled_returns: pd.Series,
    confidence_levels=DEFAULT_CONFIDENCE_LEVELS,
) -> pd.DataFrame:
    """
    Calculate GJR-GARCH-scaled Historical VaR
    at multiple confidence levels.
    """

    rows = []

    for confidence in confidence_levels:
        var = calculate_historical_var(
            scaled_returns,
            confidence,
        )

        rows.append(
            {
                "Confidence": confidence,
                "VaR": var,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Complete Phase 7 Pipeline
# ---------------------------------------------------------------------

def run_gjr_garch(
    returns: pd.Series,
    confidence_levels=DEFAULT_CONFIDENCE_LEVELS,
):
    """
    Run the complete Phase 7 GJR-GARCH pipeline.

    Returns
    -------
    dict
        Contains:
            result
            parameters
            conditional_volatility
            standardized_residuals
            forecast_volatility
            scaled_returns
            var_table
    """

    result = fit_gjr_garch(returns)

    parameters = get_gjr_parameters(result)

    conditional_volatility = get_conditional_volatility(
        result,
        returns,
    )

    standardized_residuals = get_standardized_residuals(
        result,
        returns,
    )

    forecast_volatility = forecast_next_day_volatility(
        result
    )

    scaled_returns = scale_returns(
        returns,
        conditional_volatility,
        forecast_volatility,
    )

    var_table = calculate_gjr_var_table(
        scaled_returns,
        confidence_levels,
    )

    return {
        "result": result,
        "parameters": parameters,
        "conditional_volatility": conditional_volatility,
        "standardized_residuals": standardized_residuals,
        "forecast_volatility": forecast_volatility,
        "scaled_returns": scaled_returns,
        "var_table": var_table,
    }


# ---------------------------------------------------------------------
# CSV Output Generation
# ---------------------------------------------------------------------

def save_gjr_outputs(
    output_dir: str | Path,
    conditional_volatility: pd.Series,
    standardized_residuals: pd.Series,
    scaled_returns: pd.Series,
    parameters: dict,
    forecast_volatility: float,
    var_table: pd.DataFrame,
):
    """
    Save Phase 7 outputs into data/processed/.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------------
    # 1. GJR-GARCH volatility
    # ---------------------------------------------------------------

    volatility_df = pd.DataFrame(
        {
            "Date": conditional_volatility.index,
            "GJR-GARCH Conditional Volatility":
                conditional_volatility.values,
            "Standardized Residual":
                standardized_residuals.reindex(
                    conditional_volatility.index
                ).values,
        }
    )

    volatility_df.to_csv(
        output_dir / "gjr_garch_volatility.csv",
        index=False,
    )

    # ---------------------------------------------------------------
    # 2. Scaled returns
    # ---------------------------------------------------------------

    scaled_df = pd.DataFrame(
        {
            "Date": scaled_returns.index,
            "GJR-GARCH Scaled Return":
                scaled_returns.values,
        }
    )

    scaled_df.to_csv(
        output_dir / "gjr_garch_scaled_returns.csv",
        index=False,
    )

    # ---------------------------------------------------------------
    # 3. VaR + model parameters
    # ---------------------------------------------------------------

    var_df = var_table.copy()

    var_df["Omega"] = parameters["omega"]
    var_df["Alpha"] = parameters["alpha"]
    var_df["Gamma"] = parameters["gamma"]
    var_df["Beta"] = parameters["beta"]
    var_df["Persistence"] = parameters["persistence"]
    var_df["Forecast Volatility"] = forecast_volatility

    var_df.to_csv(
        output_dir / "gjr_garch_var.csv",
        index=False,
    )

    return {
        "volatility_file":
            output_dir / "gjr_garch_volatility.csv",
        "scaled_returns_file":
            output_dir / "gjr_garch_scaled_returns.csv",
        "var_file":
            output_dir / "gjr_garch_var.csv",
    }


# ---------------------------------------------------------------------
# Script Entry Point
# ---------------------------------------------------------------------

if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    portfolio_file = (
        PROJECT_ROOT
        / "data"
        / "portfolio"
        / "portfolio_daily.csv"
    )

    output_dir = (
        PROJECT_ROOT
        / "data"
        / "processed"
    )

    returns = load_portfolio_returns(
        portfolio_file
    )

    results = run_gjr_garch(
        returns
    )

    files = save_gjr_outputs(
        output_dir=output_dir,
        conditional_volatility=
            results["conditional_volatility"],
        standardized_residuals=
            results["standardized_residuals"],
        scaled_returns=
            results["scaled_returns"],
        parameters=
            results["parameters"],
        forecast_volatility=
            results["forecast_volatility"],
        var_table=
            results["var_table"],
    )

    print("\n" + "=" * 60)
    print("PHASE 7 - GJR-GARCH VOLATILITY SCALING")
    print("=" * 60)

    print("\nGJR-GARCH Parameters:")

    for key, value in results["parameters"].items():
        print(f"{key:15s}: {value:.6f}")

    print(
        "\nForecast Volatility: "
        f"{results['forecast_volatility']:.6%}"
    )

    print("\nGJR-GARCH Scaled Historical VaR:")

    print(
        results["var_table"].to_string(
            index=False
        )
    )

    print("\nOutput files:")

    for name, path in files.items():
        print(f"{name}: {path}")

    print("\nPhase 7 completed successfully.")