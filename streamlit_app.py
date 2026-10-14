"""
Financial Risk Intelligence System (FRIS) — Advanced Streamlit Platform
========================================================================
Interactive Next-Generation Risk Intelligence & Transaction Monitoring Dashboard.
Extends and complements the Power BI dashboard with:
  1. Executive Financial BI & Real-Time Monitoring Center
  2. AI Risk Agent Decision Support & Interactive Case Dossier Studio
  3. Dynamic What-If Financial Exposure & Staffing Optimizer
  4. Live Real-Time Transaction Scoring Sandbox (ML Inference)
  5. Model Governance, Feature Importance & Algorithmic Transparency
  6. Human-in-the-Loop Analyst Resolution Station & Audit Trail Hub

Author: Financial Risk Intelligence Team (Deepika K & Guhasri R)
Course: 20MSSL10 – Business Intelligence Laboratory, CIT
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import joblib

# -----------------------------------------------------------------------------
# 0. Page Configuration & Custom Modern Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Financial Risk Intelligence Platform | FRIS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Deep FinTech Dark Theme CSS with Glassmorphism, Top Navigation & High-Contrast Typography
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, [class*="stCode"] {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Background gradient styling */
.stApp {
    background: radial-gradient(circle at 50% 0%, #111827 0%, #080C14 100%);
    color: #F3F4F6;
}

/* Top Brand Navbar */
.top-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(17, 24, 39, 0.90);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px 24px;
    margin-bottom: 20px;
    backdrop-filter: blur(16px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}

.brand-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-subtitle {
    font-size: 0.80rem;
    color: #94A3B8;
    font-weight: 500;
    margin-top: 2px;
}

.status-chip {
    background: rgba(99, 102, 241, 0.14);
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: #A5B4FC;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.status-chip-success {
    background: rgba(16, 185, 129, 0.14);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34D399;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Glassmorphism Metric Cards */
.kpi-card {
    background: linear-gradient(135deg, rgba(26, 34, 52, 0.85) 0%, rgba(17, 24, 39, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(16px);
    transition: all 0.25s ease-in-out;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 15px 30px -5px rgba(99, 102, 241, 0.2);
}

.kpi-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #FFFFFF;
    line-height: 1.2;
}

.kpi-subtext {
    font-size: 0.75rem;
    font-weight: 500;
    color: #64748B;
    margin-top: 6px;
}

/* Badges */
.badge-danger {
    background: rgba(239, 68, 68, 0.16);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-block;
}
.badge-warning {
    background: rgba(245, 158, 11, 0.16);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.35);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-block;
}
.badge-success {
    background: rgba(16, 185, 129, 0.16);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-block;
}
.badge-indigo {
    background: rgba(99, 102, 241, 0.18);
    color: #A5B4FC;
    border: 1px solid rgba(99, 102, 241, 0.4);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-block;
}

/* Dossier Card */
.dossier-box {
    background: rgba(20, 27, 45, 0.9);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
}

/* Section Header Styling */
.section-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 3px;
}
.section-subtitle {
    font-size: 0.83rem;
    color: #94A3B8;
    margin-bottom: 14px;
}

/* Sidebar Styling */
div[data-testid="stSidebar"] {
    background: #090D16;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* Segmented Control / Navigation Styling */
div[data-testid="stSegmentedControl"] {
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 12px;
    padding: 4px;
}

div[data-testid="stSegmentedControl"] button {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: #4F46E5 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
}

/* Custom scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0B0F19;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. Paths & Data Loading Layer (Strictly Read-Only)
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_OUTPUT = PROJECT_ROOT / "data" / "output"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"


def format_fig(
    fig: go.Figure,
    height: int = 320,
    show_legend: bool = False,
    x_title: str | None = None,
    y_title: str | None = None,
    y2_title: str | None = None,
    margin: dict | None = None,
) -> go.Figure:
    """Safely applies dark modern theme to Plotly figures without invalid layout keys."""
    m = margin or dict(l=15, r=15, t=25, b=15)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8"),
        height=height,
        showlegend=show_legend,
        margin=m,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.06)",
        zeroline=False,
        title_text=x_title,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.06)",
        zeroline=False,
        title_text=y_title,
    )
    if y2_title:
        fig.update_layout(yaxis2=dict(title_text=y2_title, showgrid=False, overlaying="y", side="right"))
    return fig


@st.cache_data(show_spinner=False)
def load_fact_data() -> pd.DataFrame:
    """Loads the main FactTransactions dataset produced by the pipeline."""
    fact_path = DATA_OUTPUT / "fact_transactions.csv"
    if not fact_path.exists():
        st.error(f"Cannot find `{fact_path}`. Run pipeline first.")
        st.stop()
    df = pd.read_csv(
        fact_path,
        parse_dates=["transaction_datetime"],
        dtype={
            "transaction_id": str,
            "date_key": int,
            "transaction_hour": int,
            "amount": float,
            "amount_band": str,
            "actual_class": int,
            "risk_score": float,
            "risk_band": str,
            "anomaly_flag": int,
            "review_status": str,
            "investigation_priority": str,
            "customer_segment": str,
            "region": str,
        },
    )
    return df


@st.cache_data(show_spinner=False)
def load_ai_insights() -> pd.DataFrame:
    """Loads the AI Risk Investigation Agent recommendations."""
    path = DATA_OUTPUT / "AI_Risk_Insights.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_metrics_data() -> tuple[pd.DataFrame, dict]:
    """Loads model performance summary and metrics JSON."""
    metrics_csv = DATA_OUTPUT / "model_metrics.csv"
    metrics_json = REPORTS_DIR / "metrics.json"

    df_metrics = pd.read_csv(metrics_csv) if metrics_csv.exists() else pd.DataFrame()
    meta = {}
    if metrics_json.exists():
        with open(metrics_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
    return df_metrics, meta


@st.cache_resource(show_spinner=False)
def load_ml_models():
    """Loads trained Random Forest classifier and RobustScaler for live sandbox."""
    model_path = MODELS_DIR / "rf_model.joblib"
    scaler_path = MODELS_DIR / "scaler.joblib"
    model = joblib.load(model_path) if model_path.exists() else None
    scaler = joblib.load(scaler_path) if scaler_path.exists() else None
    return model, scaler


# Baseline genuine statistics for anomaly deviation calculations
GENUINE_STATS = {
    "V1": {"mean": 0.0134, "std": 1.9222},
    "V2": {"mean": -0.0098, "std": 1.6335},
    "V3": {"mean": 0.0129, "std": 1.4576},
    "V4": {"mean": -0.0104, "std": 1.3986},
    "V5": {"mean": 0.0068, "std": 1.3558},
    "V6": {"mean": 0.0013, "std": 1.3299},
    "V7": {"mean": 0.0104, "std": 1.1775},
    "V8": {"mean": -0.0024, "std": 1.1571},
    "V9": {"mean": 0.0026, "std": 1.0869},
    "V10": {"mean": 0.0077, "std": 1.0363},
    "V11": {"mean": -0.0060, "std": 1.0023},
    "V12": {"mean": 0.0095, "std": 0.9454},
    "V13": {"mean": 0.0008, "std": 0.9952},
    "V14": {"mean": 0.0117, "std": 0.8944},
    "V15": {"mean": 0.0012, "std": 0.9147},
    "V16": {"mean": 0.0078, "std": 0.8446},
    "V17": {"mean": 0.0110, "std": 0.7485},
    "V18": {"mean": 0.0051, "std": 0.8250},
    "V19": {"mean": -0.0014, "std": 0.8112},
    "V20": {"mean": -0.0005, "std": 0.7686},
    "V21": {"mean": -0.0012, "std": 0.7156},
    "V22": {"mean": -0.0002, "std": 0.7235},
    "V23": {"mean": 0.0004, "std": 0.6212},
    "V24": {"mean": 0.0004, "std": 0.6057},
    "V25": {"mean": -0.0003, "std": 0.5206},
    "V26": {"mean": 0.00006, "std": 0.4821},
    "V27": {"mean": 0.0014, "std": 0.3927},
    "V28": {"mean": 0.0004, "std": 0.3276},
    "amount_zscore_recent": {"mean": -0.00002, "std": 1.0680},
}

# Initialize session state for analyst resolutions
if "analyst_audit_log" not in st.session_state:
    st.session_state.analyst_audit_log = []

# -----------------------------------------------------------------------------
# 2. Load Core Data
# -----------------------------------------------------------------------------
df_fact = load_fact_data()
df_ai = load_ai_insights()
df_metrics, metrics_meta = load_metrics_data()
rf_model, robust_scaler = load_ml_models()

# -----------------------------------------------------------------------------
# 3. Top Header Bar & Top Navigation Bar
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="top-navbar">
        <div>
            <div class="brand-title">
                <span>🛡️</span> FINANCIAL RISK INTELLIGENCE SYSTEM
            </div>
            <div class="brand-subtitle">
                AI-Enhanced Financial Risk Intelligence & Transaction Monitoring Suite · 20MSSL10 BI Lab (Deepika K & Guhasri R)
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <div class="status-chip-success">
                <span>●</span> Star Schema Synced (283.7K Txns)
            </div>
            <div class="status-chip">
                <span>⚡</span> RF + SMOTE (AUC-ROC 0.974)
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Top Navigation Bar (Segmented Control across all 6 core modules)
NAV_OPTIONS = [
    "📊 Executive BI Center",
    "🤖 AI Risk Agent Studio",
    "🎛️ What-If & Staffing Simulator",
    "🧪 Live Transaction Sandbox",
    "📈 Model Governance & Transparency",
    "📑 Compliance Audit Trail",
]

page = st.segmented_control(
    "Navigation Menu",
    NAV_OPTIONS,
    default="📊 Executive BI Center",
    label_visibility="collapsed",
)
if page is None:
    page = "📊 Executive BI Center"

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Sidebar Dedicated to Global Filters & Slicers
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px;">
            <div style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">
                ⚙️ GLOBAL FILTERS & SLICERS
            </div>
            <div style="font-size: 0.75rem; color: #94A3B8;">Dynamic context slicing across fact tables</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Risk Band filter
    all_bands = ["High", "Medium", "Low"]
    sel_bands = st.multiselect("Risk Band Classification", all_bands, default=all_bands)

    # Review Status filter
    all_statuses = sorted(df_fact["review_status"].dropna().unique().tolist())
    sel_statuses = st.multiselect("Operational Review Status", all_statuses, default=all_statuses)

    # Customer Segment filter
    all_segments = sorted(df_fact["customer_segment"].dropna().unique().tolist())
    sel_segments = st.multiselect("Customer Segment", all_segments, default=all_segments)

    # Region filter
    all_regions = sorted(df_fact["region"].dropna().unique().tolist())
    sel_regions = st.multiselect("Geographic Region", all_regions, default=all_regions)

    # Hour of day slider
    hour_range = st.slider("Hour of Day (Intraday)", 0, 23, (0, 23))

    # Reset button
    if st.button("Reset Global Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size: 0.72rem; color: #64748B; line-height: 1.5; padding: 4px;">
            <b>Total Records:</b> {len(df_fact):,}<br>
            <b>AI Investigated:</b> {len(df_ai)}<br>
            <b>Model:</b> RandomForest + SMOTE<br>
            <i>*Attributes (segment, region, workflow) are simulated for demonstration.</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Apply Global Filters to df_fact
# -----------------------------------------------------------------------------
filtered_df = df_fact[
    (df_fact["risk_band"].isin(sel_bands))
    & (df_fact["review_status"].isin(sel_statuses))
    & (df_fact["customer_segment"].isin(sel_segments))
    & (df_fact["region"].isin(sel_regions))
    & (df_fact["transaction_hour"] >= hour_range[0])
    & (df_fact["transaction_hour"] <= hour_range[1])
]

# Precomputed KPIs
total_txns = len(filtered_df)
total_amt = filtered_df["amount"].sum()
avg_amt = filtered_df["amount"].mean() if total_txns > 0 else 0.0
fraud_count = int(filtered_df["actual_class"].sum())
genuine_count = total_txns - fraud_count
fraud_rate_pct = (fraud_count / total_txns * 100) if total_txns > 0 else 0.0
high_risk_count = int((filtered_df["risk_band"] == "High").sum())
medium_risk_count = int((filtered_df["risk_band"] == "Medium").sum())
low_risk_count = int((filtered_df["risk_band"] == "Low").sum())
anomaly_count = int((filtered_df["anomaly_flag"] == 1).sum())
avg_risk_score = filtered_df["risk_score"].mean() if total_txns > 0 else 0.0


def fmt_cur(val: float) -> str:
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val / 1_000:.1f}K"
    return f"${val:.2f}"


# =============================================================================
# MODULE 1: EXECUTIVE BI & MONITORING CENTER
# =============================================================================
if page == "📊 Executive BI Center":
    # Sub-header
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">
                Executive Portfolio & Real-Time Monitoring Center
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                Comprehensive transaction monitoring, intraday volume trends, fraud incidence and capital concentration.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPI Ribbon
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title"><span>💳</span> Total Transactions</div>
                <div class="kpi-value">{total_txns:,}</div>
                <div class="kpi-subtext">Base: {len(df_fact):,} total</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title"><span>💰</span> Total Amount</div>
                <div class="kpi-value">{fmt_cur(total_amt)}</div>
                <div class="kpi-subtext">Avg ticket: ${avg_amt:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #EF4444;">
                <div class="kpi-title" style="color: #FCA5A5;"><span>🚨</span> Fraud Detected</div>
                <div class="kpi-value" style="color: #F87171;">{fraud_count:,}</div>
                <div class="kpi-subtext"><span class="badge-danger">{fraud_rate_pct:.3f}% rate</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #10B981;">
                <div class="kpi-title" style="color: #6EE7B7;"><span>🛡️</span> Genuine Volume</div>
                <div class="kpi-value" style="color: #34D399;">{genuine_count:,}</div>
                <div class="kpi-subtext">{(genuine_count/total_txns*100 if total_txns else 0):.2f}% safe</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #F59E0B;">
                <div class="kpi-title" style="color: #FCD34D;"><span>⚠️</span> High Risk Queue</div>
                <div class="kpi-value" style="color: #FBBF24;">{high_risk_count:,}</div>
                <div class="kpi-subtext">+{medium_risk_count} Medium risk</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title"><span>⚡</span> Anomaly Triggers</div>
                <div class="kpi-value">{anomaly_count:,}</div>
                <div class="kpi-subtext">|z| ≥ 3.0 outlier signals</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    # Row 1: Intraday Volume vs Fraud Velocity & Risk Concentration
    col_chart1, col_chart2 = st.columns([7, 5])

    with col_chart1:
        st.markdown("<div class='section-title'>Intraday Transaction Volume & Fraud Velocity</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Temporal patterns across 24-hour cycle showing peak transaction volume and fraud spikes.</div>", unsafe_allow_html=True)

        hourly_stats = (
            filtered_df.groupby("transaction_hour")
            .agg(
                total_txns=("transaction_id", "count"),
                fraud_txns=("actual_class", "sum"),
                high_risk=("risk_band", lambda s: (s == "High").sum()),
                total_amount=("amount", "sum"),
            )
            .reset_index()
        )

        fig_hourly = make_subplots(specs=[[{"secondary_y": True}]])
        fig_hourly.add_trace(
            go.Bar(
                x=hourly_stats["transaction_hour"],
                y=hourly_stats["total_txns"],
                name="Total Volume",
                marker_color="rgba(99, 102, 241, 0.40)",
                marker_line_color="#6366F1",
                marker_line_width=1.5,
                hovertemplate="Hour %{x}:00<br>Total Transactions: %{y:,}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_hourly.add_trace(
            go.Scatter(
                x=hourly_stats["transaction_hour"],
                y=hourly_stats["fraud_txns"],
                name="Fraud Count",
                mode="lines+markers",
                line=dict(color="#EF4444", width=3),
                marker=dict(size=7, color="#EF4444"),
                hovertemplate="Hour %{x}:00<br>Fraud Count: %{y}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_hourly = format_fig(
            fig_hourly,
            height=320,
            show_legend=True,
            x_title="Hour of Day (0–23)",
            y_title="Transaction Volume",
            y2_title="Fraud Count",
        )
        fig_hourly.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_hourly, use_container_width=True)

    with col_chart2:
        st.markdown("<div class='section-title'>Hourly Risk Concentration & Share</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Concentration of High-Risk transactions (High Count / Total Count per Hour).</div>", unsafe_allow_html=True)

        hourly_stats["risk_concentration"] = (
            hourly_stats["high_risk"] / hourly_stats["total_txns"] * 100
        ).fillna(0)

        fig_conc = go.Figure()
        fig_conc.add_trace(
            go.Scatter(
                x=hourly_stats["transaction_hour"],
                y=hourly_stats["risk_concentration"],
                mode="lines+markers",
                fill="tozeroy",
                fillcolor="rgba(239, 68, 68, 0.12)",
                line=dict(color="#F87171", width=2.5),
                marker=dict(size=6, color="#EF4444"),
                hovertemplate="Hour %{x}:00<br>Risk Concentration: %{y:.2f}%<extra></extra>",
            )
        )
        fig_conc.add_hline(
            y=hourly_stats["risk_concentration"].mean(),
            line_dash="dot",
            line_color="#94A3B8",
            annotation_text=f"Avg: {hourly_stats['risk_concentration'].mean():.2f}%",
            annotation_position="top left",
        )
        fig_conc = format_fig(fig_conc, height=320, x_title="Hour of Day", y_title="High-Risk Share (%)")
        st.plotly_chart(fig_conc, use_container_width=True)

    # Row 2: Amount by Risk Band & Multi-Tier Sunburst Chart
    col_row2_left, col_row2_right = st.columns([6, 6])

    with col_row2_left:
        st.markdown("<div class='section-title'>Gross Transaction Amount by Risk Band</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Capital distribution across Low (Green), Medium (Amber), and High (Red) risk tiers.</div>", unsafe_allow_html=True)

        amt_by_band = (
            filtered_df.groupby("risk_band")
            .agg(total_amount=("amount", "sum"), count=("transaction_id", "count"))
            .reindex(["High", "Medium", "Low"])
            .reset_index()
        )

        colors_map = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
        fig_band_amt = go.Figure(
            data=[
                go.Bar(
                    x=amt_by_band["risk_band"],
                    y=amt_by_band["total_amount"],
                    marker_color=[colors_map.get(b, "#6366F1") for b in amt_by_band["risk_band"]],
                    text=[f"${v/1_000_000:.2f}M" if v >= 1_000_000 else f"${v/1000:.1f}K" for v in amt_by_band["total_amount"]],
                    textposition="auto",
                    hovertemplate="%{x} Risk<br>Total Amount: $%{y:,.2f}<br>Count: %{customdata:,}<extra></extra>",
                    customdata=amt_by_band["count"],
                )
            ]
        )
        fig_band_amt = format_fig(fig_band_amt, height=300, x_title="Risk Band", y_title="Total Amount ($)")
        st.plotly_chart(fig_band_amt, use_container_width=True)

    with col_row2_right:
        st.markdown("<div class='section-title'>Multi-Tier Risk Flow (Segment → Region → Risk)</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Hierarchical breakdown of customer demographics, geography, and assigned risk levels.</div>", unsafe_allow_html=True)

        sunburst_df = (
            filtered_df.groupby(["customer_segment", "region", "risk_band"])
            .size()
            .reset_index(name="count")
        )
        fig_sunburst = px.sunburst(
            sunburst_df,
            path=["customer_segment", "region", "risk_band"],
            values="count",
            color="risk_band",
            color_discrete_map={"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"},
        )
        fig_sunburst = format_fig(fig_sunburst, height=300, margin=dict(l=5, r=5, t=5, b=5))
        st.plotly_chart(fig_sunburst, use_container_width=True)

    # Row 3: Operational Status Breakdown & Amount Distributions
    col_r3_1, col_r3_2 = st.columns([6, 6])

    with col_r3_1:
        st.markdown("<div class='section-title'>Operational Review Status Distribution</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Resolution pipeline across analyst review states (Simulated Analyst Outcomes).</div>", unsafe_allow_html=True)

        status_counts = filtered_df["review_status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]

        status_colors = {
            "Not flagged": "#334155",
            "Under Review": "#F59E0B",
            "Cleared": "#10B981",
            "Confirmed Fraud": "#EF4444",
        }
        fig_status = go.Figure(
            data=[
                go.Bar(
                    x=status_counts["status"],
                    y=status_counts["count"],
                    marker_color=[status_colors.get(s, "#6366F1") for s in status_counts["status"]],
                    text=[f"{c:,}" for c in status_counts["count"]],
                    textposition="auto",
                    hovertemplate="%{x}<br>Count: %{y:,}<extra></extra>",
                )
            ]
        )
        fig_status = format_fig(fig_status, height=290, x_title="Review Status", y_title="Count (Log Scale)")
        fig_status.update_yaxes(type="log")
        st.plotly_chart(fig_status, use_container_width=True)

    with col_r3_2:
        st.markdown("<div class='section-title'>Transaction Value Comparison (Fraud vs Genuine)</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Box plot showing log-transformed transaction amount distributions by actual class.</div>", unsafe_allow_html=True)

        sample_size = min(len(filtered_df), 15000)
        sample_df = filtered_df.sample(sample_size, random_state=42).copy()
        sample_df["Class Label"] = sample_df["actual_class"].map({1: "Fraud (1)", 0: "Genuine (0)"})

        fig_box = px.box(
            sample_df,
            x="Class Label",
            y="amount",
            color="Class Label",
            color_discrete_map={"Fraud (1)": "#EF4444", "Genuine (0)": "#10B981"},
            log_y=True,
            points=False,
        )
        fig_box = format_fig(fig_box, height=290, y_title="Amount in $ (Log Scale)")
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)


# =============================================================================
# MODULE 2: AI RISK INVESTIGATION AGENT STUDIO
# =============================================================================
elif page == "🤖 AI Risk Agent Studio":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">
                AI Risk Investigation Agent Decision Support Studio
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                Autonomous LLM-driven root cause forensics, anomalous pattern explanations and human analyst sign-off station.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df_ai.empty:
        st.warning("No AI Risk Insights found in `data/output/AI_Risk_Insights.csv`. Please run the pipeline first.")
        st.stop()

    total_ai_cases = len(df_ai)
    high_pri_count = int((df_ai["investigation_priority"] == "HIGH").sum())
    med_pri_count = int((df_ai["investigation_priority"] == "MEDIUM").sum())
    crit_att_count = int((df_ai["attention_level"] == "Critical").sum())

    ac1, ac2, ac3, ac4 = st.columns(4)
    with ac1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title"><span>🤖</span> Investigated by Agent</div>
                <div class="kpi-value">{total_ai_cases}</div>
                <div class="kpi-subtext">Medium & High risk focus</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ac2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #EF4444;">
                <div class="kpi-title" style="color: #FCA5A5;"><span>🚨</span> Critical Attention</div>
                <div class="kpi-value" style="color: #F87171;">{crit_att_count}</div>
                <div class="kpi-subtext">Immediate human intervention</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ac3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #F59E0B;">
                <div class="kpi-title" style="color: #FCD34D;"><span>⚡</span> High Priority Queue</div>
                <div class="kpi-value" style="color: #FBBF24;">{high_pri_count}</div>
                <div class="kpi-subtext">{(high_pri_count/total_ai_cases*100):.1f}% of AI cases</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ac4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title"><span>📝</span> Logged Dispositions</div>
                <div class="kpi-value">{len(st.session_state.analyst_audit_log)}</div>
                <div class="kpi-subtext">In-session analyst reviews</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    # Filter Controls for AI Cases
    col_f1, col_f2, col_f3, col_f4 = st.columns([3, 3, 3, 3])
    with col_f1:
        pri_options = ["ALL"] + sorted(df_ai["investigation_priority"].dropna().unique().tolist())
        sel_pri = st.selectbox("Filter Priority", pri_options)
    with col_f2:
        att_options = ["ALL"] + sorted(df_ai["attention_level"].dropna().unique().tolist())
        sel_att = st.selectbox("Filter Attention Level", att_options)
    with col_f3:
        act_options = ["ALL"] + sorted(df_ai["suggested_action"].dropna().unique().tolist())
        sel_act = st.selectbox("Filter Suggested Action", act_options)
    with col_f4:
        search_txn = st.text_input("Search Transaction ID", placeholder="e.g. TXN-006299").strip().upper()

    filtered_ai = df_ai.copy()
    if sel_pri != "ALL":
        filtered_ai = filtered_ai[filtered_ai["investigation_priority"] == sel_pri]
    if sel_att != "ALL":
        filtered_ai = filtered_ai[filtered_ai["attention_level"] == sel_att]
    if sel_act != "ALL":
        filtered_ai = filtered_ai[filtered_ai["suggested_action"] == sel_act]
    if search_txn:
        filtered_ai = filtered_ai[filtered_ai["transaction_id"].str.contains(search_txn, na=False)]

    st.markdown(f"**Showing {len(filtered_ai)} AI Investigated Transactions**")

    col_list, col_dossier = st.columns([5, 7])

    with col_list:
        st.markdown("<div class='section-title'>Flagged Case Queue</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Select any case to open the complete forensic dossier & sign-off form.</div>", unsafe_allow_html=True)

        if filtered_ai.empty:
            st.info("No transactions match the selected filters.")
            selected_txn_id = None
        else:
            display_cols = ["transaction_id", "risk_score", "investigation_priority", "attention_level", "suggested_action"]
            selected_idx = st.selectbox(
                "Select Transaction for Dossier Deep-Dive:",
                options=filtered_ai["transaction_id"].tolist(),
                format_func=lambda x: f"{x} — Score: {df_ai.loc[df_ai['transaction_id'] == x, 'risk_score'].values[0]:.2f} | Priority: {df_ai.loc[df_ai['transaction_id'] == x, 'investigation_priority'].values[0]}",
            )
            selected_txn_id = selected_idx

            st.dataframe(
                filtered_ai[display_cols].reset_index(drop=True),
                use_container_width=True,
                height=380,
            )

    with col_dossier:
        st.markdown("<div class='section-title'>AI Investigation Dossier & Resolution Hub</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Multi-dimensional case inspection, anomaly PCA deviations & human analyst sign-off.</div>", unsafe_allow_html=True)

        if selected_txn_id:
            row_ai = df_ai[df_ai["transaction_id"] == selected_txn_id].iloc[0]
            row_fact = df_fact[df_fact["transaction_id"] == selected_txn_id]
            txn_amount = row_fact["amount"].values[0] if not row_fact.empty else 0.0
            txn_hour = row_fact["transaction_hour"].values[0] if not row_fact.empty else "N/A"
            txn_segment = row_fact["customer_segment"].values[0] if not row_fact.empty else "N/A"
            txn_region = row_fact["region"].values[0] if not row_fact.empty else "N/A"
            txn_actual = row_fact["actual_class"].values[0] if not row_fact.empty else 0

            pri_color = "#EF4444" if row_ai["investigation_priority"] == "HIGH" else "#F59E0B"
            st.markdown(
                f"""
                <div class="dossier-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px; margin-bottom: 14px;">
                        <div>
                            <span style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF;">{selected_txn_id}</span>
                            <span style="margin-left: 10px;" class="badge-indigo">{row_ai.get('model_name', 'AI Agent')}</span>
                        </div>
                        <div>
                            <span style="background: {pri_color}22; color: {pri_color}; border: 1px solid {pri_color}55; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.8rem;">
                                Priority: {row_ai['investigation_priority']} ({row_ai.get('attention_level', 'High')})
                            </span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px;">
                        <div>
                            <div style="font-size: 0.70rem; color: #94A3B8; text-transform: uppercase;">Amount</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">${txn_amount:.2f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.70rem; color: #94A3B8; text-transform: uppercase;">ML Risk Score</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #F87171;">{row_ai['risk_score']:.2f} ({row_ai['risk_band']})</div>
                        </div>
                        <div>
                            <div style="font-size: 0.70rem; color: #94A3B8; text-transform: uppercase;">Hour & Segment</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">{txn_hour}:00 · {txn_segment}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.70rem; color: #94A3B8; text-transform: uppercase;">Ground Truth</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: {'#F87171' if txn_actual==1 else '#34D399'};">
                                {'⚠️ Fraud' if txn_actual==1 else '✅ Genuine'}
                            </div>
                        </div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.75); border-left: 4px solid #6366F1; padding: 12px 14px; border-radius: 8px; margin-bottom: 12px;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: #818CF8; text-transform: uppercase; margin-bottom: 3px;">
                            Suggested Action: {row_ai.get('suggested_action', 'Escalate for Review')}
                        </div>
                        <div style="font-size: 0.88rem; font-weight: 600; color: #F8FAFC; line-height: 1.4;">
                            {row_ai.get('recommendation', 'Escalate to a human analyst for manual review.')}
                        </div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; margin-bottom: 14px;">
                        <div style="font-size: 0.70rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 3px;">
                            Forensic Evidence & Agent Rationale
                        </div>
                        <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.5;">
                            {row_ai.get('reason', 'N/A')}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Anomaly Deviations Chart
            raw_indicators = str(row_ai.get("anomaly_indicators", ""))
            if ";" in raw_indicators or ":" in raw_indicators:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("<div style='font-size: 0.90rem; font-weight: 700; color: #F8FAFC;'>PCA Anomaly Component Forensic Deviation</div>", unsafe_allow_html=True)

                items = [item.strip() for item in raw_indicators.split(";") if ":" in item]
                features = [it.split(":")[0].strip() for it in items]
                descriptions = [it.split(":")[1].strip() for it in items]

                fig_anom = go.Figure(
                    data=[
                        go.Bar(
                            x=descriptions,
                            y=features,
                            orientation="h",
                            marker_color="#EF4444",
                            text=descriptions,
                            textposition="auto",
                        )
                    ]
                )
                fig_anom = format_fig(fig_anom, height=160, x_title="Deviation Magnitude from Genuine Norm", y_title="Component")
                st.plotly_chart(fig_anom, use_container_width=True)

            # Interactive Human Analyst Resolution Form
            st.markdown("---")
            st.markdown("<div style='font-size: 1.0rem; font-weight: 800; color: #F8FAFC;'>✍️ Human Analyst Disposition & Sign-Off</div>", unsafe_allow_html=True)

            with st.form(f"analyst_form_{selected_txn_id}"):
                fc1, fc2 = st.columns([6, 6])
                with fc1:
                    analyst_disposition = st.selectbox(
                        "Analyst Resolution Finding:",
                        [
                            "Confirmed Fraud — Block Card & Freeze Account",
                            "Cleared as False Positive — Genuine Transaction",
                            "Under Investigation — Escalate to Senior Tier 2",
                            "Step-up Authentication Requested (SMS / 2FA)",
                        ],
                    )
                with fc2:
                    analyst_name = st.text_input("Reviewer Badge / ID:", value="Deepika K (Analyst 7176)")

                analyst_notes = st.text_area(
                    "Investigation Audit Notes:",
                    placeholder="Enter case notes, customer contact verification details, or compliance rationale...",
                    height=60,
                )

                submit_disposition = st.form_submit_button("Submit & Log Official Resolution", use_container_width=True)
                if submit_disposition:
                    log_entry = {
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "transaction_id": selected_txn_id,
                        "risk_score": float(row_ai["risk_score"]),
                        "risk_band": str(row_ai["risk_band"]),
                        "amount": float(txn_amount),
                        "suggested_action": str(row_ai.get("suggested_action", "")),
                        "resolution": analyst_disposition,
                        "analyst": analyst_name,
                        "notes": analyst_notes,
                    }
                    st.session_state.analyst_audit_log.insert(0, log_entry)
                    st.success(f"Resolution logged successfully for {selected_txn_id}!")
                    st.rerun()


# =============================================================================
# MODULE 3: WHAT-IF SIMULATION & EXPOSURE OPTIMIZER
# =============================================================================
elif page == "🎛️ What-If & Staffing Simulator":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">
                Dynamic What-If Financial Exposure & Staffing Optimizer
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                Interactive portfolio risk modeling, analyst workload forecasting, and mathematical cost curve optimization.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([5, 3, 4])
    with ctrl_col1:
        threshold = st.slider(
            "🎯 Risk Decision Cutoff Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.70,
            step=0.01,
            help="Transactions with risk score ≥ this threshold are flagged for manual review or enforcement.",
        )
    with ctrl_col2:
        review_time_mins = st.number_input(
            "Avg Review Time / Txn (Mins)",
            min_value=1.0,
            max_value=60.0,
            value=8.0,
            step=1.0,
        )
    with ctrl_col3:
        cost_per_review = st.number_input(
            "Analyst Cost per Review ($)",
            min_value=1.0,
            max_value=100.0,
            value=12.50,
            step=0.50,
        )

    # Compute Live Metrics at Selected Threshold
    flagged_mask = filtered_df["risk_score"] >= threshold
    flagged_subset = filtered_df[flagged_mask]

    gross_exposure = flagged_subset["amount"].sum()
    cleared_exposure = flagged_subset[flagged_subset["review_status"] == "Cleared"]["amount"].sum()
    effective_exposure = gross_exposure - cleared_exposure

    flagged_count_sim = len(flagged_subset)
    flag_rate_sim = (flagged_count_sim / total_txns * 100) if total_txns > 0 else 0.0
    frauds_caught = int(flagged_subset["actual_class"].sum())
    frauds_missed = fraud_count - frauds_caught
    catch_rate_pct = (frauds_caught / fraud_count * 100) if fraud_count > 0 else 0.0

    total_review_hours = (flagged_count_sim * review_time_mins) / 60.0
    analyst_days = total_review_hours / 8.0
    fte_needed = analyst_days / 20.0

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #6366F1;">
                <div class="kpi-title">Gross Exposure</div>
                <div class="kpi-value">{fmt_cur(gross_exposure)}</div>
                <div class="kpi-subtext">Amount above {threshold:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #10B981;">
                <div class="kpi-title">Cleared Exposure</div>
                <div class="kpi-value" style="color: #34D399;">{fmt_cur(cleared_exposure)}</div>
                <div class="kpi-subtext">Verified genuine amount</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #EF4444;">
                <div class="kpi-title" style="color: #FCA5A5;">Effective Risk Exposure</div>
                <div class="kpi-value" style="color: #F87171;">{fmt_cur(effective_exposure)}</div>
                <div class="kpi-subtext">Net capital at risk</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Flagged Review Queue</div>
                <div class="kpi-value">{flagged_count_sim:,}</div>
                <div class="kpi-subtext">{flag_rate_sim:.2f}% of transactions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Analyst Staffing Load</div>
                <div class="kpi-value">{total_review_hours:,.0f} hrs</div>
                <div class="kpi-subtext">~{fte_needed:.1f} Full-Time Analysts</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    col_sim_left, col_sim_right = st.columns([6, 6])

    with col_sim_left:
        st.markdown("<div class='section-title'>Exposure Dynamics vs Threshold Slices</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Gross vs Cleared vs Effective Risk Exposure across the full threshold spectrum.</div>", unsafe_allow_html=True)

        threshold_steps = np.linspace(0.05, 0.95, 19)
        gross_curve = []
        cleared_curve = []
        effective_curve = []

        for th in threshold_steps:
            sub = filtered_df[filtered_df["risk_score"] >= th]
            g = sub["amount"].sum()
            c = sub[sub["review_status"] == "Cleared"]["amount"].sum()
            gross_curve.append(g)
            cleared_curve.append(c)
            effective_curve.append(g - c)

        fig_exp = go.Figure()
        fig_exp.add_trace(
            go.Scatter(x=threshold_steps, y=gross_curve, name="Gross Exposure", line=dict(color="#6366F1", width=2.5))
        )
        fig_exp.add_trace(
            go.Scatter(x=threshold_steps, y=cleared_curve, name="Cleared Exposure", line=dict(color="#10B981", width=2))
        )
        fig_exp.add_trace(
            go.Scatter(
                x=threshold_steps,
                y=effective_curve,
                name="Effective Risk Exposure",
                line=dict(color="#EF4444", width=3, dash="solid"),
                fill="tozeroy",
                fillcolor="rgba(239, 68, 68, 0.1)",
            )
        )
        fig_exp.add_vline(x=threshold, line_dash="dash", line_color="#FBBF24", annotation_text=f"Current: {threshold:.2f}")

        fig_exp = format_fig(fig_exp, height=330, show_legend=True, x_title="Risk Cutoff Threshold", y_title="Exposure ($)")
        fig_exp.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_exp, use_container_width=True)

    with col_sim_right:
        st.markdown("<div class='section-title'>Enterprise Cost-Benefit Optimization Curve</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Balancing Analyst Investigation Expense vs Uncaught Fraud Losses to find optimum.</div>", unsafe_allow_html=True)

        avg_loss_per_uncaught = 250.0

        operational_costs = []
        fraud_losses = []
        total_enterprise_costs = []

        for th in threshold_steps:
            sub = filtered_df[filtered_df["risk_score"] >= th]
            f_count = len(sub)
            caught = sub["actual_class"].sum()
            missed = fraud_count - caught

            op_cost = f_count * cost_per_review
            fr_loss = missed * avg_loss_per_uncaught
            operational_costs.append(op_cost)
            fraud_losses.append(fr_loss)
            total_enterprise_costs.append(op_cost + fr_loss)

        min_idx = int(np.argmin(total_enterprise_costs))
        optimal_th = threshold_steps[min_idx]

        fig_cost = go.Figure()
        fig_cost.add_trace(
            go.Scatter(x=threshold_steps, y=operational_costs, name="Analyst Review Cost", line=dict(color="#38BDF8", width=2))
        )
        fig_cost.add_trace(
            go.Scatter(x=threshold_steps, y=fraud_losses, name="Uncaught Fraud Loss", line=dict(color="#F87171", width=2))
        )
        fig_cost.add_trace(
            go.Scatter(
                x=threshold_steps,
                y=total_enterprise_costs,
                name="Total Enterprise Cost",
                line=dict(color="#A855F7", width=3.5),
            )
        )
        fig_cost.add_vline(
            x=optimal_th,
            line_dash="dot",
            line_color="#34D399",
            annotation_text=f"Optimal: {optimal_th:.2f}",
            annotation_position="top left",
        )

        fig_cost = format_fig(fig_cost, height=330, show_legend=True, x_title="Risk Cutoff Threshold", y_title="Estimated Total Cost ($)")
        fig_cost.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_cost, use_container_width=True)


# =============================================================================
# MODULE 4: LIVE REAL-TIME TRANSACTION SANDBOX
# =============================================================================
elif page == "🧪 Live Transaction Sandbox":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                Live Real-Time Transaction Scoring Sandbox (ML Inference)
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                Real-time interactive scoring lab: evaluate custom transactions instantly against the trained Random Forest ensemble.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rf_model is None or robust_scaler is None:
        st.error("Trained Random Forest model or Scaler not found in `models/`. Please train the model first.")
        st.stop()

    # Scenario Presets
    st.markdown("<div style='font-size: 0.90rem; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;'>⚡ One-Click Scenario Presets</div>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    with p_col1:
        if st.button("☕ Low-Risk Coffee ($4.50)", use_container_width=True):
            st.session_state["sb_amount"] = 4.50
            st.session_state["sb_hour"] = 9
            st.session_state["sb_is_night"] = 0
            st.session_state["sb_v14"] = 0.05
            st.session_state["sb_v12"] = 0.02
            st.session_state["sb_v11"] = -0.01
            st.session_state["sb_v17"] = 0.01
            st.session_state["sb_v10"] = 0.03
            st.session_state["sb_v4"] = -0.02
            st.session_state["sb_zscore"] = 0.0
            st.rerun()

    with p_col2:
        if st.button("🚨 Midnight Fraud ($245.00)", use_container_width=True):
            st.session_state["sb_amount"] = 245.00
            st.session_state["sb_hour"] = 2
            st.session_state["sb_is_night"] = 1
            st.session_state["sb_v14"] = -6.80
            st.session_state["sb_v12"] = -5.40
            st.session_state["sb_v11"] = 4.90
            st.session_state["sb_v17"] = -7.10
            st.session_state["sb_v10"] = -5.20
            st.session_state["sb_v4"] = 5.80
            st.session_state["sb_zscore"] = 3.5
            st.rerun()

    with p_col3:
        if st.button("⚡ Card Testing ($1.00)", use_container_width=True):
            st.session_state["sb_amount"] = 1.00
            st.session_state["sb_hour"] = 3
            st.session_state["sb_is_night"] = 1
            st.session_state["sb_v14"] = -7.20
            st.session_state["sb_v12"] = -6.10
            st.session_state["sb_v11"] = 5.20
            st.session_state["sb_v17"] = -4.80
            st.session_state["sb_v10"] = -4.50
            st.session_state["sb_v4"] = 4.20
            st.session_state["sb_zscore"] = -0.8
            st.rerun()

    with p_col4:
        if st.button("🎲 High-Value Retail ($850.00)", use_container_width=True):
            st.session_state["sb_amount"] = 850.00
            st.session_state["sb_hour"] = 15
            st.session_state["sb_is_night"] = 0
            st.session_state["sb_v14"] = -2.10
            st.session_state["sb_v12"] = -1.80
            st.session_state["sb_v11"] = 1.60
            st.session_state["sb_v17"] = -1.90
            st.session_state["sb_v10"] = -1.40
            st.session_state["sb_v4"] = 2.10
            st.session_state["sb_zscore"] = 4.2
            st.rerun()

    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)

    col_sb_inputs, col_sb_results = st.columns([6, 6])

    with col_sb_inputs:
        st.markdown("<div class='section-title'>Transaction Input Parameters</div>", unsafe_allow_html=True)

        i_c1, i_c2 = st.columns(2)
        with i_c1:
            in_amount = st.number_input(
                "Transaction Amount ($)",
                min_value=0.01,
                max_value=10000.0,
                value=float(st.session_state.get("sb_amount", 125.0)),
                step=1.0,
            )
            in_hour = st.slider("Transaction Hour", 0, 23, int(st.session_state.get("sb_hour", 14)))
            in_is_night = st.checkbox("Nighttime Transaction (22:00 - 06:00)", value=bool(st.session_state.get("sb_is_night", 0)))
        with i_c2:
            in_freq = st.number_input("Rolling 1h Txn Frequency", min_value=1, max_value=50, value=3)
            in_zscore = st.slider(
                "Recent Amount Z-Score",
                -3.0,
                6.0,
                float(st.session_state.get("sb_zscore", 0.0)),
                step=0.1,
            )

        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #CBD5E1; margin: 10px 0 4px;'>Key Predictive PCA Components</div>", unsafe_allow_html=True)
        v_c1, v_c2 = st.columns(2)
        with v_c1:
            in_v14 = st.slider("V14 (Top Fraud Factor)", -10.0, 10.0, float(st.session_state.get("sb_v14", 0.0)), step=0.1)
            in_v12 = st.slider("V12 Component", -10.0, 10.0, float(st.session_state.get("sb_v12", 0.0)), step=0.1)
            in_v11 = st.slider("V11 Component", -10.0, 10.0, float(st.session_state.get("sb_v11", 0.0)), step=0.1)
        with v_c2:
            in_v17 = st.slider("V17 Component", -10.0, 10.0, float(st.session_state.get("sb_v17", 0.0)), step=0.1)
            in_v10 = st.slider("V10 Component", -10.0, 10.0, float(st.session_state.get("sb_v10", 0.0)), step=0.1)
            in_v4 = st.slider("V4 Component", -10.0, 10.0, float(st.session_state.get("sb_v4", 0.0)), step=0.1)

    with col_sb_results:
        st.markdown("<div class='section-title'>Live ML Prediction & Diagnostics</div>", unsafe_allow_html=True)

        from src.features import FEATURE_COLUMNS, SCALE_COLUMNS

        sim_time = (in_hour * 3600) + 1200
        amount_log = float(np.log1p(in_amount))

        feat_dict = {
            "Time": sim_time,
            "Amount": in_amount,
            "transaction_hour": in_hour,
            "day_index": 1,
            "is_night": 1 if in_is_night else 0,
            "amount_log": amount_log,
            "rolling_txn_frequency": in_freq,
            "amount_zscore_recent": in_zscore,
        }
        for i in range(1, 29):
            col_name = f"V{i}"
            if col_name == "V14":
                feat_dict[col_name] = in_v14
            elif col_name == "V12":
                feat_dict[col_name] = in_v12
            elif col_name == "V11":
                feat_dict[col_name] = in_v11
            elif col_name == "V17":
                feat_dict[col_name] = in_v17
            elif col_name == "V10":
                feat_dict[col_name] = in_v10
            elif col_name == "V4":
                feat_dict[col_name] = in_v4
            else:
                feat_dict[col_name] = 0.0

        sample_df = pd.DataFrame([feat_dict])[FEATURE_COLUMNS]
        sample_scaled = sample_df.copy()
        sample_scaled[SCALE_COLUMNS] = robust_scaler.transform(sample_scaled[SCALE_COLUMNS])

        pred_prob = float(rf_model.predict_proba(sample_scaled)[0, 1])

        if pred_prob >= 0.70:
            pred_band = "High"
            band_color = "#EF4444"
            badge_cls = "badge-danger"
        elif pred_prob >= 0.30:
            pred_band = "Medium"
            band_color = "#F59E0B"
            badge_cls = "badge-warning"
        else:
            pred_band = "Low"
            band_color = "#10B981"
            badge_cls = "badge-success"

        anomalies_detected = []
        for feat, val in [("V14", in_v14), ("V12", in_v12), ("V11", in_v11), ("V17", in_v17), ("V10", in_v10), ("V4", in_v4), ("amount_zscore_recent", in_zscore)]:
            stat = GENUINE_STATS.get(feat, {"mean": 0.0, "std": 1.0})
            z_score = (val - stat["mean"]) / stat["std"]
            if abs(z_score) >= 3.0:
                dev = "strongly above" if z_score > 0 else "strongly below"
                anomalies_detected.append(f"{feat} ({dev} typical, z={z_score:.1f})")

        is_anom = len(anomalies_detected) > 0

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=pred_prob * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Fraud Probability Score", "font": {"size": 15, "color": "#F8FAFC"}},
                number={"suffix": "%", "font": {"size": 34, "color": band_color}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94A3B8"},
                    "bar": {"color": band_color, "thickness": 0.3},
                    "bgcolor": "rgba(30, 41, 59, 0.5)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 30], "color": "rgba(16, 185, 129, 0.25)"},
                        {"range": [30, 70], "color": "rgba(245, 158, 11, 0.25)"},
                        {"range": [70, 100], "color": "rgba(239, 68, 68, 0.25)"},
                    ],
                },
            )
        )
        fig_gauge = format_fig(fig_gauge, height=220, margin=dict(l=20, r=20, t=25, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

        suggested_action = "Escalate for Review" if pred_band == "High" else ("Hold & Verify" if pred_band == "Medium" else "Auto-Approve")
        st.markdown(
            f"""
            <div style="background: rgba(22, 30, 46, 0.95); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 1.0rem; font-weight: 700; color: #FFFFFF;">
                        Assigned Tier: <span class="{badge_cls}">{pred_band} Risk</span>
                    </div>
                    <div>
                        <span class="{'badge-danger' if is_anom else 'badge-success'}">
                            {'⚡ Anomaly Triggered' if is_anom else '✅ No Extreme Drift'}
                        </span>
                    </div>
                </div>
                <div style="font-size: 0.82rem; color: #94A3B8; margin-bottom: 6px;">
                    <b>Recommended Action:</b> <span style="color: {band_color}; font-weight: 700;">{suggested_action}</span>
                </div>
                <div style="font-size: 0.80rem; color: #CBD5E1; line-height: 1.5; background: rgba(15, 23, 42, 0.6); padding: 8px 12px; border-radius: 8px;">
                    <b>Agent Synthesis:</b> ML Random Forest predicts {pred_prob*100:.1f}% likelihood of fraudulent origin. 
                    {f"Detected critical multi-sigma deviations in: {', '.join(anomalies_detected)}." if anomalies_detected else "Feature attributes remain within nominal parameters."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# MODULE 5: MODEL GOVERNANCE & TRANSPARENCY
# =============================================================================
elif page == "📈 Model Governance & Transparency":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                Model Governance & Algorithmic Transparency
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                Technical architecture, champion-challenger benchmarks, confusion matrix diagnostics, and feature importance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sel_metrics = metrics_meta.get("selected_metrics", {})
    precision = sel_metrics.get("precision", 0.9367)
    recall = sel_metrics.get("recall", 0.7789)
    f1 = sel_metrics.get("f1", 0.8506)
    auc_roc = sel_metrics.get("auc_roc", 0.9737)
    auc_pr = sel_metrics.get("auc_pr", 0.8298)

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    with mc1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #10B981;">
                <div class="kpi-title">Model Precision</div>
                <div class="kpi-value" style="color: #34D399;">{precision*100:.2f}%</div>
                <div class="kpi-subtext">Low false alarm rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mc2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #6366F1;">
                <div class="kpi-title">Model Recall</div>
                <div class="kpi-value" style="color: #818CF8;">{recall*100:.2f}%</div>
                <div class="kpi-subtext">Fraud capture coverage</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mc3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid #38BDF8;">
                <div class="kpi-title">F1-Score</div>
                <div class="kpi-value" style="color: #38BDF8;">{f1:.4f}</div>
                <div class="kpi-subtext">Harmonic mean balance</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mc4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">AUC-ROC</div>
                <div class="kpi-value">{auc_roc:.4f}</div>
                <div class="kpi-subtext">Discrimination ability</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mc5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">AUC-PR</div>
                <div class="kpi-value">{auc_pr:.4f}</div>
                <div class="kpi-subtext">Imbalanced test PR area</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    col_gov1, col_gov2 = st.columns([6, 6])

    with col_gov1:
        st.markdown("<div class='section-title'>Confusion Matrix Diagnostic (Test Set)</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Out-of-sample evaluation on 56,746 test transactions (20% held-out test split).</div>", unsafe_allow_html=True)

        cm = sel_metrics.get("confusion_matrix", {"true_negative": 56646, "false_positive": 5, "false_negative": 21, "true_positive": 74})
        tn, fp, fn, tp = cm["true_negative"], cm["false_positive"], cm["false_negative"], cm["true_positive"]

        z_matrix = [[tn, fp], [fn, tp]]
        x_labels = ["Predicted Genuine", "Predicted Fraud"]
        y_labels = ["Actual Genuine", "Actual Fraud"]

        fig_cm = go.Figure(
            data=go.Heatmap(
                z=z_matrix,
                x=x_labels,
                y=y_labels,
                colorscale=[[0, "#111827"], [0.001, "#1E293B"], [0.05, "#312E81"], [1.0, "#6366F1"]],
                text=[[f"TN: {tn:,}", f"FP: {fp:,}"], [f"FN: {fn:,}", f"TP: {tp:,}"]],
                texttemplate="%{text}",
                textfont={"size": 15, "color": "#FFFFFF"},
                showscale=False,
            )
        )
        fig_cm = format_fig(fig_cm, height=270, margin=dict(l=10, r=10, t=10, b=10))
        fig_cm.update_layout(xaxis=dict(side="bottom"), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_cm, use_container_width=True)

    with col_gov2:
        st.markdown("<div class='section-title'>Champion vs Challenger Comparison</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Benchmarking Random Forest + SMOTE vs Random Forest + class_weight.</div>", unsafe_allow_html=True)

        comp = metrics_meta.get("comparison", {})
        comp_data = []
        if comp:
            for k, v in comp.items():
                comp_data.append(
                    {
                        "Architecture": v.get("model", k),
                        "Precision": f"{v.get('precision', 0)*100:.2f}%",
                        "Recall": f"{v.get('recall', 0)*100:.2f}%",
                        "F1 Score": f"{v.get('f1', 0):.4f}",
                        "AUC-ROC": f"{v.get('auc_roc', 0):.4f}",
                        "AUC-PR": f"{v.get('auc_pr', 0):.4f}",
                    }
                )
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, height=130)

        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px 14px; border-radius: 8px; font-size: 0.80rem; color: #94A3B8; line-height: 1.5; margin-top: 10px;">
                <b>Architectural Justification:</b> While <code>class_weight</code> achieved slightly higher precision (+2.2%), 
                <code>SMOTE</code> significantly increased recall by <b>+4.2% (capturing 74 vs 70 frauds)</b> and attained superior 
                <b>AUC-ROC (0.9737) and AUC-PR (0.8298)</b>, making it the safer enterprise choice for minimizing uncaught fraud.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Tree Ensemble Feature Importance Ranking</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Top features driving fraud classification in the trained 100-tree Random Forest model.</div>", unsafe_allow_html=True)

    if rf_model is not None:
        from src.features import FEATURE_COLUMNS

        importances = pd.Series(rf_model.feature_importances_, index=FEATURE_COLUMNS).sort_values(ascending=False).head(14)
        fig_fi = go.Figure(
            data=[
                go.Bar(
                    x=importances.values,
                    y=importances.index,
                    orientation="h",
                    marker=dict(
                        color=importances.values,
                        colorscale=[[0, "#4338CA"], [0.5, "#6366F1"], [1.0, "#A5B4FC"]],
                    ),
                    text=[f"{v*100:.1f}%" for v in importances.values],
                    textposition="auto",
                    hovertemplate="Feature %{y}<br>Relative Importance: %{x:.4f}<extra></extra>",
                )
            ]
        )
        fig_fi = format_fig(fig_fi, height=330, x_title="Relative Importance Weight", y_title="Feature Name")
        fig_fi.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_fi, use_container_width=True)


# =============================================================================
# MODULE 6: COMPLIANCE AUDIT TRAIL & EXPORTS
# =============================================================================
elif page == "📑 Compliance Audit Trail":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                Compliance Audit Trail & Enterprise Data Extraction
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                Immutable session audit log, compliance disposition history, and enterprise data extraction suite.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-title'>Session Analyst Dispositions Audit Trail</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Chronological record of manual review decisions, findings, and compliance notes executed in this session.</div>", unsafe_allow_html=True)

    if st.session_state.analyst_audit_log:
        audit_df = pd.DataFrame(st.session_state.analyst_audit_log)
        st.dataframe(audit_df, use_container_width=True, height=240)

        csv_audit = audit_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Audit Trail Log (CSV)",
            data=csv_audit,
            file_name=f"analyst_audit_trail_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No manual resolutions recorded yet in this session. Go to '🤖 AI Risk Agent Studio' to review and sign off on cases.")

    st.markdown("---")
    st.markdown("<div class='section-title'>Enterprise Data Extraction Center</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Download pre-filtered datasets, AI investigation tables, and pipeline execution logs for compliance filing.</div>", unsafe_allow_html=True)

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title"><span>📊</span> Filtered Transactions</div>
                <div class="kpi-subtext">Exports current filtered fact view with customer segment and risk bands.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        export_fact_sample = filtered_df.head(10000).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Transactions (CSV)",
            data=export_fact_sample,
            file_name="filtered_transactions.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp_col2:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title"><span>🤖</span> AI Risk Insights</div>
                <div class="kpi-subtext">Exports complete table of 499 AI agent recommendations and reasons.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not df_ai.empty:
            ai_csv = df_ai.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download AI Risk Insights (CSV)",
                data=ai_csv,
                file_name="AI_Risk_Insights.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with exp_col3:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title"><span>📈</span> Model Metrics Report</div>
                <div class="kpi-subtext">Exports model precision, recall, F1, and PR curve coordinates.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not df_metrics.empty:
            metrics_csv_data = df_metrics.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Model Metrics (CSV)",
                data=metrics_csv_data,
                file_name="model_metrics.csv",
                mime="text/csv",
                use_container_width=True,
            )

# -----------------------------------------------------------------------------
# Footer (Standard project compliance notice)
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #64748B; padding: 4px 0;">
        <div>
            <b>Financial Risk Intelligence System (FRIS)</b> — AI-Enhanced Transaction Monitoring Platform
        </div>
        <div>
            Source: Public anonymised dataset. Dates, review status, and customer/region attributes are simulated / illustrative.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
