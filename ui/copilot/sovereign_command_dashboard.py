"""
ui/copilot/sovereign_command_dashboard.py

Sovereign Command Dashboard

Unified visual sovereign operational command layer.

Renders:
- sovereign command state
- strategic projection
- governance posture
- continuity posture
- resilience posture
- sovereignty assurance posture
- strategic timeline
- explainability stream

Safe UI-only module.
Does not execute actions.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


STATE_COLORS = {
    "STABLE": "#16a34a",
    "VERIFIED": "#16a34a",
    "MONITORING": "#2563eb",
    "ELEVATED": "#f59e0b",
    "REVIEW": "#f59e0b",
    "HARDENING": "#f59e0b",
    "COORDINATED_RESPONSE": "#f97316",
    "MISSION_CONTINUITY": "#dc2626",
    "MISSION_SHIELD": "#dc2626",
    "SOVEREIGN_REVIEW": "#7c3aed",
    "SOVEREIGN_PROTECTION": "#7c3aed",
    "ESCALATED": "#dc2626",
    "NON_DEFENSIBLE": "#991b1b",
    "UNKNOWN": "#64748b",
}


def render_sovereign_command_dashboard(
    storage: Optional[Any] = None,
    *,
    copilot: Optional[Any] = None,
    tenant_id: Optional[str] = None,
    mission_id: Optional[str] = None,
    case_id: Optional[str] = None,
) -> None:
    st.markdown("## 🛡️ Sovereign Command Dashboard")
    st.caption(
        "Unified operational command, sovereignty assurance, resilience, continuity, and governance visibility."
    )

    assessment = _load_latest_assessment(
        storage=storage,
        copilot=copilot,
        tenant_id=tenant_id,
        mission_id=mission_id,
        case_id=case_id,
    )

    if not assessment:
        _render_empty_state()
        return

    data = _to_dict(assessment)

    _render_header(data)
    st.divider()

    _render_score_row(data)
    st.divider()

    left, right = st.columns([1.15, 1])

    with left:
        _render_projection_panel(data)
        _render_operational_stream(data)

    with right:
        _render_recommendation_panel(data)
        _render_explainability_panel(data)

    st.divider()
    _render_timeline(data)

    st.divider()
    _render_raw_details(data)


def _load_latest_assessment(
    *,
    storage: Optional[Any],
    copilot: Optional[Any],
    tenant_id: Optional[str],
    mission_id: Optional[str],
    case_id: Optional[str],
) -> Optional[Any]:
    if copilot is not None:
        try:
            if hasattr(copilot, "get_recent_assessments"):
                items = copilot.get_recent_assessments(limit=1)
                return items[0] if items else None

            if hasattr(copilot, "_assessments") and copilot._assessments:
                return copilot._assessments[-1]
        except Exception as exc:
            st.warning(f"Could not load copilot assessment: {exc}")

    if storage is not None:
        for method_name in (
            "get_latest_sovereign_command_assessment",
            "load_latest_sovereign_command_assessment",
            "get_latest_command_center_assessment",
        ):
            try:
                if hasattr(storage, method_name):
                    method = getattr(storage, method_name)
                    return method(
                        tenant_id=tenant_id,
                        mission_id=mission_id,
                        case_id=case_id,
                    )
            except TypeError:
                try:
                    return getattr(storage, method_name)()
                except Exception:
                    pass
            except Exception as exc:
                st.warning(f"Could not load assessment from storage: {exc}")

    return None


def _render_empty_state() -> None:
    st.info(
        "No sovereign command assessment is available yet. Once the command-center copilot emits an assessment, it will appear here."
    )

    st.markdown(
        """
        Expected upstream source:

        ```text
        core/runtime/sovereign_command_center_copilot.py
        ```
        """
    )


def _render_header(data: Dict[str, Any]) -> None:
    state = _get(data, "copilot_state", "UNKNOWN")
    projected = _get(data, "projected_state", "UNKNOWN")
    recommendation = _get(data, "recommendation", "MONITOR")
    severity = _get(data, "severity", "INFO")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _state_card("Command State", state)

    with c2:
        _state_card("Projected State", projected)

    with c3:
        _state_card("Recommendation", recommendation)

    with c4:
        _state_card("Severity", severity)


def _render_score_row(data: Dict[str, Any]) -> None:
    scores = [
        ("Operational Risk", _get_float(data, "operational_risk_score")),
        ("Governance Risk", _get_float(data, "governance_risk_score")),
        ("Sovereignty Risk", _get_float(data, "sovereignty_risk_score")),
        ("Resilience Risk", _get_float(data, "resilience_risk_score")),
        ("Continuity Risk", _get_float(data, "continuity_risk_score")),
        ("Survivability", _get_float(data, "survivability_score", 100.0)),
    ]

    cols = st.columns(len(scores))

    for col, (label, value) in zip(cols, scores):
        with col:
            st.metric(label, f"{value:.1f}")


def _render_projection_panel(data: Dict[str, Any]) -> None:
    st.markdown("### 🔭 Strategic Projection")

    projection = _to_dict(data.get("strategic_projection", {}))

    if not projection:
        st.info("No strategic projection available.")
        return

    state = _get(projection, "projection_state", "UNKNOWN")
    rationale = _get(projection, "rationale", "")

    _state_card("Projected Sovereign Future", state)

    st.write(rationale or "No projection rationale provided.")

    projection_scores = {
        "Operational": _get_float(projection, "operational_projection_score"),
        "Governance": _get_float(projection, "governance_projection_score"),
        "Sovereignty": _get_float(projection, "sovereignty_projection_score"),
        "Continuity": _get_float(projection, "continuity_projection_score"),
    }

    df = pd.DataFrame(
        [{"Dimension": key, "Score": value} for key, value in projection_scores.items()]
    )

    st.bar_chart(df.set_index("Dimension"))


def _render_recommendation_panel(data: Dict[str, Any]) -> None:
    st.markdown("### 🧭 Command Recommendation")

    recommendation = _get(data, "recommendation", "MONITOR")
    rationale = _get(data, "rationale", "")

    _state_card("Current Recommendation", recommendation)

    if rationale:
        st.write(rationale)

    controls = data.get("recommended_controls") or []
    actions = data.get("recommended_actions") or []

    if controls:
        st.markdown("#### Recommended Controls")
        for item in controls:
            st.markdown(f"- `{item}`")

    if actions:
        st.markdown("#### Recommended Actions")
        st.dataframe(pd.DataFrame(actions), use_container_width=True)


def _render_explainability_panel(data: Dict[str, Any]) -> None:
    st.markdown("### 🧠 Explainability")

    score = _get_float(data, "explainability_score")
    confidence = _get_float(data, "confidence")
    uncertainty = _get_float(data, "uncertainty_score")

    c1, c2, c3 = st.columns(3)
    c1.metric("Explainability", f"{score:.1f}")
    c2.metric("Confidence", f"{confidence:.2f}")
    c3.metric("Uncertainty", f"{uncertainty:.1f}")

    stream = _to_dict(data.get("operational_stream", {}))
    explainability = stream.get("explainability") or data.get("explainability") or []

    if explainability:
        st.markdown("#### Reasoning Stream")
        for item in explainability:
            st.markdown(f"- {item}")
    else:
        st.caption("No detailed explainability stream attached to this assessment.")


def _render_operational_stream(data: Dict[str, Any]) -> None:
    st.markdown("### 🌐 Operational Intelligence Stream")

    stream = _to_dict(data.get("operational_stream", {}))

    if not stream:
        st.info("No operational stream attached.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Signal Count", stream.get("signal_count", 0))
    c2.metric("Domains", len(stream.get("domains", []) or []))
    c3.metric("Engines", len(stream.get("engines", []) or []))

    domains = stream.get("domains") or []
    engines = stream.get("engines") or []

    if domains:
        st.markdown("#### Domains")
        st.write(", ".join(f"`{d}`" for d in domains))

    if engines:
        st.markdown("#### Source Engines")
        st.write(", ".join(f"`{e}`" for e in engines))


def _render_timeline(data: Dict[str, Any]) -> None:
    st.markdown("### 🕰️ Replayable Strategic Timeline")

    events = data.get("timeline_events") or []

    if not events:
        st.info("No timeline events available.")
        return

    rows = []

    for event in events:
        item = _to_dict(event)
        rows.append(
            {
                "Time": item.get("created_at_ms"),
                "Type": item.get("event_type"),
                "Source": item.get("source_engine"),
                "Severity": item.get("severity"),
                "Summary": item.get("summary"),
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_raw_details(data: Dict[str, Any]) -> None:
    with st.expander("Raw sovereign command assessment"):
        st.json(data)


def _state_card(label: str, value: str) -> None:
    color = STATE_COLORS.get(str(value).upper(), STATE_COLORS["UNKNOWN"])

    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 16px;
            padding: 14px 16px;
            background: rgba(15, 23, 42, 0.03);
            min-height: 88px;
        ">
            <div style="
                font-size: 0.78rem;
                color: #64748b;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: .04em;
            ">
                {label}
            </div>
            <div style="
                font-size: 1.05rem;
                font-weight: 700;
                color: {color};
                word-break: break-word;
            ">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _to_dict(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if is_dataclass(value):
        return asdict(value)

    if hasattr(value, "__dict__"):
        return dict(value.__dict__)

    return {}


def _get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    value = data.get(key, default)
    return default if value is None else value


def _get_float(data: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(data.get(key, default) or default)
    except Exception:
        return default