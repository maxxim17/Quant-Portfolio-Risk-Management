"""
Run Phase 10 - Stress Testing
"""

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# Project root
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from src.risk.stress_testing import (
    run_stress_testing,
    save_stress_results,
)


# ============================================================
# Paths
# ============================================================

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolio"
    / "portfolio_daily.csv"
)

RETURNS_FILE = (
    ROOT
    / "data"
    / "raw"
    / "returns.csv"
)

WEIGHTS_FILE = (
    ROOT
    / "data"
    / "portfolio"
    / "portfolio_weights.csv"
)

SECTORS_FILE = (
    ROOT
    / "data"
    / "raw"
    / "sectors.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "risk"
)


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("PHASE 10 - STRESS TESTING")
    print("=" * 70)

    print("\nLoading portfolio data...")

    portfolio_df = pd.read_csv(
        PORTFOLIO_FILE
    )

    print(
        f"Portfolio observations: "
        f"{len(portfolio_df):,}"
    )

    print("\nLoading asset returns...")

    returns_df = pd.read_csv(
        RETURNS_FILE
    )

    print(
        f"Return observations: "
        f"{len(returns_df):,}"
    )

    print("\nLoading portfolio weights...")

    weights_df = pd.read_csv(
        WEIGHTS_FILE
    )

    print(
        f"Portfolio positions: "
        f"{len(weights_df):,}"
    )

    print("\nLoading sector data...")

    sectors_df = pd.read_csv(
        SECTORS_FILE
    )

    print(
        f"Sector observations: "
        f"{len(sectors_df):,}"
    )

    print("\nRunning stress scenarios...")

    (
        results_df,
        ranking_df,
        observations_df,
    ) = run_stress_testing(
        portfolio_returns=portfolio_df,
        asset_returns=returns_df,
        weights=weights_df,
        sectors=sectors_df,
        confidence=0.99,
    )

    print("\nSaving outputs...")

    paths = save_stress_results(
        results_df,
        ranking_df,
        observations_df,
        OUTPUT_DIR,
    )

    print("\n" + "=" * 70)
    print("PHASE 10 COMPLETED")
    print("=" * 70)

    print("\nGenerated files:")

    for path in paths:
        print(f"  {path}")

    print("\nScenario ranking:")
    print(
        ranking_df.to_string(
            index=False
        )
    )

    print("\nStress results:")
    print(
        results_df[
            [
                "Scenario",
                "Scenario Type",
                "Stressed Portfolio Loss",
                "Stressed VaR",
                "Stressed Expected Shortfall",
                "Worst-Case Loss",
            ]
        ].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()