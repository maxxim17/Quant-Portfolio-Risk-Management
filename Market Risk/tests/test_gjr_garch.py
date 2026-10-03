import numpy as np
import pandas as pd
import pytest

from src.risk.gjr_garch import (
    calculate_historical_var,
    calculate_gjr_var_table,
    fit_gjr_garch,
    forecast_next_day_volatility,
    get_gjr_parameters,
    get_standardized_residuals,
    scale_returns,
)


@pytest.fixture
def sample_returns():
    np.random.seed(42)

    returns = np.random.normal(
        0,
        0.01,
        750,
    )

    return pd.Series(
        returns,
        index=pd.date_range(
            "2023-01-01",
            periods=750,
            freq="D",
        ),
        name="Portfolio Return",
    )


def test_gjr_garch_fit(sample_returns):

    result = fit_gjr_garch(
        sample_returns
    )

    assert result is not None


def test_gjr_parameters(sample_returns):

    result = fit_gjr_garch(
        sample_returns
    )

    parameters = get_gjr_parameters(
        result
    )

    assert "omega" in parameters
    assert "alpha" in parameters
    assert "gamma" in parameters
    assert "beta" in parameters
    assert "persistence" in parameters


def test_gamma_exists(sample_returns):

    result = fit_gjr_garch(
        sample_returns
    )

    parameters = get_gjr_parameters(
        result
    )

    assert np.isfinite(
        parameters["gamma"]
    )


def test_forecast_volatility(sample_returns):

    result = fit_gjr_garch(
        sample_returns
    )

    forecast = forecast_next_day_volatility(
        result
    )

    assert np.isfinite(forecast)
    assert forecast > 0


def test_standardized_residuals(sample_returns):

    result = fit_gjr_garch(
        sample_returns
    )

    residuals = get_standardized_residuals(
        result,
        sample_returns,
    )

    assert len(residuals) > 0
    assert np.isfinite(
        residuals
    ).all()


def test_scale_returns(sample_returns):

    result = fit_gjr_garch(
        sample_returns
    )

    volatility = (
        result.conditional_volatility / 100
    )

    forecast = forecast_next_day_volatility(
        result
    )

    scaled = scale_returns(
        sample_returns,
        volatility,
        forecast,
    )

    assert len(scaled) > 0
    assert np.isfinite(
        scaled
    ).all()


def test_historical_var(sample_returns):

    var = calculate_historical_var(
        sample_returns,
        0.95,
    )

    assert np.isfinite(var)
    assert var >= 0


def test_var_table(sample_returns):

    result = fit_gjr_garch(
        sample_returns
    )

    volatility = (
        result.conditional_volatility / 100
    )

    forecast = forecast_next_day_volatility(
        result
    )

    scaled = scale_returns(
        sample_returns,
        volatility,
        forecast,
    )

    table = calculate_gjr_var_table(
        scaled
    )

    assert len(table) == 3

    assert "Confidence" in table.columns
    assert "VaR" in table.columns


def test_invalid_confidence(sample_returns):

    with pytest.raises(ValueError):

        calculate_historical_var(
            sample_returns,
            1.5,
        )


def test_invalid_forecast_volatility(
    sample_returns,
):

    result = fit_gjr_garch(
        sample_returns
    )

    volatility = (
        result.conditional_volatility / 100
    )

    with pytest.raises(ValueError):

        scale_returns(
            sample_returns,
            volatility,
            0,
        )