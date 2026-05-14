import sqlite3
import pandas as pd
import streamlit as st


def render_timeline_page(storage):

    st.title(
        "🕒 Timeline Intelligence"
    )

    con = sqlite3.connect(
        storage.ledger.db_path
    )

    con.row_factory = sqlite3.Row

    # ---------------------------------------
    # 🔥 LOAD TIMELINE EVENTS
    # ---------------------------------------

    rows = con.execute(
        """
        SELECT

            created_at_ms,

            source_evidence_id,

            correlation_type,

            correlation_value,

            confidence

        FROM evidence_correlations

        ORDER BY created_at_ms ASC
        """
    ).fetchall()

    if not rows:

        st.warning(
            "No timeline data found."
        )

        return

    df = pd.DataFrame(
        rows,
        columns=[
            "created_at_ms",
            "evidence_id",
            "correlation_type",
            "correlation_value",
            "confidence",
        ]
    )

    # ---------------------------------------
    # 🔥 TIMESTAMP CONVERSION
    # ---------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["created_at_ms"],
        unit="ms",
    )

    # ---------------------------------------
    # 🔥 FILTERS
    # ---------------------------------------

    st.subheader(
        "🔎 Timeline Filters"
    )

    selected_types = st.multiselect(
        "Correlation Types",
        options=sorted(
            df["correlation_type"].unique()
        ),
        default=sorted(
            df["correlation_type"].unique()
        ),
    )

    if selected_types:

        df = df[
            df["correlation_type"].isin(
                selected_types
            )
        ]

    # ---------------------------------------
    # 🔥 TIMELINE TABLE
    # ---------------------------------------

    st.subheader(
        "📜 Relationship Timeline"
    )

    display_df = df[[
        "timestamp",
        "correlation_type",
        "correlation_value",
        "evidence_id",
        "confidence",
    ]]

    st.dataframe(
        display_df,
        use_container_width=True,
    )

    # ---------------------------------------
    # 🔥 ENTITY FREQUENCY
    # ---------------------------------------

    st.subheader(
        "📊 Entity Frequency"
    )

    freq_df = (
        df.groupby(
            [
                "correlation_type",
                "correlation_value"
            ]
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False
        )
    )

    st.dataframe(
        freq_df,
        use_container_width=True,
    )

    con.close()