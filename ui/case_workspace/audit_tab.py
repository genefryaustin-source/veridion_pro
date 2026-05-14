import streamlit as st
import datetime


def _format_ts(ms):

    if not ms:
        return "-"

    try:
        return datetime.datetime.fromtimestamp(
            int(ms) / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return "-"


def render_audit_tab(storage, case):

    ledger = storage.ledger

    case_id = case.get("id")

    st.subheader("🧾 Audit Log")

    audit = ledger.get_case_audit_log(
        case_id
    )

    if not audit:
        st.info("No audit records")
        return

    for entry in reversed(audit):

        ts = _format_ts(
            entry.get("created_at_ms")
        )

        action = entry.get("action")
        user = entry.get("performed_by")
        details = entry.get("details")

        st.markdown(f"""
        <div style="
            border-left:4px solid #4CAF50;
            padding:10px;
            margin-bottom:10px;
            background:#111;
            border-radius:6px;
        ">

        <div style="
            font-weight:bold;
            margin-bottom:5px;
        ">
            {action}
        </div>

        <div style="
            font-size:12px;
            color:#aaa;
            margin-bottom:6px;
        ">
            {user} — {ts}
        </div>

        <div>
            {details or ""}
        </div>

        </div>
        """, unsafe_allow_html=True)