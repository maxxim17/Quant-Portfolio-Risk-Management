from src.validation.backtesting_validation import (
    validate_exception_rate,
)


def test_exception_rate():

    exceptions = 25
    observations = 1000
    expected_rate = 0.025

    result = validate_exception_rate(
        exceptions,
        observations,
        expected_rate,
    )

    assert result