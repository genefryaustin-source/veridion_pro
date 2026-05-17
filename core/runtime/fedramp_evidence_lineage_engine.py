"""
core/runtime/fedramp_evidence_lineage_engine.py

FedRAMP Evidence Lineage Engine

Compliance-native operational evidence graph layer.

This engine links:
- sovereign lineage events
- governance approvals
- execution alignment verdicts
- resilience decisions
- rollback records
- verification records
- custody/evidence references
- control mappings

into replayable FedRAMP/CMMC-ready evidence chains.

IMPORTANT:
This engine DOES NOT:
- generate final SSP documents
- generate final POA&M documents
- execute controls
- mutate prior evidence records
- alter operational state
- execute connectors

It ONLY:
- records compliance evidence lineage
- maps evidence to controls
- creates replayable evidence chains
- preserves audit-ready evidence relationships
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

DEFAULT_ENGINE_NAME = "fedramp_evidence_lineage_engine"

FRAMEWORK_FEDRAMP_MODERATE = "FEDRAMP_MODERATE"
FRAMEWORK_FEDRAMP_HIGH = "FEDRAMP_HIGH"
FRAMEWORK_CMMC_LEVEL_2 = "CMMC_LEVEL_2"
FRAMEWORK_NIST_800_53 = "NIST_800_53"

EVIDENCE_STATUS_RECORDED = "RECORDED"
EVIDENCE_STATUS_VERIFIED = "VERIFIED"
EVIDENCE_STATUS_REQUIRES_REVIEW = "REQUIRES_REVIEW"
EVIDENCE_STATUS_REJECTED = "REJECTED"
EVIDENCE_STATUS_SUPERSEDED = "SUPERSEDED"

RELATIONSHIP_SUPPORTS = "SUPPORTS"
RELATIONSHIP_DERIVED_FROM = "DERIVED_FROM"
RELATIONSHIP_APPROVED_BY = "APPROVED_BY"
RELATIONSHIP_VERIFIED_BY = "VERIFIED_BY"
RELATIONSHIP_CONSTRAINED_BY = "CONSTRAINED_BY"
RELATIONSHIP_ROLLBACK_FOR = "ROLLBACK_FOR"
RELATIONSHIP_CONTINUITY_FOR = "CONTINUITY_FOR"
RELATIONSHIP_REMEDIATES = "REMEDIATES"
RELATIONSHIP_POAM_FOR = "POAM_FOR"


# ============================================================
# ENUMS
# ============================================================

class FedRAMPControlFamily(str, Enum):
    AC = "AC"
    AU = "AU"
    AT = "AT"
    CA = "CA"
    CM = "CM"
    CP = "CP"
    IA = "IA"
    IR = "IR"
    MA = "MA"
    MP = "MP"
    PE = "PE"
    PL = "PL"
    PM = "PM"
    PS = "PS"
    RA = "RA"
    SA = "SA"
    SC = "SC"
    SI = "SI"
    SR = "SR"
    UNKNOWN = "UNKNOWN"


class EvidenceType(str, Enum):
    COGNITION_DECISION = "COGNITION_DECISION"
    COORDINATION_DECISION = "COORDINATION_DECISION"
    DECISION_ROUTE_PLAN = "DECISION_ROUTE_PLAN"
    EXECUTION_ALIGNMENT_VERDICT = "EXECUTION_ALIGNMENT_VERDICT"
    GOVERNANCE_APPROVAL = "GOVERNANCE_APPROVAL"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    LEGAL_REVIEW = "LEGAL_REVIEW"
    EXPORT_CONTROL_REVIEW = "EXPORT_CONTROL_REVIEW"
    RESILIENCE_DECISION = "RESILIENCE_DECISION"
    CONTINUITY_REVIEW = "CONTINUITY_REVIEW"
    ROLLBACK_PLAN = "ROLLBACK_PLAN"
    ROLLBACK_EXECUTION = "ROLLBACK_EXECUTION"
    VERIFICATION_RESULT = "VERIFICATION_RESULT"
    CUSTODY_EVENT = "CUSTODY_EVENT"
    EVIDENCE_RECORD = "EVIDENCE_RECORD"
    CASE_EVENT = "CASE_EVENT"
    POLICY_EVALUATION = "POLICY_EVALUATION"
    POAM_ITEM = "POAM_ITEM"
    SSP_COMPONENT = "SSP_COMPONENT"
    UNKNOWN = "UNKNOWN"


class EvidenceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class FedRAMPEvidenceControlMapping:
    """
    Evidence-to-control mapping.
    """

    mapping_id: str
    evidence_event_id: str
    framework: str
    control_id: str
    control_family: str
    rationale: str
    confidence: float
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class FedRAMPEvidenceRelationship:
    """
    Immutable evidence relationship edge.
    """

    relationship_id: str
    relationship_type: str
    source_evidence_event_id: str
    target_evidence_event_id: str
    rationale: str = ""
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class FedRAMPEvidenceLineageEvent:
    """
    Immutable compliance evidence event.
    """

    evidence_event_id: str
    evidence_type: str
    evidence_status: str
    source_engine: str
    summary: str

    severity: str
    confidence: float
    mission_priority: int

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    lineage_event_ids: List[str] = field(default_factory=list)
    parent_evidence_event_ids: List[str] = field(default_factory=list)
    related_control_ids: List[str] = field(default_factory=list)

    approvals: List[str] = field(default_factory=list)
    verifications: List[str] = field(default_factory=list)
    rollback_refs: List[str] = field(default_factory=list)
    custody_refs: List[str] = field(default_factory=list)
    poam_refs: List[str] = field(default_factory=list)

    constraints: List[str] = field(default_factory=list)
    evidence_payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class FedRAMPEvidenceChain:
    """
    Replayable evidence chain.
    """

    chain_id: str
    root_evidence_event_id: str
    evidence_event_ids: List[str]
    relationship_ids: List[str]
    control_ids: List[str]
    frameworks: List[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]
    generated_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class FedRAMPEvidenceLineageSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str
    total_evidence_events: int
    total_relationships: int
    total_control_mappings: int
    last_evidence_event_id: Optional[str]
    last_evidence_type: Optional[str]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class FedRAMPEvidenceLineageEngine:
    """
    Append-only FedRAMP/CMMC evidence lineage engine.

    Design guarantees:
    - append-only evidence records
    - immutable relationships
    - deterministic control mapping
    - replayable evidence chains
    - no execution behavior
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine

        self._events: List[FedRAMPEvidenceLineageEvent] = []
        self._relationships: List[FedRAMPEvidenceRelationship] = []
        self._control_mappings: List[FedRAMPEvidenceControlMapping] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def record_evidence(
        self,
        event: FedRAMPEvidenceLineageEvent | Dict[str, Any],
        *,
        auto_map_controls: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> FedRAMPEvidenceLineageEvent:
        """
        Record immutable compliance evidence event.
        """

        normalized = self._normalize_event(event)

        self._events.append(normalized)
        self._create_parent_relationships(normalized)

        if auto_map_controls:
            self._auto_map_controls(normalized)

        self._write_to_operational_memory(normalized, context=context)
        self._write_to_sovereign_lineage(normalized, context=context)
        self._emit_event(normalized, context=context)

        return normalized

    def append_evidence(
        self,
        event: FedRAMPEvidenceLineageEvent | Dict[str, Any],
        *,
        auto_map_controls: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> FedRAMPEvidenceLineageEvent:
        """
        Append-only alias.
        """

        return self.record_evidence(
            event,
            auto_map_controls=auto_map_controls,
            context=context,
        )

    def create_evidence_event(
        self,
        *,
        evidence_type: str,
        source_engine: str,
        summary: str,
        severity: str,
        confidence: float,
        mission_priority: int = 0,
        evidence_status: str = EVIDENCE_STATUS_RECORDED,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        lineage_event_ids: Optional[Sequence[str]] = None,
        parent_evidence_event_ids: Optional[Sequence[str]] = None,
        related_control_ids: Optional[Sequence[str]] = None,
        approvals: Optional[Sequence[str]] = None,
        verifications: Optional[Sequence[str]] = None,
        rollback_refs: Optional[Sequence[str]] = None,
        custody_refs: Optional[Sequence[str]] = None,
        poam_refs: Optional[Sequence[str]] = None,
        constraints: Optional[Sequence[str]] = None,
        evidence_payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FedRAMPEvidenceLineageEvent:
        """
        Create normalized evidence event.
        """

        return FedRAMPEvidenceLineageEvent(
            evidence_event_id=str(uuid.uuid4()),
            evidence_type=self._safe_evidence_type(evidence_type),
            evidence_status=self._safe_evidence_status(evidence_status),
            source_engine=source_engine or "unknown_engine",
            summary=summary or "",
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            mission_priority=max(0, int(mission_priority)),
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            lineage_event_ids=list(lineage_event_ids or []),
            parent_evidence_event_ids=list(parent_evidence_event_ids or []),
            related_control_ids=list(related_control_ids or []),
            approvals=list(approvals or []),
            verifications=list(verifications or []),
            rollback_refs=list(rollback_refs or []),
            custody_refs=list(custody_refs or []),
            poam_refs=list(poam_refs or []),
            constraints=list(constraints or []),
            evidence_payload=dict(evidence_payload or {}),
            metadata=dict(metadata or {}),
        )

    def create_relationship(
        self,
        *,
        relationship_type: str,
        source_evidence_event_id: str,
        target_evidence_event_id: str,
        rationale: str = "",
    ) -> FedRAMPEvidenceRelationship:
        """
        Create immutable evidence relationship.
        """

        relationship = FedRAMPEvidenceRelationship(
            relationship_id=str(uuid.uuid4()),
            relationship_type=self._safe_relationship_type(relationship_type),
            source_evidence_event_id=source_evidence_event_id,
            target_evidence_event_id=target_evidence_event_id,
            rationale=rationale or "",
        )

        self._relationships.append(relationship)
        return relationship

    def map_control(
        self,
        *,
        evidence_event_id: str,
        control_id: str,
        framework: str = FRAMEWORK_NIST_800_53,
        rationale: str = "",
        confidence: float = 1.0,
    ) -> FedRAMPEvidenceControlMapping:
        """
        Explicitly map an evidence event to a control.
        """

        mapping = FedRAMPEvidenceControlMapping(
            mapping_id=str(uuid.uuid4()),
            evidence_event_id=evidence_event_id,
            framework=self._safe_framework(framework),
            control_id=self._normalize_control_id(control_id),
            control_family=self._control_family(control_id),
            rationale=rationale or "",
            confidence=self._clamp_confidence(confidence),
        )

        self._control_mappings.append(mapping)
        return mapping

    def build_evidence_chain(
        self,
        root_evidence_event_id: str,
    ) -> FedRAMPEvidenceChain:
        """
        Build replayable evidence ancestry chain.
        """

        visited = set()
        evidence_ids: List[str] = []
        relationship_ids: List[str] = []

        def walk(event_id: str) -> None:
            if event_id in visited:
                return

            visited.add(event_id)
            event = self.get_evidence_event(event_id)

            if event is None:
                return

            evidence_ids.append(event.evidence_event_id)

            for relationship in self.get_relationships(event.evidence_event_id):
                relationship_ids.append(relationship.relationship_id)

                if relationship.source_evidence_event_id == event.evidence_event_id:
                    walk(relationship.target_evidence_event_id)
                elif relationship.target_evidence_event_id == event.evidence_event_id:
                    walk(relationship.source_evidence_event_id)

            for parent_id in event.parent_evidence_event_ids:
                walk(parent_id)

        walk(root_evidence_event_id)

        control_ids = sorted(
            {
                mapping.control_id
                for mapping in self._control_mappings
                if mapping.evidence_event_id in evidence_ids
            }
        )

        frameworks = sorted(
            {
                mapping.framework
                for mapping in self._control_mappings
                if mapping.evidence_event_id in evidence_ids
            }
        )

        root = self.get_evidence_event(root_evidence_event_id)

        return FedRAMPEvidenceChain(
            chain_id=str(uuid.uuid4()),
            root_evidence_event_id=root_evidence_event_id,
            evidence_event_ids=evidence_ids,
            relationship_ids=list(dict.fromkeys(relationship_ids)),
            control_ids=control_ids,
            frameworks=frameworks,
            tenant_id=root.tenant_id if root else None,
            case_id=root.case_id if root else None,
            correlation_id=root.correlation_id if root else None,
        )

    def get_evidence_event(
        self,
        evidence_event_id: str,
    ) -> Optional[FedRAMPEvidenceLineageEvent]:
        """
        Retrieve evidence event by ID.
        """

        for event in self._events:
            if event.evidence_event_id == evidence_event_id:
                return event

        return None

    def get_recent_events(
        self,
        *,
        limit: int = 50,
    ) -> List[FedRAMPEvidenceLineageEvent]:
        """
        Return recent evidence events newest-first.
        """

        limit = max(1, int(limit))
        return list(reversed(self._events[-limit:]))

    def get_relationships(
        self,
        evidence_event_id: Optional[str] = None,
    ) -> List[FedRAMPEvidenceRelationship]:
        """
        Retrieve evidence relationships.
        """

        if evidence_event_id is None:
            return list(self._relationships)

        return [
            relationship
            for relationship in self._relationships
            if (
                relationship.source_evidence_event_id == evidence_event_id
                or relationship.target_evidence_event_id == evidence_event_id
            )
        ]

    def get_control_mappings(
        self,
        evidence_event_id: Optional[str] = None,
        *,
        control_id: Optional[str] = None,
        framework: Optional[str] = None,
    ) -> List[FedRAMPEvidenceControlMapping]:
        """
        Retrieve control mappings.
        """

        mappings = list(self._control_mappings)

        if evidence_event_id:
            mappings = [
                mapping
                for mapping in mappings
                if mapping.evidence_event_id == evidence_event_id
            ]

        if control_id:
            normalized = self._normalize_control_id(control_id)
            mappings = [
                mapping
                for mapping in mappings
                if mapping.control_id == normalized
            ]

        if framework:
            safe_framework = self._safe_framework(framework)
            mappings = [
                mapping
                for mapping in mappings
                if mapping.framework == safe_framework
            ]

        return mappings

    def snapshot(self) -> FedRAMPEvidenceLineageSnapshot:
        """
        Lightweight diagnostics snapshot.
        """

        last = self._events[-1] if self._events else None

        return FedRAMPEvidenceLineageSnapshot(
            engine_name=self.engine_name,
            total_evidence_events=len(self._events),
            total_relationships=len(self._relationships),
            total_control_mappings=len(self._control_mappings),
            last_evidence_event_id=(
                last.evidence_event_id if last else None
            ),
            last_evidence_type=last.evidence_type if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # AUTOMATIC CONTROL MAPPING
    # --------------------------------------------------------

    def _auto_map_controls(
        self,
        event: FedRAMPEvidenceLineageEvent,
    ) -> None:
        """
        Conservative automatic control mapping.

        These are seed mappings only. Later export layers can enrich them.
        """

        mappings = self._suggest_controls(event)

        for control_id, rationale in mappings:
            self.map_control(
                evidence_event_id=event.evidence_event_id,
                control_id=control_id,
                framework=FRAMEWORK_NIST_800_53,
                rationale=rationale,
                confidence=0.75,
            )

    def _suggest_controls(
        self,
        event: FedRAMPEvidenceLineageEvent,
    ) -> List[tuple[str, str]]:
        """
        Suggest control mappings by evidence type and constraints.
        """

        suggested: List[tuple[str, str]] = []

        if event.evidence_type in {
            EvidenceType.GOVERNANCE_APPROVAL.value,
            EvidenceType.HUMAN_APPROVAL.value,
            EvidenceType.LEGAL_REVIEW.value,
            EvidenceType.EXPORT_CONTROL_REVIEW.value,
            EvidenceType.POLICY_EVALUATION.value,
        }:
            suggested.extend(
                [
                    ("AU-12", "Evidence supports audit event generation."),
                    ("CM-3", "Evidence supports governed change control."),
                    ("CA-7", "Evidence supports continuous monitoring."),
                ]
            )

        if event.evidence_type == EvidenceType.EXECUTION_ALIGNMENT_VERDICT.value:
            suggested.extend(
                [
                    ("AC-3", "Evidence supports access enforcement decisioning."),
                    ("AC-6", "Evidence supports least privilege constraints."),
                    ("SI-4", "Evidence supports security monitoring analysis."),
                    ("IR-4", "Evidence supports incident handling actions."),
                ]
            )

        if event.evidence_type == EvidenceType.RESILIENCE_DECISION.value:
            suggested.extend(
                [
                    ("CP-10", "Evidence supports system recovery posture."),
                    ("IR-4", "Evidence supports incident response handling."),
                    ("SI-4", "Evidence supports monitoring and detection."),
                ]
            )

        if event.evidence_type in {
            EvidenceType.ROLLBACK_PLAN.value,
            EvidenceType.ROLLBACK_EXECUTION.value,
        }:
            suggested.extend(
                [
                    ("CP-10", "Evidence supports recovery and reconstitution."),
                    ("CM-3", "Evidence supports controlled rollback/change."),
                    ("IR-4", "Evidence supports incident response recovery."),
                ]
            )

        if event.evidence_type == EvidenceType.VERIFICATION_RESULT.value:
            suggested.extend(
                [
                    ("CA-7", "Evidence supports continuous monitoring verification."),
                    ("SI-4", "Evidence supports security monitoring verification."),
                    ("AU-6", "Evidence supports audit review and analysis."),
                ]
            )

        if event.evidence_type in {
            EvidenceType.CUSTODY_EVENT.value,
            EvidenceType.EVIDENCE_RECORD.value,
        }:
            suggested.extend(
                [
                    ("AU-9", "Evidence supports audit information protection."),
                    ("AU-12", "Evidence supports audit event generation."),
                    ("IR-5", "Evidence supports incident monitoring."),
                ]
            )

        if event.evidence_type == EvidenceType.CASE_EVENT.value:
            suggested.extend(
                [
                    ("IR-4", "Evidence supports incident handling."),
                    ("IR-5", "Evidence supports incident monitoring."),
                    ("AU-6", "Evidence supports audit review."),
                ]
            )

        if "export_control_review" in event.constraints:
            suggested.append(
                ("RA-3", "Evidence supports risk assessment for export control review.")
            )

        if "human_approval" in event.constraints:
            suggested.append(
                ("AC-5", "Evidence supports separation of duties.")
            )

        if "rollback_plan" in event.constraints:
            suggested.append(
                ("CP-10", "Evidence supports recovery planning.")
            )

        if "post_execution_verification" in event.constraints:
            suggested.append(
                ("CA-7", "Evidence supports continuous monitoring.")
            )

        return list(dict.fromkeys(suggested))

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    def _create_parent_relationships(
        self,
        event: FedRAMPEvidenceLineageEvent,
    ) -> None:
        for parent_id in event.parent_evidence_event_ids:
            self.create_relationship(
                relationship_type=RELATIONSHIP_DERIVED_FROM,
                source_evidence_event_id=event.evidence_event_id,
                target_evidence_event_id=parent_id,
                rationale="Evidence event derived from parent evidence event.",
            )

    # --------------------------------------------------------
    # MEMORY / LINEAGE / EVENTS
    # --------------------------------------------------------

    def _write_to_operational_memory(
        self,
        event: FedRAMPEvidenceLineageEvent,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "FEDRAMP_EVIDENCE_LINEAGE_EVENT",
            "evidence_event": self._event_to_dict(event),
            "context": context or {},
        }

        try:
            if hasattr(memory, "append_memory"):
                memory.append_memory(payload)
            elif hasattr(memory, "record"):
                memory.record(payload)
            elif hasattr(memory, "write"):
                memory.write(payload)
        except Exception as exc:
            print(f"⚠️ FedRAMP evidence memory write failed: {exc}")

    def _write_to_sovereign_lineage(
        self,
        event: FedRAMPEvidenceLineageEvent,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "COMPLIANCE",
            "lineage_status": "RECORDED",
            "source_engine": self.engine_name,
            "summary": event.summary,
            "severity": event.severity,
            "confidence": event.confidence,
            "mission_priority": event.mission_priority,
            "tenant_id": event.tenant_id,
            "case_id": event.case_id,
            "correlation_id": event.correlation_id,
            "parent_event_ids": list(event.lineage_event_ids),
            "constraints": list(event.constraints),
            "approvals": list(event.approvals),
            "verification_requirements": list(event.verifications),
            "context": {
                "type": "FEDRAMP_EVIDENCE_LINEAGE_EVENT",
                "evidence_event": self._event_to_dict(event),
                "control_mappings": [
                    asdict(mapping)
                    for mapping in self.get_control_mappings(
                        event.evidence_event_id
                    )
                ],
                "context": context or {},
            },
            "metadata": {
                "evidence_event_id": event.evidence_event_id,
                "evidence_type": event.evidence_type,
                "related_control_ids": list(event.related_control_ids),
            },
        }

        try:
            if hasattr(lineage, "record_lineage"):
                lineage.record_lineage(payload)
            elif hasattr(lineage, "append_lineage"):
                lineage.append_lineage(payload)
            elif hasattr(lineage, "record"):
                lineage.record(payload)
        except Exception as exc:
            print(f"⚠️ FedRAMP evidence lineage write failed: {exc}")

    def _emit_event(
        self,
        event: FedRAMPEvidenceLineageEvent,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "FEDRAMP_EVIDENCE_LINEAGE_EVENT",
            "engine_name": self.engine_name,
            "evidence_event": self._event_to_dict(event),
            "control_mappings": [
                asdict(mapping)
                for mapping in self.get_control_mappings(
                    event.evidence_event_id
                )
            ],
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "FEDRAMP_EVIDENCE_LINEAGE_EVENT",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "FEDRAMP_EVIDENCE_LINEAGE_EVENT",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ FedRAMP evidence event emit failed: {exc}")

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_event(
        self,
        event: FedRAMPEvidenceLineageEvent | Dict[str, Any],
    ) -> FedRAMPEvidenceLineageEvent:
        if isinstance(event, FedRAMPEvidenceLineageEvent):
            return event

        return FedRAMPEvidenceLineageEvent(
            evidence_event_id=str(
                event.get("evidence_event_id") or uuid.uuid4()
            ),
            evidence_type=self._safe_evidence_type(
                event.get("evidence_type")
            ),
            evidence_status=self._safe_evidence_status(
                event.get("evidence_status")
            ),
            source_engine=str(event.get("source_engine") or "unknown_engine"),
            summary=str(event.get("summary") or ""),
            severity=self._safe_severity(event.get("severity")),
            confidence=self._clamp_confidence(event.get("confidence", 0.0)),
            mission_priority=max(
                0,
                int(event.get("mission_priority", 0) or 0),
            ),
            tenant_id=event.get("tenant_id"),
            case_id=event.get("case_id"),
            correlation_id=event.get("correlation_id"),
            lineage_event_ids=list(event.get("lineage_event_ids", []) or []),
            parent_evidence_event_ids=list(
                event.get("parent_evidence_event_ids", []) or []
            ),
            related_control_ids=[
                self._normalize_control_id(control_id)
                for control_id in list(
                    event.get("related_control_ids", []) or []
                )
            ],
            approvals=list(event.get("approvals", []) or []),
            verifications=list(event.get("verifications", []) or []),
            rollback_refs=list(event.get("rollback_refs", []) or []),
            custody_refs=list(event.get("custody_refs", []) or []),
            poam_refs=list(event.get("poam_refs", []) or []),
            constraints=list(event.get("constraints", []) or []),
            evidence_payload=dict(event.get("evidence_payload", {}) or {}),
            metadata=dict(event.get("metadata", {}) or {}),
        )

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    @staticmethod
    def _event_to_dict(
        event: FedRAMPEvidenceLineageEvent,
    ) -> Dict[str, Any]:
        return asdict(event)

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe_evidence_type(value: Any) -> str:
        value = str(value or EvidenceType.UNKNOWN.value).upper()
        valid = {item.value for item in EvidenceType}
        return value if value in valid else EvidenceType.UNKNOWN.value

    @staticmethod
    def _safe_evidence_status(value: Any) -> str:
        value = str(value or EVIDENCE_STATUS_RECORDED).upper()
        valid = {
            EVIDENCE_STATUS_RECORDED,
            EVIDENCE_STATUS_VERIFIED,
            EVIDENCE_STATUS_REQUIRES_REVIEW,
            EVIDENCE_STATUS_REJECTED,
            EVIDENCE_STATUS_SUPERSEDED,
        }
        return value if value in valid else EVIDENCE_STATUS_RECORDED

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or EvidenceSeverity.INFO.value).upper()
        valid = {item.value for item in EvidenceSeverity}
        return value if value in valid else EvidenceSeverity.INFO.value

    @staticmethod
    def _safe_framework(value: Any) -> str:
        value = str(value or FRAMEWORK_NIST_800_53).upper()
        valid = {
            FRAMEWORK_FEDRAMP_MODERATE,
            FRAMEWORK_FEDRAMP_HIGH,
            FRAMEWORK_CMMC_LEVEL_2,
            FRAMEWORK_NIST_800_53,
        }
        return value if value in valid else FRAMEWORK_NIST_800_53

    @staticmethod
    def _safe_relationship_type(value: Any) -> str:
        value = str(value or RELATIONSHIP_SUPPORTS).upper()
        valid = {
            RELATIONSHIP_SUPPORTS,
            RELATIONSHIP_DERIVED_FROM,
            RELATIONSHIP_APPROVED_BY,
            RELATIONSHIP_VERIFIED_BY,
            RELATIONSHIP_CONSTRAINED_BY,
            RELATIONSHIP_ROLLBACK_FOR,
            RELATIONSHIP_CONTINUITY_FOR,
            RELATIONSHIP_REMEDIATES,
            RELATIONSHIP_POAM_FOR,
        }
        return value if value in valid else RELATIONSHIP_SUPPORTS

    @staticmethod
    def _normalize_control_id(value: Any) -> str:
        return str(value or "UNKNOWN").upper().strip().replace(" ", "")

    @staticmethod
    def _control_family(control_id: Any) -> str:
        control_id = str(control_id or "").upper().strip()
        family = control_id.split("-")[0] if "-" in control_id else "UNKNOWN"
        valid = {item.value for item in FedRAMPControlFamily}
        return family if family in valid else FedRAMPControlFamily.UNKNOWN.value

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(1.0, score))


# ============================================================
# FACTORY
# ============================================================

def build_fedramp_evidence_lineage_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
) -> FedRAMPEvidenceLineageEngine:
    """
    Factory for explicit dependency injection.
    """

    return FedRAMPEvidenceLineageEngine(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
    )