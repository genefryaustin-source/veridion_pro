"""
core/runtime/sovereign_execution_alignment_bootstrap.py

Bootstrap layer for the Sovereign Execution Alignment Engine.

Responsibilities:
- deterministic lifecycle initialization
- singleton ownership
- inversion-of-control dependency wiring
- startup ordering enforcement
- runtime-safe dependency injection
- startup telemetry emission
- immutable bootstrap state exposure

IMPORTANT:
This file ONLY owns bootstrap/runtime lifecycle behavior.

It does NOT:
- perform execution alignment logic
- execute connectors
- mutate external systems
- contain governance logic
- contain routing logic

All alignment behavior remains inside:
    sovereign_execution_alignment_engine.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.sovereign_execution_alignment_engine import (
    AutonomyMode,
    SovereignExecutionAlignmentEngine,
    build_sovereign_execution_alignment_engine,
)


# ============================================================
# SINGLETONS
# ============================================================

_DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE: Optional[
    SovereignExecutionAlignmentEngine
] = None

_BOOTSTRAP_LOCK = threading.RLock()


# ============================================================
# BOOTSTRAP STATE
# ============================================================

@dataclass(frozen=True)
class SovereignExecutionAlignmentBootstrapState:
    """
    Immutable bootstrap snapshot.
    """

    initialized: bool
    engine_name: str
    autonomy_mode: str

    governance_connected: bool
    operational_memory_connected: bool
    lineage_connected: bool
    continuity_connected: bool
    event_bus_connected: bool


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_sovereign_execution_alignment_engine(
    *,
    autonomy_mode: str = (
        AutonomyMode.SUPERVISED_AUTONOMY.value
    ),
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    governance_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    continuity_engine: Optional[Any] = None,
    reset: bool = False,
    emit_startup_events: bool = True,
) -> SovereignExecutionAlignmentEngine:
    """
    Deterministically bootstrap sovereign execution alignment.

    Expected startup order:

        runtime cognition
            ↓
        runtime intelligence
            ↓
        mission continuity
            ↓
        operational memory
            ↓
        sovereign AI coordination
            ↓
        sovereign decision fabric
            ↓
        sovereign execution alignment

    This ensures:
    - cognition exists before alignment
    - continuity exists before survivability review
    - governance exists before approval gating
    - memory exists before lineage recording
    """

    global _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE

    with _BOOTSTRAP_LOCK:

        if (
            reset
            or (
                _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE
                is None
            )
        ):

            _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE = (
                build_sovereign_execution_alignment_engine(
                    autonomy_mode=autonomy_mode,
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    governance_engine=governance_engine,
                    lineage_engine=lineage_engine,
                    continuity_engine=continuity_engine,
                )
            )

            if emit_startup_events:
                _emit_startup_event(
                    engine=(
                        _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE
                    ),
                    event_bus=event_bus,
                    autonomy_mode=autonomy_mode,
                )

            _log_bootstrap_summary(
                engine=(
                    _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE
                ),
                autonomy_mode=autonomy_mode,
                event_bus=event_bus,
                operational_memory_engine=(
                    operational_memory_engine
                ),
                governance_engine=governance_engine,
                lineage_engine=lineage_engine,
                continuity_engine=continuity_engine,
            )

        return _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE


# ============================================================
# ACCESSORS
# ============================================================

def get_sovereign_execution_alignment_engine(
    *,
    raise_if_missing: bool = True,
) -> Optional[SovereignExecutionAlignmentEngine]:
    """
    Return active execution alignment engine.
    """

    engine = (
        _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE
    )

    if engine is None and raise_if_missing:
        raise RuntimeError(
            "Sovereign Execution Alignment Engine "
            "has not been bootstrapped."
        )

    return engine


def reset_sovereign_execution_alignment_engine() -> None:
    """
    Reset singleton execution alignment engine.

    Useful for:
    - deterministic testing
    - runtime reconstruction
    - isolated orchestration validation
    """

    global _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE

    with _BOOTSTRAP_LOCK:
        _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE = None


# ============================================================
# STATE / SNAPSHOTS
# ============================================================

def get_sovereign_execution_alignment_bootstrap_state(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    governance_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    continuity_engine: Optional[Any] = None,
) -> SovereignExecutionAlignmentBootstrapState:
    """
    Lightweight immutable bootstrap snapshot.
    """

    engine = (
        _DEFAULT_SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE
    )

    if engine is None:
        return SovereignExecutionAlignmentBootstrapState(
            initialized=False,
            engine_name="UNINITIALIZED",
            autonomy_mode="UNKNOWN",
            governance_connected=False,
            operational_memory_connected=False,
            lineage_connected=False,
            continuity_connected=False,
            event_bus_connected=False,
        )

    return SovereignExecutionAlignmentBootstrapState(
        initialized=True,
        engine_name=engine.engine_name,
        autonomy_mode=engine.autonomy_mode,
        governance_connected=(
            governance_engine is not None
        ),
        operational_memory_connected=(
            operational_memory_engine is not None
        ),
        lineage_connected=(
            lineage_engine is not None
        ),
        continuity_connected=(
            continuity_engine is not None
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
    engine: SovereignExecutionAlignmentEngine,
    event_bus: Optional[Any],
    autonomy_mode: str,
) -> None:
    """
    Emit startup telemetry event.
    """

    if event_bus is None:
        return

    payload: Dict[str, Any] = {
        "event_type": (
            "SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE_STARTED"
        ),
        "engine_name": engine.engine_name,
        "autonomy_mode": autonomy_mode,
    }

    try:

        if hasattr(event_bus, "emit"):
            event_bus.emit(
                "SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE_STARTED",
                payload,
            )

        elif hasattr(event_bus, "publish"):
            event_bus.publish(
                "SOVEREIGN_EXECUTION_ALIGNMENT_ENGINE_STARTED",
                payload,
            )

    except Exception as exc:
        print(
            "⚠️ Failed to emit sovereign execution alignment "
            f"startup event: {exc}"
        )


def _log_bootstrap_summary(
    *,
    engine: SovereignExecutionAlignmentEngine,
    autonomy_mode: str,
    event_bus: Optional[Any],
    operational_memory_engine: Optional[Any],
    governance_engine: Optional[Any],
    lineage_engine: Optional[Any],
    continuity_engine: Optional[Any],
) -> None:
    """
    Deterministic startup diagnostics.
    """

    print("\n🧠 SOVEREIGN EXECUTION ALIGNMENT BOOTSTRAP")
    print("--------------------------------------------------")
    print(f"ENGINE: {engine.engine_name}")
    print(f"AUTONOMY MODE: {autonomy_mode}")

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
        "LINEAGE ENGINE: "
        f"{'CONNECTED' if lineage_engine else 'DISCONNECTED'}"
    )

    print(
        "CONTINUITY ENGINE: "
        f"{'CONNECTED' if continuity_engine else 'DISCONNECTED'}"
    )

    print("STATUS: INITIALIZED")
    print("--------------------------------------------------\n")