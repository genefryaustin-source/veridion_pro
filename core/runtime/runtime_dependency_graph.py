"""
core/runtime/runtime_dependency_graph.py

Runtime Dependency Graph.

Purpose:
- explicit runtime service topology
- dependency validation
- circular dependency detection
- cascading failure / blast-radius analysis
- restart impact analysis
- quarantine propagation support
- runtime visualization feed
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set


NODE_STATUS_UNKNOWN = "UNKNOWN"
NODE_STATUS_READY = "READY"
NODE_STATUS_DEGRADED = "DEGRADED"
NODE_STATUS_UNAVAILABLE = "UNAVAILABLE"
NODE_STATUS_QUARANTINED = "QUARANTINED"
NODE_STATUS_STOPPED = "STOPPED"

EDGE_REQUIRED = "REQUIRED"
EDGE_OPTIONAL = "OPTIONAL"
EDGE_RUNTIME = "RUNTIME"
EDGE_EVENT = "EVENT"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeDependencyNode:
    node_id: str
    service_name: str
    tenant_id: str = DEFAULT_TENANT
    status: str = NODE_STATUS_UNKNOWN
    owner: str = "system"
    health_score: float = 100.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeDependencyEdge:
    edge_id: str
    from_service: str
    to_service: str
    edge_type: str = EDGE_REQUIRED
    tenant_id: str = DEFAULT_TENANT
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuntimeDependencyGraph:
    def __init__(
        self,
        *,
        registry: Any,
        lifecycle: Any = None,
        health_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.registry = registry
        self.lifecycle = lifecycle
        self.health_manager = health_manager
        self.storage = storage
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

    # ========================================================
    # BUILD GRAPH
    # ========================================================

    def build_graph(self) -> Dict[str, Any]:
        nodes: Dict[str, RuntimeDependencyNode] = {}
        edges: List[RuntimeDependencyEdge] = []

        services = self._safe_services()

        for record in services:
            service_name = getattr(record, "service_name", None)
            if not service_name:
                continue

            node = RuntimeDependencyNode(
                node_id=f"RDN-{service_name}",
                service_name=service_name,
                tenant_id=getattr(record, "tenant_id", DEFAULT_TENANT),
                status=self._normalize_status(getattr(record, "status", NODE_STATUS_UNKNOWN)),
                owner=getattr(record, "owner", "system"),
                health_score=float(getattr(record, "health_score", 100.0) or 100.0),
                tags=list(getattr(record, "tags", []) or []),
                metadata=dict(getattr(record, "metadata", {}) or {}),
            )

            nodes[service_name] = node

            for dep in list(getattr(record, "dependencies", []) or []):
                edges.append(
                    RuntimeDependencyEdge(
                        edge_id=f"RDE-{uuid.uuid4().hex[:12].upper()}",
                        from_service=dep,
                        to_service=service_name,
                        edge_type=EDGE_REQUIRED,
                        tenant_id=getattr(record, "tenant_id", DEFAULT_TENANT),
                    )
                )

        graph = {
            "nodes": [
                node.to_dict()
                for node in nodes.values()
            ],
            "edges": [
                edge.to_dict()
                for edge in edges
            ],
            "created_at_ms": _now_ms(),
        }

        self._emit(
            "RUNTIME_DEPENDENCY_GRAPH_BUILT",
            {
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
        )

        return graph

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> Dict[str, Any]:
        graph = self.build_graph()

        nodes = {
            n["service_name"]
            for n in graph["nodes"]
        }

        missing_dependencies = []
        orphaned_services = []
        cycles = self.detect_cycles()

        for edge in graph["edges"]:
            if edge["from_service"] not in nodes:
                missing_dependencies.append(
                    {
                        "service": edge["to_service"],
                        "missing_dependency": edge["from_service"],
                    }
                )

        dependency_targets = {
            e["to_service"]
            for e in graph["edges"]
        }

        dependency_sources = {
            e["from_service"]
            for e in graph["edges"]
        }

        for node in nodes:
            if node not in dependency_targets and node not in dependency_sources:
                orphaned_services.append(node)

        ok = (
            not missing_dependencies
            and not cycles
        )

        result = {
            "ok": ok,
            "missing_dependencies": missing_dependencies,
            "orphaned_services": orphaned_services,
            "cycles": cycles,
            "node_count": len(nodes),
            "edge_count": len(graph["edges"]),
        }

        self._emit(
            "RUNTIME_DEPENDENCY_GRAPH_VALIDATED",
            result,
        )

        return result

    def detect_cycles(self) -> List[List[str]]:
        adjacency = self._adjacency()
        visited: Set[str] = set()
        active: Set[str] = set()
        path: List[str] = []
        cycles: List[List[str]] = []

        def visit(node: str) -> None:
            if node in active:
                try:
                    idx = path.index(node)
                    cycles.append(path[idx:] + [node])
                except Exception:
                    cycles.append([node])
                return

            if node in visited:
                return

            visited.add(node)
            active.add(node)
            path.append(node)

            for nxt in adjacency.get(node, []):
                visit(nxt)

            path.pop()
            active.discard(node)

        for node in adjacency.keys():
            visit(node)

        return cycles

    # ========================================================
    # IMPACT / BLAST RADIUS
    # ========================================================

    def downstream_services(
        self,
        service_name: str,
    ) -> List[str]:
        adjacency = self._adjacency()
        downstream: Set[str] = set()

        def walk(node: str) -> None:
            for nxt in adjacency.get(node, []):
                if nxt in downstream:
                    continue
                downstream.add(nxt)
                walk(nxt)

        walk(service_name)

        return sorted(downstream)

    def upstream_services(
        self,
        service_name: str,
    ) -> List[str]:
        reverse = self._reverse_adjacency()
        upstream: Set[str] = set()

        def walk(node: str) -> None:
            for nxt in reverse.get(node, []):
                if nxt in upstream:
                    continue
                upstream.add(nxt)
                walk(nxt)

        walk(service_name)

        return sorted(upstream)

    def blast_radius(
        self,
        service_name: str,
    ) -> Dict[str, Any]:
        downstream = self.downstream_services(service_name)
        upstream = self.upstream_services(service_name)

        risk = "LOW"
        if len(downstream) >= 3:
            risk = "MEDIUM"
        if len(downstream) >= 6:
            risk = "HIGH"
        if len(downstream) >= 10:
            risk = "CRITICAL"

        result = {
            "service_name": service_name,
            "risk": risk,
            "downstream_services": downstream,
            "upstream_services": upstream,
            "affected_count": len(downstream),
            "dependency_count": len(upstream),
        }

        self._emit(
            "RUNTIME_BLAST_RADIUS_ANALYZED",
            result,
        )

        return result

    def restart_impact(
        self,
        service_name: str,
    ) -> Dict[str, Any]:
        radius = self.blast_radius(service_name)

        recommendation = "SAFE_RESTART"

        if radius["risk"] == "MEDIUM":
            recommendation = "RESTART_WITH_CAUTION"
        elif radius["risk"] == "HIGH":
            recommendation = "DRAIN_DEPENDENTS_FIRST"
        elif radius["risk"] == "CRITICAL":
            recommendation = "MAINTENANCE_WINDOW_REQUIRED"

        return {
            **radius,
            "recommendation": recommendation,
        }

    def quarantine_impact(
        self,
        service_name: str,
    ) -> Dict[str, Any]:
        radius = self.blast_radius(service_name)

        affected = radius["downstream_services"]

        return {
            **radius,
            "quarantine_action": (
                "PROPAGATE_DEGRADED_STATE"
                if affected
                else "LOCAL_ONLY"
            ),
            "affected_services": affected,
        }

    # ========================================================
    # VISUALIZATION FEED
    # ========================================================

    def visualization_payload(self) -> Dict[str, Any]:
        graph = self.build_graph()
        validation = self.validate()

        nodes = []
        edges = []

        for node in graph["nodes"]:
            nodes.append(
                {
                    "id": node["service_name"],
                    "label": node["service_name"],
                    "status": node["status"],
                    "health_score": node["health_score"],
                    "owner": node["owner"],
                    "tenant_id": node["tenant_id"],
                    "tags": node.get("tags", []),
                }
            )

        for edge in graph["edges"]:
            edges.append(
                {
                    "source": edge["from_service"],
                    "target": edge["to_service"],
                    "type": edge["edge_type"],
                }
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "validation": validation,
            "created_at_ms": _now_ms(),
        }

    # ========================================================
    # INTERNAL GRAPH HELPERS
    # ========================================================

    def _adjacency(self) -> Dict[str, List[str]]:
        graph = self.build_graph()
        adjacency: Dict[str, List[str]] = {}

        for node in graph["nodes"]:
            adjacency.setdefault(node["service_name"], [])

        for edge in graph["edges"]:
            adjacency.setdefault(edge["from_service"], [])
            adjacency.setdefault(edge["to_service"], [])
            adjacency[edge["from_service"]].append(edge["to_service"])

        return adjacency

    def _reverse_adjacency(self) -> Dict[str, List[str]]:
        graph = self.build_graph()
        reverse: Dict[str, List[str]] = {}

        for node in graph["nodes"]:
            reverse.setdefault(node["service_name"], [])

        for edge in graph["edges"]:
            reverse.setdefault(edge["from_service"], [])
            reverse.setdefault(edge["to_service"], [])
            reverse[edge["to_service"]].append(edge["from_service"])

        return reverse

    def _safe_services(self) -> List[Any]:
        if self.registry is None:
            return []

        try:
            return self.registry.list_services()
        except Exception:
            return []

    def _normalize_status(
        self,
        status: str,
    ) -> str:
        status = str(status or "").upper()

        if status in {"READY", "RUNNING"}:
            return NODE_STATUS_READY

        if status in {"DEGRADED"}:
            return NODE_STATUS_DEGRADED

        if status in {"UNAVAILABLE", "FAILED"}:
            return NODE_STATUS_UNAVAILABLE

        if status in {"QUARANTINED"}:
            return NODE_STATUS_QUARANTINED

        if status in {"STOPPED"}:
            return NODE_STATUS_STOPPED

        return NODE_STATUS_UNKNOWN

    # ========================================================
    # EVENTS
    # ========================================================

    def _emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                source="runtime_dependency_graph",
                severity="INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_RUNTIME_DEPENDENCY_GRAPH: Optional[
    RuntimeDependencyGraph
] = None


def get_runtime_dependency_graph(
    *,
    registry: Any,
    lifecycle: Any = None,
    health_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> RuntimeDependencyGraph:
    global _DEFAULT_RUNTIME_DEPENDENCY_GRAPH

    if reset or _DEFAULT_RUNTIME_DEPENDENCY_GRAPH is None:
        _DEFAULT_RUNTIME_DEPENDENCY_GRAPH = RuntimeDependencyGraph(
            registry=registry,
            lifecycle=lifecycle,
            health_manager=health_manager,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_RUNTIME_DEPENDENCY_GRAPH