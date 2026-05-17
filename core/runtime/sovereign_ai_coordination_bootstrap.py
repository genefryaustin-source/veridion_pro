"""
core/runtime/sovereign_ai_coordination_bootstrap.py

Bootstrap layer for sovereign AI coordination.

Responsibilities:
- deterministic startup ordering
- inversion-of-control initialization
- explicit dependency injection
- lifecycle-safe singleton management
- coordination engine ownership wiring
- startup telemetry + validation

IMPORTANT:
This file owns bootstrap/runtime lifecycle behavior ONLY.

It does NOT:
- perform cognition arbitration
- execute governance decisions
- mutate runtime orchestration logic
- contain execution behavior

All coordination behavior remains inside:
    sovereign_ai_coordination_engine.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.sovereign_ai_coordination_engine import (
    CoordinationMode,
    SovereignAICoordinationEngine,
    build_sovereign_ai_coordination_engine,
)


# ============================================================
# GLOBAL SINGLETONS
# ============================================================

_DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE: Optional[
    SovereignAICoordinationEngine
] = None

_BOOTSTRAP_LOCK = threading.RLock()


# ============================================================
# BOOTSTRAP STATE
# ============================================================

@dataclass(frozen=True)
class SovereignAICoordinationBootstrapState:
    """
    Immutable bootstrap status snapshot.
    """

    initialized: bool
    coordination_mode: str
    engine_name: str
    governance_connected: bool
    operational_memory_connected: bool
    mission_continuity_connected: bool
    runtime_cognition_connected: bool
    event_bus_connected: bool


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_sovereign_ai_coordination(
    *,
    coordination_mode: str = CoordinationMode.SUPERVISED_AUTONOMY.value,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    governance_engine: Optional[Any] = None,
    mission_continuity_engine: Optional[Any] = None,
    runtime_cognition_orchestrator: Optional[Any] = None,
    reset: bool = False,
    emit_startup_events: bool = True,
) -> SovereignAICoordinationEngine:
    """
    Deterministically bootstrap sovereign AI coordination.

    Startup ordering expectation:

        runtime cognition
            ↓
        runtime intelligence
            ↓
        mission continuity
            ↓
        sovereign operational memory
            ↓
        sovereign AI coordination

    This layer intentionally initializes AFTER cognition
    and continuity layers so coordination has complete
    situational awareness available during arbitration.
    """

    global _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE

    with _BOOTSTRAP_LOCK:

        if (
            reset
            or _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE is None
        ):

            _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE = (
                build_sovereign_ai_coordination_engine(
                    coordination_mode=coordination_mode,
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    governance_engine=governance_engine,
                    mission_continuity_engine=(
                        mission_continuity_engine
                    ),
                    runtime_cognition_orchestrator=(
                        runtime_cognition_orchestrator
                    ),
                )
            )

            if emit_startup_events:
                _emit_startup_event(
                    engine=(
                        _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE
                    ),
                    coordination_mode=coordination_mode,
                    event_bus=event_bus,
                )

            _log_bootstrap_summary(
                engine=(
                    _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE
                ),
                coordination_mode=coordination_mode,
                event_bus=event_bus,
                operational_memory_engine=(
                    operational_memory_engine
                ),
                governance_engine=governance_engine,
                mission_continuity_engine=(
                    mission_continuity_engine
                ),
                runtime_cognition_orchestrator=(
                    runtime_cognition_orchestrator
                ),
            )

        return _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE


# ============================================================
# ACCESSORS
# ============================================================

def get_sovereign_ai_coordination_engine(
    *,
    raise_if_missing: bool = True,
) -> Optional[SovereignAICoordinationEngine]:
    """
    Return active sovereign AI coordination engine.
    """

    engine = _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE

    if engine is None and raise_if_missing:
        raise RuntimeError(
            "Sovereign AI Coordination Engine "
            "has not been bootstrapped."
        )

    return engine


def reset_sovereign_ai_coordination_engine() -> None:
    """
    Reset singleton coordination engine.

    Useful for:
    - deterministic testing
    - runtime rebuilds
    - isolated orchestration validation
    """

    global _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE

    with _BOOTSTRAP_LOCK:
        _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE = None


# ============================================================
# STATUS / SNAPSHOTS
# ============================================================

def get_sovereign_ai_coordination_bootstrap_state(
    *,
    governance_engine: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    mission_continuity_engine: Optional[Any] = None,
    runtime_cognition_orchestrator: Optional[Any] = None,
    event_bus: Optional[Any] = None,
) -> SovereignAICoordinationBootstrapState:
    """
    Lightweight immutable bootstrap state snapshot.
    """

    engine = _DEFAULT_SOVEREIGN_AI_COORDINATION_ENGINE

    if engine is None:
        return SovereignAICoordinationBootstrapState(
            initialized=False,
            coordination_mode="UNKNOWN",
            engine_name="UNINITIALIZED",
            governance_connected=False,
            operational_memory_connected=False,
            mission_continuity_connected=False,
            runtime_cognition_connected=False,
            event_bus_connected=False,
        )

    return SovereignAICoordinationBootstrapState(
        initialized=True,
        coordination_mode=engine.coordination_mode,
        engine_name=engine.engine_name,
        governance_connected=(
            governance_engine is not None
        ),
        operational_memory_connected=(
            operational_memory_engine is not None
        ),
        mission_continuity_connected=(
            mission_continuity_engine is not None
        ),
        runtime_cognition_connected=(
            runtime_cognition_orchestrator is not None
        ),
        event_bus_connected=(
            event_bus is not None
        ),
    )


# ============================================================
# INTERNALS
# ============================================================

def _emit_startup_event(
    *,
    engine: SovereignAICoordinationEngine,
    coordination_mode: str,
    event_bus: Optional[Any],
) -> None:
    """
    Emit startup telemetry event.
    """

    if event_bus is None:
        return

    payload: Dict[str, Any] = {
        "event_type": (
            "SOVEREIGN_AI_COORDINATION_ENGINE_STARTED"
        ),
        "engine_name": engine.engine_name,
        "coordination_mode": coordination_mode,
    }

    try:

        if hasattr(event_bus, "emit"):
            event_bus.emit(
                "SOVEREIGN_AI_COORDINATION_ENGINE_STARTED",
                payload,
            )

        elif hasattr(event_bus, "publish"):
            event_bus.publish(
                "SOVEREIGN_AI_COORDINATION_ENGINE_STARTED",
                payload,
            )

    except Exception as exc:
        print(
            "⚠️ Failed to emit sovereign AI coordination "
            f"startup event: {exc}"
        )


def _log_bootstrap_summary(
    *,
    engine: SovereignAICoordinationEngine,
    coordination_mode: str,
    event_bus: Optional[Any],
    operational_memory_engine: Optional[Any],
    governance_engine: Optional[Any],
    mission_continuity_engine: Optional[Any],
    runtime_cognition_orchestrator: Optional[Any],
) -> None:
    """
    Deterministic startup diagnostics.
    """

    print("\n🧠 SOVEREIGN AI COORDINATION BOOTSTRAP")
    print("--------------------------------------------------")
    print(f"ENGINE: {engine.engine_name}")
    print(f"MODE: {coordination_mode}")
    print(
        "EVENT BUS: "
        f"{'CONNECTED' if event_bus else 'DISCONNECTED'}"
    )
    print(
        "OPERATIONAL MEMORY: "
        f"{'CONNECTED' if operational_memory_engine else 'DISCONNECTED'}"
    )
    print(
        "GOVERNANCE ENGINE: "
        f"{'CONNECTED' if governance_engine else 'DISCONNECTED'}"
    )
    print(
        "MISSION CONTINUITY: "
        f"{'CONNECTED' if mission_continuity_engine else 'DISCONNECTED'}"
    )
    print(
        "RUNTIME COGNITION: "
        f"{'CONNECTED' if runtime_cognition_orchestrator else 'DISCONNECTED'}"
    )
    print("STATUS: INITIALIZED")
    print("--------------------------------------------------\n")