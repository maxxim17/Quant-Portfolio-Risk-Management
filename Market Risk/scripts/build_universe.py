from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd
import requests


NASDAQ_LISTED_URL = (
    "https://www.nasdaqtrader.com/"
    "dynamic/SymDir/nasdaqlisted.txt"
)

OTHER_LISTED_URL = (
    "https://www.nasdaqtrader.com/"
    "dynamic/SymDir/otherlisted.txt"
)

OUTPUT_PATH = Path(
    "data/universe/us_equities.csv"
)


def download_pipe_file(url: str) -> pd.DataFrame:
    response = requests.get(
        url,
        timeout=30,
    )

    response.raise_for_status()

    return pd.read_csv(
        StringIO(response.text),
        sep="|",
    )


def clean_nasdaq_listed(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df[
        df["Symbol"].notna()
        & (df["Symbol"] != "File Creation Time")
    ]

    # Remove test securities.
    if "Test Issue" in df.columns:
        df = df[df["Test Issue"] == "N"]

    # Remove bankrupt/deficient securities where possible.
    if "Financial Status" in df.columns:
        df = df[
            df["Financial Status"].isin(["N"])
        ]

    # Remove ETFs when the source provides the ETF flag.
    if "ETF" in df.columns:
        df = df[
            df["ETF"].fillna("N") == "N"
        ]

    result = pd.DataFrame(
        {
            "ticker": df["Symbol"],
            "name": df["Security Name"],
            "exchange": "NASDAQ",
            "asset_type": "Equity",
            "status": "Active",
        }
    )

    return result


def clean_other_listed(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df[
        df["ACT Symbol"].notna()
        & (df["ACT Symbol"] != "File Creation Time")
    ]

    if "Test Issue" in df.columns:
        df = df[df["Test Issue"] == "N"]

    if "ETF" in df.columns:
        df = df[
            df["ETF"].fillna("N") == "N"
        ]

    result = pd.DataFrame(
        {
            "ticker": df["ACT Symbol"],
            "name": df["Security Name"],
            "exchange": df["Exchange"],
            "asset_type": "Equity",
            "status": "Active",
        }
    )

    return result


def remove_non_common_securities(
    df: pd.DataFrame,
) -> pd.DataFrame:

    df = df.copy()

    name = (
        df["name"]
        .astype(str)
        .str.upper()
    )

    excluded_terms = [
        " ETF",
        " FUND",
        " TRUST",
        " WARRANT",
        " RIGHTS",
        " UNIT",
        " PREFERRED",
        " DEPOSITARY",
        "NOTE",
        "BOND",
        "ETN",
    ]

    mask = pd.Series(True, index=df.index)

    for term in excluded_terms:
        mask &= ~name.str.contains(
            term,
            regex=False,
            na=False,
        )

    return df[mask]


def build_universe() -> pd.DataFrame:

    print("Downloading NASDAQ-listed securities...")

    nasdaq = download_pipe_file(
        NASDAQ_LISTED_URL
    )

    print("Downloading other US-listed securities...")

    other = download_pipe_file(
        OTHER_LISTED_URL
    )

    nasdaq_clean = clean_nasdaq_listed(
        nasdaq
    )

    other_clean = clean_other_listed(
        other
    )

    universe = pd.concat(
        [
            nasdaq_clean,
            other_clean,
        ],
        ignore_index=True,
    )

    universe = remove_non_common_securities(
        universe
    )

    universe["ticker"] = (
        universe["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    universe = universe.drop_duplicates(
        subset="ticker"
    )

    universe = universe.sort_values(
        "ticker"
    ).reset_index(drop=True)

    return universe


def main() -> None:

    universe = build_universe()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    universe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print(
        f"Universe created: {len(universe):,} securities"
    )

    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()