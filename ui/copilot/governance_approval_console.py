"""
ui/copilot/governance_approval_console.py
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

from core.runtime.governance_approval_engine import (
    APPROVAL_STATUS_ESCALATED,
    APPROVAL_STATUS_PENDING,
    REVIEW_TYPE_DUAL,
    REVIEW_TYPE_LEGAL,
    get_governance_approval_engine,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _fmt_ms(ms: Any) -> str:
    try:
        value = int(ms or 0)
        if value <= 0:
            return ""
        return pd.to_datetime(value, unit="ms").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""


def _age_label(ms: Any) -> str:
    try:
        remaining = int(ms or 0) - _now_ms()
        if remaining <= 0:
            return "EXPIRED"

        seconds = remaining // 1000
        if seconds < 60:
            return f"{seconds}s"
        if seconds < 3600:
            return f"{seconds // 60}m"
        if seconds < 86400:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"
    except Exception:
        return "UNKNOWN"


def _severity_badge(severity: Any) -> str:
    sev = str(severity or "UNKNOWN").upper()
    colors = {
        "CRITICAL": "#991b1b",
        "HIGH": "#dc2626",
        "MEDIUM": "#f59e0b",
        "LOW": "#2563eb",
        "UNKNOWN": "#64748b",
    }
    color = colors.get(sev, "#64748b")
    return (
        f"<span style='background:{color}; color:white; padding:4px 9px; "
        f"border-radius:999px; font-size:12px; font-weight:800;'>{sev}</span>"
    )


def _status_badge(status: Any) -> str:
    value = str(status or "UNKNOWN").upper()
    colors = {
        "PENDING": "#ca8a04",
        "ESCALATED": "#dc2626",
        "APPROVED": "#16a34a",
        "REJECTED": "#991b1b",
        "EXPIRED": "#64748b",
        "OVERRIDE_APPROVED": "#7c3aed",
    }
    color = colors.get(value, "#64748b")
    return (
        f"<span style='background:{color}; color:white; padding:4px 9px; "
        f"border-radius:999px; font-size:12px; font-weight:800;'>{value}</span>"
    )


def _load_pending(engine: Any, tenant_id: Optional[str], review_type: Optional[str]) -> pd.DataFrame:
    rows = engine.list_pending_approvals(
        tenant_id=tenant_id if tenant_id and tenant_id != "All" else None,
        review_type=review_type if review_type and review_type != "All" else None,
        limit=1000,
    )

    df = pd.DataFrame(rows or [])

    if df.empty:
        return df

    df["expires_at"] = df["expires_at_ms"].apply(_fmt_ms)
    df["time_remaining"] = df["expires_at_ms"].apply(_age_label)
    df["created_at"] = df["created_at_ms"].apply(_fmt_ms)
    df["risk_score"] = pd.to_numeric(df.get("risk_score", 0), errors="coerce").fillna(0).astype(int)

    return df


def _render_header() -> None:
    st.markdown(
        """
        <div style="
            padding:18px 22px;
            border-radius:18px;
            background:linear-gradient(135deg,#111827,#1f2937,#374151);
            color:white;
            margin-bottom:18px;
            box-shadow:0 12px 30px rgba(15,23,42,.25);
        ">
            <div style="font-size:13px; opacity:.8; letter-spacing:.12em; font-weight:800;">
                VERIDION PRO GOVCLOUD
            </div>
            <div style="font-size:30px; font-weight:900; margin-top:4px;">
                ⚖️ Governance Approval Console
            </div>
            <div style="font-size:15px; opacity:.9; margin-top:8px;">
                Approval queue, legal review, dual approval, emergency override, and governed execution release.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metrics(df: pd.DataFrame) -> None:
    if df.empty:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Pending", 0)
        c2.metric("Escalated", 0)
        c3.metric("Legal", 0)
        c4.metric("Dual Approval", 0)
        c5.metric("Expired", 0)
        return

    now = _now_ms()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pending", len(df))
    c2.metric("Escalated", int((df["status"].astype(str).str.upper() == APPROVAL_STATUS_ESCALATED).sum()))
    c3.metric("Legal", int(pd.to_numeric(df.get("requires_legal", 0), errors="coerce").fillna(0).sum()))
    c4.metric("Dual Approval", int(pd.to_numeric(df.get("requires_dual_approval", 0), errors="coerce").fillna(0).sum()))
    c5.metric("Expired / Due", int((pd.to_numeric(df.get("expires_at_ms", 0), errors="coerce").fillna(0) <= now).sum()))


def _render_filters(df: pd.DataFrame) -> Dict[str, Any]:
    tenants = ["All"]
    if not df.empty and "tenant_id" in df.columns:
        tenants += sorted([str(x) for x in df["tenant_id"].dropna().unique().tolist()])

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        tenant = st.selectbox(
            "Tenant",
            tenants,
            key="gov_approval_filter_tenant",
        )

    with c2:
        review_type = st.selectbox(
            "Review Type",
            ["All", REVIEW_TYPE_LEGAL, REVIEW_TYPE_DUAL, "STANDARD", "LEGAL+DUAL"],
            key="gov_approval_filter_review",
        )

    with c3:
        search = st.text_input(
            "Search approval, action, case, execution",
            key="gov_approval_filter_search",
        ).strip()

    return {
        "tenant": tenant,
        "review_type": review_type,
        "search": search,
    }


def _apply_display_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    if df.empty:
        return df

    result = df.copy()

    tenant = filters.get("tenant")
    review_type = filters.get("review_type")
    search = filters.get("search")

    if tenant and tenant != "All" and "tenant_id" in result.columns:
        result = result[result["tenant_id"].astype(str) == tenant]

    if review_type and review_type != "All" and "review_type" in result.columns:
        result = result[result["review_type"].astype(str).str.upper() == review_type.upper()]

    if search:
        search_lower = search.lower()
        cols = [
            c
            for c in [
                "approval_id",
                "action",
                "case_id",
                "execution_id",
                "job_id",
                "tenant_id",
                "reason",
            ]
            if c in result.columns
        ]

        mask = False
        for col in cols:
            mask = mask | result[col].astype(str).str.lower().str.contains(search_lower, na=False)

        result = result[mask]

    return result


def _render_queue(df: pd.DataFrame) -> None:
    st.markdown("### Pending Governance Queue")

    if df.empty:
        st.info("No pending approvals found.")
        return

    show = df.copy()

    keep_cols = [
        "approval_id",
        "tenant_id",
        "status",
        "review_type",
        "action",
        "severity",
        "risk_score",
        "case_id",
        "execution_id",
        "requires_legal",
        "requires_dual_approval",
        "requested_by",
        "created_at",
        "time_remaining",
        "reason",
    ]

    keep_cols = [c for c in keep_cols if c in show.columns]

    st.dataframe(
        show[keep_cols],
        use_container_width=True,
        height=420,
        key="gov_approval_queue_table",
    )


def _render_detail(engine: Any, df: pd.DataFrame) -> None:
    if df.empty:
        return

    st.markdown("### Approval Detail & Actions")

    options = []
    for idx, row in df.iterrows():
        approval_id = str(row.get("approval_id"))
        label = (
            f"{approval_id} · {row.get('action')} · "
            f"{row.get('severity')} · Case {row.get('case_id')}"
        )
        options.append((approval_id, label))

    selected = st.selectbox(
        "Select approval request",
        options,
        format_func=lambda x: x[1],
        key="gov_approval_selected_request",
    )

    approval_id = selected[0]
    request = engine.get_approval_request(approval_id)

    if not request:
        st.error("Approval request could not be loaded.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_status_badge(request.get("status")), unsafe_allow_html=True)
    c2.markdown(_severity_badge(request.get("severity")), unsafe_allow_html=True)
    c3.metric("Risk Score", int(request.get("risk_score") or 0))
    c4.metric("Time Remaining", _age_label(request.get("expires_at_ms")))

    st.markdown("#### Request Context")

    display_context = {
        "approval_id": request.get("approval_id"),
        "tenant_id": request.get("tenant_id"),
        "action": request.get("action"),
        "review_type": request.get("review_type"),
        "case_id": request.get("case_id"),
        "alert_id": request.get("alert_id"),
        "evidence_id": request.get("evidence_id"),
        "execution_id": request.get("execution_id"),
        "requested_by": request.get("requested_by"),
        "reason": request.get("reason"),
        "requires_legal": bool(request.get("requires_legal")),
        "requires_dual_approval": bool(request.get("requires_dual_approval")),
        "approved_by": request.get("approved_by"),
        "second_approved_by": request.get("second_approved_by"),
        "legal_reviewer": request.get("legal_reviewer"),
    }

    st.json(display_context)

    reason = st.text_area(
        "Approval / rejection / override reason",
        key=f"gov_approval_reason_{approval_id}",
        placeholder="Required for audit trail...",
    )

    actor = st.text_input(
        "Actor",
        value="analyst",
        key=f"gov_approval_actor_{approval_id}",
    )

    st.markdown("#### Decision Controls")

    c5, c6, c7, c8, c9 = st.columns(5)

    with c5:
        if st.button("Approve", key=f"gov_approve_{approval_id}"):
            result = engine.approve(
                approval_id,
                actor=actor,
                reason=reason or "Approved from Governance Approval Console.",
                release_execution=True,
            )
            _render_result(result)
            st.rerun()

    with c6:
        if st.button("Legal Approve", key=f"gov_legal_approve_{approval_id}"):
            result = engine.approve(
                approval_id,
                actor=actor,
                reason=reason or "Legal approval granted.",
                legal_approval=True,
                release_execution=True,
            )
            _render_result(result)
            st.rerun()

    with c7:
        if st.button("Second Approve", key=f"gov_second_approve_{approval_id}"):
            result = engine.approve(
                approval_id,
                actor=actor,
                reason=reason or "Second approval granted.",
                second_approval=True,
                release_execution=True,
            )
            _render_result(result)
            st.rerun()

    with c8:
        if st.button("Reject", key=f"gov_reject_{approval_id}"):
            result = engine.reject(
                approval_id,
                actor=actor,
                reason=reason or "Rejected from Governance Approval Console.",
            )
            _render_result(result)
            st.rerun()

    with c9:
        if st.button("Emergency Override", key=f"gov_override_{approval_id}"):
            result = engine.emergency_override(
                approval_id,
                actor=actor,
                reason=reason or "Emergency override from Governance Approval Console.",
                release_execution=True,
            )
            _render_result(result)
            st.rerun()

    st.markdown("#### Approval Event Timeline")
    events = engine.list_approval_events(approval_id)
    if not events:
        st.info("No approval events recorded yet.")
    else:
        events_df = pd.DataFrame(events)
        if not events_df.empty and "created_at_ms" in events_df.columns:
            events_df["created_at"] = events_df["created_at_ms"].apply(_fmt_ms)

        cols = [
            c
            for c in ["created_at", "event_type", "actor", "message", "details_json"]
            if c in events_df.columns
        ]

        st.dataframe(
            events_df[cols],
            use_container_width=True,
            height=260,
            key=f"gov_approval_events_{approval_id}",
        )


def _render_result(result: Any) -> None:
    ok = getattr(result, "ok", False)
    message = getattr(result, "message", "")

    if ok:
        st.success(message or "Action completed.")
    else:
        st.error(message or "Action failed.")


def _render_maintenance(engine: Any, tenant_id: Optional[str]) -> None:
    st.markdown("### Queue Maintenance")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Escalate Near-Expiry Approvals", key="gov_approval_escalate_near_expiry"):
            escalated = engine.escalate_pending_approvals(
                tenant_id=tenant_id if tenant_id and tenant_id != "All" else None,
                actor="governance_approval_console",
            )
            st.success(f"Escalated {len(escalated)} approval(s).")
            st.rerun()

    with c2:
        if st.button("Expire Stale Approvals", key="gov_approval_expire_stale"):
            expired = engine.expire_stale_approvals(
                tenant_id=tenant_id if tenant_id and tenant_id != "All" else None,
                actor="governance_approval_console",
            )
            st.success(f"Expired {len(expired)} approval(s).")
            st.rerun()


def render_governance_approval_console(storage: Any, event_bus: Any = None) -> None:
    _render_header()

    engine = get_governance_approval_engine(
        storage,
        event_bus=event_bus,
    )

    raw_df = _load_pending(engine, tenant_id=None, review_type=None)

    filters = _render_filters(raw_df)
    df = _apply_display_filters(raw_df, filters)

    if st.button("Refresh", key="gov_approval_refresh"):
        st.rerun()

    _render_metrics(df)

    tab_queue, tab_detail, tab_maintenance = st.tabs(
        [
            "Approval Queue",
            "Review & Decide",
            "Maintenance",
        ]
    )

    with tab_queue:
        _render_queue(df)

    with tab_detail:
        _render_detail(engine, df)

    with tab_maintenance:
        _render_maintenance(engine, filters.get("tenant"))


# Backward-compatible alias
render_approval_console = render_governance_approval_console