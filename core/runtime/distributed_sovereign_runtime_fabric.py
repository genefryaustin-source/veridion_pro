"""
core/runtime/distributed_sovereign_runtime_fabric.py

Distributed Sovereign Runtime Fabric

Distributed coordination layer for sovereign operational runtimes.

Coordinates:
- sovereign runtimes
- tenant runtimes
- regional runtimes
- resilience runtimes
- continuity runtimes
- command-center runtimes

IMPORTANT:
This subsystem DOES NOT:
- execute destructive operations
- bypass governance
- violate tenant isolation
- override sovereignty protections
- mutate infrastructure directly

It ONLY:
- coordinate distributed runtime cognition
- coordinate runtime survivability
- coordinate continuity failover
- coordinate sovereignty-aware runtime orchestration
- aggregate distributed telemetry visibility
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from enum import Enum

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
)


DEFAULT_ENGINE_NAME = (
    "distributed_sovereign_runtime_fabric"
)

DEFAULT_REGION = "global"

DEFAULT_SURVIVABILITY_THRESHOLD = (
    65.0
)


FABRIC_STATE_STABLE = "STABLE"

FABRIC_STATE_ELEVATED = (
    "ELEVATED"
)

FABRIC_STATE_FAILOVER_READY = (
    "FAILOVER_READY"
)

FABRIC_STATE_RESILIENCE_COORDINATION = (
    "RESILIENCE_COORDINATION"
)

FABRIC_STATE_SOVEREIGN_COORDINATION = (
    "SOVEREIGN_COORDINATION"
)

FABRIC_STATE_CONTINUITY_PROTECTION = (
    "CONTINUITY_PROTECTION"
)

FABRIC_STATE_DEGRADED = (
    "DEGRADED"
)

FABRIC_STATE_CRITICAL = (
    "CRITICAL"
)

FAILOVER_NONE = "NONE"

FAILOVER_PREPARE = (
    "PREPARE"
)

FAILOVER_COORDINATED = (
    "COORDINATED"
)

FAILOVER_ACTIVE = (
    "ACTIVE"
)

FAILOVER_SOVEREIGN_PROTECTION = (
    "SOVEREIGN_PROTECTION"
)

PROJECTION_STABLE = "STABLE"

PROJECTION_RUNTIME_SURVIVAL = (
    "RUNTIME_SURVIVAL"
)

PROJECTION_REGION_FAILOVER = (
    "REGION_FAILOVER"
)

PROJECTION_CONTINUITY_SHIELD = (
    "CONTINUITY_SHIELD"
)

PROJECTION_SOVEREIGN_RECOVERY = (
    "SOVEREIGN_RECOVERY"
)


class FabricSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RuntimeNode:
    runtime_id: str

    tenant_id: Optional[str]
    region: str

    runtime_role: str

    healthy: bool = True
    active: bool = True

    survivability_score: float = (
        100.0
    )

    governance_score: float = (
        100.0
    )

    sovereignty_score: float = (
        100.0
    )

    continuity_score: float = (
        100.0
    )

    telemetry_score: float = (
        100.0
    )

    last_heartbeat_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class DistributedTelemetry:
    telemetry_id: str

    runtime_id: str
    region: str

    operational_risk_score: float = (
        0.0
    )

    governance_risk_score: float = (
        0.0
    )

    sovereignty_risk_score: float = (
        0.0
    )

    resilience_risk_score: float = (
        0.0
    )

    continuity_risk_score: float = (
        0.0
    )

    uncertainty_score: float = (
        0.0
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class DistributedProjection:
    projection_id: str

    projected_state: str

    survivability_projection_score: float
    sovereignty_projection_score: float
    continuity_projection_score: float
    resilience_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class DistributedRuntimeFabricAssessment:
    assessment_id: str

    fabric_state: str
    failover_state: str

    runtime_count: int
    active_runtime_count: int

    region_count: int
    tenant_count: int

    survivability_score: float
    governance_score: float
    sovereignty_score: float
    continuity_score: float
    telemetry_score: float

    operational_risk_score: float
    governance_risk_score: float
    sovereignty_risk_score: float
    resilience_risk_score: float
    continuity_risk_score: float

    distributed_confidence: float
    uncertainty_score: float

    strategic_projection: DistributedProjection

    runtime_topology: Dict[str, Any]

    telemetry_fusion: Dict[str, Any]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


class DistributedSovereignRuntimeFabric:
    """
    Distributed sovereign operational runtime mesh.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
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

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._runtime_nodes: Dict[
            str,
            RuntimeNode
        ] = {}

        self._telemetry: List[
            DistributedTelemetry
        ] = []

        self._assessments: List[
            DistributedRuntimeFabricAssessment
        ] = []

    # ==========================================================
    # REGISTRATION
    # ==========================================================

    def register_runtime(
        self,
        node: RuntimeNode,
    ) -> None:

        self._runtime_nodes[
            node.runtime_id
        ] = node

    def register_telemetry(
        self,
        telemetry: DistributedTelemetry,
    ) -> None:

        self._telemetry.append(
            telemetry
        )

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
    ) -> (
        DistributedRuntimeFabricAssessment
    ):

        nodes = list(
            self._runtime_nodes.values()
        )

        telemetry = list(
            self._telemetry[-500:]
        )

        runtime_count = len(nodes)

        active_runtime_count = len(
            [
                n
                for n in nodes
                if n.active
            ]
        )

        region_count = len(
            {
                n.region
                for n in nodes
            }
        )

        tenant_count = len(
            {
                n.tenant_id
                for n in nodes
                if n.tenant_id
            }
        )

        survivability_score = (
            self._avg_score(
                [
                    n
                    .survivability_score
                    for n in nodes
                ],
                default=100.0,
            )
        )

        governance_score = (
            self._avg_score(
                [
                    n.governance_score
                    for n in nodes
                ],
                default=100.0,
            )
        )

        sovereignty_score = (
            self._avg_score(
                [
                    n.sovereignty_score
                    for n in nodes
                ],
                default=100.0,
            )
        )

        continuity_score = (
            self._avg_score(
                [
                    n.continuity_score
                    for n in nodes
                ],
                default=100.0,
            )
        )

        telemetry_score = (
            self._avg_score(
                [
                    n.telemetry_score
                    for n in nodes
                ],
                default=100.0,
            )
        )

        operational_risk = (
            self._avg_score(
                [
                    t
                    .operational_risk_score
                    for t in telemetry
                ]
            )
        )

        governance_risk = (
            self._avg_score(
                [
                    t
                    .governance_risk_score
                    for t in telemetry
                ]
            )
        )

        sovereignty_risk = (
            self._avg_score(
                [
                    t
                    .sovereignty_risk_score
                    for t in telemetry
                ]
            )
        )

        resilience_risk = (
            self._avg_score(
                [
                    t
                    .resilience_risk_score
                    for t in telemetry
                ]
            )
        )

        continuity_risk = (
            self._avg_score(
                [
                    t
                    .continuity_risk_score
                    for t in telemetry
                ]
            )
        )

        uncertainty = (
            self._avg_score(
                [
                    t
                    .uncertainty_score
                    for t in telemetry
                ]
            )
        )

        fabric_state = (
            self._fabric_state(
                survivability_score=(
                    survivability_score
                ),
                sovereignty_score=(
                    sovereignty_score
                ),
                continuity_score=(
                    continuity_score
                ),
                operational_risk_score=(
                    operational_risk
                ),
            )
        )

        failover_state = (
            self._failover_state(
                survivability_score=(
                    survivability_score
                ),
                continuity_score=(
                    continuity_score
                ),
                sovereignty_score=(
                    sovereignty_score
                ),
            )
        )

        projection = (
            self._projection(
                survivability_score=(
                    survivability_score
                ),
                sovereignty_score=(
                    sovereignty_score
                ),
                continuity_score=(
                    continuity_score
                ),
                resilience_risk_score=(
                    resilience_risk
                ),
            )
        )

        assessment = (
            DistributedRuntimeFabricAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                fabric_state=(
                    fabric_state
                ),
                failover_state=(
                    failover_state
                ),
                runtime_count=(
                    runtime_count
                ),
                active_runtime_count=(
                    active_runtime_count
                ),
                region_count=(
                    region_count
                ),
                tenant_count=(
                    tenant_count
                ),
                survivability_score=(
                    survivability_score
                ),
                governance_score=(
                    governance_score
                ),
                sovereignty_score=(
                    sovereignty_score
                ),
                continuity_score=(
                    continuity_score
                ),
                telemetry_score=(
                    telemetry_score
                ),
                operational_risk_score=(
                    operational_risk
                ),
                governance_risk_score=(
                    governance_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                resilience_risk_score=(
                    resilience_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                distributed_confidence=(
                    self
                    ._distributed_confidence(
                        nodes
                    )
                ),
                uncertainty_score=(
                    uncertainty
                ),
                strategic_projection=(
                    projection
                ),
                runtime_topology=(
                    self._runtime_topology(
                        nodes
                    )
                ),
                telemetry_fusion=(
                    self._telemetry_fusion(
                        telemetry
                    )
                ),
                rationale=(
                    self._rationale(
                        fabric_state=(
                            fabric_state
                        ),
                        failover_state=(
                            failover_state
                        ),
                        runtime_count=(
                            runtime_count
                        ),
                    )
                ),
                metadata={
                    "regions": sorted(
                        {
                            n.region
                            for n in nodes
                        }
                    )
                },
            )
        )

        self._record_assessment(
            assessment
        )

        return assessment

    # ==========================================================
    # STATES
    # ==========================================================

    @staticmethod
    def _fabric_state(
        *,
        survivability_score: float,
        sovereignty_score: float,
        continuity_score: float,
        operational_risk_score: float,
    ) -> str:

        if sovereignty_score <= 45:
            return (
                FABRIC_STATE_SOVEREIGN_COORDINATION
            )

        if continuity_score <= 45:
            return (
                FABRIC_STATE_CONTINUITY_PROTECTION
            )

        if survivability_score <= 35:
            return (
                FABRIC_STATE_CRITICAL
            )

        if survivability_score <= 55:
            return (
                FABRIC_STATE_FAILOVER_READY
            )

        if operational_risk_score >= 60:
            return (
                FABRIC_STATE_ELEVATED
            )

        return FABRIC_STATE_STABLE

    @staticmethod
    def _failover_state(
        *,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
    ) -> str:

        if sovereignty_score <= 40:
            return (
                FAILOVER_SOVEREIGN_PROTECTION
            )

        if survivability_score <= 35:
            return (
                FAILOVER_ACTIVE
            )

        if continuity_score <= 55:
            return (
                FAILOVER_COORDINATED
            )

        if survivability_score <= 70:
            return (
                FAILOVER_PREPARE
            )

        return FAILOVER_NONE

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        survivability_score: float,
        sovereignty_score: float,
        continuity_score: float,
        resilience_risk_score: float,
    ) -> DistributedProjection:

        state = PROJECTION_STABLE

        if sovereignty_score <= 45:
            state = (
                PROJECTION_SOVEREIGN_RECOVERY
            )

        elif continuity_score <= 50:
            state = (
                PROJECTION_CONTINUITY_SHIELD
            )

        elif survivability_score <= 50:
            state = (
                PROJECTION_REGION_FAILOVER
            )

        elif resilience_risk_score >= 55:
            state = (
                PROJECTION_RUNTIME_SURVIVAL
            )

        return DistributedProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=state,
            survivability_projection_score=(
                survivability_score
            ),
            sovereignty_projection_score=(
                sovereignty_score
            ),
            continuity_projection_score=(
                continuity_score
            ),
            resilience_projection_score=(
                resilience_risk_score
            ),
            rationale=(
                f"Distributed runtime "
                f"projection state "
                f"{state}."
            ),
        )

    # ==========================================================
    # TOPOLOGY
    # ==========================================================

    def _runtime_topology(
        self,
        nodes: Sequence[
            RuntimeNode
        ],
    ) -> Dict[str, Any]:

        return {
            "runtime_count": len(
                nodes
            ),
            "regions": sorted(
                {
                    n.region
                    for n in nodes
                }
            ),
            "tenants": sorted(
                {
                    n.tenant_id
                    for n in nodes
                    if n.tenant_id
                }
            ),
        }

    def _telemetry_fusion(
        self,
        telemetry: Sequence[
            DistributedTelemetry
        ],
    ) -> Dict[str, Any]:

        return {
            "telemetry_count": len(
                telemetry
            ),
            "regions": sorted(
                {
                    t.region
                    for t in telemetry
                }
            ),
        }

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            DistributedRuntimeFabricAssessment
        ),
    ) -> None:

        self._assessments.append(
            assessment
        )

        payload = asdict(
            assessment
        )

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
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Distributed fabric memory write failed: {exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _distributed_confidence(
        self,
        nodes: Sequence[
            RuntimeNode
        ],
    ) -> float:

        if not nodes:
            return 0.0

        healthy = len(
            [
                n
                for n in nodes
                if n.healthy
            ]
        )

        return self._clamp_probability(
            healthy / len(nodes)
        )

    def _rationale(
        self,
        *,
        fabric_state: str,
        failover_state: str,
        runtime_count: int,
    ) -> str:

        return (
            f"Distributed sovereign "
            f"runtime evaluation "
            f"completed. "
            f"Fabric state "
            f"{fabric_state}; "
            f"failover state "
            f"{failover_state}; "
            f"runtime count "
            f"{runtime_count}."
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
    def _clamp_probability(
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

    def _avg_score(
        self,
        values: Sequence[float],
        *,
        default: float = 0.0,
    ) -> float:

        if not values:
            return default

        return self._clamp_score(
            statistics.mean(values)
        )


def build_distributed_sovereign_runtime_fabric(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> (
    DistributedSovereignRuntimeFabric
):

    return (
        DistributedSovereignRuntimeFabric(
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