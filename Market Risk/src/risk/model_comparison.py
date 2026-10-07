"""
Phase 9 - VaR Model Comparison

Compares:
    1. Historical Simulation VaR
    2. EWMA-scaled Historical VaR
    3. GARCH-scaled Historical VaR
    4. GJR-GARCH-scaled Historical VaR

The module consumes already-generated VaR/backtesting outputs
and produces a common comparison framework.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd
from scipy.stats import chi2


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

MODEL_NAMES = [
    "Historical Simulation",
    "EWMA",
    "GARCH",
    "GJR-GARCH",
]

MODEL_COLUMNS = {
    "Historical Simulation": "Historical VaR",
    "EWMA": "EWMA VaR",
    "GARCH": "GARCH VaR",
    "GJR-GARCH": "GJR-GARCH VaR",
}


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def _validate_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
    dataframe_name: str = "DataFrame",
) -> None:
    """Validate that required columns exist."""
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"{dataframe_name} is missing required columns: {missing}"
        )


def _prepare_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Date column to datetime and sort chronologically."""
    result = df.copy()

    _validate_columns(result, ["Date"], "Input")

    result["Date"] = pd.to_datetime(result["Date"], errors="coerce")
    result = result.dropna(subset=["Date"])
    result = result.sort_values("Date")
    result = result.drop_duplicates(subset=["Date"])

    return result


# ---------------------------------------------------------------------
# Exception detection
# ---------------------------------------------------------------------

def identify_exceptions(
    actual_pnl: pd.Series,
    var: pd.Series,
) -> pd.Series:
    """
    Identify VaR exceptions.

    VaR is assumed to be represented as a positive loss threshold.

    Exception occurs when:
        -actual P&L > VaR

    Returns:
        Series containing 0/1 exception indicators.
    """

    pnl = pd.to_numeric(actual_pnl, errors="coerce")
    var_series = pd.to_numeric(var, errors="coerce")

    exceptions = (-pnl > var_series).astype(int)

    exceptions = exceptions.where(
        pnl.notna() & var_series.notna(),
        np.nan,
    )

    return exceptions


# ---------------------------------------------------------------------
# Kupiec POF test
# ---------------------------------------------------------------------

def kupiec_pof_test(
    exceptions: pd.Series,
    confidence_level: float = 0.99,
) -> Dict[str, float]:
    """
    Kupiec Proportion of Failures test.

    H0:
        Observed exception probability equals expected exception probability.

    Returns:
        LR statistic and p-value.
    """

    clean = pd.Series(exceptions).dropna().astype(int)

    n = len(clean)

    if n == 0:
        return {
            "kupiec_lr": np.nan,
            "kupiec_p_value": np.nan,
        }

    x = int(clean.sum())

    alpha = 1.0 - confidence_level

    if alpha <= 0 or alpha >= 1:
        raise ValueError("confidence_level must be between 0 and 1.")

    observed_rate = x / n

    # Log-likelihood under null
    ll_null = (
        x * np.log(alpha)
        + (n - x) * np.log(1 - alpha)
    )

    # Handle boundary cases safely
    if observed_rate == 0:
        ll_alt = n * np.log(1 - observed_rate)
    elif observed_rate == 1:
        ll_alt = n * np.log(observed_rate)
    else:
        ll_alt = (
            x * np.log(observed_rate)
            + (n - x) * np.log(1 - observed_rate)
        )

    lr = -2.0 * (ll_null - ll_alt)

    p_value = 1.0 - chi2.cdf(lr, df=1)

    return {
        "kupiec_lr": float(lr),
        "kupiec_p_value": float(p_value),
    }


# ---------------------------------------------------------------------
# Expected Shortfall
# ---------------------------------------------------------------------

def calculate_expected_shortfall(
    pnl: pd.Series,
    var: pd.Series,
) -> float:
    """
    Calculate Expected Shortfall from losses exceeding VaR.

    Returns positive monetary loss.
    """

    pnl = pd.to_numeric(pnl, errors="coerce")
    var = pd.to_numeric(var, errors="coerce")

    losses = -pnl

    mask = pnl.notna() & var.notna() & (losses > var)

    tail_losses = losses.loc[mask]

    if tail_losses.empty:
        return 0.0

    return float(tail_losses.mean())


# ---------------------------------------------------------------------
# Model metrics
# ---------------------------------------------------------------------

def calculate_model_metrics(
    df: pd.DataFrame,
    var_column: str,
    pnl_column: str = "Portfolio P&L",
    confidence_level: float = 0.99,
) -> Dict[str, float]:
    """
    Calculate all Phase 9 comparison metrics for one model.
    """

    _validate_columns(
        df,
        [var_column, pnl_column],
        "Model comparison DataFrame",
    )

    work = df[[pnl_column, var_column]].copy()

    work[pnl_column] = pd.to_numeric(
        work[pnl_column],
        errors="coerce",
    )

    work[var_column] = pd.to_numeric(
        work[var_column],
        errors="coerce",
    )

    work = work.dropna()

    if work.empty:
        return {
            "Number of Exceptions": 0,
            "Exception Ratio": np.nan,
            "Average VaR": np.nan,
            "VaR Volatility": np.nan,
            "Worst Daily Loss": np.nan,
            "Expected Shortfall": np.nan,
            "Kupiec LR": np.nan,
            "Kupiec p-value": np.nan,
            "Traffic Light": "N/A",
        }

    exceptions = identify_exceptions(
        work[pnl_column],
        work[var_column],
    )

    exception_count = int(exceptions.sum())
    observations = len(work)

    exception_ratio = exception_count / observations

    avg_var = float(work[var_column].mean())

    var_volatility = float(work[var_column].std())

    worst_daily_loss = float((-work[pnl_column]).max())

    expected_shortfall = calculate_expected_shortfall(
        work[pnl_column],
        work[var_column],
    )

    kupiec = kupiec_pof_test(
        exceptions,
        confidence_level=confidence_level,
    )

    traffic_light = classify_traffic_light(
        exception_count,
        observations,
    )

    return {
        "Number of Exceptions": exception_count,
        "Exception Ratio": exception_ratio,
        "Average VaR": avg_var,
        "VaR Volatility": var_volatility,
        "Worst Daily Loss": worst_daily_loss,
        "Expected Shortfall": expected_shortfall,
        "Kupiec LR": kupiec["kupiec_lr"],
        "Kupiec p-value": kupiec["kupiec_p_value"],
        "Traffic Light": traffic_light,
    }


# ---------------------------------------------------------------------
# Basel Traffic Light
# ---------------------------------------------------------------------

def classify_traffic_light(
    exceptions: int,
    observations: int,
) -> str:
    """
    Basel-style traffic light classification.

    For the standard 250-observation / 99% VaR framework:

        Green: 0-4 exceptions
        Yellow: 5-9 exceptions
        Red: 10+ exceptions

    For different sample lengths, this function scales the
    exception boundaries approximately by sample size.
    """

    if observations <= 0:
        return "N/A"

    scale = observations / 250.0

    green_limit = max(4, int(np.floor(4 * scale)))
    yellow_limit = max(
        green_limit + 1,
        int(np.floor(9 * scale)),
    )

    if exceptions <= green_limit:
        return "Green"

    if exceptions <= yellow_limit:
        return "Yellow"

    return "Red"


# ---------------------------------------------------------------------
# Model ranking
# ---------------------------------------------------------------------

def rank_models(
    comparison_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Rank VaR models.

    Lower is generally better for:
        - exception ratio, when coverage is acceptable
        - average VaR
        - VaR volatility
        - Expected Shortfall

    Models receive a composite score.

    Backtesting p-value is rewarded because a higher p-value
    indicates less evidence against correct coverage.
    """

    result = comparison_df.copy()

    # Start with zero score.
    result["Score"] = 0.0

    # Exception ratio
    result["Exception Ratio Rank"] = (
        result["Exception Ratio"]
        .rank(method="min", ascending=True)
    )

    # Average VaR
    result["Average VaR Rank"] = (
        result["Average VaR"]
        .rank(method="min", ascending=True)
    )

    # VaR volatility
    result["VaR Volatility Rank"] = (
        result["VaR Volatility"]
        .rank(method="min", ascending=True)
    )

    # Expected Shortfall
    result["Expected Shortfall Rank"] = (
        result["Expected Shortfall"]
        .rank(method="min", ascending=True)
    )

    # Backtesting p-value: higher is better
    result["Backtesting Rank"] = (
        result["Kupiec p-value"]
        .rank(method="min", ascending=False)
    )

    rank_columns = [
        "Exception Ratio Rank",
        "Average VaR Rank",
        "VaR Volatility Rank",
        "Expected Shortfall Rank",
        "Backtesting Rank",
    ]

    result["Score"] = result[rank_columns].sum(axis=1)

    result = result.sort_values(
        "Score",
        ascending=True,
    )

    result["Overall Rank"] = (
        np.arange(len(result)) + 1
    )

    return result


# ---------------------------------------------------------------------
# Full comparison engine
# ---------------------------------------------------------------------

def compare_models(
    df: pd.DataFrame,
    confidence_level: float = 0.99,
    pnl_column: str = "Portfolio P&L",
) -> pd.DataFrame:
    """
    Compare all available VaR models in a common DataFrame.

    Expected columns:

        Date
        Portfolio P&L
        Historical VaR
        EWMA VaR
        GARCH VaR
        GJR-GARCH VaR
    """

    _validate_columns(
        df,
        ["Date", pnl_column],
        "Model comparison input",
    )

    available_models = {
        model: column
        for model, column in MODEL_COLUMNS.items()
        if column in df.columns
    }

    if not available_models:
        raise ValueError(
            "No VaR model columns were found."
        )

    rows = []

    for model_name, var_column in available_models.items():

        metrics = calculate_model_metrics(
            df=df,
            var_column=var_column,
            pnl_column=pnl_column,
            confidence_level=confidence_level,
        )

        metrics["Model"] = model_name

        rows.append(metrics)

    result = pd.DataFrame(rows)

    column_order = [
        "Model",
        "Number of Exceptions",
        "Exception Ratio",
        "Average VaR",
        "VaR Volatility",
        "Worst Daily Loss",
        "Expected Shortfall",
        "Kupiec LR",
        "Kupiec p-value",
        "Traffic Light",
    ]

    return result[column_order]


# ---------------------------------------------------------------------
# Build common observation dataset
# ---------------------------------------------------------------------

def build_observation_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create an observation-level dataset containing actual P&L,
    each model's VaR and exception indicator.
    """

    required = ["Date", "Portfolio P&L"]

    _validate_columns(
        df,
        required,
        "Observation dataset",
    )

    result = df.copy()

    result["Date"] = pd.to_datetime(
        result["Date"],
        errors="coerce",
    )

    result = result.sort_values("Date")

    for model, var_column in MODEL_COLUMNS.items():

        if var_column not in result.columns:
            continue

        exception_column = (
            f"{model} Exception"
        )

        result[exception_column] = identify_exceptions(
            result["Portfolio P&L"],
            result[var_column],
        )

    return result


# ---------------------------------------------------------------------
# Save Phase 9 outputs
# ---------------------------------------------------------------------

def save_phase9_outputs(
    comparison_df,
    observations_df,
    output_dir,
):
    """
    Save Phase 9 model-comparison outputs.

    Parameters
    ----------
    comparison_df : pandas.DataFrame
        Model comparison metrics.

    observations_df : pandas.DataFrame
        Daily observations with exception indicators.

    output_dir : pathlib.Path
        Directory where Phase 9 files will be saved.
    """

    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # MODEL COMPARISON
    # ---------------------------------------------------------------
    comparison_path = (
        output_dir / "phase9_model_comparison.csv"
    )

    comparison_df.to_csv(
        comparison_path,
        index=False,
    )

    # ---------------------------------------------------------------
    # DAILY OBSERVATIONS
    # ---------------------------------------------------------------
    observations_path = (
        output_dir / "phase9_observations.csv"
    )

    observations_df.to_csv(
        observations_path,
        index=False,
    )

    # ---------------------------------------------------------------
    # MODEL RANKING
    # ---------------------------------------------------------------
    ranking_df = rank_models(comparison_df)

    ranking_path = (
        output_dir / "phase9_model_ranking.csv"
    )

    ranking_df.to_csv(
        ranking_path,
        index=False,
    )

    print()
    print("Phase 9 files saved:")
    print(f"  {comparison_path}")
    print(f"  {observations_path}")
    print(f"  {ranking_path}")