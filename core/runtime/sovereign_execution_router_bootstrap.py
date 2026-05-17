"""
core/runtime/sovereign_execution_router_bootstrap.py

Bootstrap layer for the Sovereign Execution Router.

Responsibilities:
- deterministic lifecycle initialization
- singleton ownership
- explicit dependency injection
- governed execution routing lifecycle wiring
- replay-safe startup ordering
- startup telemetry emission
- immutable bootstrap state exposure

IMPORTANT:
This file ONLY owns bootstrap/runtime lifecycle behavior.

It does NOT:
- execute connectors
- mutate external systems
- perform execution routing logic
- perform governance approval logic
- generate evidence documents

All routing behavior remains inside:
    sovereign_execution_router.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.sovereign_execution_router import (
    SovereignExecutionRouter,
    build_sovereign_execution_router,
)


# ============================================================
# SINGLETONS
# ============================================================

_DEFAULT_SOVEREIGN_EXECUTION_ROUTER: Optional[
    SovereignExecutionRouter
] = None

_BOOTSTRAP_LOCK = threading.RLock()


# ============================================================
# BOOTSTRAP STATE
# ============================================================

@dataclass(frozen=True)
class SovereignExecutionRouterBootstrapState:
    """
    Immutable bootstrap snapshot.
    """

    initialized: bool
    router_name: str

    event_bus_connected: bool
    operational_memory_connected: bool
    sovereign_lineage_connected: bool
    fedramp_evidence_connected: bool
    connector_execution_fabric_connected: bool

    auto_handoff_to_connector_fabric: bool
    governed_routing_mode: bool
    replay_safe_mode: bool


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_sovereign_execution_router(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
    connector_execution_fabric: Optional[Any] = None,
    auto_handoff_to_connector_fabric: bool = False,
    reset: bool = False,
    emit_startup_events: bool = True,
) -> SovereignExecutionRouter:
    """
    Deterministically bootstrap sovereign execution router.

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
            ↓
        FedRAMP evidence lineage
            ↓
        sovereign execution router

    This ensures execution routing can be:
    - memory-backed
    - lineage-backed
    - evidence-backed
    - resilience-aware
    - governed before connector fabric handoff
    """

    global _DEFAULT_SOVEREIGN_EXECUTION_ROUTER

    with _BOOTSTRAP_LOCK:

        if (
            reset
            or _DEFAULT_SOVEREIGN_EXECUTION_ROUTER is None
        ):

            _DEFAULT_SOVEREIGN_EXECUTION_ROUTER = (
                build_sovereign_execution_router(
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    lineage_engine=lineage_engine,
                    fedramp_evidence_lineage_engine=(
                        fedramp_evidence_lineage_engine
                    ),
                    connector_execution_fabric=(
                        connector_execution_fabric
                    ),
                    auto_handoff_to_connector_fabric=(
                        auto_handoff_to_connector_fabric
                    ),
                )
            )

            if emit_startup_events:
                _emit_startup_event(
                    router=_DEFAULT_SOVEREIGN_EXECUTION_ROUTER,
                    event_bus=event_bus,
                    auto_handoff_to_connector_fabric=(
                        auto_handoff_to_connector_fabric
                    ),
                )

            _log_bootstrap_summary(
                router=_DEFAULT_SOVEREIGN_EXECUTION_ROUTER,
                event_bus=event_bus,
                operational_memory_engine=(
                    operational_memory_engine
                ),
                lineage_engine=lineage_engine,
                fedramp_evidence_lineage_engine=(
                    fedramp_evidence_lineage_engine
                ),
                connector_execution_fabric=(
                    connector_execution_fabric
                ),
                auto_handoff_to_connector_fabric=(
                    auto_handoff_to_connector_fabric
                ),
            )

        return _DEFAULT_SOVEREIGN_EXECUTION_ROUTER


# ============================================================
# ACCESSORS
# ============================================================

def get_sovereign_execution_router(
    *,
    raise_if_missing: bool = True,
) -> Optional[SovereignExecutionRouter]:
    """
    Return active sovereign execution router.
    """

    router = _DEFAULT_SOVEREIGN_EXECUTION_ROUTER

    if router is None and raise_if_missing:
        raise RuntimeError(
            "Sovereign Execution Router has not been bootstrapped."
        )

    return router


def reset_sovereign_execution_router() -> None:
    """
    Reset singleton sovereign execution router.

    Useful for:
    - deterministic testing
    - isolated routing validation
    - replay scenarios
    """

    global _DEFAULT_SOVEREIGN_EXECUTION_ROUTER

    with _BOOTSTRAP_LOCK:
        _DEFAULT_SOVEREIGN_EXECUTION_ROUTER = None


# ============================================================
# STATE / SNAPSHOTS
# ============================================================

def get_sovereign_execution_router_bootstrap_state(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
    connector_execution_fabric: Optional[Any] = None,
) -> SovereignExecutionRouterBootstrapState:
    """
    Lightweight immutable bootstrap snapshot.
    """

    router = _DEFAULT_SOVEREIGN_EXECUTION_ROUTER

    if router is None:
        return SovereignExecutionRouterBootstrapState(
            initialized=False,
            router_name="UNINITIALIZED",
            event_bus_connected=False,
            operational_memory_connected=False,
            sovereign_lineage_connected=False,
            fedramp_evidence_connected=False,
            connector_execution_fabric_connected=False,
            auto_handoff_to_connector_fabric=False,
            governed_routing_mode=True,
            replay_safe_mode=True,
        )

    return SovereignExecutionRouterBootstrapState(
        initialized=True,
        router_name=router.router_name,
        event_bus_connected=(event_bus is not None),
        operational_memory_connected=(
            operational_memory_engine is not None
        ),
        sovereign_lineage_connected=(lineage_engine is not None),
        fedramp_evidence_connected=(
            fedramp_evidence_lineage_engine is not None
        ),
        connector_execution_fabric_connected=(
            connector_execution_fabric is not None
        ),
        auto_handoff_to_connector_fabric=(
            router.auto_handoff_to_connector_fabric
        ),
        governed_routing_mode=True,
        replay_safe_mode=True,
    )


# ============================================================
# INTERNALS
# ============================================================

def _emit_startup_event(
    *,
    router: SovereignExecutionRouter,
    event_bus: Optional[Any],
    auto_handoff_to_connector_fabric: bool,
) -> None:
    """
    Emit startup telemetry event.
    """

    if event_bus is None:
        return

    payload: Dict[str, Any] = {
        "event_type": "SOVEREIGN_EXECUTION_ROUTER_STARTED",
        "router_name": router.router_name,
        "auto_handoff_to_connector_fabric": (
            auto_handoff_to_connector_fabric
        ),
        "governed_routing_mode": True,
        "replay_safe_mode": True,
    }

    try:

        if hasattr(event_bus, "emit"):
            event_bus.emit(
                "SOVEREIGN_EXECUTION_ROUTER_STARTED",
                payload,
            )

        elif hasattr(event_bus, "publish"):
            event_bus.publish(
                "SOVEREIGN_EXECUTION_ROUTER_STARTED",
                payload,
            )

    except Exception as exc:
        print(
            "⚠️ Failed to emit sovereign execution router "
            f"startup event: {exc}"
        )


def _log_bootstrap_summary(
    *,
    router: SovereignExecutionRouter,
    event_bus: Optional[Any],
    operational_memory_engine: Optional[Any],
    lineage_engine: Optional[Any],
    fedramp_evidence_lineage_engine: Optional[Any],
    connector_execution_fabric: Optional[Any],
    auto_handoff_to_connector_fabric: bool,
) -> None:
    """
    Deterministic startup diagnostics.
    """

    print("\n🧠 SOVEREIGN EXECUTION ROUTER BOOTSTRAP")
    print("--------------------------------------------------")
    print(f"ROUTER: {router.router_name}")

    print(
        "EVENT BUS: "
        f"{'CONNECTED' if event_bus else 'DISCONNECTED'}"
    )

    print(
        "OPERATIONAL MEMORY: "
        f"{'CONNECTED' if operational_memory_engine else 'DISCONNECTED'}"
    )

    print(
        "SOVEREIGN LINEAGE: "
        f"{'CONNECTED' if lineage_engine else 'DISCONNECTED'}"
    )

    print(
        "FEDRAMP EVIDENCE LINEAGE: "
        f"{'CONNECTED' if fedramp_evidence_lineage_engine else 'DISCONNECTED'}"
    )

    print(
        "CONNECTOR EXECUTION FABRIC: "
        f"{'CONNECTED' if connector_execution_fabric else 'DISCONNECTED'}"
    )

    print(
        "AUTO CONNECTOR FABRIC HANDOFF: "
        f"{'ENABLED' if auto_handoff_to_connector_fabric else 'DISABLED'}"
    )

    print("GOVERNED ROUTING MODE: ENABLED")
    print("REPLAY SAFE MODE: ENABLED")
    print("STATUS: INITIALIZED")
    print("--------------------------------------------------\n")