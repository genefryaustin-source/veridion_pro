"""
ui/copilot/runtime_supervisor_console.py

Autonomous Runtime Supervisor Console.

Purpose:
- autonomous runtime oversight UI
- runtime cognition dashboard
- recovery telemetry
- backpressure visibility
- watchdog visibility
- autonomous stabilization visibility
- runtime operational mode awareness
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def _fmt_ts(ms: Any) -> str:
    if not ms:
        return "-"

    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(int(ms) / 1000),
        )
    except Exception:
        return str(ms)


def _mode_icon(mode: str) -> str:
    mode = str(mode or "").upper()

    mapping = {
        "NORMAL": "🟢",
        "DEGRADED": "🟡",
        "CONTAINMENT": "🟠",
        "LOCKDOWN": "🔴",
        "RECOVERY": "🟣",
        "MAINTENANCE": "🔵",
    }

    return mapping.get(mode, "⚪")


def _severity_icon(level: str) -> str:
    level = str(level or "").upper()

    mapping = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🟠",
        "CRITICAL": "🔴",
        "INFO": "🔵",
        "WARNING": "🟠",
        "ERROR": "🔴",
    }

    return mapping.get(level, "⚪")


def render_runtime_supervisor_console(
    storage: Any,
) -> None:

    st.markdown(
        "# 🤖 Autonomous Runtime Supervisor"
    )

    st.caption(
        "Continuous autonomous runtime oversight and stabilization layer."
    )

    supervisor = getattr(
        storage,
        "autonomous_runtime_supervisor",
        None,
    )

    if supervisor is None:

        st.error(
            "Autonomous runtime supervisor unavailable."
        )

        return

    recovery_manager = getattr(
        storage,
        "runtime_recovery_manager",
        None,
    )

    health_manager = getattr(
        storage,
        "runtime_health_manager",
        None,
    )

    dependency_graph = getattr(
        storage,
        "runtime_dependency_graph",
        None,
    )

    # ========================================================
    # STATUS SNAPSHOT
    # ========================================================

    st.markdown(
        "## 🌐 Runtime Supervisor Status"
    )

    snapshot = supervisor.status_snapshot()

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Status",
        snapshot.get(
            "status",
            "UNKNOWN",
        ),
    )

    runtime_mode = snapshot.get(
        "runtime_mode",
        "UNKNOWN",
    )

    c2.metric(
        "Runtime Mode",
        f"{_mode_icon(runtime_mode)} {runtime_mode}",
    )

    c3.metric(
        "Cycles",
        snapshot.get(
            "cycle_count",
            0,
        ),
    )

    c4.metric(
        "Recoveries",
        snapshot.get(
            "recovery_count",
            0,
        ),
    )

    c5.metric(
        "Errors",
        snapshot.get(
            "error_count",
            0,
        ),
    )

    c6.metric(
        "Last Cycle",
        _fmt_ts(
            snapshot.get(
                "last_cycle_ms"
            )
        ),
    )

    st.markdown("---")

    # ========================================================
    # RUNTIME HEALTH
    # ========================================================

    st.markdown(
        "## ❤️ Runtime Health"
    )

    if health_manager is not None:

        try:

            health = health_manager.evaluate()

            health_dict = (
                health.to_dict()
                if hasattr(
                    health,
                    "to_dict",
                )
                else {}
            )

            h1, h2, h3 = st.columns(3)

            h1.metric(
                "Health",
                health_dict.get(
                    "health",
                    "UNKNOWN",
                ),
            )

            h2.metric(
                "Score",
                round(
                    health_dict.get(
                        "score",
                        0.0,
                    ),
                    2,
                ),
            )

            risk = health_dict.get(
                "risk",
                "UNKNOWN",
            )

            h3.metric(
                "Risk",
                f"{_severity_icon(risk)} {risk}",
            )

            findings = (
                health_dict.get(
                    "findings",
                    [],
                )
            )

            if findings:

                st.markdown(
                    "### ⚠️ Runtime Findings"
                )

                rows = []

                for finding in findings:

                    rows.append({

                        "Type":
                            finding.get(
                                "type",
                                "UNKNOWN",
                            ),

                        "Service":
                            (
                                finding.get(
                                    "service"
                                )
                                or finding.get(
                                    "service_name"
                                )
                                or "-"
                            ),

                        "Severity":
                            finding.get(
                                "severity",
                                "UNKNOWN",
                            ),

                        "Message":
                            finding.get(
                                "message",
                                "-"
                            ),
                    })

                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    height=260,
                )

        except Exception as e:

            st.error(
                f"Health evaluation failed: {e}"
            )

    st.markdown("---")

    # ========================================================
    # DEPENDENCY TOPOLOGY
    # ========================================================

    st.markdown(
        "## 🕸️ Runtime Dependency Topology"
    )

    if dependency_graph is not None:

        try:

            validation = (
                dependency_graph.validate()
            )

            d1, d2, d3, d4 = st.columns(4)

            d1.metric(
                "Nodes",
                validation.get(
                    "node_count",
                    0,
                ),
            )

            d2.metric(
                "Edges",
                validation.get(
                    "edge_count",
                    0,
                ),
            )

            d3.metric(
                "Cycles",
                len(
                    validation.get(
                        "cycles",
                        [],
                    )
                ),
            )

            d4.metric(
                "Missing",
                len(
                    validation.get(
                        "missing_dependencies",
                        [],
                    )
                ),
            )

            cycles = validation.get(
                "cycles",
                [],
            )

            if cycles:

                st.markdown(
                    "### 🔥 Dependency Cycles"
                )

                cycle_rows = []

                for cycle in cycles:

                    cycle_rows.append({

                        "Cycle":
                            " → ".join(cycle)
                    })

                st.dataframe(
                    pd.DataFrame(cycle_rows),
                    use_container_width=True,
                    height=180,
                )

        except Exception as e:

            st.error(
                f"Dependency graph validation failed: {e}"
            )

    st.markdown("---")

    # ========================================================
    # RECOVERY OPERATIONS
    # ========================================================

    st.markdown(
        "## 🔄 Autonomous Recovery"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "Run Supervisor Cycle",
            use_container_width=True,
            key="run_supervisor_cycle",
        ):

            try:

                result = supervisor.run_cycle()

                st.success(
                    "Supervisor cycle completed."
                )

                st.json(
                    result.to_dict()
                    if hasattr(
                        result,
                        "to_dict",
                    )
                    else result
                )

            except Exception as e:

                st.error(
                    f"Supervisor cycle failed: {e}"
                )

    with col2:

        if st.button(
            "Force Recovery",
            use_container_width=True,
            key="force_runtime_recovery",
        ):

            try:

                result = supervisor.run_cycle(
                    force_recovery=True,
                )

                st.success(
                    "Forced recovery completed."
                )

                st.json(
                    result.to_dict()
                    if hasattr(
                        result,
                        "to_dict",
                    )
                    else result
                )

            except Exception as e:

                st.error(
                    f"Recovery failed: {e}"
                )

    with col3:

        if st.button(
            "Pause Supervisor",
            use_container_width=True,
            key="pause_runtime_supervisor",
        ):

            try:

                supervisor.pause()

                st.warning(
                    "Supervisor paused."
                )

            except Exception as e:

                st.error(
                    f"Pause failed: {e}"
                )

    st.markdown("---")

    # ========================================================
    # SUPERVISOR EVENTS
    # ========================================================

    st.markdown(
        "## 📜 Supervisor Events"
    )

    try:

        events = supervisor.list_events(
            limit=200,
        )

        if events:

            rows = []

            for event in events:

                rows.append({

                    "Time":
                        _fmt_ts(
                            event.get(
                                "created_at_ms"
                            )
                        ),

                    "Severity":
                        (
                            f"{_severity_icon(event.get('severity'))} "
                            f"{event.get('severity')}"
                        ),

                    "Type":
                        event.get(
                            "event_type",
                            "UNKNOWN",
                        ),

                    "Runtime Mode":
                        (
                            f"{_mode_icon(event.get('runtime_mode'))} "
                            f"{event.get('runtime_mode')}"
                        ),

                    "Message":
                        event.get(
                            "message",
                            "-",
                        ),
                })

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                height=420,
            )

        else:

            st.info(
                "No supervisor events available."
            )

    except Exception as e:

        st.error(
            f"Failed to load supervisor events: {e}"
        )

    st.markdown("---")

    # ========================================================
    # SUPERVISOR CYCLES
    # ========================================================

    st.markdown(
        "## 🔁 Supervisor Cycles"
    )

    try:

        cycles = supervisor.list_cycles(
            limit=100,
        )

        if cycles:

            cycle_rows = []

            for cycle in cycles:

                cycle_rows.append({

                    "Cycle":
                        cycle.get(
                            "cycle_id",
                            "-"
                        ),

                    "Time":
                        _fmt_ts(
                            cycle.get(
                                "created_at_ms"
                            )
                        ),

                    "Runtime Mode":
                        (
                            f"{_mode_icon(cycle.get('runtime_mode'))} "
                            f"{cycle.get('runtime_mode')}"
                        ),

                    "Risk":
                        (
                            f"{_severity_icon(cycle.get('risk'))} "
                            f"{cycle.get('risk')}"
                        ),

                    "Health":
                        round(
                            cycle.get(
                                "health_score",
                                0.0,
                            ),
                            2,
                        ),

                    "Recovery":
                        cycle.get(
                            "recovery_triggered",
                            False,
                        ),

                    "Backpressure":
                        cycle.get(
                            "backpressure_triggered",
                            False,
                        ),

                    "Watchdog":
                        cycle.get(
                            "watchdog_triggered",
                            False,
                        ),
                })

            st.dataframe(
                pd.DataFrame(cycle_rows),
                use_container_width=True,
                height=420,
            )

        else:

            st.info(
                "No supervisor cycles available."
            )

    except Exception as e:

        st.error(
            f"Failed to load supervisor cycles: {e}"
        )

    st.markdown("---")

    # ========================================================
    # RECOVERY MANAGER
    # ========================================================

    st.markdown(
        "## 🛠️ Recovery Plans"
    )

    if recovery_manager is not None:

        try:

            plans = recovery_manager.list_plans(
                limit=100,
            )

            if plans:

                plan_rows = []

                for plan in plans:

                    plan_rows.append({

                        "Plan":
                            plan.get(
                                "plan_id",
                                "-"
                            ),

                        "Risk":
                            (
                                f"{_severity_icon(plan.get('risk'))} "
                                f"{plan.get('risk')}"
                            ),

                        "Status":
                            plan.get(
                                "status",
                                "-"
                            ),

                        "Actions":
                            len(
                                plan.get(
                                    "actions",
                                    [],
                                )
                            ),

                        "Reason":
                            plan.get(
                                "reason",
                                "-"
                            ),

                        "Created":
                            _fmt_ts(
                                plan.get(
                                    "created_at_ms"
                                )
                            ),
                    })

                st.dataframe(
                    pd.DataFrame(plan_rows),
                    use_container_width=True,
                    height=320,
                )

            else:

                st.info(
                    "No recovery plans available."
                )

        except Exception as e:

            st.error(
                f"Recovery plan loading failed: {e}"
            )

    st.markdown("---")

    # ========================================================
    # CONTROL OPERATIONS
    # ========================================================

    st.markdown(
        "## 🎛️ Supervisor Controls"
    )

    ctl1, ctl2, ctl3 = st.columns(3)

    with ctl1:

        if st.button(
            "Resume Supervisor",
            use_container_width=True,
            key="resume_runtime_supervisor",
        ):

            try:

                supervisor.resume()

                st.success(
                    "Supervisor resumed."
                )

            except Exception as e:

                st.error(
                    f"Resume failed: {e}"
                )

    with ctl2:

        if st.button(
            "Stop Supervisor",
            use_container_width=True,
            key="stop_runtime_supervisor",
        ):

            try:

                supervisor.stop()

                st.warning(
                    "Supervisor stopped."
                )

            except Exception as e:

                st.error(
                    f"Stop failed: {e}"
                )

    with ctl3:

        if st.button(
            "Start Supervisor",
            use_container_width=True,
            key="start_runtime_supervisor",
        ):

            try:

                supervisor.start()

                st.success(
                    "Supervisor started."
                )

            except Exception as e:

                st.error(
                    f"Start failed: {e}"
                )

    st.markdown("---")

    # ========================================================
    # AUTO REFRESH
    # ========================================================

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="runtime_supervisor_auto_refresh",
    )

    if auto_refresh:

        time.sleep(5)

        st.rerun()