"""
Tests for Module 4 (AI Risk Investigation Agent).

Focus: schema validation, the deterministic priority floor (which the LLM
may raise but never lower), and the offline agent's grounded output.
"""
import pytest

from src.agent import prompt as P
from src.agent.investigate import OfflineTemplateAgent


# --- priority floor rule -----------------------------------------------------
def test_priority_floor_high_for_high_score():
    assert P.priority_floor(0.95, amount=10, anomaly_count=0) == "HIGH"


def test_priority_floor_medium_for_mid_score():
    assert P.priority_floor(0.50, amount=10, anomaly_count=0) == "MEDIUM"


def test_priority_floor_low_for_low_score():
    assert P.priority_floor(0.05, amount=10, anomaly_count=0) == "LOW"


def test_priority_floor_escalates_large_anomalous_medium():
    # Medium score, large amount, anomalous -> bumped to HIGH.
    assert P.priority_floor(0.40, amount=900, anomaly_count=2) == "HIGH"


def test_enforce_priority_floor_raises_but_not_lowers():
    out = {"investigation_priority": "LOW"}
    P.enforce_priority_floor(out, "HIGH")
    assert out["investigation_priority"] == "HIGH"
    out2 = {"investigation_priority": "HIGH"}
    P.enforce_priority_floor(out2, "LOW")
    assert out2["investigation_priority"] == "HIGH"  # not lowered


# --- schema validation -------------------------------------------------------
def _valid_output():
    return {
        "risk_classification": "HIGH",
        "investigation_priority": "HIGH",
        "attention_level": "Critical",
        "suggested_action": "Escalate for Review",
        "investigation_recommendation": "Escalate to an analyst.",
        "reason": "High risk score and anomalous component V14.",
    }


def test_validate_accepts_good_output():
    ok, errors = P.validate_output(_valid_output())
    assert ok and errors == []


def test_validate_rejects_missing_field():
    bad = _valid_output()
    del bad["reason"]
    ok, errors = P.validate_output(bad)
    assert not ok and any("reason" in e for e in errors)


def test_validate_rejects_bad_enum():
    bad = _valid_output()
    bad["suggested_action"] = "Delete account"
    ok, errors = P.validate_output(bad)
    assert not ok


def test_validate_rejects_non_dict():
    ok, errors = P.validate_output("not json")
    assert not ok


# --- offline agent grounded output ------------------------------------------
def _evidence(score):
    return {
        "transaction_id": "TXN-000001",
        "amount": 850.0,
        "time_seconds": 1000,
        "transaction_hour": 2,
        "risk_score": score,
        "risk_band": "High" if score >= 0.7 else "Medium" if score >= 0.3 else "Low",
        "historical_fraud_rate_amount_band": 0.012,
        "historical_fraud_rate_hour": 0.004,
        "anomaly_indicators": [
            {"feature": "V14", "deviation": "strongly below typical range", "zscore": -6.1}
        ],
        "anomaly_count": 1,
        "review_status": "Flagged",
        "priority_floor": P.priority_floor(score, 850.0, 1),
    }


def test_offline_agent_output_passes_schema():
    agent = OfflineTemplateAgent()
    out = agent.investigate(_evidence(0.9))
    ok, errors = P.validate_output(out)
    assert ok, errors


def test_offline_agent_respects_floor():
    agent = OfflineTemplateAgent()
    out = agent.investigate(_evidence(0.9))
    assert out["investigation_priority"] == "HIGH"


def test_offline_agent_reason_cites_evidence():
    agent = OfflineTemplateAgent()
    out = agent.investigate(_evidence(0.9))
    # The reason must mention the score and the anomalous component (grounded).
    assert "0.90" in out["reason"]
    assert "V14" in out["reason"]
