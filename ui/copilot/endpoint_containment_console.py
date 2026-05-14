"""
ui/copilot/endpoint_containment_console.py

Realtime endpoint containment operations console.

Provides:
- live endpoint isolation visibility
- CrowdStrike + SentinelOne telemetry
- containment status monitoring
- verification visibility
- blast radius indicators
- rollback-aware release actions
- autonomous containment audit visibility
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


SEVERITY_COLORS = {
    "LOW": "#4caf50",
    "MEDIUM": "#ff9800",
    "HIGH": "#ff5722",
    "CRITICAL": "#e53935",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


# ---------------------------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------------------------

def render_endpoint_containment_console(
    storage: Any,
) -> None:

    st.markdown(
        """
        ## 🛡️ Endpoint Containment Console
        Realtime endpoint isolation + containment operations.
        """
    )

    ledger = getattr(storage, "ledger", None)

    connector_registry = getattr(
        storage,
        "connector_registry",
        None,
    )

    # -------------------------------------------------------------
    # TOP METRICS
    # -------------------------------------------------------------

    metrics = _build_metrics(
        ledger,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Contained Hosts",
        metrics["contained_hosts"],
    )

    c2.metric(
        "Pending Verification",
        metrics["pending_verifications"],
    )

    c3.metric(
        "Rollback Required",
        metrics["rollback_required"],
    )

    c4.metric(
        "Failed Containment",
        metrics["failed_containment"],
    )

    c5.metric(
        "Blast Radius Alerts",
        metrics["blast_radius_alerts"],
    )

    st.divider()

    # -------------------------------------------------------------
    # CONNECTOR STATUS
    # -------------------------------------------------------------

    st.markdown(
        "### 🔌 Containment Connectors"
    )

    connector_rows = _build_connector_rows(
        connector_registry,
    )

    if connector_rows:

        st.dataframe(
            pd.DataFrame(connector_rows),
            use_container_width=True,
            height=220,
        )

    else:

        st.info(
            "No containment connectors registered."
        )

    st.divider()

    # -------------------------------------------------------------
    # ACTIVE CONTAINMENT EVENTS
    # -------------------------------------------------------------

    st.markdown(
        "### 🚨 Active Containment Events"
    )

    events = _load_containment_events(
        ledger,
    )

    if not events:

        st.success(
            "No active containment events."
        )

    else:

        for idx, event in enumerate(events):

            _render_event_card(
                storage,
                event,
                idx,
            )

    st.divider()

    # -------------------------------------------------------------
    # VERIFICATION FAILURES
    # -------------------------------------------------------------

    st.markdown(
        "### ⚠️ Verification Failures"
    )

    failures = _load_verification_failures(
        ledger,
    )

    if failures:

        failure_df = pd.DataFrame(
            failures
        )

        st.dataframe(
            failure_df,
            use_container_width=True,
            height=260,
        )

    else:

        st.success(
            "No verification failures."
        )

    st.divider()

    # -------------------------------------------------------------
    # BLAST RADIUS
    # -------------------------------------------------------------

    st.markdown(
        "### 🌐 Blast Radius Overview"
    )

    blast_rows = _load_blast_radius_rows(
        ledger,
    )

    if blast_rows:

        st.dataframe(
            pd.DataFrame(blast_rows),
            use_container_width=True,
            height=260,
        )

    else:

        st.info(
            "No blast radius telemetry available."
        )


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def _build_metrics(
    ledger: Any,
) -> Dict[str, int]:

    metrics = {
        "contained_hosts": 0,
        "pending_verifications": 0,
        "rollback_required": 0,
        "failed_containment": 0,
        "blast_radius_alerts": 0,
    }

    if ledger is None:
        return metrics

    try:

        rows = (
            ledger.get_recent_events(
                limit=500
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        for row in rows:

            event_type = str(
                row.get("event_type", "")
            ).upper()

            if event_type in {
                "ENDPOINT_ISOLATED",
                "HOST_CONTAINED",
            }:
                metrics[
                    "contained_hosts"
                ] += 1

            if event_type in {
                "VERIFICATION_PENDING",
            }:
                metrics[
                    "pending_verifications"
                ] += 1

            if event_type in {
                "ROLLBACK_REQUIRED",
            }:
                metrics[
                    "rollback_required"
                ] += 1

            if event_type in {
                "CONTAINMENT_FAILED",
                "VERIFICATION_FAILED",
            }:
                metrics[
                    "failed_containment"
                ] += 1

            if event_type in {
                "BLAST_RADIUS_HIGH",
                "BLAST_RADIUS_CRITICAL",
            }:
                metrics[
                    "blast_radius_alerts"
                ] += 1

    except Exception:
        pass

    return metrics


# ---------------------------------------------------------------------
# CONNECTOR ROWS
# ---------------------------------------------------------------------

def _build_connector_rows(
    registry: Any,
) -> List[Dict[str, Any]]:

    rows: List[
        Dict[str, Any]
    ] = []

    if registry is None:
        return rows

    try:

        connectors = getattr(
            registry,
            "_connectors",
            {},
        )

        for connector_id, connector in connectors.items():

            auth_state = getattr(
                connector,
                "auth_state",
                None,
            )

            rows.append(
                {
                    "connector": connector_id,
                    "vendor": getattr(
                        connector,
                        "vendor",
                        "Unknown",
                    ),
                    "authenticated": bool(
                        getattr(
                            auth_state,
                            "authenticated",
                            False,
                        )
                    ),
                    "simulation_mode": bool(
                        getattr(
                            connector,
                            "simulation_mode",
                            True,
                        )
                    ),
                    "tenant_id": getattr(
                        connector,
                        "tenant_id",
                        "default",
                    ),
                }
            )

    except Exception:
        pass

    return rows


# ---------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------

def _load_containment_events(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    try:

        rows = (
            ledger.get_recent_events(
                limit=200
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        filtered = []

        for row in rows:

            event_type = str(
                row.get("event_type", "")
            ).upper()

            if event_type in {
                "ENDPOINT_ISOLATED",
                "HOST_CONTAINED",
                "CONTAINMENT_TRIGGERED",
                "AUTONOMOUS_CONTAINMENT",
            }:
                filtered.append(row)

        return filtered

    except Exception:
        return []


def _render_event_card(
    storage: Any,
    event: Dict[str, Any],
    idx: int,
) -> None:

    severity = str(
        event.get(
            "severity",
            "MEDIUM",
        )
    ).upper()

    color = SEVERITY_COLORS.get(
        severity,
        "#607d8b",
    )

    case_id = event.get(
        "case_id",
        "N/A",
    )

    connector = event.get(
        "connector_id",
        "unknown",
    )

    host = (
        event.get("target_id")
        or event.get("host_id")
        or "unknown"
    )

    ts = event.get(
        "timestamp_ms",
        0,
    )

    st.markdown(
        f"""
        <div style="
            border-left: 6px solid {color};
            background: #111827;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 12px;
        ">
            <div style="
                font-size:18px;
                font-weight:700;
                color:white;
            ">
                {event.get('event_type')}
            </div>

            <div style="color:#cbd5e1;">
                Host: {host}
            </div>

            <div style="color:#cbd5e1;">
                Connector: {connector}
            </div>

            <div style="color:#cbd5e1;">
                Case: {case_id}
            </div>

            <div style="color:#cbd5e1;">
                Severity: {severity}
            </div>

            <div style="color:#94a3b8;">
                Timestamp: {ts}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "🔍 Verify",
            key=f"verify_{idx}",
        ):

            st.info(
                "Verification workflow trigger placeholder."
            )

    with c2:

        if st.button(
            "↩️ Rollback",
            key=f"rollback_{idx}",
        ):

            st.warning(
                "Rollback orchestration placeholder."
            )

    with c3:

        if st.button(
            "🧊 Release",
            key=f"release_{idx}",
        ):

            st.warning(
                "Containment release placeholder."
            )


# ---------------------------------------------------------------------
# FAILURES
# ---------------------------------------------------------------------

def _load_verification_failures(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    try:

        rows = (
            ledger.get_recent_events(
                limit=250
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        failures = []

        for row in rows:

            event_type = str(
                row.get("event_type", "")
            ).upper()

            if event_type in {
                "VERIFICATION_FAILED",
                "ROLLBACK_REQUIRED",
                "CONTAINMENT_FAILED",
            }:
                failures.append(
                    {
                        "event_type": event_type,
                        "target": row.get(
                            "target_id"
                        ),
                        "connector": row.get(
                            "connector_id"
                        ),
                        "severity": row.get(
                            "severity"
                        ),
                        "timestamp_ms": row.get(
                            "timestamp_ms"
                        ),
                    }
                )

        return failures

    except Exception:
        return []


# ---------------------------------------------------------------------
# BLAST RADIUS
# ---------------------------------------------------------------------

def _load_blast_radius_rows(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    try:

        rows = (
            ledger.get_recent_events(
                limit=250
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        blast_rows = []

        for row in rows:

            event_type = str(
                row.get("event_type", "")
            ).upper()

            if "BLAST_RADIUS" in event_type:

                blast_rows.append(
                    {
                        "event_type": event_type,
                        "target": row.get(
                            "target_id"
                        ),
                        "risk_score": row.get(
                            "risk_score"
                        ),
                        "severity": row.get(
                            "severity"
                        ),
                        "timestamp_ms": row.get(
                            "timestamp_ms"
                        ),
                    }
                )

        return blast_rows

    except Exception:
        return []