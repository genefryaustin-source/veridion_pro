import streamlit as st
from collections import defaultdict


RELATIONSHIP_COLORS = {
    "RELATED_TO": "#4CAF50",
    "COMMUNICATED_WITH": "#2196F3",
    "ATTACHED_TO": "#FF9800",
    "OBSERVED_WITH": "#9C27B0",
    "LINKED_TO": "#E91E63",
    "CO_OCCURRENCE": "#00BCD4",
    "UNKNOWN": "#777777",
}





def normalize_relationship(rel):

    if not isinstance(rel, dict):
        return None

    source = (
        rel.get("source_value")
        or rel.get("source")
        or rel.get("source_entity")
        or rel.get("from")
        or "Unknown"
    )

    target = (
        rel.get("target_value")
        or rel.get("target")
        or rel.get("target_entity")
        or rel.get("to")
        or "Unknown"
    )

    relation = (
        rel.get("relationship_type")
        or rel.get("relationship")
        or rel.get("type")
        or "RELATED_TO"
    ).upper()

    confidence = rel.get(
        "confidence",
        "-"
    )

    evidence_id = rel.get(
        "evidence_id",
        "-"
    )

    return {
        "source": source,
        "target": target,
        "relationship": relation,
        "confidence": confidence,
        "evidence_id": evidence_id,
    }


def render_relationship_card(
    storage,
    case_id,
    rel,
):

    relation = rel["relationship"]

    color = RELATIONSHIP_COLORS.get(
        relation,
        "#777777"
    )

    pivot_cases = []

    # -----------------------------------
    # CROSS-CASE RELATIONSHIP PIVOTS
    # -----------------------------------
    try:

        with storage.ledger._connect() as con:

            rows = con.execute(
                """
                SELECT DISTINCT
                    ce.case_id,
                    c.title,
                    c.status

                FROM relationship_edges re

                JOIN entities s
                    ON re.source_entity_id = s.entity_id

                JOIN entities t
                    ON re.target_entity_id = t.entity_id

                JOIN case_entities ce
                    ON ce.entity_id = s.entity_id

                LEFT JOIN cases c
                    ON c.case_id = ce.case_id

                WHERE
                    LOWER(s.entity_value) = ?
                    AND LOWER(t.entity_value) = ?
                    AND ce.case_id != ?
                """,
                (
                    rel["source"].lower(),
                    rel["target"].lower(),
                    case_id,
                ),
            ).fetchall()

            pivot_cases = [
                dict(r)
                for r in rows
            ]

    except Exception:
        pivot_cases = []

    # -----------------------------------
    # RELATIONSHIP CARD
    # -----------------------------------
    st.markdown(f"""
    <div style="
        border:1px solid #333;
        border-radius:8px;
        padding:12px;
        margin-bottom:10px;
        background:#111;
    ">

        <div style="
            font-size:15px;
            margin-bottom:10px;
            word-wrap:break-word;
        ">

            <b>{rel["source"]}</b>

            <span style="
                color:{color};
                font-weight:bold;
                margin-left:8px;
                margin-right:8px;
            ">
                ── {relation} ──▶
            </span>

            <b>{rel["target"]}</b>

        </div>

        <div style="
            font-size:12px;
            color:#aaa;
            margin-bottom:4px;
        ">
            Confidence: {rel["confidence"]}
        </div>

        <div style="
            font-size:12px;
            color:#aaa;
        ">
            Evidence ID: {rel["evidence_id"]}
        </div>

    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------
    # CROSS-CASE RESULTS
    # -----------------------------------
    if pivot_cases:

        st.warning(
            f"Relationship appears in "
            f"{len(pivot_cases)} other case(s)"
        )

        for p in pivot_cases:

            st.markdown(f"""
            <div style="
                border:1px solid #444;
                border-radius:6px;
                padding:10px;
                margin-bottom:8px;
                background:#181818;
            ">

                <div style="
                    font-weight:bold;
                    color:white;
                    margin-bottom:4px;
                ">
                    {p.get("title") or "Untitled Case"}
                </div>

                <div style="
                    font-size:12px;
                    color:#aaa;
                ">
                    Case ID: {p.get("case_id")}
                </div>

                <div style="
                    font-size:12px;
                    color:#aaa;
                ">
                    Status: {p.get("status")}
                </div>

            </div>
            """, unsafe_allow_html=True)

    else:

        st.success(
            "No related relationship pivots found."
        )


def render_relationships_tab(
    storage,
    case,
    relationships,
):



    st.subheader("🕸️ Relationship Intelligence")
    case_id = (
            case.get("id")
            or case.get("case_id")
    )


    # -----------------------------------
    # NORMALIZE
    # -----------------------------------
    clean_relationships = []

    for r in relationships:

        normalized = normalize_relationship(r)

        if normalized:

            clean_relationships.append(
                normalized
            )

    # -----------------------------------
    # GROUP
    # -----------------------------------
    grouped = defaultdict(list)

    for r in clean_relationships:

        grouped[
            r["relationship"]
        ].append(r)

    # -----------------------------------
    # METRICS
    # -----------------------------------
    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Relationships",
            len(clean_relationships)
        )

    with col2:

        st.metric(
            "Relationship Types",
            len(grouped)
        )

    st.divider()

    # -----------------------------------
    # FILTER
    # -----------------------------------
    relationship_types = sorted(
        grouped.keys()
    )

    selected = st.selectbox(
        "Filter Relationship Type",
        ["ALL"] + relationship_types,
        key=f"relationship_filter_{case_id}",
    )

    st.divider()

    # -----------------------------------
    # RENDER
    # -----------------------------------
    for rel_type in sorted(grouped.keys()):

        if (
            selected != "ALL"
            and rel_type != selected
        ):
            continue

        items = grouped[rel_type]

        with st.expander(
            f"{rel_type} ({len(items)})",
            expanded=True
        ):

            for rel in items:

                render_relationship_card(
                    storage=storage,
                    case_id=case_id,
                    rel=rel,
                )