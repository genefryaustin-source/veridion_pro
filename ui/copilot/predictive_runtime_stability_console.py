"""
ui/copilot/predictive_runtime_stability_console.py

Predictive Runtime Stability Console.

Purpose:
- predictive runtime cognition command center
- anticipatory sovereign operational visibility
- future-state runtime forecasting
- topology degradation prediction
- governance overload intelligence
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def _fmt_ts(ms: Any) -> str:
    if not ms:
        return "-"

    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(int(ms) / 1000),
        )
    except Exception:
        return str(ms)


def _icon(value: str) -> str:
    value = str(value or "").upper()

    if value in {
        "LOW",
        "STABLE",
        "CONFIRMED",
    }:
        return "🟢"

    if value in {
        "MEDIUM",
        "WATCH",
        "PENDING",
    }:
        return "🟡"

    if value in {
        "HIGH",
        "DEGRADING",
    }:
        return "🟠"

    if value in {
        "CRITICAL",
        "UNSTABLE",
        "FALSE_POSITIVE",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_predictive_runtime_stability_console(
    storage: Any,
) -> None:

    st.markdown("# 🔮 Predictive Runtime Stability")
    st.caption(
        "Anticipatory sovereign runtime cognition, instability forecasting, and future-state operational intelligence."
    )

    engine = getattr(
        storage,
        "predictive_runtime_stability_engine",
        None,
    )

    learning_engine = getattr(
        storage,
        "runtime_fabric_learning_engine",
        None,
    )

    sovereignty_engine = getattr(
        storage,
        "sovereignty_decision_engine",
        None,
    )

    if engine is None:
        st.error(
            "Predictive Runtime Stability Engine unavailable."
        )
        return

    # ========================================================
    # STATUS
    # ========================================================

    st.markdown("## 🌐 Predictive Runtime Status")

    try:
        status = engine.predictive_status()
    except Exception as exc:
        status = {"error": str(exc)}

    latest = status.get("latest_assessment") or {}

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Assessments",
        status.get("assessment_count", 0),
    )

    c2.metric(
        "Predictions",
        status.get("prediction_count", 0),
    )

    c3.metric(
        "Pending",
        status.get("pending_predictions", 0),
    )

    c4.metric(
        "High Risk",
        status.get("high_risk_predictions", 0),
    )

    c5.metric(
        "Predictive State",
        f"{_icon(latest.get('predictive_state'))} {latest.get('predictive_state', 'UNKNOWN')}",
    )

    st.markdown("---")

    # ========================================================
    # OPERATIONS
    # ========================================================

    st.markdown("## ⚙️ Predictive Runtime Operations")

    o1, o2, o3 = st.columns(3)

    with o1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="predictive_runtime_tenant",
        )

    with o2:
        auto_assess = st.checkbox(
            "Auto Assess",
            value=False,
            key="predictive_runtime_auto_assess",
        )

    with o3:
        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=False,
            key="predictive_runtime_auto_refresh",
        )

    if st.button(
        "Run Predictive Runtime Assessment",
        use_container_width=True,
        key="predictive_runtime_assess_btn",
    ):
        try:
            assessment = engine.assess(
                tenant_id=tenant_id,
            )

            st.success(
                "Predictive runtime assessment completed."
            )

            st.json(
                assessment.to_dict()
                if hasattr(assessment, "to_dict")
                else assessment
            )

        except Exception as exc:
            st.error(
                f"Predictive runtime assessment failed: {exc}"
            )

    st.markdown("---")

    # ========================================================
    # LATEST ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Predictive Assessment")

    if latest:

        assess_tabs = st.tabs(
            [
                "Assessment",
                "Predictions",
                "Early Warnings",
                "Telemetry",
            ]
        )

        with assess_tabs[0]:
            st.json(latest)

        with assess_tabs[1]:

            rows = []

            for pred in latest.get("predictions", []):

                rows.append(
                    {
                        "Prediction": pred.get("prediction_type"),
                        "Severity": f"{_icon(pred.get('severity'))} {pred.get('severity')}",
                        "Probability": pred.get("probability"),
                        "Confidence": pred.get("confidence"),
                        "Timeline": pred.get("projected_timeline_minutes"),
                        "Target": pred.get("target"),
                        "Message": pred.get("message"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=420,
                )
            else:
                st.info(
                    "No predictive runtime forecasts available."
                )

        with assess_tabs[2]:

            rows = []

            for warning in latest.get("early_warnings", []):

                rows.append(
                    {
                        "Warning": warning.get("warning_type"),
                        "Severity": f"{_icon(warning.get('severity'))} {warning.get('severity')}",
                        "Probability": warning.get("probability"),
                        "Confidence": warning.get("confidence"),
                        "Timeline": warning.get("timeline_minutes"),
                        "Message": warning.get("message"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info(
                    "No predictive warnings available."
                )

        with assess_tabs[3]:
            st.json(
                latest.get("telemetry", {})
            )

    else:
        st.info(
            "No predictive runtime assessments available."
        )

    st.markdown("---")

    # ========================================================
    # PREDICTION STREAM
    # ========================================================

    st.markdown("## 🔮 Prediction Stream")

    try:

        predictions = engine.list_predictions(limit=250)

        rows = []

        for pred in predictions:

            rows.append(
                {
                    "Time": _fmt_ts(pred.get("created_at_ms")),
                    "Prediction": pred.get("prediction_type"),
                    "Severity": f"{_icon(pred.get('severity'))} {pred.get('severity')}",
                    "Probability": pred.get("probability"),
                    "Confidence": pred.get("confidence"),
                    "Target": pred.get("target"),
                    "Timeline": pred.get("projected_timeline_minutes"),
                    "Status": pred.get("status"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=450,
            )
        else:
            st.info(
                "No predictive runtime forecasts available."
            )

    except Exception as exc:
        st.error(
            f"Prediction stream failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # EARLY WARNING INTELLIGENCE
    # ========================================================

    st.markdown("## 🚨 Early Warning Intelligence")

    try:

        assessments = engine.list_assessments(limit=50)

        rows = []

        for item in assessments:

            rows.append(
                {
                    "Time": _fmt_ts(item.get("created_at_ms")),
                    "State": f"{_icon(item.get('predictive_state'))} {item.get('predictive_state')}",
                    "Stability": item.get("stability_score"),
                    "Confidence": item.get("confidence"),
                    "Predictions": len(item.get("predictions", [])),
                    "Warnings": len(item.get("early_warnings", [])),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=360,
            )
        else:
            st.info(
                "No predictive runtime intelligence available."
            )

    except Exception as exc:
        st.error(
            f"Early warning intelligence failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # PREDICTION OUTCOMES
    # ========================================================

    st.markdown("## 🧪 Prediction Outcome Validation")

    try:

        outcomes = engine.list_outcomes(limit=250)

        rows = []

        for item in outcomes:

            rows.append(
                {
                    "Time": _fmt_ts(item.get("resolved_at_ms")),
                    "Prediction ID": item.get("prediction_id"),
                    "Status": f"{_icon(item.get('status'))} {item.get('status')}",
                    "Notes": item.get("notes"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=320,
            )
        else:
            st.info(
                "No prediction outcome validations available."
            )

    except Exception as exc:
        st.error(
            f"Prediction validation telemetry failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # CONNECTED ENGINE TELEMETRY
    # ========================================================

    st.markdown("## 🔬 Runtime Cognition Telemetry")

    telemetry_tabs = st.tabs(
        [
            "Learning Engine",
            "Sovereignty Decisions",
            "Predictive Status",
        ]
    )

    with telemetry_tabs[0]:

        try:
            if learning_engine is not None:
                st.json(
                    learning_engine.learning_status()
                )
            else:
                st.info(
                    "Runtime learning engine unavailable."
                )
        except Exception as exc:
            st.error(
                f"Learning telemetry failed: {exc}"
            )

    with telemetry_tabs[1]:

        try:
            if sovereignty_engine is not None:
                st.json(
                    sovereignty_engine.decision_engine_status()
                )
            else:
                st.info(
                    "Sovereignty decision engine unavailable."
                )
        except Exception as exc:
            st.error(
                f"Sovereignty telemetry failed: {exc}"
            )

    with telemetry_tabs[2]:
        st.json(status)

    if auto_assess:
        try:
            engine.assess(
                tenant_id=tenant_id,
            )
        except Exception:
            pass

    if auto_refresh:
        time.sleep(5)
        st.rerun()