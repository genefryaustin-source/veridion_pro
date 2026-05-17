"""
core/runtime/strategic_resilience_bootstrap.py

Bootstrap layer for the Strategic Resilience Engine.

Responsibilities:
- deterministic lifecycle initialization
- singleton ownership
- explicit dependency injection
- runtime-safe startup ordering
- survivability bootstrap telemetry
- immutable bootstrap state exposure

IMPORTANT:
This file ONLY owns bootstrap/runtime lifecycle behavior.

It does NOT:
- evaluate resilience posture
- execute recovery actions
- mutate autonomy state directly
- restart workers
- isolate subsystems
- execute connectors

All resilience decision logic remains inside:
    strategic_resilience_engine.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.strategic_resilience_engine import (
    StrategicResilienceEngine,
    build_strategic_resilience_engine,
)


# ============================================================
# SINGLETONS
# ============================================================

_DEFAULT_STRATEGIC_RESILIENCE_ENGINE: Optional[
    StrategicResilienceEngine
] = None

_BOOTSTRAP_LOCK = threading.RLock()


# ============================================================
# BOOTSTRAP STATE
# ============================================================

@dataclass(frozen=True)
class StrategicResilienceBootstrapState:
    """
    Immutable bootstrap snapshot.
    """

    initialized: bool
    engine_name: str

    event_bus_connected: bool
    operational_memory_connected: bool
    lineage_connected: bool

    survivability_mode_enabled: bool
    replay_safe_mode: bool


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_strategic_resilience_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    reset: bool = False,
    emit_startup_events: bool = True,
) -> StrategicResilienceEngine:
    """
    Deterministically bootstrap strategic resilience.

    Expected startup order:

        runtime cognition
            ↓
        runtime intelligence
            ↓
        mission continuity
            ↓
        sovereign operational memory
            ↓
        sovereign AI coordination
            ↓
        sovereign decision fabric
            ↓
        sovereign execution alignment
            ↓
        sovereign operational lineage
            ↓
        strategic resilience

    This ensures resilience decisions can be:
    - written to memory
    - written to lineage
    - emitted as runtime events
    - replayed for audit and governance review
    """

    global _DEFAULT_STRATEGIC_RESILIENCE_ENGINE

    with _BOOTSTRAP_LOCK:

        if (
            reset
            or (
                _DEFAULT_STRATEGIC_RESILIENCE_ENGINE
                is None
            )
        ):

            _DEFAULT_STRATEGIC_RESILIENCE_ENGINE = (
                build_strategic_resilience_engine(
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    lineage_engine=lineage_engine,
                )
            )

            if emit_startup_events:
                _emit_startup_event(
                    engine=_DEFAULT_STRATEGIC_RESILIENCE_ENGINE,
                    event_bus=event_bus,
                )

            _log_bootstrap_summary(
                engine=_DEFAULT_STRATEGIC_RESILIENCE_ENGINE,
                event_bus=event_bus,
                operational_memory_engine=(
                    operational_memory_engine
                ),
                lineage_engine=lineage_engine,
            )

        return _DEFAULT_STRATEGIC_RESILIENCE_ENGINE


# ============================================================
# ACCESSORS
# ============================================================

def get_strategic_resilience_engine(
    *,
    raise_if_missing: bool = True,
) -> Optional[StrategicResilienceEngine]:
    """
    Return active strategic resilience engine.
    """

    engine = _DEFAULT_STRATEGIC_RESILIENCE_ENGINE

    if engine is None and raise_if_missing:
        raise RuntimeError(
            "Strategic Resilience Engine has not been bootstrapped."
        )

    return engine


def reset_strategic_resilience_engine() -> None:
    """
    Reset singleton strategic resilience engine.

    Useful for:
    - deterministic testing
    - isolated runtime validation
    - resilience replay scenarios
    """

    global _DEFAULT_STRATEGIC_RESILIENCE_ENGINE

    with _BOOTSTRAP_LOCK:
        _DEFAULT_STRATEGIC_RESILIENCE_ENGINE = None


# ============================================================
# STATE / SNAPSHOTS
# ============================================================

def get_strategic_resilience_bootstrap_state(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
) -> StrategicResilienceBootstrapState:
    """
    Lightweight immutable bootstrap snapshot.
    """

    engine = _DEFAULT_STRATEGIC_RESILIENCE_ENGINE

    if engine is None:
        return StrategicResilienceBootstrapState(
            initialized=False,
            engine_name="UNINITIALIZED",
            event_bus_connected=False,
            operational_memory_connected=False,
            lineage_connected=False,
            survivability_mode_enabled=True,
            replay_safe_mode=True,
        )

    return StrategicResilienceBootstrapState(
        initialized=True,
        engine_name=engine.engine_name,
        event_bus_connected=(event_bus is not None),
        operational_memory_connected=(
            operational_memory_engine is not None
        ),
        lineage_connected=(lineage_engine is not None),
        survivability_mode_enabled=True,
        replay_safe_mode=True,
    )


# ============================================================
# INTERNALS
# ============================================================

def _emit_startup_event(
    *,
    engine: StrategicResilienceEngine,
    event_bus: Optional[Any],
) -> None:
    """
    Emit startup telemetry event.
    """

    if event_bus is None:
        return

    payload: Dict[str, Any] = {
        "event_type": "STRATEGIC_RESILIENCE_ENGINE_STARTED",
        "engine_name": engine.engine_name,
        "survivability_mode_enabled": True,
        "replay_safe_mode": True,
    }

    try:

        if hasattr(event_bus, "emit"):
            event_bus.emit(
                "STRATEGIC_RESILIENCE_ENGINE_STARTED",
                payload,
            )

        elif hasattr(event_bus, "publish"):
            event_bus.publish(
                "STRATEGIC_RESILIENCE_ENGINE_STARTED",
                payload,
            )

    except Exception as exc:
        print(
            "⚠️ Failed to emit strategic resilience startup "
            f"event: {exc}"
        )


def _log_bootstrap_summary(
    *,
    engine: StrategicResilienceEngine,
    event_bus: Optional[Any],
    operational_memory_engine: Optional[Any],
    lineage_engine: Optional[Any],
) -> None:
    """
    Deterministic startup diagnostics.
    """

    print("\n🧠 STRATEGIC RESILIENCE BOOTSTRAP")
    print("--------------------------------------------------")
    print(f"ENGINE: {engine.engine_name}")

    print(
        "EVENT BUS: "
        f"{'CONNECTED' if event_bus else 'DISCONNECTED'}"
    )

    print(
        "OPERATIONAL MEMORY: "
        f"{'CONNECTED' if operational_memory_engine else 'DISCONNECTED'}"
    )

    print(
        "LINEAGE ENGINE: "
        f"{'CONNECTED' if lineage_engine else 'DISCONNECTED'}"
    )

    print("SURVIVABILITY MODE: ENABLED")
    print("REPLAY SAFE MODE: ENABLED")
    print("STATUS: INITIALIZED")
    print("--------------------------------------------------\n")