import streamlit as st


def render_escalation_panel(storage, case):

    ledger = storage.ledger

    case_id = case.get("id")

    st.subheader("🚨 Escalation")

    if hasattr(ledger, "evaluate_case_escalation"):

        result = ledger.evaluate_case_escalation(case_id)

        if not result:
            st.success("No escalation active")
            return

        level = result.get("escalation", "LOW")

        reason = result.get("reason", "No reason provided")

        if level == "CRITICAL":
            st.error(f"CRITICAL ESCALATION — {reason}")

        elif level == "HIGH":
            st.warning(f"HIGH ESCALATION — {reason}")

        elif level == "MEDIUM":
            st.info(f"MEDIUM ESCALATION — {reason}")

        else:
            st.success("No escalation active")