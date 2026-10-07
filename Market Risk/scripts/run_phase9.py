# """
# Run Phase 9 - Model Comparison
# """


# from pathlib import Path

# import pandas as pd

# from pathlib import Path
# import sys

# PROJECT_ROOT = Path(__file__).resolve().parents[1]

# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# from src.risk.model_comparison import (
#     build_observation_dataset,
#     compare_models,
#     save_phase9_outputs,
# )


# ROOT = Path(__file__).resolve().parents[1]

# RISK_DIR = ROOT / "data" / "risk"
# PROCESSED_DIR = ROOT / "data" / "processed"
# PORTFOLIO_DIR = ROOT / "data" / "portfolio"


# def load_csv(path: Path) -> pd.DataFrame:
#     """Load CSV and fail clearly if missing."""

#     if not path.exists():
#         raise FileNotFoundError(
#             f"Required file not found:\n{path}"
#         )

#     return pd.read_csv(path)


# def main() -> None:

#     print("=" * 70)
#     print("PHASE 9 - MODEL COMPARISON")
#     print("=" * 70)

#     # -------------------------------------------------------------
#     # Load portfolio data
#     # -------------------------------------------------------------

#     portfolio_path = (
#         PORTFOLIO_DIR / "portfolio_daily.csv"
#     )

#     portfolio_df = load_csv(portfolio_path)

#     print(
#         f"\nPortfolio data loaded: "
#         f"{portfolio_path}"
#     )

#     print(
#         "Portfolio columns:",
#         portfolio_df.columns.tolist(),
#     )

#     # -------------------------------------------------------------
#     # Load Historical VaR
#     # -------------------------------------------------------------

#     historical_path = (
#         RISK_DIR / "historical_var_es.csv"
#     )

#     historical_df = load_csv(historical_path)

#     print(
#         "\nHistorical VaR loaded:",
#         historical_path,
#     )

#     print(
#         "Historical columns:",
#         historical_df.columns.tolist(),
#     )

#     # -------------------------------------------------------------
#     # Load EWMA VaR
#     # -------------------------------------------------------------

#     ewma_path = (
#         RISK_DIR / "ewma_var.csv"
#     )

#     ewma_df = load_csv(ewma_path)

#     print(
#         "\nEWMA VaR loaded:",
#         ewma_path,
#     )

#     print(
#         "EWMA columns:",
#         ewma_df.columns.tolist(),
#     )

#     # -------------------------------------------------------------
#     # Load GARCH VaR
#     # -------------------------------------------------------------

#     garch_path = (
#         PROCESSED_DIR / "garch_var.csv"
#     )

#     garch_df = load_csv(garch_path)

#     print(
#         "\nGARCH VaR loaded:",
#         garch_path,
#     )

#     print(
#         "GARCH columns:",
#         garch_df.columns.tolist(),
#     )

#     # -------------------------------------------------------------
#     # Load GJR-GARCH VaR
#     # -------------------------------------------------------------

#     gjr_path = (
#         PROCESSED_DIR / "gjr_garch_var.csv"
#     )

#     gjr_df = load_csv(gjr_path)

#     print(
#         "\nGJR-GARCH VaR loaded:",
#         gjr_path,
#     )

#     print(
#         "GJR-GARCH columns:",
#         gjr_df.columns.tolist(),
#     )

#     # -------------------------------------------------------------
#     # Normalize Date
#     # -------------------------------------------------------------

#     for dataframe in [
#         portfolio_df,
#         historical_df,
#         ewma_df,
#         garch_df,
#         gjr_df,
#     ]:
#         if "Date" in dataframe.columns:
#             dataframe["Date"] = pd.to_datetime(
#                 dataframe["Date"],
#                 errors="coerce",
#             )

#     # -------------------------------------------------------------
#     # Identify P&L
#     # -------------------------------------------------------------

#     pnl_column = None

#     for candidate in [
#         "Portfolio P&L",
#         "P&L",
#         "Portfolio PnL",
#         "PnL",
#     ]:
#         if candidate in portfolio_df.columns:
#             pnl_column = candidate
#             break

#     if pnl_column is None:
#         raise ValueError(
#             "Could not find Portfolio P&L column in "
#             "portfolio_daily.csv."
#         )

#     # -------------------------------------------------------------
#     # Rename P&L consistently
#     # -------------------------------------------------------------

#     portfolio_df = portfolio_df[
#         ["Date", pnl_column]
#     ].rename(
#         columns={
#             pnl_column: "Portfolio P&L"
#         }
#     )

#     # -------------------------------------------------------------
#     # Helper: identify VaR column
#     # -------------------------------------------------------------

#     def find_column(
#         dataframe: pd.DataFrame,
#         candidates: list[str],
#         label: str,
#     ) -> str:

#         for candidate in candidates:
#             if candidate in dataframe.columns:
#                 return candidate

#         raise ValueError(
#             f"Could not find {label} column.\n"
#             f"Available columns: "
#             f"{dataframe.columns.tolist()}"
#         )

#     # -------------------------------------------------------------
#     # Historical VaR
#     # -------------------------------------------------------------

#     historical_var_column = find_column(
#         historical_df,
#         [
#             "Historical VaR",
#             "VaR",
#             "Historical_VaR",
#         ],
#         "Historical VaR",
#     )

#     historical_df = historical_df[
#         ["Date", historical_var_column]
#     ].rename(
#         columns={
#             historical_var_column: "Historical VaR"
#         }
#     )

#     # -------------------------------------------------------------
#     # EWMA VaR
#     # -------------------------------------------------------------

#     ewma_var_column = find_column(
#         ewma_df,
#         [
#             "EWMA VaR",
#             "VaR",
#             "EWMA_VaR",
#         ],
#         "EWMA VaR",
#     )

#     ewma_df = ewma_df[
#         ["Date", ewma_var_column]
#     ].rename(
#         columns={
#             ewma_var_column: "EWMA VaR"
#         }
#     )

#     # -------------------------------------------------------------
#     # GARCH VaR
#     # -------------------------------------------------------------

#     garch_var_column = find_column(
#         garch_df,
#         [
#             "GARCH Scaled VaR",
#             "GARCH VaR",
#             "VaR",
#         ],
#         "GARCH VaR",
#     )

#     garch_df = garch_df[
#         ["Date", garch_var_column]
#     ].rename(
#         columns={
#             garch_var_column: "GARCH VaR"
#         }
#     )

#     # -------------------------------------------------------------
#     # GJR-GARCH VaR
#     # -------------------------------------------------------------

#     gjr_var_column = find_column(
#         gjr_df,
#         [
#             "GJR-GARCH Scaled VaR",
#             "GJR-GARCH VaR",
#             "VaR",
#         ],
#         "GJR-GARCH VaR",
#     )

#     gjr_df = gjr_df[
#         ["Date", gjr_var_column]
#     ].rename(
#         columns={
#             gjr_var_column: "GJR-GARCH VaR"
#         }
#     )

#     # -------------------------------------------------------------
#     # Merge everything
#     # -------------------------------------------------------------

#     comparison_data = portfolio_df.copy()

#     for dataframe in [
#         historical_df,
#         ewma_df,
#         garch_df,
#         gjr_df,
#     ]:

#         comparison_data = comparison_data.merge(
#             dataframe,
#             on="Date",
#             how="inner",
#         )

#     comparison_data = comparison_data.sort_values(
#         "Date"
#     )

#     print(
#         "\nCommon observations:",
#         len(comparison_data),
#     )

#     print(
#         "Comparison columns:",
#         comparison_data.columns.tolist(),
#     )

#     if comparison_data.empty:
#         raise ValueError(
#             "No common dates were found between "
#             "portfolio P&L and VaR models."
#         )

#     # -------------------------------------------------------------
#     # Calculate metrics
#     # -------------------------------------------------------------

#     comparison_df = compare_models(
#         comparison_data,
#         confidence_level=0.99,
#         pnl_column="Portfolio P&L",
#     )

#     print("\n")
#     print("=" * 70)
#     print("MODEL COMPARISON")
#     print("=" * 70)

#     print(
#         comparison_df.to_string(
#             index=False
#         )
#     )

#     # -------------------------------------------------------------
#     # Build observation-level data
#     # -------------------------------------------------------------

#     observations_df = build_observation_dataset(
#         comparison_data
#     )

#     # -------------------------------------------------------------
#     # Save outputs
#     # -------------------------------------------------------------

#     paths = save_phase9_outputs(
#         comparison_df=comparison_df,
#         observations_df=observations_df,
#         output_directory=RISK_DIR,
#     )

#     print("\n")
#     print("=" * 70)
#     print("PHASE 9 OUTPUTS")
#     print("=" * 70)

#     for name, path in paths.items():
#         print(
#             f"{name:15s}: {path}"
#         )

#     print("\nPhase 9 completed successfully.")


# if __name__ == "__main__":
#     main()

from pathlib import Path
import sys

# ---------------------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from src.risk.model_comparison import (
    compare_models,
    build_observation_dataset,
    save_phase9_outputs,
)


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
CONFIDENCE_LEVEL = 0.99
HISTORICAL_WINDOW = 250

DATA_DIR = PROJECT_ROOT / "data"
PORTFOLIO_DIR = DATA_DIR / "portfolio"
RISK_DIR = DATA_DIR / "risk"
PROCESSED_DIR = DATA_DIR / "processed"


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def load_csv(path: Path, name: str) -> pd.DataFrame:
    """Load CSV and validate that it exists."""
    if not path.exists():
        raise FileNotFoundError(
            f"\n{name} file not found:\n{path}"
        )

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(
            f"\n{name} file is empty:\n{path}"
        )

    print(f"{name} loaded: {path}")
    print(f"{name} columns: {list(df.columns)}")
    print()

    return df


def prepare_date(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Convert Date column to datetime."""
    if "Date" not in df.columns:
        raise KeyError(
            f"{name} does not contain a 'Date' column. "
            f"Available columns: {list(df.columns)}"
        )

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if df["Date"].isna().any():
        raise ValueError(
            f"{name} contains invalid Date values."
        )

    return df.sort_values("Date").reset_index(drop=True)


def calculate_historical_var_series(
    returns: pd.Series,
    window: int = 250,
    confidence_level: float = 0.99,
) -> pd.Series:
    """
    Calculate rolling Historical Simulation VaR.

    Returns are expressed as decimal returns.
    VaR is returned as a positive loss threshold.

    Example:
        return = -0.03
        VaR    =  0.025

    means the 3% loss exceeds the 2.5% VaR threshold.
    """

    alpha = 1.0 - confidence_level

    def rolling_var(values):
        if len(values) < window:
            return np.nan

        # Historical losses are the negative of returns.
        losses = -np.asarray(values)

        return float(np.quantile(losses, 1.0 - alpha))

    return returns.rolling(
        window=window,
        min_periods=window,
    ).apply(
        rolling_var,
        raw=True,
    )


def calculate_scaled_var_series(
    scaled_returns: pd.Series,
    window: int = 250,
    confidence_level: float = 0.99,
) -> pd.Series:
    """
    Calculate rolling Historical Simulation VaR
    on a volatility-scaled return series.
    """

    alpha = 1.0 - confidence_level

    def rolling_var(values):
        if len(values) < window:
            return np.nan

        losses = -np.asarray(values)

        return float(np.quantile(losses, 1.0 - alpha))

    return scaled_returns.rolling(
        window=window,
        min_periods=window,
    ).apply(
        rolling_var,
        raw=True,
    )


def standardize_var_series(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return Date + requested VaR column."""
    return df[["Date", column]].copy()


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():

    print("=" * 70)
    print("PHASE 9 - MODEL COMPARISON")
    print("=" * 70)
    print()

    # ================================================================
    # 1. LOAD PORTFOLIO DATA
    # ================================================================
    portfolio_path = (
        PORTFOLIO_DIR / "portfolio_daily.csv"
    )

    portfolio_df = load_csv(
        portfolio_path,
        "Portfolio data",
    )

    portfolio_df = prepare_date(
        portfolio_df,
        "Portfolio data",
    )

    required_portfolio_columns = [
        "Date",
        "Portfolio Return",
        "Portfolio P&L",
    ]

    missing = [
        c for c in required_portfolio_columns
        if c not in portfolio_df.columns
    ]

    if missing:
        raise KeyError(
            f"Portfolio data missing columns: {missing}\n"
            f"Available columns: {list(portfolio_df.columns)}"
        )

    # ================================================================
    # 2. LOAD EWMA SCALED RETURNS
    # ================================================================
    ewma_path = (
        RISK_DIR / "ewma_scaled_returns.csv"
    )

    ewma_df = load_csv(
        ewma_path,
        "EWMA scaled returns",
    )

    ewma_df = prepare_date(
        ewma_df,
        "EWMA scaled returns",
    )

    if "EWMA Scaled Return" not in ewma_df.columns:
        raise KeyError(
            "EWMA scaled returns must contain "
            "'EWMA Scaled Return'."
        )

    # ================================================================
    # 3. LOAD GARCH SCALED RETURNS
    # ================================================================
    garch_path = (
        PROCESSED_DIR / "garch_scaled_returns.csv"
    )

    garch_df = load_csv(
        garch_path,
        "GARCH scaled returns",
    )

    garch_df = prepare_date(
        garch_df,
        "GARCH scaled returns",
    )

    if "GARCH Scaled Return" not in garch_df.columns:
        raise KeyError(
            "GARCH scaled returns must contain "
            "'GARCH Scaled Return'."
        )

    # ================================================================
    # 4. LOAD GJR-GARCH SCALED RETURNS
    # ================================================================
    gjr_path = (
        PROCESSED_DIR / "gjr_garch_scaled_returns.csv"
    )

    gjr_df = load_csv(
        gjr_path,
        "GJR-GARCH scaled returns",
    )

    gjr_df = prepare_date(
        gjr_df,
        "GJR-GARCH scaled returns",
    )

    if "GJR-GARCH Scaled Return" not in gjr_df.columns:
        raise KeyError(
            "GJR-GARCH scaled returns must contain "
            "'GJR-GARCH Scaled Return'."
        )

    # ================================================================
    # 5. CREATE HISTORICAL SIMULATION VAR
    # ================================================================
    print(
        f"Calculating {HISTORICAL_WINDOW}-day "
        f"Historical Simulation VaR..."
    )

    portfolio_df["Historical VaR"] = (
        calculate_historical_var_series(
            portfolio_df["Portfolio Return"],
            window=HISTORICAL_WINDOW,
            confidence_level=CONFIDENCE_LEVEL,
        )
    )

    # ================================================================
    # 6. CREATE EWMA-SCALED HISTORICAL VAR
    # ================================================================
    print("Calculating EWMA-scaled Historical VaR...")

    ewma_df["EWMA VaR"] = (
        calculate_scaled_var_series(
            ewma_df["EWMA Scaled Return"],
            window=HISTORICAL_WINDOW,
            confidence_level=CONFIDENCE_LEVEL,
        )
    )

    # ================================================================
    # 7. CREATE GARCH-SCALED HISTORICAL VAR
    # ================================================================
    print("Calculating GARCH-scaled Historical VaR...")

    garch_df["GARCH VaR"] = (
        calculate_scaled_var_series(
            garch_df["GARCH Scaled Return"],
            window=HISTORICAL_WINDOW,
            confidence_level=CONFIDENCE_LEVEL,
        )
    )

    # ================================================================
    # 8. CREATE GJR-GARCH-SCALED HISTORICAL VAR
    # ================================================================
    print("Calculating GJR-GARCH-scaled Historical VaR...")

    gjr_df["GJR-GARCH VaR"] = (
        calculate_scaled_var_series(
            gjr_df["GJR-GARCH Scaled Return"],
            window=HISTORICAL_WINDOW,
            confidence_level=CONFIDENCE_LEVEL,
        )
    )

    # ================================================================
    # 9. BUILD DAILY COMPARISON DATASET
    # ================================================================
    print()
    print("Aligning all models by Date...")

    comparison_df = portfolio_df[
        [
            "Date",
            "Portfolio Return",
            "Portfolio P&L",
            "Historical VaR",
        ]
    ].copy()

    comparison_df = comparison_df.merge(
        ewma_df[
            [
                "Date",
                "EWMA VaR",
            ]
        ],
        on="Date",
        how="inner",
    )

    comparison_df = comparison_df.merge(
        garch_df[
            [
                "Date",
                "GARCH VaR",
            ]
        ],
        on="Date",
        how="inner",
    )

    comparison_df = comparison_df.merge(
        gjr_df[
            [
                "Date",
                "GJR-GARCH VaR",
            ]
        ],
        on="Date",
        how="inner",
    )

    comparison_df = comparison_df.sort_values(
        "Date"
    ).reset_index(drop=True)

    # Remove rows before the rolling 250-day VaR
    # becomes available.
    var_columns = [
        "Historical VaR",
        "EWMA VaR",
        "GARCH VaR",
        "GJR-GARCH VaR",
    ]

    comparison_df = comparison_df.dropna(
        subset=var_columns
    ).reset_index(drop=True)

    if comparison_df.empty:
        raise ValueError(
            "No observations remain after aligning the "
            "four VaR models."
        )

    print(
        f"Final comparison observations: "
        f"{len(comparison_df)}"
    )

    print(
        f"Date range: "
        f"{comparison_df['Date'].min().date()} "
        f"to "
        f"{comparison_df['Date'].max().date()}"
    )

    # ================================================================
    # 10. CALCULATE MODEL METRICS
    # ================================================================
    print()
    print("Calculating model metrics...")

    metrics_df = compare_models(
        comparison_df,
        confidence_level=CONFIDENCE_LEVEL,
        pnl_column="Portfolio P&L",
    )

    # ================================================================
    # 11. BUILD OBSERVATION DATASET
    # ================================================================
    observations_df = build_observation_dataset(
        comparison_df
    )

    # ================================================================
    # 12. SAVE OUTPUTS
    # ================================================================
    print()
    print("Saving Phase 9 outputs...")

    save_phase9_outputs(
        comparison_df=metrics_df,
        observations_df=observations_df,
        output_dir=RISK_DIR,
    )

    print()
    print("=" * 70)
    print("PHASE 9 COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print()

    print("Model comparison:")
    print(metrics_df.to_string(index=False))

    print()
    print("Output files:")
    print(
        RISK_DIR / "phase9_model_comparison.csv"
    )
    print(
        RISK_DIR / "phase9_observations.csv"
    )
    print(
        RISK_DIR / "phase9_model_ranking.csv"
    )


if __name__ == "__main__":
    main()