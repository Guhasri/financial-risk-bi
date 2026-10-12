"""
Module 2 — Machine Learning Risk Scoring (scoring)

Loads the trained model + scaler and scores every transaction:
  * risk_score  : fraud probability 0-1 from the Random Forest
  * risk_band   : Low / Medium / High from documented thresholds
  * anomaly_flag / anomaly_indicators : which features deviate most from the
    genuine-transaction norm (what the AI agent later cites). Because the
    V-columns are anonymised, deviations are described as "anomalous pattern
    in component V14", never a business meaning.

Run standalone (after train):
    python -m src.score
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import joblib

from src import config
from src.features import FEATURE_COLUMNS, V_COLUMNS, TARGET

# Features examined for anomaly deviation (anonymised components + recent
# amount z-score). Picked because they carry the fraud-separating signal.
ANOMALY_FEATURES = V_COLUMNS + ["amount_zscore_recent"]
ANOMALY_Z = 3.0      # |z| >= this on the top feature -> anomaly_flag = 1
ANOMALY_REPORT_Z = 2.0  # only report features at least this deviant
TOP_K = 3            # max deviating features listed per transaction


def _deviation_phrase(z: float) -> str:
    if z >= 3:
        return "strongly above typical range"
    if z >= 2:
        return "above typical range"
    if z <= -3:
        return "strongly below typical range"
    if z <= -2:
        return "below typical range"
    return "near typical range"


def compute_genuine_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Mean/std of each anomaly feature over GENUINE transactions."""
    genuine = df[df[TARGET] == 0]
    stats = pd.DataFrame(
        {
            "mean": genuine[ANOMALY_FEATURES].mean(),
            "std": genuine[ANOMALY_FEATURES].std(ddof=1),
        }
    )
    # Guard against zero std.
    stats["std"] = stats["std"].replace(0, np.nan)
    return stats


def compute_anomalies(df: pd.DataFrame, stats: pd.DataFrame):
    """Return (anomaly_flag array, anomaly_indicators JSON-string array)."""
    z = (df[ANOMALY_FEATURES] - stats["mean"]) / stats["std"]
    z = z.fillna(0.0)
    z_abs = z.abs()

    flags = np.zeros(len(df), dtype=int)
    indicators = []

    z_values = z.to_numpy()
    z_abs_values = z_abs.to_numpy()
    feat = np.array(ANOMALY_FEATURES)

    for i in range(len(df)):
        row_abs = z_abs_values[i]
        order = np.argsort(row_abs)[::-1][:TOP_K]
        items = []
        for j in order:
            if row_abs[j] >= ANOMALY_REPORT_Z:
                items.append(
                    {
                        "feature": feat[j],
                        "deviation": _deviation_phrase(z_values[i, j]),
                        "zscore": round(float(z_values[i, j]), 2),
                    }
                )
        if row_abs.max() >= ANOMALY_Z:
            flags[i] = 1
        indicators.append(json.dumps(items))

    return flags, indicators


def assign_risk_band(score: float) -> str:
    if score < config.RISK_LOW_MAX:
        return "Low"
    if score >= config.RISK_HIGH_MIN:
        return "High"
    return "Medium"


def run(clean_path=None):
    config.ensure_dirs()
    clean_path = clean_path or config.CLEAN_CSV
    df = pd.read_csv(clean_path)

    model = joblib.load(config.MODEL_PATH)
    scaler = joblib.load(config.SCALER_PATH)

    from src.features import SCALE_COLUMNS

    X = df[FEATURE_COLUMNS].copy()
    X[SCALE_COLUMNS] = scaler.transform(X[SCALE_COLUMNS])

    df["risk_score"] = model.predict_proba(X)[:, 1]
    df["risk_band"] = df["risk_score"].apply(assign_risk_band)

    stats = compute_genuine_stats(df)
    flags, indicators = compute_anomalies(df, stats)
    df["anomaly_flag"] = flags
    df["anomaly_indicators"] = indicators

    cols = [
        "transaction_id",
        "risk_score",
        "risk_band",
        "anomaly_flag",
        "anomaly_indicators",
        "Class",
    ]
    scored = df[cols].rename(columns={"Class": "actual_class"})
    scored.to_csv(config.SCORED_CSV, index=False)

    band_counts = df["risk_band"].value_counts().to_dict()
    print(
        f"[score] wrote {config.SCORED_CSV}\n"
        f"        risk bands: {band_counts}\n"
        f"        anomalies flagged: {int(flags.sum()):,}"
    )
    return scored


if __name__ == "__main__":
    run()
