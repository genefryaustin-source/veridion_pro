"""
core/runtime/sovereign_operational_lineage_engine.py

Sovereign Operational Lineage Engine

Replayable sovereign operational provenance layer.

This engine records immutable, append-only lineage events that explain:

- why decisions occurred
- what influenced those decisions
- what governance posture existed
- what approvals/constraints existed
- what alignment analysis existed
- what rollback requirements existed
- what continuity considerations existed

IMPORTANT:
This engine DOES NOT:
- execute actions
- mutate prior lineage history
- alter operational state
- call external connectors

This engine ONLY:
- records lineage
- links ancestry
- preserves provenance
- emits replayable governance history
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_ENGINE_NAME = "sovereign_operational_lineage_engine"

LINEAGE_TYPE_COGNITION = "COGNITION"
LINEAGE_TYPE_COORDINATION = "COORDINATION"
LINEAGE_TYPE_DECISION = "DECISION"
LINEAGE_TYPE_ALIGNMENT = "ALIGNMENT"
LINEAGE_TYPE_GOVERNANCE = "GOVERNANCE"
LINEAGE_TYPE_EXECUTION = "EXECUTION"
LINEAGE_TYPE_ROLLBACK = "ROLLBACK"
LINEAGE_TYPE_CONTINUITY = "CONTINUITY"
LINEAGE_TYPE_VERIFICATION = "VERIFICATION"
LINEAGE_TYPE_EVIDENCE = "EVIDENCE"
LINEAGE_TYPE_COMPLIANCE = "COMPLIANCE"

RELATIONSHIP_PARENT = "PARENT"
RELATIONSHIP_CHILD = "CHILD"
RELATIONSHIP_INFLUENCED_BY = "INFLUENCED_BY"
RELATIONSHIP_APPROVED_BY = "APPROVED_BY"
RELATIONSHIP_CONSTRAINED_BY = "CONSTRAINED_BY"
RELATIONSHIP_VERIFIED_BY = "VERIFIED_BY"
RELATIONSHIP_ESCALATED_BY = "ESCALATED_BY"
RELATIONSHIP_SUPERSEDES = "SUPERSEDES"


# ============================================================
# ENUMS
# ============================================================

class LineageSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LineageStatus(str, Enum):
    RECORDED = "RECORDED"
    VERIFIED = "VERIFIED"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class SovereignLineageRelationship:
    """
    Relationship edge between lineage events.
    """

    relationship_id: str
    relationship_type: str
    source_event_id: str
    target_event_id: str
    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class SovereignOperationalLineageEvent:
    """
    Immutable append-only lineage event.
    """

    lineage_event_id: str
    lineage_type: str
    lineage_status: str

    source_engine: str
    summary: str

    severity: str
    confidence: float
    mission_priority: int

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    parent_event_ids: List[str] = field(default_factory=list)

    constraints: List[str] = field(default_factory=list)
    approvals: List[str] = field(default_factory=list)
    verification_requirements: List[str] = field(default_factory=list)

    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class SovereignOperationalLineageSnapshot:
    """
    Runtime diagnostics snapshot.
    """

    engine_name: str
    total_lineage_events: int
    total_relationships: int
    last_event_id: Optional[str]
    last_event_type: Optional[str]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class SovereignOperationalLineageEngine:
    """
    Immutable replayable sovereign lineage engine.

    Design guarantees:
    - append-only lineage
    - deterministic provenance recording
    - explicit dependency injection
    - immutable lineage event storage
    - replay-safe operational ancestry
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name

        self.event_bus = event_bus
        self.operational_memory_engine = (
            operational_memory_engine
        )

        self._events: List[
            SovereignOperationalLineageEvent
        ] = []

        self._relationships: List[
            SovereignLineageRelationship
        ] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def record_lineage(
        self,
        event: (
            SovereignOperationalLineageEvent
            | Dict[str, Any]
        ),
    ) -> SovereignOperationalLineageEvent:
        """
        Record immutable lineage event.
        """

        normalized = self._normalize_event(event)

        # ----------------------------------------------------
        # APPEND ONLY
        # ----------------------------------------------------

        self._events.append(normalized)

        # ----------------------------------------------------
        # RELATIONSHIP GRAPH
        # ----------------------------------------------------

        self._create_parent_relationships(normalized)

        # ----------------------------------------------------
        # MEMORY + EVENT EMISSION
        # ----------------------------------------------------

        self._write_to_operational_memory(normalized)
        self._emit_lineage_event(normalized)

        return normalized

    def append_lineage(
        self,
        event: (
            SovereignOperationalLineageEvent
            | Dict[str, Any]
        ),
    ) -> SovereignOperationalLineageEvent:
        """
        Alias for append-only semantics.
        """

        return self.record_lineage(event)

    def create_lineage_event(
        self,
        *,
        lineage_type: str,
        source_engine: str,
        summary: str,
        severity: str,
        confidence: float,
        mission_priority: int,
        lineage_status: str = (
            LineageStatus.RECORDED.value
        ),
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        parent_event_ids: Optional[
            Sequence[str]
        ] = None,
        constraints: Optional[
            Sequence[str]
        ] = None,
        approvals: Optional[
            Sequence[str]
        ] = None,
        verification_requirements: Optional[
            Sequence[str]
        ] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SovereignOperationalLineageEvent:
        """
        Create immutable lineage event.
        """

        return SovereignOperationalLineageEvent(
            lineage_event_id=str(uuid.uuid4()),
            lineage_type=self._safe_lineage_type(
                lineage_type
            ),
            lineage_status=self._safe_lineage_status(
                lineage_status
            ),
            source_engine=source_engine or "unknown_engine",
            summary=summary or "",
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            mission_priority=max(
                0,
                int(mission_priority),
            ),
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            parent_event_ids=list(parent_event_ids or []),
            constraints=list(constraints or []),
            approvals=list(approvals or []),
            verification_requirements=list(
                verification_requirements or []
            ),
            context=dict(context or {}),
            metadata=dict(metadata or {}),
        )

    def get_lineage_event(
        self,
        lineage_event_id: str,
    ) -> Optional[SovereignOperationalLineageEvent]:
        """
        Retrieve lineage event by ID.
        """

        for item in self._events:
            if item.lineage_event_id == lineage_event_id:
                return item

        return None

    def get_lineage_chain(
        self,
        lineage_event_id: str,
    ) -> List[SovereignOperationalLineageEvent]:
        """
        Retrieve ancestry chain recursively.
        """

        result: List[
            SovereignOperationalLineageEvent
        ] = []

        visited = set()

        def walk(event_id: str) -> None:

            if event_id in visited:
                return

            visited.add(event_id)

            item = self.get_lineage_event(event_id)

            if item is None:
                return

            result.append(item)

            for parent_id in item.parent_event_ids:
                walk(parent_id)

        walk(lineage_event_id)

        return result

    def get_relationships(
        self,
        lineage_event_id: Optional[str] = None,
    ) -> List[SovereignLineageRelationship]:
        """
        Retrieve lineage relationships.
        """

        if lineage_event_id is None:
            return list(self._relationships)

        return [
            rel
            for rel in self._relationships
            if (
                rel.source_event_id == lineage_event_id
                or rel.target_event_id
                == lineage_event_id
            )
        ]

    def get_recent_events(
        self,
        *,
        limit: int = 50,
    ) -> List[SovereignOperationalLineageEvent]:
        """
        Return recent lineage events newest-first.
        """

        limit = max(1, int(limit))

        return list(
            reversed(self._events[-limit:])
        )

    def snapshot(
        self,
    ) -> SovereignOperationalLineageSnapshot:
        """
        Lightweight diagnostics snapshot.
        """

        last = self._events[-1] if self._events else None

        return SovereignOperationalLineageSnapshot(
            engine_name=self.engine_name,
            total_lineage_events=len(self._events),
            total_relationships=len(
                self._relationships
            ),
            last_event_id=(
                last.lineage_event_id
                if last
                else None
            ),
            last_event_type=(
                last.lineage_type
                if last
                else None
            ),
            last_updated_ms=int(
                time.time() * 1000
            ),
        )

    # --------------------------------------------------------
    # RELATIONSHIP GRAPH
    # --------------------------------------------------------

    def create_relationship(
        self,
        *,
        relationship_type: str,
        source_event_id: str,
        target_event_id: str,
    ) -> SovereignLineageRelationship:
        """
        Create immutable lineage relationship edge.
        """

        relationship = (
            SovereignLineageRelationship(
                relationship_id=str(uuid.uuid4()),
                relationship_type=(
                    relationship_type
                ),
                source_event_id=source_event_id,
                target_event_id=target_event_id,
            )
        )

        self._relationships.append(
            relationship
        )

        return relationship

    def _create_parent_relationships(
        self,
        event: SovereignOperationalLineageEvent,
    ) -> None:
        """
        Automatically generate ancestry edges.
        """

        for parent_id in event.parent_event_ids:

            self.create_relationship(
                relationship_type=(
                    RELATIONSHIP_PARENT
                ),
                source_event_id=(
                    event.lineage_event_id
                ),
                target_event_id=parent_id,
            )

    # --------------------------------------------------------
    # MEMORY / EVENTS
    # --------------------------------------------------------

    def _write_to_operational_memory(
        self,
        event: SovereignOperationalLineageEvent,
    ) -> None:
        """
        Append lineage into operational memory.
        """

        memory = self.operational_memory_engine

        if memory is None:
            return

        payload = {
            "type": (
                "SOVEREIGN_OPERATIONAL_LINEAGE_EVENT"
            ),
            "lineage_event": (
                self._event_to_dict(event)
            ),
        }

        try:

            if hasattr(memory, "append_memory"):
                memory.append_memory(payload)

            elif hasattr(memory, "record"):
                memory.record(payload)

            elif hasattr(memory, "write"):
                memory.write(payload)

        except Exception as exc:
            print(
                "⚠️ Sovereign lineage memory write "
                f"failed: {exc}"
            )

    def _emit_lineage_event(
        self,
        event: SovereignOperationalLineageEvent,
    ) -> None:
        """
        Emit replayable lineage telemetry.
        """

        if self.event_bus is None:
            return

        payload = {
            "event_type": (
                "SOVEREIGN_OPERATIONAL_LINEAGE_EVENT"
            ),
            "engine_name": self.engine_name,
            "lineage_event": (
                self._event_to_dict(event)
            ),
        }

        try:

            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_OPERATIONAL_LINEAGE_EVENT",
                    payload,
                )

            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "SOVEREIGN_OPERATIONAL_LINEAGE_EVENT",
                    payload,
                )

        except Exception as exc:
            print(
                "⚠️ Sovereign lineage event emit "
                f"failed: {exc}"
            )

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_event(
        self,
        event: (
            SovereignOperationalLineageEvent
            | Dict[str, Any]
        ),
    ) -> SovereignOperationalLineageEvent:
        """
        Normalize external lineage payloads.
        """

        if isinstance(
            event,
            SovereignOperationalLineageEvent,
        ):
            return event

        return SovereignOperationalLineageEvent(
            lineage_event_id=str(
                event.get("lineage_event_id")
                or uuid.uuid4()
            ),
            lineage_type=(
                self._safe_lineage_type(
                    event.get("lineage_type")
                )
            ),
            lineage_status=(
                self._safe_lineage_status(
                    event.get("lineage_status")
                )
            ),
            source_engine=str(
                event.get("source_engine")
                or "unknown_engine"
            ),
            summary=str(
                event.get("summary") or ""
            ),
            severity=self._safe_severity(
                event.get("severity")
            ),
            confidence=self._clamp_confidence(
                event.get("confidence", 0.0)
            ),
            mission_priority=max(
                0,
                int(
                    event.get(
                        "mission_priority",
                        0,
                    )
                    or 0
                ),
            ),
            tenant_id=event.get("tenant_id"),
            case_id=event.get("case_id"),
            correlation_id=(
                event.get("correlation_id")
            ),
            parent_event_ids=list(
                event.get(
                    "parent_event_ids",
                    [],
                )
                or []
            ),
            constraints=list(
                event.get("constraints", [])
                or []
            ),
            approvals=list(
                event.get("approvals", [])
                or []
            ),
            verification_requirements=list(
                event.get(
                    "verification_requirements",
                    [],
                )
                or []
            ),
            context=dict(
                event.get("context", {})
                or {}
            ),
            metadata=dict(
                event.get("metadata", {})
                or {}
            ),
        )

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    @staticmethod
    def _event_to_dict(
        event: SovereignOperationalLineageEvent,
    ) -> Dict[str, Any]:
        """
        Serialize immutable lineage event.
        """

        return asdict(event)

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe_lineage_type(
        value: Any,
    ) -> str:
        value = str(
            value or LINEAGE_TYPE_COGNITION
        ).upper()

        valid = {
            LINEAGE_TYPE_COGNITION,
            LINEAGE_TYPE_COORDINATION,
            LINEAGE_TYPE_DECISION,
            LINEAGE_TYPE_ALIGNMENT,
            LINEAGE_TYPE_GOVERNANCE,
            LINEAGE_TYPE_EXECUTION,
            LINEAGE_TYPE_ROLLBACK,
            LINEAGE_TYPE_CONTINUITY,
            LINEAGE_TYPE_VERIFICATION,
            LINEAGE_TYPE_EVIDENCE,
            LINEAGE_TYPE_COMPLIANCE,
        }

        return (
            value
            if value in valid
            else LINEAGE_TYPE_COGNITION
        )

    @staticmethod
    def _safe_lineage_status(
        value: Any,
    ) -> str:
        value = str(
            value or LineageStatus.RECORDED.value
        ).upper()

        valid = {
            item.value
            for item in LineageStatus
        }

        return (
            value
            if value in valid
            else LineageStatus.RECORDED.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:
        value = str(
            value
            or LineageSeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in LineageSeverity
        }

        return (
            value
            if value in valid
            else LineageSeverity.INFO.value
        )

    @staticmethod
    def _clamp_confidence(
        value: Any,
    ) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(
            0.0,
            min(1.0, score),
        )


# ============================================================
# FACTORY
# ============================================================

def build_sovereign_operational_lineage_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
) -> SovereignOperationalLineageEngine:
    """
    Factory for explicit dependency injection.
    """

    return SovereignOperationalLineageEngine(
        event_bus=event_bus,
        operational_memory_engine=(
            operational_memory_engine
        ),
    )