import streamlit as st

from core.services.cases.case_intelligence_service import (analyze_case_intelligence)

from core.cases.case_evidence_service import (
    build_case_evidence_context
)


def aggregate_case_text(
    evidence_records,
    limit_per_record=3000,
    max_records=10,
):

    texts = []

    for r in evidence_records[:max_records]:

        text = (
            r.get("text")
            or ""
        )

        if not text.strip():
            continue

        eid = r.get("id")

        texts.append(
            f"--- Evidence {eid} ---\n"
            f"{text[:limit_per_record]}"
        )

    return "\n\n".join(texts)


def render_risk_badge(
    score,
    severity,
):

    if severity == "CRITICAL":

        st.error(
            f"Risk Score: {score}/100 — {severity}"
        )

    elif severity == "HIGH":

        st.warning(
            f"Risk Score: {score}/100 — {severity}"
        )

    elif severity == "MEDIUM":

        st.info(
            f"Risk Score: {score}/100 — {severity}"
        )

    else:

        st.success(
            f"Risk Score: {score}/100 — {severity}"
        )


def render_intelligence_tab(
    storage,
    case,
    alerts,
    evidence,
):

    ledger = storage.ledger

    case_id = case.get("id")

    st.subheader("🧠 Case Intelligence")

    # -----------------------------------
    # BUILD EVIDENCE CONTEXT
    # -----------------------------------
    evidence_ctx = build_case_evidence_context(
        ledger=ledger,
        evidence=evidence,
    )

    evidence_records = (
        evidence_ctx.get("records")
        or []
    )

    # -----------------------------------
    # AGGREGATE TEXT
    # -----------------------------------
    combined_text = aggregate_case_text(
        evidence_records
    )

    # -----------------------------------
    # GENERATE INTELLIGENCE
    # -----------------------------------
    intelligence = analyze_case_intelligence(
        text=combined_text,
        case=case,
        alerts=alerts,
        evidence=evidence,
    )

    score = intelligence.get(
        "risk_score",
        0
    )

    severity = intelligence.get(
        "severity",
        "LOW"
    )

    findings = intelligence.get(
        "findings",
        []
    )

    recommendations = intelligence.get(
        "recommendations",
        []
    )

    summary = intelligence.get(
        "summary",
        ""
    )

    # -----------------------------------
    # RISK BADGE
    # -----------------------------------
    render_risk_badge(
        score,
        severity,
    )

    st.divider()

    # -----------------------------------
    # SUMMARY
    # -----------------------------------
    st.subheader("📘 Investigation Summary")

    st.write(summary)

    st.divider()

    # -----------------------------------
    # FINDINGS
    # -----------------------------------
    st.subheader("🔎 Findings")

    if not findings:

        st.info(
            "No significant findings detected."
        )

    else:

        for level, message in findings:

            if level == "CRITICAL":

                st.error(
                    f"{level}: {message}"
                )

            elif level == "HIGH":

                st.warning(
                    f"{level}: {message}"
                )

            elif level == "MEDIUM":

                st.info(
                    f"{level}: {message}"
                )

            else:

                st.write(
                    f"{level}: {message}"
                )

    st.divider()

    # -----------------------------------
    # RECOMMENDATIONS
    # -----------------------------------
    st.subheader("✅ Recommendations")

    if not recommendations:

        st.info(
            "No recommendations generated."
        )

    else:

        for r in recommendations:

            st.write(f"- {r}")

    st.divider()

    # -----------------------------------
    # INTELLIGENCE METRICS
    # -----------------------------------
    st.subheader("📊 Intelligence Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Evidence Records",
            len(evidence_records)
        )

    with col2:
        st.metric(
            "Critical Evidence",
            evidence_ctx.get(
                "critical",
                0
            )
        )

    with col3:
        st.metric(
            "High Risk Evidence",
            evidence_ctx.get(
                "high",
                0
            )
        )

    with col4:
        st.metric(
            "Alerts",
            len(alerts)
        )
