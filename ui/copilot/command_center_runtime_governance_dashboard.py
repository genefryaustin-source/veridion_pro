"""
ui/copilot/command_center_runtime_governance_dashboard.py

Command Center Runtime Governance Dashboard

Streamlit visualization layer for sovereign runtime governance cognition.

Reads from:
- runtime governance heatmap
- sovereign operational state graph
- strategic operational prediction engine
- infrastructure resilience correlation engine
- runtime telemetry fusion engine
- sovereign autonomy pressure engine
- execution verification mesh
- runtime connector health engine

IMPORTANT:
This UI does NOT own runtime state.
It only renders snapshots / recent assessments from injected engines.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


def render_command_center_runtime_governance_dashboard(
    *,
    heatmap_engine: Optional[Any] = None,
    operational_state_graph: Optional[Any] = None,
    prediction_engine: Optional[Any] = None,
    resilience_engine: Optional[Any] = None,
    telemetry_fusion_engine: Optional[Any] = None,
    autonomy_pressure_engine: Optional[Any] = None,
    verification_mesh: Optional[Any] = None,
    connector_health_engine: Optional[Any] = None,
    max_rows: int = 25,
) -> None:
    """
    Render sovereign runtime governance dashboard.
    """

    st.subheader("🧠 Sovereign Runtime Governance Command Center")

    st.caption(
        "Unified view of runtime governance pressure, survivability, "
        "prediction, topology, verification, connector health, and telemetry."
    )

    snapshots = {
        "Heatmap": _safe_snapshot(heatmap_engine),
        "Operational Graph": _safe_snapshot(operational_state_graph, method="graph_snapshot"),
        "Prediction": _safe_snapshot(prediction_engine),
        "Resilience": _safe_snapshot(resilience_engine),
        "Telemetry Fusion": _safe_snapshot(telemetry_fusion_engine),
        "Autonomy Pressure": _safe_snapshot(autonomy_pressure_engine),
        "Verification Mesh": _safe_snapshot(verification_mesh),
        "Connector Health": _safe_snapshot(connector_health_engine),
    }

    _render_snapshot_overview(snapshots)

    tabs = st.tabs(
        [
            "🔥 Heatmap",
            "🕸️ Topology",
            "🔮 Predictions",
            "🛡️ Resilience",
            "📡 Telemetry",
            "⚖️ Governance Pressure",
            "✅ Verification",
            "🔌 Connectors",
        ]
    )

    with tabs[0]:
        _render_heatmap_tab(heatmap_engine, max_rows=max_rows)

    with tabs[1]:
        _render_topology_tab(operational_state_graph, max_rows=max_rows)

    with tabs[2]:
        _render_recent_assessment_tab(
            title="Strategic Operational Predictions",
            engine=prediction_engine,
            empty="No strategic prediction assessments available.",
            max_rows=max_rows,
        )

    with tabs[3]:
        _render_recent_assessment_tab(
            title="Infrastructure Resilience",
            engine=resilience_engine,
            empty="No resilience assessments available.",
            max_rows=max_rows,
        )

    with tabs[4]:
        _render_recent_assessment_tab(
            title="Runtime Telemetry Fusion",
            engine=telemetry_fusion_engine,
            empty="No telemetry fusion assessments available.",
            max_rows=max_rows,
        )

    with tabs[5]:
        _render_recent_assessment_tab(
            title="Sovereign Autonomy Pressure",
            engine=autonomy_pressure_engine,
            empty="No autonomy pressure assessments available.",
            max_rows=max_rows,
        )

    with tabs[6]:
        _render_recent_assessment_tab(
            title="Execution Verification Mesh",
            engine=verification_mesh,
            empty="No verification assessments available.",
            max_rows=max_rows,
        )

    with tabs[7]:
        _render_recent_assessment_tab(
            title="Runtime Connector Health",
            engine=connector_health_engine,
            empty="No connector health assessments available.",
            max_rows=max_rows,
        )


def _render_snapshot_overview(
    snapshots: Dict[str, Dict[str, Any]],
) -> None:
    st.markdown("### Runtime Cognition Overview")

    cols = st.columns(4)

    items = list(snapshots.items())

    for idx, (name, snapshot) in enumerate(items):
        with cols[idx % 4]:
            if not snapshot:
                st.metric(name, "Offline")
                continue

            status = (
                snapshot.get("last_overall_heat_level")
                or snapshot.get("last_runtime_state")
                or snapshot.get("last_prediction_state")
                or snapshot.get("last_resilience_state")
                or snapshot.get("last_pressure_status")
                or snapshot.get("last_verification_status")
                or snapshot.get("last_health_status")
                or "Online"
            )

            score = (
                snapshot.get("last_overall_heat_score")
                or snapshot.get("last_systemic_runtime_pressure_score")
                or snapshot.get("last_prediction_risk_score")
                or snapshot.get("last_collapse_risk_score")
                or snapshot.get("last_safety_score")
                or snapshot.get("last_confidence_score")
                or snapshot.get("last_health_score")
            )

            st.metric(
                name,
                status,
                None if score is None else f"{float(score):.1f}",
            )


def _render_heatmap_tab(
    heatmap_engine: Optional[Any],
    *,
    max_rows: int,
) -> None:
    st.markdown("### Runtime Governance Heatmap")

    assessments = _safe_recent(heatmap_engine, limit=1)

    if not assessments:
        st.info("No heatmap assessments available yet.")
        return

    assessment = _to_dict(assessments[0])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Overall Heat", assessment.get("overall_heat_level", "UNKNOWN"))
    c2.metric("Heat Score", _fmt_score(assessment.get("overall_heat_score")))
    c3.metric("Collapse Risk", _fmt_score(assessment.get("collapse_risk_score")))
    c4.metric("Hotspots", len(assessment.get("hotspots") or []))

    st.markdown("#### Heat Scores")

    score_df = pd.DataFrame(
        [
            {
                "Governance": assessment.get("governance_heat_score", 0),
                "Autonomy": assessment.get("autonomy_heat_score", 0),
                "Execution": assessment.get("execution_heat_score", 0),
                "Survivability": assessment.get("survivability_heat_score", 0),
                "Telemetry": assessment.get("telemetry_heat_score", 0),
                "Collapse Risk": assessment.get("collapse_risk_score", 0),
            }
        ]
    )

    st.bar_chart(score_df.T)

    hotspots = assessment.get("hotspots") or []
    cells = assessment.get("cells") or []

    st.markdown("#### Critical / High Hotspots")

    if hotspots:
        st.dataframe(
            _records_to_df(
                hotspots,
                fields=[
                    "label",
                    "domain",
                    "heat_level",
                    "heat_score",
                    "risk_score",
                    "pressure_score",
                    "tenant_id",
                    "connector_name",
                    "recommended_action",
                ],
            ).head(max_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("No high or critical hotspots detected.")

    with st.expander("All Heatmap Cells", expanded=False):
        if cells:
            st.dataframe(
                _records_to_df(
                    cells,
                    fields=[
                        "label",
                        "domain",
                        "heat_level",
                        "heat_score",
                        "risk_score",
                        "pressure_score",
                        "tenant_id",
                        "node_name",
                        "connector_name",
                        "primary_signal_type",
                    ],
                ).head(max_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No heatmap cells available.")

    _render_recommended_actions(assessment)


def _render_topology_tab(
    operational_state_graph: Optional[Any],
    *,
    max_rows: int,
) -> None:
    st.markdown("### Sovereign Operational Topology")

    snapshot = _safe_snapshot(operational_state_graph, method="graph_snapshot")

    if not snapshot:
        st.info("Operational state graph is not available.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nodes", snapshot.get("total_nodes", 0))
    c2.metric("Edges", snapshot.get("total_edges", 0))
    c3.metric("Transitions", snapshot.get("total_transitions", 0))
    c4.metric(
        "Degraded / Unstable / Failed",
        f"{snapshot.get('degraded_nodes', 0)} / "
        f"{snapshot.get('unstable_nodes', 0)} / "
        f"{snapshot.get('failed_nodes', 0)}",
    )

    degraded = []

    if operational_state_graph is not None and hasattr(
        operational_state_graph,
        "degraded_nodes",
    ):
        try:
            degraded = operational_state_graph.degraded_nodes()
        except Exception as exc:
            st.warning(f"Could not load degraded nodes: {exc}")

    st.markdown("#### Degraded Operational Nodes")

    if degraded:
        st.dataframe(
            _records_to_df(
                [_to_dict(item) for item in degraded],
                fields=[
                    "node_name",
                    "node_type",
                    "state",
                    "domain",
                    "tenant_id",
                    "survivability_score",
                    "resilience_score",
                    "prediction_risk_score",
                    "updated_at_ms",
                ],
            ).head(max_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("No degraded operational graph nodes detected.")


def _render_recent_assessment_tab(
    *,
    title: str,
    engine: Optional[Any],
    empty: str,
    max_rows: int,
) -> None:
    st.markdown(f"### {title}")

    assessments = _safe_recent(engine, limit=max_rows)

    if not assessments:
        st.info(empty)
        return

    records = [_flatten_assessment(_to_dict(item)) for item in assessments]

    df = pd.DataFrame(records)

    preferred = [
        "created_at_ms",
        "status",
        "state",
        "recommendation",
        "severity",
        "confidence",
        "tenant_id",
        "case_id",
        "correlation_id",
        "score",
        "rationale",
    ]

    columns = [col for col in preferred if col in df.columns] + [
        col for col in df.columns if col not in preferred
    ]

    st.dataframe(
        df[columns].head(max_rows),
        use_container_width=True,
        hide_index=True,
    )

    latest = _to_dict(assessments[0])

    _render_recommended_actions(latest)

    with st.expander("Latest Raw Assessment", expanded=False):
        st.json(latest)


def _render_recommended_actions(
    assessment: Dict[str, Any],
) -> None:
    actions = assessment.get("recommended_actions") or []

    st.markdown("#### Recommended Actions")

    if not actions:
        st.info("No recommended actions.")
        return

    for action in actions[:10]:
        st.write(f"• `{action.get('action', 'unknown')}`")


def _safe_snapshot(
    engine: Optional[Any],
    *,
    method: str = "snapshot",
) -> Dict[str, Any]:
    if engine is None:
        return {}

    if not hasattr(engine, method):
        return {}

    try:
        return _to_dict(getattr(engine, method)())
    except Exception:
        return {}


def _safe_recent(
    engine: Optional[Any],
    *,
    limit: int,
) -> List[Any]:
    if engine is None:
        return []

    if not hasattr(engine, "get_recent_assessments"):
        return []

    try:
        return list(engine.get_recent_assessments(limit=limit) or [])
    except Exception:
        return []


def _to_dict(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return dict(value)

    if is_dataclass(value):
        return asdict(value)

    if hasattr(value, "__dict__"):
        return dict(value.__dict__)

    return {"value": value}


def _records_to_df(
    records: List[Any],
    *,
    fields: List[str],
) -> pd.DataFrame:
    rows = []

    for record in records:
        data = _to_dict(record)
        rows.append({field: data.get(field) for field in fields})

    return pd.DataFrame(rows)


def _flatten_assessment(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    status = (
        data.get("status")
        or data.get("runtime_state")
        or data.get("prediction_state")
        or data.get("resilience_state")
        or data.get("pressure_status")
        or data.get("verification_status")
        or data.get("health_status")
        or data.get("overall_heat_level")
        or "UNKNOWN"
    )

    score = (
        data.get("overall_heat_score")
        or data.get("systemic_runtime_pressure_score")
        or data.get("systemic_prediction_risk_score")
        or data.get("systemic_collapse_risk_score")
        or data.get("safety_score")
        or data.get("verification_confidence_score")
        or data.get("health_score")
        or data.get("connector_pressure_score")
    )

    return {
        "created_at_ms": data.get("created_at_ms"),
        "status": status,
        "state": status,
        "recommendation": data.get("recommendation"),
        "severity": data.get("severity"),
        "confidence": data.get("confidence"),
        "tenant_id": data.get("tenant_id"),
        "case_id": data.get("case_id"),
        "correlation_id": data.get("correlation_id"),
        "score": score,
        "rationale": data.get("rationale"),
    }


def _fmt_score(value: Any) -> str:
    try:
        return f"{float(value):.1f}"
    except Exception:
        return "0.0"