"""
ui/copilot/mission_planner_console.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from typing import Any

from core.ai.orchestration.mission_planner import (
    get_mission_planner,
    MISSION_PENDING,
    MISSION_APPROVAL_REQUIRED,
    MISSION_APPROVED,
    MISSION_RUNNING,
    MISSION_COMPLETED,
    MISSION_FAILED,
    MISSION_CANCELLED,
)


def render_mission_planner_console(
    storage: Any,
) -> None:

    st.markdown("## 🎯 Mission Planner")

    planner = get_mission_planner(storage)

    # -------------------------------------------------
    # CREATE MISSION
    # -------------------------------------------------

    with st.expander(
        "Create Mission",
        expanded=False,
    ):

        name = st.text_input(
            "Mission Name",
            key="mission_name",
        )

        description = st.text_area(
            "Description",
            key="mission_description",
        )

        objective = st.text_area(
            "Objective",
            key="mission_objective",
        )

        priority = st.selectbox(
            "Priority",
            [
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            ],
            key="mission_priority",
        )

        requires_approval = st.checkbox(
            "Requires Approval",
            value=False,
            key="mission_requires_approval",
        )

        if st.button(
            "Create Mission",
            key="create_mission_btn",
        ):

            mission = planner.create_mission(
                name=name,
                description=description,
                objective=objective,
                priority=priority,
                requires_approval=requires_approval,
            )

            st.success(
                f"Mission created: {mission.mission_id}"
            )

    st.markdown("---")

    # -------------------------------------------------
    # MISSION TABLE
    # -------------------------------------------------

    missions = planner.list_missions(
        limit=250,
    )

    rows = []

    for m in missions:

        rows.append({

            "Mission ID": m.get(
                "mission_id"
            ),

            "Name": m.get(
                "name"
            ),

            "Priority": m.get(
                "priority"
            ),

            "Status": m.get(
                "status"
            ),

            "Requires Approval": m.get(
                "requires_approval"
            ),

            "Created By": m.get(
                "created_by"
            ),

            "Created": m.get(
                "created_at_ms"
            ),

            "Updated": m.get(
                "updated_at_ms"
            ),
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        height=500,
    )

    st.markdown("---")

    # -------------------------------------------------
    # STATUS SUMMARY
    # -------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    statuses = [
        MISSION_PENDING,
        MISSION_RUNNING,
        MISSION_COMPLETED,
        MISSION_FAILED,
    ]

    counts = {
        s: len(
            [
                m for m in missions
                if m.get("status") == s
            ]
        )
        for s in statuses
    }

    col1.metric(
        "Pending",
        counts[MISSION_PENDING],
    )

    col2.metric(
        "Running",
        counts[MISSION_RUNNING],
    )

    col3.metric(
        "Completed",
        counts[MISSION_COMPLETED],
    )

    col4.metric(
        "Failed",
        counts[MISSION_FAILED],
    )