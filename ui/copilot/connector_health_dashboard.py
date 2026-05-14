"""
ui/copilot/connector_health_dashboard.py

Realtime Connector Health Dashboard
for Veridion Pro / CUI GovCloud.

Provides:
- connector auth visibility
- connector latency telemetry
- API failure monitoring
- rate limit visibility
- degraded connector detection
- tenant connector visibility
- execution telemetry
- operational connector health analytics
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


CONNECTOR_EVENTS = {
    "CONNECTOR_EXECUTION_STARTED",
    "CONNECTOR_EXECUTION_COMPLETED",
    "CONNECTOR_EXECUTION_FAILED",
    "CONNECTOR_DEGRADED",
    "CONNECTOR_RATE_LIMITED",
    "CONNECTOR_AUTH_FAILED",
    "CONNECTOR_VERIFICATION_FAILED",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


# ---------------------------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------------------------

def render_connector_health_dashboard(
    storage: Any,
) -> None:

    st.markdown(
        """
        ## 🔌 Connector Health Dashboard

        Realtime connector telemetry,
        operational health,
        degradation monitoring,
        and execution analytics.
        """
    )

    registry = getattr(
        storage,
        "connector_registry",
        None,
    )

    ledger = getattr(
        storage,
        "ledger",
        None,
    )

    # -------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------

    metrics = _build_metrics(
        storage,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Registered",
        metrics["registered"],
    )

    c2.metric(
        "Authenticated",
        metrics["authenticated"],
    )

    c3.metric(
        "Failures",
        metrics["failures"],
    )

    c4.metric(
        "Rate Limited",
        metrics["rate_limited"],
    )

    c5.metric(
        "Degraded",
        metrics["degraded"],
    )

    st.divider()

    # -------------------------------------------------------------
    # CONNECTOR STATUS TABLE
    # -------------------------------------------------------------

    st.markdown(
        "### 📡 Connector Status"
    )

    connector_rows = _build_connector_rows(
        registry,
    )

    if connector_rows:

        st.dataframe(
            pd.DataFrame(connector_rows),
            use_container_width=True,
            height=300,
        )

    else:

        st.warning(
            "No registered connectors."
        )

    st.divider()

    # -------------------------------------------------------------
    # EXECUTION TELEMETRY
    # -------------------------------------------------------------

    st.markdown(
        "### 🚀 Connector Execution Telemetry"
    )

    telemetry_rows = _load_execution_telemetry(
        ledger,
    )

    if telemetry_rows:

        st.dataframe(
            pd.DataFrame(telemetry_rows),
            use_container_width=True,
            height=320,
        )

    else:

        st.info(
            "No execution telemetry available."
        )

    st.divider()

    # -------------------------------------------------------------
    # FAILURES
    # -------------------------------------------------------------

    st.markdown(
        "### ❌ Connector Failures"
    )

    failure_rows = _load_connector_failures(
        ledger,
    )

    if failure_rows:

        st.dataframe(
            pd.DataFrame(failure_rows),
            use_container_width=True,
            height=260,
        )

    else:

        st.success(
            "No connector failures detected."
        )

    st.divider()

    # -------------------------------------------------------------
    # RATE LIMITING
    # -------------------------------------------------------------

    st.markdown(
        "### ⏱️ Rate Limiting"
    )

    rate_rows = _load_rate_limit_rows(
        ledger,
    )

    if rate_rows:

        st.dataframe(
            pd.DataFrame(rate_rows),
            use_container_width=True,
            height=240,
        )

    else:

        st.success(
            "No connector rate limiting detected."
        )

    st.divider()

    # -------------------------------------------------------------
    # DEGRADATION
    # -------------------------------------------------------------

    st.markdown(
        "### ⚠️ Connector Degradation"
    )

    degraded_rows = _load_degraded_rows(
        ledger,
    )

    if degraded_rows:

        st.dataframe(
            pd.DataFrame(degraded_rows),
            use_container_width=True,
            height=260,
        )

    else:

        st.success(
            "No degraded connectors."
        )

    st.divider()

    # -------------------------------------------------------------
    # MANUAL HEALTH CHECKS
    # -------------------------------------------------------------

    st.markdown(
        "### 🩺 Manual Health Checks"
    )

    if registry is not None:

        connector_ids = sorted(
            list(
                getattr(
                    registry,
                    "_connectors",
                    {},
                ).keys()
            )
        )

    else:

        connector_ids = []

    selected_connector = st.selectbox(
        "Connector",
        connector_ids,
        key="connector_health_check_connector",
    )

    if st.button(
        "Run Health Check",
        key="connector_health_check_button",
    ):

        if not selected_connector:

            st.error(
                "Connector required."
            )

        else:

            try:

                connector = (
                    registry.get_connector(
                        selected_connector
                    )
                    if hasattr(
                        registry,
                        "get_connector",
                    )
                    else None
                )

                if connector is None:

                    st.error(
                        "Connector not found."
                    )

                else:

                    auth_state = (
                        connector.ensure_authenticated()
                    )

                    st.success(
                        f"""
                        Health check completed.

                        authenticated:
                        {auth_state.authenticated}
                        """
                    )

            except Exception as exc:

                st.error(
                    f"Health check failed: {exc}"
                )


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def _build_metrics(
    storage: Any,
) -> Dict[str, int]:

    metrics = {
        "registered": 0,
        "authenticated": 0,
        "failures": 0,
        "rate_limited": 0,
        "degraded": 0,
    }

    registry = getattr(
        storage,
        "connector_registry",
        None,
    )

    ledger = getattr(
        storage,
        "ledger",
        None,
    )

    try:

        if registry is not None:

            connectors = getattr(
                registry,
                "_connectors",
                {},
            )

            metrics[
                "registered"
            ] = len(connectors)

            for connector in connectors.values():

                auth_state = getattr(
                    connector,
                    "auth_state",
                    None,
                )

                if bool(
                    getattr(
                        auth_state,
                        "authenticated",
                        False,
                    )
                ):

                    metrics[
                        "authenticated"
                    ] += 1

        if ledger is not None:

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
                    row.get(
                        "event_type",
                        "",
                    )
                ).upper()

                if event_type in {
                    "CONNECTOR_EXECUTION_FAILED",
                    "CONNECTOR_AUTH_FAILED",
                }:

                    metrics[
                        "failures"
                    ] += 1

                if event_type in {
                    "CONNECTOR_RATE_LIMITED",
                }:

                    metrics[
                        "rate_limited"
                    ] += 1

                if event_type in {
                    "CONNECTOR_DEGRADED",
                }:

                    metrics[
                        "degraded"
                    ] += 1

    except Exception:
        pass

    return metrics


# ---------------------------------------------------------------------
# CONNECTOR TABLE
# ---------------------------------------------------------------------

def _build_connector_rows(
    registry: Any,
) -> List[Dict[str, Any]]:

    rows = []

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
                    "tenant_id": getattr(
                        connector,
                        "tenant_id",
                        "default",
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
                    "verification_supported": hasattr(
                        connector,
                        "_verify_real",
                    ),
                    "rollback_supported": hasattr(
                        connector,
                        "_rollback_real",
                    ),
                }
            )

    except Exception:
        pass

    return rows


# ---------------------------------------------------------------------
# TELEMETRY
# ---------------------------------------------------------------------

def _load_execution_telemetry(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    telemetry = []

    try:

        rows = (
            ledger.get_recent_events(
                limit=400
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        for row in rows:

            event_type = str(
                row.get(
                    "event_type",
                    "",
                )
            ).upper()

            if event_type in {
                "CONNECTOR_EXECUTION_STARTED",
                "CONNECTOR_EXECUTION_COMPLETED",
                "CONNECTOR_EXECUTION_FAILED",
            }:

                telemetry.append(
                    {
                        "event_type": event_type,
                        "connector": row.get(
                            "connector_id"
                        ),
                        "target": row.get(
                            "target_id"
                        ),
                        "severity": row.get(
                            "severity"
                        ),
                        "timestamp_ms": row.get(
                            "timestamp_ms"
                        ),
                    }
                )

    except Exception:
        pass

    return telemetry


# ---------------------------------------------------------------------
# FAILURES
# ---------------------------------------------------------------------

def _load_connector_failures(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    failures = []

    try:

        rows = (
            ledger.get_recent_events(
                limit=400
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        for row in rows:

            event_type = str(
                row.get(
                    "event_type",
                    "",
                )
            ).upper()

            if event_type in {
                "CONNECTOR_EXECUTION_FAILED",
                "CONNECTOR_AUTH_FAILED",
                "CONNECTOR_VERIFICATION_FAILED",
            }:

                failures.append(
                    {
                        "event_type": event_type,
                        "connector": row.get(
                            "connector_id"
                        ),
                        "target": row.get(
                            "target_id"
                        ),
                        "severity": row.get(
                            "severity"
                        ),
                        "timestamp_ms": row.get(
                            "timestamp_ms"
                        ),
                    }
                )

    except Exception:
        pass

    return failures


# ---------------------------------------------------------------------
# RATE LIMITS
# ---------------------------------------------------------------------

def _load_rate_limit_rows(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    rows_out = []

    try:

        rows = (
            ledger.get_recent_events(
                limit=300
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        for row in rows:

            event_type = str(
                row.get(
                    "event_type",
                    "",
                )
            ).upper()

            if event_type in {
                "CONNECTOR_RATE_LIMITED",
            }:

                rows_out.append(
                    {
                        "connector": row.get(
                            "connector_id"
                        ),
                        "target": row.get(
                            "target_id"
                        ),
                        "severity": row.get(
                            "severity"
                        ),
                        "timestamp_ms": row.get(
                            "timestamp_ms"
                        ),
                    }
                )

    except Exception:
        pass

    return rows_out


# ---------------------------------------------------------------------
# DEGRADED
# ---------------------------------------------------------------------

def _load_degraded_rows(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    degraded = []

    try:

        rows = (
            ledger.get_recent_events(
                limit=300
            )
            if hasattr(
                ledger,
                "get_recent_events",
            )
            else []
        )

        for row in rows:

            event_type = str(
                row.get(
                    "event_type",
                    "",
                )
            ).upper()

            if event_type in {
                "CONNECTOR_DEGRADED",
            }:

                degraded.append(
                    {
                        "connector": row.get(
                            "connector_id"
                        ),
                        "target": row.get(
                            "target_id"
                        ),
                        "severity": row.get(
                            "severity"
                        ),
                        "timestamp_ms": row.get(
                            "timestamp_ms"
                        ),
                    }
                )

    except Exception:
        pass

    return degraded