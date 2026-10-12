"""
Module 4 — AI Risk Investigation Agent (runner)

Pipeline:
  1. Build per-transaction EVIDENCE from the scored + clean data, including
     historical fraud rates for the transaction's amount band and hour
     (computed in Python from the dataset — not invented).
  2. Select the highest-risk transactions (Medium/High) up to a configurable
     cap to control LLM cost.
  3. Ask the LLM (Anthropic Claude) to return a validated JSON recommendation.
     Guardrails: schema validation + retries + a rule-based priority floor.
  4. If no API key is configured (or AGENT_FORCE_OFFLINE=true), use the
     offline template agent so the pipeline still runs end-to-end.
  5. Write data/output/AI_Risk_Insights.csv for Power BI.

Run standalone (after score):
    python -m src.agent.investigate
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

from src import config
from src.agent import prompt as P

# Load .env so standalone `python -m src.agent.investigate` sees the keys.
load_dotenv(config.PROJECT_ROOT / ".env")


# --------------------------------------------------------------------------
# Evidence construction
# --------------------------------------------------------------------------
def _historical_fraud_rates(clean: pd.DataFrame) -> tuple[dict, dict]:
    """Fraud rate per amount_band and per hour, from the actual labels."""
    by_band = clean.groupby("amount_band")["Class"].mean().to_dict()
    by_hour = clean.groupby("transaction_hour")["Class"].mean().to_dict()
    return by_band, by_hour


def build_evidence(clean: pd.DataFrame, scored: pd.DataFrame) -> pd.DataFrame:
    """Join scored + clean and attach the fields the agent needs."""
    cols = [
        "transaction_id",
        "Time",
        "Amount",
        "amount_band",
        "transaction_hour",
    ]
    merged = scored.merge(clean[cols], on="transaction_id", how="left")

    by_band, by_hour = _historical_fraud_rates(clean)
    merged["hist_fraud_rate_amount_band"] = merged["amount_band"].map(by_band)
    merged["hist_fraud_rate_hour"] = merged["transaction_hour"].map(by_hour)
    return merged


def _review_status(risk_band: str) -> str:
    """Simulated analyst-workflow status (labelled simulated in the dashboard)."""
    return "Flagged" if risk_band in {"Medium", "High"} else "Not flagged"


def evidence_record(row: pd.Series) -> dict:
    """Build the structured evidence dict for one transaction."""
    try:
        anomalies = json.loads(row["anomaly_indicators"])
    except (TypeError, ValueError):
        anomalies = []
    floor = P.priority_floor(
        risk_score=float(row["risk_score"]),
        amount=float(row["Amount"]),
        anomaly_count=len(anomalies),
    )
    return {
        "transaction_id": row["transaction_id"],
        "amount": round(float(row["Amount"]), 2),
        "time_seconds": int(row["Time"]),
        "transaction_hour": int(row["transaction_hour"]),
        "risk_score": round(float(row["risk_score"]), 4),
        "risk_band": row["risk_band"],
        "historical_fraud_rate_amount_band": round(
            float(row["hist_fraud_rate_amount_band"]), 5
        ),
        "historical_fraud_rate_hour": round(float(row["hist_fraud_rate_hour"]), 5),
        "anomaly_indicators": anomalies,
        "anomaly_count": len(anomalies),
        "review_status": _review_status(row["risk_band"]),
        "priority_floor": floor,
    }


def select_transactions(evidence: pd.DataFrame, max_n: int) -> pd.DataFrame:
    """Highest-risk first; focus the LLM budget on Medium/High transactions."""
    candidates = evidence[evidence["risk_band"].isin(["Medium", "High"])].copy()
    candidates = candidates.sort_values("risk_score", ascending=False)
    if max_n > 0:
        candidates = candidates.head(max_n)
    return candidates


# --------------------------------------------------------------------------
# Agents
# --------------------------------------------------------------------------
class OfflineTemplateAgent:
    """
    Deterministic, evidence-based agent used when no LLM key is available.
    It is NOT a random mock: it composes a recommendation strictly from the
    supplied evidence using the same rules the LLM is asked to follow.
    """

    name = "offline-template"

    def investigate(self, evidence: dict) -> dict:
        score = evidence["risk_score"]
        floor = evidence["priority_floor"]
        anomalies = evidence["anomaly_indicators"]
        amount = evidence["amount"]

        classification = (
            "HIGH" if score >= config.RISK_HIGH_MIN
            else "MEDIUM" if score >= config.RISK_LOW_MAX
            else "LOW"
        )
        if classification == "HIGH":
            action, attention = "Escalate for Review", "Critical"
        elif classification == "MEDIUM":
            action, attention = "Hold", "Elevated"
        else:
            action, attention = "Approve", "Normal"

        if anomalies:
            feats = ", ".join(
                f"{a['feature']} ({a['deviation']})" for a in anomalies[:3]
            )
            anomaly_phrase = f"anomalous patterns in {feats}"
        else:
            anomaly_phrase = "no strong feature-level anomalies"

        reason = (
            f"ML risk score {score:.2f} ({evidence['risk_band']} band); "
            f"{anomaly_phrase}; historical fraud rate for the "
            f"{evidence['historical_fraud_rate_amount_band']:.3%} amount band "
            f"and {evidence['historical_fraud_rate_hour']:.3%} for hour "
            f"{evidence['transaction_hour']}; amount {amount:.2f}."
        )
        recommendation = {
            "Escalate for Review": "Escalate to a human analyst for manual review before settlement.",
            "Hold": "Place a temporary hold and request secondary verification.",
            "Approve": "No action required; approve and continue monitoring.",
        }[action]

        out = {
            "risk_classification": classification,
            "investigation_priority": classification,
            "attention_level": attention,
            "suggested_action": action,
            "investigation_recommendation": recommendation,
            "reason": reason,
        }
        return P.enforce_priority_floor(out, floor)


class AnthropicAgent:
    """Real LLM agent backed by the Anthropic Claude API."""

    def __init__(self, api_key: str, model: str, max_retries: int = 2):
        import anthropic  # imported lazily so the offline path needs no SDK

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.name = model
        self.max_retries = max_retries

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Pull the first JSON object out of the model's text response."""
        text = text.strip()
        # Strip accidental markdown fences.
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("no JSON object found in response")
        return json.loads(match.group(0))

    def investigate(self, evidence: dict) -> dict:
        user_prompt = P.build_user_prompt(evidence)
        last_err = None
        for _ in range(self.max_retries + 1):
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                temperature=0.0,
                system=P.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = resp.content[0].text
            try:
                parsed = self._extract_json(text)
            except ValueError as e:
                last_err = str(e)
                continue
            ok, errors = P.validate_output(parsed)
            if ok:
                return P.enforce_priority_floor(parsed, evidence["priority_floor"])
            last_err = "; ".join(errors)
        raise RuntimeError(f"LLM failed schema validation: {last_err}")


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model's text response."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("no JSON object found in response")
    return json.loads(match.group(0))


class RateLimitError(Exception):
    """Raised when the provider signals a rate/quota limit (HTTP 429)."""


class GeminiAgent:
    """Real LLM agent backed by the Google Gemini API (free-tier friendly)."""

    def __init__(self, api_key: str, model: str, max_retries: int = 2):
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=api_key)
        self._genai = genai
        self.model_id = model
        self.name = f"google/{model}"
        self.max_retries = max_retries
        self._model = genai.GenerativeModel(
            model_name=model,
            system_instruction=P.SYSTEM_PROMPT,
        )

    def investigate(self, evidence: dict) -> dict:
        from google.api_core import exceptions as gexc

        user_prompt = P.build_user_prompt(evidence)
        last_err = None
        for _ in range(self.max_retries + 1):
            try:
                resp = self._model.generate_content(
                    user_prompt,
                    generation_config={
                        "temperature": 0.0,
                        "max_output_tokens": 600,
                        "response_mime_type": "application/json",
                    },
                    request_options={"timeout": 60},
                )
            except (gexc.ResourceExhausted, gexc.TooManyRequests) as e:
                raise RateLimitError(str(e)) from e
            except gexc.GoogleAPICallError as e:
                last_err = f"api error: {e}"
                continue

            try:
                parsed = _extract_json(resp.text)
            except (ValueError, AttributeError) as e:
                last_err = str(e)
                continue
            ok, errors = P.validate_output(parsed)
            if ok:
                return P.enforce_priority_floor(parsed, evidence["priority_floor"])
            last_err = "; ".join(errors)
        raise RuntimeError(f"LLM failed schema validation: {last_err}")


def build_agent():
    """Pick the LLM agent based on LLM_PROVIDER and available keys."""
    s = config.agent_settings()
    if s["force_offline"]:
        print("[agent] using OfflineTemplateAgent (forced offline).")
        return OfflineTemplateAgent()

    provider = s["provider"]
    if provider == "google" and s["google_api_key"]:
        print(f"[agent] using GeminiAgent (model={s['gemini_model']}).")
        return GeminiAgent(api_key=s["google_api_key"], model=s["gemini_model"])
    if provider == "anthropic" and s["anthropic_api_key"]:
        print(f"[agent] using AnthropicAgent (model={s['anthropic_model']}).")
        return AnthropicAgent(api_key=s["anthropic_api_key"], model=s["anthropic_model"])

    # Fallback: try whichever key exists.
    if s["google_api_key"]:
        print(f"[agent] using GeminiAgent (model={s['gemini_model']}).")
        return GeminiAgent(api_key=s["google_api_key"], model=s["gemini_model"])
    if s["anthropic_api_key"]:
        print(f"[agent] using AnthropicAgent (model={s['anthropic_model']}).")
        return AnthropicAgent(api_key=s["anthropic_api_key"], model=s["anthropic_model"])

    print("[agent] using OfflineTemplateAgent (no API key configured).")
    return OfflineTemplateAgent()


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
MAX_RATE_LIMIT_WAITS = 30  # how many times to wait-out a 429 before giving up


def _retry_seconds(message: str) -> float:
    """Extract the server-suggested retry delay from a 429 message."""
    m = re.search(r"retry in ([0-9.]+)s", message)
    if m:
        return float(m.group(1)) + 2.0  # small buffer
    return 35.0  # safe default for a 15 requests/min limit


def _load_cache() -> dict:
    if config.AI_CACHE_JSON.exists():
        try:
            with open(config.AI_CACHE_JSON) as f:
                return json.load(f)
        except (ValueError, OSError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    with open(config.AI_CACHE_JSON, "w") as f:
        json.dump(cache, f)


def run(clean_path=None, scored_path=None):
    config.ensure_dirs()
    clean = pd.read_csv(clean_path or config.CLEAN_CSV)
    scored = pd.read_csv(scored_path or config.SCORED_CSV)

    settings = config.agent_settings()
    evidence_df = build_evidence(clean, scored)
    selected = select_transactions(evidence_df, settings["max_transactions"])

    agent = build_agent()
    interval = settings["request_interval"]
    is_llm = not isinstance(agent, OfflineTemplateAgent)

    cache = _load_cache() if is_llm else {}
    # Keep cached results from the same provider family. This lets us finish a
    # run with a different Gemini model (each model has its own daily quota)
    # without discarding work already done by another Gemini model.
    def _same_family(cached_name: str, agent_name: str) -> bool:
        if agent_name.startswith("google/") and cached_name.startswith("google/"):
            return True
        return cached_name == agent_name

    cache = {
        k: v for k, v in cache.items()
        if _same_family(v.get("model_name", ""), agent.name)
    }

    total = len(selected)
    print(
        f"[agent] investigating {total} transactions "
        f"(engine={agent.name}, cached={len(cache)}, interval={interval}s)..."
    )

    rows = []
    generated_at = datetime.now(timezone.utc).isoformat()
    rate_limited = False
    done = 0

    for _, row in selected.iterrows():
        ev = evidence_record(row)
        tid = ev["transaction_id"]

        if tid in cache:
            rows.append(cache[tid])
            done += 1
            continue

        # Call the agent, waiting out free-tier rate limits automatically.
        result = None
        rl_waits = 0
        err_tries = 0
        while result is None:
            try:
                result = agent.investigate(ev)
            except RateLimitError as e:
                wait_s = _retry_seconds(str(e))
                rl_waits += 1
                if rl_waits > MAX_RATE_LIMIT_WAITS:
                    rate_limited = True
                    print(
                        f"\n[agent] rate limit persisted after "
                        f"{MAX_RATE_LIMIT_WAITS} waits ({done}/{total} done)."
                    )
                    break
                print(
                    f"[agent]   rate limit at {done}/{total}; "
                    f"waiting {wait_s:.0f}s then resuming..."
                )
                _save_cache(cache)
                time.sleep(wait_s)
            except Exception as e:  # transient API/network/schema error
                err_tries += 1
                if err_tries > 3:
                    print(f"[agent]   skipping {tid} after errors: {str(e)[:120]}")
                    break
                time.sleep(3)
        if result is None:  # rate-limited out OR skipped this transaction
            if rate_limited:
                break
            continue

        record = {
            "transaction_id": tid,
            "risk_score": ev["risk_score"],
            "risk_band": ev["risk_band"],
            "anomaly_indicators": "; ".join(
                f"{a['feature']}:{a['deviation']}" for a in ev["anomaly_indicators"]
            ),
            "investigation_priority": result["investigation_priority"],
            "risk_classification": result["risk_classification"],
            "attention_level": result["attention_level"],
            "suggested_action": result["suggested_action"],
            "recommendation": result["investigation_recommendation"],
            "reason": result["reason"],
            "review_status": ev["review_status"],
            "model_name": agent.name,
            "generated_at": generated_at,
        }
        rows.append(record)
        done += 1

        if is_llm:
            cache[tid] = record
            if done % 10 == 0:
                _save_cache(cache)
                print(f"[agent]   {done}/{total} done...")
            if interval > 0:
                time.sleep(interval)

    if is_llm:
        _save_cache(cache)

    out = pd.DataFrame(rows)
    if len(out):
        out.to_csv(config.AI_INSIGHTS_CSV, index=False)

    priorities = out["investigation_priority"].value_counts().to_dict() if len(out) else {}
    print(
        f"[agent] wrote {config.AI_INSIGHTS_CSV}  "
        f"({len(out)} insights; priorities={priorities})"
    )

    if rate_limited:
        print(
            "\n[agent] *** Stopped early due to rate limiting. ***\n"
            "        Progress is cached — just run the agent again later to resume\n"
            "        (already-done transactions are skipped).\n"
            "        Free-tier options if this keeps happening:\n"
            "          * Gemini free tier: ~15 requests/min, ~1500/day. Wait and\n"
            "            re-run; the cache resumes. Lower-traffic model:\n"
            "            set GEMINI_MODEL=gemini-1.5-flash-8b in .env.\n"
            "          * Groq (free, very fast): llama-3.1-8b-instant / llama-3.3-70b.\n"
            "          * OpenRouter free models (e.g. meta-llama free tier).\n"
            "          * Hugging Face Inference API (free tier).\n"
            "        Send me whichever free key you can get and I'll wire it in.\n"
        )
    return out


if __name__ == "__main__":
    run()
