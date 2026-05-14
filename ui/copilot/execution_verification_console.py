"""
ui/copilot/execution_verification_console.py

Realtime Execution Verification Console
for Veridion Pro / CUI GovCloud.

Provides:
- pending verification visibility
- failed verification telemetry
- degraded execution visibility
- verification retry/requeue controls
- connector verification health
- realtime execution verification operations
"""

from __future__ import annotations

import json
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


VERIFICATION_EVENTS = {
    "VERIFICATION_STARTED",
    "VERIFICATION_COMPLETED",
    "VERIFICATION_FAILED",
    "VERIFICATION_PENDING",
    "VERIFICATION_RETRY",
    "ROLLBACK_REQUIRED",
    "EXECUTION_DEGRADED",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


# ---------------------------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------------------------

def render_execution_verification_console(
    storage: Any,
) -> None:

    st.markdown(
        """
        ## ✅ Execution Verification Console

        Realtime execution validation,
        degradation detection,
        and verification orchestration.
        """
    )

    ledger = getattr(
        storage,
        "ledger",
        None,
    )

    verifier = getattr(
        storage,
        "execution_verifier",
        None,
    )

    # -------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------

    metrics = _build_metrics(
        ledger,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Pending",
        metrics["pending"],
    )

    c2.metric(
        "Verified",
        metrics["verified"],
    )

    c3.metric(
        "Failed",
        metrics["failed"],
    )

    c4.metric(
        "Degraded",
        metrics["degraded"],
    )

    c5.metric(
        "Rollback Required",
        metrics["rollback_required"],
    )

    st.divider()

    # -------------------------------------------------------------
    # ACTIVE VERIFICATIONS
    # -------------------------------------------------------------

    st.markdown(
        "### 🔎 Active Verifications"
    )

    active_rows = _load_active_verifications(
        ledger,
    )

    if not active_rows:

        st.success(
            "No active verification operations."
        )

    else:

        for idx, row in enumerate(
            active_rows
        ):

            _render_verification_card(
                storage,
                row,
                idx,
            )

    st.divider()

    # -------------------------------------------------------------
    # FAILED VERIFICATIONS
    # -------------------------------------------------------------

    st.markdown(
        "### ❌ Failed Verifications"
    )

    failures = _load_failed_verifications(
        ledger,
    )

    if failures:

        st.dataframe(
            pd.DataFrame(failures),
            use_container_width=True,
            height=280,
        )

    else:

        st.success(
            "No verification failures."
        )

    st.divider()

    # -------------------------------------------------------------
    # DEGRADED EXECUTIONS
    # -------------------------------------------------------------

    st.markdown(
        "### ⚠️ Degraded Executions"
    )

    degraded_rows = _load_degraded_executions(
        ledger,
    )

    if degraded_rows:

        st.dataframe(
            pd.DataFrame(degraded_rows),
            use_container_width=True,
            height=280,
        )

    else:

        st.success(
            "No degraded executions."
        )

    st.divider()

    # -------------------------------------------------------------
    # CONNECTOR HEALTH
    # -------------------------------------------------------------

    st.markdown(
        "### 🔌 Connector Verification Health"
    )

    connector_rows = _build_connector_health_rows(
        storage,
    )

    if connector_rows:

        st.dataframe(
            pd.DataFrame(connector_rows),
            use_container_width=True,
            height=240,
        )

    else:

        st.info(
            "No connector telemetry available."
        )

    st.divider()

    # -------------------------------------------------------------
    # MANUAL VERIFICATION CONTROL
    # -------------------------------------------------------------

    st.markdown(
        "### ▶️ Manual Verification Control"
    )

    with st.expander(
        "Trigger Verification",
        expanded=False,
    ):

        execution_id = st.text_input(
            "Execution ID",
            key="manual_verification_execution_id",
        )

        dry_run = st.checkbox(
            "Dry Run",
            value=True,
            key="manual_verification_dry_run",
        )

        if st.button(
            "Verify Execution",
            key="manual_verify_button",
        ):

            if not execution_id:

                st.error(
                    "Execution ID required."
                )

            else:

                try:

                    if (
                        verifier
                        and hasattr(
                            verifier,
                            "verify_execution",
                        )
                    ):

                        result = (
                            verifier.verify_execution(
                                execution_id=execution_id,
                                dry_run=dry_run,
                            )
                        )

                        st.success(
                            f"Verification triggered: {result}"
                        )

                    else:

                        st.warning(
                            "Execution verifier unavailable."
                        )

                except Exception as exc:

                    st.error(
                        f"Verification failed: {exc}"
                    )


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def _build_metrics(
    ledger: Any,
) -> Dict[str, int]:

    metrics = {
        "pending": 0,
        "verified": 0,
        "failed": 0,
        "degraded": 0,
        "rollback_required": 0,
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

            if event_type == "VERIFICATION_PENDING":

                metrics["pending"] += 1

            elif event_type == "VERIFICATION_COMPLETED":

                metrics["verified"] += 1

            elif event_type == "VERIFICATION_FAILED":

                metrics["failed"] += 1

            elif event_type == "EXECUTION_DEGRADED":

                metrics["degraded"] += 1

            elif event_type == "ROLLBACK_REQUIRED":

                metrics[
                    "rollback_required"
                ] += 1

    except Exception:
        pass

    return metrics


# ---------------------------------------------------------------------
# ACTIVE VERIFICATIONS
# ---------------------------------------------------------------------

def _load_active_verifications(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    rows_out = []

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

        for row in rows:

            event_type = str(
                row.get("event_type", "")
            ).upper()

            if event_type in {
                "VERIFICATION_STARTED",
                "VERIFICATION_PENDING",
                "VERIFICATION_RETRY",
            }:

                rows_out.append(row)

    except Exception:
        pass

    return rows_out


def _render_verification_card(
    storage: Any,
    row: Dict[str, Any],
    idx: int,
) -> None:

    severity = str(
        row.get(
            "severity",
            "MEDIUM",
        )
    ).upper()

    color = SEVERITY_COLORS.get(
        severity,
        "#607d8b",
    )

    execution_id = (
        row.get("execution_id")
        or row.get("target_id")
        or f"execution-{idx}"
    )

    connector = row.get(
        "connector_id",
        "unknown",
    )

    target = (
        row.get("target_id")
        or row.get("host_id")
        or row.get("user")
        or "unknown"
    )

    st.markdown(
        f"""
        <div style="
            border-left: 6px solid {color};
            background: #111827;
            padding: 14px;
            border-radius: 10px;
            margin-bottom: 14px;
        ">
            <div style="
                font-size:18px;
                font-weight:700;
                color:white;
            ">
                {row.get('event_type')}
            </div>

            <div style="color:#cbd5e1;">
                Execution ID: {execution_id}
            </div>

            <div style="color:#cbd5e1;">
                Target: {target}
            </div>

            <div style="color:#cbd5e1;">
                Connector: {connector}
            </div>

            <div style="color:#cbd5e1;">
                Severity: {severity}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "🔁 Retry",
            key=f"verification_retry_{idx}",
        ):

            st.info(
                "Verification retry placeholder."
            )

    with c2:

        if st.button(
            "↩️ Rollback",
            key=f"verification_rollback_{idx}",
        ):

            st.warning(
                "Rollback trigger placeholder."
            )

    with c3:

        if st.button(
            "📜 Details",
            key=f"verification_details_{idx}",
        ):

            st.json(row)


# ---------------------------------------------------------------------
# FAILURES
# ---------------------------------------------------------------------

def _load_failed_verifications(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    failures = []

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
                row.get("event_type", "")
            ).upper()

            if event_type in {
                "VERIFICATION_FAILED",
                "ROLLBACK_REQUIRED",
            }:

                failures.append(
                    {
                        "event_type": event_type,
                        "execution_id": row.get(
                            "execution_id"
                        ),
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
# DEGRADED
# ---------------------------------------------------------------------

def _load_degraded_executions(
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
                row.get("event_type", "")
            ).upper()

            if event_type in {
                "EXECUTION_DEGRADED",
                "CONNECTOR_DEGRADED",
            }:

                degraded.append(
                    {
                        "event_type": event_type,
                        "execution_id": row.get(
                            "execution_id"
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

    except Exception:
        pass

    return degraded


# ---------------------------------------------------------------------
# CONNECTOR HEALTH
# ---------------------------------------------------------------------

def _build_connector_health_rows(
    storage: Any,
) -> List[Dict[str, Any]]:

    rows = []

    registry = getattr(
        storage,
        "connector_registry",
        None,
    )

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
                    "verification_supported": hasattr(
                        connector,
                        "_verify_real",
                    ),
                }
            )

    except Exception:
        pass

    return rows