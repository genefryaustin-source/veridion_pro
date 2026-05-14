import streamlit as st
from collections import Counter, defaultdict


NODE_COLORS = {
    "CASE": "#D32F2F",
    "ALERT": "#FF9800",
    "EVIDENCE": "#2196F3",
    "ENTITY": "#4CAF50",
    "UNKNOWN": "#777777",
}


def _node_color(node_type):
    return NODE_COLORS.get(
        str(node_type or "UNKNOWN").upper(),
        NODE_COLORS["UNKNOWN"],
    )


def _build_metrics(graph):
    nodes = graph.get("nodes", []) or []
    edges = graph.get("edges", []) or []

    node_types = Counter(
        n.get("type", "UNKNOWN")
        for n in nodes
    )

    edge_types = Counter(
        e.get("type", "UNKNOWN")
        for e in edges
    )

    degree = defaultdict(int)

    for e in edges:
        degree[e.get("source")] += 1
        degree[e.get("target")] += 1

    central_nodes = sorted(
        degree.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:5]

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_types": node_types,
        "edge_types": edge_types,
        "central_nodes": central_nodes,
    }


def _find_node(graph, node_id):
    for node in graph.get("nodes", []) or []:
        if node.get("id") == node_id:
            return node

    return None


def _render_metric_panel(graph):
    metrics = _build_metrics(graph)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Nodes",
            metrics["node_count"],
        )

    with col2:
        st.metric(
            "Edges",
            metrics["edge_count"],
        )

    with col3:
        density = 0

        if metrics["node_count"] > 1:
            density = round(
                metrics["edge_count"] / metrics["node_count"],
                2,
            )

        st.metric(
            "Graph Density",
            density,
        )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Node Types")

        for k, v in metrics["node_types"].items():
            st.write(f"{k}: {v}")

    with c2:
        st.markdown("#### Edge Types")

        for k, v in metrics["edge_types"].items():
            st.write(f"{k}: {v}")

    st.divider()

    st.markdown("#### Most Connected Nodes")

    for node_id, count in metrics["central_nodes"]:
        st.write(f"`{node_id}` — {count} connection(s)")


def _render_graph_tables(graph):
    nodes = graph.get("nodes", []) or []
    edges = graph.get("edges", []) or []

    st.markdown("### Graph Nodes")

    if nodes:
        st.dataframe(
            nodes,
            use_container_width=True,
        )
    else:
        st.info("No graph nodes available.")

    st.markdown("### Graph Edges")

    if edges:
        st.dataframe(
            edges,
            use_container_width=True,
        )
    else:
        st.info("No graph edges available.")


def _render_interactive_graph(graph):
    try:
        from streamlit_agraph import (
            agraph,
            Node,
            Edge,
            Config,
        )

    except Exception:
        st.warning(
            "Interactive graph requires streamlit-agraph. "
            "Install with: pip install streamlit-agraph"
        )

        _render_graph_tables(graph)
        return

    nodes = []

    for n in graph.get("nodes", []) or []:
        node_type = n.get("type", "UNKNOWN")

        nodes.append(
            Node(
                id=n.get("id"),
                label=str(n.get("label") or n.get("id")),
                size=25 if node_type == "CASE" else 18,
                color=_node_color(node_type),
            )
        )

    edges = []

    for e in graph.get("edges", []) or []:
        edges.append(
            Edge(
                source=e.get("source"),
                target=e.get("target"),
                label=e.get("type", ""),
            )
        )

    config = Config(
        width="100%",
        height=650,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=True,
    )

    selected = agraph(
        nodes=nodes,
        edges=edges,
        config=config,
    )

    if selected:
        st.session_state["selected_graph_node"] = selected


def _render_pivot_panel(graph):
    selected = st.session_state.get(
        "selected_graph_node"
    )

    st.markdown("### Graph Pivot Panel")

    if not selected:
        st.info(
            "Select a node in the graph to inspect pivots."
        )
        return

    node = _find_node(
        graph,
        selected,
    )

    if not node:
        st.warning(
            f"Selected node not found: {selected}"
        )
        return

    st.markdown(f"#### Selected: `{node.get('label')}`")

    st.json(node)

    connected_edges = []

    for e in graph.get("edges", []) or []:
        if (
            e.get("source") == selected
            or e.get("target") == selected
        ):
            connected_edges.append(e)

    st.markdown("#### Connected Relationships")

    if not connected_edges:
        st.info("No connected relationships found.")
        return

    for e in connected_edges:
        source_node = _find_node(
            graph,
            e.get("source"),
        )

        target_node = _find_node(
            graph,
            e.get("target"),
        )

        st.markdown(
            f"- **{source_node.get('label') if source_node else e.get('source')}** "
            f"→ `{e.get('type')}` → "
            f"**{target_node.get('label') if target_node else e.get('target')}**"
        )


def render_graph_tab(
    storage,
    case,
    graph,
):
    st.subheader("🕸️ Investigation Graph Viewer")

    graph = graph or {
        "nodes": [],
        "edges": [],
    }

    if not graph.get("nodes"):
        st.info("No graph data available for this case yet.")
        return

    _render_metric_panel(graph)

    view_mode = st.radio(
        "Graph View",
        [
            "Interactive Graph",
            "Tables",
        ],
        horizontal=True,
        key=f"graph_view_{case.get('id') or case.get('case_id')}",
    )

    st.divider()

    if view_mode == "Interactive Graph":
        _render_interactive_graph(graph)
    else:
        _render_graph_tables(graph)

    st.divider()

    _render_pivot_panel(graph)