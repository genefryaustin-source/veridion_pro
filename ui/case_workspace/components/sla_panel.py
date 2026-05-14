import streamlit as st
import datetime


def render_sla_panel(storage, case):

    created_ms = case.get("created_at_ms")

    if not created_ms:
        st.info("No SLA data available")
        return

    created = datetime.datetime.fromtimestamp(
        created_ms / 1000
    )

    now = datetime.datetime.utcnow()

    age = now - created

    st.subheader("⏱ SLA Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Case Age",
            str(age).split(".")[0]
        )

    with col2:
        if age.total_seconds() > 86400:
            st.error("SLA BREACHED")
        else:
            st.success("Within SLA")

    with col3:
        remaining = max(
            0,
            86400 - int(age.total_seconds())
        )

        st.metric(
            "SLA Remaining",
            f"{remaining // 3600}h"
        )