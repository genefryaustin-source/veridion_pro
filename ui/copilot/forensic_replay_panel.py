import json
import pandas as pd
import streamlit as st
from ui.copilot.governance_action_handlers import (
    GovernanceActionHandlers,
)


def _query_df(storage, sql, params=None):
    try:
        return pd.read_sql_query(sql, storage.ledger.conn, params=params or {})
    except Exception:
        return pd.DataFrame()


def _table_exists(storage, table_name):
    df = _query_df(
        storage,
        "SELECT name FROM sqlite_master WHERE type='table' AND name=:name",
        {"name": table_name},
    )
    return not df.empty


def _add_rows(rows, df, source, event_col, actor_col=None, status_col=None, ts_col="created_at_ms"):
    if df.empty:
        return

    for _, r in df.iterrows():
        rows.append({
            "timestamp": r.get(ts_col) or r.get("timestamp_ms") or r.get("created_at"),
            "source": source,
            "event": r.get(event_col) or source,
            "actor": r.get(actor_col) if actor_col else r.get("actor", ""),
            "status": r.get(status_col) if status_col else r.get("status", ""),
            "trace": r.get("decision_id") or r.get("run_id") or r.get("evidence_id") or r.get("case_id") or "",
            "details": dict(r),
        })


def render_forensic_replay_panel(storage=None):
    st.subheader("🧾 Forensic Replay")
    st.caption("Operational black box replay of AI actions, analyst decisions, approvals, containment, rollback, and evidence events.")

    case_id = st.text_input("Filter by Case ID, Evidence ID, Run ID, or Decision ID", value="")

    rows = []

    # ---------------------------------------------------------
    # ORCHESTRATION DECISIONS
    # ---------------------------------------------------------
    if _table_exists(storage, "orchestration_decisions"):
        df = _query_df(storage, "SELECT * FROM orchestration_decisions ORDER BY created_at_ms DESC LIMIT 500")
        _add_rows(rows, df, "AI Decision", "recommendation", status_col="outcome")

    # ---------------------------------------------------------
    # ANALYST OVERRIDES
    # ---------------------------------------------------------
    if _table_exists(storage, "analyst_overrides"):
        df = _query_df(storage, "SELECT * FROM analyst_overrides ORDER BY created_at_ms DESC LIMIT 500")
        for _, r in df.iterrows():
            rows.append({
                "timestamp": r.get("created_at_ms"),
                "source": "Analyst Override",
                "event": f"{r.get('original_action', '')} → {r.get('override_action', '')}",
                "actor": r.get("analyst", ""),
                "status": "OVERRIDDEN",
                "trace": r.get("decision_id", ""),
                "details": dict(r),
            })

    # ---------------------------------------------------------
    # APPROVAL REQUESTS
    # ---------------------------------------------------------
    if _table_exists(storage, "approval_requests"):
        df = _query_df(storage, "SELECT * FROM approval_requests ORDER BY created_at_ms DESC LIMIT 500")
        _add_rows(rows, df, "Approval Chain", "action", actor_col="reviewer", status_col="status")

    # ---------------------------------------------------------
    # GOVERNANCE EVENTS
    # ---------------------------------------------------------
    if _table_exists(storage, "governance_events"):
        df = _query_df(storage, "SELECT * FROM governance_events ORDER BY created_at_ms DESC LIMIT 500")
        _add_rows(rows, df, "Governance Event", "event_type", actor_col="actor", status_col="status")

    # ---------------------------------------------------------
    # ROLLBACK EVENTS
    # ---------------------------------------------------------
    if _table_exists(storage, "rollback_events"):
        df = _query_df(storage, "SELECT * FROM rollback_events ORDER BY created_at_ms DESC LIMIT 500")
        _add_rows(rows, df, "Rollback", "rollback_action", actor_col="actor", status_col="status")

    # ---------------------------------------------------------
    # CASE EVENTS
    # ---------------------------------------------------------
    if _table_exists(storage, "case_events"):
        df = _query_df(storage, "SELECT * FROM case_events ORDER BY created_at_ms DESC LIMIT 500")
        _add_rows(rows, df, "Case Timeline", "event_type", actor_col="actor", status_col="status")

    # ---------------------------------------------------------
    # CUSTODY EVENTS
    # ---------------------------------------------------------
    if _table_exists(storage, "custody_events"):
        df = _query_df(storage, "SELECT * FROM custody_events ORDER BY timestamp_ms DESC LIMIT 500")
        _add_rows(rows, df, "Evidence Custody", "event_type", actor_col="actor", ts_col="timestamp_ms")

    if not rows:
        st.info("No replayable forensic events found yet.")
        return

    replay = pd.DataFrame(rows)

    if case_id.strip():
        needle = case_id.strip().lower()
        replay = replay[
            replay.apply(
                lambda row: needle in str(row.to_dict()).lower(),
                axis=1,
            )
        ]

    replay = replay.sort_values("timestamp", ascending=True)

    st.metric("Replay Events", len(replay))

    

    handlers = GovernanceActionHandlers(storage)

    current_user = (
            st.session_state.get("username")
            or st.session_state.get("user_email")
            or "analyst"
    )

    for idx, r in replay.iterrows():

        details = r.get("details", {}) or {}

        decision_id = (
                details.get("decision_id")
                or r.get("trace")
        )

        evidence_id = details.get("evidence_id")

        case_ref = (
                details.get("case_id")
                or details.get("run_id")
        )

        severity = (
                details.get("severity")
                or details.get("risk")
                or "INFO"
        )

        rollback_available = bool(
            details.get("rollback_available")
            or details.get("rollback")
            or False
        )

        with st.container(border=True):

            # -------------------------------------------------
            # HEADER
            # -------------------------------------------------

            top_col1, top_col2 = st.columns([4, 1])

            with top_col1:

                st.markdown(
                    f"""
                    ### 🧬 {r['source']}

                    **Event:** {r['event']}

                    **Status:** {r.get('status', '')}

                    **Actor:** {r.get('actor', '')}

                    **Severity:** {severity}

                    **Trace:** `{r.get('trace', '')}`

                    **Case:** `{case_ref or 'N/A'}`

                    **Decision ID:** `{decision_id or 'N/A'}`

                    **Evidence ID:** `{evidence_id or 'N/A'}`
                    """
                )

            with top_col2:

                st.caption(
                    f"Timestamp: {r.get('timestamp')}"
                )

            # -------------------------------------------------
            # DETAILS
            # -------------------------------------------------

            with st.expander(
                    "Details",
                    expanded=False,
            ):

                st.json(details)

            # -------------------------------------------------
            # ACTION CONTROLS
            # -------------------------------------------------

            replay_col, rollback_col, seal_col, investigate_col = st.columns(4)

            # ---------------------------------------------
            # REPLAY EXECUTION
            # ---------------------------------------------
            with replay_col:

                if st.button(
                        "▶ Replay",
                        key=f"replay_{idx}",
                        use_container_width=True,
                ):
                    storage.governance.record_governance_event(
                        event_type="FORENSIC_REPLAY_TRIGGERED",
                        actor=current_user,
                        action=r["event"],
                        severity=severity,
                        status="REPLAYING",
                        decision_id=decision_id,
                        evidence_id=evidence_id,
                        case_id=case_ref,
                        details={
                            "source": r["source"],
                            "replay_index": idx,
                        },
                    )

                    st.success(
                        "Replay initiated."
                    )

            # ---------------------------------------------
            # ROLLBACK ACTION
            # ---------------------------------------------
            with rollback_col:

                rollback_disabled = (
                        not rollback_available
                        or not decision_id
                )

                if st.button(
                        "↩ Rollback",
                        key=f"rollback_{idx}",
                        disabled=rollback_disabled,
                        use_container_width=True,
                ):

                    result = handlers.rollback_action(
                        decision_id=decision_id,
                        actor=current_user,
                        rollback_reason="Manual rollback from forensic replay",
                    )

                    if result.get("success"):

                        st.warning(
                            "Rollback initiated."
                        )

                        st.rerun()

                    else:

                        st.error(
                            result.get("reason")
                        )

            # ---------------------------------------------
            # SEAL EVIDENCE
            # ---------------------------------------------
            with seal_col:

                seal_disabled = not evidence_id

                if st.button(
                        "🔒 Seal Evidence",
                        key=f"seal_{idx}",
                        disabled=seal_disabled,
                        use_container_width=True,
                ):

                    result = handlers.seal_evidence(
                        evidence_id=evidence_id,
                        actor=current_user,
                        reason="Manual sealing from forensic replay",
                    )

                    if result.get("success"):

                        st.success(
                            "Evidence sealed."
                        )

                        st.rerun()

                    else:

                        st.error(
                            result.get("reason")
                        )

            # ---------------------------------------------
            # OPEN INVESTIGATION
            # ---------------------------------------------
            with investigate_col:

                open_disabled = not case_ref

                if st.button(
                        "🕵 Open Investigation",
                        key=f"investigate_{idx}",
                        disabled=open_disabled,
                        use_container_width=True,
                ):
                    st.session_state[
                        "selected_case_id"
                    ] = case_ref

                    storage.governance.record_governance_event(
                        event_type="FORENSIC_INVESTIGATION_OPENED",
                        actor=current_user,
                        action="OPEN_INVESTIGATION",
                        severity=severity,
                        status="INVESTIGATION_OPENED",
                        case_id=case_ref,
                        evidence_id=evidence_id,
                        decision_id=decision_id,
                        details={
                            "source": r["source"],
                            "replay_index": idx,
                        },
                    )

                    st.success(
                        f"Investigation opened for {case_ref}"
                    )

            # -------------------------------------------------
            # TIMELINE RECONSTRUCTION
            # -------------------------------------------------

            if decision_id:

                with st.expander(
                        f"Timeline Reconstruction #{idx}",
                        expanded=False,
                ):

                    try:

                        traces = (
                            storage.governance.get_execution_traces(
                                decision_id=decision_id,
                                limit=100,
                            )
                        )

                    except Exception as e:

                        st.error(
                            f"Failed loading traces: {e}"
                        )

                        traces = []

                    if not traces:

                        st.info(
                            "No execution traces available."
                        )

                    else:

                        for t_idx, trace in enumerate(traces):

                            st.markdown(
                                f"""
                                ### ⚙ {trace.get('stage')}

                                **Status:** {trace.get('status')}

                                **Actor:** {trace.get('actor')}

                                **Action:** {trace.get('action')}

                                **Message:** {trace.get('message')}
                                """
                            )

                            payload = (
                                    trace.get("payload")
                                    or {}
                            )

                            if payload:
                                st.json(payload)

                            if t_idx < len(traces) - 1:
                                st.markdown("---")