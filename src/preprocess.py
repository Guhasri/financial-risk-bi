"""
Module 1 — Data Preparation (ETL + Feature Engineering)

Extract  : read the raw Kaggle creditcard.csv
Transform: validate, de-duplicate, add identifiers and engineered features
Load     : write data/processed/clean_transactions.csv

Design rules enforced here:
  * No data leakage: time-based rolling features use ONLY past rows.
  * No fabrication: synthetic columns (datetime anchor) are clearly named.
  * The same clean file feeds BOTH the BI dashboard and the ML pipeline.

Run standalone:
    python -m src.preprocess
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config


# --------------------------------------------------------------------------
# Extract
# --------------------------------------------------------------------------
def load_raw(path=None) -> pd.DataFrame:
    """Read the raw transactions CSV."""
    path = path or config.RAW_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {path}. "
            "Place the Kaggle creditcard.csv there (see README)."
        )
    df = pd.read_csv(path)
    return df


# --------------------------------------------------------------------------
# Transform — validation & cleaning
# --------------------------------------------------------------------------
def validate_raw(df: pd.DataFrame) -> None:
    """Fail fast if the raw file is not the expected dataset."""
    expected_cols = (
        ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]
    )
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Raw data missing expected columns: {missing}")
    if not set(df["Class"].unique()).issubset({0, 1}):
        raise ValueError("Class column must contain only 0/1 values.")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """De-duplicate and validate values. Returns a cleaned copy."""
    df = df.copy()

    # Drop exact duplicate rows (the dataset is known to contain ~1081).
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    dropped = before - len(df)

    # Validate ranges.
    df = df[df["Amount"] >= 0].reset_index(drop=True)
    df["Class"] = df["Class"].astype(int)

    df.attrs["duplicates_removed"] = dropped
    return df


# --------------------------------------------------------------------------
# Transform — feature engineering
# --------------------------------------------------------------------------
def add_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    """Add a unique transaction_id and a (synthetic-anchored) datetime."""
    df = df.copy()
    # Stable, zero-padded ids: TXN-000001 ...
    df.insert(0, "transaction_id", [f"TXN-{i + 1:06d}" for i in range(len(df))])

    # Synthetic datetime = labelled anchor date + Time seconds.
    anchor = pd.Timestamp(config.SYNTHETIC_START_DATE)
    df["transaction_datetime"] = anchor + pd.to_timedelta(df["Time"], unit="s")
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive hour-of-day, day index and a night flag from Time."""
    df = df.copy()
    dt = df["transaction_datetime"]
    df["transaction_hour"] = dt.dt.hour
    # day_index: 1 for the first 24h, 2 for the second day, ...
    df["day_index"] = (df["Time"] // 86400).astype(int) + 1
    df["is_night"] = df["transaction_hour"].isin(config.NIGHT_HOURS).astype(int)
    return df


def add_amount_features(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the right-skewed Amount into model/BI-friendly forms."""
    df = df.copy()
    df["amount_log"] = np.log1p(df["Amount"])
    df["amount_band"] = pd.cut(
        df["Amount"],
        bins=config.AMOUNT_BAND_EDGES,
        labels=config.AMOUNT_BAND_LABELS,
        include_lowest=True,
    ).astype(str)
    return df


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Past-rows-only context features (NO leakage).

    The dataset has no customer/card id, so these describe the recent
    transaction STREAM (dataset-wide), not per-customer velocity. This is
    documented as a volume-context feature.

      * rolling_txn_frequency : count of transactions in the previous
                                ROLLING_WINDOW_SECONDS, excluding the current row.
      * amount_zscore_recent  : (amount - recent mean) / recent std over the
                                same trailing window, using only prior rows.
    """
    df = df.sort_values("Time").reset_index(drop=True).copy()

    times = df["Time"].to_numpy()
    amounts = df["Amount"].to_numpy()
    n = len(df)
    window = config.ROLLING_WINDOW_SECONDS

    freq = np.zeros(n, dtype=float)
    zscore = np.zeros(n, dtype=float)

    left = 0  # sliding window left boundary
    for right in range(n):
        # Advance left until the window [t-window, t) holds only prior rows.
        t = times[right]
        while times[left] < t - window:
            left += 1
        # Prior rows strictly before the current index and within window.
        prior = amounts[left:right]
        freq[right] = len(prior)
        if len(prior) >= 2:
            mu = prior.mean()
            sd = prior.std(ddof=1)
            zscore[right] = (amounts[right] - mu) / sd if sd > 0 else 0.0
        else:
            zscore[right] = 0.0

    df["rolling_txn_frequency"] = freq
    df["amount_zscore_recent"] = zscore
    return df


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
def build_clean_dataset(raw_path=None) -> pd.DataFrame:
    """Full Module 1 pipeline, returns the clean dataframe."""
    df = load_raw(raw_path)
    validate_raw(df)
    df = clean(df)
    df = add_identifiers(df)
    df = add_time_features(df)
    df = add_amount_features(df)
    df = add_rolling_features(df)
    return df


def run(raw_path=None, out_path=None) -> pd.DataFrame:
    """Build and persist the clean dataset. Returns the dataframe."""
    config.ensure_dirs()
    out_path = out_path or config.CLEAN_CSV
    df = build_clean_dataset(raw_path)
    df.to_csv(out_path, index=False)

    frauds = int(df["Class"].sum())
    print(
        f"[preprocess] wrote {out_path}\n"
        f"             rows={len(df):,}  columns={df.shape[1]}  "
        f"frauds={frauds} ({frauds / len(df) * 100:.3f}%)  "
        f"duplicates_removed={df.attrs.get('duplicates_removed', 0)}"
    )
    return df


if __name__ == "__main__":
    run()
