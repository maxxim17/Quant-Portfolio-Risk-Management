from src.validation.risk_validation import (
    validate_var_positive,
    validate_confidence_order,
    validate_es_greater_than_var,
    validate_horizon_scaling,
)


def test_var_positive():

    assert validate_var_positive(0.025)


def test_confidence_order():

    assert validate_confidence_order(
        0.015,
        0.025,
        0.040,
    )


def test_es_greater_than_var():

    assert validate_es_greater_than_var(
        0.025,
        0.035,
    )


def test_horizon_scaling():

    assert validate_horizon_scaling(
        0.025,
        0.075,
    )