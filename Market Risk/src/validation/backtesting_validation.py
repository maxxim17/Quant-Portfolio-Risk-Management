import numpy as np


def validate_exception_rate(
    exceptions,
    total_observations,
    expected_rate,
    tolerance=0.03,
):
    """
    Check whether observed exception rate is reasonably
    close to expected exception rate.
    """

    if total_observations <= 0:
        return False

    observed_rate = exceptions / total_observations

    return abs(observed_rate - expected_rate) <= tolerance


def validate_exception_clustering(
    exception_series,
    max_allowed_cluster=10,
):
    """
    Basic clustering check.

    Flags excessively long consecutive exception runs.
    """

    current_run = 0
    max_run = 0

    for value in exception_series:

        if bool(value):
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0

    return max_run <= max_allowed_cluster


def validate_kupiec_result(result):
    """
    Validate that Kupiec test returns the expected fields.
    """

    required = [
        "statistic",
        "p_value",
        "reject",
    ]

    return all(
        key in result
        for key in required
    )


def validate_christoffersen_result(result):
    """
    Validate that Christoffersen test returns the expected fields.
    """

    required = [
        "statistic",
        "p_value",
        "reject",
    ]

    return all(
        key in result
        for key in required
    )


def run_backtesting_validation(
    exceptions,
    total_observations,
    expected_rate,
    kupiec_result,
    christoffersen_result,
):
    """
    Complete backtesting validation.
    """

    exception_rate_valid = validate_exception_rate(
        exceptions,
        total_observations,
        expected_rate,
    )

    clustering_valid = validate_exception_clustering(
        exceptions
    )

    kupiec_valid = validate_kupiec_result(
        kupiec_result
    )

    christoffersen_valid = validate_christoffersen_result(
        christoffersen_result
    )

    return {
        "exception_rate": exception_rate_valid,
        "exception_clustering": clustering_valid,
        "kupiec": kupiec_valid,
        "christoffersen": christoffersen_valid,
        "passed": all([
            exception_rate_valid,
            clustering_valid,
            kupiec_valid,
            christoffersen_valid,
        ]),
    }