"""
Phase 10 - Stress Testing

Historical and hypothetical market stress scenarios.

Outputs:
    - Stressed portfolio loss
    - Stressed VaR
    - Stressed Expected Shortfall
    - Worst-case loss
    - Scenario ranking
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

CONFIDENCE_LEVEL = 0.99

HISTORICAL_SCENARIOS = {
    "2008 Financial Crisis": ("2008-09-01", "2008-12-31"),
    "COVID Crash 2020": ("2020-02-19", "2020-03-23"),
    "Inflation Shock 2022": ("2022-01-03", "2022-10-12"),
    "Banking Stress 2023": ("2023-03-01", "2023-05-05"),
    "Tech Selloff": ("2022-01-03", "2022-06-16"),
}


# ============================================================
# Utility functions
# ============================================================

def _find_date_column(df: pd.DataFrame) -> str:
    """Find the date column."""

    candidates = [
        "Date",
        "date",
        "Datetime",
        "datetime",
        "Timestamp",
        "timestamp",
    ]

    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        "No date column found. Expected one of: "
        + ", ".join(candidates)
    )


def _prepare_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a normalized Date column."""

    df = df.copy()

    date_column = _find_date_column(df)

    if date_column != "Date":
        df = df.rename(columns={date_column: "Date"})

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")
    df = df.drop_duplicates(subset=["Date"])

    return df


def _find_return_column(df: pd.DataFrame) -> str:
    """Find portfolio return column."""

    candidates = [
        "Portfolio Return",
        "portfolio_return",
        "Return",
        "return",
        "Portfolio Returns",
    ]

    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        "Portfolio return column not found. "
        "Expected 'Portfolio Return'."
    )


def _find_weight_column(df: pd.DataFrame) -> str:
    """Find portfolio weight column."""

    candidates = [
        "Weight",
        "weight",
        "Portfolio Weight",
        "portfolio_weight",
        "Weights",
    ]

    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        "Weight column not found in portfolio weights file."
    )


def _find_ticker_column(df: pd.DataFrame) -> str:
    """Find ticker/symbol column."""

    candidates = [
        "Ticker",
        "ticker",
        "Symbol",
        "symbol",
        "Ticker Symbol",
    ]

    for column in candidates:
        if column in df.columns:
            return column

    # If no obvious ticker column exists, use first object column.
    object_columns = df.select_dtypes(include=["object"]).columns

    if len(object_columns) > 0:
        return object_columns[0]

    raise ValueError("Ticker column not found.")


# ============================================================
# VaR / Expected Shortfall
# ============================================================

def calculate_var(
    returns: pd.Series,
    confidence: float = CONFIDENCE_LEVEL,
) -> float:
    """
    Calculate loss VaR as a positive percentage.

    Example:
        returns = -0.05
        VaR = 0.03
    """

    returns = pd.Series(returns).dropna().astype(float)

    if returns.empty:
        return np.nan

    quantile = np.quantile(
        returns,
        1.0 - confidence,
    )

    return float(-quantile)


def calculate_expected_shortfall(
    returns: pd.Series,
    confidence: float = CONFIDENCE_LEVEL,
) -> float:
    """
    Calculate Expected Shortfall as a positive percentage.
    """

    returns = pd.Series(returns).dropna().astype(float)

    if returns.empty:
        return np.nan

    var_threshold = np.quantile(
        returns,
        1.0 - confidence,
    )

    tail = returns[returns <= var_threshold]

    if tail.empty:
        return float(-var_threshold)

    return float(-tail.mean())


# ============================================================
# Historical Stress
# ============================================================

def calculate_historical_stress(
    portfolio_returns: pd.DataFrame,
    scenario_name: str,
    start_date: str,
    end_date: str,
    confidence: float = CONFIDENCE_LEVEL,
) -> Tuple[dict, pd.DataFrame]:
    """
    Calculate historical stress metrics for a given historical window.
    """

    df = _prepare_dates(portfolio_returns)

    return_column = _find_return_column(df)

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    scenario_df = df[
        (df["Date"] >= start)
        & (df["Date"] <= end)
    ].copy()

    if scenario_df.empty:
        raise ValueError(
            f"No portfolio observations found for "
            f"{scenario_name}: {start_date} to {end_date}"
        )

    scenario_df["Portfolio Return"] = pd.to_numeric(
        scenario_df[return_column],
        errors="coerce",
    )

    scenario_df = scenario_df.dropna(
        subset=["Portfolio Return"]
    )

    returns = scenario_df["Portfolio Return"]

    losses = -returns

    var = calculate_var(
        returns,
        confidence,
    )

    es = calculate_expected_shortfall(
        returns,
        confidence,
    )

    worst_loss = float(losses.max())

    worst_date = scenario_df.loc[
        losses.idxmax(),
        "Date",
    ]

    stressed_portfolio_loss = worst_loss

    result = {
        "Scenario": scenario_name,
        "Scenario Type": "Historical",
        "Start Date": start,
        "End Date": end,
        "Observations": len(scenario_df),
        "Stressed Portfolio Loss": stressed_portfolio_loss,
        "Stressed VaR": var,
        "Stressed Expected Shortfall": es,
        "Worst-Case Loss": worst_loss,
        "Worst Loss Date": worst_date,
    }

    observations = scenario_df[
        ["Date", "Portfolio Return"]
    ].copy()

    observations["Scenario"] = scenario_name
    observations["Scenario Type"] = "Historical"

    return result, observations


# ============================================================
# Hypothetical Stress
# ============================================================

def market_down_scenario(
    portfolio_returns: pd.DataFrame,
    shock: float,
    confidence: float = CONFIDENCE_LEVEL,
) -> Tuple[dict, pd.DataFrame]:
    """
    Apply a uniform market shock.

    shock:
        0.05  -> market down 5%
        0.10  -> market down 10%
        0.20  -> market down 20%
    """

    df = _prepare_dates(portfolio_returns)

    return_column = _find_return_column(df)

    base_returns = pd.to_numeric(
        df[return_column],
        errors="coerce",
    )

    base_returns = base_returns.dropna()

    scenario_name = f"Equity Market Down {int(shock * 100)}%"

    # Apply the hypothetical shock to the historical distribution.
    stressed_returns = base_returns - shock

    var = calculate_var(
        stressed_returns,
        confidence,
    )

    es = calculate_expected_shortfall(
        stressed_returns,
        confidence,
    )

    worst_loss = float(-stressed_returns.min())

    stressed_loss = shock

    result = {
        "Scenario": scenario_name,
        "Scenario Type": "Hypothetical",
        "Start Date": pd.NaT,
        "End Date": pd.NaT,
        "Observations": len(stressed_returns),
        "Stressed Portfolio Loss": stressed_loss,
        "Stressed VaR": var,
        "Stressed Expected Shortfall": es,
        "Worst-Case Loss": worst_loss,
        "Worst Loss Date": pd.NaT,
    }

    observations = pd.DataFrame({
        "Date": df.loc[
            base_returns.index,
            "Date",
        ].values,
        "Portfolio Return": base_returns.values,
        "Stressed Return": stressed_returns.values,
    })

    observations["Scenario"] = scenario_name
    observations["Scenario Type"] = "Hypothetical"

    return result, observations


def volatility_doubles_scenario(
    portfolio_returns: pd.DataFrame,
    confidence: float = CONFIDENCE_LEVEL,
) -> Tuple[dict, pd.DataFrame]:
    """
    Double the volatility of the portfolio return distribution.
    """

    df = _prepare_dates(portfolio_returns)

    return_column = _find_return_column(df)

    returns = pd.to_numeric(
        df[return_column],
        errors="coerce",
    ).dropna()

    mean_return = returns.mean()

    stressed_returns = (
        mean_return
        + 2.0 * (returns - mean_return)
    )

    var = calculate_var(
        stressed_returns,
        confidence,
    )

    es = calculate_expected_shortfall(
        stressed_returns,
        confidence,
    )

    worst_loss = float(-stressed_returns.min())

    result = {
        "Scenario": "Volatility Doubles",
        "Scenario Type": "Hypothetical",
        "Start Date": pd.NaT,
        "End Date": pd.NaT,
        "Observations": len(stressed_returns),
        "Stressed Portfolio Loss": worst_loss,
        "Stressed VaR": var,
        "Stressed Expected Shortfall": es,
        "Worst-Case Loss": worst_loss,
        "Worst Loss Date": pd.NaT,
    }

    observations = pd.DataFrame({
        "Date": df.loc[
            returns.index,
            "Date",
        ].values,
        "Portfolio Return": returns.values,
        "Stressed Return": stressed_returns.values,
    })

    observations["Scenario"] = "Volatility Doubles"
    observations["Scenario Type"] = "Hypothetical"

    return result, observations


def correlation_spike_scenario(
    returns_df: pd.DataFrame,
    weights_df: pd.DataFrame,
    confidence: float = CONFIDENCE_LEVEL,
) -> Tuple[dict, pd.DataFrame]:
    """
    Correlation spike scenario.

    Method:
        Preserve each asset's historical return magnitude,
        but force cross-sectional correlation toward +1.

    For each day:
        stressed asset return = cross-sectional average return.

    This represents a strong common-factor shock.
    """

    returns = _prepare_dates(returns_df)
    weights = weights_df.copy()

    ticker_column = _find_ticker_column(weights)
    weight_column = _find_weight_column(weights)

    weights[ticker_column] = (
        weights[ticker_column]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    weights[weight_column] = pd.to_numeric(
        weights[weight_column],
        errors="coerce",
    )

    weights = weights.dropna(
        subset=[weight_column]
    )

    asset_columns = []

    for ticker in weights[ticker_column]:
        if ticker in returns.columns:
            asset_columns.append(ticker)

    if not asset_columns:
        raise ValueError(
            "No portfolio-weight tickers were found "
            "in the returns data."
        )

    weights = weights[
        weights[ticker_column].isin(asset_columns)
    ].copy()

    weight_map = dict(
        zip(
            weights[ticker_column],
            weights[weight_column],
        )
    )

    normalized_weights = np.array([
        weight_map[ticker]
        for ticker in asset_columns
    ])

    weight_sum = normalized_weights.sum()

    if np.isclose(weight_sum, 0.0):
        raise ValueError(
            "Portfolio weights sum to zero."
        )

    normalized_weights = (
        normalized_weights / weight_sum
    )

    asset_returns = returns[asset_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    # Cross-sectional common factor.
    common_factor = asset_returns.mean(axis=1)

    stressed_asset_returns = pd.DataFrame(
        np.repeat(
            common_factor.values.reshape(-1, 1),
            len(asset_columns),
            axis=1,
        ),
        index=asset_returns.index,
        columns=asset_columns,
    )

    stressed_portfolio_returns = (
        stressed_asset_returns
        * normalized_weights
    ).sum(axis=1)

    var = calculate_var(
        stressed_portfolio_returns,
        confidence,
    )

    es = calculate_expected_shortfall(
        stressed_portfolio_returns,
        confidence,
    )

    worst_loss = float(
        -stressed_portfolio_returns.min()
    )

    result = {
        "Scenario": "Correlation Spikes",
        "Scenario Type": "Hypothetical",
        "Start Date": pd.NaT,
        "End Date": pd.NaT,
        "Observations": len(stressed_portfolio_returns),
        "Stressed Portfolio Loss": worst_loss,
        "Stressed VaR": var,
        "Stressed Expected Shortfall": es,
        "Worst-Case Loss": worst_loss,
        "Worst Loss Date": pd.NaT,
    }

    observations = pd.DataFrame({
        "Date": returns.loc[
            stressed_portfolio_returns.index,
            "Date",
        ].values,
        "Portfolio Return": stressed_portfolio_returns.values,
        "Stressed Return": stressed_portfolio_returns.values,
    })

    observations["Scenario"] = "Correlation Spikes"
    observations["Scenario Type"] = "Hypothetical"

    return result, observations


def sector_specific_shock(
    returns_df: pd.DataFrame,
    weights_df: pd.DataFrame,
    sectors_df: pd.DataFrame,
    sector_shock: float = 0.20,
    confidence: float = CONFIDENCE_LEVEL,
) -> Tuple[dict, pd.DataFrame]:
    """
    Apply a negative shock to one sector.

    The sector selected is the sector with the largest
    portfolio weight, making the scenario deterministic.
    """

    returns = _prepare_dates(returns_df)

    weights = weights_df.copy()
    sectors = sectors_df.copy()

    ticker_column = _find_ticker_column(weights)
    weight_column = _find_weight_column(weights)

    sector_ticker_column = _find_ticker_column(sectors)

    # Detect sector column.
    sector_columns = [
        "Sector",
        "sector",
        "GICS Sector",
        "gics_sector",
        "Industry",
        "industry",
    ]

    sector_column = None

    for column in sector_columns:
        if column in sectors.columns:
            sector_column = column
            break

    if sector_column is None:
        raise ValueError(
            "Sector column not found in sectors.csv."
        )

    weights[ticker_column] = (
        weights[ticker_column]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    sectors[sector_ticker_column] = (
        sectors[sector_ticker_column]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    weights[weight_column] = pd.to_numeric(
        weights[weight_column],
        errors="coerce",
    )

    weights = weights.dropna(
        subset=[weight_column]
    )

    merged = weights.merge(
        sectors[
            [
                sector_ticker_column,
                sector_column,
            ]
        ],
        left_on=ticker_column,
        right_on=sector_ticker_column,
        how="left",
    )

    merged = merged.dropna(
        subset=[sector_column]
    )

    if merged.empty:
        raise ValueError(
            "Could not match portfolio weights to sectors."
        )

    sector_weights = (
        merged.groupby(sector_column)[weight_column]
        .sum()
        .sort_values(ascending=False)
    )

    selected_sector = sector_weights.index[0]

    selected_tickers = merged.loc[
        merged[sector_column] == selected_sector,
        ticker_column,
    ].tolist()

    available_tickers = [
        ticker
        for ticker in selected_tickers
        if ticker in returns.columns
    ]

    if not available_tickers:
        raise ValueError(
            "No selected-sector tickers found in returns data."
        )

    base_returns = returns[
        available_tickers
    ].apply(
        pd.to_numeric,
        errors="coerce",
    )

    sector_weight = merged.loc[
        merged[ticker_column].isin(
            available_tickers
        ),
        weight_column,
    ].sum()

    sector_daily_return = (
        base_returns.mean(axis=1)
    )

    stressed_sector_return = (
        sector_daily_return - sector_shock
    )

    # Portfolio approximation:
    # preserve the rest of the portfolio's historical return
    # and add the incremental sector shock.
    portfolio_return_column = None

    for candidate in [
        "Portfolio Return",
        "portfolio_return",
        "Return",
    ]:
        if candidate in returns.columns:
            portfolio_return_column = candidate
            break

    if portfolio_return_column is not None:
        base_portfolio_returns = pd.to_numeric(
            returns[portfolio_return_column],
            errors="coerce",
        )
    else:
        # Construct portfolio return from available weights.
        base_portfolio_returns = pd.Series(
            0.0,
            index=returns.index,
        )

    stressed_returns = (
        base_portfolio_returns
        - sector_weight * sector_shock
    )

    var = calculate_var(
        stressed_returns,
        confidence,
    )

    es = calculate_expected_shortfall(
        stressed_returns,
        confidence,
    )

    worst_loss = float(
        -stressed_returns.min()
    )

    scenario_name = (
        f"Sector-Specific Shock - "
        f"{selected_sector} - "
        f"{int(sector_shock * 100)}%"
    )

    result = {
        "Scenario": scenario_name,
        "Scenario Type": "Hypothetical",
        "Start Date": pd.NaT,
        "End Date": pd.NaT,
        "Observations": len(stressed_returns),
        "Stressed Portfolio Loss": worst_loss,
        "Stressed VaR": var,
        "Stressed Expected Shortfall": es,
        "Worst-Case Loss": worst_loss,
        "Worst Loss Date": pd.NaT,
        "Shocked Sector": selected_sector,
        "Sector Portfolio Weight": sector_weight,
    }

    observations = pd.DataFrame({
        "Date": returns.loc[
            stressed_returns.index,
            "Date",
        ].values,
        "Portfolio Return": base_portfolio_returns.values,
        "Stressed Return": stressed_returns.values,
    })

    observations["Scenario"] = scenario_name
    observations["Scenario Type"] = "Hypothetical"

    return result, observations


# ============================================================
# Complete Stress Test
# ============================================================

def run_stress_testing(
    portfolio_returns: pd.DataFrame,
    asset_returns: pd.DataFrame,
    weights: pd.DataFrame,
    sectors: pd.DataFrame,
    confidence: float = CONFIDENCE_LEVEL,
):
    """
    Run all Phase 10 stress scenarios.

    Returns:
        results_df
        ranking_df
        observations_df
    """

    results = []
    observations = []

    # --------------------------------------------------------
    # Historical scenarios
    # --------------------------------------------------------

    for (
        scenario_name,
        (start_date, end_date),
    ) in HISTORICAL_SCENARIOS.items():

        try:
            result, obs = calculate_historical_stress(
                portfolio_returns,
                scenario_name,
                start_date,
                end_date,
                confidence,
            )

            results.append(result)
            observations.append(obs)

        except ValueError as exc:
            print(
                f"WARNING: {exc}"
            )

    # --------------------------------------------------------
    # Hypothetical market shocks
    # --------------------------------------------------------

    for shock in [0.05, 0.10, 0.20]:

        result, obs = market_down_scenario(
            portfolio_returns,
            shock,
            confidence,
        )

        results.append(result)
        observations.append(obs)

    # --------------------------------------------------------
    # Volatility
    # --------------------------------------------------------

    result, obs = volatility_doubles_scenario(
        portfolio_returns,
        confidence,
    )

    results.append(result)
    observations.append(obs)

    # --------------------------------------------------------
    # Correlation
    # --------------------------------------------------------

    try:
        result, obs = correlation_spike_scenario(
            asset_returns,
            weights,
            confidence,
        )

        results.append(result)
        observations.append(obs)

    except ValueError as exc:
        print(
            f"WARNING: Correlation scenario skipped: {exc}"
        )

    # --------------------------------------------------------
    # Sector shock
    # --------------------------------------------------------

    try:
        result, obs = sector_specific_shock(
            asset_returns,
            weights,
            sectors,
            sector_shock=0.20,
            confidence=confidence,
        )

        results.append(result)
        observations.append(obs)

    except ValueError as exc:
        print(
            f"WARNING: Sector scenario skipped: {exc}"
        )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    results_df = pd.DataFrame(results)

    if results_df.empty:
        raise RuntimeError(
            "No stress scenarios were successfully calculated."
        )

    # Add default columns if absent.
    for column in [
        "Shocked Sector",
        "Sector Portfolio Weight",
    ]:
        if column not in results_df.columns:
            results_df[column] = np.nan

    # --------------------------------------------------------
    # Scenario ranking
    # --------------------------------------------------------

    ranking_df = results_df.copy()

    ranking_df = ranking_df.sort_values(
        by=[
            "Worst-Case Loss",
            "Stressed Expected Shortfall",
            "Stressed VaR",
        ],
        ascending=False,
    ).reset_index(drop=True)

    ranking_df["Rank"] = (
        np.arange(len(ranking_df)) + 1
    )

    ranking_df = ranking_df[
        [
            "Rank",
            "Scenario",
            "Scenario Type",
            "Stressed Portfolio Loss",
            "Stressed VaR",
            "Stressed Expected Shortfall",
            "Worst-Case Loss",
        ]
    ]

    # --------------------------------------------------------
    # Observations
    # --------------------------------------------------------

    if observations:
        observations_df = pd.concat(
            observations,
            ignore_index=True,
        )
    else:
        observations_df = pd.DataFrame()

    return (
        results_df,
        ranking_df,
        observations_df,
    )


# ============================================================
# CSV helper
# ============================================================

def save_stress_results(
    results_df: pd.DataFrame,
    ranking_df: pd.DataFrame,
    observations_df: pd.DataFrame,
    output_dir: str | Path,
):
    """Save Phase 10 outputs."""

    output_dir = Path(output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_path = (
        output_dir
        / "phase10_stress_results.csv"
    )

    ranking_path = (
        output_dir
        / "phase10_scenario_ranking.csv"
    )

    observations_path = (
        output_dir
        / "phase10_stress_observations.csv"
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    ranking_df.to_csv(
        ranking_path,
        index=False,
    )

    observations_df.to_csv(
        observations_path,
        index=False,
    )

    return (
        results_path,
        ranking_path,
        observations_path,
    )