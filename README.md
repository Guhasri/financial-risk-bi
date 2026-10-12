# Financial Risk Intelligence System

**AI-Enhanced Financial Risk Intelligence System for Transaction Monitoring** — a
Business Intelligence project that extends a descriptive Power BI dashboard with
**ML-based transaction risk scoring** (Random Forest) and an **LLM-powered AI Risk
Investigation Agent**.

**Course:** 20MSSL10 – Business Intelligence Laboratory, Coimbatore Institute of Technology
**Team:** Guhasri R (7176 22 31 021), Deepika K (7176 22 31 012)

> New to the project? Read **`PLAN.md`** first — it explains the whole idea,
> every concept, and the architecture from zero. This README is the hands-on
> setup and run guide.

---

## What this system does

```
creditcard.csv → clean & engineer → Random Forest risk score → AI agent explains → CSVs → Power BI dashboard
     (Module 1)        (Module 1)          (Module 2)            (Module 4)      (Module 5)   (Module 3)
```

- **Python** does all the data, ML, and AI work and writes CSV files.
- **Power BI** reads those CSVs and shows everything as **one dashboard**.
- The AI agent's recommendations appear as **formatted visuals** (table + cards
  + drill-through), never as raw CSV.

---

## Who runs what

| You | OS | What you do |
|---|---|---|
| **Guhasri** | macOS | Run the Python pipeline → produces the CSVs in `data/output/` |
| **Teammate** | Windows | Build the Power BI `.pbix` from those CSVs (see `powerbi/POWERBI_BUILD_GUIDE.md`) |

Power BI Desktop is Windows-only, which is why the dashboard is built on the
Windows machine. Everything else runs on either OS.

---

## Project layout

```
bi-project/
├── PLAN.md                     ← the full concept/architecture explainer (read first)
├── README.md                   ← this file
├── requirements.txt            ← Python dependencies (pinned)
├── .env.example                ← copy to .env and add your API key
├── data/
│   ├── raw/creditcard.csv       ← input dataset (284,807 rows) — already present
│   ├── processed/               ← clean_transactions.csv (generated)
│   └── output/                  ← CSVs Power BI reads (generated)
├── src/
│   ├── config.py                ← paths + settings (single source of truth)
│   ├── features.py              ← the model feature list
│   ├── preprocess.py            ← Module 1: ETL + feature engineering
│   ├── train.py                 ← Module 2: train RF (class-weight vs SMOTE)
│   ├── score.py                 ← Module 2: score + risk bands + anomalies
│   ├── build_bi_tables.py       ← star-schema tables for Power BI
│   ├── run_pipeline.py          ← Module 5: one-command end-to-end
│   └── agent/
│       ├── prompt.py            ← Module 4: prompt, schema, guardrails
│       └── investigate.py       ← Module 4: LLM agent + offline fallback
├── models/                      ← rf_model.joblib, scaler.joblib (generated)
├── reports/                     ← metrics.json (generated)
├── powerbi/
│   ├── measures.dax             ← DAX measures to paste into Power BI
│   └── POWERBI_BUILD_GUIDE.md   ← click-by-click dashboard build guide
└── tests/                       ← pytest suite
```

---

## Part 1 — Setup on macOS (Guhasri)

### 1. Prerequisites
- Python 3.11–3.13 (check: `python3 --version`). If missing: `brew install python`.

### 2. Create the virtual environment and install dependencies
```bash
cd /Users/Guhasri/Desktop/bi-project
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Confirm the dataset is in place
The file `data/raw/creditcard.csv` should already exist (284,807 rows). Quick check:
```bash
wc -l data/raw/creditcard.csv        # ~284808 including the header
```
If it's missing, download it from Kaggle (`mlg-ulb/creditcardfraud`) and place
it at `data/raw/creditcard.csv`.

### 4. Configure the AI agent
```bash
cp .env.example .env
```
Open `.env` and set your **Google Gemini** key (free student tier):
```
LLM_PROVIDER=google
GOOGLE_API_KEY=...your Gemini key...
GEMINI_MODEL=gemini-flash-latest
AGENT_MAX_TRANSACTIONS=0        # 0 = all flagged (Medium/High) transactions
AGENT_REQUEST_INTERVAL=4.5      # spacing to respect the free-tier rate limit
AGENT_FORCE_OFFLINE=false
```
Get a free key at https://aistudio.google.com/app/apikey.

- **No key?** Set `AGENT_FORCE_OFFLINE=true` (or leave the key blank). The agent
  then uses a built-in offline template so the pipeline still runs end-to-end
  (clearly marked `model_name=offline-template` in the output).
- `AGENT_MAX_TRANSACTIONS=0` investigates **all** flagged transactions. The agent
  only sends Medium/High transactions to the LLM (the ~506 that matter); the
  283k Low-risk rows don't need AI investigation and would blow the free quota.

> **Security:** `.env` is git-ignored and holds your API key. **Before you zip
> the project to send your teammate, delete `.env` from the copy** (they build
> Power BI from CSVs and don't need the key).

### Free Gemini tier — rate limits (important)
The free tier has **two** limits that affect a full run:
- **~15 requests per minute** — the pipeline paces itself via
  `AGENT_REQUEST_INTERVAL` and auto-waits when throttled.
- **~500 requests per day, per model** — a full run of ~506 transactions is
  right at this edge. If you hit it, the agent prints a message and **saves
  progress to a resume cache** (`data/output/.agent_cache.json`).

**If you get rate-limited partway:** just run the agent again later —
already-done transactions are skipped and it resumes. Because each *model* has
its own daily quota, you can also switch `GEMINI_MODEL` to a different model to
finish the remainder immediately:
```bash
# finish whatever is left using a different model (fresh daily quota)
# edit GEMINI_MODEL in .env, then:
python -m src.agent.investigate      # resumes from the cache
python -m src.build_bi_tables        # refresh the Power BI tables
```

### Choosing a Gemini model your key can access
Not every key can use every model. List the ones yours can call:
```bash
python -c "import os;from dotenv import load_dotenv;load_dotenv('.env');import google.generativeai as g;g.configure(api_key=os.environ['GOOGLE_API_KEY']);[print(m.name) for m in g.list_models() if 'generateContent' in m.supported_generation_methods]"
```
Good free-tier picks: `gemini-flash-latest`, `gemini-3.1-flash-lite`,
`gemini-3-flash-preview`.

---

## Part 2 — Run the pipeline (macOS)

### One command (recommended)
```bash
source .venv/bin/activate
python -m src.run_pipeline
```
This runs: preprocess → train → score → AI agent → build BI tables, and writes a
`data/output/run_log.json` with timings, metrics, and reconciliation checks.

Useful flags:
```bash
python -m src.run_pipeline --skip-train    # reuse the existing model (faster)
python -m src.run_pipeline --skip-agent     # skip the LLM step
```

### Or run modules individually
```bash
python -m src.preprocess          # -> data/processed/clean_transactions.csv
python -m src.train               # -> models/*.joblib, reports/metrics.json
python -m src.score               # -> data/output/scored_transactions.csv
python -m src.agent.investigate   # -> data/output/AI_Risk_Insights.csv
python -m src.build_bi_tables     # -> data/output/fact_*, dim_*, model_metrics
```

### What you get in `data/output/` (these go to Power BI)
| File | Contents |
|---|---|
| `fact_transactions.csv` | one row per transaction (amount, risk score/band, anomaly flag, review status, priority, simulated segment/region) |
| `dim_date.csv`, `dim_risk_band.csv`, `dim_review_status.csv`, `dim_priority.csv` | dimension tables |
| `AI_Risk_Insights.csv` | the AI agent's recommendations + reasons |
| `model_metrics.csv` | precision/recall/F1/AUC for the model cards |
| `scored_transactions.csv` | raw per-transaction scores (reference) |
| `run_log.json` | run metadata + reconciliation checks |

### Run the tests
```bash
python -m pytest -q
```

---

## Part 3 — Build the dashboard on Windows (teammate)

The teammate needs only the `data/output/` folder and the `powerbi/` folder.

1. Install **Power BI Desktop** (free, Microsoft Store / https://aka.ms/pbidesktopstore).
2. Open **`powerbi/POWERBI_BUILD_GUIDE.md`** and follow it step by step:
   import the CSVs, set relationships, paste the DAX from `powerbi/measures.dax`,
   build the two dashboard pages, and save `FRI.pbix`.
3. Expected sanity numbers are listed in the guide (Total Transactions ≈ 283,726,
   Fraud Rate ≈ 0.167%, etc.).

That guide is self-contained — the teammate does **not** need Python or any of
the ML details to build the dashboard.

---

## Part 4 — Configuration reference (`.env`)

| Variable | Default | Meaning |
|---|---|---|
| `LLM_PROVIDER` | `google` | `google` (Gemini) or `anthropic` (Claude). |
| `GOOGLE_API_KEY` | (empty) | Google Gemini key. Empty → offline template agent. |
| `GEMINI_MODEL` | `gemini-flash-latest` | Gemini model the agent calls. |
| `ANTHROPIC_API_KEY` | (empty) | Anthropic key (only if `LLM_PROVIDER=anthropic`). |
| `LLM_MODEL` | `claude-3-5-haiku-20241022` | Claude model. |
| `AGENT_MAX_TRANSACTIONS` | `0` | Max flagged transactions sent to the LLM (`0` = all). |
| `AGENT_REQUEST_INTERVAL` | `4.5` | Seconds between LLM calls (free-tier pacing). |
| `AGENT_FORCE_OFFLINE` | `false` | `true` → always use the offline template (zero cost). |

---

## How the design stays honest (important for the report)

- **No fabricated data.** The dataset has no customer identity, location, or
  merchant. `review_status`, `customer_segment`, and `region` are **simulated**
  and are labelled "Illustrative / Simulated" on every dashboard visual.
- **No data leakage.** The train/test split happens first; the scaler and SMOTE
  are fit on training data only; rolling features use only past rows.
- **Honest metrics.** At 0.172% fraud, accuracy is meaningless, so we report
  Precision, Recall, F1, AUC-ROC, AUC-PR, and a confusion matrix.
- **AI guardrails.** The agent uses only the supplied evidence, returns a
  validated JSON schema, and a rule-based priority floor prevents it from
  under-rating risky transactions. The anonymised V-features are described as
  "anomalous pattern", never given a business meaning.
- **Decision support only.** The system advises a human; it never auto-blocks
  or freezes anything.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Raw dataset not found` | Put `creditcard.csv` in `data/raw/`. |
| `Clean dataset not found` | Run `python -m src.preprocess` first. |
| Agent says "using OfflineTemplateAgent" but you set a key | Check `.env` is in the project root and `AGENT_FORCE_OFFLINE=false`; re-activate the venv. |
| Training is slow | It trains two models on ~227k rows (~3 min is normal). Use `--skip-train` on later runs. |
| Power BI measure errors | Table names must match the guide exactly (`FactTransactions`, etc.). |
