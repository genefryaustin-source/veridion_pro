"""
ui/copilot/autonomy_control_panel.py

Live Autonomy Command Authority Panel for Veridion Pro / CUI GovCloud SOC.

Controls:
- Live autonomy mode switching
- Pause autonomous execution
- Force approval mode
- Disable destructive actions
- Restrict identity actions
- Restrict endpoint actions
- Emergency lockdown activation
- Governance telemetry
- Event bus subscription bridge

Safe design:
- Works even if event bus, ledger, memory, optimizer, or execution engine are not fully wired yet.
- Uses Streamlit session_state as fallback runtime governance state.
- Does not require schema changes.
"""

from __future__ import annotations

import time
import json
import traceback
from typing import Any, Dict, List, Optional, Callable


try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


# ============================================================
# AUTONOMY MODE CONSTANTS
# ============================================================

MODE_MANUAL = "MANUAL"
MODE_ASSISTED = "ASSISTED"
MODE_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
MODE_FULL_AUTONOMY = "FULL_AUTONOMY"
MODE_LOCKDOWN = "LOCKDOWN"

AUTONOMY_MODES = [
    MODE_MANUAL,
    MODE_ASSISTED,
    MODE_SUPERVISED_AUTONOMY,
    MODE_FULL_AUTONOMY,
    MODE_LOCKDOWN,
]


MODE_DESCRIPTIONS = {
    MODE_MANUAL: "Human-driven operations. AI may recommend, but cannot execute.",
    MODE_ASSISTED: "AI assists and prepares actions. Human approval required for execution.",
    MODE_SUPERVISED_AUTONOMY: "AI can execute low-risk actions. High-risk actions require approval.",
    MODE_FULL_AUTONOMY: "AI can execute approved policy actions autonomously with verification.",
    MODE_LOCKDOWN: "Emergency mode. Containment-first posture with heightened verification.",
}


MODE_RISK_POSTURE = {
    MODE_MANUAL: "LOW",
    MODE_ASSISTED: "LOW-MEDIUM",
    MODE_SUPERVISED_AUTONOMY: "MEDIUM",
    MODE_FULL_AUTONOMY: "HIGH",
    MODE_LOCKDOWN: "CRITICAL",
}


# ============================================================
# EVENT CONSTANTS
# ============================================================

EXECUTION_STARTED = "EXECUTION_STARTED"
EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
EXECUTION_FAILED = "EXECUTION_FAILED"
ROLLBACK_TRIGGERED = "ROLLBACK_TRIGGERED"
AUTONOMY_POLICY_BLOCK = "AUTONOMY_POLICY_BLOCK"

SUBSCRIBED_EVENTS = [
    EXECUTION_STARTED,
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    ROLLBACK_TRIGGERED,
    AUTONOMY_POLICY_BLOCK,
]


# ============================================================
# SAFE OPTIONAL IMPORTS
# ============================================================

def _safe_get_event_bus() -> Any:
    try:
        from core.events.event_bus import get_event_bus
        return get_event_bus()
    except Exception:
        return None


def _safe_get_autonomy_mode() -> Optional[str]:
    try:
        from core.ai.orchestration.autonomy_modes import get_autonomy_mode
        mode = get_autonomy_mode()
        if isinstance(mode, str):
            return mode.upper()
        if hasattr(mode, "name"):
            return str(mode.name).upper()
        if hasattr(mode, "value"):
            return str(mode.value).upper()
    except Exception:
        return None

    return None


def _safe_set_autonomy_mode(mode: str) -> bool:
    """
    Attempts to update the backend autonomy mode if your project exposes
    a setter. Falls back to Streamlit session state.
    """

    mode = normalize_mode(mode)

    possible_paths = [
        ("core.ai.orchestration.autonomy_modes", "set_autonomy_mode"),
        ("core.ai.orchestration.autonomy_modes", "update_autonomy_mode"),
        ("core.ai.orchestration.execution_engine", "set_autonomy_mode"),
        ("core.ai.orchestration.execution_engine", "update_autonomy_mode"),
    ]

    for module_path, fn_name in possible_paths:
        try:
            module = __import__(module_path, fromlist=[fn_name])
            fn = getattr(module, fn_name, None)
            if callable(fn):
                fn(mode)
                return True
        except Exception:
            continue

    return False


# ============================================================
# SESSION STATE
# ============================================================

def _ensure_state() -> None:
    if st is None:
        return

    defaults = {
        "autonomy_mode": _safe_get_autonomy_mode() or MODE_MANUAL,
        "autonomy_paused": False,
        "force_approval_mode": False,
        "disable_destructive_actions": True,
        "restrict_identity_actions": True,
        "restrict_endpoint_actions": False,
        "emergency_lockdown_active": False,
        "aggressive_containment": False,
        "bypass_low_risk_approval": False,
        "escalation_sensitivity": "NORMAL",
        "verification_frequency": "NORMAL",
        "governance_events": [],
        "event_bus_subscribed": False,
        "last_governance_update_ms": _now_ms(),
        "optimizer_confidence": 0.0,
        "governance_drift": 0.0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _now_ms() -> int:
    return int(time.time() * 1000)


def normalize_mode(mode: Any) -> str:
    if mode is None:
        return MODE_MANUAL

    mode = str(mode).strip().upper()

    aliases = {
        "MANUAL": MODE_MANUAL,
        "ASSISTED": MODE_ASSISTED,
        "SUPERVISED": MODE_SUPERVISED_AUTONOMY,
        "SUPERVISED_AUTONOMY": MODE_SUPERVISED_AUTONOMY,
        "FULL": MODE_FULL_AUTONOMY,
        "FULL_AUTONOMY": MODE_FULL_AUTONOMY,
        "LOCKDOWN": MODE_LOCKDOWN,
    }

    return aliases.get(mode, MODE_MANUAL)


# ============================================================
# GOVERNANCE EVENT CAPTURE
# ============================================================

def _append_governance_event(
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    source: str = "autonomy_control_panel",
) -> None:
    if st is None:
        return

    _ensure_state()

    event = {
        "ts_ms": _now_ms(),
        "event_type": event_type,
        "source": source,
        "payload": payload or {},
    }

    events = st.session_state.get("governance_events", [])
    events.insert(0, event)

    st.session_state["governance_events"] = events[:250]
    st.session_state["last_governance_update_ms"] = event["ts_ms"]


def _event_bus_callback(event: Any = None, *args: Any, **kwargs: Any) -> None:
    """
    Flexible callback because your event bus may pass either:
    - event object
    - event_type + payload
    - keyword payload
    """

    event_type = None
    payload: Dict[str, Any] = {}

    try:
        if isinstance(event, str):
            event_type = event
            payload = dict(kwargs or {})
        elif isinstance(event, dict):
            event_type = (
                event.get("event_type")
                or event.get("type")
                or event.get("name")
                or event.get("event")
                or "UNKNOWN_EVENT"
            )
            payload = event
        elif event is not None:
            event_type = (
                getattr(event, "event_type", None)
                or getattr(event, "type", None)
                or getattr(event, "name", None)
                or "UNKNOWN_EVENT"
            )
            payload = getattr(event, "payload", None) or getattr(event, "data", None) or {}
            if not isinstance(payload, dict):
                payload = {"value": str(payload)}
        else:
            event_type = kwargs.get("event_type") or kwargs.get("type") or "UNKNOWN_EVENT"
            payload = dict(kwargs or {})

        _append_governance_event(
            event_type=str(event_type),
            payload=payload,
            source="event_bus",
        )

    except Exception:
        _append_governance_event(
            event_type="EVENT_BUS_CALLBACK_ERROR",
            payload={"error": traceback.format_exc()},
            source="event_bus",
        )


def subscribe_to_event_bus() -> bool:
    """
    Subscribes to governance-critical events if the existing event bus supports it.
    Safe no-op if not available.
    """

    if st is None:
        return False

    _ensure_state()

    if st.session_state.get("event_bus_subscribed"):
        return True

    bus = _safe_get_event_bus()

    if bus is None:
        return False

    subscribed = False

    for event_name in SUBSCRIBED_EVENTS:
        try:
            if hasattr(bus, "subscribe") and callable(bus.subscribe):
                bus.subscribe(event_name, _event_bus_callback)
                subscribed = True
            elif hasattr(bus, "on") and callable(bus.on):
                bus.on(event_name, _event_bus_callback)
                subscribed = True
            elif hasattr(bus, "register") and callable(bus.register):
                bus.register(event_name, _event_bus_callback)
                subscribed = True
        except Exception:
            _append_governance_event(
                "EVENT_SUBSCRIPTION_FAILED",
                {
                    "event": event_name,
                    "error": traceback.format_exc(),
                },
            )

    st.session_state["event_bus_subscribed"] = subscribed

    if subscribed:
        _append_governance_event(
            "EVENT_BUS_SUBSCRIBED",
            {"events": SUBSCRIBED_EVENTS},
        )

    return subscribed


def publish_governance_event(event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
    payload = payload or {}

    _append_governance_event(event_type, payload)

    bus = _safe_get_event_bus()

    if bus is None:
        return

    try:
        if hasattr(bus, "publish") and callable(bus.publish):
            bus.publish(event_type, payload)
        elif hasattr(bus, "emit") and callable(bus.emit):
            bus.emit(event_type, payload)
        elif hasattr(bus, "dispatch") and callable(bus.dispatch):
            bus.dispatch(event_type, payload)
    except Exception:
        _append_governance_event(
            "EVENT_PUBLISH_FAILED",
            {
                "event_type": event_type,
                "error": traceback.format_exc(),
            },
        )


# ============================================================
# GOVERNANCE MODE APPLICATION
# ============================================================

def apply_autonomy_mode(mode: str) -> None:
    if st is None:
        return

    _ensure_state()

    mode = normalize_mode(mode)
    previous = st.session_state.get("autonomy_mode", MODE_MANUAL)

    st.session_state["autonomy_mode"] = mode

    backend_updated = _safe_set_autonomy_mode(mode)

    if mode == MODE_MANUAL:
        st.session_state["force_approval_mode"] = True
        st.session_state["disable_destructive_actions"] = True
        st.session_state["restrict_identity_actions"] = True
        st.session_state["restrict_endpoint_actions"] = True
        st.session_state["aggressive_containment"] = False
        st.session_state["bypass_low_risk_approval"] = False
        st.session_state["escalation_sensitivity"] = "NORMAL"
        st.session_state["verification_frequency"] = "NORMAL"
        st.session_state["emergency_lockdown_active"] = False

    elif mode == MODE_ASSISTED:
        st.session_state["force_approval_mode"] = True
        st.session_state["disable_destructive_actions"] = True
        st.session_state["restrict_identity_actions"] = True
        st.session_state["restrict_endpoint_actions"] = False
        st.session_state["aggressive_containment"] = False
        st.session_state["bypass_low_risk_approval"] = False
        st.session_state["escalation_sensitivity"] = "NORMAL"
        st.session_state["verification_frequency"] = "NORMAL"
        st.session_state["emergency_lockdown_active"] = False

    elif mode == MODE_SUPERVISED_AUTONOMY:
        st.session_state["force_approval_mode"] = False
        st.session_state["disable_destructive_actions"] = True
        st.session_state["restrict_identity_actions"] = True
        st.session_state["restrict_endpoint_actions"] = False
        st.session_state["aggressive_containment"] = False
        st.session_state["bypass_low_risk_approval"] = False
        st.session_state["escalation_sensitivity"] = "ELEVATED"
        st.session_state["verification_frequency"] = "ELEVATED"
        st.session_state["emergency_lockdown_active"] = False

    elif mode == MODE_FULL_AUTONOMY:
        st.session_state["force_approval_mode"] = False
        st.session_state["disable_destructive_actions"] = False
        st.session_state["restrict_identity_actions"] = True
        st.session_state["restrict_endpoint_actions"] = False
        st.session_state["aggressive_containment"] = True
        st.session_state["bypass_low_risk_approval"] = True
        st.session_state["escalation_sensitivity"] = "HIGH"
        st.session_state["verification_frequency"] = "HIGH"
        st.session_state["emergency_lockdown_active"] = False

    elif mode == MODE_LOCKDOWN:
        enter_lockdown()

    publish_governance_event(
        "AUTONOMY_MODE_CHANGED",
        {
            "previous_mode": previous,
            "new_mode": mode,
            "backend_updated": backend_updated,
        },
    )


def enter_lockdown() -> None:
    if st is None:
        return

    _ensure_state()

    previous = st.session_state.get("autonomy_mode", MODE_MANUAL)

    st.session_state["autonomy_mode"] = MODE_LOCKDOWN
    st.session_state["emergency_lockdown_active"] = True
    st.session_state["autonomy_paused"] = False

    # Lockdown posture
    st.session_state["aggressive_containment"] = True
    st.session_state["bypass_low_risk_approval"] = True
    st.session_state["escalation_sensitivity"] = "MAXIMUM"
    st.session_state["verification_frequency"] = "MAXIMUM"

    # Safety rails remain enabled for high-impact destructive/identity action.
    st.session_state["disable_destructive_actions"] = True
    st.session_state["restrict_identity_actions"] = True

    # Endpoint containment may be required during lockdown.
    st.session_state["restrict_endpoint_actions"] = False

    backend_updated = _safe_set_autonomy_mode(MODE_LOCKDOWN)

    publish_governance_event(
        "LOCKDOWN_ACTIVATED",
        {
            "previous_mode": previous,
            "new_mode": MODE_LOCKDOWN,
            "backend_updated": backend_updated,
            "aggressive_containment": True,
            "bypass_low_risk_approval": True,
            "escalation_sensitivity": "MAXIMUM",
            "verification_frequency": "MAXIMUM",
        },
    )


def exit_lockdown(target_mode: str = MODE_SUPERVISED_AUTONOMY) -> None:
    if st is None:
        return

    _ensure_state()

    st.session_state["emergency_lockdown_active"] = False
    apply_autonomy_mode(target_mode)

    publish_governance_event(
        "LOCKDOWN_EXITED",
        {"target_mode": target_mode},
    )


# ============================================================
# METRIC COLLECTION
# ============================================================

def _call_first_available(obj: Any, method_names: List[str], default: Any = None) -> Any:
    if obj is None:
        return default

    for name in method_names:
        try:
            fn = getattr(obj, name, None)
            if callable(fn):
                return fn()
        except Exception:
            continue

    return default


def _safe_count_rows(storage: Any, table_name: str, where_clause: str = "") -> int:
    """
    Optional helper for SQLite-like ledger connections.
    Does not assume any schema exists.
    """

    try:
        ledger = getattr(storage, "ledger", storage)

        conn = getattr(ledger, "conn", None) or getattr(ledger, "connection", None)
        if conn is None and hasattr(ledger, "get_connection"):
            conn = ledger.get_connection()

        if conn is None:
            return 0

        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
        return int(row[0] or 0)
    except Exception:
        return 0


def collect_governance_metrics(storage: Any = None) -> Dict[str, Any]:
    if st is not None:
        _ensure_state()

    ledger = getattr(storage, "ledger", storage) if storage is not None else None

    active_execution_count = _call_first_available(
        ledger,
        [
            "count_active_executions",
            "get_active_execution_count",
            "count_running_executions",
            "count_active_jobs",
        ],
        default=None,
    )

    if active_execution_count is None:
        active_execution_count = _safe_count_rows(
            storage,
            "pipeline_jobs",
            "status IN ('RUNNING','PROCESSING','LEASED')",
        )

    approval_queue_depth = _call_first_available(
        ledger,
        [
            "count_pending_approvals",
            "get_approval_queue_depth",
            "count_approval_queue",
        ],
        default=None,
    )

    if approval_queue_depth is None:
        approval_queue_depth = _safe_count_rows(
            storage,
            "approval_requests",
            "status IN ('PENDING','OPEN','AWAITING_REVIEW')",
        )

    failed_verification_count = _call_first_available(
        ledger,
        [
            "count_failed_verifications",
            "get_failed_verification_count",
        ],
        default=None,
    )

    if failed_verification_count is None:
        failed_verification_count = _safe_count_rows(
            storage,
            "pipeline_jobs",
            "stage IN ('VERIFY','VERIFICATION') AND status IN ('FAILED','ERROR')",
        )

    escalation_pressure = _call_first_available(
        ledger,
        [
            "get_escalation_pressure",
            "calculate_escalation_pressure",
            "count_active_escalations",
        ],
        default=None,
    )

    if escalation_pressure is None:
        escalation_pressure = _safe_count_rows(
            storage,
            "cases",
            "severity IN ('CRITICAL','HIGH') AND status NOT IN ('CLOSED','RESOLVED')",
        )

    rollback_rate = calculate_rollback_rate()
    governance_drift = calculate_governance_drift()
    optimizer_confidence = calculate_optimizer_confidence()

    metrics = {
        "current_autonomy_mode": st.session_state.get("autonomy_mode", MODE_MANUAL) if st else MODE_MANUAL,
        "active_execution_count": int(active_execution_count or 0),
        "rollback_rate": float(rollback_rate),
        "approval_queue_depth": int(approval_queue_depth or 0),
        "failed_verification_count": int(failed_verification_count or 0),
        "escalation_pressure": int(escalation_pressure or 0),
        "governance_drift": float(governance_drift),
        "optimizer_confidence": float(optimizer_confidence),
    }

    return metrics


def calculate_rollback_rate() -> float:
    if st is None:
        return 0.0

    events = st.session_state.get("governance_events", [])

    execution_events = [
        e for e in events
        if e.get("event_type") in {EXECUTION_STARTED, EXECUTION_COMPLETED, EXECUTION_FAILED}
    ]

    rollback_events = [
        e for e in events
        if e.get("event_type") == ROLLBACK_TRIGGERED
    ]

    if not execution_events:
        return 0.0

    return round((len(rollback_events) / max(len(execution_events), 1)) * 100.0, 2)


def calculate_governance_drift() -> float:
    if st is None:
        return 0.0

    mode = st.session_state.get("autonomy_mode", MODE_MANUAL)

    drift = 0.0

    if mode == MODE_MANUAL and not st.session_state.get("force_approval_mode"):
        drift += 25.0

    if mode in {MODE_MANUAL, MODE_ASSISTED} and not st.session_state.get("disable_destructive_actions"):
        drift += 30.0

    if mode != MODE_LOCKDOWN and st.session_state.get("emergency_lockdown_active"):
        drift += 35.0

    if st.session_state.get("autonomy_paused") and mode == MODE_FULL_AUTONOMY:
        drift += 10.0

    if st.session_state.get("bypass_low_risk_approval") and mode in {MODE_MANUAL, MODE_ASSISTED}:
        drift += 20.0

    return min(round(drift, 2), 100.0)


def calculate_optimizer_confidence() -> float:
    if st is None:
        return 0.0

    events = st.session_state.get("governance_events", [])

    if not events:
        return 0.0

    recent = events[:50]

    failures = len([e for e in recent if e.get("event_type") in {EXECUTION_FAILED, AUTONOMY_POLICY_BLOCK}])
    rollbacks = len([e for e in recent if e.get("event_type") == ROLLBACK_TRIGGERED])
    completed = len([e for e in recent if e.get("event_type") == EXECUTION_COMPLETED])

    score = 70.0 + min(completed * 2.0, 20.0) - failures * 6.0 - rollbacks * 8.0

    return max(0.0, min(round(score, 2), 100.0))


# ============================================================
# UI HELPERS
# ============================================================

def _badge(label: str, value: str, tone: str = "neutral") -> None:
    if st is None:
        return

    colors = {
        "neutral": ("#1f2937", "#e5e7eb"),
        "green": ("#065f46", "#d1fae5"),
        "yellow": ("#92400e", "#fef3c7"),
        "red": ("#991b1b", "#fee2e2"),
        "blue": ("#1e40af", "#dbeafe"),
        "purple": ("#5b21b6", "#ede9fe"),
    }

    fg, bg = colors.get(tone, colors["neutral"])

    st.markdown(
        f"""
        <div style="
            padding: 0.65rem 0.8rem;
            border-radius: 0.85rem;
            background: {bg};
            color: {fg};
            border: 1px solid rgba(0,0,0,0.06);
            margin-bottom: 0.45rem;
        ">
            <div style="font-size:0.72rem; opacity:0.78;">{label}</div>
            <div style="font-size:1.05rem; font-weight:800;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _mode_tone(mode: str) -> str:
    mode = normalize_mode(mode)

    if mode == MODE_MANUAL:
        return "blue"
    if mode == MODE_ASSISTED:
        return "green"
    if mode == MODE_SUPERVISED_AUTONOMY:
        return "yellow"
    if mode == MODE_FULL_AUTONOMY:
        return "purple"
    if mode == MODE_LOCKDOWN:
        return "red"

    return "neutral"


def _metric_tone(value: float, warning: float, critical: float, inverse: bool = False) -> str:
    if inverse:
        if value >= warning:
            return "green"
        if value >= critical:
            return "yellow"
        return "red"

    if value >= critical:
        return "red"
    if value >= warning:
        return "yellow"
    return "green"


def _render_status_header(metrics: Dict[str, Any]) -> None:
    mode = metrics["current_autonomy_mode"]

    st.markdown("### Autonomous Command Authority")

    _badge(
        "Current Autonomy Mode",
        mode,
        _mode_tone(mode),
    )

    st.caption(MODE_DESCRIPTIONS.get(mode, ""))

    if st.session_state.get("emergency_lockdown_active"):
        st.error("🚨 Emergency Lockdown is ACTIVE. Containment-first governance posture is enabled.")

    if st.session_state.get("autonomy_paused"):
        st.warning("Autonomous execution is currently PAUSED.")


def _render_mode_switcher() -> None:
    st.markdown("#### Live Autonomy Mode Switching")

    current = normalize_mode(st.session_state.get("autonomy_mode", MODE_MANUAL))

    selected = st.selectbox(
        "Autonomy Mode",
        AUTONOMY_MODES,
        index=AUTONOMY_MODES.index(current) if current in AUTONOMY_MODES else 0,
        format_func=lambda x: x.replace("_", " ").title(),
        key="autonomy_mode_selector",
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        if st.button("Apply Mode", use_container_width=True, key="apply_autonomy_mode_btn"):
            apply_autonomy_mode(selected)
            st.success(f"Autonomy mode updated to {selected}.")
            st.rerun()

    with c2:
        if st.button("Refresh Governance", use_container_width=True, key="refresh_governance_btn"):
            publish_governance_event("GOVERNANCE_PANEL_REFRESHED", {})
            st.rerun()

    st.info(
        f"Risk posture: **{MODE_RISK_POSTURE.get(current, 'UNKNOWN')}**"
    )


def _render_safety_controls() -> None:
    st.markdown("#### Operational Safety Controls")

    controls = [
        ("autonomy_paused", "Pause autonomous execution"),
        ("force_approval_mode", "Force approval mode"),
        ("disable_destructive_actions", "Disable destructive actions"),
        ("restrict_identity_actions", "Restrict identity actions"),
        ("restrict_endpoint_actions", "Restrict endpoint actions"),
    ]

    for key, label in controls:
        previous = st.session_state.get(key, False)
        value = st.toggle(label, value=previous, key=f"toggle_{key}")

        if value != previous:
            st.session_state[key] = value
            publish_governance_event(
                "GOVERNANCE_CONTROL_CHANGED",
                {
                    "control": key,
                    "previous": previous,
                    "new": value,
                },
            )

    st.divider()

    c1, c2 = st.columns([1, 1])

    with c1:
        if st.button("🚨 ENTER LOCKDOWN MODE", type="primary", use_container_width=True, key="enter_lockdown_btn"):
            enter_lockdown()
            st.rerun()

    with c2:
        if st.button("Exit Lockdown to Supervised", use_container_width=True, key="exit_lockdown_btn"):
            exit_lockdown(MODE_SUPERVISED_AUTONOMY)
            st.rerun()


def _render_live_governance_state(metrics: Dict[str, Any]) -> None:
    st.markdown("#### Live Governance State")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Active Executions", metrics["active_execution_count"])
        st.metric("Approval Queue", metrics["approval_queue_depth"])

    with c2:
        st.metric("Rollback Rate", f"{metrics['rollback_rate']}%")
        st.metric("Failed Verifications", metrics["failed_verification_count"])

    with c3:
        st.metric("Escalation Pressure", metrics["escalation_pressure"])
        st.metric("Governance Drift", f"{metrics['governance_drift']}%")

    with c4:
        st.metric("Optimizer Confidence", f"{metrics['optimizer_confidence']}%")
        st.metric("Mode Risk", MODE_RISK_POSTURE.get(metrics["current_autonomy_mode"], "UNKNOWN"))

    drift = metrics["governance_drift"]
    confidence = metrics["optimizer_confidence"]

    if drift >= 50:
        st.error("Governance drift is elevated. Review safety controls and autonomy policy alignment.")
    elif drift >= 20:
        st.warning("Governance drift is present. Some controls may conflict with the active autonomy mode.")
    else:
        st.success("Governance posture is aligned with the active autonomy mode.")

    if confidence < 35 and metrics["current_autonomy_mode"] in {MODE_FULL_AUTONOMY, MODE_SUPERVISED_AUTONOMY}:
        st.warning("Optimizer confidence is low for the selected autonomy level.")


def _render_lockdown_posture() -> None:
    st.markdown("#### Lockdown Control State")

    c1, c2 = st.columns(2)

    with c1:
        _badge(
            "Aggressive Containment",
            str(st.session_state.get("aggressive_containment", False)).upper(),
            "red" if st.session_state.get("aggressive_containment") else "neutral",
        )

        _badge(
            "Bypass Low-Risk Approval",
            str(st.session_state.get("bypass_low_risk_approval", False)).upper(),
            "yellow" if st.session_state.get("bypass_low_risk_approval") else "neutral",
        )

    with c2:
        _badge(
            "Escalation Sensitivity",
            str(st.session_state.get("escalation_sensitivity", "NORMAL")),
            "red" if st.session_state.get("escalation_sensitivity") == "MAXIMUM" else "blue",
        )

        _badge(
            "Verification Frequency",
            str(st.session_state.get("verification_frequency", "NORMAL")),
            "red" if st.session_state.get("verification_frequency") == "MAXIMUM" else "blue",
        )


def _render_event_bus_status() -> None:
    st.markdown("#### Event Bus Subscriptions")

    subscribed = subscribe_to_event_bus()

    if subscribed:
        st.success("Event bus subscription active.")
    else:
        st.warning("Event bus subscription not active yet. Panel is using session-state telemetry fallback.")

    st.code("\n".join(SUBSCRIBED_EVENTS), language="text")


def _render_recent_events() -> None:
    st.markdown("#### Recent Governance Events")

    events = st.session_state.get("governance_events", [])

    if not events:
        st.info("No governance events captured yet.")
        return

    for event in events[:10]:
        ts = event.get("ts_ms", 0)
        event_type = event.get("event_type", "UNKNOWN")
        source = event.get("source", "unknown")
        payload = event.get("payload", {})

        with st.expander(f"{event_type} · {source} · {ts}", expanded=False):
            st.json(payload)


# ============================================================
# PUBLIC RENDER FUNCTION
# ============================================================

def render_autonomous_control_panel(storage: Any = None) -> None:
    """
    Main UI entrypoint.

    Usage:
        from ui.copilot.autonomy_control_panel import render_autonomous_control_panel
        render_autonomous_control_panel(storage)
    """

    if st is None:
        raise RuntimeError("Streamlit is required to render autonomy control panel.")

    _ensure_state()
    subscribe_to_event_bus()

    metrics = collect_governance_metrics(storage)

    _render_status_header(metrics)

    tab_control, tab_state, tab_lockdown, tab_events = st.tabs(
        [
            "Command Controls",
            "Governance State",
            "Lockdown",
            "Events",
        ]
    )

    with tab_control:
        _render_mode_switcher()
        st.divider()
        _render_safety_controls()

    with tab_state:
        _render_live_governance_state(metrics)

    with tab_lockdown:
        _render_lockdown_posture()

    with tab_events:
        _render_event_bus_status()
        st.divider()
        _render_recent_events()


# Backward-compatible alias if you wire by shorter name.
def render_autonomy_control_panel(storage: Any = None) -> None:
    render_autonomous_control_panel(storage)