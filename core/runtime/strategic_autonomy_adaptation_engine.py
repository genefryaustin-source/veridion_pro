"""
core/runtime/strategic_autonomy_adaptation_engine.py

Strategic Autonomy Adaptation Engine

Adaptive sovereign operational autonomy cognition layer.

This subsystem dynamically adapts:
- autonomy modes
- governance strictness
- execution aggressiveness
- survivability prioritization
- stabilization posture
- rollback thresholds
- failover thresholds
- retry posture
- execution restrictions

Based on:
- runtime instability
- survivability degradation
- governance saturation
- predictive collapse risk
- verification degradation
- infrastructure instability
- operational pressure
- autonomy destabilization

IMPORTANT:
This subsystem DOES NOT:
- directly execute containment
- directly mutate runtime infrastructure
- directly perform failovers
- directly trigger destructive actions

It ONLY:
- evaluates operational posture
- adapts runtime autonomy posture
- recommends operational restrictions
- recommends governance escalation
- records replayable adaptation lineage/evidence
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

DEFAULT_ENGINE_NAME = (
    "strategic_autonomy_adaptation_engine"
)

AUTONOMY_LOCKDOWN = "LOCKDOWN"
AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED = (
    "SUPERVISED_AUTONOMY"
)
AUTONOMY_FULL = "FULL_AUTONOMY"

ADAPTATION_STABLE = "STABLE"
ADAPTATION_CONSTRAINED = (
    "CONSTRAINED"
)
ADAPTATION_RESTRICTED = (
    "RESTRICTED"
)
ADAPTATION_SURVIVABILITY = (
    "SURVIVABILITY_MODE"
)
ADAPTATION_LOCKDOWN = (
    "LOCKDOWN_MODE"
)

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_REDUCE_AUTONOMY = (
    "REDUCE_AUTONOMY"
)
RECOMMENDATION_ENABLE_SURVIVABILITY = (
    "ENABLE_SURVIVABILITY_MODE"
)
RECOMMENDATION_ENABLE_LOCKDOWN = (
    "ENABLE_LOCKDOWN_MODE"
)
RECOMMENDATION_GOVERNANCE_ESCALATION = (
    "GOVERNANCE_ESCALATION"
)
RECOMMENDATION_RESTRICT_EXECUTION = (
    "RESTRICT_EXECUTION"
)
RECOMMENDATION_FAILOVER_PREP = (
    "FAILOVER_PREP"
)
RECOMMENDATION_REVIEW = "REVIEW"

DEFAULT_POLICY_PROFILE = (
    "BALANCED"
)


# ============================================================
# ENUMS
# ============================================================

class AdaptationDomain(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    AUTONOMY = "AUTONOMY"
    RESILIENCE = "RESILIENCE"
    TELEMETRY = "TELEMETRY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    TENANT = "TENANT"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class AdaptationSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class AutonomyAdaptationSignal:
    """
    Input adaptation signal.
    """

    adaptation_signal_id: str

    signal_type: str
    domain: str

    source_engine: str
    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    current_autonomy_mode: str = (
        AUTONOMY_SUPERVISED
    )

    governance_pressure_score: float = 0.0
    survivability_risk_score: float = 0.0
    collapse_risk_score: float = 0.0
    verification_risk_score: float = 0.0
    execution_instability_score: float = 0.0
    telemetry_instability_score: float = 0.0
    infrastructure_instability_score: (
        float
    ) = 0.0
    autonomy_destabilization_score: (
        float
    ) = 0.0

    rollback_pressure_score: float = 0.0
    failover_pressure_score: float = 0.0
    retry_pressure_score: float = 0.0

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class StrategicAutonomyAdaptationAssessment:
    """
    Adaptive autonomy assessment.
    """

    assessment_id: str

    adaptation_state: str

    current_autonomy_mode: str
    recommended_autonomy_mode: str

    recommendation: str

    policy_profile: str

    governance_pressure_score: float
    survivability_risk_score: float
    collapse_risk_score: float
    verification_risk_score: float
    execution_instability_score: float
    telemetry_instability_score: float
    infrastructure_instability_score: (
        float
    )
    autonomy_destabilization_score: (
        float
    )

    systemic_operational_pressure_score: (
        float
    )

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    severity: str
    confidence: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    recommended_controls: List[str]
    recommended_restrictions: List[str]
    recommended_actions: List[
        Dict[str, Any]
    ]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class StrategicAutonomyAdaptationSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str

    total_signals_seen: int
    total_assessments_created: int

    last_assessment_id: Optional[str]
    last_adaptation_state: Optional[str]
    last_systemic_runtime_pressure_score: (
        Optional[float]
    )

    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class StrategicAutonomyAdaptationEngine:
    """
    Sovereign adaptive operational cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[
            Any
        ] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: (
            Optional[Any]
        ) = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._signals_seen = 0

        self._assessments: List[
            StrategicAutonomyAdaptationAssessment
        ] = []

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate(
        self,
        signals: Sequence[
            AutonomyAdaptationSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        StrategicAutonomyAdaptationAssessment
    ):
        """
        Evaluate adaptive autonomy posture.
        """

        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:

            assessment = (
                self._empty_assessment(
                    tenant_id=tenant_id,
                    case_id=case_id,
                    correlation_id=correlation_id,
                )
            )

            self._record_assessment(
                assessment,
                context=context,
            )

            return assessment

        selected = (
            self._select_highest_pressure_signal(
                normalized
            )
        )

        governance_pressure = self._avg(
            [
                item
                .governance_pressure_score
                for item in normalized
            ]
        )

        survivability_risk = self._avg(
            [
                item
                .survivability_risk_score
                for item in normalized
            ]
        )

        collapse_risk = self._avg(
            [
                item.collapse_risk_score
                for item in normalized
            ]
        )

        verification_risk = self._avg(
            [
                item
                .verification_risk_score
                for item in normalized
            ]
        )

        execution_instability = self._avg(
            [
                item
                .execution_instability_score
                for item in normalized
            ]
        )

        telemetry_instability = self._avg(
            [
                item
                .telemetry_instability_score
                for item in normalized
            ]
        )

        infrastructure_instability = (
            self._avg(
                [
                    item
                    .infrastructure_instability_score
                    for item in normalized
                ]
            )
        )

        autonomy_destabilization = (
            self._avg(
                [
                    item
                    .autonomy_destabilization_score
                    for item in normalized
                ]
            )
        )

        systemic_pressure = (
            self._systemic_pressure(
                normalized
            )
        )

        adaptation_state = (
            self._adaptation_state(
                systemic_pressure=(
                    systemic_pressure
                ),
                collapse_risk=(
                    collapse_risk
                ),
                survivability_risk=(
                    survivability_risk
                ),
            )
        )

        recommendation = (
            self._recommendation(
                adaptation_state=(
                    adaptation_state
                ),
                collapse_risk=(
                    collapse_risk
                ),
                governance_pressure=(
                    governance_pressure
                ),
                survivability_risk=(
                    survivability_risk
                ),
            )
        )

        current_mode = (
            selected
            .current_autonomy_mode
        )

        recommended_mode = (
            self._recommended_mode(
                current_mode=current_mode,
                recommendation=(
                    recommendation
                ),
                adaptation_state=(
                    adaptation_state
                ),
            )
        )

        policy_profile = (
            self._policy_profile(
                adaptation_state=(
                    adaptation_state
                ),
                survivability_risk=(
                    survivability_risk
                ),
                governance_pressure=(
                    governance_pressure
                ),
            )
        )

        assessment = (
            StrategicAutonomyAdaptationAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                adaptation_state=(
                    adaptation_state
                ),
                current_autonomy_mode=(
                    current_mode
                ),
                recommended_autonomy_mode=(
                    recommended_mode
                ),
                recommendation=(
                    recommendation
                ),
                policy_profile=(
                    policy_profile
                ),
                governance_pressure_score=(
                    governance_pressure
                ),
                survivability_risk_score=(
                    survivability_risk
                ),
                collapse_risk_score=(
                    collapse_risk
                ),
                verification_risk_score=(
                    verification_risk
                ),
                execution_instability_score=(
                    execution_instability
                ),
                telemetry_instability_score=(
                    telemetry_instability
                ),
                infrastructure_instability_score=(
                    infrastructure_instability
                ),
                autonomy_destabilization_score=(
                    autonomy_destabilization
                ),
                systemic_operational_pressure_score=(
                    systemic_pressure
                ),
                selected_signal_id=(
                    selected
                    .adaptation_signal_id
                ),
                selected_signal_type=(
                    selected.signal_type
                ),
                severity=selected.severity,
                confidence=selected.confidence,
                tenant_id=(
                    tenant_id
                    or selected.tenant_id
                ),
                case_id=(
                    case_id
                    or selected.case_id
                ),
                correlation_id=(
                    correlation_id
                    or selected.correlation_id
                ),
                recommended_controls=(
                    self._recommended_controls(
                        adaptation_state=(
                            adaptation_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                recommended_restrictions=(
                    self
                    ._recommended_restrictions(
                        adaptation_state=(
                            adaptation_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                recommended_actions=(
                    self._recommended_actions(
                        recommendation=(
                            recommendation
                        ),
                        recommended_mode=(
                            recommended_mode
                        ),
                        adaptation_state=(
                            adaptation_state
                        ),
                    )
                ),
                rationale=self._build_rationale(
                    selected=selected,
                    adaptation_state=(
                        adaptation_state
                    ),
                    recommendation=(
                        recommendation
                    ),
                    policy_profile=(
                        policy_profile
                    ),
                    recommended_mode=(
                        recommended_mode
                    ),
                    governance_pressure=(
                        governance_pressure
                    ),
                    survivability_risk=(
                        survivability_risk
                    ),
                    collapse_risk=(
                        collapse_risk
                    ),
                    verification_risk=(
                        verification_risk
                    ),
                    execution_instability=(
                        execution_instability
                    ),
                    telemetry_instability=(
                        telemetry_instability
                    ),
                    infrastructure_instability=(
                        infrastructure_instability
                    ),
                    autonomy_destabilization=(
                        autonomy_destabilization
                    ),
                    systemic_pressure=(
                        systemic_pressure
                    ),
                    signal_count=len(
                        normalized
                    ),
                ),
                metadata={
                    "evaluated_signal_ids": [
                        item
                        .adaptation_signal_id
                        for item in normalized
                    ],
                    "source_engines": sorted(
                        {
                            item.source_engine
                            for item in normalized
                        }
                    ),
                },
            )
        )

        self._record_assessment(
            assessment,
            context=context,
        )

        return assessment

    def submit(
        self,
        signals: Sequence[
            AutonomyAdaptationSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        StrategicAutonomyAdaptationAssessment
    ):

        return self.evaluate(
            signals,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            context=context,
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[
        StrategicAutonomyAdaptationAssessment
    ]:

        limit = max(1, int(limit))

        return list(
            reversed(
                self._assessments[-limit:]
            )
        )

    def snapshot(
        self,
    ) -> (
        StrategicAutonomyAdaptationSnapshot
    ):

        latest = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            StrategicAutonomyAdaptationSnapshot(
                engine_name=self.engine_name,
                total_signals_seen=(
                    self._signals_seen
                ),
                total_assessments_created=len(
                    self._assessments
                ),
                last_assessment_id=(
                    latest.assessment_id
                    if latest
                    else None
                ),
                last_adaptation_state=(
                    latest.adaptation_state
                    if latest
                    else None
                ),
                last_systemic_runtime_pressure_score=(
                    latest
                    .systemic_operational_pressure_score
                    if latest
                    else None
                ),
                last_updated_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # ========================================================
    # INTERNAL SCORING
    # ========================================================

    def _systemic_pressure(
        self,
        signals: Sequence[
            AutonomyAdaptationSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item
                .governance_pressure_score
            )

            total += (
                item
                .survivability_risk_score
            )

            total += (
                item
                .collapse_risk_score
            )

            total += (
                item
                .verification_risk_score
            )

            total += (
                item
                .execution_instability_score
            )

            total += (
                item
                .telemetry_instability_score
            )

            total += (
                item
                .infrastructure_instability_score
            )

            total += (
                item
                .autonomy_destabilization_score
            )

        return self._clamp_score(
            total / (max(1, len(signals)) * 8)
        )

    def _adaptation_state(
        self,
        *,
        systemic_pressure: float,
        collapse_risk: float,
        survivability_risk: float,
    ) -> str:

        if (
            collapse_risk >= 85
            or systemic_pressure >= 90
        ):
            return ADAPTATION_LOCKDOWN

        if (
            survivability_risk >= 75
            or systemic_pressure >= 75
        ):
            return (
                ADAPTATION_SURVIVABILITY
            )

        if systemic_pressure >= 60:
            return (
                ADAPTATION_RESTRICTED
            )

        if systemic_pressure >= 35:
            return (
                ADAPTATION_CONSTRAINED
            )

        return ADAPTATION_STABLE

    def _recommendation(
        self,
        *,
        adaptation_state: str,
        collapse_risk: float,
        governance_pressure: float,
        survivability_risk: float,
    ) -> str:

        if (
            adaptation_state
            == ADAPTATION_LOCKDOWN
        ):
            return (
                RECOMMENDATION_ENABLE_LOCKDOWN
            )

        if (
            adaptation_state
            == ADAPTATION_SURVIVABILITY
        ):
            return (
                RECOMMENDATION_ENABLE_SURVIVABILITY
            )

        if collapse_risk >= 70:
            return (
                RECOMMENDATION_FAILOVER_PREP
            )

        if governance_pressure >= 70:
            return (
                RECOMMENDATION_GOVERNANCE_ESCALATION
            )

        if survivability_risk >= 60:
            return (
                RECOMMENDATION_RESTRICT_EXECUTION
            )

        if (
            adaptation_state
            in {
                ADAPTATION_RESTRICTED,
                ADAPTATION_CONSTRAINED,
            }
        ):
            return (
                RECOMMENDATION_REDUCE_AUTONOMY
            )

        return RECOMMENDATION_NONE

    def _recommended_mode(
        self,
        *,
        current_mode: str,
        recommendation: str,
        adaptation_state: str,
    ) -> str:

        current_mode = (
            self._safe_autonomy_mode(
                current_mode
            )
        )

        if (
            recommendation
            == RECOMMENDATION_ENABLE_LOCKDOWN
        ):
            return AUTONOMY_LOCKDOWN

        if (
            recommendation
            == RECOMMENDATION_ENABLE_SURVIVABILITY
        ):
            return AUTONOMY_MANUAL

        if (
            recommendation
            in {
                RECOMMENDATION_REDUCE_AUTONOMY,
                RECOMMENDATION_RESTRICT_EXECUTION,
            }
        ):
            return self._reduce_mode(
                current_mode
            )

        return current_mode

    def _policy_profile(
        self,
        *,
        adaptation_state: str,
        survivability_risk: float,
        governance_pressure: float,
    ) -> str:

        if (
            adaptation_state
            == ADAPTATION_LOCKDOWN
        ):
            return "LOCKDOWN"

        if survivability_risk >= 75:
            return "SURVIVABILITY_FIRST"

        if governance_pressure >= 70:
            return (
                "GOVERNANCE_ESCALATED"
            )

        if (
            adaptation_state
            == ADAPTATION_RESTRICTED
        ):
            return (
                "CONSERVATIVE_EXECUTION"
            )

        return DEFAULT_POLICY_PROFILE

    # ========================================================
    # OUTPUT BUILDERS
    # ========================================================

    def _recommended_controls(
        self,
        *,
        adaptation_state: str,
        recommendation: str,
    ) -> List[str]:

        controls = [
            "lineage_recording",
            "evidence_recording",
        ]

        if (
            adaptation_state
            != ADAPTATION_STABLE
        ):
            controls.append(
                "operator_review"
            )

        if recommendation in {
            RECOMMENDATION_ENABLE_LOCKDOWN,
            RECOMMENDATION_GOVERNANCE_ESCALATION,
        }:
            controls.append(
                "governance_review"
            )

        return list(
            dict.fromkeys(controls)
        )

    def _recommended_restrictions(
        self,
        *,
        adaptation_state: str,
        recommendation: str,
    ) -> List[str]:

        restrictions: List[str] = []

        if (
            adaptation_state
            == ADAPTATION_CONSTRAINED
        ):
            restrictions.append(
                "reduced_execution_aggressiveness"
            )

        if (
            adaptation_state
            == ADAPTATION_RESTRICTED
        ):
            restrictions.extend(
                [
                    "restricted_connector_execution",
                    "restricted_failovers",
                    "restricted_retry_behavior",
                ]
            )

        if (
            adaptation_state
            == ADAPTATION_SURVIVABILITY
        ):
            restrictions.extend(
                [
                    "survivability_priority_execution",
                    "manual_governance_review",
                    "reduced_autonomous_actions",
                ]
            )

        if (
            adaptation_state
            == ADAPTATION_LOCKDOWN
        ):
            restrictions.extend(
                [
                    "autonomous_execution_frozen",
                    "manual_override_required",
                    "high_risk_actions_disabled",
                ]
            )

        return list(
            dict.fromkeys(restrictions)
        )

    def _recommended_actions(
        self,
        *,
        recommendation: str,
        recommended_mode: str,
        adaptation_state: str,
    ) -> List[Dict[str, Any]]:

        actions: List[
            Dict[str, Any]
        ] = []

        actions.append(
            {
                "action": (
                    "record_adaptation_lineage"
                )
            }
        )

        actions.append(
            {
                "action": (
                    "record_adaptation_evidence"
                )
            }
        )

        if (
            recommendation
            != RECOMMENDATION_NONE
        ):
            actions.append(
                {
                    "action": (
                        "review_runtime_autonomy"
                    ),
                    "recommended_mode": (
                        recommended_mode
                    ),
                }
            )

        if (
            adaptation_state
            == ADAPTATION_SURVIVABILITY
        ):
            actions.append(
                {
                    "action": (
                        "prioritize_survivability"
                    )
                }
            )

        if (
            adaptation_state
            == ADAPTATION_LOCKDOWN
        ):
            actions.append(
                {
                    "action": (
                        "prepare_lockdown_controls"
                    )
                }
            )

        return actions

    def _build_rationale(
        self,
        *,
        selected: (
            AutonomyAdaptationSignal
        ),
        adaptation_state: str,
        recommendation: str,
        policy_profile: str,
        recommended_mode: str,
        governance_pressure: float,
        survivability_risk: float,
        collapse_risk: float,
        verification_risk: float,
        execution_instability: float,
        telemetry_instability: float,
        infrastructure_instability: float,
        autonomy_destabilization: float,
        systemic_pressure: float,
        signal_count: int,
    ) -> str:

        return (
            f"Strategic autonomy adaptation "
            f"assessment generated from "
            f"{selected.signal_type}. "
            f"Adaptation state "
            f"{adaptation_state}; "
            f"recommendation "
            f"{recommendation}; "
            f"policy profile "
            f"{policy_profile}; "
            f"recommended autonomy "
            f"{recommended_mode}. "
            f"Governance pressure "
            f"{governance_pressure:.2f}; "
            f"survivability risk "
            f"{survivability_risk:.2f}; "
            f"collapse risk "
            f"{collapse_risk:.2f}; "
            f"verification risk "
            f"{verification_risk:.2f}; "
            f"execution instability "
            f"{execution_instability:.2f}; "
            f"telemetry instability "
            f"{telemetry_instability:.2f}; "
            f"infrastructure instability "
            f"{infrastructure_instability:.2f}; "
            f"autonomy destabilization "
            f"{autonomy_destabilization:.2f}; "
            f"systemic operational pressure "
            f"{systemic_pressure:.2f}. "
            f"Evaluated across "
            f"{signal_count} signal(s)."
        )

    # ========================================================
    # RECORDING
    # ========================================================

    def _record_assessment(
        self,
        assessment: (
            StrategicAutonomyAdaptationAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

        self._write_to_memory(
            assessment,
            context=context,
        )

        self._write_to_lineage(
            assessment,
            context=context,
        )

        self._write_to_evidence(
            assessment,
            context=context,
        )

        self._emit_event(
            assessment,
            context=context,
        )

    def _write_to_memory(
        self,
        assessment: (
            StrategicAutonomyAdaptationAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        memory = (
            self.operational_memory_engine
        )

        if memory is None:
            return

        payload = {
            "type": (
                "STRATEGIC_AUTONOMY_ADAPTATION_ASSESSMENT"
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                memory,
                "append_memory",
            ):
                memory.append_memory(
                    payload
                )

            elif hasattr(
                memory,
                "record",
            ):
                memory.record(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Adaptation memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            StrategicAutonomyAdaptationAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        lineage = self.lineage_engine

        if lineage is None:
            return

        payload = {
            "lineage_type": (
                "AUTONOMY_ADAPTATION"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "context": {
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                lineage,
                "record_lineage",
            ):
                lineage.record_lineage(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Adaptation lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            StrategicAutonomyAdaptationAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        evidence = (
            self
            .fedramp_evidence_lineage_engine
        )

        if evidence is None:
            return

        payload = {
            "evidence_type": (
                "AUTONOMY_ADAPTATION"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "evidence_payload": {
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                evidence,
                "record_evidence",
            ):
                evidence.record_evidence(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Adaptation evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            StrategicAutonomyAdaptationAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.event_bus is None:
            return

        payload = {
            "event_type": (
                "STRATEGIC_AUTONOMY_ADAPTATION_ASSESSMENT"
            ),
            "engine_name": (
                self.engine_name
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                self.event_bus,
                "emit",
            ):
                self.event_bus.emit(
                    (
                        "STRATEGIC_AUTONOMY_ADAPTATION_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Adaptation event emit failed: {exc}"
            )

    # ========================================================
    # HELPERS
    # ========================================================

    def _select_highest_pressure_signal(
        self,
        signals: Sequence[
            AutonomyAdaptationSignal
        ],
    ) -> (
        AutonomyAdaptationSignal
    ):

        return sorted(
            signals,
            key=lambda item: (
                item
                .collapse_risk_score,
                item
                .survivability_risk_score,
                item
                .governance_pressure_score,
                item
                .execution_instability_score,
                item
                .autonomy_destabilization_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _normalize_signal(
        self,
        item: (
            AutonomyAdaptationSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        AutonomyAdaptationSignal
    ):

        if isinstance(
            item,
            AutonomyAdaptationSignal,
        ):
            return item

        return (
            AutonomyAdaptationSignal(
                adaptation_signal_id=str(
                    item.get(
                        "adaptation_signal_id"
                    )
                    or uuid.uuid4()
                ),
                signal_type=str(
                    item.get(
                        "signal_type"
                    )
                    or "UNKNOWN"
                ),
                domain=self._safe_domain(
                    item.get("domain")
                ),
                source_engine=str(
                    item.get(
                        "source_engine"
                    )
                    or "unknown_engine"
                ),
                severity=self._safe_severity(
                    item.get("severity")
                ),
                confidence=(
                    self._clamp_confidence(
                        item.get(
                            "confidence",
                            0.0,
                        )
                    )
                ),
                summary=str(
                    item.get("summary")
                    or ""
                ),
                tenant_id=(
                    tenant_id
                    or item.get(
                        "tenant_id"
                    )
                ),
                case_id=(
                    case_id
                    or item.get(
                        "case_id"
                    )
                ),
                correlation_id=(
                    correlation_id
                    or item.get(
                        "correlation_id"
                    )
                ),
                current_autonomy_mode=(
                    self
                    ._safe_autonomy_mode(
                        item.get(
                            "current_autonomy_mode"
                        )
                    )
                ),
                governance_pressure_score=(
                    self._clamp_score(
                        item.get(
                            "governance_pressure_score",
                            0.0,
                        )
                    )
                ),
                survivability_risk_score=(
                    self._clamp_score(
                        item.get(
                            "survivability_risk_score",
                            0.0,
                        )
                    )
                ),
                collapse_risk_score=(
                    self._clamp_score(
                        item.get(
                            "collapse_risk_score",
                            0.0,
                        )
                    )
                ),
                verification_risk_score=(
                    self._clamp_score(
                        item.get(
                            "verification_risk_score",
                            0.0,
                        )
                    )
                ),
                execution_instability_score=(
                    self._clamp_score(
                        item.get(
                            "execution_instability_score",
                            0.0,
                        )
                    )
                ),
                telemetry_instability_score=(
                    self._clamp_score(
                        item.get(
                            "telemetry_instability_score",
                            0.0,
                        )
                    )
                ),
                infrastructure_instability_score=(
                    self._clamp_score(
                        item.get(
                            "infrastructure_instability_score",
                            0.0,
                        )
                    )
                ),
                autonomy_destabilization_score=(
                    self._clamp_score(
                        item.get(
                            "autonomy_destabilization_score",
                            0.0,
                        )
                    )
                ),
                rollback_pressure_score=(
                    self._clamp_score(
                        item.get(
                            "rollback_pressure_score",
                            0.0,
                        )
                    )
                ),
                failover_pressure_score=(
                    self._clamp_score(
                        item.get(
                            "failover_pressure_score",
                            0.0,
                        )
                    )
                ),
                retry_pressure_score=(
                    self._clamp_score(
                        item.get(
                            "retry_pressure_score",
                            0.0,
                        )
                    )
                ),
                payload=dict(
                    item.get(
                        "payload",
                        {},
                    )
                    or {}
                ),
            )
        )

    def _empty_assessment(
        self,
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        StrategicAutonomyAdaptationAssessment
    ):

        return (
            StrategicAutonomyAdaptationAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                adaptation_state=(
                    ADAPTATION_STABLE
                ),
                current_autonomy_mode=(
                    AUTONOMY_SUPERVISED
                ),
                recommended_autonomy_mode=(
                    AUTONOMY_SUPERVISED
                ),
                recommendation=(
                    RECOMMENDATION_NONE
                ),
                policy_profile=(
                    DEFAULT_POLICY_PROFILE
                ),
                governance_pressure_score=0.0,
                survivability_risk_score=0.0,
                collapse_risk_score=0.0,
                verification_risk_score=0.0,
                execution_instability_score=0.0,
                telemetry_instability_score=0.0,
                infrastructure_instability_score=0.0,
                autonomy_destabilization_score=0.0,
                systemic_operational_pressure_score=0.0,
                selected_signal_id=None,
                selected_signal_type=None,
                severity=(
                    AdaptationSeverity
                    .INFO.value
                ),
                confidence=1.0,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
                recommended_controls=[
                    "lineage_recording",
                    "evidence_recording",
                ],
                recommended_restrictions=[],
                recommended_actions=[
                    {
                        "action": (
                            "continue_runtime_operations"
                        )
                    }
                ],
                rationale=(
                    "No adaptation signals "
                    "submitted."
                ),
                metadata={},
            )
        )

    @staticmethod
    def _avg(
        values: Sequence[float],
    ) -> float:

        if not values:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                sum(values)
                / len(values),
            ),
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or AdaptationDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                AdaptationDomain
            )
        }

        return (
            value
            if value in valid
            else (
                AdaptationDomain
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or AdaptationSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in (
                AdaptationSeverity
            )
        }

        return (
            value
            if value in valid
            else (
                AdaptationSeverity
                .INFO.value
            )
        )

    @staticmethod
    def _safe_autonomy_mode(
        value: Any,
    ) -> str:

        value = str(
            value
            or AUTONOMY_SUPERVISED
        ).upper()

        valid = {
            AUTONOMY_LOCKDOWN,
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED,
            AUTONOMY_FULL,
        }

        return (
            value
            if value in valid
            else AUTONOMY_SUPERVISED
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

    @staticmethod
    def _clamp_score(
        value: Any,
    ) -> float:

        try:
            score = float(value)

        except Exception:
            score = 0.0

        return max(
            0.0,
            min(100.0, score),
        )

    @staticmethod
    def _reduce_mode(
        current: str,
    ) -> str:

        order = [
            AUTONOMY_LOCKDOWN,
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED,
            AUTONOMY_FULL,
        ]

        current = str(
            current
            or AUTONOMY_SUPERVISED
        ).upper()

        if current not in order:
            return AUTONOMY_ASSISTED

        idx = order.index(current)

        return order[
            max(0, idx - 1)
        ]


# ============================================================
# FACTORY
# ============================================================

def build_strategic_autonomy_adaptation_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> (
    StrategicAutonomyAdaptationEngine
):
    """
    Factory for explicit dependency injection.
    """

    return (
        StrategicAutonomyAdaptationEngine(
            event_bus=event_bus,
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )