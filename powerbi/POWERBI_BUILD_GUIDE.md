# Power BI Build Guide — Financial Risk Intelligence System

**Who this is for:** the teammate on **Windows** with **Power BI Desktop**.
**What you'll produce:** `FRI.pbix` — one dashboard with two page groups (Financial Transaction BI + AI Risk Intelligence).
**Time needed:** ~60–90 minutes.
**You do NOT need Python.** Everything you need is the CSV files in `data/output/`.

> This guide is also the safety net: if the `.pbix` ever fails to open, anyone can rebuild the entire dashboard by following these steps.

---

## 0. Before you start

1. Install **Power BI Desktop** (free) from the Microsoft Store or
   https://aka.ms/pbidesktopstore. (Windows only — this is why it's your job.)
2. Get the project folder (Guhasri will zip and send it). You need the
   **`data/output/`** folder, which contains:
   - `fact_transactions.csv`  (the main table, ~283,726 rows)
   - `dim_date.csv`
   - `dim_risk_band.csv`
   - `dim_review_status.csv`
   - `dim_priority.csv`
   - `AI_Risk_Insights.csv`  (the AI agent's recommendations)
   - `model_metrics.csv`
   - `run_log.json` (reference only; not imported)
3. Keep `powerbi/measures.dax` open in Notepad — you'll copy formulas from it.

---

## 1. Import the data

1. Open Power BI Desktop → **Home → Get data → Text/CSV**.
2. Select `data/output/fact_transactions.csv` → **Open** → in the preview click
   **Transform Data** (not Load — we'll check types first).
3. In **Power Query Editor**, confirm column types (click the icon left of each
   header if wrong):
   - `transaction_id` = Text
   - `transaction_datetime` = Date/Time
   - `date_key` = Whole Number
   - `transaction_hour` = Whole Number
   - `amount` = Decimal Number
   - `amount_band`, `risk_band`, `review_status`, `investigation_priority`,
     `customer_segment`, `region` = Text
   - `actual_class`, `anomaly_flag` = Whole Number
   - `risk_score` = Decimal Number
4. Click **Home → Close & Apply**.
5. Repeat **Get data → Text/CSV** for each remaining file. Load (not transform)
   is fine for the small dimension tables:
   `dim_date.csv`, `dim_risk_band.csv`, `dim_review_status.csv`,
   `dim_priority.csv`, `AI_Risk_Insights.csv`, `model_metrics.csv`.
6. **Rename the tables** in the Fields pane (right-click → Rename) to match the
   DAX file exactly:
   | CSV file | Rename table to |
   |---|---|
   | fact_transactions | `FactTransactions` |
   | AI_Risk_Insights | `FactAIInsights` |
   | dim_date | `DimDate` |
   | dim_risk_band | `DimRiskBand` |
   | dim_review_status | `DimReviewStatus` |
   | dim_priority | `DimPriority` |
   | model_metrics | `ModelMetrics` |

> **Tip (portability):** To make the folder path easy to change later, in Power
> Query create a parameter `DataFolder` (Home → Manage Parameters) and point
> each query's source at it. Optional — skip if short on time.

---

## 2. Build the data model (relationships — the star schema)

Go to the **Model view** (left sidebar, third icon). Create these relationships
by dragging one field onto the other. All are **one-to-many**, single direction,
from the dimension (one side) to the fact (many side).

| From (one side) | To (many side) | On field |
|---|---|---|
| `DimDate[date_key]` | `FactTransactions[date_key]` | date_key |
| `DimRiskBand[risk_band]` | `FactTransactions[risk_band]` | risk_band |
| `DimReviewStatus[review_status]` | `FactTransactions[review_status]` | review_status |
| `DimPriority[priority]` | `FactAIInsights[investigation_priority]` | priority |
| `FactTransactions[transaction_id]` | `FactAIInsights[transaction_id]` | transaction_id (1-to-1 or 1-to-many; set cross-filter to Both) |

> If Power BI auto-created wrong relationships on import, delete them first
> (click the line → Delete) and create the ones above.

**Sort columns for nice ordering:**
- Select `DimRiskBand` → column `risk_band` → **Column tools → Sort by column →
  sort_order**.
- Do the same for `DimReviewStatus[review_status]` by `sort_order` and
  `DimPriority[priority]` by `sort_order`.

---

## 3. Add the DAX measures

1. In the Fields pane, click **FactTransactions** so new measures land there.
2. **Home → New measure**. Delete the placeholder text, then open
   `powerbi/measures.dax` and copy **one whole measure** (its name + `=` + the
   formula). Paste and press Enter.
3. Repeat for every measure in the file. There are ~30. Work top to bottom.
4. For the **What-if parameter** (needed by the Effective Risk Exposure
   measures): **Modeling → New parameter → Numeric range**. Name it exactly
   **`Risk Threshold`**, Min 0, Max 1, Increment 0.05, Default 0.70. Click OK.
   This auto-creates a table `Risk Threshold` and a slicer on the page. Then
   add the `Risk Threshold Value`, `Gross Exposure`, `Cleared Exposure`, and
   `Effective Risk Exposure` measures from the DAX file.

> If a measure errors because a measure it references doesn't exist yet, just
> add them in order (Section 6 of the DAX file: add `Risk Threshold Value`
> before `Gross Exposure`).

---

## 4. Page A — Financial Transaction BI Dashboard

Add a new page (bottom tab **+**). Rename it "Financial Transaction BI".
Keep ≤ 8 visuals. Suggested layout (KPIs across the top):

**Row 1 — KPI cards** (Insert → Card, or the multi-row card). One card each:
- `Total Transactions`
- `Total Amount`  (format as currency or number)
- `Fraud Count`
- `Fraud Rate %`  (format as %, 3 decimals — it's ~0.17%)
- `Average Amount`

**Row 2 — Trends:**
- **Line chart**: Axis = `DimDate[date]` (or `transaction_hour` for intraday),
  Values = `Total Transactions`. Title: "Transaction Volume Trend".
- **Line chart**: Axis = `transaction_hour`, Values = `Total Amount`.
  Title: "Transaction Amount by Hour".
- **Column chart**: Axis = `transaction_hour`, Values = `Total Transactions`.
  Title: "Peak Transaction Hours".

**Row 3 — Risk & amount:**
- **Donut chart**: Legend = a field that labels fraud vs genuine. Create a
  quick column or use `actual_class` (0/1). Values = `Total Transactions`.
  Title: "Fraud vs Genuine". (Tip: add a calc column
  `Class Label = IF(FactTransactions[actual_class]=1,"Fraud","Genuine")`.)
- **Clustered bar**: Axis = `DimRiskBand[risk_band]`, Values = `Total Amount`.
  Title: "Amount by Risk Band". Apply the band colours (red/amber/green) via
  `DimRiskBand[color_hex]` (Format → Data colors → fx → Field value).
- **Stacked column**: Axis = `DimReviewStatus[review_status]`,
  Values = `Total Transactions`. Title: "Review Status (Simulated)".

**Slicers (left side):** `DimDate[date]`, `DimRiskBand[risk_band]`,
`DimReviewStatus[review_status]`.

**Footer text box (every page):**
> *Source: public anonymised dataset. Dates, review status, and
> customer/region attributes are simulated / illustrative.*

---

## 5. Page B — AI Risk Intelligence Dashboard

Add another page, name it "AI Risk Intelligence". The six abstract indicators:

1. **Risk Score** — **Histogram/column**: Axis = `risk_band` (or bin
   `risk_score`), Values = `Total Transactions`. Plus a card `Average Risk
   Score`.
2. **Anomaly Indicator** — **Table**: columns `transaction_id`, `risk_score`,
   `anomaly_flag`, and from `FactAIInsights` the `anomaly_indicators`. Add card
   `Anomaly Count`.
3. **Risk Concentration** — **Line chart**: Axis = `transaction_hour`,
   Values = `Risk Concentration`. Plus card `Risk Concentration`.
4. **Investigation Priority** — **Bar chart**: Axis =
   `FactAIInsights[investigation_priority]`, Values = `High Priority Count`
   (or COUNTROWS). Add a slicer on `investigation_priority`.
5. **Suggested Action** — **Stacked bar**: Axis =
   `FactAIInsights[suggested_action]`, Values =
   `Transactions Investigated by Agent`.
6. **Effective Risk Exposure** — **Card**: `Effective Risk Exposure`. Place the
   `Risk Threshold` slicer next to it so moving the threshold updates the card.

**Investigation table (the AI results, shown as a visual — NOT raw CSV):**
A **Table** visual from `FactAIInsights` with columns:
`transaction_id`, `risk_score`, `investigation_priority`, `attention_level`,
`suggested_action`, `recommendation`, `reason`.
Title it "AI Risk Investigation — Agent Recommendations".

**Model performance cards (optional):** cards for `Model Precision`,
`Model Recall`, `Model F1`, `Model AUC ROC`, `Model AUC PR`.

---

## 6. Drill-through page (one transaction's full AI explanation)

1. Add a page named "Transaction Detail". Set it as a drill-through:
   **Visualizations → Drill through → Add `transaction_id`** to the
   "Drill through" well.
2. On this page add cards/table showing that transaction's `risk_score`,
   `risk_band`, `investigation_priority`, `suggested_action`, `recommendation`,
   and `reason` from `FactAIInsights`, plus `amount`, `transaction_hour`,
   `anomaly_flag` from `FactTransactions`.
3. Now on Page B, right-click any row in the investigation table →
   **Drill through → Transaction Detail** to see the full write-up.

---

## 7. Styling

- **Colours:** red = High, amber = Medium, green = Low (use `color_hex` from
  `DimRiskBand`). Keep it consistent across pages.
- **Fraud Rate %**: format with 3 decimal places (value ≈ 0.167%).
- Titles on every visual; the simulated-data footer on every page.
- Keep each page uncluttered (≤ 8 visuals).

---

## 8. Save and share

1. **File → Save as → `FRI.pbix`** (save it into the `powerbi/` folder).
2. Take screenshots of both pages for the report.
3. (Optional) **Home → Refresh** anytime the CSVs are regenerated — Power BI
   re-reads them. If you used the `DataFolder` parameter, update the path once
   under **Transform data → Edit parameters**.

---

## 9. Expected numbers (sanity check against the data)

After import, these should roughly match (they come from the real pipeline run):

| Measure | Expected (approx.) |
|---|---|
| Total Transactions | 283,726 |
| Fraud Count | 473 |
| Fraud Rate % | ~0.167% |
| High Risk Count | ~448 |
| Medium Risk Count | ~58 |
| Model Precision / Recall / F1 | from `model_metrics.csv` |

If `Total Transactions` ≠ the row count of `fact_transactions.csv`, re-check the
import didn't filter rows.

---

## 10. Troubleshooting

- **A measure shows an error:** the table names must match Section 1 exactly
  (`FactTransactions`, `FactAIInsights`, etc.). Rename and the measures fix
  themselves.
- **Relationship won't create:** make sure both key columns are the same data
  type (e.g., both Text for `transaction_id`).
- **Effective Risk Exposure blank:** you skipped the `Risk Threshold` What-if
  parameter (Section 3, step 4) — create it, or hard-code 0.70 in
  `Risk Threshold Value`.
- **CSV won't load / encoding issues:** in the Text/CSV dialog set File Origin
  to `65001: Unicode (UTF-8)`.
