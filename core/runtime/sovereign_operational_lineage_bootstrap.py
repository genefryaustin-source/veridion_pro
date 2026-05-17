"""
core/runtime/sovereign_operational_lineage_bootstrap.py

Bootstrap layer for the Sovereign Operational Lineage Engine.

Responsibilities:
- deterministic lifecycle initialization
- singleton ownership
- inversion-of-control dependency wiring
- append-only lineage startup guarantees
- replay-safe initialization ordering
- immutable bootstrap state exposure
- startup telemetry emission

IMPORTANT:
This file ONLY owns bootstrap/runtime lifecycle behavior.

It does NOT:
- mutate lineage history
- execute runtime actions
- perform governance decisions
- contain lineage logic
- alter operational state

All lineage behavior remains inside:
    sovereign_operational_lineage_engine.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.sovereign_operational_lineage_engine import (
    SovereignOperationalLineageEngine,
    build_sovereign_operational_lineage_engine,
)


# ============================================================
# SINGLETONS
# ============================================================

_DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE: Optional[
    SovereignOperationalLineageEngine
] = None

_BOOTSTRAP_LOCK = threading.RLock()


# ============================================================
# BOOTSTRAP STATE
# ============================================================

@dataclass(frozen=True)
class SovereignOperationalLineageBootstrapState:
    """
    Immutable bootstrap snapshot.
    """

    initialized: bool
    engine_name: str

    event_bus_connected: bool
    operational_memory_connected: bool

    append_only_mode: bool
    replay_safe_mode: bool


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_sovereign_operational_lineage_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    reset: bool = False,
    emit_startup_events: bool = True,
) -> SovereignOperationalLineageEngine:
    """
    Deterministically bootstrap sovereign operational lineage.

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

    This ordering guarantees:
    - lineage initializes AFTER cognition
    - lineage initializes AFTER coordination
    - lineage initializes AFTER alignment
    - operational memory exists before lineage persistence
    - replay-safe operational ancestry exists before execution routing
    """

    global _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE

    with _BOOTSTRAP_LOCK:

        if (
            reset
            or (
                _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE
                is None
            )
        ):

            _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE = (
                build_sovereign_operational_lineage_engine(
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                )
            )

            if emit_startup_events:
                _emit_startup_event(
                    engine=(
                        _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE
                    ),
                    event_bus=event_bus,
                )

            _log_bootstrap_summary(
                engine=(
                    _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE
                ),
                event_bus=event_bus,
                operational_memory_engine=(
                    operational_memory_engine
                ),
            )

        return _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE


# ============================================================
# ACCESSORS
# ============================================================

def get_sovereign_operational_lineage_engine(
    *,
    raise_if_missing: bool = True,
) -> Optional[SovereignOperationalLineageEngine]:
    """
    Return active sovereign operational lineage engine.
    """

    engine = (
        _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE
    )

    if engine is None and raise_if_missing:
        raise RuntimeError(
            "Sovereign Operational Lineage Engine "
            "has not been bootstrapped."
        )

    return engine


def reset_sovereign_operational_lineage_engine() -> None:
    """
    Reset singleton lineage engine.

    Useful for:
    - deterministic testing
    - isolated replay validation
    - runtime reconstruction
    """

    global _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE

    with _BOOTSTRAP_LOCK:
        _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE = None


# ============================================================
# STATE / SNAPSHOTS
# ============================================================

def get_sovereign_operational_lineage_bootstrap_state(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
) -> SovereignOperationalLineageBootstrapState:
    """
    Lightweight immutable bootstrap snapshot.
    """

    engine = (
        _DEFAULT_SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE
    )

    if engine is None:
        return SovereignOperationalLineageBootstrapState(
            initialized=False,
            engine_name="UNINITIALIZED",
            event_bus_connected=False,
            operational_memory_connected=False,
            append_only_mode=True,
            replay_safe_mode=True,
        )

    return SovereignOperationalLineageBootstrapState(
        initialized=True,
        engine_name=engine.engine_name,
        event_bus_connected=(
            event_bus is not None
        ),
        operational_memory_connected=(
            operational_memory_engine
            is not None
        ),
        append_only_mode=True,
        replay_safe_mode=True,
    )


# ============================================================
# INTERNALS
# ============================================================

def _emit_startup_event(
    *,
    engine: SovereignOperationalLineageEngine,
    event_bus: Optional[Any],
) -> None:
    """
    Emit startup telemetry event.
    """

    if event_bus is None:
        return

    payload: Dict[str, Any] = {
        "event_type": (
            "SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE_STARTED"
        ),
        "engine_name": engine.engine_name,
        "append_only_mode": True,
        "replay_safe_mode": True,
    }

    try:

        if hasattr(event_bus, "emit"):
            event_bus.emit(
                "SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE_STARTED",
                payload,
            )

        elif hasattr(event_bus, "publish"):
            event_bus.publish(
                "SOVEREIGN_OPERATIONAL_LINEAGE_ENGINE_STARTED",
                payload,
            )

    except Exception as exc:
        print(
            "⚠️ Failed to emit sovereign operational lineage "
            f"startup event: {exc}"
        )


def _log_bootstrap_summary(
    *,
    engine: SovereignOperationalLineageEngine,
    event_bus: Optional[Any],
    operational_memory_engine: Optional[Any],
) -> None:
    """
    Deterministic startup diagnostics.
    """

    print("\n🧠 SOVEREIGN OPERATIONAL LINEAGE BOOTSTRAP")
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

    print("APPEND ONLY MODE: ENABLED")
    print("REPLAY SAFE MODE: ENABLED")

    print("STATUS: INITIALIZED")
    print("--------------------------------------------------\n")
    