# ui/theme.py
"""
Veridion Pro - Professional Theme & UI Components
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd


def apply_veridion_pro_theme():
    """Apply the full Veridion Pro theme"""
    st.markdown("""
    <style>
        /* ====================== GLOBAL ====================== */
        .stApp { background-color: #f8fafc; }

                # ui/theme.py  (add/replace this CSS)
        # ui/theme.py
                /* ====================== SIDEBAR ====================== */
        section[data-testid="stSidebar"] {
            background-color: #0a1428 !important;
        }

        /* Veridion Pro Logo */
        .veridion-logo {
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.2rem !important;
            padding: 0 0.5rem;
            color: #1e40af;
        }
        .veridion-logo span { color: #3b82f6 !important; }

        /* Base navigation text */
        .stRadio label,
        .stRadio > div > div > label,
        div[role="radiogroup"] label,
        div[data-testid="stSidebar"] .stRadio label {
            color: #e2e8f0 !important;
            font-size: 1.05rem !important;
        }

        /* HOVER - Clean & Reliable White Text */
        .stRadio label:hover,
        .stRadio > div > div > label:hover,
        div[role="radiogroup"] label:hover,
        div[data-testid="stSidebar"] .stRadio label:hover {
            background-color: #1e2937 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: inset 5px 0 0 #3b82f6 !important;
        }

        /* Selected state */
        .stRadio label[data-baseweb="radio"] div[role="radio"][aria-checked="true"],
        .stRadio > div > div > label[data-baseweb="radio"] div[role="radio"][aria-checked="true"] {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        /* MAIN CONTENT */
        h1, h2, h3, h4 { color: #1e2937 !important; font-weight: 600; }

        /* Metric Cards */
        .stMetric {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 20px 18px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        .stMetric label { color: #64748b !important; font-weight: 500; }
        .stMetric .metric-value { font-size: 2.25rem !important; font-weight: 700; }

        .metric-delta--positive { color: #22c55e !important; }
        .metric-delta--negative { color: #ef4444 !important; }

        /* Charts */
        .stPlotlyChart {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
        }
                /* Nuclear hover override */
        .stRadio label:hover * {
            color: #ffffff !important;
        }
        .stRadio label:hover {
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)


def veridion_sidebar_logo():
    """Veridion Pro logo matching the latest screenshot"""
    st.markdown("""
        <h1 style="
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.2rem !important;
            padding: 0 0.5rem;
            color: #1e40af;           /* Darker blue for VERIDION */
        ">
            VERIDION <span style="color: #3b82f6;">PRO</span>™
        </h1>
    """, unsafe_allow_html=True)


def veridion_header(title: str = "Compliance Overview", show_period: bool = True):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(title)
    if show_period:
        with col2:
            st.selectbox("Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"], index=0)


def render_compliance_metrics():
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Scans Completed", "1,247", "↑ 18% vs last 7 days")
    with col2: st.metric("Risks Detected", "23", "↓ 12% vs last 7 days")
    with col3: st.metric("Policies Monitored", "15", "↑ 7% vs last 7 days")
    with col4: st.metric("Systems Protected", "98", "↑ 5% vs last 7 days")


def risk_trend_chart(height: int = 380):
    dates = pd.date_range(end=datetime.today(), periods=7).tolist()
    values = [12, 18, 15, 22, 19, 25, 28]
    fig = go.Figure(go.Scatter(x=dates, y=values, mode='lines', line=dict(color="#3b82f6", width=3.5)))
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


def top_risk_categories_chart(height: int = 380):
    fig = px.pie(
        names=["Sensitive Data", "Access Control", "Configuration", "Other"],
        values=[45, 25, 20, 10],
        hole=0.62,
        color_discrete_sequence=["#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"]
    )
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)