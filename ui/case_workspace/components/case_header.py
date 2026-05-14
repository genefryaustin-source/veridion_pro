import streamlit as st
import datetime


def _format_created(ts):

    if not ts:
        return "-"

    try:

        if isinstance(ts, (int, float)):

            return datetime.datetime.fromtimestamp(
                int(ts) / 1000
            ).strftime(
                "%Y-%m-%d %H:%M"
            )

        return str(ts)

    except Exception:

        return str(ts)


def render_case_header(
    storage,
    case,
    alerts,
    evidence,
):

    case_id = case.get("id")

    title = (
        case.get("title")
        or f"Case {case_id}"
    )

    status = case.get(
        "status",
        "OPEN"
    )

    owner = (
        case.get("assigned_to")
        or "Unassigned"
    )

    created = _format_created(
        case.get("created_at_ms")
    )

    st.markdown(
        f"""
### 📁 {title}

| Field | Value |
|---|---|
| Case ID | {case_id} |
| Status | {status} |
| Owner | {owner} |
| Alerts | {len(alerts)} |
| Evidence | {len(evidence)} |
| Created | {created} |
""",
        unsafe_allow_html=False
    )