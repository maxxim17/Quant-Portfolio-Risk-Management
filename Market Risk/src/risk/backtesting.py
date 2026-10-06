# """
# Phase 8 - VaR Backtesting

# Implements:
# - Rolling out-of-sample VaR backtesting
# - Exception detection
# - Exception statistics
# - Kupiec POF test
# - Christoffersen Independence test
# - Christoffersen Conditional Coverage test
# - Basel Traffic Light test
# """

# from __future__ import annotations

# from dataclasses import dataclass
# from math import log, isfinite
# from typing import Iterable

# import numpy as np
# import pandas as pd
# from scipy.stats import chi2


# # ============================================================
# # Configuration
# # ============================================================

# DEFAULT_ESTIMATION_WINDOW = 750
# DEFAULT_BACKTEST_WINDOW = 250
# DEFAULT_CONFIDENCE_LEVEL = 0.99


# # ============================================================
# # Exception Detection
# # ============================================================

# def calculate_exceptions(
#     actual_returns: pd.Series,
#     var_series: pd.Series,
# ) -> pd.Series:
#     """
#     Calculate VaR exceptions.

#     VaR is represented as a positive loss number.

#     Exception occurs when:

#         Actual Loss > VaR

#     Since returns are normally negative during losses:

#         Actual Loss = -Actual Return
#     """

#     actual_returns = pd.Series(actual_returns, dtype=float)
#     var_series = pd.Series(var_series, dtype=float)

#     aligned = pd.concat(
#         [actual_returns.rename("actual_return"),
#          var_series.rename("var")],
#         axis=1,
#     ).dropna()

#     actual_loss = -aligned["actual_return"]

#     exceptions = actual_loss > aligned["var"]

#     return pd.Series(
#         exceptions.astype(int).values,
#         index=aligned.index,
#         name="Exception",
#     )


# # ============================================================
# # Exception Statistics
# # ============================================================

# def exception_statistics(
#     exceptions: pd.Series,
#     confidence_level: float,
# ) -> dict:
#     """
#     Calculate exception statistics.
#     """

#     exceptions = pd.Series(exceptions).dropna().astype(int)

#     n = len(exceptions)

#     if n == 0:
#         raise ValueError("No observations available for backtesting.")

#     number_of_exceptions = int(exceptions.sum())

#     expected_probability = 1.0 - confidence_level

#     expected_exceptions = n * expected_probability

#     exception_ratio = number_of_exceptions / n

#     return {
#         "Observations": n,
#         "Exceptions": number_of_exceptions,
#         "Expected Exceptions": expected_exceptions,
#         "Exception Ratio": exception_ratio,
#         "Expected Exception Ratio": expected_probability,
#     }


# # ============================================================
# # Kupiec POF Test
# # ============================================================

# def kupiec_pof_test(
#     exceptions: pd.Series,
#     confidence_level: float,
# ) -> dict:
#     """
#     Kupiec Proportion of Failures (POF) test.

#     H0:
#         Observed exception probability equals expected
#         exception probability.

#     H1:
#         Observed exception probability differs from expected.
#     """

#     exceptions = pd.Series(exceptions).dropna().astype(int)

#     n = len(exceptions)
#     x = int(exceptions.sum())

#     if n == 0:
#         raise ValueError("No observations available.")

#     p = 1.0 - confidence_level

#     if x == 0:
#         likelihood_ratio = -2.0 * (
#             n * log(1.0 - p)
#             - n * log(1.0)
#         )

#         # Equivalent stable formulation
#         likelihood_ratio = -2.0 * (
#             n * log(1.0 - p)
#             - n * log(1.0)
#         )

#         # Since observed probability = 0,
#         # likelihood under alternative is 1.
#         likelihood_ratio = -2.0 * (
#             n * log(1.0 - p)
#         )

#     elif x == n:
#         likelihood_ratio = -2.0 * (
#             n * log(p)
#         )

#     else:
#         observed_probability = x / n

#         log_likelihood_null = (
#             (n - x) * log(1.0 - p)
#             + x * log(p)
#         )

#         log_likelihood_alt = (
#             (n - x) * log(1.0 - observed_probability)
#             + x * log(observed_probability)
#         )

#         likelihood_ratio = -2.0 * (
#             log_likelihood_null - log_likelihood_alt
#         )

#     p_value = 1.0 - chi2.cdf(likelihood_ratio, df=1)

#     conclusion = "PASS" if p_value >= 0.05 else "FAIL"

#     return {
#         "Kupiec LR": likelihood_ratio,
#         "Kupiec P-Value": p_value,
#         "Kupiec Conclusion": conclusion,
#     }


# # ============================================================
# # Christoffersen Independence Test
# # ============================================================

# def christoffersen_independence_test(
#     exceptions: pd.Series,
# ) -> dict:
#     """
#     Christoffersen Independence Test.

#     Tests whether VaR exceptions occur independently.

#     H0:
#         Exceptions are independent.

#     H1:
#         Exceptions are clustered.
#     """

#     exceptions = pd.Series(exceptions).dropna().astype(int)

#     if len(exceptions) < 2:
#         raise ValueError(
#             "At least two observations are required."
#         )

#     previous = exceptions.iloc[:-1].to_numpy()
#     current = exceptions.iloc[1:].to_numpy()

#     n00 = int(((previous == 0) & (current == 0)).sum())
#     n01 = int(((previous == 0) & (current == 1)).sum())
#     n10 = int(((previous == 1) & (current == 0)).sum())
#     n11 = int(((previous == 1) & (current == 1)).sum())

#     n0 = n00 + n01
#     n1 = n10 + n11

#     total = n0 + n1

#     def safe_prob(numerator, denominator):
#         if denominator == 0:
#             return 0.0

#         return numerator / denominator

#     pi0 = safe_prob(n01, n0)
#     pi1 = safe_prob(n11, n1)
#     pi = safe_prob(n01 + n11, total)

#     def log_likelihood(count_a, count_b, probability):
#         if count_a == 0 or probability == 0:
#             term_a = 0.0
#         else:
#             term_a = count_a * log(probability)

#         if count_b == 0 or probability == 1:
#             term_b = 0.0
#         else:
#             term_b = count_b * log(1.0 - probability)

#         return term_a + term_b

#     log_likelihood_independent = (
#         log_likelihood(n01 + n11, n00 + n10, pi)
#     )

#     log_likelihood_markov = (
#         log_likelihood(n01, n00, pi0)
#         + log_likelihood(n11, n10, pi1)
#     )

#     likelihood_ratio = -2.0 * (
#         log_likelihood_independent
#         - log_likelihood_markov
#     )

#     p_value = 1.0 - chi2.cdf(
#         likelihood_ratio,
#         df=1,
#     )

#     conclusion = "PASS" if p_value >= 0.05 else "FAIL"

#     return {
#         "Christoffersen Independence LR": likelihood_ratio,
#         "Christoffersen Independence P-Value": p_value,
#         "Christoffersen Independence Conclusion": conclusion,
#         "N00": n00,
#         "N01": n01,
#         "N10": n10,
#         "N11": n11,
#     }


# # ============================================================
# # Christoffersen Conditional Coverage
# # ============================================================

# def christoffersen_conditional_coverage_test(
#     exceptions: pd.Series,
#     confidence_level: float,
# ) -> dict:
#     """
#     Christoffersen Conditional Coverage Test.

#     Combines:

#         Kupiec POF
#         +
#         Independence Test
#     """

#     kupiec = kupiec_pof_test(
#         exceptions,
#         confidence_level,
#     )

#     independence = christoffersen_independence_test(
#         exceptions
#     )

#     conditional_coverage_lr = (
#         kupiec["Kupiec LR"]
#         + independence["Christoffersen Independence LR"]
#     )

#     p_value = 1.0 - chi2.cdf(
#         conditional_coverage_lr,
#         df=2,
#     )

#     conclusion = "PASS" if p_value >= 0.05 else "FAIL"

#     return {
#         "Christoffersen Conditional Coverage LR":
#             conditional_coverage_lr,
#         "Christoffersen Conditional Coverage P-Value":
#             p_value,
#         "Christoffersen Conditional Coverage Conclusion":
#             conclusion,
#     }


# # ============================================================
# # Basel Traffic Light
# # ============================================================

# def basel_traffic_light(
#     exceptions: int,
#     observations: int,
#     confidence_level: float = 0.99,
# ) -> dict:
#     """
#     Basel Traffic Light Test.

#     Standard Basel traffic-light thresholds are based on
#     a 250-day observation period at 99% VaR.

#     Green:
#         0 - 4 exceptions

#     Yellow:
#         5 - 9 exceptions

#     Red:
#         10 or more exceptions
#     """

#     if confidence_level != 0.99:
#         return {
#             "Basel Zone": "N/A",
#             "Basel Conclusion":
#                 "Basel Traffic Light requires 99% VaR.",
#         }

#     if observations != 250:
#         return {
#             "Basel Zone": "N/A",
#             "Basel Conclusion":
#                 "Use exactly 250 observations for the standard Basel test.",
#         }

#     if exceptions <= 4:
#         zone = "GREEN"
#         conclusion = "PASS"

#     elif exceptions <= 9:
#         zone = "YELLOW"
#         conclusion = "REVIEW"

#     else:
#         zone = "RED"
#         conclusion = "FAIL"

#     return {
#         "Basel Zone": zone,
#         "Basel Conclusion": conclusion,
#     }


# # ============================================================
# # Complete Backtest
# # ============================================================

# def run_backtest(
#     actual_returns: pd.Series,
#     var_series: pd.Series,
#     confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
# ) -> dict:
#     """
#     Run the complete Phase 8 backtesting suite.
#     """

#     exceptions = calculate_exceptions(
#         actual_returns,
#         var_series,
#     )

#     stats = exception_statistics(
#         exceptions,
#         confidence_level,
#     )

#     kupiec = kupiec_pof_test(
#         exceptions,
#         confidence_level,
#     )

#     independence = christoffersen_independence_test(
#         exceptions
#     )

#     conditional_coverage = (
#         christoffersen_conditional_coverage_test(
#             exceptions,
#             confidence_level,
#         )
#     )

#     basel = basel_traffic_light(
#         exceptions=int(exceptions.sum()),
#         observations=len(exceptions),
#         confidence_level=confidence_level,
#     )

#     result = {}

#     result.update(stats)
#     result.update(kupiec)
#     result.update(independence)
#     result.update(conditional_coverage)
#     result.update(basel)

#     result["Confidence Level"] = confidence_level

#     return result


# # ============================================================
# # Rolling Backtest Dataset
# # ============================================================

# def prepare_backtesting_window(
#     portfolio_df: pd.DataFrame,
#     estimation_window: int = DEFAULT_ESTIMATION_WINDOW,
#     backtest_window: int = DEFAULT_BACKTEST_WINDOW,
# ) -> pd.DataFrame:
#     """
#     Select the rolling out-of-sample period.

#     Example:

#         750 observations -> estimation
#         following 250   -> backtesting
#     """

#     df = portfolio_df.copy()

#     if "Date" in df.columns:
#         df["Date"] = pd.to_datetime(df["Date"])
#         df = df.sort_values("Date")

#     df = df.reset_index(drop=True)

#     required_column = "Portfolio Return"

#     if required_column not in df.columns:
#         raise ValueError(
#             f"Missing required column: {required_column}"
#         )

#     minimum_required = (
#         estimation_window + backtest_window
#     )

#     if len(df) < minimum_required:
#         raise ValueError(
#             f"Need at least {minimum_required} observations. "
#             f"Found {len(df)}."
#         )

#     start = estimation_window

#     end = estimation_window + backtest_window

#     return df.iloc[start:end].copy()


# # ============================================================
# # Build Exception Series
# # ============================================================

# def build_backtest_table(
#     portfolio_df: pd.DataFrame,
#     var_df: pd.DataFrame,
#     var_column: str,
#     estimation_window: int = DEFAULT_ESTIMATION_WINDOW,
#     backtest_window: int = DEFAULT_BACKTEST_WINDOW,
# ) -> pd.DataFrame:
#     """
#     Align actual portfolio returns and VaR values.

#     var_df must contain:
#         Date
#         selected VaR column
#     """

#     portfolio = portfolio_df.copy()
#     var_data = var_df.copy()

#     portfolio["Date"] = pd.to_datetime(
#         portfolio["Date"]
#     )

#     var_data["Date"] = pd.to_datetime(
#         var_data["Date"]
#     )

#     portfolio = portfolio.sort_values("Date")
#     var_data = var_data.sort_values("Date")

#     minimum_required = (
#         estimation_window + backtest_window
#     )

#     if len(portfolio) < minimum_required:
#         raise ValueError(
#             f"Need at least {minimum_required} portfolio observations."
#         )

#     portfolio_test = portfolio.iloc[
#         estimation_window:
#         estimation_window + backtest_window
#     ].copy()

#     merged = portfolio_test.merge(
#         var_data[["Date", var_column]],
#         on="Date",
#         how="left",
#     )

#     merged = merged.dropna(
#         subset=["Portfolio Return", var_column]
#     )

#     merged["Actual Loss"] = -merged["Portfolio Return"]

#     merged["Exception"] = (
#         merged["Actual Loss"] > merged[var_column]
#     ).astype(int)

#     return merged



import numpy as np
from scipy.stats import chi2


def kupiec_pof_test(exceptions, confidence_level=0.99):
    """
    Kupiec Proportion of Failures test.

    H0: observed exception rate equals expected exception rate.
    """

    exceptions = np.asarray(exceptions, dtype=int)

    n = len(exceptions)
    x = exceptions.sum()

    if n == 0:
        raise ValueError("Exception series cannot be empty.")

    alpha = 1 - confidence_level

    # Observed exception rate
    p_hat = x / n

    # Handle boundary cases
    if x == 0:
        log_likelihood_restricted = n * np.log(1 - alpha)
        log_likelihood_unrestricted = n * np.log(1 - p_hat)
    elif x == n:
        log_likelihood_restricted = n * np.log(alpha)
        log_likelihood_unrestricted = n * np.log(p_hat)
    else:
        log_likelihood_restricted = (
            (n - x) * np.log(1 - alpha)
            + x * np.log(alpha)
        )

        log_likelihood_unrestricted = (
            (n - x) * np.log(1 - p_hat)
            + x * np.log(p_hat)
        )

    lr_stat = -2 * (
        log_likelihood_restricted
        - log_likelihood_unrestricted
    )

    p_value = 1 - chi2.cdf(lr_stat, df=1)

    return {
        "LR Statistic": lr_stat,
        "p-value": p_value,
        "Exceptions": int(x),
        "Exception Ratio": p_hat,
        "Expected Exception Ratio": alpha,
        "Pass": p_value >= 0.05,
    }


def christoffersen_independence_test(exceptions):
    """
    Christoffersen Independence Test.
    """

    exceptions = np.asarray(exceptions, dtype=int)

    if len(exceptions) < 2:
        raise ValueError("At least two observations are required.")

    n00 = n01 = n10 = n11 = 0

    for i in range(1, len(exceptions)):
        previous = exceptions[i - 1]
        current = exceptions[i]

        if previous == 0 and current == 0:
            n00 += 1
        elif previous == 0 and current == 1:
            n01 += 1
        elif previous == 1 and current == 0:
            n10 += 1
        elif previous == 1 and current == 1:
            n11 += 1

    total_0 = n00 + n01
    total_1 = n10 + n11

    pi0 = n01 / total_0 if total_0 > 0 else 0
    pi1 = n11 / total_1 if total_1 > 0 else 0

    total = total_0 + total_1
    pi = (n01 + n11) / total if total > 0 else 0

    def safe_log_likelihood(prob, successes, failures):
        if successes == 0:
            success_term = 0
        else:
            success_term = successes * np.log(prob)

        if failures == 0:
            failure_term = 0
        else:
            failure_term = failures * np.log(1 - prob)

        return success_term + failure_term

    ll_restricted = safe_log_likelihood(
        pi,
        n01 + n11,
        n00 + n10
    )

    ll_unrestricted = (
        safe_log_likelihood(pi0, n01, n00)
        + safe_log_likelihood(pi1, n11, n10)
    )

    lr_stat = -2 * (
        ll_restricted - ll_unrestricted
    )

    p_value = 1 - chi2.cdf(lr_stat, df=1)

    return {
        "LR Statistic": lr_stat,
        "p-value": p_value,
        "Pass": p_value >= 0.05,
    }


def christoffersen_conditional_coverage_test(
    exceptions,
    confidence_level=0.99
):
    """
    Christoffersen Conditional Coverage Test.

    Combines:
    - Kupiec unconditional coverage
    - Christoffersen independence
    """

    kupiec = kupiec_pof_test(
        exceptions,
        confidence_level
    )

    independence = christoffersen_independence_test(
        exceptions
    )

    lr_stat = (
        kupiec["LR Statistic"]
        + independence["LR Statistic"]
    )

    p_value = 1 - chi2.cdf(
        lr_stat,
        df=2
    )

    return {
        "LR Statistic": lr_stat,
        "p-value": p_value,
        "Pass": p_value >= 0.05,
    }


def basel_traffic_light(
    exception_count,
    observations=250
):
    """
    Basel Traffic Light classification
    for 99% VaR over 250 observations.
    """

    if observations != 250:
        return {
            "Zone": "N/A",
            "Pass": None,
        }

    if 0 <= exception_count <= 4:
        zone = "Green"
        passed = True

    elif 5 <= exception_count <= 9:
        zone = "Yellow"
        passed = False

    else:
        zone = "Red"
        passed = False

    return {
        "Zone": zone,
        "Pass": passed,
    }


def run_model_backtest(
    exceptions,
    confidence_level=0.99
):
    """
    Run all Phase 8 backtests for one VaR model.
    """

    exceptions = np.asarray(
        exceptions,
        dtype=int
    )

    kupiec = kupiec_pof_test(
        exceptions,
        confidence_level
    )

    independence = christoffersen_independence_test(
        exceptions
    )

    conditional_coverage = (
        christoffersen_conditional_coverage_test(
            exceptions,
            confidence_level
        )
    )

    traffic_light = basel_traffic_light(
        exception_count=int(exceptions.sum()),
        observations=len(exceptions)
    )

    return {
        "Number of Observations": len(exceptions),
        "Number of Exceptions": int(exceptions.sum()),
        "Exception Ratio": exceptions.mean(),
        "Expected Exception Ratio": 1 - confidence_level,
        "Kupiec p-value": kupiec["p-value"],
        "Kupiec Pass": kupiec["Pass"],
        "Christoffersen Independence p-value":
            independence["p-value"],
        "Christoffersen Independence Pass":
            independence["Pass"],
        "Conditional Coverage p-value":
            conditional_coverage["p-value"],
        "Conditional Coverage Pass":
            conditional_coverage["Pass"],
        "Basel Zone":
            traffic_light["Zone"],
        "Basel Pass":
            traffic_light["Pass"],
    }
