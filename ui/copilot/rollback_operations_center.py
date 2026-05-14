"""
ui/copilot/rollback_operations_center.py

Rollback Operations Center for Veridion Pro / CUI GovCloud.

Provides:
- rollback execution visibility
- rollback replay controls
- rollback verification telemetry
- rollback escalation monitoring
- rollback drift detection
- autonomous rollback operations graph
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


ROLLBACK_EVENT_TYPES = {
    "ROLLBACK_TRIGGERED",
    "ROLLBACK_STARTED",
    "ROLLBACK_COMPLETED",
    "ROLLBACK_FAILED",
    "ROLLBACK_REQUIRED",
    "ROLLBACK_ESCALATED",
    "ROLLBACK_VERIFICATION_FAILED",
    "ROLLBACK_DRIFT_DETECTED",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


# ---------------------------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------------------------

def render_rollback_operations_center(
    storage: Any,
) -> None:

    st.markdown(
        """
        ## ↩️ Rollback Operations Center

        Realtime rollback orchestration,
        replay, escalation, and verification.
        """
    )

    ledger = getattr(
        storage,
        "ledger",
        None,
    )

    rollback_orchestrator = getattr(
        storage,
        "rollback_orchestrator",
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
        "Rollback Events",
        metrics["rollback_events"],
    )

    c2.metric(
        "Rollback Failures",
        metrics["rollback_failures"],
    )

    c3.metric(
        "Rollback Escalations",
        metrics["rollback_escalations"],
    )

    c4.metric(
        "Drift Detected",
        metrics["drift_detected"],
    )

    c5.metric(
        "Pending Verification",
        metrics["pending_verification"],
    )

    st.divider()

    # -------------------------------------------------------------
    # ACTIVE ROLLBACKS
    # -------------------------------------------------------------

    st.markdown(
        "### 🚨 Active Rollback Operations"
    )

    active_rollbacks = _load_active_rollbacks(
        ledger,
    )

    if not active_rollbacks:

        st.success(
            "No active rollback operations."
        )

    else:

        for idx, rollback in enumerate(
            active_rollbacks
        ):

            _render_rollback_card(
                storage,
                rollback,
                idx,
            )

    st.divider()

    # -------------------------------------------------------------
    # ROLLBACK TIMELINE
    # -------------------------------------------------------------

    st.markdown(
        "### 🕒 Rollback Timeline"
    )

    timeline_rows = _build_timeline_rows(
        ledger,
    )

    if timeline_rows:

        st.dataframe(
            pd.DataFrame(timeline_rows),
            use_container_width=True,
            height=320,
        )

    else:

        st.info(
            "No rollback timeline telemetry."
        )

    st.divider()

    # -------------------------------------------------------------
    # DRIFT DETECTION
    # -------------------------------------------------------------

    st.markdown(
        "### 🌐 Rollback Drift Detection"
    )

    drift_rows = _load_drift_rows(
        ledger,
    )

    if drift_rows:

        st.dataframe(
            pd.DataFrame(drift_rows),
            use_container_width=True,
            height=260,
        )

    else:

        st.success(
            "No rollback drift detected."
        )

    st.divider()

    # -------------------------------------------------------------
    # VERIFICATION FAILURES
    # -------------------------------------------------------------

    st.markdown(
        "### ⚠️ Rollback Verification Failures"
    )

    failures = _load_verification_failures(
        ledger,
    )

    if failures:

        st.dataframe(
            pd.DataFrame(failures),
            use_container_width=True,
            height=260,
        )

    else:

        st.success(
            "No rollback verification failures."
        )

    st.divider()

    # -------------------------------------------------------------
    # REPLAY / MANUAL OPERATIONS
    # -------------------------------------------------------------

    st.markdown(
        "### 🔁 Rollback Replay Controls"
    )

    with st.expander(
        "Manual Rollback Replay",
        expanded=False,
    ):

        rollback_id = st.text_input(
            "Rollback ID",
            key="rollback_replay_id",
        )

        replay_reason = st.text_area(
            "Replay Reason",
            key="rollback_replay_reason",
        )

        dry_run = st.checkbox(
            "Dry Run Replay",
            value=True,
            key="rollback_replay_dry_run",
        )

        if st.button(
            "▶️ Replay Rollback",
            key="rollback_replay_button",
        ):

            if not rollback_id:

                st.error(
                    "Rollback ID required."
                )

            else:

                try:

                    if (
                        rollback_orchestrator
                        and hasattr(
                            rollback_orchestrator,
                            "replay_rollback",
                        )
                    ):

                        result = (
                            rollback_orchestrator.replay_rollback(
                                rollback_id=rollback_id,
                                reason=replay_reason,
                                dry_run=dry_run,
                            )
                        )

                        st.success(
                            f"Rollback replay triggered: {result}"
                        )

                    else:

                        st.warning(
                            "Rollback replay engine unavailable."
                        )

                except Exception as exc:

                    st.error(
                        f"Replay failed: {exc}"
                    )


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def _build_metrics(
    ledger: Any,
) -> Dict[str, int]:

    metrics = {
        "rollback_events": 0,
        "rollback_failures": 0,
        "rollback_escalations": 0,
        "drift_detected": 0,
        "pending_verification": 0,
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

            if event_type in ROLLBACK_EVENT_TYPES:

                metrics[
                    "rollback_events"
                ] += 1

            if event_type in {
                "ROLLBACK_FAILED",
            }:

                metrics[
                    "rollback_failures"
                ] += 1

            if event_type in {
                "ROLLBACK_ESCALATED",
            }:

                metrics[
                    "rollback_escalations"
                ] += 1

            if event_type in {
                "ROLLBACK_DRIFT_DETECTED",
            }:

                metrics[
                    "drift_detected"
                ] += 1

            if event_type in {
                "ROLLBACK_VERIFICATION_PENDING",
            }:

                metrics[
                    "pending_verification"
                ] += 1

    except Exception:
        pass

    return metrics


# ---------------------------------------------------------------------
# ACTIVE ROLLBACKS
# ---------------------------------------------------------------------

def _load_active_rollbacks(
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

        active = []

        for row in rows:

            event_type = str(
                row.get("event_type", "")
            ).upper()

            if event_type in {
                "ROLLBACK_STARTED",
                "ROLLBACK_REQUIRED",
                "ROLLBACK_ESCALATED",
            }:

                active.append(row)

        return active

    except Exception:
        return []


def _render_rollback_card(
    storage: Any,
    rollback: Dict[str, Any],
    idx: int,
) -> None:

    severity = str(
        rollback.get(
            "severity",
            "MEDIUM",
        )
    ).upper()

    color = SEVERITY_COLORS.get(
        severity,
        "#607d8b",
    )

    rollback_id = (
        rollback.get("rollback_id")
        or rollback.get("execution_id")
        or f"rollback-{idx}"
    )

    target = (
        rollback.get("target_id")
        or rollback.get("host_id")
        or rollback.get("user")
        or "unknown"
    )

    connector = rollback.get(
        "connector_id",
        "unknown",
    )

    details = rollback.get(
        "details",
        {},
    )

    if isinstance(details, str):

        try:
            details = json.loads(details)
        except Exception:
            details = {}

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
                {rollback.get("event_type")}
            </div>

            <div style="color:#cbd5e1;">
                Rollback ID: {rollback_id}
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

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        if st.button(
            "🔍 Verify",
            key=f"rollback_verify_{idx}",
        ):

            st.info(
                "Rollback verification placeholder."
            )

    with c2:

        if st.button(
            "🔁 Replay",
            key=f"rollback_replay_{idx}",
        ):

            st.warning(
                "Rollback replay placeholder."
            )

    with c3:

        if st.button(
            "⬆️ Escalate",
            key=f"rollback_escalate_{idx}",
        ):

            st.warning(
                "Rollback escalation placeholder."
            )

    with c4:

        if st.button(
            "📜 Timeline",
            key=f"rollback_timeline_{idx}",
        ):

            st.info(
                details
                if details
                else "No timeline metadata."
            )


# ---------------------------------------------------------------------
# TIMELINE
# ---------------------------------------------------------------------

def _build_timeline_rows(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    rows_out = []

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

            if event_type in ROLLBACK_EVENT_TYPES:

                rows_out.append(
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

    except Exception:
        pass

    return rows_out


# ---------------------------------------------------------------------
# DRIFT
# ---------------------------------------------------------------------

def _load_drift_rows(
    ledger: Any,
) -> List[Dict[str, Any]]:

    if ledger is None:
        return []

    drift_rows = []

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
                "ROLLBACK_DRIFT_DETECTED",
                "CONTAINMENT_DRIFT_DETECTED",
            }:

                drift_rows.append(
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

    except Exception:
        pass

    return drift_rows


# ---------------------------------------------------------------------
# VERIFICATION FAILURES
# ---------------------------------------------------------------------

def _load_verification_failures(
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
                "ROLLBACK_VERIFICATION_FAILED",
                "ROLLBACK_FAILED",
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

    except Exception:
        pass

    return failures