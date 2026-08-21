"""
Risk management package.

Phase 4:
- Historical Simulation VaR
- Historical Expected Shortfall
- Rolling Historical VaR
"""

from .historical_var import (
    calculate_historical_losses,
    calculate_historical_var,
    calculate_monetary_var,
    calculate_var_es_table,
    calculate_all_rolling_var,
)

from .historical_es import calculate_historical_es

__all__ = [
    "calculate_historical_losses",
    "calculate_historical_var",
    "calculate_monetary_var",
    "calculate_var_es_table",
    "calculate_all_rolling_var",
    "calculate_historical_es",
]