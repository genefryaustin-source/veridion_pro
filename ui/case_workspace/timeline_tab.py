import json
import datetime
import streamlit as st


def _format_ts(ms):
    if not ms:
        return "-"

    try:
        return datetime.datetime.fromtimestamp(
            int(ms) / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ms)


def _safe_json(raw):
    try:
        return json.loads(raw or "{}")
    except Exception:
        return {}





def _add_event(events, timestamp, event_type, severity, summary, source, metadata=None):
    events.append(
        {
            "timestamp": timestamp or 0,
            "event_type": event_type or "EVENT",
            "severity": severity or "INFO",
            "summary": summary or "",
            "source": source or "system",
            "metadata": metadata or {},
        }
    )










def _severity_badge(severity):
    severity = (severity or "INFO").upper()

    if severity in ["CRITICAL", "FAILED"]:
        return "🔴"

    if severity in ["HIGH", "WARNING", "RETRY"]:
        return "🟠"

    if severity in ["MEDIUM", "PROCESSING"]:
        return "🟡"

    if severity in ["COMPLETED", "LOW", "INFO"]:
        return "🟢"

    return "⚪"


def render_timeline_tab(
    storage,
    case,
    timeline,
):
    st.subheader("🕒 Investigation Timeline")

    events = timeline or []

    if not events:
        st.info("No timeline events found.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Timeline Events",
            len(events),
        )

    with col2:
        sources = sorted(
            set(e["source"] for e in events)
        )

        st.metric(
            "Sources",
            len(sources),
        )

    st.divider()

    source_filter = st.selectbox(
        "Filter Source",
        ["ALL"] + sources,
        key=f"timeline_source_filter_{case.get('id') or case.get('case_id')}",
    )

    st.divider()

    for event in events:
        if source_filter != "ALL" and event["source"] != source_filter:
            continue

        badge = _severity_badge(
            event.get("severity")
        )

        st.markdown(
            f"""
            <div style="
                border:1px solid #333;
                border-radius:8px;
                padding:12px;
                margin-bottom:10px;
                background:#111;
            ">
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:6px;
                ">
                    <div style="
                        font-size:15px;
                        font-weight:bold;
                        color:white;
                    ">
                        {badge} {event["event_type"]}
                    </div>

                    <div style="
                        font-size:12px;
                        color:#aaa;
                    ">
                        {_format_ts(event["timestamp"])}
                    </div>
                </div>

                <div style="
                    font-size:14px;
                    color:#ddd;
                    margin-bottom:6px;
                ">
                    {event["summary"]}
                </div>

                <div style="
                    font-size:12px;
                    color:#888;
                ">
                    Source: {event["source"]} | Severity: {event["severity"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Details", expanded=False):
            st.json(event.get("metadata") or {})