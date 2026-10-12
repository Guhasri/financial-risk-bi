"""
Module 4 — AI Risk Investigation Agent: prompt, schema, validation, guardrails.

This file holds the "contract" between our code and the LLM:
  * SYSTEM_PROMPT      — the agent's instructions and anti-hallucination rules
  * build_user_prompt  — turns one transaction's structured evidence into text
  * REQUIRED_FIELDS    — the JSON shape the LLM must return
  * validate_output    — rejects malformed / off-schema responses
  * priority_floor     — a deterministic rule the LLM may raise but NOT lower

Keeping all of this in one place makes the agent auditable and testable.
"""
from __future__ import annotations

import json

PRIORITIES = ("LOW", "MEDIUM", "HIGH")
RISK_CLASSES = ("LOW", "MEDIUM", "HIGH")
ACTIONS = ("Approve", "Hold", "Escalate for Review")
ATTENTION_LEVELS = ("Normal", "Elevated", "Critical")

REQUIRED_FIELDS = {
    "risk_classification": RISK_CLASSES,
    "investigation_priority": PRIORITIES,
    "attention_level": ATTENTION_LEVELS,
    "suggested_action": ACTIONS,
    # free-text fields validated for presence/non-emptiness only:
    "investigation_recommendation": None,
    "reason": None,
}

SYSTEM_PROMPT = """\
You are the AI Risk Investigation Agent inside a financial transaction \
monitoring system. A machine-learning model has already scored a transaction \
for fraud risk. Your job is NOT to re-score it, but to interpret the score \
together with the supplied evidence and produce a short, evidence-based \
investigation recommendation for a human analyst.

STRICT RULES:
1. Use ONLY the structured evidence provided in the user message. Do not \
invent customer identities, names, locations, merchants, devices, account \
history, or any fact that is not given to you.
2. The features V1..V28 are anonymised PCA components with NO real-world \
meaning. Refer to them only as "anonymised component Vx shows an anomalous \
pattern" — never assign them a business interpretation.
3. If the evidence is weak or ambiguous, say so plainly rather than \
overstating risk.
4. You MUST return a single valid JSON object and nothing else — no prose \
before or after, no markdown fences.
5. The JSON must contain exactly these keys:
   - "risk_classification": one of "LOW", "MEDIUM", "HIGH"
   - "investigation_priority": one of "LOW", "MEDIUM", "HIGH"
   - "attention_level": one of "Normal", "Elevated", "Critical"
   - "suggested_action": one of "Approve", "Hold", "Escalate for Review"
   - "investigation_recommendation": one sentence telling the analyst what to do
   - "reason": one to three sentences citing the specific evidence fields that \
drove your decision (e.g. the risk score, anomalous components, historical \
fraud rate for the amount/time band)
6. The system enforces a minimum investigation_priority by rule. You may \
match or exceed it, but a transaction already deemed HIGH by rule must remain \
HIGH. High-priority transactions always require human review.
"""


def build_user_prompt(evidence: dict) -> str:
    """Render one transaction's evidence as the user message."""
    return (
        "Investigate the following transaction and respond with the required "
        "JSON object only.\n\n"
        "TRANSACTION EVIDENCE:\n"
        f"{json.dumps(evidence, indent=2)}\n\n"
        f"RULE-ENFORCED MINIMUM PRIORITY: {evidence.get('priority_floor', 'LOW')}\n"
    )


def priority_floor(risk_score: float, amount: float, anomaly_count: int) -> str:
    """
    Deterministic minimum priority. The LLM may raise above this but never
    below it, giving the system predictable, auditable behaviour.
    """
    if risk_score >= 0.70:
        floor = "HIGH"
    elif risk_score >= 0.30:
        floor = "MEDIUM"
    else:
        floor = "LOW"

    # Escalate medium-risk, large, anomalous transactions.
    if floor == "MEDIUM" and amount >= 500 and anomaly_count >= 1:
        floor = "HIGH"
    return floor


def _rank(priority: str) -> int:
    return PRIORITIES.index(priority)


def enforce_priority_floor(output: dict, floor: str) -> dict:
    """Raise the agent's priority up to the floor if it tried to go lower."""
    if _rank(output.get("investigation_priority", "LOW")) < _rank(floor):
        output["investigation_priority"] = floor
    return output


def validate_output(output) -> tuple[bool, list[str]]:
    """Check the LLM output against the required schema. Returns (ok, errors)."""
    errors: list[str] = []
    if not isinstance(output, dict):
        return False, ["output is not a JSON object"]

    for field, allowed in REQUIRED_FIELDS.items():
        if field not in output:
            errors.append(f"missing field: {field}")
            continue
        value = output[field]
        if allowed is None:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"field '{field}' must be a non-empty string")
        else:
            if value not in allowed:
                errors.append(
                    f"field '{field}'='{value}' not in allowed {allowed}"
                )
    return (len(errors) == 0), errors
