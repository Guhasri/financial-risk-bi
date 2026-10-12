# Financial Risk Intelligence System — Project Plan

**Course:** 20MSSL10 – Business Intelligence Laboratory (Coimbatore Institute of Technology)
**Team:** Guhasri R (7176 22 31 021), Deepika K (7176 22 31 012)
**Program:** M.Sc. Software Systems

> **How to read this document:** You do not need any prior knowledge — not even the project title. Read top to bottom. Every term is explained the first time it appears. By the end you will understand *what* we are building, *why*, *how the pieces connect*, and *who does what*. The Python side (Modules 1, 2, 4, 5) is **built and runs**; the Power BI dashboard (Module 3) is built on Windows from the prepared files. See §4.5 for the current status and real results.

---

## PART 1 — UNDERSTAND THE PROJECT (start here)

### 1.1 What is this project, in one plain paragraph?

Banks process millions of card transactions. A tiny fraction are **fraud** (stolen card, etc.). We are building a system that (1) **shows** the transaction activity in a dashboard, (2) uses **machine learning** to give every transaction a **risk score** (how likely it is to be fraud), and (3) uses an **AI agent** (powered by a large language model, like the tech behind ChatGPT/Claude) to **explain in plain English why a transaction looks risky and what a human analyst should do about it**. All three results appear together in **one dashboard**.

### 1.2 The three layers — the heart of the idea

Think of three questions a bank analyst asks, and which part of our system answers each:

| Layer | The question it answers | What it is | Jargon term |
|---|---|---|---|
| **BI** (Business Intelligence) | *What happened?* | Charts and numbers summarising past transactions | **Descriptive** analytics |
| **ML** (Machine Learning) | *Which transactions are likely risky?* | A model that scores each transaction 0–1 | **Predictive** analytics |
| **AI Agent** (LLM) | *Why is this one risky, and what do I do?* | A program that uses an AI language model to write an explanation + recommendation | **Decision-support** / Generative AI |

- **BI** = turning raw data into charts. "BI" just means dashboards/reports that tell you what already happened. The tool for this is **Power BI** (a Microsoft dashboard app).
- **ML** = a computer program that learns patterns from past examples. Here it learns what fraud "looks like" from thousands of past labelled transactions, then scores new ones.
- **LLM** (Large Language Model) = the kind of AI that reads and writes human language (e.g., Claude, GPT). Our **AI agent** feeds the model the facts about a risky transaction and asks it to write a short, evidence-based explanation and a recommended action.

### 1.3 The closed loop (how data flows through the system)

The whole system is a loop: **DATA → BI → ML → AI DECISION → BI.** Raw data comes in; it's cleaned; the dashboard shows it; ML scores it; the AI agent explains the risky ones; and those explanations flow *back into the same dashboard* so the analyst sees analytics and advice side by side.

```
          creditcard.csv  (raw transactions)
                   │
                   ▼
          Data Cleaning / ETL                     ← Module 1 (Python)
                   │
                   ▼
          Feature Engineering → Random Forest      ← Module 2 (Python ML)
                   │   (produces a risk score 0–1 per transaction)
                   ▼
          AI Risk Investigation Agent (LLM)         ← Module 4 (Python + AI)
                   │   (writes "why risky + what to do")
                   ▼
          CSV files  (clean data + risk scores + AI explanations)   ← Module 5 glues it all
                   │
                   ▼
          Power BI reads the CSV files              ← Module 3 (dashboard)
                   │
                   ▼
          ONE dashboard: transactions + risk scores + AI advice
```

### 1.4 The most important design decisions (read these — they explain the whole architecture)

These four decisions define how everything fits together. If you understand only one section, understand this one.

1. **ONE dashboard, not two.** All results — transactions, ML risk scores, and AI explanations — appear in a **single Power BI dashboard** with multiple pages. We do **not** build a separate app for the AI/ML part.

2. **CSV files are the bridge between Python and Power BI.** The ML and AI work happens in **Python**, *before* the dashboard opens. Python saves its results as plain **CSV files** (spreadsheet-style text files). Power BI then simply **reads those CSV files** like any normal data source. There is no live link — Python runs first and writes the files; Power BI reads them. This is deliberate: Power BI never runs the ML model or calls the AI; it only *displays* results. (This also means we don't need any paid Power BI "AI" features.)

3. **AI results are shown as proper visuals, never as raw CSV.** The CSV is just the plumbing. In the dashboard, the AI agent's output becomes a formatted **table** (Transaction ID · Risk Score · Priority · Recommendation · Reason), **KPI cards** (e.g., "High priority: 42"), and a **drill-through page** (click a transaction → see its full explanation nicely laid out). The audience sees polished visuals, not a spreadsheet.

4. **No fabricated data or results.** The dataset is anonymised and has **no customer names, no location, no merchant, no device info**. Anything we show for those (e.g., "risk by region") is clearly stamped **"Illustrative / Simulated"**. We only report model accuracy and risk numbers *after we actually compute them* — never made-up figures.

### 1.5 Who builds what, and on which computer

| Part | Language/Tool | Where it's built | Who |
|---|---|---|---|
| Modules 1, 2, 4, 5 (data, ML, AI agent, pipeline) | Python | **Mac** (Guhasri's machine) | Us, together |
| Module 3 — the Power BI `.pbix` dashboard | Power BI Desktop | **Windows** (teammate's machine) | Teammate, using the guide we prepare |

**Why the split?** Power BI Desktop is **Windows-only** — it cannot run on a Mac. Guhasri is on a Mac; the teammate has Windows + Power BI. So we do all the Python/data/AI work on the Mac and produce ready-to-use CSV files + a step-by-step build guide; the teammate opens Power BI on Windows and builds the actual dashboard from those files.

### 1.6 About the `.pbix` file (important, honest note)

A `.pbix` is the Power BI dashboard file. It is a **proprietary binary** that only Power BI Desktop (on Windows) can create reliably. It **cannot be hand-written or script-generated on a Mac** — a fake one would fail to open. So the plan is:

- On the Mac we prepare: the **final CSV files**, a **`measures.dax`** file (formulas to copy-paste into Power BI), and a **`POWERBI_BUILD_GUIDE.md`** — a click-by-click guide so the teammate can rebuild every visual even if they've never seen the project.
- On Windows the teammate: imports the CSVs, pastes the formulas, follows the guide, and saves the real `.pbix`. Takes roughly an hour.
- The **build guide Markdown is the safety net**: if the `.pbix` ever breaks or won't open, anyone can recreate the whole dashboard by following it. (We may also attempt a best-effort text-based `.pbip` project format as a bonus, but the guide is the reliable path.)

### 1.7 What we are NOT building (scope limits, from the abstract)

- **Not** a real-time system that blocks transactions or freezes funds. It only *advises* a human. (Decision support, not enforcement.)
- **Not** a multi-model or multi-agent system. Exactly **one** ML model (Random Forest) and **one** AI agent.
- **Not** an identity/customer investigation tool — the data has no identities. We analyse *transactions*, not people.
- **Not** a second web app/frontend. Power BI is the only frontend. (Streamlit was considered and **dropped** — the teammate's Power BI covers it.)

---

## PART 2 — THE DATA (what we're working with)

### 2.1 The dataset

**Credit Card Fraud Detection dataset** (Kaggle, published by the ULB Machine Learning Group). It contains **284,807** real card transactions by European cardholders over 2 days in September 2013. Of these, **492 are fraud** — only **0.172%**. That extreme imbalance is the central challenge (see 2.4).

**Status: already downloaded and verified.** The file is at `data/raw/creditcard.csv` (≈150 MB). We checked it (read-only) and confirmed:
- **284,807** data rows ✅
- **31** columns ✅
- **492** fraud rows (`Class = 1`), i.e. 0.172% ✅
- No missing values ✅

So there is nothing left to download. (If anyone needs to re-download: Kaggle → `mlg-ulb/creditcardfraud`.)

### 2.2 Why the columns look like gibberish (V1–V28)

The dataset has 31 columns. Most are named `V1, V2 … V28` and are just numbers with no obvious meaning. Here's why:

The bank couldn't publish real card details (privacy law). So they ran the original sensitive columns (things like merchant, location, channel — never disclosed) through a math technique called **PCA (Principal Component Analysis)**. PCA mixes many correlated columns into new combined columns (`V1…V28`) that:
- carry the useful statistical signal,
- are **anonymous** (you can't reverse them to recover the originals),
- are ordered by importance (`V1` holds the most information, `V28` the least).

They look meaningless to a human but are still useful to a model, because fraud and genuine transactions sit in different regions of this transformed number-space. **Key consequence:** our AI agent must describe these as *"anomalous pattern in anonymised component V14,"* never pretend they mean a real-world thing.

### 2.3 The columns, explained

| Column | What it is | Real or transformed |
|---|---|---|
| `Time` | Seconds since the *first* transaction in the file (0 → ~172,792 = 2 days). Not a clock time. | **Real** |
| `V1`–`V28` | 28 anonymised PCA components. No human meaning individually. | PCA-transformed |
| `Amount` | The transaction amount (currency not stated). Very skewed — many small, a few huge. | **Real** |
| `Class` | **The answer we're trying to predict:** 1 = fraud, 0 = genuine. | **Real label** |

> `Class` is the **target** (the thing the model learns to predict). It is used only for *training and grading* the model — never as an input, because in real life you don't know it in advance.

### 2.4 The core challenge: class imbalance

Only 0.172% of rows are fraud. This breaks naive thinking:
- A lazy model that labels **everything "genuine"** would be **99.83% accurate** — and catch **zero fraud**. Useless.
- So **accuracy is a trap here.** We measure success differently (see Module 2 metrics), and we use special techniques (class weighting / SMOTE) so the model actually pays attention to the rare fraud cases.

### 2.5 Columns we create (not in the original file)

The raw data is thin, so Module 1 adds helper columns. Those marked **Simulated** are clearly labelled everywhere they appear.

| New column | Why we add it | Real or simulated |
|---|---|---|
| `transaction_id` (e.g. `TXN-000001`) | A unique ID per row — the dashboard and AI agent need one; the data has none | Generated key |
| `transaction_datetime` | A fake start date + the `Time` seconds, so we can draw time-trend charts | **Synthetic — labelled** |
| `transaction_hour`, `is_night` | Hour of day, night flag — fraud may cluster at certain hours | Derived from real `Time` |
| `amount_log`, `amount_band` | Tamed/bucketed version of `Amount` for charts and the model | Derived from real `Amount` |
| `rolling_txn_frequency` | How many transactions happened in the recent window before this one | Derived |
| `amount_zscore_recent` | How unusual this amount is vs recent amounts | Derived |
| `risk_score` | ML output: fraud probability 0–1 | Model output (Module 2) |
| `risk_band` | Low / Medium / High, from the score | Model output |
| `anomaly_flag`, `anomaly_indicators` | Whether/which features look abnormal | Model-derived |
| `investigation_priority` | HIGH / MEDIUM / LOW to-do level | Rule + agent |
| `review_status` | Flagged / Under Review / Cleared / Confirmed Fraud (a pretend analyst workflow) | **Simulated — labelled** |
| `customer_segment`, `region` | Only for the optional "by segment/region" charts | **Illustrative / Simulated — labelled** |
| `recommendation`, `reason`, `attention_level`, `suggested_action` | The AI agent's written output | AI-generated (Module 4) |

---

## PART 3 — THE MODULES (how we build it, step by step)

The project is split into 5 modules, matching the abstract. Modules 1–2 and 4–5 are Python (built on the Mac). Module 3 is the Power BI dashboard (built on Windows from our prepared files).

### Module 1 — Data Preparation (Python)

**Goal:** turn the raw CSV into a clean, enriched table everything else uses.

**Key concept — ETL** = **E**xtract (read the raw CSV) → **T**ransform (clean it, add the helper columns from 2.5) → **L**oad (save a tidy file).

Steps:
1. **Understand the data (EDA = Exploratory Data Analysis):** check shape, missing values, duplicates (there are ~1,081 duplicate rows), the class imbalance, the amount distribution, and how fraud differs from genuine on the strongest columns. We report only what we actually measure.
2. **Clean & validate:** remove duplicates; confirm `Amount ≥ 0` and `Class` is 0/1; tidy column names.
3. **Add helper columns** (2.5), being careful that time-based features use **only past rows** (so the model never "peeks" at the future — that would be cheating, called *data leakage*).
4. **Save** `data/processed/clean_transactions.csv`.

**Deliverables:** `src/preprocess.py` (ETL + feature engineering, with a printed EDA-style summary), `data/processed/clean_transactions.csv`, and the data dictionary in §2 of this document.

### Module 2 — Machine Learning Risk Scoring (Python)

**Goal:** give every transaction a `risk_score` (0–1) = probability it's fraud.

**Key concept — Random Forest** = a model made of many **decision trees** (flowchart-like yes/no questioners). Each tree sees a random slice of the data and makes a guess; the "forest" averages all their votes. This handles complex patterns well, resists over-fitting, and can tell us which features mattered most. We use it because we *have* labelled fraud examples (so a learning-from-labels model fits) and the patterns are non-linear (simpler models would miss them).

Steps:
1. **Train/test split (stratified 80/20).** "Stratified" means both the training and testing halves keep the same 0.172% fraud ratio, so the test is realistic. We split **first**, then do everything else on the training half only — again to prevent leakage.
2. **Handle imbalance** two ways and compare:
   - **Class weighting** — tell the model that mistakes on the rare fraud class cost more.
   - **SMOTE** — create synthetic extra fraud examples (training data only) so the model sees more fraud.
   We keep whichever scores better on the untouched test half, and document the comparison.
3. **Score every transaction** → `risk_score`, then bucket into `risk_band` (Low/Medium/High). The cut-offs are a *business choice* we pick from the results (lower cut-offs catch more fraud but raise false alarms).
4. **Anomaly indicators:** for each transaction, note which features deviate most from normal — this is what the AI agent will cite.
5. **Measure properly** (accuracy is useless here):

   | Metric | Plain meaning |
   |---|---|
   | **Precision** | Of the transactions we flagged, how many were truly fraud? (Low = analysts chase false alarms) |
   | **Recall** | Of all real frauds, how many did we catch? (Low = fraud slips through) |
   | **F1-score** | A balance of precision and recall — the headline number here |
   | **AUC-ROC** | How well the model ranks fraud above genuine across all thresholds |

   We also report **AUC-PR** and a **confusion matrix** (an honest breakdown of right/wrong on each class).

**Deliverables:** `src/train.py`, `src/score.py`, the saved model `models/rf_model.joblib` (+ `models/scaler.joblib`), `reports/metrics.json`, and `data/output/scored_transactions.csv`.

### Module 3 — The Power BI Dashboard (built on Windows)

**Goal:** one dashboard that shows transactions, risk scores, and AI advice together.

**Key concept — star schema.** Power BI likes data arranged as one central **fact table** (the rows of events — here, transactions with their numbers) surrounded by small **dimension tables** (descriptive lookups — dates, risk-band labels, etc.) joined by IDs. This keeps formulas simple and charts fast.

**Key concept — DAX.** The formula language in Power BI. A **measure** is a formula computed on the fly as you filter (e.g., "Fraud Rate %"). Example measures:
```DAX
Total Transactions = COUNTROWS ( FactTransactions )
Fraud Count        = CALCULATE ( COUNTROWS ( FactTransactions ), FactTransactions[actual_class] = 1 )
Fraud Rate %       = DIVIDE ( [Fraud Count], [Total Transactions] )
High Risk Count    = CALCULATE ( COUNTROWS ( FactTransactions ), FactTransactions[risk_band] = "High" )
```
(The full set goes in `powerbi/measures.dax` for the teammate to paste in.)

**The dashboard has two kinds of pages (one dashboard, multiple tabs):**

**Page group A — Financial Transaction BI** (what happened):
- **KPI cards:** Total Transactions · Total Amount · Flagged (Fraud) count · Fraud Rate % · Average Amount
- **Trends:** transaction volume over time, amount over time, peak hours
- **Risk overview:** Fraud vs Genuine donut, fraud rate over time, high-risk count
- **Amount analysis:** amount distribution, amount by risk band, average amount fraud-vs-genuine
- **Review status:** Flagged / Under Review / Cleared / Confirmed Fraud (simulated — labelled)
- *(Optional, clearly labelled Simulated:* risk by customer segment / region)

**Page group B — AI Risk Intelligence** (why + what to do) — the six indicators from the abstract:
- **Risk Score** distribution (Low/Med/High)
- **Anomaly Indicator** table
- **Risk Concentration** (share of high-risk in a time window)
- **Investigation Priority** counts (HIGH/MED/LOW)
- **Suggested Action** breakdown (Escalate / Hold / Approve)
- **Effective Risk Exposure** (money at risk above threshold, minus what's already cleared)
- Plus an **investigation table** (transaction · score · priority · **AI recommendation + reason**) and a **drill-through page** showing one transaction's full AI explanation.

**This is where the AI results live — as these visuals, not as raw CSV.** The AI agent's `AI_Risk_Insights.csv` is imported and displayed through the table, cards, and drill-through above.

**Every page carries a footer:** *"Source: public anonymised dataset. Dates, review status, and customer/region attributes are simulated/illustrative."*

**Deliverables (we prepare on Mac):** `powerbi/measures.dax`, `powerbi/POWERBI_BUILD_GUIDE.md`, the final CSVs. **Deliverable (teammate on Windows):** `FRI.pbix` + screenshots.

### Module 4 — AI Risk Investigation Agent (Python + LLM)

**Goal:** for risky transactions, produce a short, evidence-based explanation and a recommended action.

**Key concept — the agent does NOT replace the model.** The ML model produces the *number* (risk score). The agent takes that number plus the supporting facts and produces the *words* — a human-readable "why" and "what to do." It uses an **LLM API** (we use **Google Gemini**, free student tier; Anthropic Claude is also supported via a config switch) to write the explanation.

**What the agent is given** (per transaction): Transaction ID, Amount, Time/hour, the ML risk score, the historical fraud rate for similar amount/time bands (computed in Python), the anomaly indicators (which features deviate), a rule-based starting priority, and the current review status. Example input:
```json
{
  "transaction_id": "TXN-084213",
  "amount": 842.10,
  "transaction_hour": 11,
  "risk_score": 0.91,
  "risk_band": "High",
  "historical_fraud_rate_amount_band": 0.012,
  "anomaly_indicators": [
    {"feature": "V14", "deviation": "strongly below typical range"},
    {"feature": "V17", "deviation": "strongly below typical range"}
  ],
  "investigation_priority_rule": "HIGH",
  "review_status": "Flagged"
}
```

**What the agent outputs** (as structured JSON, then saved to CSV):
- Risk classification (HIGH / MEDIUM / LOW)
- Investigation recommendation
- Reason (citing only the facts it was given)
- Attention level
- Suggested action: **Escalate for Review / Hold / Approve**

**Guardrails (so the AI doesn't make things up):**
- The prompt tells it to use **only the supplied facts**, say "insufficient evidence" when unsure, and never invent customers/locations.
- It must return a fixed **JSON shape**; our code validates it and retries if malformed.
- A **rule-based priority floor**: code sets the minimum priority from score+amount+anomaly; the AI can justify but not downgrade below it. High priority always says "human review required."
- To control cost, we only run the agent on **Medium/High** transactions (or a demo sample, e.g., 300). An **offline template fallback** lets the whole thing run even with no API key. **We estimate the cost and get approval before any large run.**

**Deliverables:** `src/agent/prompt.py`, `src/agent/investigate.py`, `data/output/AI_Risk_Insights.csv`.

### Module 5 — Integration Pipeline (Python)

**Goal:** one command that runs the whole chain and writes everything Power BI needs.

`python -m src.run_pipeline` does: clean → train/load model → score → build the Power BI tables → run the agent → write all `data/output/*.csv` + a `run_log.json` (timestamps, row counts, metrics). It's repeatable and logged.

**Files Power BI reads:** `fact_transactions.csv`, `dim_date.csv`, `dim_risk_band.csv`, `dim_review_status.csv`, `AI_Risk_Insights.csv`, `model_metrics.csv`.

**Refresh in Power BI:** on Windows, the teammate clicks **Home → Refresh** and Power BI re-reads the CSVs. (For a nicer setup, a path parameter lets them point to the folder once.)

**Demo story (the closed loop):** show the dashboard → run the pipeline on updated data → click Refresh in Power BI → new risk scores and AI recommendations appear next to the charts.

**Deliverables:** `src/run_pipeline.py`, the full `data/output/` set, `run_log.json`.

---

## PART 4 — LOGISTICS

### 4.1 Project folder layout
```
bi-project/
├── PLAN.md  README.md  requirements.txt  .env.example  .gitignore
├── data/
│   ├── raw/creditcard.csv            ← already here, verified
│   ├── processed/clean_transactions.csv
│   └── output/   (the CSVs Power BI reads)
├── src/
│   ├── config.py  features.py  preprocess.py  train.py  score.py
│   ├── build_bi_tables.py  run_pipeline.py
│   └── agent/  prompt.py  investigate.py
├── models/   reports/
├── powerbi/  measures.dax  POWERBI_BUILD_GUIDE.md  [FRI.pbip]  FRI.pbix (built on Windows)
└── tests/
```

### 4.2 Tech stack (all free; Python runs on the Mac)
Python 3.11+, pandas, numpy, scikit-learn (Random Forest + metrics), imbalanced-learn (SMOTE), joblib, matplotlib/seaborn (EDA plots), google-generativeai (Gemini LLM API; anthropic also supported; offline template fallback exists), python-dotenv, jupyter, pytest. Power BI Desktop (on the teammate's Windows PC) for the dashboard.

### 4.3 Safety / honesty rules we follow throughout
- **Secrets:** API keys go in a git-ignored `.env` file, never pasted into chat or committed.
- **No leakage:** split the data before scaling/SMOTE; time features use past rows only.
- **No fabrication:** simulated columns are always labelled; metrics reported only after computing.
- **Decision support only:** the system advises; it never auto-blocks or freezes anything.

### 4.4 Suggested build order (we stop for review after each)
1. **Module 1** — scaffold + clean data → inspect the clean CSV & EDA.
2. **Module 2** — the model → see real metrics.
3. **Module 4** — the AI agent → see sample explanations.
4. **Module 5** — the one-command pipeline → all CSVs produced.
5. **Module 3 prep** — we write `measures.dax` + `POWERBI_BUILD_GUIDE.md`.
6. **Module 3 build** — teammate builds `FRI.pbix` on Windows from those files (the final, mechanical step).

### 4.5 Status snapshot
| Item | Status |
|---|---|
| Dataset downloaded & verified (284,807 rows, 31 cols, 492 frauds) | ✅ done |
| This plan (concepts + decisions) | ✅ done |
| Module 1 — ETL + feature engineering (`src/preprocess.py`) | ✅ built & run |
| Module 2 — Random Forest train/score (`src/train.py`, `src/score.py`) | ✅ built & run |
| Module 4 — AI agent, real Google Gemini (`src/agent/`) | ✅ built & run |
| Module 5 — one-command pipeline (`src/run_pipeline.py`) | ✅ built & run |
| Module 3 prep — `measures.dax` + `POWERBI_BUILD_GUIDE.md` | ✅ done |
| Tests (`tests/`, 19 tests) | ✅ passing |
| Module 3 — `FRI.pbix` on Windows | ⏳ teammate builds from the guide |

### 4.5.1 Real results (computed, not fabricated)
- **Clean data:** 283,726 rows after removing 1,081 duplicates; 473 frauds (0.167%).
- **Model (Random Forest + SMOTE, chosen over class-weighting by AUC-PR):**
  Precision **0.9125**, Recall **0.7684**, F1 **0.8343**, AUC-ROC **0.9730**,
  AUC-PR **0.8261**. Confusion matrix on the 56,746-row test set:
  TP 73, FP 7, FN 22, TN 56,644.
- **Risk bands across all transactions:** Low 283,220 · Medium 58 · High 448;
  40,408 flagged with an anomaly pattern.
- **AI agent:** 497 of the ~506 flagged (Medium/High) transactions investigated
  by **real Google Gemini** (`gemini-3.5-flash-lite`). Output varied naturally
  (452 HIGH / 45 MEDIUM priority; 476 Escalate / 21 Hold). The final handful
  were left for a later resume run due to the free tier's daily request cap —
  the resume cache completes them on re-run with no rework.

### 4.6 Decisions already locked
- ✅ **One** Power BI dashboard; **CSV files** are the bridge from Python.
- ✅ AI results shown as **formatted visuals** (table + cards + drill-through), never raw CSV.
- ✅ **No Streamlit / no second frontend** — Power BI is the only frontend.
- ✅ `.pbix` built by the **teammate on Windows** from our CSVs + `measures.dax` + build-guide Markdown (the guide is the backup if the `.pbix` ever fails).
- ✅ **LLM provider:** Google Gemini (free student tier). Risk thresholds chosen from the precision–recall results (0.30 / 0.70). Built fresh (reference repos not needed).

> The Python pipeline is complete and reproducible via `python -m src.run_pipeline`.
> The only remaining step is building `FRI.pbix` on Windows using
> `powerbi/POWERBI_BUILD_GUIDE.md`.
