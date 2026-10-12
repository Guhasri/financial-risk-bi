"""
Module 5 — Integration Pipeline

One command runs the whole chain and writes everything Power BI needs:

    preprocess -> train (optional) -> score -> AI agent -> BI tables -> run_log

Usage:
    python -m src.run_pipeline                # full run, trains if no model
    python -m src.run_pipeline --skip-train   # reuse an existing model
    python -m src.run_pipeline --skip-agent   # skip the LLM step

Reads .env automatically (for the agent's API key and settings).
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

from src import build_bi_tables, config, preprocess, score, train
from src.agent import investigate


def _count(path):
    return int(len(pd.read_csv(path))) if path.exists() else 0


def main():
    load_dotenv(config.PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(description="Financial Risk Intelligence pipeline")
    parser.add_argument("--skip-train", action="store_true",
                        help="reuse the existing trained model")
    parser.add_argument("--skip-agent", action="store_true",
                        help="skip the AI Risk Investigation Agent step")
    args = parser.parse_args()

    config.ensure_dirs()
    started = time.time()
    log = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "steps": {},
    }

    # 1. Preprocess ---------------------------------------------------------
    t = time.time()
    preprocess.run()
    log["steps"]["preprocess"] = {
        "seconds": round(time.time() - t, 1),
        "clean_rows": _count(config.CLEAN_CSV),
    }

    # 2. Train --------------------------------------------------------------
    if args.skip_train and config.MODEL_PATH.exists():
        print("[pipeline] skipping training (reusing existing model).")
        with open(config.METRICS_JSON) as f:
            report = json.load(f)
        log["steps"]["train"] = {"skipped": True, "selected_model": report["selected_model_name"]}
    else:
        t = time.time()
        report = train.run()
        log["steps"]["train"] = {
            "seconds": round(time.time() - t, 1),
            "selected_model": report["selected_model_name"],
            "metrics": report["selected_metrics"],
        }

    # 3. Score --------------------------------------------------------------
    t = time.time()
    score.run()
    scored = pd.read_csv(config.SCORED_CSV)
    log["steps"]["score"] = {
        "seconds": round(time.time() - t, 1),
        "risk_bands": scored["risk_band"].value_counts().to_dict(),
        "anomalies_flagged": int(scored["anomaly_flag"].sum()),
    }

    # 4. AI agent -----------------------------------------------------------
    if args.skip_agent:
        print("[pipeline] skipping AI agent step.")
        log["steps"]["agent"] = {"skipped": True}
    else:
        t = time.time()
        insights = investigate.run()
        log["steps"]["agent"] = {
            "seconds": round(time.time() - t, 1),
            "insights": int(len(insights)),
            "engine": insights["model_name"].iloc[0] if len(insights) else None,
            "priorities": insights["investigation_priority"].value_counts().to_dict()
            if len(insights) else {},
        }

    # 5. BI tables ----------------------------------------------------------
    t = time.time()
    fact = build_bi_tables.run()
    log["steps"]["bi_tables"] = {
        "seconds": round(time.time() - t, 1),
        "fact_rows": int(len(fact)),
    }

    # 6. Reconciliation checks ---------------------------------------------
    clean = pd.read_csv(config.CLEAN_CSV)
    checks = {
        "fact_rows_equal_clean_rows": int(len(fact)) == int(len(clean)),
        "fraud_count_clean": int(clean["Class"].sum()),
        "fraud_count_fact": int(fact["actual_class"].sum()),
        "fraud_counts_match": int(clean["Class"].sum()) == int(fact["actual_class"].sum()),
    }
    log["reconciliation"] = checks

    log["finished_at"] = datetime.now(timezone.utc).isoformat()
    log["total_seconds"] = round(time.time() - started, 1)

    with open(config.RUN_LOG_JSON, "w") as f:
        json.dump(log, f, indent=2)

    print("\n=== PIPELINE COMPLETE ===")
    print(f"Total time: {log['total_seconds']}s")
    print(f"Reconciliation: {checks}")
    print(f"Run log: {config.RUN_LOG_JSON}")
    print("Power BI inputs ready in: data/output/")


if __name__ == "__main__":
    main()
