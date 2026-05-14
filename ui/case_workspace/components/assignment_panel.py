import streamlit as st


def render_assignment_panel(storage, case):

    ledger = storage.ledger

    case_id = case.get("id")

    st.subheader("👤 Assignment")

    current_owner = case.get("assigned_to")

    col1, col2 = st.columns([3, 1])

    with col1:
        new_owner = st.text_input(
            "Assigned Analyst",
            value=current_owner or "",
            key=f"assignment_owner_{case_id}"
        )

    with col2:
        if st.button(
            "Assign",
            key=f"assignment_btn_{case_id}"
        ):

            ledger.assign_case(
                case_id=case_id,
                assigned_to=new_owner,
                assigned_by="analyst",
            )

            if hasattr(ledger, "add_case_event"):
                ledger.add_case_event(
                    case_id,
                    "CASE_ASSIGNED",
                    f"Assigned to {new_owner}"
                )

            st.success("Assignment updated")
            st.rerun()

    if current_owner:
        st.info(f"Current Owner: {current_owner}")
    else:
        st.warning("Case is currently unassigned")