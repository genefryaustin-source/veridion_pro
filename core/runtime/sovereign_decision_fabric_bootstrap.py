"""
core/runtime/sovereign_decision_fabric_bootstrap.py

Bootstrap layer for the Sovereign Decision Fabric.

Responsibilities:
- deterministic lifecycle initialization
- explicit dependency injection
- singleton ownership
- runtime-safe bootstrap ordering
- startup diagnostics + telemetry
- inversion-of-control enforcement

IMPORTANT:
This file owns ONLY lifecycle/bootstrap behavior.

It does NOT:
- execute connectors
- perform sovereign arbitration
- perform governance decisions
- mutate runtime execution state
- contain routing logic

All routing behavior remains inside:
    sovereign_decision_fabric.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.sovereign_decision_fabric import (
    SovereignDecisionFabric,
    build_sovereign_decision_fabric,
)


# ============================================================
# SINGLETONS
# ============================================================

_DEFAULT_SOVEREIGN_DECISION_FABRIC: Optional[
    SovereignDecisionFabric
] = None

_BOOTSTRAP_LOCK = threading.RLock()


# ============================================================
# BOOTSTRAP STATE
# ============================================================

@dataclass(frozen=True)
class SovereignDecisionFabricBootstrapState:
    """
    Immutable bootstrap snapshot.
    """

    initialized: bool
    fabric_name: str

    governance_connected: bool
    operational_memory_connected: bool
    lineage_connected: bool
    execution_alignment_connected: bool
    event_bus_connected: bool


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_sovereign_decision_fabric(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    governance_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    execution_alignment_engine: Optional[Any] = None,
    reset: bool = False,
    emit_startup_events: bool = True,
) -> SovereignDecisionFabric:
    """
    Deterministically bootstrap sovereign decision fabric.

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

    This ordering ensures:
    - cognition already exists
    - continuity already exists
    - memory already exists
    - coordination already exists
    before routing/handoff orchestration begins.
    """

    global _DEFAULT_SOVEREIGN_DECISION_FABRIC

    with _BOOTSTRAP_LOCK:

        if (
            reset
            or _DEFAULT_SOVEREIGN_DECISION_FABRIC is None
        ):

            _DEFAULT_SOVEREIGN_DECISION_FABRIC = (
                build_sovereign_decision_fabric(
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    governance_engine=governance_engine,
                    lineage_engine=lineage_engine,
                    execution_alignment_engine=(
                        execution_alignment_engine
                    ),
                )
            )

            if emit_startup_events:
                _emit_startup_event(
                    fabric=(
                        _DEFAULT_SOVEREIGN_DECISION_FABRIC
                    ),
                    event_bus=event_bus,
                )

            _log_bootstrap_summary(
                fabric=(
                    _DEFAULT_SOVEREIGN_DECISION_FABRIC
                ),
                event_bus=event_bus,
                operational_memory_engine=(
                    operational_memory_engine
                ),
                governance_engine=governance_engine,
                lineage_engine=lineage_engine,
                execution_alignment_engine=(
                    execution_alignment_engine
                ),
            )

        return _DEFAULT_SOVEREIGN_DECISION_FABRIC


# ============================================================
# ACCESSORS
# ============================================================

def get_sovereign_decision_fabric(
    *,
    raise_if_missing: bool = True,
) -> Optional[SovereignDecisionFabric]:
    """
    Return active sovereign decision fabric.
    """

    fabric = _DEFAULT_SOVEREIGN_DECISION_FABRIC

    if fabric is None and raise_if_missing:
        raise RuntimeError(
            "Sovereign Decision Fabric "
            "has not been bootstrapped."
        )

    return fabric


def reset_sovereign_decision_fabric() -> None:
    """
    Reset singleton fabric.

    Useful for:
    - deterministic testing
    - isolated runtime validation
    - orchestration rebuilds
    """

    global _DEFAULT_SOVEREIGN_DECISION_FABRIC

    with _BOOTSTRAP_LOCK:
        _DEFAULT_SOVEREIGN_DECISION_FABRIC = None


# ============================================================
# STATE / SNAPSHOTS
# ============================================================

def get_sovereign_decision_fabric_bootstrap_state(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    governance_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    execution_alignment_engine: Optional[Any] = None,
) -> SovereignDecisionFabricBootstrapState:
    """
    Lightweight immutable bootstrap state.
    """

    fabric = _DEFAULT_SOVEREIGN_DECISION_FABRIC

    if fabric is None:
        return SovereignDecisionFabricBootstrapState(
            initialized=False,
            fabric_name="UNINITIALIZED",
            governance_connected=False,
            operational_memory_connected=False,
            lineage_connected=False,
            execution_alignment_connected=False,
            event_bus_connected=False,
        )

    return SovereignDecisionFabricBootstrapState(
        initialized=True,
        fabric_name=fabric.fabric_name,
        governance_connected=(
            governance_engine is not None
        ),
        operational_memory_connected=(
            operational_memory_engine is not None
        ),
        lineage_connected=(
            lineage_engine is not None
        ),
        execution_alignment_connected=(
            execution_alignment_engine is not None
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
    fabric: SovereignDecisionFabric,
    event_bus: Optional[Any],
) -> None:
    """
    Emit startup telemetry.
    """

    if event_bus is None:
        return

    payload: Dict[str, Any] = {
        "event_type": (
            "SOVEREIGN_DECISION_FABRIC_STARTED"
        ),
        "fabric_name": fabric.fabric_name,
    }

    try:

        if hasattr(event_bus, "emit"):
            event_bus.emit(
                "SOVEREIGN_DECISION_FABRIC_STARTED",
                payload,
            )

        elif hasattr(event_bus, "publish"):
            event_bus.publish(
                "SOVEREIGN_DECISION_FABRIC_STARTED",
                payload,
            )

    except Exception as exc:
        print(
            "⚠️ Failed to emit sovereign decision fabric "
            f"startup event: {exc}"
        )


def _log_bootstrap_summary(
    *,
    fabric: SovereignDecisionFabric,
    event_bus: Optional[Any],
    operational_memory_engine: Optional[Any],
    governance_engine: Optional[Any],
    lineage_engine: Optional[Any],
    execution_alignment_engine: Optional[Any],
) -> None:
    """
    Deterministic startup diagnostics.
    """

    print("\n🧠 SOVEREIGN DECISION FABRIC BOOTSTRAP")
    print("--------------------------------------------------")
    print(f"FABRIC: {fabric.fabric_name}")

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
        "EXECUTION ALIGNMENT: "
        f"{'CONNECTED' if execution_alignment_engine else 'DISCONNECTED'}"
    )

    print("STATUS: INITIALIZED")
    print("--------------------------------------------------\n")