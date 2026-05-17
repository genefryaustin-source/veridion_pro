"""
core/runtime/runtime_governance_heatmap.py

Runtime Governance Heatmap

Backend heatmap cognition layer for:
- governance pressure
- autonomy pressure
- survivability pressure
- execution instability
- connector instability
- telemetry degradation
- tenant stress
- collapse-risk concentration

IMPORTANT:
This module DOES NOT render UI directly.
It produces structured heatmap models for Command Center panels.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_HEATMAP_NAME = "runtime_governance_heatmap"

HEAT_LOW = "LOW"
HEAT_MEDIUM = "MEDIUM"
HEAT_HIGH = "HIGH"
HEAT_CRITICAL = "CRITICAL"
HEAT_UNKNOWN = "UNKNOWN"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_REVIEW = "REVIEW"
RECOMMENDATION_ESCALATE = "ESCALATE"
RECOMMENDATION_STABILIZE = "STABILIZE"
RECOMMENDATION_FREEZE_REVIEW = "FREEZE_REVIEW"
RECOMMENDATION_TENANT_ISOLATION_REVIEW = "TENANT_ISOLATION_REVIEW"


class HeatmapDomain(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    AUTONOMY = "AUTONOMY"
    EXECUTION = "EXECUTION"
    VERIFICATION = "VERIFICATION"
    CONNECTOR = "CONNECTOR"
    TELEMETRY = "TELEMETRY"
    RESILIENCE = "RESILIENCE"
    TENANT = "TENANT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class HeatmapSignalType(str, Enum):
    GOVERNANCE_PRESSURE = "GOVERNANCE_PRESSURE"
    APPROVAL_SATURATION = "APPROVAL_SATURATION"
    ESCALATION_HOTSPOT = "ESCALATION_HOTSPOT"
    ROLLBACK_HOTSPOT = "ROLLBACK_HOTSPOT"
    AUTONOMY_PRESSURE = "AUTONOMY_PRESSURE"
    EXECUTION_INSTABILITY = "EXECUTION_INSTABILITY"
    VERIFICATION_INSTABILITY = "VERIFICATION_INSTABILITY"
    CONNECTOR_INSTABILITY = "CONNECTOR_INSTABILITY"
    TELEMETRY_DEGRADATION = "TELEMETRY_DEGRADATION"
    SURVIVABILITY_DECLINE = "SURVIVABILITY_DECLINE"
    COLLAPSE_RISK = "COLLAPSE_RISK"
    TENANT_STRESS = "TENANT_STRESS"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeHeatmapSignal:
    heatmap_signal_id: str
    signal_type: str
    domain: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None
    node_id: Optional[str] = None
    node_name: Optional[str] = None
    connector_name: Optional[str] = None

    governance_pressure: float = 0.0
    autonomy_pressure: float = 0.0
    execution_pressure: float = 0.0
    verification_pressure: float = 0.0
    connector_pressure: float = 0.0
    telemetry_pressure: float = 0.0
    resilience_pressure: float = 0.0
    survivability_pressure: float = 0.0
    collapse_risk: float = 0.0

    approval_count: int = 0
    escalation_count: int = 0
    rollback_count: int = 0
    failover_count: int = 0
    contradiction_count: int = 0
    degraded_node_count: int = 0
    unstable_node_count: int = 0
    failed_node_count: int = 0

    payload: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class RuntimeHeatmapCell:
    cell_id: str
    label: str
    domain: str
    heat_level: str
    heat_score: float
    risk_score: float
    pressure_score: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    node_id: Optional[str]
    node_name: Optional[str]
    connector_name: Optional[str]

    primary_signal_type: Optional[str]
    recommended_action: str
    constraints: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class RuntimeGovernanceHeatmapAssessment:
    assessment_id: str
    heatmap_name: str
    overall_heat_level: str
    overall_heat_score: float
    governance_heat_score: float
    autonomy_heat_score: float
    execution_heat_score: float
    survivability_heat_score: float
    telemetry_heat_score: float
    collapse_risk_score: float

    cells: List[RuntimeHeatmapCell]
    hotspots: List[RuntimeHeatmapCell]

    recommendation: str
    recommended_actions: List[Dict[str, Any]]
    required_controls: List[str]
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class RuntimeGovernanceHeatmapSnapshot:
    heatmap_name: str
    total_signals_seen: int
    total_assessments_created: int
    last_assessment_id: Optional[str]
    last_overall_heat_level: Optional[str]
    last_overall_heat_score: Optional[float]
    last_updated_ms: int


class RuntimeGovernanceHeatmap:
    """
    Produces backend heatmap assessments for Command Center visualization.
    """

    def __init__(
        self,
        *,
        heatmap_name: str = DEFAULT_HEATMAP_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:
        self.heatmap_name = heatmap_name
        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._signals_seen = 0
        self._assessments: List[RuntimeGovernanceHeatmapAssessment] = []

    def evaluate(
        self,
        signals: Sequence[RuntimeHeatmapSignal | Dict[str, Any]],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> RuntimeGovernanceHeatmapAssessment:
        normalized = [self._normalize_signal(item) for item in signals]
        self._signals_seen += len(normalized)

        if not normalized:
            assessment = self._empty_assessment()
            self._record_assessment(assessment, context=context)
            return assessment

        cells = [self._cell_from_signal(signal) for signal in normalized]
        hotspots = sorted(
            [cell for cell in cells if cell.heat_level in {HEAT_HIGH, HEAT_CRITICAL}],
            key=lambda cell: cell.heat_score,
            reverse=True,
        )

        governance_heat = self._avg([s.governance_pressure for s in normalized])
        autonomy_heat = self._avg([s.autonomy_pressure for s in normalized])
        execution_heat = self._avg([s.execution_pressure for s in normalized])
        survivability_heat = self._avg(
            [max(s.survivability_pressure, s.resilience_pressure) for s in normalized]
        )
        telemetry_heat = self._avg([s.telemetry_pressure for s in normalized])
        collapse_risk = self._avg([s.collapse_risk for s in normalized])

        overall = self._clamp_score(
            (
                governance_heat
                + autonomy_heat
                + execution_heat
                + survivability_heat
                + telemetry_heat
                + collapse_risk
            )
            / 6
        )

        overall_level = self._heat_level(overall)
        recommendation = self._recommendation(overall_level, collapse_risk)

        assessment = RuntimeGovernanceHeatmapAssessment(
            assessment_id=str(uuid.uuid4()),
            heatmap_name=self.heatmap_name,
            overall_heat_level=overall_level,
            overall_heat_score=overall,
            governance_heat_score=governance_heat,
            autonomy_heat_score=autonomy_heat,
            execution_heat_score=execution_heat,
            survivability_heat_score=survivability_heat,
            telemetry_heat_score=telemetry_heat,
            collapse_risk_score=collapse_risk,
            cells=cells,
            hotspots=hotspots[:25],
            recommendation=recommendation,
            recommended_actions=self._recommended_actions(
                overall_level=overall_level,
                recommendation=recommendation,
                hotspots=hotspots,
            ),
            required_controls=self._required_controls(overall_level, recommendation),
            rationale=(
                f"Runtime governance heatmap evaluated {len(normalized)} signal(s). "
                f"Overall heat {overall:.2f} ({overall_level}); governance "
                f"{governance_heat:.2f}; autonomy {autonomy_heat:.2f}; execution "
                f"{execution_heat:.2f}; survivability {survivability_heat:.2f}; "
                f"telemetry {telemetry_heat:.2f}; collapse risk {collapse_risk:.2f}."
            ),
            metadata={
                "signal_ids": [signal.heatmap_signal_id for signal in normalized],
                "hotspot_count": len(hotspots),
                "domains": sorted({signal.domain for signal in normalized}),
                "tenants": sorted({signal.tenant_id for signal in normalized if signal.tenant_id}),
            },
        )

        self._record_assessment(assessment, context=context)
        return assessment

    def submit(
        self,
        signals: Sequence[RuntimeHeatmapSignal | Dict[str, Any]],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> RuntimeGovernanceHeatmapAssessment:
        return self.evaluate(signals, context=context)

    def create_signal(
        self,
        *,
        signal_type: str,
        domain: str,
        source_engine: str,
        severity: str,
        confidence: float,
        summary: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        node_id: Optional[str] = None,
        node_name: Optional[str] = None,
        connector_name: Optional[str] = None,
        governance_pressure: float = 0.0,
        autonomy_pressure: float = 0.0,
        execution_pressure: float = 0.0,
        verification_pressure: float = 0.0,
        connector_pressure: float = 0.0,
        telemetry_pressure: float = 0.0,
        resilience_pressure: float = 0.0,
        survivability_pressure: float = 0.0,
        collapse_risk: float = 0.0,
        approval_count: int = 0,
        escalation_count: int = 0,
        rollback_count: int = 0,
        failover_count: int = 0,
        contradiction_count: int = 0,
        degraded_node_count: int = 0,
        unstable_node_count: int = 0,
        failed_node_count: int = 0,
        payload: Optional[Dict[str, Any]] = None,
    ) -> RuntimeHeatmapSignal:
        return RuntimeHeatmapSignal(
            heatmap_signal_id=str(uuid.uuid4()),
            signal_type=self._safe_signal_type(signal_type),
            domain=self._safe_domain(domain),
            source_engine=source_engine or "unknown_engine",
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            summary=summary or "",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            node_id=node_id,
            node_name=node_name,
            connector_name=connector_name,
            governance_pressure=self._clamp_score(governance_pressure),
            autonomy_pressure=self._clamp_score(autonomy_pressure),
            execution_pressure=self._clamp_score(execution_pressure),
            verification_pressure=self._clamp_score(verification_pressure),
            connector_pressure=self._clamp_score(connector_pressure),
            telemetry_pressure=self._clamp_score(telemetry_pressure),
            resilience_pressure=self._clamp_score(resilience_pressure),
            survivability_pressure=self._clamp_score(survivability_pressure),
            collapse_risk=self._clamp_score(collapse_risk),
            approval_count=max(0, int(approval_count)),
            escalation_count=max(0, int(escalation_count)),
            rollback_count=max(0, int(rollback_count)),
            failover_count=max(0, int(failover_count)),
            contradiction_count=max(0, int(contradiction_count)),
            degraded_node_count=max(0, int(degraded_node_count)),
            unstable_node_count=max(0, int(unstable_node_count)),
            failed_node_count=max(0, int(failed_node_count)),
            payload=dict(payload or {}),
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[RuntimeGovernanceHeatmapAssessment]:
        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    def snapshot(self) -> RuntimeGovernanceHeatmapSnapshot:
        last = self._assessments[-1] if self._assessments else None
        return RuntimeGovernanceHeatmapSnapshot(
            heatmap_name=self.heatmap_name,
            total_signals_seen=self._signals_seen,
            total_assessments_created=len(self._assessments),
            last_assessment_id=last.assessment_id if last else None,
            last_overall_heat_level=last.overall_heat_level if last else None,
            last_overall_heat_score=last.overall_heat_score if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    def _cell_from_signal(self, signal: RuntimeHeatmapSignal) -> RuntimeHeatmapCell:
        pressure = self._clamp_score(
            (
                signal.governance_pressure
                + signal.autonomy_pressure
                + signal.execution_pressure
                + signal.verification_pressure
                + signal.connector_pressure
                + signal.telemetry_pressure
                + signal.resilience_pressure
                + signal.survivability_pressure
                + signal.collapse_risk
            )
            / 9
        )

        count_pressure = min(
            100.0,
            (
                signal.approval_count
                + signal.escalation_count * 2
                + signal.rollback_count * 2
                + signal.failover_count * 2
                + signal.contradiction_count * 3
                + signal.degraded_node_count * 2
                + signal.unstable_node_count * 3
                + signal.failed_node_count * 4
            ),
        )

        heat_score = self._clamp_score((pressure * 0.75) + (count_pressure * 0.25))
        heat_level = self._heat_level(heat_score)

        label = (
            signal.node_name
            or signal.connector_name
            or signal.tenant_id
            or signal.domain
            or "UNKNOWN"
        )

        return RuntimeHeatmapCell(
            cell_id=str(uuid.uuid4()),
            label=label,
            domain=signal.domain,
            heat_level=heat_level,
            heat_score=heat_score,
            risk_score=self._clamp_score(max(signal.collapse_risk, signal.survivability_pressure)),
            pressure_score=pressure,
            tenant_id=signal.tenant_id,
            case_id=signal.case_id,
            node_id=signal.node_id,
            node_name=signal.node_name,
            connector_name=signal.connector_name,
            primary_signal_type=signal.signal_type,
            recommended_action=self._cell_recommendation(heat_level, signal),
            constraints=self._cell_constraints(heat_level, signal),
            metadata={
                "source_engine": signal.source_engine,
                "severity": signal.severity,
                "confidence": signal.confidence,
                "summary": signal.summary,
                "correlation_id": signal.correlation_id,
                "counts": {
                    "approval_count": signal.approval_count,
                    "escalation_count": signal.escalation_count,
                    "rollback_count": signal.rollback_count,
                    "failover_count": signal.failover_count,
                    "contradiction_count": signal.contradiction_count,
                    "degraded_node_count": signal.degraded_node_count,
                    "unstable_node_count": signal.unstable_node_count,
                    "failed_node_count": signal.failed_node_count,
                },
            },
        )

    def _cell_recommendation(
        self,
        heat_level: str,
        signal: RuntimeHeatmapSignal,
    ) -> str:
        if heat_level == HEAT_CRITICAL:
            if signal.tenant_id and signal.signal_type == HeatmapSignalType.TENANT_STRESS.value:
                return RECOMMENDATION_TENANT_ISOLATION_REVIEW
            if signal.collapse_risk >= 75:
                return RECOMMENDATION_FREEZE_REVIEW
            return RECOMMENDATION_STABILIZE

        if heat_level == HEAT_HIGH:
            return RECOMMENDATION_ESCALATE

        if heat_level == HEAT_MEDIUM:
            return RECOMMENDATION_REVIEW

        if heat_level == HEAT_LOW:
            return RECOMMENDATION_MONITOR

        return RECOMMENDATION_NONE

    def _cell_constraints(
        self,
        heat_level: str,
        signal: RuntimeHeatmapSignal,
    ) -> List[str]:
        constraints: List[str] = [f"heat_level_{heat_level.lower()}"]

        if signal.governance_pressure >= 70:
            constraints.append("governance_hotspot")

        if signal.autonomy_pressure >= 70:
            constraints.append("autonomy_hotspot")

        if signal.execution_pressure >= 70:
            constraints.append("execution_hotspot")

        if signal.verification_pressure >= 70:
            constraints.append("verification_hotspot")

        if signal.connector_pressure >= 70:
            constraints.append("connector_hotspot")

        if signal.telemetry_pressure >= 70:
            constraints.append("telemetry_hotspot")

        if signal.collapse_risk >= 70:
            constraints.append("collapse_risk_hotspot")

        if signal.failed_node_count:
            constraints.append("failed_nodes_present")

        return list(dict.fromkeys(constraints))

    def _recommendation(self, overall_level: str, collapse_risk: float) -> str:
        if overall_level == HEAT_CRITICAL:
            return RECOMMENDATION_FREEZE_REVIEW if collapse_risk >= 75 else RECOMMENDATION_STABILIZE
        if overall_level == HEAT_HIGH:
            return RECOMMENDATION_ESCALATE
        if overall_level == HEAT_MEDIUM:
            return RECOMMENDATION_REVIEW
        if overall_level == HEAT_LOW:
            return RECOMMENDATION_MONITOR
        return RECOMMENDATION_NONE

    def _recommended_actions(
        self,
        *,
        overall_level: str,
        recommendation: str,
        hotspots: List[RuntimeHeatmapCell],
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        if recommendation == RECOMMENDATION_FREEZE_REVIEW:
            actions.append({"action": "review_runtime_freeze", "reason": "Critical heat detected."})

        if recommendation == RECOMMENDATION_STABILIZE:
            actions.append({"action": "prepare_runtime_stabilization"})

        if recommendation == RECOMMENDATION_ESCALATE:
            actions.append({"action": "escalate_hotspots", "hotspot_count": len(hotspots)})

        if recommendation == RECOMMENDATION_REVIEW:
            actions.append({"action": "review_heatmap_hotspots", "hotspot_count": len(hotspots)})

        if recommendation == RECOMMENDATION_MONITOR:
            actions.append({"action": "continue_monitoring"})

        actions.append({"action": "record_heatmap_lineage"})
        actions.append({"action": "record_heatmap_evidence"})

        return actions

    def _required_controls(self, overall_level: str, recommendation: str) -> List[str]:
        controls = ["lineage_recording", "evidence_recording"]

        if overall_level in {HEAT_HIGH, HEAT_CRITICAL}:
            controls.append("operator_review")

        if recommendation in {
            RECOMMENDATION_FREEZE_REVIEW,
            RECOMMENDATION_TENANT_ISOLATION_REVIEW,
        }:
            controls.append("governance_review")

        return list(dict.fromkeys(controls))

    def _record_assessment(
        self,
        assessment: RuntimeGovernanceHeatmapAssessment,
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
        assessment: RuntimeGovernanceHeatmapAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.operational_memory_engine is None:
            return

        payload = {
            "type": "RUNTIME_GOVERNANCE_HEATMAP_ASSESSMENT",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.operational_memory_engine, "append_memory"):
                self.operational_memory_engine.append_memory(payload)
            elif hasattr(self.operational_memory_engine, "record"):
                self.operational_memory_engine.record(payload)
        except Exception as exc:
            print(f"⚠️ Heatmap memory write failed: {exc}")

    def _write_to_lineage(
        self,
        assessment: RuntimeGovernanceHeatmapAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": "HEATMAP",
            "lineage_status": "RECORDED",
            "source_engine": self.heatmap_name,
            "summary": assessment.rationale,
            "severity": assessment.overall_heat_level,
            "confidence": 1.0,
            "constraints": [f"overall_heat_{assessment.overall_heat_level.lower()}"],
            "context": {
                "type": "RUNTIME_GOVERNANCE_HEATMAP_ASSESSMENT",
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.lineage_engine, "record_lineage"):
                self.lineage_engine.record_lineage(payload)
        except Exception as exc:
            print(f"⚠️ Heatmap lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        assessment: RuntimeGovernanceHeatmapAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.fedramp_evidence_lineage_engine is None:
            return

        payload = {
            "evidence_type": "RUNTIME_GOVERNANCE_HEATMAP",
            "evidence_status": "RECORDED",
            "source_engine": self.heatmap_name,
            "summary": assessment.rationale,
            "severity": assessment.overall_heat_level,
            "confidence": 1.0,
            "evidence_payload": {
                "type": "RUNTIME_GOVERNANCE_HEATMAP_ASSESSMENT",
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.fedramp_evidence_lineage_engine, "record_evidence"):
                self.fedramp_evidence_lineage_engine.record_evidence(payload)
        except Exception as exc:
            print(f"⚠️ Heatmap evidence write failed: {exc}")

    def _emit_event(
        self,
        assessment: RuntimeGovernanceHeatmapAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "RUNTIME_GOVERNANCE_HEATMAP_ASSESSMENT",
            "heatmap_name": self.heatmap_name,
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit("RUNTIME_GOVERNANCE_HEATMAP_ASSESSMENT", payload)
        except Exception as exc:
            print(f"⚠️ Heatmap event emit failed: {exc}")

    def _normalize_signal(self, item: RuntimeHeatmapSignal | Dict[str, Any]) -> RuntimeHeatmapSignal:
        if isinstance(item, RuntimeHeatmapSignal):
            return item

        return RuntimeHeatmapSignal(
            heatmap_signal_id=str(item.get("heatmap_signal_id") or uuid.uuid4()),
            signal_type=self._safe_signal_type(item.get("signal_type")),
            domain=self._safe_domain(item.get("domain")),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_confidence(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            tenant_id=item.get("tenant_id"),
            case_id=item.get("case_id"),
            correlation_id=item.get("correlation_id"),
            node_id=item.get("node_id"),
            node_name=item.get("node_name"),
            connector_name=item.get("connector_name"),
            governance_pressure=self._clamp_score(item.get("governance_pressure", 0.0)),
            autonomy_pressure=self._clamp_score(item.get("autonomy_pressure", 0.0)),
            execution_pressure=self._clamp_score(item.get("execution_pressure", 0.0)),
            verification_pressure=self._clamp_score(item.get("verification_pressure", 0.0)),
            connector_pressure=self._clamp_score(item.get("connector_pressure", 0.0)),
            telemetry_pressure=self._clamp_score(item.get("telemetry_pressure", 0.0)),
            resilience_pressure=self._clamp_score(item.get("resilience_pressure", 0.0)),
            survivability_pressure=self._clamp_score(item.get("survivability_pressure", 0.0)),
            collapse_risk=self._clamp_score(item.get("collapse_risk", 0.0)),
            approval_count=max(0, int(item.get("approval_count", 0) or 0)),
            escalation_count=max(0, int(item.get("escalation_count", 0) or 0)),
            rollback_count=max(0, int(item.get("rollback_count", 0) or 0)),
            failover_count=max(0, int(item.get("failover_count", 0) or 0)),
            contradiction_count=max(0, int(item.get("contradiction_count", 0) or 0)),
            degraded_node_count=max(0, int(item.get("degraded_node_count", 0) or 0)),
            unstable_node_count=max(0, int(item.get("unstable_node_count", 0) or 0)),
            failed_node_count=max(0, int(item.get("failed_node_count", 0) or 0)),
            payload=dict(item.get("payload", {}) or {}),
        )

    def _empty_assessment(self) -> RuntimeGovernanceHeatmapAssessment:
        return RuntimeGovernanceHeatmapAssessment(
            assessment_id=str(uuid.uuid4()),
            heatmap_name=self.heatmap_name,
            overall_heat_level=HEAT_LOW,
            overall_heat_score=0.0,
            governance_heat_score=0.0,
            autonomy_heat_score=0.0,
            execution_heat_score=0.0,
            survivability_heat_score=0.0,
            telemetry_heat_score=0.0,
            collapse_risk_score=0.0,
            cells=[],
            hotspots=[],
            recommendation=RECOMMENDATION_NONE,
            recommended_actions=[{"action": "continue_monitoring"}],
            required_controls=["lineage_recording", "evidence_recording"],
            rationale="No heatmap signals were submitted.",
            metadata={},
        )

    @staticmethod
    def _heat_level(score: float) -> str:
        if score >= 85:
            return HEAT_CRITICAL
        if score >= 65:
            return HEAT_HIGH
        if score >= 35:
            return HEAT_MEDIUM
        if score >= 0:
            return HEAT_LOW
        return HEAT_UNKNOWN

    @staticmethod
    def _safe_signal_type(value: Any) -> str:
        value = str(value or HeatmapSignalType.UNKNOWN.value).upper()
        valid = {item.value for item in HeatmapSignalType}
        return value if value in valid else HeatmapSignalType.UNKNOWN.value

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or HeatmapDomain.UNKNOWN.value).upper()
        valid = {item.value for item in HeatmapDomain}
        return value if value in valid else HeatmapDomain.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or "INFO").upper()
        valid = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
        return value if value in valid else "INFO"

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(1.0, score))

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(100.0, score))

    @staticmethod
    def _avg(values: Sequence[float]) -> float:
        if not values:
            return 0.0
        return max(0.0, min(100.0, sum(values) / len(values)))


def build_runtime_governance_heatmap(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> RuntimeGovernanceHeatmap:
    return RuntimeGovernanceHeatmap(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )