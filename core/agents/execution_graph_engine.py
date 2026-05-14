"""
core/agents/execution_graph_engine.py

Execution Graph Engine.

Purpose:
- agents become graph nodes
- containment chains become executable graphs
- verification branches occur automatically
- rollback propagates upstream
- optimizer can tune workflow paths over time

This layer sits above AgentCoordinator.
"""

from __future__ import annotations

import time
import uuid
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from core.agents.agent_coordinator import (
    AgentCoordinator,
    CoordinatedStep,
    CoordinatedWorkflowResult,
    STATUS_PENDING,
    STATUS_RUNNING,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_BLOCKED,
    STATUS_ROLLED_BACK,
)

try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


NODE_PENDING = "PENDING"
NODE_RUNNING = "RUNNING"
NODE_COMPLETED = "COMPLETED"
NODE_FAILED = "FAILED"
NODE_BLOCKED = "BLOCKED"
NODE_SKIPPED = "SKIPPED"
NODE_ROLLED_BACK = "ROLLED_BACK"


EDGE_SUCCESS = "success"
EDGE_FAILURE = "failure"
EDGE_ALWAYS = "always"
EDGE_VERIFICATION_FAILED = "verification_failed"


@dataclass
class ExecutionGraphNode:
    node_id: str
    agent_name: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)

    required: bool = True
    rollback_on_failure: bool = True
    verification_node: bool = False
    rollback_node: bool = False

    status: str = NODE_PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionGraphEdge:
    from_node: str
    to_node: str
    condition: str = EDGE_SUCCESS


@dataclass
class ExecutionGraph:
    graph_id: str
    nodes: Dict[str, ExecutionGraphNode] = field(default_factory=dict)
    edges: List[ExecutionGraphEdge] = field(default_factory=list)
    entry_nodes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionGraphResult:
    graph_id: str
    success: bool
    status: str
    executed_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    rolled_back_nodes: List[str] = field(default_factory=list)
    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionGraphEngine:
    """
    Executes autonomous SOC workflows as directed graphs.
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        coordinator: Optional[AgentCoordinator] = None,
    ):
        self.storage = storage
        self.config = config or {}
        self.coordinator = coordinator or AgentCoordinator(storage=storage, config=config)

    # ============================================================
    # EVENTING
    # ============================================================

    def emit_event(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        dispatch_event(
            event_type=event_type,
            payload=payload or {},
            source="execution_graph_engine",
        )

    # ============================================================
    # GRAPH EXECUTION
    # ============================================================

    def execute_graph(self, graph: ExecutionGraph) -> ExecutionGraphResult:
        result = ExecutionGraphResult(
            graph_id=graph.graph_id,
            success=False,
            status=STATUS_RUNNING,
        )

        self.emit_event(
            "EXECUTION_GRAPH_STARTED",
            {
                "graph_id": graph.graph_id,
                "node_count": len(graph.nodes),
            },
        )

        executed_stack: List[str] = []
        visited: Set[str] = set()

        try:
            queue: List[str] = list(graph.entry_nodes)

            while queue:
                node_id = queue.pop(0)

                if node_id in visited:
                    continue

                node = graph.nodes.get(node_id)

                if node is None:
                    continue

                visited.add(node_id)

                node_result = self.execute_node(node)

                node.result = node_result

                if node_result and getattr(node_result, "success", False):
                    node.status = NODE_COMPLETED
                    result.executed_nodes.append(node_id)
                    executed_stack.append(node_id)

                    next_nodes = self.get_next_nodes(
                        graph=graph,
                        from_node=node_id,
                        condition=EDGE_SUCCESS,
                    )

                    next_nodes += self.get_next_nodes(
                        graph=graph,
                        from_node=node_id,
                        condition=EDGE_ALWAYS,
                    )

                    queue.extend(next_nodes)

                else:
                    node.status = NODE_FAILED
                    node.error = getattr(node_result, "error", "node_failed")
                    result.failed_nodes.append(node_id)

                    failure_nodes = self.get_next_nodes(
                        graph=graph,
                        from_node=node_id,
                        condition=EDGE_FAILURE,
                    )

                    verification_failed_nodes = []

                    if node.verification_node:
                        verification_failed_nodes = self.get_next_nodes(
                            graph=graph,
                            from_node=node_id,
                            condition=EDGE_VERIFICATION_FAILED,
                        )

                    if failure_nodes or verification_failed_nodes:
                        queue.extend(failure_nodes + verification_failed_nodes)
                    elif node.required:
                        result.status = STATUS_FAILED
                        result.error = node.error
                        result.message = f"Required node failed: {node_id}"

                        self.rollback_graph(graph, executed_stack, result)
                        return result

            result.success = not result.failed_nodes
            result.status = STATUS_COMPLETED if result.success else STATUS_FAILED

            if result.success:
                result.message = "Execution graph completed successfully."
            else:
                result.message = "Execution graph completed with failures."

            self.emit_event(
                "EXECUTION_GRAPH_COMPLETED",
                {
                    "graph_id": graph.graph_id,
                    "success": result.success,
                    "executed_nodes": result.executed_nodes,
                    "failed_nodes": result.failed_nodes,
                },
            )

            return result

        except Exception:
            error = traceback.format_exc()

            result.success = False
            result.status = STATUS_FAILED
            result.error = error
            result.message = "Execution graph failed."

            self.rollback_graph(graph, executed_stack, result)

            self.emit_event(
                "EXECUTION_GRAPH_FAILED",
                {
                    "graph_id": graph.graph_id,
                    "error": error,
                },
            )

            return result

    def execute_node(self, node: ExecutionGraphNode):
        node.status = NODE_RUNNING

        self.emit_event(
            "EXECUTION_GRAPH_NODE_STARTED",
            {
                "node_id": node.node_id,
                "agent_name": node.agent_name,
                "action": node.action,
            },
        )

        step = CoordinatedStep(
            step_id=node.node_id,
            agent_name=node.agent_name,
            action=node.action,
            context=node.context,
            required=node.required,
            rollback_on_failure=node.rollback_on_failure,
        )

        workflow_result: CoordinatedWorkflowResult = self.coordinator.execute_workflow(
            steps=[step],
            workflow_id=f"graph-node-{node.node_id}",
            require_governance=True,
        )

        if workflow_result.steps and workflow_result.steps[0].result:
            agent_result = workflow_result.steps[0].result
        else:
            agent_result = None

        self.emit_event(
            "EXECUTION_GRAPH_NODE_COMPLETED",
            {
                "node_id": node.node_id,
                "success": bool(agent_result and agent_result.success),
            },
        )

        return agent_result

    # ============================================================
    # GRAPH TRAVERSAL
    # ============================================================

    def get_next_nodes(
        self,
        graph: ExecutionGraph,
        from_node: str,
        condition: str,
    ) -> List[str]:
        return [
            edge.to_node
            for edge in graph.edges
            if edge.from_node == from_node and edge.condition == condition
        ]

    # ============================================================
    # ROLLBACK PROPAGATION
    # ============================================================

    def rollback_graph(
        self,
        graph: ExecutionGraph,
        executed_stack: List[str],
        result: ExecutionGraphResult,
    ) -> None:
        self.emit_event(
            "EXECUTION_GRAPH_ROLLBACK_STARTED",
            {
                "graph_id": graph.graph_id,
                "executed_stack": executed_stack,
            },
        )

        for node_id in reversed(executed_stack):
            node = graph.nodes.get(node_id)

            if node is None:
                continue

            try:
                if not node.result:
                    continue

                if not getattr(node.result, "rollback_supported", False):
                    continue

                agent = self.coordinator.get_agent(node.agent_name)
                if not agent:
                    continue

                rollback_data = getattr(node.result, "rollback_data", {}) or {}
                agent.rollback(rollback_data)

                node.status = NODE_ROLLED_BACK
                result.rolled_back_nodes.append(node_id)

                self.emit_event(
                    "EXECUTION_GRAPH_NODE_ROLLED_BACK",
                    {
                        "graph_id": graph.graph_id,
                        "node_id": node_id,
                        "agent_name": node.agent_name,
                        "action": node.action,
                    },
                )

            except Exception:
                self.emit_event(
                    "EXECUTION_GRAPH_ROLLBACK_FAILED",
                    {
                        "graph_id": graph.graph_id,
                        "node_id": node_id,
                        "error": traceback.format_exc(),
                    },
                )

    # ============================================================
    # GRAPH FACTORIES
    # ============================================================

    def build_containment_graph(
        self,
        context: Dict[str, Any],
    ) -> ExecutionGraph:
        graph_id = context.get("graph_id") or str(uuid.uuid4())

        graph = ExecutionGraph(
            graph_id=graph_id,
            metadata={
                "type": "containment_graph",
                "created_at_ms": int(time.time() * 1000),
            },
        )

        previous_nodes: List[str] = []

        def add_node(
            action: str,
            agent_name: str,
            required: bool = True,
            verification_node: bool = False,
            rollback_node: bool = False,
        ) -> str:
            node_id = f"{action}-{uuid.uuid4()}"

            graph.nodes[node_id] = ExecutionGraphNode(
                node_id=node_id,
                agent_name=agent_name,
                action=action,
                context=context,
                required=required,
                verification_node=verification_node,
                rollback_node=rollback_node,
            )

            return node_id

        if context.get("mailbox"):
            mailbox_node = add_node(
                action="mailbox_isolation",
                agent_name="containment_agent",
                required=True,
            )
            graph.entry_nodes.append(mailbox_node)
            previous_nodes.append(mailbox_node)

        if context.get("endpoint"):
            endpoint_node = add_node(
                action="endpoint_quarantine",
                agent_name="containment_agent",
                required=True,
            )

            if not graph.entry_nodes:
                graph.entry_nodes.append(endpoint_node)
            else:
                for prev in previous_nodes:
                    graph.edges.append(
                        ExecutionGraphEdge(prev, endpoint_node, EDGE_SUCCESS)
                    )

            previous_nodes = [endpoint_node]

        if context.get("user"):
            session_node = add_node(
                action="session_kill",
                agent_name="containment_agent",
                required=False,
            )

            token_node = add_node(
                action="token_revocation",
                agent_name="containment_agent",
                required=False,
            )

            if not graph.entry_nodes:
                graph.entry_nodes.append(session_node)

            for prev in previous_nodes:
                graph.edges.append(
                    ExecutionGraphEdge(prev, session_node, EDGE_SUCCESS)
                )

            graph.edges.append(
                ExecutionGraphEdge(session_node, token_node, EDGE_ALWAYS)
            )

            previous_nodes = [token_node]

        verification_node = add_node(
            action="verify_containment",
            agent_name="verification_agent",
            required=True,
            verification_node=True,
        )

        if not graph.entry_nodes:
            graph.entry_nodes.append(verification_node)

        for prev in previous_nodes:
            graph.edges.append(
                ExecutionGraphEdge(prev, verification_node, EDGE_SUCCESS)
            )

        rollback_node = add_node(
            action="trigger_rollback",
            agent_name="verification_agent",
            required=False,
            rollback_node=True,
        )

        graph.edges.append(
            ExecutionGraphEdge(
                verification_node,
                rollback_node,
                EDGE_VERIFICATION_FAILED,
            )
        )

        if context.get("severity") in {"HIGH", "CRITICAL"}:
            escalation_node = add_node(
                action="sla_escalation",
                agent_name="escalation_agent",
                required=False,
            )

            graph.edges.append(
                ExecutionGraphEdge(
                    verification_node,
                    escalation_node,
                    EDGE_SUCCESS,
                )
            )

        if context.get("export_control") or context.get("category") == "EXPORT_CONTROL":
            export_node = add_node(
                action="export_control_escalation",
                agent_name="escalation_agent",
                required=True,
            )

            legal_node = add_node(
                action="legal_routing",
                agent_name="escalation_agent",
                required=True,
            )

            graph.edges.append(
                ExecutionGraphEdge(
                    verification_node,
                    export_node,
                    EDGE_SUCCESS,
                )
            )

            graph.edges.append(
                ExecutionGraphEdge(
                    export_node,
                    legal_node,
                    EDGE_SUCCESS,
                )
            )

        return graph

    def execute_containment_graph(
        self,
        context: Dict[str, Any],
    ) -> ExecutionGraphResult:
        graph = self.build_containment_graph(context)
        return self.execute_graph(graph)

    # ============================================================
    # OPTIMIZER HOOKS
    # ============================================================

    def record_optimizer_feedback(
        self,
        graph: ExecutionGraph,
        result: ExecutionGraphResult,
    ) -> None:
        """
        Placeholder hook for adaptive_policy_optimizer.py.

        Future:
        - record node success rates
        - tune route priority
        - detect noisy branches
        - strengthen verification thresholds
        - reduce rollback-heavy paths
        """

        self.emit_event(
            "EXECUTION_GRAPH_OPTIMIZER_FEEDBACK",
            {
                "graph_id": graph.graph_id,
                "success": result.success,
                "status": result.status,
                "executed_nodes": result.executed_nodes,
                "failed_nodes": result.failed_nodes,
                "rolled_back_nodes": result.rolled_back_nodes,
            },
        )