"""
core/runtime/sovereign_operational_state_graph.py

Sovereign Operational State Graph

Unified sovereign operational topology cognition layer.

This subsystem models:
- operational topology
- engine relationships
- infrastructure relationships
- governance topology
- execution topology
- resilience topology
- survivability topology
- telemetry relationships
- prediction ancestry
- dependency intelligence
- operational state transitions

IMPORTANT:
This subsystem DOES NOT:
- directly execute runtime actions
- directly mutate infrastructure
- directly orchestrate failovers
- directly trigger governance actions

It ONLY:
- models operational topology
- records operational state relationships
- models dependency lineage
- models causal propagation
- enables future digital twin simulation
- emits replayable graph lineage/evidence
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_GRAPH_NAME = (
    "sovereign_operational_state_graph"
)

NODE_STATE_ACTIVE = "ACTIVE"
NODE_STATE_DEGRADED = "DEGRADED"
NODE_STATE_UNSTABLE = "UNSTABLE"
NODE_STATE_RECOVERING = "RECOVERING"
NODE_STATE_FAILED = "FAILED"
NODE_STATE_UNKNOWN = "UNKNOWN"

EDGE_RELATIONSHIP_DEPENDS_ON = (
    "DEPENDS_ON"
)
EDGE_RELATIONSHIP_INFLUENCES = (
    "INFLUENCES"
)
EDGE_RELATIONSHIP_COORDINATES = (
    "COORDINATES"
)
EDGE_RELATIONSHIP_ESCALATES_TO = (
    "ESCALATES_TO"
)
EDGE_RELATIONSHIP_RECOVERS = (
    "RECOVERS"
)
EDGE_RELATIONSHIP_PREDICTS = (
    "PREDICTS"
)
EDGE_RELATIONSHIP_VERIFIES = (
    "VERIFIES"
)
EDGE_RELATIONSHIP_GOVERNS = (
    "GOVERNS"
)

GRAPH_EVENT_NODE_CREATED = (
    "NODE_CREATED"
)
GRAPH_EVENT_NODE_UPDATED = (
    "NODE_UPDATED"
)
GRAPH_EVENT_EDGE_CREATED = (
    "EDGE_CREATED"
)
GRAPH_EVENT_TRANSITION = (
    "STATE_TRANSITION"
)

DEFAULT_DOMAIN = "GLOBAL"

DEFAULT_NODE_TYPE_ENGINE = "ENGINE"
DEFAULT_NODE_TYPE_CONNECTOR = (
    "CONNECTOR"
)
DEFAULT_NODE_TYPE_TENANT = "TENANT"
DEFAULT_NODE_TYPE_CASE = "CASE"
DEFAULT_NODE_TYPE_RUNTIME = "RUNTIME"
DEFAULT_NODE_TYPE_GOVERNANCE = (
    "GOVERNANCE"
)
DEFAULT_NODE_TYPE_AUTONOMY = (
    "AUTONOMY"
)
DEFAULT_NODE_TYPE_INFRASTRUCTURE = (
    "INFRASTRUCTURE"
)
DEFAULT_NODE_TYPE_UNKNOWN = (
    "UNKNOWN"
)


# ============================================================
# ENUMS
# ============================================================

class OperationalNodeType(str, Enum):
    ENGINE = "ENGINE"
    CONNECTOR = "CONNECTOR"
    TENANT = "TENANT"
    CASE = "CASE"
    GOVERNANCE = "GOVERNANCE"
    AUTONOMY = "AUTONOMY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    EXECUTION = "EXECUTION"
    TELEMETRY = "TELEMETRY"
    RESILIENCE = "RESILIENCE"
    PREDICTION = "PREDICTION"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"


class OperationalEdgeType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    INFLUENCES = "INFLUENCES"
    COORDINATES = "COORDINATES"
    ESCALATES_TO = "ESCALATES_TO"
    RECOVERS = "RECOVERS"
    PREDICTS = "PREDICTS"
    VERIFIES = "VERIFIES"
    GOVERNS = "GOVERNS"
    ROUTES_TO = "ROUTES_TO"
    OBSERVES = "OBSERVES"
    UNKNOWN = "UNKNOWN"


class OperationalState(str, Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    UNSTABLE = "UNSTABLE"
    RECOVERING = "RECOVERING"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class OperationalGraphNode:
    """
    Operational graph node.
    """

    node_id: str

    node_name: str
    node_type: str
    state: str

    domain: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    survivability_score: float = 100.0
    resilience_score: float = 100.0
    prediction_risk_score: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )

    updated_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class OperationalGraphEdge:
    """
    Operational graph edge.
    """

    edge_id: str

    source_node_id: str
    target_node_id: str

    relationship_type: str

    weight: float = 1.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class OperationalStateTransition:
    """
    Replayable state transition.
    """

    transition_id: str

    node_id: str

    previous_state: str
    new_state: str

    reason: str

    transition_metadata: Dict[
        str,
        Any,
    ] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class SovereignOperationalGraphSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    graph_name: str

    total_nodes: int
    total_edges: int
    total_transitions: int

    degraded_nodes: int
    unstable_nodes: int
    failed_nodes: int

    created_at_ms: int


# ============================================================
# GRAPH ENGINE
# ============================================================

class SovereignOperationalStateGraph:
    """
    Sovereign operational topology cognition graph.
    """

    def __init__(
        self,
        *,
        graph_name: str = DEFAULT_GRAPH_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[
            Any
        ] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: (
            Optional[Any]
        ) = None,
    ) -> None:

        self.graph_name = graph_name

        self.event_bus = event_bus

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._nodes: Dict[
            str,
            OperationalGraphNode,
        ] = {}

        self._edges: Dict[
            str,
            OperationalGraphEdge,
        ] = {}

        self._transitions: List[
            OperationalStateTransition
        ] = []

        self._adjacency: Dict[
            str,
            Set[str],
        ] = defaultdict(set)

    # ========================================================
    # NODE MANAGEMENT
    # ========================================================

    def upsert_node(
        self,
        *,
        node_name: str,
        node_type: str,
        state: str = NODE_STATE_ACTIVE,
        domain: str = DEFAULT_DOMAIN,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        survivability_score: float = 100.0,
        resilience_score: float = 100.0,
        prediction_risk_score: float = 0.0,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> OperationalGraphNode:
        """
        Create or update operational node.
        """

        existing = self.find_node_by_name(
            node_name
        )

        now_ms = int(time.time() * 1000)

        if existing:

            updated = OperationalGraphNode(
                node_id=existing.node_id,
                node_name=existing.node_name,
                node_type=(
                    self._safe_node_type(
                        node_type
                    )
                ),
                state=self._safe_state(
                    state
                ),
                domain=domain or DEFAULT_DOMAIN,
                tenant_id=(
                    tenant_id
                    or existing.tenant_id
                ),
                case_id=(
                    case_id
                    or existing.case_id
                ),
                correlation_id=(
                    correlation_id
                    or existing.correlation_id
                ),
                survivability_score=(
                    self._clamp_score(
                        survivability_score
                    )
                ),
                resilience_score=(
                    self._clamp_score(
                        resilience_score
                    )
                ),
                prediction_risk_score=(
                    self._clamp_score(
                        prediction_risk_score
                    )
                ),
                metadata=dict(
                    metadata or {}
                ),
                created_at_ms=(
                    existing.created_at_ms
                ),
                updated_at_ms=now_ms,
            )

            if existing.state != updated.state:

                self._record_transition(
                    node_id=updated.node_id,
                    previous_state=(
                        existing.state
                    ),
                    new_state=(
                        updated.state
                    ),
                    reason=(
                        "node_state_updated"
                    ),
                )

            self._nodes[
                updated.node_id
            ] = updated

            self._record_graph_event(
                GRAPH_EVENT_NODE_UPDATED,
                updated,
            )

            return updated

        node = OperationalGraphNode(
            node_id=str(uuid.uuid4()),
            node_name=node_name,
            node_type=self._safe_node_type(
                node_type
            ),
            state=self._safe_state(
                state
            ),
            domain=domain or DEFAULT_DOMAIN,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            survivability_score=(
                self._clamp_score(
                    survivability_score
                )
            ),
            resilience_score=(
                self._clamp_score(
                    resilience_score
                )
            ),
            prediction_risk_score=(
                self._clamp_score(
                    prediction_risk_score
                )
            ),
            metadata=dict(metadata or {}),
        )

        self._nodes[node.node_id] = node

        self._record_graph_event(
            GRAPH_EVENT_NODE_CREATED,
            node,
        )

        return node

    def find_node_by_name(
        self,
        node_name: str,
    ) -> Optional[OperationalGraphNode]:

        for node in self._nodes.values():

            if (
                node.node_name
                == node_name
            ):
                return node

        return None

    # ========================================================
    # EDGE MANAGEMENT
    # ========================================================

    def connect(
        self,
        *,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        weight: float = 1.0,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> OperationalGraphEdge:
        """
        Connect operational nodes.
        """

        edge = OperationalGraphEdge(
            edge_id=str(uuid.uuid4()),
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=(
                self._safe_edge_type(
                    relationship_type
                )
            ),
            weight=max(
                0.0,
                float(weight),
            ),
            metadata=dict(metadata or {}),
        )

        self._edges[edge.edge_id] = edge

        self._adjacency[
            source_node_id
        ].add(target_node_id)

        self._record_graph_event(
            GRAPH_EVENT_EDGE_CREATED,
            edge,
        )

        return edge

    # ========================================================
    # TOPOLOGY ANALYSIS
    # ========================================================

    def get_neighbors(
        self,
        node_id: str,
    ) -> List[
        OperationalGraphNode
    ]:

        neighbors = []

        for neighbor_id in self._adjacency.get(
            node_id,
            set(),
        ):

            node = self._nodes.get(
                neighbor_id
            )

            if node:
                neighbors.append(node)

        return neighbors

    def dependency_chain(
        self,
        node_id: str,
        *,
        max_depth: int = 5,
    ) -> List[str]:
        """
        Return dependency traversal chain.
        """

        visited: Set[str] = set()

        results: List[str] = []

        def _walk(
            current_id: str,
            depth: int,
        ) -> None:

            if (
                depth > max_depth
                or current_id in visited
            ):
                return

            visited.add(current_id)

            results.append(current_id)

            for neighbor in self._adjacency.get(
                current_id,
                set(),
            ):
                _walk(
                    neighbor,
                    depth + 1,
                )

        _walk(node_id, 0)

        return results

    def degraded_nodes(
        self,
    ) -> List[
        OperationalGraphNode
    ]:

        return [
            node
            for node in self._nodes.values()
            if node.state
            in {
                NODE_STATE_DEGRADED,
                NODE_STATE_UNSTABLE,
                NODE_STATE_FAILED,
            }
        ]

    def graph_snapshot(
        self,
    ) -> (
        SovereignOperationalGraphSnapshot
    ):

        degraded = 0
        unstable = 0
        failed = 0

        for node in self._nodes.values():

            if (
                node.state
                == NODE_STATE_DEGRADED
            ):
                degraded += 1

            elif (
                node.state
                == NODE_STATE_UNSTABLE
            ):
                unstable += 1

            elif (
                node.state
                == NODE_STATE_FAILED
            ):
                failed += 1

        return (
            SovereignOperationalGraphSnapshot(
                graph_name=self.graph_name,
                total_nodes=len(
                    self._nodes
                ),
                total_edges=len(
                    self._edges
                ),
                total_transitions=len(
                    self._transitions
                ),
                degraded_nodes=degraded,
                unstable_nodes=unstable,
                failed_nodes=failed,
                created_at_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # ========================================================
    # TRANSITIONS
    # ========================================================

    def _record_transition(
        self,
        *,
        node_id: str,
        previous_state: str,
        new_state: str,
        reason: str,
        transition_metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        transition = (
            OperationalStateTransition(
                transition_id=str(
                    uuid.uuid4()
                ),
                node_id=node_id,
                previous_state=(
                    previous_state
                ),
                new_state=new_state,
                reason=reason,
                transition_metadata=dict(
                    transition_metadata
                    or {}
                ),
            )
        )

        self._transitions.append(
            transition
        )

        self._record_graph_event(
            GRAPH_EVENT_TRANSITION,
            transition,
        )

    # ========================================================
    # EVENT RECORDING
    # ========================================================

    def _record_graph_event(
        self,
        event_type: str,
        payload_obj: Any,
    ) -> None:

        payload = {
            "event_type": event_type,
            "graph_name": self.graph_name,
            "payload": asdict(
                payload_obj
            ),
        }

        self._write_to_memory(
            payload
        )

        self._write_to_lineage(
            payload
        )

        self._write_to_evidence(
            payload
        )

        self._emit_event(payload)

    def _write_to_memory(
        self,
        payload: Dict[str, Any],
    ) -> None:

        memory = (
            self.operational_memory_engine
        )

        if memory is None:
            return

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
                f"⚠️ Graph memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        payload: Dict[str, Any],
    ) -> None:

        lineage = self.lineage_engine

        if lineage is None:
            return

        try:

            if hasattr(
                lineage,
                "record_lineage",
            ):
                lineage.record_lineage(
                    {
                        "lineage_type": (
                            "OPERATIONAL_GRAPH"
                        ),
                        "source_engine": (
                            self.graph_name
                        ),
                        "context": payload,
                    }
                )

        except Exception as exc:
            print(
                f"⚠️ Graph lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        payload: Dict[str, Any],
    ) -> None:

        evidence = (
            self
            .fedramp_evidence_lineage_engine
        )

        if evidence is None:
            return

        try:

            if hasattr(
                evidence,
                "record_evidence",
            ):
                evidence.record_evidence(
                    {
                        "evidence_type": (
                            "OPERATIONAL_GRAPH"
                        ),
                        "source_engine": (
                            self.graph_name
                        ),
                        "evidence_payload": payload,
                    }
                )

        except Exception as exc:
            print(
                f"⚠️ Graph evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        payload: Dict[str, Any],
    ) -> None:

        if self.event_bus is None:
            return

        try:

            if hasattr(
                self.event_bus,
                "emit",
            ):
                self.event_bus.emit(
                    (
                        "SOVEREIGN_OPERATIONAL_GRAPH_EVENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Graph event emit failed: {exc}"
            )

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _safe_node_type(
        value: Any,
    ) -> str:

        value = str(
            value
            or DEFAULT_NODE_TYPE_UNKNOWN
        ).upper()

        valid = {
            item.value
            for item in (
                OperationalNodeType
            )
        }

        return (
            value
            if value in valid
            else DEFAULT_NODE_TYPE_UNKNOWN
        )

    @staticmethod
    def _safe_edge_type(
        value: Any,
    ) -> str:

        value = str(
            value
            or OperationalEdgeType
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                OperationalEdgeType
            )
        }

        return (
            value
            if value in valid
            else (
                OperationalEdgeType
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_state(
        value: Any,
    ) -> str:

        value = str(
            value
            or NODE_STATE_UNKNOWN
        ).upper()

        valid = {
            item.value
            for item in (
                OperationalState
            )
        }

        return (
            value
            if value in valid
            else NODE_STATE_UNKNOWN
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


# ============================================================
# FACTORY
# ============================================================

def build_sovereign_operational_state_graph(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> SovereignOperationalStateGraph:
    """
    Factory for explicit dependency injection.
    """

    return (
        SovereignOperationalStateGraph(
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