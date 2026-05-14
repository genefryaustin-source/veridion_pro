"""
ui/copilot/agent_operations_console.py

Realtime Multi-Agent Operations Console
for Veridion Pro / CUI GovCloud.

Provides:
- agent task orchestration visibility
- autonomous coordination telemetry
- task execution monitoring
- agent escalation visibility
- hunt/evidence/rollback operations
- realtime agent governance telemetry
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from core.agents.agent_coordinator import (
    AGENT_CONTAINMENT,
    AGENT_ESCALATION,
    AGENT_EVIDENCE,
    AGENT_GOVERNANCE,
    AGENT_HUNT,
    AGENT_ROLLBACK,
    AGENT_VERIFICATION,
    STATUS_BLOCKED,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_RUNNING,
)


SEVERITY_COLORS = {
    "LOW": "#22c55e",
    "MEDIUM": "#f59e0b",
    "HIGH": "#f97316",
    "CRITICAL": "#dc2626",
    "INFO": "#3b82f6",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_json(value: Any) -> Dict[str, Any]:

    if isinstance(value, dict):
        return value

    try:
        return json.loads(value or "{}")

    except Exception:
        return {}


# ---------------------------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------------------------

def render_agent_operations_console(
    storage: Any,
) -> None:

    st.markdown(
        """
        ## 🤖 Agent Operations Console

        Realtime multi-agent SOC orchestration visibility.
        """
    )

    coordinator = getattr(
        storage,
        "agent_coordinator",
        None,
    )

    if coordinator is None:

        st.error(
            "Agent coordinator unavailable."
        )

        return

    tasks = coordinator.list_tasks(
        limit=500
    )

    metrics = _build_metrics(
        tasks
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Total Tasks",
        metrics["total"],
    )

    c2.metric(
        "Running",
        metrics["running"],
    )

    c3.metric(
        "Completed",
        metrics["completed"],
    )

    c4.metric(
        "Failed",
        metrics["failed"],
    )

    c5.metric(
        "Blocked",
        metrics["blocked"],
    )

    st.divider()

    # -------------------------------------------------------------
    # FILTERS
    # -------------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        agent_filter = st.selectbox(
            "Agent",
            [
                "ALL",
                AGENT_GOVERNANCE,
                AGENT_CONTAINMENT,
                AGENT_VERIFICATION,
                AGENT_ROLLBACK,
                AGENT_ESCALATION,
                AGENT_EVIDENCE,
                AGENT_HUNT,
            ],
            key="agent_console_agent_filter",
        )

    with col2:

        status_filter = st.selectbox(
            "Status",
            [
                "ALL",
                STATUS_PENDING,
                STATUS_RUNNING,
                STATUS_COMPLETED,
                STATUS_FAILED,
                STATUS_BLOCKED,
            ],
            key="agent_console_status_filter",
        )

    with col3:

        search = st.text_input(
            "Search",
            key="agent_console_search",
        )

    filtered = _filter_tasks(
        tasks,
        agent_filter,
        status_filter,
        search,
    )

    # -------------------------------------------------------------
    # LIVE TASKS
    # -------------------------------------------------------------

    st.markdown(
        "### 🚀 Live Agent Tasks"
    )

    if not filtered:

        st.info(
            "No agent tasks."
        )

    else:

        for idx, task in enumerate(
            filtered[:100]
        ):

            _render_task_card(
                storage,
                task,
                idx,
            )

    st.divider()

    # -------------------------------------------------------------
    # TASK TABLE
    # -------------------------------------------------------------

    st.markdown(
        "### 📊 Structured Agent Tasks"
    )

    rows = [
        _task_row(t)
        for t in filtered
    ]

    if rows:

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            height=420,
        )

    st.divider()

    # -------------------------------------------------------------
    # MANUAL TASK EXECUTION
    # -------------------------------------------------------------

    st.markdown(
        "### ▶️ Manual Agent Operations"
    )

    with st.expander(
        "Create Manual Agent Task",
        expanded=False,
    ):

        manual_agent = st.selectbox(
            "Agent",
            [
                AGENT_GOVERNANCE,
                AGENT_CONTAINMENT,
                AGENT_VERIFICATION,
                AGENT_ROLLBACK,
                AGENT_ESCALATION,
                AGENT_EVIDENCE,
                AGENT_HUNT,
            ],
            key="manual_agent_select",
        )

        manual_task_type = st.text_input(
            "Task Type",
            key="manual_task_type",
        )

        manual_case_id = st.text_input(
            "Case ID",
            key="manual_case_id",
        )

        manual_payload = st.text_area(
            "Payload JSON",
            value="{}",
            key="manual_task_payload",
        )

        if st.button(
            "Create Task",
            key="manual_task_create_button",
        ):

            try:

                payload = _safe_json(
                    manual_payload
                )

                task = (
                    coordinator.create_task(
                        agent_name=manual_agent,
                        task_type=manual_task_type,
                        case_id=manual_case_id,
                        payload=payload,
                    )
                )

                st.success(
                    f"Task created: {task.task_id}"
                )

            except Exception as exc:

                st.error(
                    f"Task creation failed: {exc}"
                )


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def _build_metrics(
    tasks: List[Dict[str, Any]],
) -> Dict[str, int]:

    return {
        "total": len(tasks),

        "running": sum(
            1
            for t in tasks
            if t.get("status")
            == STATUS_RUNNING
        ),

        "completed": sum(
            1
            for t in tasks
            if t.get("status")
            == STATUS_COMPLETED
        ),

        "failed": sum(
            1
            for t in tasks
            if t.get("status")
            == STATUS_FAILED
        ),

        "blocked": sum(
            1
            for t in tasks
            if t.get("status")
            == STATUS_BLOCKED
        ),
    }


# ---------------------------------------------------------------------
# FILTER
# ---------------------------------------------------------------------

def _filter_tasks(
    tasks: List[Dict[str, Any]],
    agent_filter: str,
    status_filter: str,
    search: str,
) -> List[Dict[str, Any]]:

    rows = []

    for task in tasks:

        if (
            agent_filter != "ALL"
            and task.get("agent_name")
            != agent_filter
        ):
            continue

        if (
            status_filter != "ALL"
            and task.get("status")
            != status_filter
        ):
            continue

        if search:

            blob = json.dumps(
                task,
                default=str,
            ).lower()

            if (
                search.lower()
                not in blob
            ):
                continue

        rows.append(task)

    return rows


# ---------------------------------------------------------------------
# TASK CARD
# ---------------------------------------------------------------------

def _render_task_card(
    storage: Any,
    task: Dict[str, Any],
    idx: int,
) -> None:

    priority = str(
        task.get(
            "priority",
            "INFO",
        )
    ).upper()

    color = SEVERITY_COLORS.get(
        priority,
        "#64748b",
    )

    st.markdown(
        f"""
        <div style="
            border-left: 6px solid {color};
            background:#111827;
            padding:14px;
            border-radius:10px;
            margin-bottom:12px;
            color:white;
        ">
            <div style="
                font-size:18px;
                font-weight:900;
            ">
                🤖 {task.get("agent_name")}
            </div>

            <div style="margin-top:8px;">
                <b>Task:</b> {task.get("task_type")}<br>
                <b>Status:</b> {task.get("status")}<br>
                <b>Case:</b> {task.get("case_id")}<br>
                <b>Priority:</b> {priority}<br>
                <b>Task ID:</b> {task.get("task_id")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "▶️ Execute",
            key=f"agent_execute_{idx}",
        ):

            try:

                coordinator = getattr(
                    storage,
                    "agent_coordinator",
                    None,
                )

                result = (
                    coordinator.run_task(
                        task["task_id"]
                    )
                )

                st.success(
                    f"Execution complete: {result}"
                )

            except Exception as exc:

                st.error(str(exc))

    with c2:

        if st.button(
            "📜 Details",
            key=f"agent_details_{idx}",
        ):

            st.json(task)

    with c3:

        if st.button(
            "🚨 Escalate",
            key=f"agent_escalate_{idx}",
        ):

            st.warning(
                "Escalation workflow placeholder."
            )


# ---------------------------------------------------------------------
# ROW
# ---------------------------------------------------------------------

def _task_row(
    task: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "task_id": task.get(
            "task_id"
        ),

        "agent": task.get(
            "agent_name"
        ),

        "task_type": task.get(
            "task_type"
        ),

        "status": task.get(
            "status"
        ),

        "priority": task.get(
            "priority"
        ),

        "case_id": task.get(
            "case_id"
        ),

        "execution_id": task.get(
            "execution_id"
        ),

        "created_at_ms": task.get(
            "created_at_ms"
        ),
    }