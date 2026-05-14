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


def render_execution_timeline(storage=None):
    st.subheader("📡 Live AI Operations Feed")
    st.caption("Agent decisions, approvals, escalations, SLA breaches, containment, rollback, and evidence mutation activity.")

    rows = []

    sources = [
        ("orchestration_decisions", "created_at_ms", "AI Decision"),
        ("governance_events", "created_at_ms", "Governance"),
        ("approval_requests", "created_at_ms", "Approval"),
        ("rollback_events", "created_at_ms", "Rollback"),
        ("case_events", "created_at_ms", "Case Event"),
        ("custody_events", "timestamp_ms", "Evidence"),
    ]

    for table, ts_col, label in sources:
        if not _table_exists(storage, table):
            continue

        df = _query_df(storage, f"SELECT * FROM {table} ORDER BY {ts_col} DESC LIMIT 100")

        for _, r in df.iterrows():
            event = (
                r.get("event_type")
                or r.get("action")
                or r.get("recommendation")
                or r.get("final_action")
                or r.get("rollback_action")
                or label
            )

            rows.append({
                "Timestamp": r.get(ts_col),
                "Type": label,
                "Event": event,
                "Status": r.get("status") or r.get("outcome") or "",
                "Severity": r.get("severity") or r.get("risk") or "",
                "Trace": r.get("decision_id") or r.get("run_id") or r.get("case_id") or r.get("evidence_id") or "",
            })

    if not rows:
        st.info("No live execution events yet.")
        return

    df_out = pd.DataFrame(rows).sort_values("Timestamp", ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric("Feed Events", len(df_out))
    c2.metric("Rollback Events", int((df_out["Type"] == "Rollback").sum()))
    c3.metric("Approval Events", int((df_out["Type"] == "Approval").sum()))

    st.dataframe(df_out, use_container_width=True, hide_index=True)