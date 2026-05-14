import os
import tempfile
import sqlite3

import networkx as nx
import pandas as pd
import streamlit as st

from pyvis.network import Network


def render_relationship_graph(storage):

    st.title(
        "🕸️ Relationship Graph"
    )

    con = sqlite3.connect(
        storage.ledger.db_path
    )

    con.row_factory = sqlite3.Row

    # ---------------------------------------
    # 🔥 LOAD CORRELATIONS
    # ---------------------------------------

    rows = con.execute(
        """
        SELECT

            source_evidence_id,
            target_evidence_id,

            correlation_type,
            correlation_value,

            confidence,

            created_at_ms

        FROM evidence_correlations
        """
    ).fetchall()

    if not rows:

        st.warning(
            "No correlations found."
        )

        return

    df = pd.DataFrame(
        rows,
        columns=[
            "source",
            "target",
            "type",
            "value",
            "confidence",
            "created_at_ms",
        ]
    )

    # ---------------------------------------
    # 🔥 STATS
    # ---------------------------------------

    st.subheader(
        "📊 Correlation Statistics"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Correlations",
        len(df)
    )

    c2.metric(
        "Unique Evidence",
        len(
            set(df["source"]).union(
                set(df["target"])
            )
        )
    )

    c3.metric(
        "Correlation Types",
        df["type"].nunique()
    )

    # ---------------------------------------
    # 🔥 FILTERS
    # ---------------------------------------

    st.subheader(
        "🔎 Filters"
    )

    selected_types = st.multiselect(
        "Correlation Types",
        options=sorted(
            df["type"].unique()
        ),
        default=sorted(
            df["type"].unique()
        ),
    )

    if selected_types:

        df = df[
            df["type"].isin(
                selected_types
            )
        ]

    # ---------------------------------------
    # 🔥 EDGE LIMITING
    # ---------------------------------------

    max_edges = st.slider(
        "Max Edges",
        25,
        500,
        150,
    )

    df = df.head(max_edges)

    # ---------------------------------------
    # 🔥 EDGE WEIGHTING
    # ---------------------------------------

    EDGE_WEIGHTS = {

        "SSN_MATCH": 10,

        "CONTRACT_MATCH": 9,

        "EXPORT_REF_MATCH": 8,

        "IP_ENTITY_MATCH": 7,

        "PHONE_ENTITY_MATCH": 6,

        "EMAIL_ENTITY_MATCH": 3,
    }

    # ---------------------------------------
    # 🔥 ENTITY TYPE COLORS
    # ---------------------------------------

    ENTITY_COLORS = {

        "SSN_MATCH": "#ff3333",

        "CONTRACT_MATCH": "#ff9900",

        "EXPORT_REF_MATCH": "#cc66ff",

        "IP_ENTITY_MATCH": "#33ccff",

        "EMAIL_ENTITY_MATCH": "#66ff66",

        "PHONE_ENTITY_MATCH": "#ff66cc",
    }

    # ---------------------------------------
    # 🔥 BUILD GRAPH
    # ---------------------------------------

    G = nx.Graph()

    for _, row in df.iterrows():

        source = row["source"]

        correlation_type = row["type"]

        correlation_value = row["value"]

        # ---------------------------------------
        # 🔥 EVIDENCE NODE IMPORTANCE
        # ---------------------------------------

        source_degree = len(
            list(G.neighbors(source))
        ) if source in G else 1

        source_size = max(
            14,
            source_degree * 2
        )

        # ---------------------------------------
        # 🔥 EVIDENCE NODE
        # ---------------------------------------

        G.add_node(
            source,

            label=source[:10],

            title=source,

            color="#4da3ff",

            size=source_size,
        )

        # ---------------------------------------
        # 🔥 EDGE WEIGHT
        # ---------------------------------------

        weight = EDGE_WEIGHTS.get(
            correlation_type,
            1,
        )

        # ---------------------------------------
        # 🔥 ENTITY NODE
        # ---------------------------------------

        entity_node = (
            f"{correlation_type}: "
            f"{correlation_value}"
        )

        entity_degree = len(
            list(G.neighbors(entity_node))
        ) if entity_node in G else 1

        entity_size = max(
            18,
            entity_degree * 3
        )

        G.add_node(
            entity_node,

            label=(
                correlation_value[:12] + "..."
                if len(correlation_value) > 12
                else correlation_value
            ),

            title=entity_node,

            color=ENTITY_COLORS.get(
                correlation_type,
                "#ff6666"
            ),

            size=entity_size,
        )

        # ---------------------------------------
        # 🔥 EVIDENCE → ENTITY EDGE
        # ---------------------------------------

        G.add_edge(
            source,
            entity_node,

            title=(
                f"{correlation_type}\n"
                f"{correlation_value}"
            ),

            value=weight,

            width=max(
                1,
                weight * 0.35
            ),

            color=ENTITY_COLORS.get(
                correlation_type,
                "#66ff66"
            ),
        )

    # ---------------------------------------
    # 🔥 PYVIS NETWORK
    # ---------------------------------------

    net = Network(
        height="850px",
        width="100%",
        bgcolor="#111111",
        font_color="white",
    )

    net.from_nx(G)

    # ---------------------------------------
    # 🔥 GRAPH PHYSICS
    # ---------------------------------------

    net.force_atlas_2based(

        gravity=-180,

        central_gravity=0.004,

        spring_length=320,

        spring_strength=0.015,

        damping=0.95,
    )

    # ---------------------------------------
    # 🔥 HOVER-FIRST LABEL STRATEGY
    # ---------------------------------------

    net.set_options("""
    {
      "nodes": {

        "font": {
          "size": 10,
          "face": "arial",
          "strokeWidth": 0
        }

      },

      "edges": {

        "font": {
          "size": 0
        },

        "smooth": {
          "type": "dynamic"
        }

      },

      "interaction": {

        "hover": true,
        "tooltipDelay": 100

      },

      "physics": {

        "enabled": true

      }
    }
    """)

    # ---------------------------------------
    # 🔥 SAVE GRAPH
    # ---------------------------------------

    tmp_dir = tempfile.gettempdir()

    graph_path = os.path.join(
        tmp_dir,
        "relationship_graph.html"
    )

    net.save_graph(
        graph_path
    )

    with open(
        graph_path,
        "r",
        encoding="utf-8",
    ) as f:

        html = f.read()

    # ---------------------------------------
    # 🔥 GRAPH RENDER
    # ---------------------------------------

    st.subheader(
        "🔎 Investigation Pivot"
    )
    st.info(
        "Click a graph node, then paste "
        "its value into Pivot Analysis."
    )
    st.components.v1.html(
        html,
        height=900,
        scrolling=True,
    )

    # ---------------------------------------
    # 🔥 ANALYST PIVOT PANEL
    # ---------------------------------------

    st.markdown("---")

    st.subheader(
        "🧠 Pivot Analysis"
    )

    selected_node = st.text_input(
        "Entity Node",
        value="",
        placeholder="EMAIL_ENTITY_MATCH: john@company.com",
    )

    if selected_node:

        st.markdown(
            f"### 🔍 Selected: `{selected_node}`"
        )

        if ":" in selected_node:

            entity_type, entity_value = (
                selected_node.split(":", 1)
            )

            rows = con.execute(
                """
                SELECT

                    source_evidence_id,
                    created_at_ms,
                    correlation_type,
                    correlation_value

                FROM evidence_correlations

                WHERE correlation_value = ?

                ORDER BY created_at_ms ASC
                """,
                (
                    entity_value.strip(),
                )
            ).fetchall()

            linked_df = pd.DataFrame(
                rows,
                columns=[
                    "evidence_id",
                    "created_at_ms",
                    "correlation_type",
                    "correlation_value",
                ]
            )
            # ---------------------------------------
            # 🔥 LINKED EVIDENCE SUMMARY
            # ---------------------------------------

            st.metric(
                "Linked Evidence",
                len(linked_df)
            )

            if not linked_df.empty:

                first_seen = linked_df[
                    "created_at_ms"
                ].min()

                last_seen = linked_df[
                    "created_at_ms"
                ].max()

                c1, c2 = st.columns(2)

                c1.metric(
                    "First Seen",
                    first_seen
                )

                c2.metric(
                    "Last Seen",
                    last_seen
                )

                st.dataframe(
                    linked_df,
                    use_container_width=True,
                )

                # ---------------------------------------
                # 🔥 EVIDENCE DRILLDOWN
                # ---------------------------------------

                selected_evidence = st.selectbox(
                    "Select Evidence",
                    options=linked_df[
                        "evidence_id"
                    ].tolist()
                )
                # ---------------------------------------
                # 🔥 PIVOT TO EVIDENCE VIEWER
                # ---------------------------------------

                if st.button(
                        "🔍 Open In Evidence Viewer"
                ):
                    st.session_state[
                        "selected_evidence_id"
                    ] = selected_evidence

                    st.session_state[
                        "active_page"
                    ] = "Evidence Viewer"

                    st.rerun()
                if selected_evidence:

                    evidence = con.execute(
                        """
                        SELECT

                            evidence_id,
                            metadata_json,
                            created_at_ms

                        FROM evidence_records

                        WHERE evidence_id = ?
                        """,
                        (
                            selected_evidence,
                        )
                    ).fetchone()

                    if evidence:

                        st.markdown("---")

                        st.subheader(
                            "📄 Evidence Details"
                        )

                        st.code(
                            evidence["evidence_id"]
                        )

                        st.caption(
                            f"Created: "
                            f"{evidence['created_at_ms']}"
                        )

                        try:

                            import json

                            metadata = json.loads(
                                evidence["metadata_json"]
                                or "{}"
                            )

                            st.json(metadata)

                            # ---------------------------------------
                            # 🔥 LOAD ANALYSIS
                            # ---------------------------------------

                            analysis_rows = con.execute(
                                """
                                SELECT
                                    analysis_json,
                                    created_at_ms
                                FROM evidence_analysis
                                WHERE evidence_id = ?
                                ORDER BY created_at_ms DESC
                                """,
                                (
                                    selected_evidence,
                                )
                            ).fetchall()

                            if analysis_rows:

                                st.markdown("---")

                                st.subheader(
                                    "🧠 Analysis Intelligence"
                                )

                                import json

                                for row in analysis_rows:

                                    analysis = json.loads(
                                        row["analysis_json"]
                                    )

                                    # ---------------------------------------
                                    # 🔥 FLAGS
                                    # ---------------------------------------

                                    flags = analysis.get(
                                        "flags",
                                        []
                                    )

                                    if flags:
                                        st.markdown(
                                            f"### 🚨 Flags: "
                                            f"{', '.join(flags)}"
                                        )

                                    # ---------------------------------------
                                    # 🔥 ENTITIES
                                    # ---------------------------------------

                                    entities = analysis.get(
                                        "entities",
                                        {}
                                    )

                                    if entities:
                                        st.markdown(
                                            "### 🧬 Entities"
                                        )

                                        st.json(
                                            entities
                                        )

                                    # ---------------------------------------
                                    # 🔥 MATCHES
                                    # ---------------------------------------

                                    matches = analysis.get(
                                        "matches",
                                        []
                                    )

                                    if matches:
                                        st.markdown(
                                            "### 🔍 Matches"
                                        )

                                        st.json(
                                            matches
                                        )

                                    # ---------------------------------------
                                    # 🔥 RAW ANALYSIS
                                    # ---------------------------------------

                                    with st.expander(
                                            "Raw Analysis JSON"
                                    ):

                                        st.json(
                                            analysis
                                        )

                        except Exception:

                            st.text(
                                evidence["metadata_json"]
                            )
            st.metric(
                "Linked Evidence",
                len(linked_df)
            )

            if not linked_df.empty:

                first_seen = linked_df[
                    "created_at_ms"
                ].min()

                last_seen = linked_df[
                    "created_at_ms"
                ].max()

                c1, c2 = st.columns(2)

                c1.metric(
                    "First Seen",
                    first_seen
                )

                c2.metric(
                    "Last Seen",
                    last_seen
                )

                st.dataframe(
                    linked_df,
                    use_container_width=True,
                )

    # ---------------------------------------
    # 🔥 RAW TABLE
    # ---------------------------------------

    HIGH_VALUE_TYPES = [

        "SSN_MATCH",

        "CONTRACT_MATCH",

        "EXPORT_REF_MATCH",

        "IP_ENTITY_MATCH",

    ]

    show_low_value = st.checkbox(
        "Show low-value correlations",
        value=False,
    )

    if not show_low_value:

        df = df[
            df["type"].isin(
                HIGH_VALUE_TYPES
            )
        ]

    with st.expander(
        "📋 Raw Correlations"
    ):

        st.dataframe(
            df,
            use_container_width=True,
        )