"""
core/agents/action_execution_router.py

Real Agent Execution Pipeline.

Bridge between:
- autonomous agents
- policy engine
- real external connectors
- rollback handlers
- graph memory
- telemetry streaming
- case orchestration

Execution flow:
agent
  -> action_execution_router
  -> agent_policy_engine
  -> execution_sandbox
  -> connector
  -> telemetry
  -> graph_memory
  -> optional case_orchestrator
"""

from __future__ import annotations

import time
import uuid
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from core.connectors.connector_execution_fabric import (
    get_connector_execution_fabric,
)
from core.connectors.base_connector import (
    ConnectorActionResult,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_BLOCKED,
    STATUS_SKIPPED,
)

from core.security.execution_sandbox import (
    sandbox_check,
    DECISION_BLOCK as SANDBOX_DECISION_BLOCK,
    DECISION_REQUIRE_APPROVAL as SANDBOX_DECISION_REQUIRE_APPROVAL,
)

from core.runtime.tenant_execution_context import (
    get_current_tenant_context,
)

from core.connectors.crowdstrike_connector import CrowdStrikeConnector

try:
    from core.connectors.microsoft_graph_connector import (
        MicrosoftGraphConnector,
    )
except Exception:
    MicrosoftGraphConnector = None

try:
    from core.policy.agent_policy_engine import (
        AgentPolicyEngine,
        AgentPolicyDecision,
        DECISION_ALLOW,
        DECISION_BLOCK,
        DECISION_REQUIRE_APPROVAL,
        DECISION_ESCALATE,
    )
except Exception:
    AgentPolicyEngine = None
    AgentPolicyDecision = None
    DECISION_ALLOW = "ALLOW"
    DECISION_BLOCK = "BLOCK"
    DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DECISION_ESCALATE = "ESCALATE"

try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None

try:
    from core.ai.orchestration.graph_memory import (
        GraphMemory,
        GraphMemoryRecord,
    )
except Exception:
    GraphMemory = None
    GraphMemoryRecord = None


# ============================================================
# ROUTER RESULT
# ============================================================

@dataclass
class ActionExecutionRouterResult:
    success: bool
    status: str
    agent_name: str
    action: str
    routed_connector: Optional[str] = None
    target: Optional[str] = None
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    policy_decision: Optional[str] = None
    requires_approval: bool = False
    requires_escalation: bool = False
    requires_legal: bool = False

    sandbox_decision: Optional[str] = None
    sandbox_reason: Optional[str] = None
    approval_required: bool = False

    rollback_supported: bool = False
    rollback_connector: Optional[str] = None
    rollback_action: Optional[str] = None
    rollback_data: Dict[str, Any] = field(default_factory=dict)

    connector_result: Optional[ConnectorActionResult] = None

    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ACTION EXECUTION ROUTER
# ============================================================

class ActionExecutionRouter:
    """
    Central operational execution pipeline.

    Responsibilities:
    - route autonomous actions to real connectors
    - enforce policy
    - enforce sandbox safety
    - block unsafe actions
    - capture telemetry
    - support rollback
    - register learning memory
    - invoke escalation/case hooks
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
    ):
        self.storage = storage
        self.config = config or {}
        self.dry_run = bool(self.config.get("dry_run", dry_run))

        self.policy_engine = AgentPolicyEngine() if AgentPolicyEngine else None
        self.graph_memory = GraphMemory() if GraphMemory else None

        self.connectors = self._initialize_connectors()
        # ------------------------------------------------
        # CONNECTOR EXECUTION FABRIC
        # ------------------------------------------------

        self.execution_fabric = get_connector_execution_fabric(
            connectors=self.connectors,
            config=self.config,
        )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def _initialize_connectors(self) -> Dict[str, Any]:
        connector_config = self.config.get("connectors", {})

        connectors = {
            "crowdstrike": CrowdStrikeConnector(
                config=connector_config.get("crowdstrike", {}),
                dry_run=self.dry_run,
            )
        }

        if MicrosoftGraphConnector is not None:
            connectors["microsoft_graph"] = MicrosoftGraphConnector(
                config=connector_config.get("microsoft_graph", {}),
                dry_run=self.dry_run,
            )

        return connectors

    # ========================================================
    # TELEMETRY
    # ========================================================

    def emit_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        dispatch_event(
            event_type=event_type,
            payload=payload or {},
            source="action_execution_router",
        )

    # ========================================================
    # ROUTING
    # ========================================================

    def route_action_to_connector(
        self,
        agent_name: str,
        action: str,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """
        Maps agent-level actions to connector providers.
        """

        explicit_connector = context.get("connector")
        if explicit_connector:
            return explicit_connector

        endpoint_actions = {
            "endpoint_quarantine",
            "contain_host",
            "lift_containment",
            "verify_containment",
            "process_kill",
            "rtr_command",
            "sensor_telemetry",
        }

        identity_actions = {
            "token_revocation",
            "session_kill",
            "disable_user",
            "enable_user",
            "revoke_sessions",
            "mailbox_isolation",
            "mailbox_quarantine",
            "message_search",
            "message_purge",
            "legal_hold",
            "enforce_mfa",
            "conditional_access_trigger",
        }

        if action in endpoint_actions:
            return "crowdstrike"

        if action in identity_actions:
            return context.get("identity_connector") or "microsoft_graph"

        return context.get("default_connector")

    def normalize_connector_action(
        self,
        agent_name: str,
        action: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Converts agent actions into connector-native action names.
        """

        mapping = {
            "endpoint_quarantine": "contain_host",
            "contain_host": "contain_host",
            "verify_containment": "verify_containment",
            "containment_rollback": "lift_containment",
            "token_revocation": "revoke_sessions",
            "session_kill": "revoke_sessions",
            "mailbox_isolation": "mailbox_quarantine",
        }

        return mapping.get(action, action)

    def resolve_target(
        self,
        action: str,
        connector_action: str,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """
        Resolves target for connector execution.
        """

        if connector_action in {
            "contain_host",
            "lift_containment",
            "verify_containment",
            "process_kill",
            "rtr_command",
            "sensor_telemetry",
        }:
            return (
                context.get("aid")
                or context.get("device_id")
                or context.get("endpoint_id")
                or context.get("endpoint")
                or context.get("host_id")
            )

        if connector_action in {
            "revoke_sessions",
            "disable_user",
            "enable_user",
            "mailbox_quarantine",
            "message_search",
            "message_purge",
            "legal_hold",
            "enforce_mfa",
            "conditional_access_trigger",
        }:
            return (
                context.get("user_id")
                or context.get("user")
                or context.get("mailbox")
                or context.get("email")
            )

        return context.get("target")

    # ========================================================
    # POLICY
    # ========================================================

    def evaluate_policy(
        self,
        agent_name: str,
        action: str,
        context: Dict[str, Any],
    ) -> Any:
        if not self.policy_engine:
            return None

        return self.policy_engine.evaluate(
            agent_name=agent_name,
            action=action,
            context=context,
        )

    def _policy_blocks_execution(self, decision: Any) -> bool:
        if decision is None:
            return False

        if getattr(decision, "decision", None) == DECISION_BLOCK:
            return True

        if getattr(decision, "requires_approval", False):
            return True

        return not bool(getattr(decision, "allowed", False))

    # ========================================================
    # MAIN EXECUTION
    # ========================================================

    def execute(
        self,
        agent_name: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        allow_destructive: bool = False,
        graph_id: Optional[str] = None,
    ) -> ActionExecutionRouterResult:

        context = context or {}
        execution_id = str(uuid.uuid4())

        self.emit_event(
            "ACTION_ROUTER_EXECUTION_STARTED",
            {
                "execution_id": execution_id,
                "agent_name": agent_name,
                "action": action,
                "context": self._safe_context(context),
            },
        )

        try:
            # ------------------------------------------------
            # POLICY
            # ------------------------------------------------

            policy_decision = self.evaluate_policy(
                agent_name=agent_name,
                action=action,
                context=context,
            )

            if self._policy_blocks_execution(policy_decision):

                result = ActionExecutionRouterResult(
                    success=False,
                    status=STATUS_BLOCKED,
                    agent_name=agent_name,
                    action=action,
                    execution_id=execution_id,
                    policy_decision=getattr(policy_decision, "decision", None),
                    requires_approval=getattr(policy_decision, "requires_approval", False),
                    requires_escalation=getattr(policy_decision, "requires_escalation", False),
                    requires_legal=getattr(policy_decision, "requires_legal", False),
                    approval_required=getattr(policy_decision, "requires_approval", False),
                    message=getattr(policy_decision, "reason", "policy_blocked"),
                    error=getattr(policy_decision, "reason", "policy_blocked"),
                    metadata={
                        "policy": getattr(policy_decision, "__dict__", {}),
                    },
                )

                self.emit_event(
                    "ACTION_ROUTER_POLICY_BLOCKED",
                    result.__dict__,
                )

                self._invoke_case_orchestration(result, context)
                return result

            # ------------------------------------------------
            # CONNECTOR ROUTING
            # ------------------------------------------------

            connector_name = self.route_action_to_connector(
                agent_name=agent_name,
                action=action,
                context=context,
            )

            if not connector_name:
                return self._failed(
                    execution_id=execution_id,
                    agent_name=agent_name,
                    action=action,
                    status=STATUS_FAILED,
                    error="no_connector_route",
                    message="No connector route found for action.",
                    policy_decision=policy_decision,
                    context=context,
                )

            connector = self.connectors.get(connector_name)

            if connector is None:
                return self._failed(
                    execution_id=execution_id,
                    agent_name=agent_name,
                    action=action,
                    status=STATUS_FAILED,
                    routed_connector=connector_name,
                    error="connector_unavailable",
                    message=f"Connector unavailable: {connector_name}",
                    policy_decision=policy_decision,
                    context=context,
                )

            connector_action = self.normalize_connector_action(
                agent_name=agent_name,
                action=action,
                context=context,
            )

            target = self.resolve_target(
                action=action,
                connector_action=connector_action,
                context=context,
            )

            # ------------------------------------------------
            # TENANT CONTEXT
            # ------------------------------------------------

            tenant_ctx = get_current_tenant_context()

            tenant_id = (
                context.get("tenant_id")
                or (
                    tenant_ctx.tenant_id
                    if tenant_ctx
                    else "default"
                )
            )

            autonomy_mode = (
                context.get("autonomy_mode")
                or (
                    tenant_ctx.autonomy_mode
                    if tenant_ctx
                    else "MANUAL"
                )
            )

            severity = str(
                context.get("severity")
                or "LOW"
            ).upper()

            # ------------------------------------------------
            # SANDBOX
            # ------------------------------------------------

            rollback_supported = bool(
                getattr(connector, "supports_rollback", False)
            )

            sandbox_result = sandbox_check(
                tenant_id=tenant_id,
                action=action,
                connector=connector_name,
                target=target,
                rollback_supported=rollback_supported,
                context={
                    **context,
                    "tenant_id": tenant_id,
                    "autonomy_mode": autonomy_mode,
                    "severity": severity,
                    "graph_id": graph_id,
                    "case_id": context.get("case_id"),
                },
            )

            if sandbox_result.decision == SANDBOX_DECISION_BLOCK:

                self.emit_event(
                    "AUTONOMOUS_ACTION_BLOCKED_BY_SANDBOX",
                    {
                        "tenant_id": tenant_id,
                        "action": action,
                        "connector": connector_name,
                        "target": target,
                        "reason": sandbox_result.reason,
                        "graph_id": graph_id,
                    },
                )

                return ActionExecutionRouterResult(
                    success=False,
                    status="SANDBOX_BLOCKED",
                    agent_name=agent_name,
                    action=action,
                    routed_connector=connector_name,
                    target=target,
                    execution_id=execution_id,
                    sandbox_decision=sandbox_result.decision,
                    sandbox_reason=sandbox_result.reason,
                    approval_required=False,
                    error=f"Execution blocked by sandbox: {sandbox_result.reason}",
                    metadata={
                        "sandbox_id": sandbox_result.sandbox_id,
                        "tenant_id": tenant_id,
                    },
                )

            if sandbox_result.decision == SANDBOX_DECISION_REQUIRE_APPROVAL:

                self.emit_event(
                    "AUTONOMOUS_ACTION_REQUIRES_APPROVAL",
                    {
                        "tenant_id": tenant_id,
                        "action": action,
                        "connector": connector_name,
                        "target": target,
                        "reason": sandbox_result.reason,
                        "graph_id": graph_id,
                    },
                )

                return ActionExecutionRouterResult(
                    success=False,
                    status="APPROVAL_REQUIRED",
                    agent_name=agent_name,
                    action=action,
                    routed_connector=connector_name,
                    target=target,
                    execution_id=execution_id,
                    sandbox_decision=sandbox_result.decision,
                    sandbox_reason=sandbox_result.reason,
                    approval_required=True,
                    requires_approval=True,
                    error=f"Approval required by sandbox: {sandbox_result.reason}",
                    metadata={
                        "sandbox_id": sandbox_result.sandbox_id,
                        "tenant_id": tenant_id,
                    },
                )

            self.emit_event(
                "AUTONOMOUS_ACTION_SANDBOX_APPROVED",
                {
                    "tenant_id": tenant_id,
                    "action": action,
                    "connector": connector_name,
                    "target": target,
                    "graph_id": graph_id,
                    "sandbox_id": sandbox_result.sandbox_id,
                },
            )

            # ------------------------------------------------
            # CONNECTOR EXECUTION
            # ------------------------------------------------

            # ------------------------------------------------
            # EXECUTION FABRIC
            # ------------------------------------------------

            fabric_result = self.execution_fabric.execute(
                capability=connector_action,
                action=connector_action,
                target=target,
                payload={
                    **context,
                    "graph_id": graph_id,
                    "tenant_id": tenant_id,
                    "severity": severity,
                    "autonomy_mode": autonomy_mode,
                },
                tenant_id=tenant_id,
                preferred_connector=connector_name,
                allow_destructive=(
                        allow_destructive
                        or self._allow_from_policy(policy_decision, context)
                ),
            )

            connector_result = fabric_result.connector_result
            if connector_result is None:

                return ActionExecutionRouterResult(
                    success=False,
                    status=fabric_result.status,
                    agent_name=agent_name,
                    action=action,
                    execution_id=execution_id,
                    routed_connector=connector_name,
                    target=target,
                    policy_decision=getattr(policy_decision, "decision", None),
                    requires_approval=getattr(policy_decision, "requires_approval", False),
                    requires_escalation=getattr(policy_decision, "requires_escalation", False),
                    requires_legal=getattr(policy_decision, "requires_legal", False),
                    sandbox_decision=sandbox_result.decision,
                    sandbox_reason=sandbox_result.reason,
                    approval_required=False,
                    rollback_supported=False,
                    connector_result=None,
                    message=fabric_result.message,
                    error=fabric_result.error,
                    metadata={
                        "fabric_execution_id": fabric_result.fabric_execution_id,
                        "connector_attempts": [
                            a.__dict__
                            for a in fabric_result.attempts
                        ],
                        "graph_id": graph_id,
                    },
                )
            result = ActionExecutionRouterResult(
                success=connector_result.success,
                status=connector_result.status,
                agent_name=agent_name,
                action=action,
                execution_id=execution_id,
                routed_connector=connector_name,
                target=target,
                policy_decision=getattr(policy_decision, "decision", None),
                requires_approval=getattr(policy_decision, "requires_approval", False),
                requires_escalation=getattr(policy_decision, "requires_escalation", False),
                requires_legal=getattr(policy_decision, "requires_legal", False),
                sandbox_decision=sandbox_result.decision,
                sandbox_reason=sandbox_result.reason,
                approval_required=False,
                rollback_supported=fabric_result.rollback_supported,
                rollback_connector=fabric_result.rollback_connector,
                rollback_action=fabric_result.rollback_action,
                rollback_data=fabric_result.rollback_data,
                connector_result=connector_result,
                message=connector_result.message,
                error=connector_result.error,
                metadata={
                    "connector_action": connector_action,
                    "graph_id": graph_id,
                    "policy": getattr(policy_decision, "__dict__", {}),
                    "fabric_execution_id": fabric_result.fabric_execution_id,
                    "connector_attempts": [
                        a.__dict__
                        for a in fabric_result.attempts
                    ],
                },
            )

            self.emit_event(
                "ACTION_ROUTER_EXECUTION_COMPLETED",
                self._result_payload(result),
            )

            if result.requires_escalation or result.requires_legal:
                self._invoke_escalation(result, context)

            self._record_graph_memory(
                graph_id=graph_id,
                result=result,
                context=context,
            )

            self._invoke_case_orchestration(result, context)

            return result

        except Exception:
            error = traceback.format_exc()

            result = ActionExecutionRouterResult(
                success=False,
                status=STATUS_FAILED,
                agent_name=agent_name,
                action=action,
                execution_id=execution_id,
                error=error,
                message="Action execution router failed.",
            )

            self.emit_event(
                "ACTION_ROUTER_EXECUTION_FAILED",
                self._result_payload(result),
            )

            self._invoke_case_orchestration(result, context)
            return result

    # ========================================================
    # FAILOVER
    # ========================================================

    def execute_with_failover(
        self,
        agent_name: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        connector_order: Optional[List[str]] = None,
        allow_destructive: bool = False,
        graph_id: Optional[str] = None,
    ) -> ActionExecutionRouterResult:

        context = context or {}
        connector_order = connector_order or []

        if not connector_order:
            primary = self.route_action_to_connector(agent_name, action, context)
            connector_order = [primary] if primary else []

        last_result: Optional[ActionExecutionRouterResult] = None

        for connector_name in connector_order:

            if not connector_name:
                continue

            attempt_context = dict(context)
            attempt_context["connector"] = connector_name

            result = self.execute(
                agent_name=agent_name,
                action=action,
                context=attempt_context,
                allow_destructive=allow_destructive,
                graph_id=graph_id,
            )

            last_result = result

            if result.success:
                return result

            self.emit_event(
                "ACTION_ROUTER_CONNECTOR_FAILOVER",
                {
                    "agent_name": agent_name,
                    "action": action,
                    "failed_connector": connector_name,
                    "error": result.error,
                },
            )

        return last_result or ActionExecutionRouterResult(
            success=False,
            status=STATUS_FAILED,
            agent_name=agent_name,
            action=action,
            error="no_failover_connector_available",
        )

    # ========================================================
    # ROLLBACK
    # ========================================================

    def rollback(
        self,
        result: ActionExecutionRouterResult,
    ) -> ActionExecutionRouterResult:

        if not result.rollback_supported:
            return ActionExecutionRouterResult(
                success=False,
                status=STATUS_FAILED,
                agent_name=result.agent_name,
                action="rollback",
                routed_connector=result.rollback_connector,
                error="rollback_not_supported",
                message="Rollback not supported for this execution result.",
            )

        connector = self.connectors.get(result.rollback_connector or "")

        if connector is None:
            return ActionExecutionRouterResult(
                success=False,
                status=STATUS_FAILED,
                agent_name=result.agent_name,
                action="rollback",
                routed_connector=result.rollback_connector,
                error="rollback_connector_unavailable",
            )

        connector_result = connector.rollback(
            rollback_action=result.rollback_action or "",
            rollback_data=result.rollback_data,
        )

        rollback_result = ActionExecutionRouterResult(
            success=connector_result.success,
            status=connector_result.status,
            agent_name=result.agent_name,
            action="rollback",
            routed_connector=result.rollback_connector,
            target=result.target,
            connector_result=connector_result,
            message=connector_result.message,
            error=connector_result.error,
        )

        self.emit_event(
            "ACTION_ROUTER_ROLLBACK_COMPLETED",
            self._result_payload(rollback_result),
        )

        return rollback_result

    # ========================================================
    # GRAPH MEMORY
    # ========================================================

    def _record_graph_memory(
        self,
        graph_id: Optional[str],
        result: ActionExecutionRouterResult,
        context: Dict[str, Any],
    ) -> None:

        if not graph_id or not self.graph_memory or not GraphMemoryRecord:
            return

        try:
            record = GraphMemoryRecord(
                graph_id=graph_id,
                tenant_id=str(context.get("tenant_id") or "default"),
                graph_type=str(context.get("graph_type") or "action_execution"),
                success=result.success,
                status=result.status,
                rollback_count=0,
                failed_nodes=[] if result.success else [result.action],
                executed_nodes=[result.action],
                verification_confidence=float(context.get("verification_confidence") or 0.0),
                escalation_triggered=result.requires_escalation,
                containment_effective=result.success if result.action in {
                    "endpoint_quarantine",
                    "contain_host",
                    "mailbox_isolation",
                } else None,
                policy_decision=result.policy_decision,
                metadata=self._result_payload(result),
            )

            self.graph_memory.record_graph_result(record)

            self.emit_event(
                "ACTION_ROUTER_GRAPH_MEMORY_RECORDED",
                {
                    "graph_id": graph_id,
                    "agent_name": result.agent_name,
                    "action": result.action,
                    "success": result.success,
                },
            )

        except Exception:
            self.emit_event(
                "ACTION_ROUTER_GRAPH_MEMORY_FAILED",
                {
                    "graph_id": graph_id,
                    "error": traceback.format_exc(),
                },
            )

    # ========================================================
    # ESCALATION / CASE HOOKS
    # ========================================================

    def _invoke_escalation(
        self,
        result: ActionExecutionRouterResult,
        context: Dict[str, Any],
    ) -> None:

        self.emit_event(
            "ACTION_ROUTER_ESCALATION_REQUIRED",
            {
                "execution_id": result.execution_id,
                "agent_name": result.agent_name,
                "action": result.action,
                "requires_legal": result.requires_legal,
                "requires_escalation": result.requires_escalation,
                "context": self._safe_context(context),
            },
        )

    def _invoke_case_orchestration(
        self,
        result: ActionExecutionRouterResult,
        context: Dict[str, Any],
    ) -> None:
        """
        Optional bridge for:
        core/cases/autonomous_case_orchestrator.py
        """

        try:
            from core.cases.autonomous_case_orchestrator import (
                AutonomousCaseOrchestrator,
            )

            orchestrator = AutonomousCaseOrchestrator(storage=self.storage)

            orchestrator.record_autonomous_action(
                action_result=result,
                context=context,
            )

        except Exception:
            self.emit_event(
                "ACTION_ROUTER_CASE_ORCHESTRATION_SKIPPED",
                {
                    "execution_id": result.execution_id,
                    "reason": "case_orchestrator_unavailable_or_failed",
                },
            )

    # ========================================================
    # SAFETY HELPERS
    # ========================================================

    def _allow_from_policy(
        self,
        policy_decision: Any,
        context: Dict[str, Any],
    ) -> bool:

        if policy_decision is None:
            return False

        if getattr(policy_decision, "decision", None) == DECISION_ALLOW:

            return bool(
                context.get("allow_destructive")
                or context.get("autonomy_mode") in {
                    "FULL_AUTONOMY",
                    "LOCKDOWN",
                }
            )

        return False

    def _safe_context(self, context: Dict[str, Any]) -> Dict[str, Any]:

        redacted = {}

        sensitive_keys = {
            "client_secret",
            "password",
            "token",
            "access_token",
            "refresh_token",
            "api_key",
            "secret",
        }

        for k, v in context.items():

            if k.lower() in sensitive_keys:
                redacted[k] = "***REDACTED***"
            else:
                redacted[k] = v

        return redacted

    def _result_payload(
        self,
        result: ActionExecutionRouterResult,
    ) -> Dict[str, Any]:

        payload = result.__dict__.copy()

        connector_result = payload.get("connector_result")

        if connector_result is not None:
            payload["connector_result"] = connector_result.__dict__

        return payload

    def _failed(
        self,
        execution_id: str,
        agent_name: str,
        action: str,
        status: str,
        error: str,
        message: str,
        context: Dict[str, Any],
        policy_decision: Any = None,
        routed_connector: Optional[str] = None,
    ) -> ActionExecutionRouterResult:

        result = ActionExecutionRouterResult(
            success=False,
            status=status,
            agent_name=agent_name,
            action=action,
            execution_id=execution_id,
            routed_connector=routed_connector,
            policy_decision=getattr(policy_decision, "decision", None),
            requires_approval=getattr(policy_decision, "requires_approval", False),
            requires_escalation=getattr(policy_decision, "requires_escalation", False),
            requires_legal=getattr(policy_decision, "requires_legal", False),
            error=error,
            message=message,
            metadata={
                "context": self._safe_context(context),
                "policy": getattr(policy_decision, "__dict__", {}),
            },
        )

        self.emit_event(
            "ACTION_ROUTER_EXECUTION_FAILED",
            self._result_payload(result),
        )

        self._invoke_case_orchestration(result, context)

        return result