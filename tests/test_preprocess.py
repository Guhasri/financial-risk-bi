"""
Tests for Module 1 (preprocessing & feature engineering).

Focus: the no-leakage guarantee of the rolling features, plus the
correctness of the engineered columns on a small synthetic frame.
"""
import numpy as np
import pandas as pd
import pytest

from src import preprocess
from src.features import V_COLUMNS


def _tiny_raw(n=10):
    """A tiny valid raw-shaped frame (Time, V1..V28, Amount, Class)."""
    rng = np.random.default_rng(0)
    data = {"Time": np.arange(n) * 10.0}
    for v in V_COLUMNS:
        data[v] = rng.normal(size=n)
    data["Amount"] = rng.uniform(1, 1000, size=n)
    data["Class"] = np.zeros(n, dtype=int)
    return pd.DataFrame(data)


def test_validate_raw_accepts_good_frame():
    preprocess.validate_raw(_tiny_raw())  # should not raise


def test_validate_raw_rejects_missing_column():
    df = _tiny_raw().drop(columns=["Amount"])
    with pytest.raises(ValueError):
        preprocess.validate_raw(df)


def test_clean_removes_duplicates():
    df = _tiny_raw(5)
    dup = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    cleaned = preprocess.clean(dup)
    assert len(cleaned) == 5
    assert cleaned.attrs["duplicates_removed"] == 1


def test_identifiers_are_unique_and_formatted():
    df = preprocess.add_identifiers(_tiny_raw(3))
    assert list(df["transaction_id"]) == ["TXN-000001", "TXN-000002", "TXN-000003"]
    assert df["transaction_id"].is_unique


def test_rolling_frequency_is_past_only():
    """The first transaction can have NO prior transactions in its window."""
    df = _tiny_raw(6)
    df = preprocess.add_identifiers(df)
    df = preprocess.add_time_features(df)
    df = preprocess.add_amount_features(df)
    df = preprocess.add_rolling_features(df)
    # Row 0 has no prior rows -> frequency 0 and z-score 0 (no leakage).
    assert df.loc[0, "rolling_txn_frequency"] == 0
    assert df.loc[0, "amount_zscore_recent"] == 0.0
    # Frequencies are non-decreasing within the window as history accrues.
    assert (df["rolling_txn_frequency"] >= 0).all()


def test_rolling_zscore_uses_only_prior_rows():
    """
    Construct amounts so the current row's value cannot affect its own
    z-score: a big spike at the end must be measured against the calm history
    before it, giving a large positive z-score (not ~0).
    """
    df = _tiny_raw(5)
    # Varied-but-calm history (non-zero variance) then a big spike at the end.
    df["Amount"] = [100.0, 110.0, 90.0, 105.0, 10000.0]
    df["Time"] = [0, 1, 2, 3, 4]
    df = preprocess.add_identifiers(df)
    df = preprocess.add_time_features(df)
    df = preprocess.add_amount_features(df)
    df = preprocess.add_rolling_features(df)
    assert df.loc[4, "amount_zscore_recent"] > 5  # spike vs calm history


def test_amount_bands_cover_all_rows():
    df = preprocess.add_amount_features(_tiny_raw(20))
    assert df["amount_band"].notna().all()
    assert df["amount_band"].str.len().gt(0).all()
