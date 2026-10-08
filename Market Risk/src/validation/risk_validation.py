import numpy as np


def validate_var_positive(var_value):
    """
    VaR should be represented as a positive loss number.
    """

    if var_value is None:
        return False

    return float(var_value) >= 0


def validate_confidence_order(var_90, var_95, var_99):
    """
    Higher confidence levels should produce larger VaR.
    """

    return (
        var_90 <= var_95 <= var_99
    )


def validate_es_greater_than_var(var_value, es_value):
    """
    Expected Shortfall should generally be >= VaR.
    """

    return float(es_value) >= float(var_value)


def validate_horizon_scaling(
    var_1d,
    var_10d,
):
    """
    10-day VaR should generally be greater than
    1-day VaR.
    """

    return float(var_10d) >= float(var_1d)


def validate_volatility_response(
    low_vol_var,
    high_vol_var,
):
    """
    VaR should generally increase when volatility increases.
    """

    return float(high_vol_var) >= float(low_vol_var)


def run_risk_validation(
    var_90,
    var_95,
    var_99,
    es_95,
    var_1d,
    var_10d,
    low_vol_var,
    high_vol_var,
):
    """
    Run complete VaR validation suite.
    """

    results = {
        "var_positive": validate_var_positive(var_95),

        "confidence_order":
            validate_confidence_order(
                var_90,
                var_95,
                var_99,
            ),

        "es_greater_than_var":
            validate_es_greater_than_var(
                var_95,
                es_95,
            ),

        "horizon_scaling":
            validate_horizon_scaling(
                var_1d,
                var_10d,
            ),

        "volatility_response":
            validate_volatility_response(
                low_vol_var,
                high_vol_var,
            ),
    }

    results["passed"] = all(results.values())

    return results