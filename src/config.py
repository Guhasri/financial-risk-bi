"""
Central configuration: paths, constants, and tunable parameters.

Everything in the project imports paths from here so there is a single
source of truth. No business logic lives in this file.
"""
from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------
# Paths (all relative to the project root, so the project is portable)
# --------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

RAW_CSV = RAW_DIR / "creditcard.csv"
CLEAN_CSV = PROCESSED_DIR / "clean_transactions.csv"
SCORED_CSV = OUTPUT_DIR / "scored_transactions.csv"

# Model + report artifacts
MODEL_PATH = MODELS_DIR / "rf_model.joblib"
SCALER_PATH = MODELS_DIR / "scaler.joblib"
METRICS_JSON = REPORTS_DIR / "metrics.json"

# Power BI table outputs
FACT_TRANSACTIONS_CSV = OUTPUT_DIR / "fact_transactions.csv"
DIM_DATE_CSV = OUTPUT_DIR / "dim_date.csv"
DIM_RISK_BAND_CSV = OUTPUT_DIR / "dim_risk_band.csv"
DIM_REVIEW_STATUS_CSV = OUTPUT_DIR / "dim_review_status.csv"
DIM_PRIORITY_CSV = OUTPUT_DIR / "dim_priority.csv"
AI_INSIGHTS_CSV = OUTPUT_DIR / "AI_Risk_Insights.csv"
AI_CACHE_JSON = OUTPUT_DIR / ".agent_cache.json"
MODEL_METRICS_CSV = OUTPUT_DIR / "model_metrics.csv"
RUN_LOG_JSON = OUTPUT_DIR / "run_log.json"

# --------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.20

# --------------------------------------------------------------------------
# Feature engineering parameters
# --------------------------------------------------------------------------
# Synthetic anchor date so Time (seconds) can become a datetime for trend
# charts. This is a LABELLED synthetic anchor, not a real transaction date.
SYNTHETIC_START_DATE = "2013-09-01"

# Rolling window (in seconds) for volume-context and amount z-score features.
# The dataset has no per-customer id, so these are dataset-wide, past-rows-only
# context features (clearly documented as such).
ROLLING_WINDOW_SECONDS = 3600  # 1 hour of prior transactions
NIGHT_HOURS = set(range(0, 6))  # 00:00–05:59 counted as "night"

# Amount bands (currency units). Right-skewed data, so bands are coarse.
AMOUNT_BAND_EDGES = [0, 10, 100, 500, float("inf")]
AMOUNT_BAND_LABELS = ["Low (0-10)", "Mid (10-100)", "High (100-500)", "Very High (500+)"]

# --------------------------------------------------------------------------
# Risk band thresholds on the ML fraud probability (0-1).
# Starting point from the precision-recall analysis; documented in metrics.json.
# --------------------------------------------------------------------------
RISK_LOW_MAX = 0.30      # score  < 0.30            -> Low
RISK_HIGH_MIN = 0.70     # score >= 0.70            -> High
# between the two -> Medium

RISK_BANDS = ["Low", "Medium", "High"]

# --------------------------------------------------------------------------
# AI agent configuration (read from environment / .env)
# --------------------------------------------------------------------------
def _get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def agent_settings() -> dict:
    """Return agent settings resolved from environment variables."""
    force_offline = _get_env("AGENT_FORCE_OFFLINE", "false").lower() in {"1", "true", "yes"}
    try:
        max_tx = int(_get_env("AGENT_MAX_TRANSACTIONS", "300"))
    except ValueError:
        max_tx = 300
    try:
        req_interval = float(_get_env("AGENT_REQUEST_INTERVAL", "0"))
    except ValueError:
        req_interval = 0.0
    return {
        "provider": _get_env("LLM_PROVIDER", "google").lower(),
        "google_api_key": _get_env("GOOGLE_API_KEY", ""),
        "gemini_model": _get_env("GEMINI_MODEL", "gemini-1.5-flash"),
        "anthropic_api_key": _get_env("ANTHROPIC_API_KEY", ""),
        "anthropic_model": _get_env("LLM_MODEL", "claude-3-5-haiku-20241022"),
        "max_transactions": max_tx,
        "request_interval": req_interval,
        "force_offline": force_offline,
    }


def ensure_dirs() -> None:
    """Create all output directories if they do not exist."""
    for d in (PROCESSED_DIR, OUTPUT_DIR, MODELS_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
