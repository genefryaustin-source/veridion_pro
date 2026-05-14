import datetime
import streamlit as st

from ui.case_workspace.workspace_state import (
    WorkspaceState
)


def _format_ts(ms):

    if not ms:
        return "-"

    try:
        return datetime.datetime.fromtimestamp(
            int(ms) / 1000
        ).strftime("%Y-%m-%d %H:%M")

    except Exception:
        return "-"


def render_case_queue(storage):

    ledger = storage.ledger

    st.subheader("📁 Investigation Queue")

    cases = []

    if hasattr(
        ledger,
        "list_cases"
    ):

        cases = ledger.list_cases()

    if not cases:

        st.info(
            "No cases available."
        )

        return

    # -----------------------------------
    # FILTERS
    # -----------------------------------
    statuses = sorted(set(
        c.get("status", "OPEN")
        for c in cases
    ))

    selected_status = st.selectbox(
        "Filter Status",
        ["ALL"] + statuses,
        key="case_queue_status"
    )

    search = st.text_input(
        "Search Cases",
        key="case_queue_search"
    ).strip().lower()

    st.divider()

    # -----------------------------------
    # FILTER CASES
    # -----------------------------------
    filtered = []
    seen = set()

    for case in cases:

        case_id = case.get("id")

        if not case_id:
            continue

        if case_id in seen:
            continue

        seen.add(case_id)

        status = case.get(
            "status",
            "OPEN"
        )

        title = (
            case.get("title")
            or ""
        ).lower()

        if (
            selected_status != "ALL"
            and status != selected_status
        ):
            continue

        if (
            search
            and search not in title
        ):
            continue

        filtered.append(case)

    # -----------------------------------
    # RENDER CASES
    # -----------------------------------
    for idx, case in enumerate(filtered):

        case_id = case.get("id")

        title = (
            case.get("title")
            or f"Case {case_id}"
        )

        status = case.get(
            "status",
            "OPEN"
        )

        assigned_to = (
            case.get("assigned_to")
            or "Unassigned"
        )

        created = _format_ts(
            case.get("created_at_ms")
        )

        selected = (
            WorkspaceState.get_selected_case_id()
            == case_id
        )

        border = (
            "2px solid #4CAF50"
            if selected
            else "1px solid #333"
        )

        card_html = f"""
<div style="
    border:{border};
    border-radius:10px;
    padding:16px;
    margin-bottom:12px;
    background:#111111;
">

<div style="
    font-size:20px;
    font-weight:bold;
    margin-bottom:10px;
    color:white;
">
    📁 {title}
</div>

<div style="
    font-size:13px;
    color:#BBBBBB;
">
    <b>Status:</b> {status}
    &nbsp;&nbsp;|&nbsp;&nbsp;
    <b>Owner:</b> {assigned_to}
    &nbsp;&nbsp;|&nbsp;&nbsp;
    <b>Created:</b> {created}
</div>

</div>
"""

        st.markdown(
            card_html,
            unsafe_allow_html=True
        )

        if st.button(
            "Open Investigation",
            key=f"open_case_{case_id}_{idx}"
        ):

            WorkspaceState.set_selected_case_id(
                case_id
            )

            st.rerun()