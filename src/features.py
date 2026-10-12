"""
Shared feature definitions used by both training and scoring, so the two
never disagree about which columns feed the model.
"""
from __future__ import annotations

# PCA-anonymised components present in the raw dataset.
V_COLUMNS = [f"V{i}" for i in range(1, 29)]

# Raw numeric columns we keep as model inputs.
RAW_NUMERIC = ["Time", "Amount"]

# Engineered features created in Module 1 (preprocess.py).
ENGINEERED = [
    "transaction_hour",
    "day_index",
    "is_night",
    "amount_log",
    "rolling_txn_frequency",
    "amount_zscore_recent",
]

# Full ordered feature list fed to the model. Target `Class` is NOT here.
FEATURE_COLUMNS = RAW_NUMERIC + V_COLUMNS + ENGINEERED

# Continuous columns we scale (RobustScaler). The V-columns are already
# PCA-scaled-like, and the binary/categorical-ish ones are left as-is.
SCALE_COLUMNS = [
    "Time",
    "Amount",
    "amount_log",
    "rolling_txn_frequency",
    "amount_zscore_recent",
]

TARGET = "Class"
