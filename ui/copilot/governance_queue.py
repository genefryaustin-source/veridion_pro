import json
import pandas as pd
import streamlit as st
from ui.copilot.governance_action_handlers import (
    GovernanceActionHandlers,
)

def _safe_json(value):
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value)
    except Exception:
        return {}


def _query_df(storage, sql, params=None):
    try:
        conn = storage.ledger.conn
        return pd.read_sql_query(sql, conn, params=params or {})
    except Exception:
        return pd.DataFrame()


def _table_exists(storage, table_name):
    df = _query_df(
        storage,
        "SELECT name FROM sqlite_master WHERE type='table' AND name=:name",
        {"name": table_name},
    )
    return not df.empty


def _normalize_bool(value):
    return "Yes" if str(value).lower() in {"1", "true", "yes"} else "No"


def render_governance_queue(storage=None):
    handlers = GovernanceActionHandlers(storage)
    rows = []

    # ---------------------------------------------------------
    # APPROVAL REQUESTS
    # ---------------------------------------------------------
    if _table_exists(storage, "approval_requests"):

        from ui.copilot.governance_action_handlers import (
            GovernanceActionHandlers,
        )

        handlers = GovernanceActionHandlers(storage)

        current_user = (
                st.session_state.get("username")
                or st.session_state.get("user_email")
                or "analyst"
        )

        df = _query_df(
            storage,
            """
            SELECT *
            FROM approval_requests
            ORDER BY created_at_ms DESC
            LIMIT 250
            """
        )

        for idx, r in df.iterrows():

            approval = dict(r)

            risk = (
                    approval.get("risk")
                    or approval.get("severity")
                    or "UNKNOWN"
            )

            rollback_available = _normalize_bool(
                approval.get("rollback_available", 0)
            )

            st.markdown("---")

            top_col1, top_col2 = st.columns([4, 1])

            with top_col1:

                st.markdown(
                    f"""
                    ### 🛡️ {approval.get('action') or approval.get('request_type') or 'Approval Request'}

                    **Status:** {approval.get('status', 'PENDING')}

                    **Risk:** {risk}

                    **Reviewer:** {
                    approval.get('assigned_reviewer')
                    or approval.get('reviewer')
                    or approval.get('assigned_to')
                    or 'Unassigned'
                    }

                    **Rollback Available:** {"✅ Yes" if rollback_available else "❌ No"}

                    **Execution Trace:** {
                    approval.get('decision_id')
                    or approval.get('trace_id')
                    or approval.get('request_id')
                    or ''
                    }
                    """
                )

            with top_col2:

                st.caption(
                    str(
                        approval.get("created_at_ms")
                    )
                )

            # -------------------------------------------------
            # ACTION BUTTONS
            # -------------------------------------------------

            approve_col, reject_col, escalate_col, assign_col = st.columns(4)

            # ---------------------------------------------
            # APPROVE
            # ---------------------------------------------
            with approve_col:

                if st.button(
                        "✅ Approve",
                        key=f"approve_{approval['request_id']}_{idx}",
                        use_container_width=True,
                ):

                    result = handlers.approve_action(
                        approval_request_id=approval["request_id"],
                        actor=current_user,
                    )

                    if result.get("success"):

                        st.success(
                            "Approval granted."
                        )

                        st.rerun()

                    else:

                        st.error(
                            result.get("reason")
                        )

            # ---------------------------------------------
            # REJECT
            # ---------------------------------------------
            with reject_col:

                if st.button(
                        "❌ Reject",
                        key=f"reject_{approval['request_id']}_{idx}",
                        use_container_width=True,
                ):

                    result = handlers.reject_action(
                        approval_request_id=approval["request_id"],
                        actor=current_user,
                    )

                    if result.get("success"):

                        st.warning(
                            "Approval rejected."
                        )

                        st.rerun()

                    else:

                        st.error(
                            result.get("reason")
                        )

            # ---------------------------------------------
            # ESCALATE
            # ---------------------------------------------
            with escalate_col:

                if st.button(
                        "🚨 Escalate",
                        key=f"escalate_{approval['request_id']}_{idx}",
                        use_container_width=True,
                ):

                    result = handlers.escalate_action(
                        case_id=approval.get("case_id"),
                        actor=current_user,
                        reason="Manual escalation from governance queue",
                    )

                    if result.get("success"):

                        st.info(
                            "Escalation initiated."
                        )

                        st.rerun()

                    else:

                        st.error(
                            result.get("reason")
                        )

            # ---------------------------------------------
            # ASSIGN REVIEWER
            # ---------------------------------------------
            with assign_col:

                assigned_user = st.text_input(
                    "Assign Reviewer",
                    key=f"assign_input_{approval['request_id']}_{idx}",
                    placeholder="analyst@company.com",
                )

                if st.button(
                        "👤 Assign",
                        key=f"assign_btn_{approval['request_id']}_{idx}",
                        use_container_width=True,
                ):

                    result = handlers.assign_case(
                        case_id=approval.get("case_id"),
                        assigned_to=assigned_user,
                        actor=current_user,
                    )

                    if result.get("success"):

                        st.success(
                            f"Assigned to {assigned_user}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            result.get("reason")
                        )

    # ---------------------------------------------------------
    # GOVERNANCE EVENTS
    # ---------------------------------------------------------
    if _table_exists(storage, "governance_events"):
        df = _query_df(storage, "SELECT * FROM governance_events ORDER BY created_at_ms DESC LIMIT 250")

        for _, r in df.iterrows():
            rows.append({
                "Source": "governance_events",
                "Action": r.get("action") or r.get("event_type") or "Governance Event",
                "Status": r.get("status", "OPEN"),
                "Risk": r.get("severity", "UNKNOWN"),
                "Requires Approval": _normalize_bool(r.get("requires_approval", 0)),
                "Assigned Reviewer": r.get("approved_by") or r.get("assigned_reviewer") or "",
                "Rollback Available": _normalize_bool(r.get("rollback_available", 0)),
                "Execution Trace": r.get("target_id") or r.get("decision_id") or "",
                "Created": r.get("created_at_ms"),
            })

    # ---------------------------------------------------------
    # ORCHESTRATION DECISIONS
    # ---------------------------------------------------------
    if _table_exists(storage, "orchestration_decisions"):
        df = _query_df(storage, "SELECT * FROM orchestration_decisions ORDER BY created_at_ms DESC LIMIT 250")

        for _, r in df.iterrows():
            rows.append({
                "Source": "orchestration_decisions",
                "Action": r.get("final_action") or r.get("recommendation") or "AI Decision",
                "Status": r.get("outcome", "DECIDED"),
                "Risk": round(float(r.get("confidence") or 0), 2),
                "Requires Approval": _normalize_bool(r.get("requires_approval", 0)),
                "Assigned Reviewer": "",
                "Rollback Available": _normalize_bool(r.get("rollback_triggered", 0)),
                "Execution Trace": r.get("decision_id") or r.get("run_id") or "",
                "Created": r.get("created_at_ms"),
            })

    # ---------------------------------------------------------
    # ANALYST OVERRIDES
    # ---------------------------------------------------------
    if _table_exists(storage, "analyst_overrides"):
        df = _query_df(storage, "SELECT * FROM analyst_overrides ORDER BY created_at_ms DESC LIMIT 250")

        for _, r in df.iterrows():
            rows.append({
                "Source": "analyst_overrides",
                "Action": f"{r.get('original_action', '')} → {r.get('override_action', '')}",
                "Status": "OVERRIDDEN",
                "Risk": "REVIEW",
                "Requires Approval": "No",
                "Assigned Reviewer": r.get("analyst", ""),
                "Rollback Available": "Possible",
                "Execution Trace": r.get("decision_id", ""),
                "Created": r.get("created_at_ms"),
            })

    # ---------------------------------------------------------
    # ROLLBACK EVENTS
    # ---------------------------------------------------------
    if _table_exists(storage, "rollback_events"):
        df = _query_df(storage, "SELECT * FROM rollback_events ORDER BY created_at_ms DESC LIMIT 250")

        for _, r in df.iterrows():
            rows.append({
                "Source": "rollback_events",
                "Action": r.get("rollback_action") or r.get("action") or "Rollback",
                "Status": r.get("status", "ROLLBACK_REQUIRED"),
                "Risk": r.get("severity", "HIGH"),
                "Requires Approval": _normalize_bool(r.get("requires_approval", 0)),
                "Assigned Reviewer": r.get("assigned_reviewer") or "",
                "Rollback Available": "Yes",
                "Execution Trace": r.get("decision_id") or r.get("rollback_id") or "",
                "Created": r.get("created_at_ms"),
            })

    if not rows:
        st.info("No governance records found yet. This panel is wired and will populate once governance events are written.")
        return

    out = pd.DataFrame(rows)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Governance Items", len(out))
    c2.metric("Pending", int((out["Status"].astype(str).str.upper() == "PENDING").sum()))
    c3.metric("Overrides", int((out["Source"] == "analyst_overrides").sum()))
    c4.metric("Rollback Items", int((out["Rollback Available"].astype(str).str.upper().isin(["YES", "POSSIBLE"])).sum()))

    st.dataframe(out, use_container_width=True, hide_index=True)

    with st.expander("Raw governance event data"):
        st.json(rows[:50])