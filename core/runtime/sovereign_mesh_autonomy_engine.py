"""
core/runtime/sovereign_mesh_autonomy_engine.py

Sovereign Mesh Autonomy Engine

Self-adaptive sovereign operational mesh cognition layer.

Coordinates:
- autonomous runtime topology adaptation
- runtime survivability rebalancing
- continuity protection adaptation
- sovereignty-preserving routing
- tenant-isolated distributed posture
- resilience-zone adaptation
- adaptive distributed strategic projection

IMPORTANT:
This subsystem DOES NOT:
- mutate infrastructure directly
- execute failover actions
- bypass governance
- violate tenant isolation
- perform offensive cyber operations

It ONLY:
- evaluate mesh adaptation posture
- recommend topology adjustments
- coordinate sovereign adaptation cognition
- produce replayable mesh-autonomy lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = "sovereign_mesh_autonomy_engine"
DEFAULT_ADAPTATION_DEPTH = 12


MESH_STATE_STABLE = "STABLE"
MESH_STATE_ADAPTING = "ADAPTING"
MESH_STATE_REBALANCING = "REBALANCING"
MESH_STATE_CONTINUITY_PROTECTION = "CONTINUITY_PROTECTION"
MESH_STATE_SOVEREIGN_PROTECTION = "SOVEREIGN_PROTECTION"
MESH_STATE_DEGRADED = "DEGRADED"
MESH_STATE_CRITICAL = "CRITICAL"

ADAPTATION_NONE = "NONE"
ADAPTATION_MONITOR = "MONITOR"
ADAPTATION_REBALANCE = "REBALANCE"
ADAPTATION_REROUTE_CONTINUITY = "REROUTE_CONTINUITY"
ADAPTATION_REINFORCE_SOVEREIGNTY = "REINFORCE_SOVEREIGNTY"
ADAPTATION_RESILIENCE_SURGE = "RESILIENCE_SURGE"
ADAPTATION_ESCALATE_GOVERNANCE = "ESCALATE_GOVERNANCE"

PROJECTION_STABLE = "STABLE"
PROJECTION_ADAPTIVE_REBALANCE = "ADAPTIVE_REBALANCE"
PROJECTION_CONTINUITY_SHIELD = "CONTINUITY_SHIELD"
PROJECTION_SOVEREIGN_SHIELD = "SOVEREIGN_SHIELD"
PROJECTION_RESILIENCE_RECOVERY = "RESILIENCE_RECOVERY"
PROJECTION_SYSTEMIC_RISK = "SYSTEMIC_RISK"


class MeshSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class MeshNode:
    node_id: str
    runtime_id: str

    tenant_id: Optional[str]
    region: str
    zone: str

    node_role: str

    healthy: bool = True
    active: bool = True

    load_score: float = 0.0
    survivability_score: float = 100.0
    resilience_score: float = 100.0
    continuity_score: float = 100.0
    sovereignty_score: float = 100.0
    governance_score: float = 100.0
    telemetry_score: float = 100.0

    last_heartbeat_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MeshAdaptationSignal:
    signal_id: str

    source_engine: str
    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    region: Optional[str] = None
    zone: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    topology_pressure_score: float = 0.0
    runtime_imbalance_score: float = 0.0
    continuity_risk_score: float = 0.0
    resilience_risk_score: float = 0.0
    sovereignty_risk_score: float = 0.0
    governance_pressure_score: float = 0.0
    tenant_isolation_risk_score: float = 0.0
    regional_risk_score: float = 0.0
    failover_pressure_score: float = 0.0
    uncertainty_score: float = 0.0

    mesh_nodes: List[MeshNode] = field(default_factory=list)

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class MeshAdaptationDirective:
    directive_id: str

    directive_name: str
    adaptation_type: str
    priority: str

    tenant_id: Optional[str]
    region: Optional[str]
    zone: Optional[str]

    expected_survivability_gain: float
    expected_continuity_gain: float
    expected_sovereignty_gain: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MeshAdaptationProjection:
    projection_id: str

    projected_state: str

    topology_projection_score: float
    survivability_projection_score: float
    continuity_projection_score: float
    sovereignty_projection_score: float
    resilience_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MeshAdaptationSimulationStep:
    step_id: str
    step_index: int

    projected_state: str
    adaptation_type: str

    survivability_score: float
    continuity_score: float
    sovereignty_score: float
    resilience_score: float
    topology_pressure_score: float

    mesh_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SovereignMeshAutonomyAssessment:
    assessment_id: str

    mesh_state: str
    adaptation_type: str

    topology_pressure_score: float
    runtime_imbalance_score: float
    continuity_risk_score: float
    resilience_risk_score: float
    sovereignty_risk_score: float
    governance_pressure_score: float
    tenant_isolation_risk_score: float
    regional_risk_score: float
    failover_pressure_score: float
    uncertainty_score: float

    survivability_score: float
    resilience_score: float
    continuity_score: float
    sovereignty_score: float
    governance_score: float
    telemetry_score: float

    mesh_risk_score: float
    mesh_confidence: float
    explainability_score: float

    node_count: int
    active_node_count: int
    region_count: int
    tenant_count: int
    zone_count: int

    severity: str
    confidence: float

    tenant_id: Optional[str]
    region: Optional[str]
    zone: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    strategic_projection: MeshAdaptationProjection

    adaptation_directives: List[MeshAdaptationDirective]
    simulation_steps: List[MeshAdaptationSimulationStep]

    mesh_topology: Dict[str, Any]
    telemetry_fusion: Dict[str, Any]

    recommended_controls: List[str]
    recommended_actions: List[Dict[str, Any]]

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


class SovereignMeshAutonomyEngine:
    """
    Self-adaptive sovereign operational mesh cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        distributed_runtime_fabric: Optional[Any] = None,
        operational_governor: Optional[Any] = None,
        sovereignty_assurance_engine: Optional[Any] = None,
        command_center_copilot: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.distributed_runtime_fabric = distributed_runtime_fabric
        self.operational_governor = operational_governor
        self.sovereignty_assurance_engine = sovereignty_assurance_engine
        self.command_center_copilot = command_center_copilot
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._signals_seen = 0
        self._assessments: List[SovereignMeshAutonomyAssessment] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[MeshAdaptationSignal | Dict[str, Any]],
        *,
        adaptation_depth: int = DEFAULT_ADAPTATION_DEPTH,
        tenant_id: Optional[str] = None,
        region: Optional[str] = None,
        zone: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignMeshAutonomyAssessment:
        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                region=region,
                zone=zone,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:
            assessment = self._empty_assessment(
                tenant_id=tenant_id,
                region=region,
                zone=zone,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_assessment(assessment, context=context)
            return assessment

        selected = self._select_primary_signal(normalized)
        nodes = self._collect_nodes(normalized)

        topology_pressure = self._avg_score(
            [s.topology_pressure_score for s in normalized]
        )
        runtime_imbalance = self._avg_score(
            [s.runtime_imbalance_score for s in normalized]
        )
        continuity_risk = self._avg_score(
            [s.continuity_risk_score for s in normalized]
        )
        resilience_risk = self._avg_score(
            [s.resilience_risk_score for s in normalized]
        )
        sovereignty_risk = self._avg_score(
            [s.sovereignty_risk_score for s in normalized]
        )
        governance_pressure = self._avg_score(
            [s.governance_pressure_score for s in normalized]
        )
        tenant_isolation_risk = self._avg_score(
            [s.tenant_isolation_risk_score for s in normalized]
        )
        regional_risk = self._avg_score(
            [s.regional_risk_score for s in normalized]
        )
        failover_pressure = self._avg_score(
            [s.failover_pressure_score for s in normalized]
        )
        uncertainty = self._avg_score(
            [s.uncertainty_score for s in normalized]
        )

        survivability = self._avg_score(
            [n.survivability_score for n in nodes],
            default=100.0,
        )
        resilience = self._avg_score(
            [n.resilience_score for n in nodes],
            default=100.0,
        )
        continuity = self._avg_score(
            [n.continuity_score for n in nodes],
            default=100.0,
        )
        sovereignty = self._avg_score(
            [n.sovereignty_score for n in nodes],
            default=100.0,
        )
        governance = self._avg_score(
            [n.governance_score for n in nodes],
            default=100.0,
        )
        telemetry = self._avg_score(
            [n.telemetry_score for n in nodes],
            default=100.0,
        )

        mesh_risk = self._mesh_risk_score(
            topology_pressure_score=topology_pressure,
            runtime_imbalance_score=runtime_imbalance,
            continuity_risk_score=continuity_risk,
            resilience_risk_score=resilience_risk,
            sovereignty_risk_score=sovereignty_risk,
            governance_pressure_score=governance_pressure,
            tenant_isolation_risk_score=tenant_isolation_risk,
            regional_risk_score=regional_risk,
            failover_pressure_score=failover_pressure,
            uncertainty_score=uncertainty,
            survivability_score=survivability,
            continuity_score=continuity,
            sovereignty_score=sovereignty,
        )

        mesh_state = self._mesh_state(
            mesh_risk_score=mesh_risk,
            survivability_score=survivability,
            continuity_score=continuity,
            sovereignty_score=sovereignty,
            resilience_score=resilience,
        )

        adaptation_type = self._adaptation_type(
            mesh_state=mesh_state,
            runtime_imbalance_score=runtime_imbalance,
            continuity_risk_score=continuity_risk,
            sovereignty_risk_score=sovereignty_risk,
            resilience_risk_score=resilience_risk,
            governance_pressure_score=governance_pressure,
        )

        projection = self._projection(
            mesh_state=mesh_state,
            topology_pressure_score=topology_pressure,
            survivability_score=survivability,
            continuity_score=continuity,
            sovereignty_score=sovereignty,
            resilience_score=resilience,
            mesh_risk_score=mesh_risk,
        )

        directives = self._build_directives(
            adaptation_type=adaptation_type,
            mesh_state=mesh_state,
            tenant_id=tenant_id or selected.tenant_id,
            region=region or selected.region,
            zone=zone or selected.zone,
            survivability_score=survivability,
            continuity_score=continuity,
            sovereignty_score=sovereignty,
            resilience_score=resilience,
        )

        steps = self._build_steps(
            mesh_state=mesh_state,
            adaptation_type=adaptation_type,
            survivability_score=survivability,
            continuity_score=continuity,
            sovereignty_score=sovereignty,
            resilience_score=resilience,
            topology_pressure_score=topology_pressure,
            mesh_risk_score=mesh_risk,
            adaptation_depth=adaptation_depth,
        )

        assessment = SovereignMeshAutonomyAssessment(
            assessment_id=str(uuid.uuid4()),
            mesh_state=mesh_state,
            adaptation_type=adaptation_type,
            topology_pressure_score=topology_pressure,
            runtime_imbalance_score=runtime_imbalance,
            continuity_risk_score=continuity_risk,
            resilience_risk_score=resilience_risk,
            sovereignty_risk_score=sovereignty_risk,
            governance_pressure_score=governance_pressure,
            tenant_isolation_risk_score=tenant_isolation_risk,
            regional_risk_score=regional_risk,
            failover_pressure_score=failover_pressure,
            uncertainty_score=uncertainty,
            survivability_score=survivability,
            resilience_score=resilience,
            continuity_score=continuity,
            sovereignty_score=sovereignty,
            governance_score=governance,
            telemetry_score=telemetry,
            mesh_risk_score=mesh_risk,
            mesh_confidence=self._confidence(normalized),
            explainability_score=self._explainability_score(normalized, nodes),
            node_count=len(nodes),
            active_node_count=len([n for n in nodes if n.active]),
            region_count=len({n.region for n in nodes}),
            tenant_count=len({n.tenant_id for n in nodes if n.tenant_id}),
            zone_count=len({n.zone for n in nodes}),
            severity=selected.severity,
            confidence=selected.confidence,
            tenant_id=tenant_id or selected.tenant_id,
            region=region or selected.region,
            zone=zone or selected.zone,
            mission_id=mission_id or selected.mission_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            strategic_projection=projection,
            adaptation_directives=directives,
            simulation_steps=steps,
            mesh_topology=self._mesh_topology(nodes),
            telemetry_fusion=self._telemetry_fusion(normalized, nodes),
            recommended_controls=self._recommended_controls(
                mesh_state=mesh_state,
                adaptation_type=adaptation_type,
            ),
            recommended_actions=self._recommended_actions(
                mesh_state=mesh_state,
                adaptation_type=adaptation_type,
            ),
            rationale=self._build_rationale(
                mesh_state=mesh_state,
                adaptation_type=adaptation_type,
                mesh_risk_score=mesh_risk,
                node_count=len(nodes),
            ),
            metadata={
                "source_engines": sorted({s.source_engine for s in normalized}),
                "regions": sorted({n.region for n in nodes}),
                "zones": sorted({n.zone for n in nodes}),
            },
        )

        self._record_assessment(assessment, context=context)
        return assessment

    def submit(
        self,
        signals: Sequence[MeshAdaptationSignal | Dict[str, Any]],
        **kwargs: Any,
    ) -> SovereignMeshAutonomyAssessment:
        return self.evaluate(signals, **kwargs)

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignMeshAutonomyAssessment]:
        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    # ==========================================================
    # SCORING / STATES
    # ==========================================================

    def _mesh_risk_score(
        self,
        *,
        topology_pressure_score: float,
        runtime_imbalance_score: float,
        continuity_risk_score: float,
        resilience_risk_score: float,
        sovereignty_risk_score: float,
        governance_pressure_score: float,
        tenant_isolation_risk_score: float,
        regional_risk_score: float,
        failover_pressure_score: float,
        uncertainty_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
    ) -> float:
        risk = (
            topology_pressure_score
            + runtime_imbalance_score
            + continuity_risk_score
            + resilience_risk_score
            + sovereignty_risk_score
            + governance_pressure_score
            + tenant_isolation_risk_score
            + regional_risk_score
            + failover_pressure_score
            + uncertainty_score
            + (100.0 - survivability_score)
            + (100.0 - continuity_score)
            + (100.0 - sovereignty_score)
        ) / 13.0

        return self._clamp_score(risk)

    @staticmethod
    def _mesh_state(
        *,
        mesh_risk_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
    ) -> str:
        if mesh_risk_score >= 85 or survivability_score <= 30:
            return MESH_STATE_CRITICAL

        if sovereignty_score <= 45:
            return MESH_STATE_SOVEREIGN_PROTECTION

        if continuity_score <= 45:
            return MESH_STATE_CONTINUITY_PROTECTION

        if resilience_score <= 50:
            return MESH_STATE_DEGRADED

        if mesh_risk_score >= 65:
            return MESH_STATE_REBALANCING

        if mesh_risk_score >= 40:
            return MESH_STATE_ADAPTING

        return MESH_STATE_STABLE

    @staticmethod
    def _adaptation_type(
        *,
        mesh_state: str,
        runtime_imbalance_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        resilience_risk_score: float,
        governance_pressure_score: float,
    ) -> str:
        if mesh_state == MESH_STATE_CRITICAL:
            return ADAPTATION_ESCALATE_GOVERNANCE

        if sovereignty_risk_score >= 60:
            return ADAPTATION_REINFORCE_SOVEREIGNTY

        if continuity_risk_score >= 60:
            return ADAPTATION_REROUTE_CONTINUITY

        if resilience_risk_score >= 60:
            return ADAPTATION_RESILIENCE_SURGE

        if runtime_imbalance_score >= 55:
            return ADAPTATION_REBALANCE

        if governance_pressure_score >= 65:
            return ADAPTATION_ESCALATE_GOVERNANCE

        if mesh_state in {MESH_STATE_ADAPTING, MESH_STATE_REBALANCING}:
            return ADAPTATION_MONITOR

        return ADAPTATION_NONE

    # ==========================================================
    # PROJECTION / DIRECTIVES / SIMULATION
    # ==========================================================

    def _projection(
        self,
        *,
        mesh_state: str,
        topology_pressure_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
        mesh_risk_score: float,
    ) -> MeshAdaptationProjection:
        projected_state = PROJECTION_STABLE

        if mesh_state == MESH_STATE_CRITICAL:
            projected_state = PROJECTION_SYSTEMIC_RISK
        elif sovereignty_score <= 50:
            projected_state = PROJECTION_SOVEREIGN_SHIELD
        elif continuity_score <= 50:
            projected_state = PROJECTION_CONTINUITY_SHIELD
        elif resilience_score <= 55:
            projected_state = PROJECTION_RESILIENCE_RECOVERY
        elif mesh_risk_score >= 45 or topology_pressure_score >= 45:
            projected_state = PROJECTION_ADAPTIVE_REBALANCE

        return MeshAdaptationProjection(
            projection_id=str(uuid.uuid4()),
            projected_state=projected_state,
            topology_projection_score=topology_pressure_score,
            survivability_projection_score=survivability_score,
            continuity_projection_score=continuity_score,
            sovereignty_projection_score=sovereignty_score,
            resilience_projection_score=resilience_score,
            rationale=f"Projected sovereign mesh adaptation state {projected_state}.",
        )

    def _build_directives(
        self,
        *,
        adaptation_type: str,
        mesh_state: str,
        tenant_id: Optional[str],
        region: Optional[str],
        zone: Optional[str],
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
    ) -> List[MeshAdaptationDirective]:
        if adaptation_type == ADAPTATION_NONE:
            return [
                MeshAdaptationDirective(
                    directive_id=str(uuid.uuid4()),
                    directive_name="continue_mesh_monitoring",
                    adaptation_type=ADAPTATION_MONITOR,
                    priority="LOW",
                    tenant_id=tenant_id,
                    region=region,
                    zone=zone,
                    expected_survivability_gain=0.0,
                    expected_continuity_gain=0.0,
                    expected_sovereignty_gain=0.0,
                    rationale="Mesh posture is stable; continue monitoring.",
                )
            ]

        priority = "HIGH"
        if mesh_state == MESH_STATE_CRITICAL:
            priority = "CRITICAL"
        elif mesh_state in {
            MESH_STATE_SOVEREIGN_PROTECTION,
            MESH_STATE_CONTINUITY_PROTECTION,
        }:
            priority = "HIGH"
        elif mesh_state == MESH_STATE_ADAPTING:
            priority = "MEDIUM"

        return [
            MeshAdaptationDirective(
                directive_id=str(uuid.uuid4()),
                directive_name=f"{adaptation_type.lower()}_directive",
                adaptation_type=adaptation_type,
                priority=priority,
                tenant_id=tenant_id,
                region=region,
                zone=zone,
                expected_survivability_gain=max(0.0, 100.0 - survivability_score) * 0.25,
                expected_continuity_gain=max(0.0, 100.0 - continuity_score) * 0.25,
                expected_sovereignty_gain=max(0.0, 100.0 - sovereignty_score) * 0.25,
                rationale=(
                    f"Recommended {adaptation_type} because mesh state is "
                    f"{mesh_state}."
                ),
                metadata={
                    "resilience_gap": max(0.0, 100.0 - resilience_score),
                },
            )
        ]

    def _build_steps(
        self,
        *,
        mesh_state: str,
        adaptation_type: str,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
        topology_pressure_score: float,
        mesh_risk_score: float,
        adaptation_depth: int,
    ) -> List[MeshAdaptationSimulationStep]:
        steps: List[MeshAdaptationSimulationStep] = []

        for idx in range(max(1, int(adaptation_depth))):
            steps.append(
                MeshAdaptationSimulationStep(
                    step_id=str(uuid.uuid4()),
                    step_index=idx,
                    projected_state=mesh_state,
                    adaptation_type=adaptation_type,
                    survivability_score=survivability_score,
                    continuity_score=continuity_score,
                    sovereignty_score=sovereignty_score,
                    resilience_score=resilience_score,
                    topology_pressure_score=topology_pressure_score,
                    mesh_risk_score=mesh_risk_score,
                    rationale=(
                        f"Sovereign mesh autonomy projection step {idx} "
                        f"maintains {mesh_state} with adaptation {adaptation_type}."
                    ),
                )
            )

            if adaptation_type != ADAPTATION_NONE:
                survivability_score = self._clamp_score(survivability_score + 1.5)
                continuity_score = self._clamp_score(continuity_score + 1.5)
                sovereignty_score = self._clamp_score(sovereignty_score + 1.2)
                resilience_score = self._clamp_score(resilience_score + 1.4)
                topology_pressure_score = self._clamp_score(topology_pressure_score - 1.0)
                mesh_risk_score = self._clamp_score(mesh_risk_score - 1.2)

        return steps

    # ==========================================================
    # TOPOLOGY / FUSION
    # ==========================================================

    def _collect_nodes(
        self,
        signals: Sequence[MeshAdaptationSignal],
    ) -> List[MeshNode]:
        nodes: List[MeshNode] = []

        for signal in signals:
            nodes.extend(signal.mesh_nodes or [])

        return nodes

    def _mesh_topology(
        self,
        nodes: Sequence[MeshNode],
    ) -> Dict[str, Any]:
        return {
            "node_count": len(nodes),
            "active_node_count": len([n for n in nodes if n.active]),
            "healthy_node_count": len([n for n in nodes if n.healthy]),
            "regions": sorted({n.region for n in nodes}),
            "zones": sorted({n.zone for n in nodes}),
            "tenants": sorted({n.tenant_id for n in nodes if n.tenant_id}),
            "roles": sorted({n.node_role for n in nodes}),
            "nodes": [
                {
                    "node_id": n.node_id,
                    "runtime_id": n.runtime_id,
                    "tenant_id": n.tenant_id,
                    "region": n.region,
                    "zone": n.zone,
                    "node_role": n.node_role,
                    "healthy": n.healthy,
                    "active": n.active,
                    "load_score": n.load_score,
                    "survivability_score": n.survivability_score,
                    "resilience_score": n.resilience_score,
                    "continuity_score": n.continuity_score,
                    "sovereignty_score": n.sovereignty_score,
                    "governance_score": n.governance_score,
                    "telemetry_score": n.telemetry_score,
                    "last_heartbeat_ms": n.last_heartbeat_ms,
                }
                for n in nodes
            ],
        }

    def _telemetry_fusion(
        self,
        signals: Sequence[MeshAdaptationSignal],
        nodes: Sequence[MeshNode],
    ) -> Dict[str, Any]:
        return {
            "signal_count": len(signals),
            "node_count": len(nodes),
            "source_engines": sorted({s.source_engine for s in signals}),
            "signal_regions": sorted({s.region for s in signals if s.region}),
            "signal_zones": sorted({s.zone for s in signals if s.zone}),
            "signal_tenants": sorted({s.tenant_id for s in signals if s.tenant_id}),
        }

    # ==========================================================
    # RECOMMENDED CONTROLS / ACTIONS
    # ==========================================================

    @staticmethod
    def _recommended_controls(
        *,
        mesh_state: str,
        adaptation_type: str,
    ) -> List[str]:
        controls = [
            "mesh_autonomy_lineage_recording",
            "mesh_autonomy_evidence_recording",
            "tenant_boundary_preservation",
            "sovereignty_boundary_validation",
        ]

        if mesh_state != MESH_STATE_STABLE:
            controls.append("mesh_adaptation_review")

        if adaptation_type == ADAPTATION_REINFORCE_SOVEREIGNTY:
            controls.append("sovereignty_reinforcement_review")

        if adaptation_type == ADAPTATION_REROUTE_CONTINUITY:
            controls.append("continuity_reroute_review")

        if adaptation_type == ADAPTATION_ESCALATE_GOVERNANCE:
            controls.append("governance_escalation_review")

        return list(dict.fromkeys(controls))

    @staticmethod
    def _recommended_actions(
        *,
        mesh_state: str,
        adaptation_type: str,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "action": "record_mesh_autonomy_lineage",
                "mesh_state": mesh_state,
            },
            {
                "action": "record_mesh_autonomy_evidence",
                "adaptation_type": adaptation_type,
            },
            {
                "action": "review_mesh_adaptation_posture",
                "mesh_state": mesh_state,
                "adaptation_type": adaptation_type,
            },
        ]

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: SovereignMeshAutonomyAssessment,
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
        assessment: SovereignMeshAutonomyAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.operational_memory_engine is None:
            return

        payload = {
            "type": "SOVEREIGN_MESH_AUTONOMY_ASSESSMENT",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.operational_memory_engine, "append_memory"):
                self.operational_memory_engine.append_memory(payload)
        except Exception as exc:
            print(f"⚠️ Mesh autonomy memory write failed: {exc}")

    def _write_to_lineage(
        self,
        assessment: SovereignMeshAutonomyAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": "SOVEREIGN_MESH_AUTONOMY",
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
            print(f"⚠️ Mesh autonomy lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        assessment: SovereignMeshAutonomyAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.fedramp_evidence_lineage_engine is None:
            return

        payload = {
            "evidence_type": "SOVEREIGN_MESH_AUTONOMY",
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
            print(f"⚠️ Mesh autonomy evidence write failed: {exc}")

    def _emit_event(
        self,
        assessment: SovereignMeshAutonomyAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "SOVEREIGN_MESH_AUTONOMY_ASSESSMENT",
            "engine_name": self.engine_name,
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_MESH_AUTONOMY_ASSESSMENT",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Mesh autonomy event emit failed: {exc}")

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: MeshAdaptationSignal | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        region: Optional[str],
        zone: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> MeshAdaptationSignal:
        if isinstance(item, MeshAdaptationSignal):
            return item

        nodes = []

        for node in item.get("mesh_nodes", []) or []:
            nodes.append(
                MeshNode(
                    node_id=str(node.get("node_id") or uuid.uuid4()),
                    runtime_id=str(node.get("runtime_id") or "unknown_runtime"),
                    tenant_id=tenant_id or node.get("tenant_id"),
                    region=str(region or node.get("region") or "global"),
                    zone=str(zone or node.get("zone") or "default"),
                    node_role=str(node.get("node_role") or "runtime"),
                    healthy=bool(node.get("healthy", True)),
                    active=bool(node.get("active", True)),
                    load_score=self._clamp_score(node.get("load_score", 0.0)),
                    survivability_score=self._clamp_score(
                        node.get("survivability_score", 100.0)
                    ),
                    resilience_score=self._clamp_score(
                        node.get("resilience_score", 100.0)
                    ),
                    continuity_score=self._clamp_score(
                        node.get("continuity_score", 100.0)
                    ),
                    sovereignty_score=self._clamp_score(
                        node.get("sovereignty_score", 100.0)
                    ),
                    governance_score=self._clamp_score(
                        node.get("governance_score", 100.0)
                    ),
                    telemetry_score=self._clamp_score(
                        node.get("telemetry_score", 100.0)
                    ),
                    last_heartbeat_ms=int(
                        node.get("last_heartbeat_ms") or int(time.time() * 1000)
                    ),
                    metadata=dict(node.get("metadata", {}) or {}),
                )
            )

        return MeshAdaptationSignal(
            signal_id=str(item.get("signal_id") or uuid.uuid4()),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_probability(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            tenant_id=tenant_id or item.get("tenant_id"),
            region=region or item.get("region"),
            zone=zone or item.get("zone"),
            mission_id=mission_id or item.get("mission_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            topology_pressure_score=self._clamp_score(
                item.get("topology_pressure_score", 0.0)
            ),
            runtime_imbalance_score=self._clamp_score(
                item.get("runtime_imbalance_score", 0.0)
            ),
            continuity_risk_score=self._clamp_score(
                item.get("continuity_risk_score", 0.0)
            ),
            resilience_risk_score=self._clamp_score(
                item.get("resilience_risk_score", 0.0)
            ),
            sovereignty_risk_score=self._clamp_score(
                item.get("sovereignty_risk_score", 0.0)
            ),
            governance_pressure_score=self._clamp_score(
                item.get("governance_pressure_score", 0.0)
            ),
            tenant_isolation_risk_score=self._clamp_score(
                item.get("tenant_isolation_risk_score", 0.0)
            ),
            regional_risk_score=self._clamp_score(
                item.get("regional_risk_score", 0.0)
            ),
            failover_pressure_score=self._clamp_score(
                item.get("failover_pressure_score", 0.0)
            ),
            uncertainty_score=self._clamp_score(item.get("uncertainty_score", 0.0)),
            mesh_nodes=nodes,
            payload=dict(item.get("payload", {}) or {}),
        )

    def _empty_assessment(
        self,
        *,
        tenant_id: Optional[str],
        region: Optional[str],
        zone: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignMeshAutonomyAssessment:
        projection = MeshAdaptationProjection(
            projection_id=str(uuid.uuid4()),
            projected_state=PROJECTION_STABLE,
            topology_projection_score=0.0,
            survivability_projection_score=100.0,
            continuity_projection_score=100.0,
            sovereignty_projection_score=100.0,
            resilience_projection_score=100.0,
            rationale="No mesh autonomy signals submitted.",
        )

        return SovereignMeshAutonomyAssessment(
            assessment_id=str(uuid.uuid4()),
            mesh_state=MESH_STATE_STABLE,
            adaptation_type=ADAPTATION_NONE,
            topology_pressure_score=0.0,
            runtime_imbalance_score=0.0,
            continuity_risk_score=0.0,
            resilience_risk_score=0.0,
            sovereignty_risk_score=0.0,
            governance_pressure_score=0.0,
            tenant_isolation_risk_score=0.0,
            regional_risk_score=0.0,
            failover_pressure_score=0.0,
            uncertainty_score=0.0,
            survivability_score=100.0,
            resilience_score=100.0,
            continuity_score=100.0,
            sovereignty_score=100.0,
            governance_score=100.0,
            telemetry_score=100.0,
            mesh_risk_score=0.0,
            mesh_confidence=1.0,
            explainability_score=100.0,
            node_count=0,
            active_node_count=0,
            region_count=0,
            tenant_count=0,
            zone_count=0,
            severity=MeshSeverity.INFO.value,
            confidence=1.0,
            tenant_id=tenant_id,
            region=region,
            zone=zone,
            mission_id=mission_id,
            case_id=case_id,
            correlation_id=correlation_id,
            strategic_projection=projection,
            adaptation_directives=[],
            simulation_steps=[],
            mesh_topology={
                "node_count": 0,
                "active_node_count": 0,
                "healthy_node_count": 0,
                "regions": [],
                "zones": [],
                "tenants": [],
                "roles": [],
                "nodes": [],
            },
            telemetry_fusion={
                "signal_count": 0,
                "node_count": 0,
                "source_engines": [],
            },
            recommended_controls=[
                "mesh_autonomy_lineage_recording",
                "mesh_autonomy_evidence_recording",
            ],
            recommended_actions=[
                {
                    "action": "continue_mesh_autonomy_monitoring",
                }
            ],
            rationale="No mesh autonomy signals submitted.",
            metadata={},
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _select_primary_signal(
        self,
        signals: Sequence[MeshAdaptationSignal],
    ) -> MeshAdaptationSignal:
        return sorted(
            signals,
            key=lambda item: (
                item.sovereignty_risk_score,
                item.continuity_risk_score,
                item.runtime_imbalance_score,
                item.topology_pressure_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _confidence(
        self,
        signals: Sequence[MeshAdaptationSignal],
    ) -> float:
        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean([s.confidence for s in signals])
        )

    def _explainability_score(
        self,
        signals: Sequence[MeshAdaptationSignal],
        nodes: Sequence[MeshNode],
    ) -> float:
        if not signals:
            return 0.0

        explained = 0

        for signal in signals:
            if signal.summary:
                explained += 1
            if signal.source_engine:
                explained += 1
            if signal.mesh_nodes:
                explained += 1

        base = (explained / (len(signals) * 3)) * 100
        node_bonus = min(10.0, len(nodes) * 0.5)

        return self._clamp_score(base + node_bonus)

    @staticmethod
    def _build_rationale(
        *,
        mesh_state: str,
        adaptation_type: str,
        mesh_risk_score: float,
        node_count: int,
    ) -> str:
        return (
            f"Sovereign mesh autonomy evaluation completed. "
            f"Mesh state {mesh_state}; adaptation type {adaptation_type}; "
            f"mesh risk score {mesh_risk_score:.2f}; node count {node_count}."
        )

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or MeshSeverity.INFO.value).upper()
        valid = {item.value for item in MeshSeverity}
        return value if value in valid else MeshSeverity.INFO.value

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

    def _avg_score(
        self,
        values: Sequence[float],
        *,
        default: float = 0.0,
    ) -> float:
        if not values:
            return default

        return self._clamp_score(statistics.mean(values))


def build_sovereign_mesh_autonomy_engine(
    *,
    event_bus: Optional[Any] = None,
    distributed_runtime_fabric: Optional[Any] = None,
    operational_governor: Optional[Any] = None,
    sovereignty_assurance_engine: Optional[Any] = None,
    command_center_copilot: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> SovereignMeshAutonomyEngine:
    return SovereignMeshAutonomyEngine(
        event_bus=event_bus,
        distributed_runtime_fabric=distributed_runtime_fabric,
        operational_governor=operational_governor,
        sovereignty_assurance_engine=sovereignty_assurance_engine,
        command_center_copilot=command_center_copilot,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )