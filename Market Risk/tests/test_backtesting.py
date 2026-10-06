# import numpy as np
# import pandas as pd

# from src.risk.backtesting import (
#     calculate_exceptions,
#     exception_statistics,
#     kupiec_pof_test,
#     christoffersen_independence_test,
#     christoffersen_conditional_coverage_test,
#     basel_traffic_light,
#     run_backtest,
# )


# def test_exception_detection():
#     returns = pd.Series(
#         [-0.01, -0.02, -0.005]
#     )

#     var = pd.Series(
#         [0.015, 0.015, 0.01]
#     )

#     exceptions = calculate_exceptions(
#         returns,
#         var,
#     )

#     assert exceptions.tolist() == [0, 1, 0]


# def test_exception_statistics():

#     exceptions = pd.Series(
#         [0, 0, 1, 0, 1]
#     )

#     result = exception_statistics(
#         exceptions,
#         confidence_level=0.95,
#     )

#     assert result["Observations"] == 5
#     assert result["Exceptions"] == 2
#     assert result["Expected Exceptions"] == 0.25
#     assert result["Exception Ratio"] == 0.4


# def test_kupiec_returns_p_value():

#     exceptions = pd.Series(
#         [0] * 98 + [1] * 2
#     )

#     result = kupiec_pof_test(
#         exceptions,
#         confidence_level=0.99,
#     )

#     assert "Kupiec P-Value" in result
#     assert 0 <= result["Kupiec P-Value"] <= 1


# def test_christoffersen_independence():

#     exceptions = pd.Series(
#         [0, 0, 1, 0, 0, 1, 0, 0]
#     )

#     result = christoffersen_independence_test(
#         exceptions
#     )

#     assert "Christoffersen Independence P-Value" in result
#     assert 0 <= result[
#         "Christoffersen Independence P-Value"
#     ] <= 1


# def test_conditional_coverage():

#     exceptions = pd.Series(
#         [0] * 98 + [1] * 2
#     )

#     result = christoffersen_conditional_coverage_test(
#         exceptions,
#         confidence_level=0.99,
#     )

#     assert (
#         "Christoffersen Conditional Coverage P-Value"
#         in result
#     )


# def test_basel_green():

#     result = basel_traffic_light(
#         exceptions=4,
#         observations=250,
#         confidence_level=0.99,
#     )

#     assert result["Basel Zone"] == "GREEN"


# def test_basel_yellow():

#     result = basel_traffic_light(
#         exceptions=5,
#         observations=250,
#         confidence_level=0.99,
#     )

#     assert result["Basel Zone"] == "YELLOW"


# def test_basel_red():

#     result = basel_traffic_light(
#         exceptions=10,
#         observations=250,
#         confidence_level=0.99,
#     )

#     assert result["Basel Zone"] == "RED"


# def test_basel_invalid_window():

#     result = basel_traffic_light(
#         exceptions=4,
#         observations=200,
#         confidence_level=0.99,
#     )

#     assert result["Basel Zone"] == "N/A"


# def test_run_backtest():

#     returns = pd.Series(
#         [-0.001] * 98 + [-0.03] * 2
#     )

#     var = pd.Series(
#         [0.01] * 100
#     )

#     result = run_backtest(
#         returns,
#         var,
#         confidence_level=0.99,
#     )

#     assert result["Observations"] == 100
#     assert result["Exceptions"] == 2
#     assert "Kupiec P-Value" in result
#     assert (
#         "Christoffersen Independence P-Value"
#         in result
#     )


#     returns = pd.Series(
#     [-0.001] * 98 + [-0.03] * 2
# )

#     var = pd.Series([0.01] * 100)


import numpy as np
import pytest

from src.risk.backtesting import (
    kupiec_pof_test,
    christoffersen_independence_test,
    christoffersen_conditional_coverage_test,
    basel_traffic_light,
    run_model_backtest,
)


# ---------------------------------------------------------
# Kupiec POF Tests
# ---------------------------------------------------------

def test_kupiec_no_exceptions():
    exceptions = np.zeros(250, dtype=int)

    result = kupiec_pof_test(
        exceptions,
        confidence_level=0.99
    )

    assert result["Exceptions"] == 0
    assert result["Exception Ratio"] == 0
    assert "p-value" in result
    assert result["p-value"] >= 0


def test_kupiec_expected_exception_count():
    exceptions = np.zeros(250, dtype=int)

    # 2 exceptions out of 250 = 0.8%
    exceptions[50] = 1
    exceptions[150] = 1

    result = kupiec_pof_test(
        exceptions,
        confidence_level=0.99
    )

    assert result["Exceptions"] == 2
    assert result["Exception Ratio"] == pytest.approx(0.008)


def test_kupiec_invalid_empty_input():
    with pytest.raises(ValueError):
        kupiec_pof_test(
            [],
            confidence_level=0.99
        )


# ---------------------------------------------------------
# Christoffersen Independence Tests
# ---------------------------------------------------------

def test_christoffersen_independence_normal_sequence():
    exceptions = np.array([
        0, 0, 0, 1, 0,
        0, 0, 0, 1, 0,
        0, 0, 0, 0, 0,
        1, 0, 0, 0, 0
    ])

    result = christoffersen_independence_test(
        exceptions
    )

    assert "LR Statistic" in result
    assert "p-value" in result
    assert result["LR Statistic"] >= 0
    assert 0 <= result["p-value"] <= 1


def test_christoffersen_invalid_short_input():
    with pytest.raises(ValueError):
        christoffersen_independence_test([0])


# ---------------------------------------------------------
# Conditional Coverage Tests
# ---------------------------------------------------------

def test_conditional_coverage():
    exceptions = np.zeros(250, dtype=int)

    exceptions[50] = 1
    exceptions[100] = 1

    result = christoffersen_conditional_coverage_test(
        exceptions,
        confidence_level=0.99
    )

    assert "LR Statistic" in result
    assert "p-value" in result
    assert 0 <= result["p-value"] <= 1


# ---------------------------------------------------------
# Basel Traffic Light Tests
# ---------------------------------------------------------

def test_basel_green_zone():
    result = basel_traffic_light(
        exception_count=3,
        observations=250
    )

    assert result["Zone"] == "Green"
    assert result["Pass"] is True


def test_basel_yellow_zone():
    result = basel_traffic_light(
        exception_count=6,
        observations=250
    )

    assert result["Zone"] == "Yellow"
    assert result["Pass"] is False


def test_basel_red_zone():
    result = basel_traffic_light(
        exception_count=12,
        observations=250
    )

    assert result["Zone"] == "Red"
    assert result["Pass"] is False


def test_basel_non_250_observations():
    result = basel_traffic_light(
        exception_count=3,
        observations=200
    )

    assert result["Zone"] == "N/A"


# ---------------------------------------------------------
# Complete Backtest
# ---------------------------------------------------------

def test_run_model_backtest():
    exceptions = np.zeros(250, dtype=int)

    # Four exceptions = Green zone
    exceptions[30] = 1
    exceptions[80] = 1
    exceptions[140] = 1
    exceptions[210] = 1

    result = run_model_backtest(
        exceptions,
        confidence_level=0.99
    )

    assert result["Number of Observations"] == 250
    assert result["Number of Exceptions"] == 4

    assert result["Exception Ratio"] == pytest.approx(
        4 / 250
    )

    assert result["Expected Exception Ratio"] == pytest.approx(
        0.01
    )

    assert 0 <= result["Kupiec p-value"] <= 1

    assert 0 <= (
        result["Christoffersen Independence p-value"]
    ) <= 1

    assert 0 <= (
        result["Conditional Coverage p-value"]
    ) <= 1

    assert result["Basel Zone"] == "Green"


# ---------------------------------------------------------
# Exception Logic
# ---------------------------------------------------------

def test_exception_detection():
    actual_loss = np.array([
        0.01,
        0.03,
        0.02,
        0.05
    ])

    var = np.array([
        0.02,
        0.02,
        0.03,
        0.05
    ])

    exceptions = (
        actual_loss > var
    ).astype(int)

    expected = np.array([
        0,
        1,
        0,
        0
    ])

    np.testing.assert_array_equal(
        exceptions,
        expected
    )