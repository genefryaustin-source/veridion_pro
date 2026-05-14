import pandas as pd
import streamlit as st


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


def render_operational_memory_panel(storage=None):
    st.subheader("🧠 Operational Memory")
    st.caption("Human/AI learning layer: success rates, overrides, rollback frequency, approval latency, escalation outcomes, and tenant behavior.")

    metrics = {
        "successful_actions": 0,
        "failed_actions": 0,
        "analyst_overrides": 0,
        "rollback_events": 0,
        "approval_requests": 0,
        "approved": 0,
        "rejected": 0,
        "escalations": 0,
    }

    # ---------------------------------------------------------
    # ORCHESTRATION OUTCOMES
    # ---------------------------------------------------------
    if _table_exists(storage, "orchestration_decisions"):
        df = _query_df(storage, "SELECT * FROM orchestration_decisions")

        if not df.empty:
            outcome = df.get("outcome", pd.Series(dtype=str)).astype(str).str.upper()
            metrics["successful_actions"] = int(outcome.isin(["SUCCESS", "SUCCEEDED", "COMPLETED", "APPROVED"]).sum())
            metrics["failed_actions"] = int(outcome.isin(["FAILED", "ERROR", "REJECTED", "BLOCKED"]).sum())

            if "confidence" in df.columns:
                avg_conf = pd.to_numeric(df["confidence"], errors="coerce").mean()
            else:
                avg_conf = 0
        else:
            avg_conf = 0
    else:
        avg_conf = 0

    # ---------------------------------------------------------
    # OVERRIDES
    # ---------------------------------------------------------
    if _table_exists(storage, "analyst_overrides"):
        df = _query_df(storage, "SELECT * FROM analyst_overrides")
        metrics["analyst_overrides"] = len(df)

    # ---------------------------------------------------------
    # ROLLBACKS
    # ---------------------------------------------------------
    if _table_exists(storage, "rollback_events"):
        df = _query_df(storage, "SELECT * FROM rollback_events")
        metrics["rollback_events"] = len(df)

    # ---------------------------------------------------------
    # APPROVALS
    # ---------------------------------------------------------
    if _table_exists(storage, "approval_requests"):
        df = _query_df(storage, "SELECT * FROM approval_requests")
        metrics["approval_requests"] = len(df)

        if not df.empty and "status" in df.columns:
            status = df["status"].astype(str).str.upper()
            metrics["approved"] = int(status.isin(["APPROVED", "GRANTED"]).sum())
            metrics["rejected"] = int(status.isin(["REJECTED", "DENIED"]).sum())

    # ---------------------------------------------------------
    # ESCALATIONS
    # ---------------------------------------------------------
    if _table_exists(storage, "case_events"):
        df = _query_df(storage, "SELECT * FROM case_events")
        if not df.empty and "event_type" in df.columns:
            metrics["escalations"] = int(df["event_type"].astype(str).str.upper().str.contains("ESCAL").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Successful Actions", metrics["successful_actions"])
    c2.metric("Failed / Blocked", metrics["failed_actions"])
    c3.metric("Analyst Overrides", metrics["analyst_overrides"])
    c4.metric("Rollbacks", metrics["rollback_events"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Approval Requests", metrics["approval_requests"])
    c6.metric("Approved", metrics["approved"])
    c7.metric("Rejected", metrics["rejected"])
    c8.metric("Escalations", metrics["escalations"])

    st.divider()

    st.markdown("### AI Confidence Calibration")
    st.metric("Average Confidence", round(float(avg_conf or 0), 3))

    st.markdown("### Learning Signals")

    signals = []

    if metrics["analyst_overrides"] > 0:
        signals.append("Analyst intervention has occurred. Future autonomous actions should factor override history.")

    if metrics["rollback_events"] > 0:
        signals.append("Rollback activity detected. Increase caution on similar future actions.")

    if metrics["rejected"] > metrics["approved"]:
        signals.append("Approval rejection rate is high. Tenant may prefer manual review or narrower automation.")

    if metrics["escalations"] > 0:
        signals.append("Escalation pattern detected. Feed this into adaptive policy optimization.")

    if not signals:
        signals.append("No strong learning signals yet. Operational memory is ready and awaiting governance activity.")

    for s in signals:
        st.info(s)