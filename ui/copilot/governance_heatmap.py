from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


# ============================================================
# HELPERS
# ============================================================

def _safe_list(value):
    return value if isinstance(value, list) else []


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    try:
        df = pd.DataFrame(rows or [])
        if df.empty:
            return df

        df = df.fillna("")

        for col in df.columns:
            try:
                df[col] = df[col].astype(str)
            except Exception:
                pass

        return df

    except Exception:
        return pd.DataFrame()


def _count_by(rows: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    counter = Counter()

    for row in rows:
        value = row.get(field) or "UNKNOWN"
        counter[str(value)] += 1

    return dict(counter)


def _metric_card(title: str, value: Any, caption: str = ""):
    st.markdown(
        f"""
        <div style="
            padding:14px;
            border-radius:12px;
            background:#111827;
            border:1px solid #1f2937;
            margin-bottom:10px;
        ">
            <div style="color:#94a3b8;font-size:13px;">{title}</div>
            <div style="color:white;font-size:26px;font-weight:800;">{value}</div>
            <div style="color:#64748b;font-size:12px;margin-top:4px;">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _bar_table(title: str, data: Dict[str, int], empty_msg: str):
    st.markdown(f"### {title}")

    if not data:
        st.info(empty_msg)
        return

    df = pd.DataFrame(
        [
            {"Category": k, "Count": v}
            for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)
        ]
    )

    st.dataframe(
        _safe_df(df.to_dict("records")),
        use_container_width=True,
        hide_index=True,
        height=260,
    )


def _get_optimizer_snapshot(storage) -> Dict[str, Any]:
    optimizer = getattr(storage, "policy_optimizer", None)

    if optimizer:
        try:
            return {
                "metrics": optimizer.get_metrics(),
                "policy_state": optimizer.get_policy_state(),
            }
        except Exception:
            pass

    return {
        "metrics": {},
        "policy_state": {},
    }


# ============================================================
# MAIN RENDER
# ============================================================

def render_governance_heatmap(storage=None):
    st.markdown("## 🌡️ Governance Heatmap")

    st.caption(
        """
        Operational governance intelligence across approvals, rollbacks,
        analyst overrides, verification failures, escalation activity,
        autonomy readiness, and policy drift.
        """
    )

    if storage is None:
        st.warning("Storage unavailable.")
        return

    governance = getattr(storage, "governance", None)

    if governance is None:
        st.warning("Governance repository unavailable.")
        return

    tenant_id = (
        st.session_state.get("active_tenant_id")
        or st.session_state.get("tenant_id")
        or "default_tenant"
    )

    limit = st.slider(
        "Heatmap Lookback",
        min_value=50,
        max_value=1000,
        value=500,
        step=50,
        key="governance_heatmap_limit",
    )

    # ========================================================
    # LOAD TELEMETRY
    # ========================================================

    try:
        events = governance.get_governance_events(
            tenant_id=tenant_id,
            limit=limit,
        )
    except Exception:
        events = []

    try:
        approvals = governance.get_approval_history(
            tenant_id=tenant_id,
            limit=limit,
        )
    except Exception:
        approvals = []

    try:
        rollbacks = governance.get_rollback_history(
            tenant_id=tenant_id,
            limit=limit,
        )
    except Exception:
        rollbacks = []

    try:
        overrides = governance.get_case_overrides(
            case_id=None,
            limit=limit,
        )
    except Exception:
        overrides = []

    try:
        decisions = governance.get_recent_decisions(
            tenant_id=tenant_id,
            limit=limit,
        )
    except Exception:
        decisions = []

    events = _safe_list(events)
    approvals = _safe_list(approvals)
    rollbacks = _safe_list(rollbacks)
    overrides = _safe_list(overrides)
    decisions = _safe_list(decisions)

    optimizer_snapshot = _get_optimizer_snapshot(storage)
    optimizer_metrics = optimizer_snapshot.get("metrics", {})
    policy_state = optimizer_snapshot.get("policy_state", {})

    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    pending_approvals = [
        a for a in approvals
        if str(a.get("status", "")).upper() == "PENDING"
    ]

    rejected_approvals = [
        a for a in approvals
        if str(a.get("status", "")).upper() in {"REJECTED", "DENIED"}
    ]

    failed_events = [
        e for e in events
        if str(e.get("status", "")).upper() in {"FAILED", "ERROR", "BLOCKED"}
        or "FAILED" in str(e.get("event_type", "")).upper()
    ]

    escalation_events = [
        e for e in events
        if "ESCALAT" in str(e.get("event_type", "")).upper()
        or "ESCALAT" in str(e.get("action", "")).upper()
    ]

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        _metric_card(
            "Pending Approvals",
            len(pending_approvals),
            "Approval queue backlog",
        )

    with c2:
        _metric_card(
            "Rollbacks",
            len(rollbacks),
            "Rollback activity",
        )

    with c3:
        _metric_card(
            "Overrides",
            len(overrides),
            "Analyst disagreement",
        )

    with c4:
        _metric_card(
            "Failures",
            len(failed_events),
            "Failed governance events",
        )

    with c5:
        _metric_card(
            "Escalations",
            len(escalation_events),
            "Escalation pressure",
        )

    st.markdown("---")

    # ========================================================
    # POLICY STATE
    # ========================================================

    st.markdown("## 🧠 Adaptive Policy State")

    p1, p2, p3, p4, p5 = st.columns(5)

    with p1:
        st.metric(
            "Automation Confidence",
            policy_state.get("automation_confidence", "N/A"),
        )

    with p2:
        st.metric(
            "Approval Threshold",
            policy_state.get("approval_threshold", "N/A"),
        )

    with p3:
        st.metric(
            "Autonomy Level",
            policy_state.get("autonomy_level", "N/A"),
        )

    with p4:
        st.metric(
            "Rollback Sensitivity",
            policy_state.get("rollback_sensitivity", "N/A"),
        )

    with p5:
        st.metric(
            "Escalation Sensitivity",
            policy_state.get("escalation_sensitivity", "N/A"),
        )

    with st.expander("Optimizer Metrics", expanded=False):
        st.json(optimizer_metrics)

    st.markdown("---")

    # ========================================================
    # HEATMAP PANELS
    # ========================================================

    left, right = st.columns(2)

    with left:
        _bar_table(
            "🔥 Rollback Hotspots",
            _count_by(rollbacks, "rollback_action"),
            "No rollback hotspots detected.",
        )

        _bar_table(
            "🧑‍💻 Analyst Override Density",
            _count_by(overrides, "override_action"),
            "No analyst overrides detected.",
        )

        _bar_table(
            "🚨 Escalation Instability",
            _count_by(escalation_events, "action"),
            "No escalation instability detected.",
        )

    with right:
        _bar_table(
            "⏳ Approval Bottlenecks",
            _count_by(pending_approvals, "assigned_reviewer"),
            "No approval bottlenecks detected.",
        )

        _bar_table(
            "❌ Approval Rejection Zones",
            _count_by(rejected_approvals, "action"),
            "No approval rejection zones detected.",
        )

        _bar_table(
            "⚠️ Failure Hotspots",
            _count_by(failed_events, "action"),
            "No failure hotspots detected.",
        )

    st.markdown("---")

    # ========================================================
    # GOVERNANCE DRIFT SCORING
    # ========================================================

    st.markdown("## 📉 Governance Drift")

    total_signals = max(
        len(events)
        + len(approvals)
        + len(rollbacks)
        + len(overrides)
        + len(decisions),
        1,
    )

    rollback_rate = round(len(rollbacks) / total_signals, 4)
    override_rate = round(len(overrides) / total_signals, 4)
    rejection_rate = round(len(rejected_approvals) / max(len(approvals), 1), 4)
    failure_rate = round(len(failed_events) / total_signals, 4)
    escalation_rate = round(len(escalation_events) / total_signals, 4)

    drift_score = round(
        min(
            100,
            (rollback_rate * 25)
            + (override_rate * 25)
            + (rejection_rate * 20)
            + (failure_rate * 20)
            + (escalation_rate * 10),
        ),
        2,
    )

    if drift_score >= 60:
        drift_level = "HIGH"
    elif drift_score >= 30:
        drift_level = "MEDIUM"
    else:
        drift_level = "LOW"

    d1, d2, d3, d4, d5, d6 = st.columns(6)

    with d1:
        st.metric("Drift Score", drift_score)

    with d2:
        st.metric("Drift Level", drift_level)

    with d3:
        st.metric("Rollback Rate", rollback_rate)

    with d4:
        st.metric("Override Rate", override_rate)

    with d5:
        st.metric("Rejection Rate", rejection_rate)

    with d6:
        st.metric("Failure Rate", failure_rate)

    if drift_level == "HIGH":
        st.error(
            "High governance drift detected. Recommend reducing autonomy and increasing approval gating."
        )
    elif drift_level == "MEDIUM":
        st.warning(
            "Moderate governance drift detected. Monitor rollback and override patterns."
        )
    else:
        st.success(
            "Governance drift is currently low."
        )

    st.markdown("---")

    # ========================================================
    # RAW TABLES
    # ========================================================

    with st.expander("Raw Governance Telemetry", expanded=False):

        tabs = st.tabs(
            [
                "Events",
                "Approvals",
                "Rollbacks",
                "Overrides",
                "Decisions",
            ]
        )

        with tabs[0]:
            df = _safe_df(events)
            if df.empty:
                st.info("No events.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

        with tabs[1]:
            df = _safe_df(approvals)
            if df.empty:
                st.info("No approvals.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

        with tabs[2]:
            df = _safe_df(rollbacks)
            if df.empty:
                st.info("No rollbacks.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

        with tabs[3]:
            df = _safe_df(overrides)
            if df.empty:
                st.info("No overrides.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

        with tabs[4]:
            df = _safe_df(decisions)
            if df.empty:
                st.info("No decisions.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)