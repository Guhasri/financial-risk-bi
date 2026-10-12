"""
Build the star-schema tables Power BI reads.

Outputs (data/output/):
  fact_transactions.csv   one row per transaction (the central fact table)
  dim_date.csv            date dimension for time intelligence
  dim_risk_band.csv       Low/Medium/High + sort order + colour
  dim_review_status.csv   simulated analyst workflow states
  dim_priority.csv        LOW/MEDIUM/HIGH investigation priority
  model_metrics.csv       flattened model metrics for a KPI/table visual

Honesty note: review_status, customer_segment and region are SIMULATED
attributes (the source dataset has none). They are generated deterministically
and must be labelled "Illustrative / Simulated" on every visual that uses them.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

from src import config

# Simulated illustrative attributes (clearly labelled in the dashboard).
CUSTOMER_SEGMENTS = ["Retail", "Premium", "Business", "Student"]
REGIONS = ["North", "South", "East", "West", "Central"]


def _stable_choice(key: str, options: list[str]) -> str:
    """Deterministic pseudo-random pick from options, seeded by a string."""
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return options[h % len(options)]


def _review_status(row: pd.Series, rng: np.random.Generator) -> str:
    """
    Simulated analyst-workflow status (labelled simulated in the dashboard).
    Medium/High transactions are 'Flagged', then a subset is advanced using
    the TRUE class to mimic realistic reviewer outcomes.
    """
    if row["risk_band"] not in {"Medium", "High"}:
        return "Not flagged"
    # Advance ~60% of flagged items to a resolved/under-review state.
    roll = rng.random()
    if roll < 0.4:
        return "Under Review"
    # Resolved: use the real label to simulate the reviewer's finding.
    if row["actual_class"] == 1:
        return "Confirmed Fraud"
    return "Cleared"


def build_fact(clean: pd.DataFrame, scored: pd.DataFrame,
               insights: pd.DataFrame) -> pd.DataFrame:
    """Assemble the central fact table."""
    base = scored.merge(
        clean[
            [
                "transaction_id",
                "transaction_datetime",
                "transaction_hour",
                "day_index",
                "Amount",
                "amount_band",
            ]
        ],
        on="transaction_id",
        how="left",
    )

    base["transaction_datetime"] = pd.to_datetime(base["transaction_datetime"])
    base["date_key"] = base["transaction_datetime"].dt.strftime("%Y%m%d").astype(int)

    # Simulated review status (reproducible).
    rng = np.random.default_rng(config.RANDOM_STATE)
    base = base.rename(columns={"actual_class": "actual_class"})
    base["review_status"] = base.apply(lambda r: _review_status(r, rng), axis=1)

    # Simulated illustrative attributes.
    base["customer_segment"] = [
        _stable_choice(t + "seg", CUSTOMER_SEGMENTS) for t in base["transaction_id"]
    ]
    base["region"] = [
        _stable_choice(t + "reg", REGIONS) for t in base["transaction_id"]
    ]

    # Investigation priority from the agent where available, else rule-based.
    if len(insights):
        prio = insights.set_index("transaction_id")["investigation_priority"].to_dict()
    else:
        prio = {}
    base["investigation_priority"] = base.apply(
        lambda r: prio.get(
            r["transaction_id"],
            "HIGH" if r["risk_band"] == "High"
            else "MEDIUM" if r["risk_band"] == "Medium"
            else "LOW",
        ),
        axis=1,
    )

    fact = base[
        [
            "transaction_id",
            "transaction_datetime",
            "date_key",
            "transaction_hour",
            "Amount",
            "amount_band",
            "actual_class",
            "risk_score",
            "risk_band",
            "anomaly_flag",
            "review_status",
            "investigation_priority",
            "customer_segment",
            "region",
        ]
    ].rename(columns={"Amount": "amount"})
    return fact


def build_dim_date(fact: pd.DataFrame) -> pd.DataFrame:
    dt = pd.to_datetime(fact["transaction_datetime"])
    dim = pd.DataFrame({"date_key": fact["date_key"].unique()})
    dim = dim.sort_values("date_key").reset_index(drop=True)
    parsed = pd.to_datetime(dim["date_key"].astype(str), format="%Y%m%d")
    dim["date"] = parsed.dt.strftime("%Y-%m-%d")
    dim["day"] = parsed.dt.day
    dim["month"] = parsed.dt.month
    dim["month_name"] = parsed.dt.strftime("%B")
    dim["year"] = parsed.dt.year
    dim["day_name"] = parsed.dt.strftime("%A")
    return dim


def build_dim_risk_band() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "risk_band": ["Low", "Medium", "High"],
            "sort_order": [1, 2, 3],
            "color_hex": ["#2E7D32", "#F9A825", "#C62828"],  # green / amber / red
        }
    )


def build_dim_review_status() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "review_status": [
                "Not flagged",
                "Flagged",
                "Under Review",
                "Cleared",
                "Confirmed Fraud",
            ],
            "sort_order": [0, 1, 2, 3, 4],
        }
    )


def build_dim_priority() -> pd.DataFrame:
    return pd.DataFrame(
        {"priority": ["LOW", "MEDIUM", "HIGH"], "sort_order": [1, 2, 3]}
    )


def build_model_metrics() -> pd.DataFrame:
    """Flatten reports/metrics.json into a tidy metric/value table."""
    if not config.METRICS_JSON.exists():
        return pd.DataFrame(columns=["metric", "value"])
    with open(config.METRICS_JSON) as f:
        report = json.load(f)
    sm = report["selected_metrics"]
    rows = [
        ("Selected Model", report["selected_model_name"]),
        ("Precision", round(sm["precision"], 4)),
        ("Recall", round(sm["recall"], 4)),
        ("F1 Score", round(sm["f1"], 4)),
        ("AUC-ROC", round(sm["auc_roc"], 4)),
        ("AUC-PR", round(sm["auc_pr"], 4)),
        ("True Positives", sm["confusion_matrix"]["true_positive"]),
        ("False Positives", sm["confusion_matrix"]["false_positive"]),
        ("False Negatives", sm["confusion_matrix"]["false_negative"]),
        ("True Negatives", sm["confusion_matrix"]["true_negative"]),
        ("Rows (total)", report["n_rows_total"]),
        ("Train rows", report["n_train"]),
        ("Test rows", report["n_test"]),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def run():
    config.ensure_dirs()
    clean = pd.read_csv(config.CLEAN_CSV)
    scored = pd.read_csv(config.SCORED_CSV)
    insights = (
        pd.read_csv(config.AI_INSIGHTS_CSV)
        if config.AI_INSIGHTS_CSV.exists()
        else pd.DataFrame(columns=["transaction_id", "investigation_priority"])
    )

    fact = build_fact(clean, scored, insights)
    fact.to_csv(config.FACT_TRANSACTIONS_CSV, index=False)
    build_dim_date(fact).to_csv(config.DIM_DATE_CSV, index=False)
    build_dim_risk_band().to_csv(config.DIM_RISK_BAND_CSV, index=False)
    build_dim_review_status().to_csv(config.DIM_REVIEW_STATUS_CSV, index=False)
    build_dim_priority().to_csv(config.DIM_PRIORITY_CSV, index=False)
    build_model_metrics().to_csv(config.MODEL_METRICS_CSV, index=False)

    print(
        f"[bi] wrote fact_transactions.csv ({len(fact):,} rows) + "
        f"dim_date, dim_risk_band, dim_review_status, dim_priority, model_metrics"
    )
    return fact


if __name__ == "__main__":
    run()
