"""
core/runtime/sovereign_sovereignty_assurance_engine.py

Sovereign Sovereignty Assurance Engine

Assurance and defensibility layer above the autonomous operational governor.

This subsystem verifies:
- sovereign boundaries
- tenant isolation
- governance integrity
- autonomy restrictions
- command authority limits
- mission continuity protection
- evidence completeness
- FedRAMP / CMMC defensibility posture

IMPORTANT:
This subsystem DOES NOT:
- execute operational actions
- mutate infrastructure
- bypass governance
- approve destructive actions
- perform offensive cyber operations

It ONLY:
- evaluates sovereignty assurance posture
- verifies governance defensibility
- checks tenant-boundary risk
- assesses evidence completeness
- records replayable assurance lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = "sovereign_sovereignty_assurance_engine"
DEFAULT_ASSURANCE_DEPTH = 12


ASSURANCE_STATE_VERIFIED = "VERIFIED"
ASSURANCE_STATE_REVIEW = "REVIEW"
ASSURANCE_STATE_WEAKENED = "WEAKENED"
ASSURANCE_STATE_DEFICIENT = "DEFICIENT"
ASSURANCE_STATE_SOVEREIGN_RISK = "SOVEREIGN_RISK"
ASSURANCE_STATE_NON_DEFENSIBLE = "NON_DEFENSIBLE"

ASSURANCE_OUTCOME_DEFENSIBLE = "DEFENSIBLE"
ASSURANCE_OUTCOME_REVIEW_REQUIRED = "REVIEW_REQUIRED"
ASSURANCE_OUTCOME_EVIDENCE_GAP = "EVIDENCE_GAP"
ASSURANCE_OUTCOME_BOUNDARY_RISK = "BOUNDARY_RISK"
ASSURANCE_OUTCOME_NON_DEFENSIBLE = "NON_DEFENSIBLE"

RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_REVIEW_ASSURANCE = "REVIEW_ASSURANCE"
RECOMMENDATION_REPAIR_EVIDENCE = "REPAIR_EVIDENCE"
RECOMMENDATION_VALIDATE_TENANT_ISOLATION = "VALIDATE_TENANT_ISOLATION"
RECOMMENDATION_RESTRICT_AUTONOMY = "RESTRICT_AUTONOMY"
RECOMMENDATION_ESCALATE_SOVEREIGNTY = "ESCALATE_SOVEREIGNTY"


class AssuranceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AssuranceDomain(str, Enum):
    TENANT = "TENANT"
    GOVERNANCE = "GOVERNANCE"
    COMMAND = "COMMAND"
    AUTONOMY = "AUTONOMY"
    MISSION = "MISSION"
    EVIDENCE = "EVIDENCE"
    FEDRAMP = "FEDRAMP"
    CMMC = "CMMC"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class AssuranceDirective:
    directive_id: str
    directive_name: str
    domain: str
    priority: str

    assurance_control: str
    required: bool = True

    confidence_score: float = 1.0
    defensibility_impact_score: float = 0.0

    rationale: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssuranceSignal:
    assurance_signal_id: str

    source_engine: str
    domain: str
    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    sovereign_boundary_integrity_score: float = 100.0
    tenant_isolation_score: float = 100.0
    governance_integrity_score: float = 100.0
    autonomy_restriction_score: float = 100.0
    command_authority_integrity_score: float = 100.0
    mission_continuity_protection_score: float = 100.0
    evidence_completeness_score: float = 100.0
    fedramp_defensibility_score: float = 100.0
    cmmc_alignment_score: float = 100.0

    sovereignty_risk_score: float = 0.0
    evidence_gap_score: float = 0.0
    boundary_violation_risk_score: float = 0.0
    governance_drift_score: float = 0.0
    cross_tenant_risk_score: float = 0.0
    uncertainty_score: float = 0.0

    directives: List[AssuranceDirective] = field(default_factory=list)

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class AssuranceSimulationStep:
    step_id: str
    step_index: int

    projected_state: str
    projected_outcome: str
    recommendation: str

    sovereignty_score: float
    tenant_isolation_score: float
    governance_integrity_score: float
    evidence_completeness_score: float
    defensibility_score: float

    assurance_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SovereignAssuranceAssessment:
    assessment_id: str

    assurance_state: str
    projected_outcome: str
    recommendation: str

    sovereign_boundary_integrity_score: float
    tenant_isolation_score: float
    governance_integrity_score: float
    autonomy_restriction_score: float
    command_authority_integrity_score: float
    mission_continuity_protection_score: float
    evidence_completeness_score: float
    fedramp_defensibility_score: float
    cmmc_alignment_score: float

    sovereignty_risk_score: float
    evidence_gap_score: float
    boundary_violation_risk_score: float
    governance_drift_score: float
    cross_tenant_risk_score: float
    uncertainty_score: float

    defensibility_score: float
    assurance_risk_score: float

    explainability_score: float
    assurance_confidence: float

    severity: str
    confidence: float

    assurance_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[AssuranceSimulationStep]

    assurance_topology: Dict[str, Any]

    recommended_controls: List[str]
    recommended_actions: List[Dict[str, Any]]

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


class SovereignSovereigntyAssuranceEngine:
    """
    Sovereign assurance and defensibility cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_governor: Optional[Any] = None,
        operational_command_mesh: Optional[Any] = None,
        autonomous_defense_director: Optional[Any] = None,
        governance_guardrails_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.operational_governor = operational_governor
        self.operational_command_mesh = operational_command_mesh
        self.autonomous_defense_director = autonomous_defense_director
        self.governance_guardrails_engine = governance_guardrails_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine

        self._signals_seen = 0
        self._assessments: List[SovereignAssuranceAssessment] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[AssuranceSignal | Dict[str, Any]],
        *,
        assurance_depth: int = DEFAULT_ASSURANCE_DEPTH,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignAssuranceAssessment:
        normalized = [
            self._normalize_signal(
                item,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:
            assessment = self._empty_assessment(
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_assessment(assessment, context=context)
            return assessment

        selected = self._select_primary_signal(normalized)

        sovereign_boundary = self._avg_score(
            [s.sovereign_boundary_integrity_score for s in normalized]
        )
        tenant_isolation = self._avg_score(
            [s.tenant_isolation_score for s in normalized]
        )
        governance_integrity = self._avg_score(
            [s.governance_integrity_score for s in normalized]
        )
        autonomy_restriction = self._avg_score(
            [s.autonomy_restriction_score for s in normalized]
        )
        command_authority = self._avg_score(
            [s.command_authority_integrity_score for s in normalized]
        )
        mission_continuity = self._avg_score(
            [s.mission_continuity_protection_score for s in normalized]
        )
        evidence_completeness = self._avg_score(
            [s.evidence_completeness_score for s in normalized]
        )
        fedramp_defensibility = self._avg_score(
            [s.fedramp_defensibility_score for s in normalized]
        )
        cmmc_alignment = self._avg_score(
            [s.cmmc_alignment_score for s in normalized]
        )

        sovereignty_risk = self._avg_score(
            [s.sovereignty_risk_score for s in normalized]
        )
        evidence_gap = self._avg_score(
            [s.evidence_gap_score for s in normalized]
        )
        boundary_violation = self._avg_score(
            [s.boundary_violation_risk_score for s in normalized]
        )
        governance_drift = self._avg_score(
            [s.governance_drift_score for s in normalized]
        )
        cross_tenant_risk = self._avg_score(
            [s.cross_tenant_risk_score for s in normalized]
        )
        uncertainty = self._avg_score(
            [s.uncertainty_score for s in normalized]
        )

        defensibility_score = self._defensibility_score(
            sovereign_boundary_integrity_score=sovereign_boundary,
            tenant_isolation_score=tenant_isolation,
            governance_integrity_score=governance_integrity,
            autonomy_restriction_score=autonomy_restriction,
            command_authority_integrity_score=command_authority,
            mission_continuity_protection_score=mission_continuity,
            evidence_completeness_score=evidence_completeness,
            fedramp_defensibility_score=fedramp_defensibility,
            cmmc_alignment_score=cmmc_alignment,
        )

        assurance_risk = self._assurance_risk_score(
            sovereignty_risk_score=sovereignty_risk,
            evidence_gap_score=evidence_gap,
            boundary_violation_risk_score=boundary_violation,
            governance_drift_score=governance_drift,
            cross_tenant_risk_score=cross_tenant_risk,
            uncertainty_score=uncertainty,
            defensibility_score=defensibility_score,
        )

        assurance_state = self._assurance_state(
            assurance_risk_score=assurance_risk,
            defensibility_score=defensibility_score,
            tenant_isolation_score=tenant_isolation,
            governance_integrity_score=governance_integrity,
            evidence_completeness_score=evidence_completeness,
            sovereign_boundary_integrity_score=sovereign_boundary,
        )

        projected_outcome = self._projected_outcome(
            assurance_state=assurance_state,
            defensibility_score=defensibility_score,
            assurance_risk_score=assurance_risk,
        )

        recommendation = self._recommendation(
            assurance_state=assurance_state,
            evidence_gap_score=evidence_gap,
            cross_tenant_risk_score=cross_tenant_risk,
            boundary_violation_risk_score=boundary_violation,
            governance_drift_score=governance_drift,
        )

        topology = self._build_topology(normalized)

        steps = self._build_steps(
            assurance_state=assurance_state,
            projected_outcome=projected_outcome,
            recommendation=recommendation,
            sovereignty_score=sovereign_boundary,
            tenant_isolation_score=tenant_isolation,
            governance_integrity_score=governance_integrity,
            evidence_completeness_score=evidence_completeness,
            defensibility_score=defensibility_score,
            assurance_risk_score=assurance_risk,
            assurance_depth=assurance_depth,
        )

        assessment = SovereignAssuranceAssessment(
            assessment_id=str(uuid.uuid4()),
            assurance_state=assurance_state,
            projected_outcome=projected_outcome,
            recommendation=recommendation,
            sovereign_boundary_integrity_score=sovereign_boundary,
            tenant_isolation_score=tenant_isolation,
            governance_integrity_score=governance_integrity,
            autonomy_restriction_score=autonomy_restriction,
            command_authority_integrity_score=command_authority,
            mission_continuity_protection_score=mission_continuity,
            evidence_completeness_score=evidence_completeness,
            fedramp_defensibility_score=fedramp_defensibility,
            cmmc_alignment_score=cmmc_alignment,
            sovereignty_risk_score=sovereignty_risk,
            evidence_gap_score=evidence_gap,
            boundary_violation_risk_score=boundary_violation,
            governance_drift_score=governance_drift,
            cross_tenant_risk_score=cross_tenant_risk,
            uncertainty_score=uncertainty,
            defensibility_score=defensibility_score,
            assurance_risk_score=assurance_risk,
            explainability_score=self._explainability_score(normalized),
            assurance_confidence=self._confidence(normalized),
            severity=selected.severity,
            confidence=selected.confidence,
            assurance_depth=assurance_depth,
            mission_id=mission_id or selected.mission_id,
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            simulation_steps=steps,
            assurance_topology=topology,
            recommended_controls=self._recommended_controls(
                assurance_state=assurance_state,
                recommendation=recommendation,
            ),
            recommended_actions=self._recommended_actions(
                assurance_state=assurance_state,
                recommendation=recommendation,
            ),
            rationale=self._build_rationale(
                assurance_state=assurance_state,
                projected_outcome=projected_outcome,
                recommendation=recommendation,
                defensibility_score=defensibility_score,
                assurance_risk_score=assurance_risk,
                signal_count=len(normalized),
                assurance_depth=assurance_depth,
            ),
            metadata={
                "source_engines": sorted({s.source_engine for s in normalized}),
                "domains": sorted({s.domain for s in normalized}),
            },
        )

        self._record_assessment(assessment, context=context)
        return assessment

    def submit(
        self,
        signals: Sequence[AssuranceSignal | Dict[str, Any]],
        *,
        assurance_depth: int = DEFAULT_ASSURANCE_DEPTH,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignAssuranceAssessment:
        return self.evaluate(
            signals,
            assurance_depth=assurance_depth,
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            context=context,
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignAssuranceAssessment]:
        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    # ==========================================================
    # SCORING
    # ==========================================================

    def _defensibility_score(
        self,
        *,
        sovereign_boundary_integrity_score: float,
        tenant_isolation_score: float,
        governance_integrity_score: float,
        autonomy_restriction_score: float,
        command_authority_integrity_score: float,
        mission_continuity_protection_score: float,
        evidence_completeness_score: float,
        fedramp_defensibility_score: float,
        cmmc_alignment_score: float,
    ) -> float:
        score = statistics.mean(
            [
                sovereign_boundary_integrity_score,
                tenant_isolation_score,
                governance_integrity_score,
                autonomy_restriction_score,
                command_authority_integrity_score,
                mission_continuity_protection_score,
                evidence_completeness_score,
                fedramp_defensibility_score,
                cmmc_alignment_score,
            ]
        )
        return self._clamp_score(score)

    def _assurance_risk_score(
        self,
        *,
        sovereignty_risk_score: float,
        evidence_gap_score: float,
        boundary_violation_risk_score: float,
        governance_drift_score: float,
        cross_tenant_risk_score: float,
        uncertainty_score: float,
        defensibility_score: float,
    ) -> float:
        risk = (
            sovereignty_risk_score
            + evidence_gap_score
            + boundary_violation_risk_score
            + governance_drift_score
            + cross_tenant_risk_score
            + uncertainty_score
            + (100.0 - defensibility_score)
        ) / 7.0
        return self._clamp_score(risk)

    # ==========================================================
    # STATES / OUTCOMES
    # ==========================================================

    @staticmethod
    def _assurance_state(
        *,
        assurance_risk_score: float,
        defensibility_score: float,
        tenant_isolation_score: float,
        governance_integrity_score: float,
        evidence_completeness_score: float,
        sovereign_boundary_integrity_score: float,
    ) -> str:
        if defensibility_score <= 35 or assurance_risk_score >= 85:
            return ASSURANCE_STATE_NON_DEFENSIBLE

        if sovereign_boundary_integrity_score <= 45:
            return ASSURANCE_STATE_SOVEREIGN_RISK

        if tenant_isolation_score <= 55:
            return ASSURANCE_STATE_SOVEREIGN_RISK

        if evidence_completeness_score <= 60:
            return ASSURANCE_STATE_DEFICIENT

        if governance_integrity_score <= 65:
            return ASSURANCE_STATE_WEAKENED

        if assurance_risk_score >= 45:
            return ASSURANCE_STATE_REVIEW

        return ASSURANCE_STATE_VERIFIED

    @staticmethod
    def _projected_outcome(
        *,
        assurance_state: str,
        defensibility_score: float,
        assurance_risk_score: float,
    ) -> str:
        if assurance_state == ASSURANCE_STATE_NON_DEFENSIBLE:
            return ASSURANCE_OUTCOME_NON_DEFENSIBLE

        if assurance_state == ASSURANCE_STATE_SOVEREIGN_RISK:
            return ASSURANCE_OUTCOME_BOUNDARY_RISK

        if assurance_state == ASSURANCE_STATE_DEFICIENT:
            return ASSURANCE_OUTCOME_EVIDENCE_GAP

        if defensibility_score >= 80 and assurance_risk_score <= 25:
            return ASSURANCE_OUTCOME_DEFENSIBLE

        return ASSURANCE_OUTCOME_REVIEW_REQUIRED

    @staticmethod
    def _recommendation(
        *,
        assurance_state: str,
        evidence_gap_score: float,
        cross_tenant_risk_score: float,
        boundary_violation_risk_score: float,
        governance_drift_score: float,
    ) -> str:
        if assurance_state == ASSURANCE_STATE_NON_DEFENSIBLE:
            return RECOMMENDATION_ESCALATE_SOVEREIGNTY

        if cross_tenant_risk_score >= 50 or boundary_violation_risk_score >= 50:
            return RECOMMENDATION_VALIDATE_TENANT_ISOLATION

        if evidence_gap_score >= 50:
            return RECOMMENDATION_REPAIR_EVIDENCE

        if governance_drift_score >= 50:
            return RECOMMENDATION_RESTRICT_AUTONOMY

        if assurance_state in {
            ASSURANCE_STATE_REVIEW,
            ASSURANCE_STATE_WEAKENED,
            ASSURANCE_STATE_DEFICIENT,
            ASSURANCE_STATE_SOVEREIGN_RISK,
        }:
            return RECOMMENDATION_REVIEW_ASSURANCE

        return RECOMMENDATION_MONITOR

    # ==========================================================
    # TOPOLOGY / SIMULATION
    # ==========================================================

    def _build_topology(
        self,
        signals: Sequence[AssuranceSignal],
    ) -> Dict[str, Any]:
        directives = []

        for signal in signals:
            for directive in signal.directives or []:
                directives.append(
                    {
                        "directive_id": directive.directive_id,
                        "directive_name": directive.directive_name,
                        "domain": directive.domain,
                        "priority": directive.priority,
                        "assurance_control": directive.assurance_control,
                        "required": directive.required,
                        "confidence_score": directive.confidence_score,
                        "defensibility_impact_score": directive.defensibility_impact_score,
                    }
                )

        return {
            "directive_count": len(directives),
            "directives": directives,
            "topology_state": "ACTIVE" if directives else "EMPTY",
        }

    def _build_steps(
        self,
        *,
        assurance_state: str,
        projected_outcome: str,
        recommendation: str,
        sovereignty_score: float,
        tenant_isolation_score: float,
        governance_integrity_score: float,
        evidence_completeness_score: float,
        defensibility_score: float,
        assurance_risk_score: float,
        assurance_depth: int,
    ) -> List[AssuranceSimulationStep]:
        steps: List[AssuranceSimulationStep] = []

        for idx in range(max(1, int(assurance_depth))):
            steps.append(
                AssuranceSimulationStep(
                    step_id=str(uuid.uuid4()),
                    step_index=idx,
                    projected_state=assurance_state,
                    projected_outcome=projected_outcome,
                    recommendation=recommendation,
                    sovereignty_score=sovereignty_score,
                    tenant_isolation_score=tenant_isolation_score,
                    governance_integrity_score=governance_integrity_score,
                    evidence_completeness_score=evidence_completeness_score,
                    defensibility_score=defensibility_score,
                    assurance_risk_score=assurance_risk_score,
                    rationale=(
                        f"Sovereignty assurance projection step {idx} "
                        f"preserved state {assurance_state}."
                    ),
                )
            )

        return steps

    # ==========================================================
    # RECOMMENDED CONTROLS / ACTIONS
    # ==========================================================

    @staticmethod
    def _recommended_controls(
        *,
        assurance_state: str,
        recommendation: str,
    ) -> List[str]:
        controls = [
            "sovereignty_assurance_lineage_recording",
            "sovereignty_assurance_evidence_recording",
            "tenant_boundary_validation",
            "governance_integrity_review",
        ]

        if assurance_state != ASSURANCE_STATE_VERIFIED:
            controls.append("assurance_review")

        if recommendation == RECOMMENDATION_REPAIR_EVIDENCE:
            controls.append("evidence_gap_remediation")

        if recommendation == RECOMMENDATION_VALIDATE_TENANT_ISOLATION:
            controls.append("cross_tenant_isolation_validation")

        if recommendation == RECOMMENDATION_RESTRICT_AUTONOMY:
            controls.append("autonomy_restriction_review")

        if recommendation == RECOMMENDATION_ESCALATE_SOVEREIGNTY:
            controls.append("sovereignty_escalation_review")

        return list(dict.fromkeys(controls))

    @staticmethod
    def _recommended_actions(
        *,
        assurance_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "action": "record_sovereignty_assurance_lineage",
                "assurance_state": assurance_state,
            },
            {
                "action": "record_sovereignty_assurance_evidence",
                "assurance_state": assurance_state,
            },
            {
                "action": "review_sovereignty_assurance_posture",
                "recommendation": recommendation,
            },
        ]

    # ==========================================================
    # RATIONALE / RECORDING
    # ==========================================================

    @staticmethod
    def _build_rationale(
        *,
        assurance_state: str,
        projected_outcome: str,
        recommendation: str,
        defensibility_score: float,
        assurance_risk_score: float,
        signal_count: int,
        assurance_depth: int,
    ) -> str:
        return (
            f"Sovereign sovereignty assurance evaluation processed "
            f"{signal_count} signal(s) across assurance depth "
            f"{assurance_depth}. Assurance state {assurance_state}; "
            f"projected outcome {projected_outcome}; recommendation "
            f"{recommendation}. Defensibility score "
            f"{defensibility_score:.2f}; assurance risk score "
            f"{assurance_risk_score:.2f}."
        )

    def _record_assessment(
        self,
        assessment: SovereignAssuranceAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._assessments.append(assessment)

        self._write_to_memory(assessment, context=context)
        self._write_to_lineage(assessment, context=context)
        self._write_to_evidence(assessment, context=context)
        self._emit_event(assessment, context=context)

    def _write_to_memory(
        self,
        assessment: SovereignAssuranceAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.operational_memory_engine is None:
            return

        payload = {
            "type": "SOVEREIGN_SOVEREIGNTY_ASSURANCE_ASSESSMENT",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.operational_memory_engine, "append_memory"):
                self.operational_memory_engine.append_memory(payload)
        except Exception as exc:
            print(f"⚠️ Sovereignty assurance memory write failed: {exc}")

    def _write_to_lineage(
        self,
        assessment: SovereignAssuranceAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": "SOVEREIGNTY_ASSURANCE",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "context": {
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.lineage_engine, "record_lineage"):
                self.lineage_engine.record_lineage(payload)
        except Exception as exc:
            print(f"⚠️ Sovereignty assurance lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        assessment: SovereignAssuranceAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.fedramp_evidence_lineage_engine is None:
            return

        payload = {
            "evidence_type": "SOVEREIGNTY_ASSURANCE",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "evidence_payload": {
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.fedramp_evidence_lineage_engine, "record_evidence"):
                self.fedramp_evidence_lineage_engine.record_evidence(payload)
        except Exception as exc:
            print(f"⚠️ Sovereignty assurance evidence write failed: {exc}")

    def _emit_event(
        self,
        assessment: SovereignAssuranceAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "SOVEREIGNTY_ASSURANCE_ASSESSMENT",
            "engine_name": self.engine_name,
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGNTY_ASSURANCE_ASSESSMENT",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Sovereignty assurance event emit failed: {exc}")

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: AssuranceSignal | Dict[str, Any],
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> AssuranceSignal:
        if isinstance(item, AssuranceSignal):
            return item

        directives = []

        for directive in item.get("directives", []) or []:
            directives.append(
                AssuranceDirective(
                    directive_id=str(directive.get("directive_id") or uuid.uuid4()),
                    directive_name=str(
                        directive.get("directive_name") or "unknown_directive"
                    ),
                    domain=self._safe_domain(directive.get("domain")),
                    priority=str(directive.get("priority") or "LOW").upper(),
                    assurance_control=str(
                        directive.get("assurance_control") or "unspecified"
                    ),
                    required=bool(directive.get("required", True)),
                    confidence_score=self._clamp_probability(
                        directive.get("confidence_score", 1.0)
                    ),
                    defensibility_impact_score=self._clamp_score(
                        directive.get("defensibility_impact_score", 0.0)
                    ),
                    rationale=str(directive.get("rationale") or ""),
                    metadata=dict(directive.get("metadata", {}) or {}),
                )
            )

        return AssuranceSignal(
            assurance_signal_id=str(
                item.get("assurance_signal_id") or uuid.uuid4()
            ),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            domain=self._safe_domain(item.get("domain")),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_probability(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            mission_id=mission_id or item.get("mission_id"),
            tenant_id=tenant_id or item.get("tenant_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            sovereign_boundary_integrity_score=self._clamp_score(
                item.get("sovereign_boundary_integrity_score", 100.0)
            ),
            tenant_isolation_score=self._clamp_score(
                item.get("tenant_isolation_score", 100.0)
            ),
            governance_integrity_score=self._clamp_score(
                item.get("governance_integrity_score", 100.0)
            ),
            autonomy_restriction_score=self._clamp_score(
                item.get("autonomy_restriction_score", 100.0)
            ),
            command_authority_integrity_score=self._clamp_score(
                item.get("command_authority_integrity_score", 100.0)
            ),
            mission_continuity_protection_score=self._clamp_score(
                item.get("mission_continuity_protection_score", 100.0)
            ),
            evidence_completeness_score=self._clamp_score(
                item.get("evidence_completeness_score", 100.0)
            ),
            fedramp_defensibility_score=self._clamp_score(
                item.get("fedramp_defensibility_score", 100.0)
            ),
            cmmc_alignment_score=self._clamp_score(
                item.get("cmmc_alignment_score", 100.0)
            ),
            sovereignty_risk_score=self._clamp_score(
                item.get("sovereignty_risk_score", 0.0)
            ),
            evidence_gap_score=self._clamp_score(item.get("evidence_gap_score", 0.0)),
            boundary_violation_risk_score=self._clamp_score(
                item.get("boundary_violation_risk_score", 0.0)
            ),
            governance_drift_score=self._clamp_score(
                item.get("governance_drift_score", 0.0)
            ),
            cross_tenant_risk_score=self._clamp_score(
                item.get("cross_tenant_risk_score", 0.0)
            ),
            uncertainty_score=self._clamp_score(item.get("uncertainty_score", 0.0)),
            directives=directives,
            payload=dict(item.get("payload", {}) or {}),
        )

    def _empty_assessment(
        self,
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignAssuranceAssessment:
        return SovereignAssuranceAssessment(
            assessment_id=str(uuid.uuid4()),
            assurance_state=ASSURANCE_STATE_VERIFIED,
            projected_outcome=ASSURANCE_OUTCOME_DEFENSIBLE,
            recommendation=RECOMMENDATION_MONITOR,
            sovereign_boundary_integrity_score=100.0,
            tenant_isolation_score=100.0,
            governance_integrity_score=100.0,
            autonomy_restriction_score=100.0,
            command_authority_integrity_score=100.0,
            mission_continuity_protection_score=100.0,
            evidence_completeness_score=100.0,
            fedramp_defensibility_score=100.0,
            cmmc_alignment_score=100.0,
            sovereignty_risk_score=0.0,
            evidence_gap_score=0.0,
            boundary_violation_risk_score=0.0,
            governance_drift_score=0.0,
            cross_tenant_risk_score=0.0,
            uncertainty_score=0.0,
            defensibility_score=100.0,
            assurance_risk_score=0.0,
            explainability_score=100.0,
            assurance_confidence=1.0,
            severity=AssuranceSeverity.INFO.value,
            confidence=1.0,
            assurance_depth=0,
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            simulation_steps=[],
            assurance_topology={
                "directive_count": 0,
                "directives": [],
                "topology_state": "EMPTY",
            },
            recommended_controls=[
                "sovereignty_assurance_lineage_recording",
                "sovereignty_assurance_evidence_recording",
            ],
            recommended_actions=[
                {
                    "action": "continue_sovereignty_assurance_monitoring",
                }
            ],
            rationale="No sovereignty assurance signals submitted.",
            metadata={},
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _select_primary_signal(
        self,
        signals: Sequence[AssuranceSignal],
    ) -> AssuranceSignal:
        return sorted(
            signals,
            key=lambda item: (
                item.sovereignty_risk_score,
                item.boundary_violation_risk_score,
                item.cross_tenant_risk_score,
                item.evidence_gap_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _confidence(
        self,
        signals: Sequence[AssuranceSignal],
    ) -> float:
        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean([s.confidence for s in signals])
        )

    def _explainability_score(
        self,
        signals: Sequence[AssuranceSignal],
    ) -> float:
        if not signals:
            return 0.0

        explained = 0

        for signal in signals:
            if signal.summary:
                explained += 1
            if signal.source_engine:
                explained += 1
            if signal.domain:
                explained += 1

        return self._clamp_score((explained / (len(signals) * 3)) * 100)

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or AssuranceDomain.UNKNOWN.value).upper()
        valid = {item.value for item in AssuranceDomain}
        return value if value in valid else AssuranceDomain.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or AssuranceSeverity.INFO.value).upper()
        valid = {item.value for item in AssuranceSeverity}
        return value if value in valid else AssuranceSeverity.INFO.value

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _clamp_probability(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(1.0, score))

    @staticmethod
    def _avg_score(values: Sequence[float]) -> float:
        if not values:
            return 0.0

        return max(0.0, min(100.0, statistics.mean(values)))


def build_sovereign_sovereignty_assurance_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_governor: Optional[Any] = None,
    operational_command_mesh: Optional[Any] = None,
    autonomous_defense_director: Optional[Any] = None,
    governance_guardrails_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
) -> SovereignSovereigntyAssuranceEngine:
    return SovereignSovereigntyAssuranceEngine(
        event_bus=event_bus,
        operational_governor=operational_governor,
        operational_command_mesh=operational_command_mesh,
        autonomous_defense_director=autonomous_defense_director,
        governance_guardrails_engine=governance_guardrails_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
    )