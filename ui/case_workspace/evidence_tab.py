import streamlit as st
import datetime

from core.cases.case_evidence_service import (
    build_case_evidence_context,
    render_highlighted_text,
)


LEVEL_COLORS = {
    "CRITICAL": "red",
    "HIGH": "orange",
    "MEDIUM": "gold",
    "LOW": "green",
}


def _format_ts(ms):
    if not ms:
        return "-"

    try:
        return datetime.datetime.fromtimestamp(
            int(ms) / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "-"


def _render_score_badge(level, score):
    color = LEVEL_COLORS.get(level, "gray")

    st.markdown(
        f"""
        <span style="
            color:white;
            background:{color};
            padding:4px 8px;
            border-radius:6px;
            font-weight:bold;
        ">
            {level} — {score}/100
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_evidence_tab(storage, case, evidence, alerts=None):
    ledger = storage.ledger
    case_id = case.get("id")

    st.subheader("📄 Evidence Board")

    if not evidence:
        st.info("No evidence linked to this case.")
        return

    context_key = f"case_evidence_context_{case_id}"

    if (
        context_key not in st.session_state
        or st.button("🔄 Refresh Evidence Analysis", key=f"refresh_evidence_{case_id}")
    ):
        st.session_state[context_key] = build_case_evidence_context(
            ledger=ledger,
            evidence=evidence,
        )

    ctx = st.session_state[context_key]

    # ----------------------------
    # Evidence Metrics
    # ----------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total", ctx.get("total", 0))
    col2.metric("Critical", ctx.get("critical", 0))
    col3.metric("High", ctx.get("high", 0))
    col4.metric("Medium", ctx.get("medium", 0))
    col5.metric("Low", ctx.get("low", 0))

    st.divider()

    # ----------------------------
    # Filters
    # ----------------------------
    records = ctx.get("records", [])

    levels = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]

    selected_level = st.selectbox(
        "Filter by risk level",
        levels,
        key=f"evidence_level_filter_{case_id}",
    )

    search = st.text_input(
        "Search evidence text or filename",
        key=f"evidence_search_{case_id}",
    ).strip().lower()

    filtered = []

    for r in records:
        if selected_level != "ALL" and r.get("level") != selected_level:
            continue

        haystack = (
            (r.get("name") or "")
            + " "
            + (r.get("text") or "")
            + " "
            + (r.get("source") or "")
        ).lower()

        if search and search not in haystack:
            continue

        filtered.append(r)

    st.caption(f"Showing {len(filtered)} of {len(records)} evidence records")

    st.divider()

    # ----------------------------
    # Cluster View
    # ----------------------------
    view_mode = st.radio(
        "Evidence View",
        ["Ranked Evidence", "Clustered Evidence"],
        horizontal=True,
        key=f"evidence_view_mode_{case_id}",
    )

    if view_mode == "Clustered Evidence":
        _render_clustered_evidence(case_id, ctx)
    else:
        for record in filtered:
            _render_evidence_record(case_id, record)


def _render_clustered_evidence(case_id, ctx):
    clusters = ctx.get("clusters", {})

    if not clusters:
        st.info("No clusters available.")
        return

    for cluster_name, items in clusters.items():
        with st.expander(f"🧵 {cluster_name} ({len(items)})", expanded=True):
            for record in items:
                _render_evidence_record(case_id, record)


def _render_evidence_record(case_id, record):
    eid = record.get("id")
    name = record.get("name")
    level = record.get("level", "LOW")
    score = record.get("score", 0)
    text = record.get("text") or ""
    matches = record.get("matches") or []
    created = _format_ts(record.get("created_at_ms"))
    source = record.get("source") or "Unknown"
    sha256 = record.get("sha256") or "-"

    with st.container():
        st.markdown(f"### 📄 {name}")
        _render_score_badge(level, score)

        c1, c2, c3 = st.columns(3)

        c1.caption(f"Evidence ID: {eid}")
        c2.caption(f"Source: {source}")
        c3.caption(f"Created: {created}")

        st.caption(f"SHA256: {sha256}")

        match_counts = {}

        for m in matches:
            label = m.get("label", "UNKNOWN")
            match_counts[label] = match_counts.get(label, 0) + 1

        if match_counts:
            st.write(
                "Detected: "
                + ", ".join(
                    f"{k}: {v}"
                    for k, v in sorted(match_counts.items())
                )
            )
        else:
            st.info("No sensitive patterns detected in extracted text.")

        with st.expander("Preview + Highlighted Matches", expanded=False):
            if not text:
                st.warning("No extractable text available for this evidence.")
            else:
                labels = sorted(set(m.get("label") for m in matches if m.get("label")))

                filter_label = st.selectbox(
                    "Highlight filter",
                    ["ALL"] + labels,
                    key=f"match_filter_{case_id}_{eid}",
                )

                if filter_label == "ALL":
                    filter_label = None

                preview = text[:5000]

                html = render_highlighted_text(
                    preview,
                    matches,
                    filter_label=filter_label,
                )

                st.markdown(
                    f"""
                    <div style="
                        font-family: monospace;
                        white-space: pre-wrap;
                        border:1px solid #333;
                        border-radius:8px;
                        padding:12px;
                        background:#111;
                        max-height:500px;
                        overflow:auto;
                    ">
                    {html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.caption("Raw preview")
                st.code(preview[:1000])

        st.divider()