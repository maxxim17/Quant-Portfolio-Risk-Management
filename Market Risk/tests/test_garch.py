import numpy as np
import pandas as pd
import pytest

from src.risk.garch import (
    calculate_historical_var,
    fit_garch_model,
    forecast_garch_volatility,
    get_conditional_volatility,
    get_standardized_residuals,
    run_garch_analysis,
    scale_returns_garch,
)


def create_test_returns(n=500, seed=42):
    """
    Create synthetic returns with changing volatility.
    """

    rng = np.random.default_rng(seed)

    volatility = np.ones(n) * 0.01

    # Create volatility clustering.
    volatility[150:250] = 0.02
    volatility[350:420] = 0.025

    returns = (
        rng.normal(0, 1, n) *
        volatility
    )

    dates = pd.date_range(
        "2020-01-01",
        periods=n,
        freq="B",
    )

    return pd.Series(
        returns,
        index=dates,
        name="portfolio_return",
    )


def test_garch_model_fits():
    returns = create_test_returns()

    result = fit_garch_model(
        returns,
        p=1,
        q=1,
    )

    assert result is not None
    assert hasattr(result, "params")


def test_conditional_volatility():
    returns = create_test_returns()

    result = fit_garch_model(returns)

    volatility = get_conditional_volatility(
        result,
        index=returns.index,
    )

    assert len(volatility) == len(returns)

    assert volatility.notna().sum() > 0

    assert (volatility.dropna() >= 0).all()


def test_forecast_volatility():
    returns = create_test_returns()

    result = fit_garch_model(returns)

    forecast = forecast_garch_volatility(
        result
    )

    assert np.isfinite(forecast)

    assert forecast > 0


def test_standardized_residuals():
    returns = create_test_returns()

    result = fit_garch_model(returns)

    residuals = get_standardized_residuals(
        result,
        index=returns.index,
    )

    assert len(residuals) == len(returns)

    assert residuals.notna().sum() > 0


def test_garch_scaling():
    returns = create_test_returns()

    model_result = fit_garch_model(
        returns
    )

    volatility = get_conditional_volatility(
        model_result,
        index=returns.index,
    )

    forecast = forecast_garch_volatility(
        model_result
    )

    scaled_returns, scaling_factor = (
        scale_returns_garch(
            returns,
            volatility,
            forecast,
        )
    )

    assert len(scaled_returns) > 0

    assert len(scaling_factor) > 0

    assert np.isfinite(
        scaled_returns
    ).all()


def test_historical_var():
    returns = create_test_returns()

    var = calculate_historical_var(
        returns,
        0.95,
    )

    assert var >= 0

    assert np.isfinite(var)


def test_complete_garch_pipeline():
    returns = create_test_returns()

    result = run_garch_analysis(
        returns
    )

    assert result.model is not None

    assert len(
        result.conditional_volatility
    ) == len(returns)

    assert result.forecast_volatility > 0

    assert len(
        result.standardized_residuals
    ) == len(returns)

    assert len(
        result.scaled_returns
    ) > 0

    assert result.var_90 >= 0

    assert result.var_95 >= 0

    assert result.var_99 >= 0


def test_invalid_confidence():
    returns = create_test_returns()

    with pytest.raises(ValueError):
        calculate_historical_var(
            returns,
            1.5,
        )


def test_insufficient_returns():
    returns = pd.Series(
        np.random.normal(
            0,
            0.01,
            50,
        )
    )

    with pytest.raises(ValueError):
        fit_garch_model(
            returns
        )