import streamlit as st
from collections import defaultdict


ENTITY_COLORS = {
    "PERSON": "#4CAF50",
    "EMAIL": "#2196F3",
    "PHONE": "#FF9800",
    "IP": "#E91E63",
    "DOMAIN": "#9C27B0",
    "HOST": "#795548",
    "FILE": "#607D8B",
    "HASH": "#F44336",
    "CUI": "#D32F2F",
    "UNKNOWN": "#777777",
}


def normalize_entity(entity):

    if not isinstance(entity, dict):
        return None

    value = (
        entity.get("value")
        or entity.get("entity")
        or entity.get("text")
        or ""
    ).strip()

    if not value:
        return None

    label = (
        entity.get("label")
        or entity.get("type")
        or "UNKNOWN"
    ).upper()

    confidence = entity.get(
        "confidence",
        "-"
    )

    source = entity.get(
        "source",
        "Unknown"
    )

    return {
        "value": value,
        "label": label,
        "confidence": confidence,
        "source": source,
    }


def render_entity_card(
    storage,
    case_id,
    entity,
):

    ledger = storage.ledger

    label = entity["label"]

    color = ENTITY_COLORS.get(
        label,
        "#777777"
    )

    normalized_value = (
        entity["value"]
        .strip()
        .lower()
    )

    pivot_cases = []

    # -----------------------------------
    # CROSS-CASE PIVOTS
    # -----------------------------------
    try:

        with ledger._connect() as con:

            rows = con.execute(
                """
                SELECT DISTINCT
                    ce.case_id,
                    c.title,
                    c.status
                FROM case_entities ce
                JOIN entities e
                    ON ce.entity_id = e.entity_id
                LEFT JOIN cases c
                    ON c.case_id = ce.case_id
                WHERE e.normalized_value = ?
                  AND ce.case_id != ?
                """,
                (
                    normalized_value,
                    case_id,
                ),
            ).fetchall()

            pivot_cases = [
                dict(r)
                for r in rows
            ]

    except Exception as ex:

        st.error(
            f"Pivot lookup failed: {ex}"
        )

    # -----------------------------------
    # ENTITY CARD
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
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:8px;
        ">

            <div style="
                font-weight:bold;
                font-size:16px;
            ">
                {entity["value"]}
            </div>

            <div style="
                background:{color};
                color:white;
                padding:4px 8px;
                border-radius:6px;
                font-size:12px;
                font-weight:bold;
            ">
                {label}
            </div>

        </div>

        <div style="
            font-size:12px;
            color:#aaa;
        ">
            Confidence: {entity["confidence"]}
        </div>

        <div style="
            font-size:12px;
            color:#aaa;
        ">
            Source: {entity["source"]}
        </div>

    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------
    # CROSS-CASE RESULTS
    # -----------------------------------
    if pivot_cases:

        st.warning(
            f"Cross-case pivot detected "
            f"({len(pivot_cases)} related cases)"
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
            "No related investigations found."
        )


def render_entities_tab(
    storage,
    case,
    entities,
):

    ledger = storage.ledger

    case_id = case.get("id")

    st.subheader("🧬 Extracted Entities")

    entities = []

    case_id = (
            case.get("id")
            or case.get("case_id")
    )

    st.subheader("🧬 Extracted Entities")

    # -----------------------------------
    # NORMALIZE
    # -----------------------------------
    clean_entities = []

    for e in entities:

        normalized = normalize_entity(e)

        if normalized:
            clean_entities.append(
                normalized
            )

    # -----------------------------------
    # GROUP BY TYPE
    # -----------------------------------
    grouped = defaultdict(list)

    for e in clean_entities:

        grouped[
            e["label"]
        ].append(e)

    # -----------------------------------
    # METRICS
    # -----------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Entities",
            len(clean_entities)
        )

    with col2:
        st.metric(
            "Entity Types",
            len(grouped)
        )

    st.divider()

    # -----------------------------------
    # FILTER
    # -----------------------------------
    labels = sorted(
        grouped.keys()
    )

    selected = st.selectbox(
        "Filter Entity Type",
        ["ALL"] + labels,
        key=f"entity_filter_{case_id}",
    )

    st.divider()

    # -----------------------------------
    # RENDER GROUPS
    # -----------------------------------
    for label in sorted(grouped.keys()):

        if (
            selected != "ALL"
            and label != selected
        ):
            continue

        items = grouped[label]

        with st.expander(
            f"{label} ({len(items)})",
            expanded=True
        ):

            for entity in items:
                render_entity_card(
                    storage=storage,
                    case_id=case_id,
                    entity=entity,
                )