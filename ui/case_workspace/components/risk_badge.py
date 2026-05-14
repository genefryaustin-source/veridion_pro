import streamlit as st


def render_risk_badge(
    score=0,
    severity="LOW",
):

    severity = (
        severity or "LOW"
    ).upper()

    text = (
        f"Risk Score: "
        f"{score}/100 — {severity}"
    )

    if severity == "CRITICAL":

        st.error(text)

    elif severity == "HIGH":

        st.warning(text)

    elif severity == "MEDIUM":

        st.info(text)

    else:

        st.success(text)