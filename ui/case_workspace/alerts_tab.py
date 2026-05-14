import streamlit as st


def render_alerts_tab(alerts):

    st.subheader("🚨 Linked Alerts")

    if not alerts:
        st.info("No alerts linked")
        return

    for alert in alerts:

        severity = (
            alert.get("severity") or "LOW"
        ).upper()

        message = (
            alert.get("message")
            or "No message"
        )

        source = (
            alert.get("source")
            or "Unknown"
        )

        if severity == "CRITICAL":

            st.error(
                f"[{severity}] {message}"
            )

        elif severity == "HIGH":

            st.warning(
                f"[{severity}] {message}"
            )

        elif severity == "MEDIUM":

            st.info(
                f"[{severity}] {message}"
            )

        else:

            st.write(
                f"[{severity}] {message}"
            )

        st.caption(
            f"Source: {source}"
        )