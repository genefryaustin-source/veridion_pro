"""
core/runtime/sovereign_runtime_telemetry_bus.py

Sovereign Runtime Telemetry Bus

Real-time sovereign runtime nervous system.

This subsystem:
- streams sovereign runtime telemetry
- fuses cross-engine operational signals
- synchronizes distributed runtime fabrics
- propagates governance telemetry
- propagates verification telemetry
- propagates adaptive learning telemetry
- propagates policy evolution telemetry
- produces replayable telemetry lineage

This becomes:

living sovereign runtime intelligence
"""

from __future__ import annotations

import queue
import statistics
import threading
import time
import uuid

from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional


DEFAULT_BUS_NAME = (
    "sovereign_runtime_telemetry_bus"
)

DEFAULT_HISTORY_SIZE = 5000

DEFAULT_STREAM_RETENTION = 1000


# ==========================================================
# TELEMETRY TYPES
# ==========================================================

TELEMETRY_TYPE_GOVERNANCE = (
    "GOVERNANCE"
)

TELEMETRY_TYPE_VERIFICATION = (
    "VERIFICATION"
)

TELEMETRY_TYPE_ADAPTIVE = (
    "ADAPTIVE"
)

TELEMETRY_TYPE_POLICY = (
    "POLICY"
)

TELEMETRY_TYPE_ORCHESTRATION = (
    "ORCHESTRATION"
)

TELEMETRY_TYPE_SURVIVABILITY = (
    "SURVIVABILITY"
)

TELEMETRY_TYPE_RESILIENCE = (
    "RESILIENCE"
)

TELEMETRY_TYPE_SOVEREIGNTY = (
    "SOVEREIGNTY"
)

TELEMETRY_TYPE_RUNTIME = (
    "RUNTIME"
)

TELEMETRY_TYPE_EXECUTION = (
    "EXECUTION"
)


class TelemetrySeverity(str, Enum):

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ==========================================================
# TELEMETRY EVENT
# ==========================================================

@dataclass(frozen=True)
class SovereignTelemetryEvent:

    event_id: str

    telemetry_type: str

    source_engine: str

    severity: str

    summary: str

    confidence: float = 1.0

    governance_score: float = 100.0
    survivability_score: float = 100.0
    resilience_score: float = 100.0
    continuity_score: float = 100.0
    sovereignty_score: float = 100.0

    blast_radius_score: float = 0.0
    governance_drift_score: float = 0.0
    escalation_pressure_score: float = 0.0
    uncertainty_score: float = 0.0

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


# ==========================================================
# FUSION SNAPSHOT
# ==========================================================

@dataclass(frozen=True)
class SovereignTelemetryFusionSnapshot:

    snapshot_id: str

    governance_posture: float
    survivability_posture: float
    resilience_posture: float
    continuity_posture: float
    sovereignty_posture: float

    governance_drift: float
    escalation_pressure: float
    uncertainty_score: float

    systemic_risk_probability: float

    signal_count: int

    telemetry_types: List[str]

    rationale: str

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


# ==========================================================
# TELEMETRY STREAM
# ==========================================================

@dataclass
class SovereignTelemetryStream:

    stream_name: str

    subscribers: List[
        Callable[[SovereignTelemetryEvent], None]
    ] = field(default_factory=list)

    events: Deque[
        SovereignTelemetryEvent
    ] = field(
        default_factory=lambda: deque(
            maxlen=DEFAULT_STREAM_RETENTION
        )
    )


# ==========================================================
# TELEMETRY BUS
# ==========================================================

class SovereignRuntimeTelemetryBus:
    """
    Sovereign runtime nervous system.
    """

    def __init__(
        self,
        *,
        bus_name: str = (
            DEFAULT_BUS_NAME
        ),
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[
            Any
        ] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[
            Any
        ] = None,
    ) -> None:

        self.bus_name = bus_name

        self.event_bus = event_bus

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._streams: Dict[
            str,
            SovereignTelemetryStream,
        ] = {}

        self._history: Deque[
            SovereignTelemetryEvent
        ] = deque(
            maxlen=DEFAULT_HISTORY_SIZE
        )

        self._fusion_history: Deque[
            SovereignTelemetryFusionSnapshot
        ] = deque(
            maxlen=1000
        )

        self._runtime_fabrics: Dict[
            str,
            Dict[str, Any],
        ] = {}

        self._event_queue: (
            queue.Queue[
                SovereignTelemetryEvent
            ]
        ) = queue.Queue()

        self._running = False

        self._worker_thread: Optional[
            threading.Thread
        ] = None

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def start(self) -> None:

        if self._running:
            return

        self._running = True

        self._worker_thread = (
            threading.Thread(
                target=self._worker_loop,
                daemon=True,
            )
        )

        self._worker_thread.start()

        print(
            "🌐 Sovereign Runtime Telemetry Bus ONLINE."
        )

    def stop(self) -> None:

        self._running = False

        print(
            "🛑 Sovereign Runtime Telemetry Bus OFFLINE."
        )

    # ======================================================
    # STREAMS
    # ======================================================

    def register_stream(
        self,
        stream_name: str,
    ) -> None:

        if stream_name not in self._streams:

            self._streams[
                stream_name
            ] = SovereignTelemetryStream(
                stream_name=stream_name
            )

            print(
                f"📡 Telemetry stream "
                f"registered: {stream_name}"
            )

    def subscribe(
        self,
        stream_name: str,
        callback: Callable[
            [SovereignTelemetryEvent],
            None,
        ],
    ) -> None:

        self.register_stream(
            stream_name
        )

        self._streams[
            stream_name
        ].subscribers.append(
            callback
        )

    # ======================================================
    # TELEMETRY INGESTION
    # ======================================================

    def publish(
        self,
        telemetry_event: (
            SovereignTelemetryEvent
            | Dict[str, Any]
        ),
    ) -> SovereignTelemetryEvent:

        normalized = (
            self._normalize_event(
                telemetry_event
            )
        )

        self._history.append(
            normalized
        )

        self._event_queue.put(
            normalized
        )

        self._record_lineage(
            normalized
        )

        self._record_memory(
            normalized
        )

        self._record_evidence(
            normalized
        )

        self._emit_platform_event(
            normalized
        )

        return normalized

    # ======================================================
    # FUSION
    # ======================================================

    def build_fusion_snapshot(
        self,
    ) -> (
        SovereignTelemetryFusionSnapshot
    ):

        history = list(
            self._history
        )

        if not history:

            snapshot = (
                SovereignTelemetryFusionSnapshot(
                    snapshot_id=str(
                        uuid.uuid4()
                    ),
                    governance_posture=100.0,
                    survivability_posture=100.0,
                    resilience_posture=100.0,
                    continuity_posture=100.0,
                    sovereignty_posture=100.0,
                    governance_drift=0.0,
                    escalation_pressure=0.0,
                    uncertainty_score=0.0,
                    systemic_risk_probability=0.0,
                    signal_count=0,
                    telemetry_types=[],
                    rationale=(
                        "No telemetry "
                        "events available."
                    ),
                )
            )

            self._fusion_history.append(
                snapshot
            )

            return snapshot

        governance_posture = (
            self._avg_score(
                [
                    e.governance_score
                    for e in history
                ]
            )
        )

        survivability_posture = (
            self._avg_score(
                [
                    e
                    .survivability_score
                    for e in history
                ]
            )
        )

        resilience_posture = (
            self._avg_score(
                [
                    e.resilience_score
                    for e in history
                ]
            )
        )

        continuity_posture = (
            self._avg_score(
                [
                    e.continuity_score
                    for e in history
                ]
            )
        )

        sovereignty_posture = (
            self._avg_score(
                [
                    e.sovereignty_score
                    for e in history
                ]
            )
        )

        governance_drift = (
            self._avg_score(
                [
                    e
                    .governance_drift_score
                    for e in history
                ]
            )
        )

        escalation_pressure = (
            self._avg_score(
                [
                    e
                    .escalation_pressure_score
                    for e in history
                ]
            )
        )

        uncertainty = (
            self._avg_score(
                [
                    e.uncertainty_score
                    for e in history
                ]
            )
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                governance_drift=(
                    governance_drift
                ),
                escalation_pressure=(
                    escalation_pressure
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        snapshot = (
            SovereignTelemetryFusionSnapshot(
                snapshot_id=str(
                    uuid.uuid4()
                ),
                governance_posture=(
                    governance_posture
                ),
                survivability_posture=(
                    survivability_posture
                ),
                resilience_posture=(
                    resilience_posture
                ),
                continuity_posture=(
                    continuity_posture
                ),
                sovereignty_posture=(
                    sovereignty_posture
                ),
                governance_drift=(
                    governance_drift
                ),
                escalation_pressure=(
                    escalation_pressure
                ),
                uncertainty_score=(
                    uncertainty
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                signal_count=len(
                    history
                ),
                telemetry_types=sorted(
                    {
                        e.telemetry_type
                        for e in history
                    }
                ),
                rationale=(
                    "Cross-engine sovereign "
                    "telemetry fusion generated."
                ),
            )
        )

        self._fusion_history.append(
            snapshot
        )

        return snapshot

    # ======================================================
    # DISTRIBUTED SYNCHRONIZATION
    # ======================================================

    def register_runtime_fabric(
        self,
        fabric_id: str,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._runtime_fabrics[
            fabric_id
        ] = {

            "fabric_id": fabric_id,

            "metadata": (
                metadata or {}
            ),

            "registered_at_ms": int(
                time.time() * 1000
            ),
        }

        print(
            f"🛰️ Runtime fabric "
            f"registered: {fabric_id}"
        )

    def synchronize_runtime_state(
        self,
    ) -> Dict[str, Any]:

        snapshot = (
            self.build_fusion_snapshot()
        )

        return {

            "runtime_fabric_count": len(
                self._runtime_fabrics
            ),

            "governance_posture": (
                snapshot
                .governance_posture
            ),

            "survivability_posture": (
                snapshot
                .survivability_posture
            ),

            "resilience_posture": (
                snapshot
                .resilience_posture
            ),

            "continuity_posture": (
                snapshot
                .continuity_posture
            ),

            "sovereignty_posture": (
                snapshot
                .sovereignty_posture
            ),

            "systemic_risk_probability": (
                snapshot
                .systemic_risk_probability
            ),
        }

    # ======================================================
    # WORKER LOOP
    # ======================================================

    def _worker_loop(
        self,
    ) -> None:

        while self._running:

            try:

                event = (
                    self._event_queue.get(
                        timeout=0.5
                    )
                )

                self._dispatch_event(
                    event
                )

            except queue.Empty:

                continue

            except Exception as exc:

                print(
                    f"⚠️ Telemetry bus "
                    f"worker error: {exc}"
                )

    def _dispatch_event(
        self,
        event: SovereignTelemetryEvent,
    ) -> None:

        stream_name = (
            event.telemetry_type
        )

        self.register_stream(
            stream_name
        )

        stream = self._streams[
            stream_name
        ]

        stream.events.append(
            event
        )

        for subscriber in list(
            stream.subscribers
        ):

            try:

                subscriber(event)

            except Exception as exc:

                print(
                    f"⚠️ Telemetry subscriber "
                    f"error: {exc}"
                )

    # ======================================================
    # RECORDING
    # ======================================================

    def _record_memory(
        self,
        event: SovereignTelemetryEvent,
    ) -> None:

        try:

            if (
                self
                .operational_memory_engine
                and hasattr(
                    self
                    .operational_memory_engine,
                    "append_memory",
                )
            ):

                self.operational_memory_engine.append_memory(
                    {
                        "type": (
                            "SOVEREIGN_TELEMETRY"
                        ),
                        "event": asdict(
                            event
                        ),
                    }
                )

        except Exception as exc:

            print(
                f"⚠️ Telemetry memory "
                f"write failed: {exc}"
            )

    def _record_lineage(
        self,
        event: SovereignTelemetryEvent,
    ) -> None:

        try:

            if (
                self.lineage_engine
                and hasattr(
                    self.lineage_engine,
                    "record_lineage",
                )
            ):

                self.lineage_engine.record_lineage(
                    {
                        "type": (
                            "SOVEREIGN_TELEMETRY"
                        ),
                        "event": asdict(
                            event
                        ),
                    }
                )

        except Exception as exc:

            print(
                f"⚠️ Telemetry lineage "
                f"write failed: {exc}"
            )

    def _record_evidence(
        self,
        event: SovereignTelemetryEvent,
    ) -> None:

        try:

            if (
                self
                .fedramp_evidence_lineage_engine
                and hasattr(
                    self.fedramp_evidence_lineage_engine,
                    "record_evidence",
                )
            ):

                self.fedramp_evidence_lineage_engine.record_evidence(
                    {
                        "type": (
                            "SOVEREIGN_TELEMETRY"
                        ),
                        "event": asdict(
                            event
                        ),
                    }
                )

        except Exception as exc:

            print(
                f"⚠️ Telemetry evidence "
                f"write failed: {exc}"
            )

    def _emit_platform_event(
        self,
        event: SovereignTelemetryEvent,
    ) -> None:

        try:

            if (
                self.event_bus
                and hasattr(
                    self.event_bus,
                    "emit",
                )
            ):

                self.event_bus.emit(
                    "SOVEREIGN_RUNTIME_TELEMETRY",
                    asdict(event),
                )

        except Exception as exc:

            print(
                f"⚠️ Telemetry platform "
                f"event failed: {exc}"
            )

    # ======================================================
    # HELPERS
    # ======================================================

    def get_stream_events(
        self,
        stream_name: str,
    ) -> List[
        SovereignTelemetryEvent
    ]:

        if stream_name not in self._streams:
            return []

        return list(
            self._streams[
                stream_name
            ].events
        )

    def get_recent_events(
        self,
        limit: int = 100,
    ) -> List[
        SovereignTelemetryEvent
    ]:

        return list(
            self._history
        )[-limit:]

    def get_fusion_history(
        self,
        limit: int = 100,
    ) -> List[
        SovereignTelemetryFusionSnapshot
    ]:

        return list(
            self._fusion_history
        )[-limit:]

    # ======================================================
    # NORMALIZATION
    # ======================================================

    def _normalize_event(
        self,
        item: (
            SovereignTelemetryEvent
            | Dict[str, Any]
        ),
    ) -> SovereignTelemetryEvent:

        if isinstance(
            item,
            SovereignTelemetryEvent,
        ):
            return item

        return SovereignTelemetryEvent(

            event_id=str(
                item.get(
                    "event_id"
                )
                or uuid.uuid4()
            ),

            telemetry_type=str(
                item.get(
                    "telemetry_type",
                    TELEMETRY_TYPE_RUNTIME,
                )
            ),

            source_engine=str(
                item.get(
                    "source_engine",
                    "unknown_engine",
                )
            ),

            severity=self._safe_severity(
                item.get(
                    "severity"
                )
            ),

            summary=str(
                item.get(
                    "summary",
                    "",
                )
            ),

            confidence=self._clamp_probability(
                item.get(
                    "confidence",
                    1.0,
                )
            ),

            governance_score=self._clamp_score(
                item.get(
                    "governance_score",
                    100.0,
                )
            ),

            survivability_score=self._clamp_score(
                item.get(
                    "survivability_score",
                    100.0,
                )
            ),

            resilience_score=self._clamp_score(
                item.get(
                    "resilience_score",
                    100.0,
                )
            ),

            continuity_score=self._clamp_score(
                item.get(
                    "continuity_score",
                    100.0,
                )
            ),

            sovereignty_score=self._clamp_score(
                item.get(
                    "sovereignty_score",
                    100.0,
                )
            ),

            blast_radius_score=self._clamp_score(
                item.get(
                    "blast_radius_score",
                    0.0,
                )
            ),

            governance_drift_score=self._clamp_score(
                item.get(
                    "governance_drift_score",
                    0.0,
                )
            ),

            escalation_pressure_score=self._clamp_score(
                item.get(
                    "escalation_pressure_score",
                    0.0,
                )
            ),

            uncertainty_score=self._clamp_score(
                item.get(
                    "uncertainty_score",
                    0.0,
                )
            ),

            tenant_id=item.get(
                "tenant_id"
            ),

            mission_id=item.get(
                "mission_id"
            ),

            case_id=item.get(
                "case_id"
            ),

            correlation_id=item.get(
                "correlation_id"
            ),

            payload=dict(
                item.get(
                    "payload",
                    {},
                )
                or {}
            ),
        )

    # ======================================================
    # RISK
    # ======================================================

    def _systemic_risk_probability(
        self,
        *,
        governance_drift: float,
        escalation_pressure: float,
        uncertainty_score: float,
    ) -> float:

        value = (
            governance_drift
            + escalation_pressure
            + uncertainty_score
        ) / 300.0

        return self._clamp_probability(
            value
        )

    # ======================================================
    # UTILS
    # ======================================================

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or TelemetrySeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in TelemetrySeverity
        }

        return (
            value
            if value in valid
            else TelemetrySeverity.INFO.value
        )

    @staticmethod
    def _clamp_score(
        value: Any,
    ) -> float:

        try:
            value = float(value)

        except Exception:
            value = 0.0

        return max(
            0.0,
            min(100.0, value),
        )

    @staticmethod
    def _clamp_probability(
        value: Any,
    ) -> float:

        try:
            value = float(value)

        except Exception:
            value = 0.0

        return max(
            0.0,
            min(1.0, value),
        )

    def _avg_score(
        self,
        values: List[float],
    ) -> float:

        if not values:
            return 0.0

        return self._clamp_score(
            statistics.mean(values)
        )


# ==========================================================
# FACTORY
# ==========================================================

def build_sovereign_runtime_telemetry_bus(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignRuntimeTelemetryBus:

    bus = SovereignRuntimeTelemetryBus(
        event_bus=event_bus,
        operational_memory_engine=(
            operational_memory_engine
        ),
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=(
            fedramp_evidence_lineage_engine
        ),
    )

    bus.start()

    return bus