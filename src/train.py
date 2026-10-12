"""
Module 2 — Machine Learning Risk Scoring (training)

Trains a Random Forest to predict fraud probability, comparing two
class-imbalance strategies on the UNTOUCHED test set:

    A) class_weight = "balanced_subsample"
    B) SMOTE oversampling (fit on the training split only)

The better model (by Average Precision / AUC-PR, the honest metric at
0.172% prevalence) is kept and saved alongside the fitted scaler and a
full metrics report.

Design rules enforced here:
  * Split FIRST, then fit scaler / apply SMOTE on train only (no leakage).
  * Stratified split preserves the rare-class ratio in both halves.
  * Accuracy is reported but never used to choose the model.

Run standalone (after preprocess):
    python -m src.train
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import joblib
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

from src import config
from src.features import FEATURE_COLUMNS, SCALE_COLUMNS, TARGET


# --------------------------------------------------------------------------
# Data loading & splitting
# --------------------------------------------------------------------------
def load_clean(path=None) -> pd.DataFrame:
    path = path or config.CLEAN_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"Clean dataset not found at {path}. Run `python -m src.preprocess` first."
        )
    return pd.read_csv(path)


def split(df: pd.DataFrame):
    """Stratified train/test split preserving the fraud ratio."""
    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET].astype(int).copy()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.TEST_SIZE,
        stratify=y,
        random_state=config.RANDOM_STATE,
    )
    return X_train, X_test, y_train, y_test


def fit_scaler(X_train: pd.DataFrame) -> RobustScaler:
    """Fit a RobustScaler on the training continuous columns only."""
    scaler = RobustScaler()
    scaler.fit(X_train[SCALE_COLUMNS])
    return scaler


def apply_scaler(scaler: RobustScaler, X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    X[SCALE_COLUMNS] = scaler.transform(X[SCALE_COLUMNS])
    return X


# --------------------------------------------------------------------------
# Model builders
# --------------------------------------------------------------------------
def _rf(class_weight=None) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight=class_weight,
        n_jobs=-1,
        random_state=config.RANDOM_STATE,
    )


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------
def evaluate(model, X_test, y_test, label: str) -> dict:
    """Compute honest metrics on the untouched test set."""
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    metrics = {
        "model": label,
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "auc_roc": float(roc_auc_score(y_test, proba)),
        "auc_pr": float(average_precision_score(y_test, proba)),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "threshold": 0.5,
    }
    return metrics


def pr_curve_summary(model, X_test, y_test) -> list[dict]:
    """A small precision/recall/threshold table to justify the risk bands."""
    proba = model.predict_proba(X_test)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_test, proba)
    summary = []
    for t in (0.10, 0.30, 0.50, 0.70, 0.90):
        idx = np.searchsorted(thresholds, t)
        idx = min(idx, len(precision) - 1)
        summary.append(
            {
                "threshold": t,
                "precision": float(precision[idx]),
                "recall": float(recall[idx]),
            }
        )
    return summary


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
def run(clean_path=None):
    config.ensure_dirs()
    df = load_clean(clean_path)
    X_train, X_test, y_train, y_test = split(df)

    scaler = fit_scaler(X_train)
    X_train_s = apply_scaler(scaler, X_train)
    X_test_s = apply_scaler(scaler, X_test)

    results = {}

    # --- Model A: class weighting ---
    print("[train] fitting Model A (class_weight=balanced_subsample)...")
    model_a = _rf(class_weight="balanced_subsample")
    model_a.fit(X_train_s, y_train)
    metrics_a = evaluate(model_a, X_test_s, y_test, "RandomForest + class_weight")
    results["class_weight"] = metrics_a
    print(
        f"        A: precision={metrics_a['precision']:.3f} "
        f"recall={metrics_a['recall']:.3f} f1={metrics_a['f1']:.3f} "
        f"auc_roc={metrics_a['auc_roc']:.4f} auc_pr={metrics_a['auc_pr']:.4f}"
    )

    # --- Model B: SMOTE ---
    print("[train] fitting Model B (SMOTE on train only)...")
    smote = SMOTE(random_state=config.RANDOM_STATE)
    X_res, y_res = smote.fit_resample(X_train_s, y_train)
    model_b = _rf(class_weight=None)
    model_b.fit(X_res, y_res)
    metrics_b = evaluate(model_b, X_test_s, y_test, "RandomForest + SMOTE")
    results["smote"] = metrics_b
    print(
        f"        B: precision={metrics_b['precision']:.3f} "
        f"recall={metrics_b['recall']:.3f} f1={metrics_b['f1']:.3f} "
        f"auc_roc={metrics_b['auc_roc']:.4f} auc_pr={metrics_b['auc_pr']:.4f}"
    )

    # --- Choose the better model by AUC-PR (best signal under imbalance) ---
    if metrics_b["auc_pr"] > metrics_a["auc_pr"]:
        best_key, best_model, best_metrics = "smote", model_b, metrics_b
    else:
        best_key, best_model, best_metrics = "class_weight", model_a, metrics_a
    print(f"[train] selected: {best_metrics['model']} (by AUC-PR)")

    # --- Persist ---
    joblib.dump(best_model, config.MODEL_PATH)
    joblib.dump(scaler, config.SCALER_PATH)

    report = {
        "selected_model": best_key,
        "selected_model_name": best_metrics["model"],
        "n_rows_total": int(len(df)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "n_frauds_total": int(df[TARGET].sum()),
        "features": FEATURE_COLUMNS,
        "risk_band_thresholds": {
            "low_max": config.RISK_LOW_MAX,
            "high_min": config.RISK_HIGH_MIN,
        },
        "comparison": results,
        "selected_metrics": best_metrics,
        "pr_curve": pr_curve_summary(best_model, X_test_s, y_test),
    }
    with open(config.METRICS_JSON, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[train] saved model -> {config.MODEL_PATH}")
    print(f"[train] saved scaler -> {config.SCALER_PATH}")
    print(f"[train] saved metrics -> {config.METRICS_JSON}")

    return report


if __name__ == "__main__":
    run()
