import streamlit as st
import datetime


def render_evidence_board(
    storage,
    evidence,
):

    st.subheader("📄 Evidence Board")

    if not evidence:
        st.info("No evidence linked")
        return

    sorted_evidence = sorted(
        evidence,
        key=lambda x: (
            x.get("created_at_ms") or 0
        ),
        reverse=True
    )

    for e in sorted_evidence[:10]:

        eid = (
            e.get("evidence_id")
            or e.get("id")
        )

        name = (
            e.get("suggested_name")
            or f"Evidence {eid}"
        )

        created = e.get(
            "created_at_ms"
        )

        created_str = "-"

        if created:
            created_str = datetime.datetime.fromtimestamp(
                created / 1000
            ).strftime("%Y-%m-%d %H:%M")

        st.markdown(f"""
        <div style="
            border:1px solid #333;
            border-radius:8px;
            padding:12px;
            margin-bottom:10px;
            background:#111;
        ">
            <div style="
                font-weight:bold;
                margin-bottom:5px;
            ">
                📄 {name}
            </div>

            <div style="
                font-size:12px;
                color:#999;
            ">
                Evidence ID: {eid}
            </div>

            <div style="
                font-size:12px;
                color:#999;
            ">
                Created: {created_str}
            </div>
        </div>
        """, unsafe_allow_html=True)