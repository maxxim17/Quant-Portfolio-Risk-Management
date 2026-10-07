import numpy as np
import pandas as pd

from src.risk.stress_testing import (
    calculate_var,
    calculate_expected_shortfall,
    calculate_historical_stress,
    market_down_scenario,
    volatility_doubles_scenario,
)


# ============================================================
# Fixtures
# ============================================================

def sample_portfolio():
    return pd.DataFrame({
        "Date": pd.date_range(
            "2020-01-01",
            periods=10,
            freq="D",
        ),
        "Portfolio Return": [
            0.010,
            -0.020,
            0.015,
            -0.030,
            0.005,
            -0.040,
            0.020,
            -0.010,
            0.008,
            -0.025,
        ],
    })


# ============================================================
# VaR
# ============================================================

def test_var_returns_positive_loss():

    returns = pd.Series([
        0.02,
        -0.01,
        -0.03,
        0.01,
        -0.05,
    ])

    var = calculate_var(
        returns,
        confidence=0.80,
    )

    assert var >= 0


# ============================================================
# Expected Shortfall
# ============================================================

def test_expected_shortfall_is_positive():

    returns = pd.Series([
        0.02,
        -0.01,
        -0.03,
        0.01,
        -0.05,
    ])

    es = calculate_expected_shortfall(
        returns,
        confidence=0.80,
    )

    assert es >= 0


# ============================================================
# Historical stress
# ============================================================

def test_historical_stress():

    df = sample_portfolio()

    result, observations = calculate_historical_stress(
        df,
        "Test Crisis",
        "2020-01-01",
        "2020-01-10",
    )

    assert result["Scenario"] == "Test Crisis"

    assert (
        result["Scenario Type"]
        == "Historical"
    )

    assert (
        result["Observations"]
        == 10
    )

    assert (
        result["Worst-Case Loss"]
        > 0
    )

    assert not observations.empty


# ============================================================
# Market shock
# ============================================================

def test_market_down_scenario():

    df = sample_portfolio()

    result, observations = market_down_scenario(
        df,
        shock=0.10,
    )

    assert (
        result["Scenario"]
        == "Equity Market Down 10%"
    )

    assert (
        result["Scenario Type"]
        == "Hypothetical"
    )

    assert np.isclose(
        result["Stressed Portfolio Loss"],
        0.10,
    )

    assert (
        result["Stressed VaR"]
        > 0
    )

    assert not observations.empty


# ============================================================
# Volatility
# ============================================================

def test_volatility_doubles():

    df = sample_portfolio()

    result, observations = (
        volatility_doubles_scenario(
            df
        )
    )

    assert (
        result["Scenario"]
        == "Volatility Doubles"
    )

    assert (
        result["Stressed VaR"]
        >= 0
    )

    assert (
        result["Stressed Expected Shortfall"]
        >= 0
    )

    assert not observations.empty