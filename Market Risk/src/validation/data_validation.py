import numpy as np
import pandas as pd


def check_missing_dates(df, date_column="Date"):
    """
    Check whether dates are missing or duplicated.
    """

    if date_column not in df.columns:
        raise ValueError(f"{date_column} column not found.")

    dates = pd.to_datetime(df[date_column]).sort_values()

    duplicate_dates = dates.duplicated().sum()

    date_diffs = dates.diff().dropna()

    missing_dates = (date_diffs > pd.Timedelta(days=1)).sum()

    return {
        "duplicate_dates": int(duplicate_dates),
        "missing_date_gaps": int(missing_dates),
        "passed": duplicate_dates == 0 and missing_dates == 0,
    }


def check_weights(weights, tolerance=1e-6):
    """
    Check whether portfolio weights sum to 100%.
    """

    weights = pd.Series(weights).dropna()

    total = weights.sum()

    return {
        "weight_sum": float(total),
        "passed": np.isclose(total, 1.0, atol=tolerance),
    }


def check_returns_alignment(
    portfolio_df,
    return_column="Portfolio Return",
):
    """
    Check portfolio returns for missing values and infinite values.
    """

    if return_column not in portfolio_df.columns:
        raise ValueError(f"{return_column} not found.")

    returns = portfolio_df[return_column]

    missing = returns.isna().sum()
    infinite = np.isinf(returns).sum()

    return {
        "missing_returns": int(missing),
        "infinite_returns": int(infinite),
        "passed": missing == 0 and infinite == 0,
    }


def check_portfolio_pnl(
    portfolio_df,
    portfolio_value_column="Portfolio Value",
    return_column="Portfolio Return",
    pnl_column="Portfolio P&L",
    tolerance=1e-6,
):
    """
    Check whether P&L is consistent with portfolio return.

    P&L_t ≈ Portfolio Value_(t-1) × Return_t
    """

    required = [
        portfolio_value_column,
        return_column,
        pnl_column,
    ]

    for column in required:
        if column not in portfolio_df.columns:
            raise ValueError(f"{column} not found.")

    df = portfolio_df.copy()

    df["Expected P&L"] = (
        df[portfolio_value_column].shift(1)
        * df[return_column]
    )

    comparison = (
        df[pnl_column].iloc[1:]
        - df["Expected P&L"].iloc[1:]
    ).abs()

    max_error = comparison.max()

    return {
        "max_pnl_error": float(max_error),
        "passed": bool(max_error <= tolerance),
    }


def run_data_validation(
    portfolio_df,
    weights=None,
):
    """
    Run all data validation checks.
    """

    results = {}

    results["dates"] = check_missing_dates(portfolio_df)

    results["returns"] = check_returns_alignment(
        portfolio_df
    )

    results["pnl"] = check_portfolio_pnl(
        portfolio_df
    )

    if weights is not None:
        results["weights"] = check_weights(weights)

    results["passed"] = all(
        result["passed"]
        for result in results.values()
    )

    return results