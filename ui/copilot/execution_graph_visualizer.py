"""
ui/copilot/execution_graph_visualizer.py

Execution Graph Visualizer.

Realtime DAG cognition layer for:
- execution graphs
- distributed node execution
- rollback propagation
- approval gates
- worker ownership
- mission topology
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


GRAPH_STATUS_COLORS = {
    "PENDING": "⚪",
    "RUNNING": "🟡",
    "COMPLETED": "🟢",
    "FAILED": "🔴",
    "BLOCKED": "🟠",
    "APPROVAL_REQUIRED": "🟣",
}

NODE_STATUS_COLORS = {
    "PENDING": "⚪",
    "READY": "🔵",
    "QUEUED": "🟡",
    "RUNNING": "🟠",
    "COMPLETED": "🟢",
    "FAILED": "🔴",
    "BLOCKED": "🟤",
    "SKIPPED": "⚫",
    "APPROVAL_REQUIRED": "🟣",
}


def _fmt_ts(ms: Optional[int]) -> str:
    if not ms:
        return "-"

    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(int(ms) / 1000),
        )
    except Exception:
        return str(ms)


def _icon(status: str) -> str:
    status = str(status or "").upper()

    return (
        NODE_STATUS_COLORS.get(status)
        or GRAPH_STATUS_COLORS.get(status)
        or "⚪"
    )


def render_execution_graph_visualizer(
    storage: Any,
) -> None:

    st.markdown(
        "# 🧠 Execution Graph Visualizer"
    )

    st.caption(
        "Realtime DAG cognition for autonomous operations."
    )

    engine = getattr(
        storage,
        "execution_graph_engine",
        None,
    )

    if engine is None:
        st.error(
            "Execution graph engine unavailable."
        )
        return

    # ========================================================
    # FILTERS
    # ========================================================

    st.markdown(
        "## 🎛️ Graph Filters"
    )

    all_graphs = engine.list_graphs(
        limit=500,
    )

    graph_statuses = sorted(
        {
            str(g.get("status") or "UNKNOWN")
            for g in all_graphs
        }
    )

    tenants = sorted(
        {
            str(g.get("tenant_id") or "default")
            for g in all_graphs
        }
    )

    f1, f2, f3 = st.columns(3)

    with f1:

        selected_status = st.selectbox(
            "Graph Status",
            ["ALL"] + graph_statuses,
            key="graph_visualizer_status",
        )

    with f2:

        selected_tenant = st.selectbox(
            "Tenant",
            ["ALL"] + tenants,
            key="graph_visualizer_tenant",
        )

    with f3:

        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=False,
            key="graph_visualizer_refresh",
        )

    # ========================================================
    # FILTERED GRAPHS
    # ========================================================

    filtered_graphs = []

    for graph in all_graphs:

        if (
            selected_status != "ALL"
            and graph.get("status") != selected_status
        ):
            continue

        if (
            selected_tenant != "ALL"
            and graph.get("tenant_id") != selected_tenant
        ):
            continue

        filtered_graphs.append(graph)

    st.markdown("---")

    # ========================================================
    # GRAPH SUMMARY
    # ========================================================

    st.markdown(
        "## 🛰️ Graph Runtime Summary"
    )

    summary_rows = []

    for graph in filtered_graphs:

        summary_rows.append({
            "Graph": graph.get("graph_id"),
            "Name": graph.get("name"),
            "Tenant": graph.get("tenant_id"),
            "Status": (
                f"{_icon(graph.get('status'))} "
                f"{graph.get('status')}"
            ),
            "Updated": _fmt_ts(
                graph.get("updated_at_ms")
            ),
            "Created": _fmt_ts(
                graph.get("created_at_ms")
            ),
            "Completed": _fmt_ts(
                graph.get("completed_at_ms")
            ),
            "Error": graph.get("last_error"),
        })

    if summary_rows:

        st.dataframe(
            pd.DataFrame(summary_rows),
            use_container_width=True,
            height=300,
        )

    else:

        st.info(
            "No execution graphs found."
        )

    st.markdown("---")

    # ========================================================
    # GRAPH SELECTION
    # ========================================================

    graph_ids = [
        g.get("graph_id")
        for g in filtered_graphs
    ]

    if not graph_ids:
        return

    selected_graph_id = st.selectbox(
        "Select Execution Graph",
        graph_ids,
        key="execution_graph_selected",
    )

    if not selected_graph_id:
        return

    # ========================================================
    # SYNC GRAPH
    # ========================================================

    s1, s2, s3 = st.columns(3)

    with s1:

        if st.button(
            "🔄 Sync Graph",
            key="graph_sync_btn",
        ):

            result = engine.sync_queued_nodes(
                selected_graph_id
            )

            st.success(
                f"Graph sync complete ({result.get('updated')} updates)."
            )

    with s2:

        if st.button(
            "♻️ Recover Graph",
            key="graph_recover_btn",
        ):

            result = engine.recover_graph(
                selected_graph_id
            )

            st.success(
                f"Recovery status: {result.status}"
            )

    with s3:

        if st.button(
            "▶️ Run Graph",
            key="graph_run_btn",
        ):

            result = engine.run_graph(
                selected_graph_id
            )

            st.success(
                f"Execution status: {result.status}"
            )

    st.markdown("---")

    # ========================================================
    # SNAPSHOT
    # ========================================================

    snapshot = engine.graph_snapshot(
        selected_graph_id
    )

    graph = snapshot.get("graph") or {}
    nodes = snapshot.get("nodes") or []
    edges = snapshot.get("edges") or []

    # ========================================================
    # GRAPH HEADER
    # ========================================================

    st.markdown(
        "## 🌐 Execution Graph"
    )

    g1, g2, g3, g4 = st.columns(4)

    g1.metric(
        "Graph",
        graph.get("graph_id"),
    )

    g2.metric(
        "Status",
        f"{_icon(graph.get('status'))} "
        f"{graph.get('status')}",
    )

    g3.metric(
        "Tenant",
        graph.get("tenant_id"),
    )

    g4.metric(
        "Nodes",
        len(nodes),
    )

    # ========================================================
    # DAG TOPOLOGY
    # ========================================================

    st.markdown(
        "## 🕸️ DAG Topology"
    )

    edge_rows = []

    for edge in edges:

        from_node = edge.get(
            "from_node_id"
        )

        to_node = edge.get(
            "to_node_id"
        )

        from_status = next(
            (
                n.get("status")
                for n in nodes
                if n.get("node_id") == from_node
            ),
            "UNKNOWN",
        )

        to_status = next(
            (
                n.get("status")
                for n in nodes
                if n.get("node_id") == to_node
            ),
            "UNKNOWN",
        )

        edge_rows.append({
            "Execution Flow":
                f"{_icon(from_status)} "
                f"{from_node} → "
                f"{_icon(to_status)} "
                f"{to_node}",

            "From": from_node,
            "To": to_node,
            "From Status": from_status,
            "To Status": to_status,
        })

    if edge_rows:

        st.dataframe(
            pd.DataFrame(edge_rows),
            use_container_width=True,
            height=320,
        )

    else:

        st.info(
            "No DAG edges defined."
        )

    st.markdown("---")

    # ========================================================
    # NODE EXECUTION VIEW
    # ========================================================

    st.markdown(
        "## ⚙️ Node Execution View"
    )

    node_rows = []

    for node in nodes:

        node_rows.append({

            "Node":
                f"{_icon(node.get('status'))} "
                f"{node.get('name')}",

            "Node ID":
                node.get("node_id"),

            "Type":
                node.get("node_type"),

            "Action":
                node.get("action"),

            "Status":
                node.get("status"),

            "Worker":
                node.get("worker_id"),

            "Job":
                node.get("job_id"),

            "Attempts":
                f"{node.get('attempts')}/"
                f"{node.get('max_attempts')}",

            "Approval":
                bool(
                    node.get(
                        "requires_approval"
                    )
                ),

            "Updated":
                _fmt_ts(
                    node.get("updated_at_ms")
                ),

            "Completed":
                _fmt_ts(
                    node.get(
                        "completed_at_ms"
                    )
                ),

            "Error":
                node.get("last_error"),
        })

    if node_rows:

        st.dataframe(
            pd.DataFrame(node_rows),
            use_container_width=True,
            height=420,
        )

    else:

        st.info(
            "No graph nodes found."
        )

    st.markdown("---")

    # ========================================================
    # APPROVAL / BLOCKED VIEW
    # ========================================================

    st.markdown(
        "## 🛡️ Approval & Blocked Nodes"
    )

    approval_rows = []

    for node in nodes:

        status = str(
            node.get("status") or ""
        ).upper()

        if status not in {
            "BLOCKED",
            "APPROVAL_REQUIRED",
        }:
            continue

        approval_rows.append({

            "Node":
                f"{_icon(status)} "
                f"{node.get('name')}",

            "Type":
                node.get("node_type"),

            "Status":
                status,

            "Approval ID":
                node.get("approval_id"),

            "Worker":
                node.get("worker_id"),

            "Updated":
                _fmt_ts(
                    node.get("updated_at_ms")
                ),

            "Error":
                node.get("last_error"),
        })

    if approval_rows:

        st.dataframe(
            pd.DataFrame(approval_rows),
            use_container_width=True,
            height=260,
        )

    else:

        st.success(
            "No blocked or approval-required nodes."
        )

    st.markdown("---")

    # ========================================================
    # FAILURE / ROLLBACK VIEW
    # ========================================================

    st.markdown(
        "## 🔁 Rollback & Failure Propagation"
    )

    rollback_rows = []

    for node in nodes:

        status = str(
            node.get("status") or ""
        ).upper()

        node_type = str(
            node.get("node_type") or ""
        ).upper()

        if (
            status not in {
                "FAILED",
                "BLOCKED",
            }
            and node_type != "ROLLBACK"
        ):
            continue

        rollback_rows.append({

            "Node":
                f"{_icon(status)} "
                f"{node.get('name')}",

            "Node Type":
                node_type,

            "Status":
                status,

            "Worker":
                node.get("worker_id"),

            "Job":
                node.get("job_id"),

            "Attempts":
                f"{node.get('attempts')}/"
                f"{node.get('max_attempts')}",

            "Error":
                node.get("last_error"),
        })

    if rollback_rows:

        st.dataframe(
            pd.DataFrame(rollback_rows),
            use_container_width=True,
            height=260,
        )

    else:

        st.success(
            "No rollback/failure propagation visible."
        )

    st.markdown("---")

    # ========================================================
    # EXECUTION TIMELINE
    # ========================================================

    st.markdown(
        "## ⏱️ Execution Timeline"
    )

    timeline_rows = []

    sorted_nodes = sorted(
        nodes,
        key=lambda n: int(
            n.get("updated_at_ms") or 0
        ),
    )

    for idx, node in enumerate(
        sorted_nodes,
        start=1,
    ):

        timeline_rows.append({

            "Order": idx,

            "Node":
                f"{_icon(node.get('status'))} "
                f"{node.get('name')}",

            "Status":
                node.get("status"),

            "Worker":
                node.get("worker_id"),

            "Started":
                _fmt_ts(
                    node.get("created_at_ms")
                ),

            "Updated":
                _fmt_ts(
                    node.get("updated_at_ms")
                ),

            "Completed":
                _fmt_ts(
                    node.get(
                        "completed_at_ms"
                    )
                ),
        })

    if timeline_rows:

        st.dataframe(
            pd.DataFrame(timeline_rows),
            use_container_width=True,
            height=360,
        )

    st.markdown("---")

    # ========================================================
    # NODE INSPECTOR
    # ========================================================

    st.markdown(
        "## 🔬 Node Inspector"
    )

    node_ids = [
        n.get("node_id")
        for n in nodes
    ]

    selected_node_id = st.selectbox(
        "Select Node",
        node_ids,
        key="execution_graph_node_select",
    )

    selected_node = next(
        (
            n for n in nodes
            if n.get("node_id")
            == selected_node_id
        ),
        None,
    )

    if selected_node:

        ni1, ni2 = st.columns(2)

        with ni1:

            st.markdown(
                "### Node Metadata"
            )

            st.json(
                selected_node
            )

        with ni2:

            st.markdown(
                "### Node Payload"
            )

            payload = (
                selected_node.get(
                    "payload_json"
                )
                or "{}"
            )

            st.code(
                payload,
                language="json",
            )

    st.markdown("---")

    # ========================================================
    # LIVE GRAPH STREAM
    # ========================================================

    st.markdown(
        "## 📡 Live Graph Stream"
    )

    stream_rows = []

    recent_nodes = sorted(
        nodes,
        key=lambda n: int(
            n.get("updated_at_ms") or 0
        ),
        reverse=True,
    )[:100]

    for node in recent_nodes:

        stream_rows.append({

            "Time":
                _fmt_ts(
                    node.get(
                        "updated_at_ms"
                    )
                ),

            "Node":
                node.get("name"),

            "Status":
                f"{_icon(node.get('status'))} "
                f"{node.get('status')}",

            "Worker":
                node.get("worker_id"),

            "Job":
                node.get("job_id"),

            "Action":
                node.get("action"),

            "Error":
                node.get("last_error"),
        })

    if stream_rows:

        st.dataframe(
            pd.DataFrame(stream_rows),
            use_container_width=True,
            height=320,
        )

    if auto_refresh:

        time.sleep(5)

        st.rerun()