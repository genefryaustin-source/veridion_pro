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


def render_notes_tab(storage, case):

    ledger = storage.ledger

    case_id = case.get("id")

    st.subheader("📝 Case Notes")

    # -----------------------------------
    # NOTE INPUT
    # -----------------------------------
    note_input = st.text_area(
        "Add Investigation Note",
        height=150,
        key=f"case_note_input_{case_id}",
    )

    col1, col2 = st.columns([1, 5])

    with col1:

        if st.button(
            "Add Note",
            key=f"case_note_btn_{case_id}"
        ):

            if note_input.strip():

                ledger.add_case_note(
                    case_id,
                    note_input
                )

                if hasattr(ledger, "add_case_event"):

                    ledger.add_case_event(
                        case_id,
                        "NOTE_ADDED",
                        note_input[:100]
                    )

                st.success("Note added")
                st.rerun()

            else:
                st.warning("Note cannot be empty")

    st.divider()

    # -----------------------------------
    # NOTE HISTORY
    # -----------------------------------
    notes = ledger.get_case_notes(case_id)

    if not notes:
        st.info("No notes recorded")
        return

    st.subheader("📚 Investigation Notes")

    for note in reversed(notes):

        ts = _format_ts(
            note.get("created_at_ms")
        )

        st.markdown(f"""
        <div style="
            border:1px solid #333;
            border-radius:8px;
            padding:12px;
            margin-bottom:10px;
            background-color:#111;
        ">
            <div style="
                font-size:12px;
                color:#999;
                margin-bottom:8px;
            ">
                {ts}
            </div>

            <div style="
                white-space:pre-wrap;
            ">
                {note.get("note", "")}
            </div>
        </div>
        """, unsafe_allow_html=True)