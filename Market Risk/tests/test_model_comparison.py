import numpy as np
import pandas as pd
import pytest

from src.risk.model_comparison import (
    identify_exceptions,
    kupiec_pof_test,
    calculate_expected_shortfall,
    calculate_model_metrics,
    classify_traffic_light,
    compare_models,
    build_observation_dataset,
    rank_models,
)


# ---------------------------------------------------------------------
# Exception tests
# ---------------------------------------------------------------------

def test_exception_identification():

    pnl = pd.Series(
        [-5.0, -20.0, -8.0, -30.0]
    )

    var = pd.Series(
        [10.0, 10.0, 10.0, 20.0]
    )

    exceptions = identify_exceptions(
        pnl,
        var,
    )

    expected = pd.Series(
        [0, 1, 0, 1]
    )

    pd.testing.assert_series_equal(
        exceptions.reset_index(drop=True),
        expected,
        check_names=False,
    )


# ---------------------------------------------------------------------
# Kupiec test
# ---------------------------------------------------------------------

def test_kupiec_returns_valid_result():

    exceptions = pd.Series(
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    )

    result = kupiec_pof_test(
        exceptions,
        confidence_level=0.99,
    )

    assert "kupiec_lr" in result
    assert "kupiec_p_value" in result

    assert result["kupiec_lr"] >= 0
    assert 0 <= result["kupiec_p_value"] <= 1


# ---------------------------------------------------------------------
# Expected Shortfall
# ---------------------------------------------------------------------

def test_expected_shortfall():

    pnl = pd.Series(
        [-5.0, -10.0, -30.0, -40.0]
    )

    var = pd.Series(
        [20.0, 20.0, 20.0, 20.0]
    )

    es = calculate_expected_shortfall(
        pnl,
        var,
    )

    assert es == 35.0


# ---------------------------------------------------------------------
# Traffic light
# ---------------------------------------------------------------------

def test_traffic_light_green():

    assert (
        classify_traffic_light(
            exceptions=3,
            observations=250,
        )
        == "Green"
    )


def test_traffic_light_yellow():

    assert (
        classify_traffic_light(
            exceptions=7,
            observations=250,
        )
        == "Yellow"
    )


def test_traffic_light_red():

    assert (
        classify_traffic_light(
            exceptions=12,
            observations=250,
        )
        == "Red"
    )


# ---------------------------------------------------------------------
# Model metrics
# ---------------------------------------------------------------------

def test_model_metrics():

    df = pd.DataFrame(
        {
            "Portfolio P&L": [
                -5.0,
                -20.0,
                -8.0,
                -30.0,
                5.0,
            ],
            "Historical VaR": [
                10.0,
                10.0,
                10.0,
                20.0,
                10.0,
            ],
        }
    )

    result = calculate_model_metrics(
        df,
        var_column="Historical VaR",
        pnl_column="Portfolio P&L",
    )

    assert result["Number of Exceptions"] == 2

    assert np.isclose(
        result["Exception Ratio"],
        2 / 5,
    )

    assert result["Worst Daily Loss"] == 30.0

    assert result["Expected Shortfall"] == 25.0


# ---------------------------------------------------------------------
# Full model comparison
# ---------------------------------------------------------------------

def test_compare_models():

    df = pd.DataFrame(
        {
            "Date": pd.date_range(
                "2025-01-01",
                periods=10,
            ),
            "Portfolio P&L": [
                -5,
                -20,
                -8,
                -30,
                5,
                -4,
                -15,
                8,
                -7,
                -25,
            ],
            "Historical VaR": [
                10,
            ] * 10,
            "EWMA VaR": [
                11,
            ] * 10,
            "GARCH VaR": [
                12,
            ] * 10,
            "GJR-GARCH VaR": [
                13,
            ] * 10,
        }
    )

    result = compare_models(
        df,
        confidence_level=0.99,
    )

    assert len(result) == 4

    assert set(result["Model"]) == {
        "Historical Simulation",
        "EWMA",
        "GARCH",
        "GJR-GARCH",
    }

    assert (
        "Number of Exceptions"
        in result.columns
    )

    assert (
        "Expected Shortfall"
        in result.columns
    )

    assert (
        "Kupiec p-value"
        in result.columns
    )


# ---------------------------------------------------------------------
# Observation dataset
# ---------------------------------------------------------------------

def test_build_observation_dataset():

    df = pd.DataFrame(
        {
            "Date": pd.date_range(
                "2025-01-01",
                periods=3,
            ),
            "Portfolio P&L": [
                -10,
                -20,
                5,
            ],
            "Historical VaR": [
                5,
                25,
                10,
            ],
            "EWMA VaR": [
                6,
                15,
                10,
            ],
        }
    )

    result = build_observation_dataset(
        df
    )

    assert (
        "Historical Simulation Exception"
        in result.columns
    )

    assert (
        "EWMA Exception"
        in result.columns
    )


# ---------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------

def test_model_ranking():

    df = pd.DataFrame(
        {
            "Model": [
                "Historical Simulation",
                "EWMA",
                "GARCH",
                "GJR-GARCH",
            ],
            "Number of Exceptions": [
                5,
                4,
                3,
                2,
            ],
            "Exception Ratio": [
                0.02,
                0.016,
                0.012,
                0.008,
            ],
            "Average VaR": [
                100,
                95,
                90,
                85,
            ],
            "VaR Volatility": [
                20,
                18,
                16,
                15,
            ],
            "Worst Daily Loss": [
                150,
                150,
                150,
                150,
            ],
            "Expected Shortfall": [
                130,
                125,
                120,
                115,
            ],
            "Kupiec LR": [
                2,
                1.5,
                1,
                0.5,
            ],
            "Kupiec p-value": [
                0.10,
                0.20,
                0.30,
                0.40,
            ],
            "Traffic Light": [
                "Yellow",
                "Green",
                "Green",
                "Green",
            ],
        }
    )

    ranked = rank_models(df)

    assert "Overall Rank" in ranked.columns

    assert len(ranked) == 4

    assert set(
        ranked["Overall Rank"]
    ) == {1, 2, 3, 4}