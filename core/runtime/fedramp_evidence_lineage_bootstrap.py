"""
core/runtime/fedramp_evidence_lineage_bootstrap.py

Bootstrap layer for the FedRAMP Evidence Lineage Engine.

Responsibilities:
- deterministic lifecycle initialization
- singleton ownership
- explicit dependency injection
- compliance evidence lifecycle wiring
- append-only evidence startup guarantees
- replay-safe initialization
- startup telemetry emission
- immutable bootstrap state exposure

IMPORTANT:
This file ONLY owns bootstrap/runtime lifecycle behavior.

It does NOT:
- generate SSP documents
- generate POA&M documents
- execute controls
- mutate evidence history
- perform connector execution
- alter operational state

All FedRAMP evidence lineage behavior remains inside:
    fedramp_evidence_lineage_engine.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.fedramp_evidence_lineage_engine import (
    FedRAMPEvidenceLineageEngine,
    build_fedramp_evidence_lineage_engine,
)


# ============================================================
# SINGLETONS
# ============================================================

_DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE: Optional[
    FedRAMPEvidenceLineageEngine
] = None

_BOOTSTRAP_LOCK = threading.RLock()


# ============================================================
# BOOTSTRAP STATE
# ============================================================

@dataclass(frozen=True)
class FedRAMPEvidenceLineageBootstrapState:
    """
    Immutable bootstrap snapshot.
    """

    initialized: bool
    engine_name: str

    event_bus_connected: bool
    operational_memory_connected: bool
    sovereign_lineage_connected: bool

    append_only_mode: bool
    replay_safe_mode: bool
    compliance_evidence_mode: bool


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_fedramp_evidence_lineage_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    reset: bool = False,
    emit_startup_events: bool = True,
) -> FedRAMPEvidenceLineageEngine:
    """
    Deterministically bootstrap FedRAMP evidence lineage.

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

    This ensures compliance evidence can be:
    - written to operational memory
    - linked to sovereign operational lineage
    - emitted as runtime telemetry
    - replayed later for SSP / POA&M support
    """

    global _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE

    with _BOOTSTRAP_LOCK:

        if (
            reset
            or (
                _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE
                is None
            )
        ):

            _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE = (
                build_fedramp_evidence_lineage_engine(
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    lineage_engine=lineage_engine,
                )
            )

            if emit_startup_events:
                _emit_startup_event(
                    engine=_DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE,
                    event_bus=event_bus,
                )

            _log_bootstrap_summary(
                engine=_DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE,
                event_bus=event_bus,
                operational_memory_engine=(
                    operational_memory_engine
                ),
                lineage_engine=lineage_engine,
            )

        return _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE


# ============================================================
# ACCESSORS
# ============================================================

def get_fedramp_evidence_lineage_engine(
    *,
    raise_if_missing: bool = True,
) -> Optional[FedRAMPEvidenceLineageEngine]:
    """
    Return active FedRAMP evidence lineage engine.
    """

    engine = _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE

    if engine is None and raise_if_missing:
        raise RuntimeError(
            "FedRAMP Evidence Lineage Engine "
            "has not been bootstrapped."
        )

    return engine


def reset_fedramp_evidence_lineage_engine() -> None:
    """
    Reset singleton FedRAMP evidence lineage engine.

    Useful for:
    - deterministic testing
    - isolated evidence-chain validation
    - compliance replay scenarios
    """

    global _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE

    with _BOOTSTRAP_LOCK:
        _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE = None


# ============================================================
# STATE / SNAPSHOTS
# ============================================================

def get_fedramp_evidence_lineage_bootstrap_state(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
) -> FedRAMPEvidenceLineageBootstrapState:
    """
    Lightweight immutable bootstrap snapshot.
    """

    engine = _DEFAULT_FEDRAMP_EVIDENCE_LINEAGE_ENGINE

    if engine is None:
        return FedRAMPEvidenceLineageBootstrapState(
            initialized=False,
            engine_name="UNINITIALIZED",
            event_bus_connected=False,
            operational_memory_connected=False,
            sovereign_lineage_connected=False,
            append_only_mode=True,
            replay_safe_mode=True,
            compliance_evidence_mode=True,
        )

    return FedRAMPEvidenceLineageBootstrapState(
        initialized=True,
        engine_name=engine.engine_name,
        event_bus_connected=(event_bus is not None),
        operational_memory_connected=(
            operational_memory_engine is not None
        ),
        sovereign_lineage_connected=(lineage_engine is not None),
        append_only_mode=True,
        replay_safe_mode=True,
        compliance_evidence_mode=True,
    )


# ============================================================
# INTERNALS
# ============================================================

def _emit_startup_event(
    *,
    engine: FedRAMPEvidenceLineageEngine,
    event_bus: Optional[Any],
) -> None:
    """
    Emit startup telemetry event.
    """

    if event_bus is None:
        return

    payload: Dict[str, Any] = {
        "event_type": "FEDRAMP_EVIDENCE_LINEAGE_ENGINE_STARTED",
        "engine_name": engine.engine_name,
        "append_only_mode": True,
        "replay_safe_mode": True,
        "compliance_evidence_mode": True,
    }

    try:

        if hasattr(event_bus, "emit"):
            event_bus.emit(
                "FEDRAMP_EVIDENCE_LINEAGE_ENGINE_STARTED",
                payload,
            )

        elif hasattr(event_bus, "publish"):
            event_bus.publish(
                "FEDRAMP_EVIDENCE_LINEAGE_ENGINE_STARTED",
                payload,
            )

    except Exception as exc:
        print(
            "⚠️ Failed to emit FedRAMP evidence lineage "
            f"startup event: {exc}"
        )


def _log_bootstrap_summary(
    *,
    engine: FedRAMPEvidenceLineageEngine,
    event_bus: Optional[Any],
    operational_memory_engine: Optional[Any],
    lineage_engine: Optional[Any],
) -> None:
    """
    Deterministic startup diagnostics.
    """

    print("\n🧠 FEDRAMP EVIDENCE LINEAGE BOOTSTRAP")
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
        "SOVEREIGN LINEAGE: "
        f"{'CONNECTED' if lineage_engine else 'DISCONNECTED'}"
    )

    print("APPEND ONLY MODE: ENABLED")
    print("REPLAY SAFE MODE: ENABLED")
    print("COMPLIANCE EVIDENCE MODE: ENABLED")
    print("STATUS: INITIALIZED")
    print("--------------------------------------------------\n")