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


def render_analyst_activity_panel(
    storage,
    case_id,
):

    ledger = storage.ledger

    events = ledger.get_case_timeline(
        case_id
    )

    analyst_events = []

    for e in events:

        et = e.get(
            "event_type",
            ""
        )

        if et in [
            "NOTE_ADDED",
            "CASE_ASSIGNED",
            "STATUS_CHANGE",
            "CASE_ESCALATED",
        ]:
            analyst_events.append(e)

    st.subheader("👤 Analyst Activity")

    if not analyst_events:
        st.info("No analyst activity")
        return

    for event in reversed(
        analyst_events[-20:]
    ):

        ts = _format_ts(
            event.get("created_at_ms")
        )

        st.markdown(f"""
        <div style="
            border-left:3px solid #4CAF50;
            padding:10px;
            margin-bottom:10px;
            background:#111;
            border-radius:6px;
        ">
            <div style="
                font-size:12px;
                color:#999;
                margin-bottom:4px;
            ">
                {ts}
            </div>

            <div style="
                font-weight:bold;
            ">
                {event.get("event_type")}
            </div>

            <div>
                {event.get("message")}
            </div>
        </div>
        """, unsafe_allow_html=True)