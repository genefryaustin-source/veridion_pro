"""
core/runtime/tenant_execution_context.py

Tenant Execution Context.

Purpose:
- isolate queues
- isolate graph execution
- isolate telemetry
- isolate agents
- isolate evidence
- isolate escalation
- isolate optimizer learning
- isolate rollback chains

Critical for:
- GovCloud
- MSSP scale
- enterprise isolation
- future FedRAMP posture
"""

from __future__ import annotations

import time
import uuid
import json
import contextvars
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


TENANT_CONTEXT_VAR: contextvars.ContextVar[Optional["TenantExecutionContext"]] = (
    contextvars.ContextVar("tenant_execution_context", default=None)
)


@dataclass
class TenantExecutionPolicy:
    allow_autonomous_execution: bool = False
    allow_destructive_actions: bool = False
    allow_identity_actions: bool = False
    allow_endpoint_actions: bool = True
    allow_legal_routing: bool = True
    allow_export_control_escalation: bool = True

    max_concurrent_graphs: int = 5
    max_concurrent_connector_actions: int = 10
    max_rollback_chain_depth: int = 5

    default_autonomy_mode: str = "ASSISTED"
    required_approval_severity: List[str] = field(default_factory=lambda: ["HIGH", "CRITICAL"])
    restricted_connectors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantExecutionContext:
    tenant_id: str
    tenant_name: Optional[str] = None
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    user_id: Optional[str] = None
    actor: str = "system"
    autonomy_mode: str = "ASSISTED"

    case_id: Optional[Any] = None
    graph_id: Optional[str] = None
    evidence_ids: List[Any] = field(default_factory=list)

    policy: TenantExecutionPolicy = field(default_factory=TenantExecutionPolicy)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "execution_id": self.execution_id,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "actor": self.actor,
            "autonomy_mode": self.autonomy_mode,
            "case_id": self.case_id,
            "graph_id": self.graph_id,
            "evidence_ids": self.evidence_ids,
            "policy": self.policy.__dict__,
            "created_at_ms": self.created_at_ms,
            "metadata": self.metadata,
        }

    def enrich(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}

        enriched = dict(payload)
        enriched.setdefault("tenant_id", self.tenant_id)
        enriched.setdefault("tenant_name", self.tenant_name)
        enriched.setdefault("execution_id", self.execution_id)
        enriched.setdefault("correlation_id", self.correlation_id)
        enriched.setdefault("actor", self.actor)
        enriched.setdefault("autonomy_mode", self.autonomy_mode)
        enriched.setdefault("case_id", self.case_id)
        enriched.setdefault("graph_id", self.graph_id)
        enriched.setdefault("evidence_ids", self.evidence_ids)

        return enriched


class TenantContextManager:
    """
    Context manager for tenant-scoped execution.

    Usage:
        with tenant_context(ctx):
            router.execute(...)
    """

    def __init__(self, context: TenantExecutionContext):
        self.context = context
        self.token = None

    def __enter__(self) -> TenantExecutionContext:
        self.token = TENANT_CONTEXT_VAR.set(self.context)

        dispatch_event(
            "TENANT_EXECUTION_CONTEXT_ENTERED",
            self.context.as_dict(),
            source="tenant_execution_context",
        )

        return self.context

    def __exit__(self, exc_type, exc, tb) -> None:
        dispatch_event(
            "TENANT_EXECUTION_CONTEXT_EXITED",
            {
                "tenant_id": self.context.tenant_id,
                "execution_id": self.context.execution_id,
                "correlation_id": self.context.correlation_id,
                "error": str(exc) if exc else None,
            },
            source="tenant_execution_context",
        )

        if self.token is not None:
            TENANT_CONTEXT_VAR.reset(self.token)


def tenant_context(context: TenantExecutionContext) -> TenantContextManager:
    return TenantContextManager(context)


def get_current_tenant_context() -> Optional[TenantExecutionContext]:
    return TENANT_CONTEXT_VAR.get()


def require_tenant_context() -> TenantExecutionContext:
    ctx = get_current_tenant_context()

    if ctx is None:
        raise RuntimeError("Tenant execution context is required but not active.")

    return ctx


def build_tenant_context(
    tenant_id: str,
    tenant_name: Optional[str] = None,
    user_id: Optional[str] = None,
    actor: str = "system",
    autonomy_mode: str = "ASSISTED",
    case_id: Optional[Any] = None,
    graph_id: Optional[str] = None,
    evidence_ids: Optional[List[Any]] = None,
    policy: Optional[TenantExecutionPolicy] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> TenantExecutionContext:
    return TenantExecutionContext(
        tenant_id=tenant_id,
        tenant_name=tenant_name,
        user_id=user_id,
        actor=actor,
        autonomy_mode=autonomy_mode,
        case_id=case_id,
        graph_id=graph_id,
        evidence_ids=evidence_ids or [],
        policy=policy or TenantExecutionPolicy(default_autonomy_mode=autonomy_mode),
        metadata=metadata or {},
    )


def enrich_with_tenant_context(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ctx = get_current_tenant_context()

    if ctx is None:
        return payload or {}

    return ctx.enrich(payload or {})


def assert_connector_allowed(connector_name: str) -> bool:
    ctx = get_current_tenant_context()

    if ctx is None:
        return True

    if connector_name in ctx.policy.restricted_connectors:
        dispatch_event(
            "TENANT_CONNECTOR_BLOCKED",
            {
                "tenant_id": ctx.tenant_id,
                "connector": connector_name,
                "reason": "connector_restricted_by_tenant_policy",
            },
            source="tenant_execution_context",
        )
        return False

    return True


def assert_action_allowed(
    action: str,
    severity: str = "LOW",
    destructive: bool = False,
    identity_action: bool = False,
    endpoint_action: bool = False,
) -> bool:
    ctx = get_current_tenant_context()

    if ctx is None:
        return True

    policy = ctx.policy
    severity = str(severity or "LOW").upper()

    if not policy.allow_autonomous_execution and ctx.autonomy_mode in {"FULL_AUTONOMY", "LOCKDOWN"}:
        dispatch_event(
            "TENANT_ACTION_BLOCKED",
            {
                "tenant_id": ctx.tenant_id,
                "action": action,
                "reason": "autonomous_execution_disabled_for_tenant",
            },
            source="tenant_execution_context",
        )
        return False

    if destructive and not policy.allow_destructive_actions:
        dispatch_event(
            "TENANT_ACTION_BLOCKED",
            {
                "tenant_id": ctx.tenant_id,
                "action": action,
                "reason": "destructive_actions_disabled_for_tenant",
            },
            source="tenant_execution_context",
        )
        return False

    if identity_action and not policy.allow_identity_actions:
        dispatch_event(
            "TENANT_ACTION_BLOCKED",
            {
                "tenant_id": ctx.tenant_id,
                "action": action,
                "reason": "identity_actions_disabled_for_tenant",
            },
            source="tenant_execution_context",
        )
        return False

    if endpoint_action and not policy.allow_endpoint_actions:
        dispatch_event(
            "TENANT_ACTION_BLOCKED",
            {
                "tenant_id": ctx.tenant_id,
                "action": action,
                "reason": "endpoint_actions_disabled_for_tenant",
            },
            source="tenant_execution_context",
        )
        return False

    if severity in policy.required_approval_severity and ctx.autonomy_mode not in {"LOCKDOWN"}:
        dispatch_event(
            "TENANT_ACTION_REQUIRES_APPROVAL",
            {
                "tenant_id": ctx.tenant_id,
                "action": action,
                "severity": severity,
                "autonomy_mode": ctx.autonomy_mode,
            },
            source="tenant_execution_context",
        )
        return False

    return True


def tenant_scoped_payload(
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    enriched = enrich_with_tenant_context(payload or {})
    enriched["event_type"] = event_type
    return enriched


def serialize_tenant_context(context: TenantExecutionContext) -> str:
    return json.dumps(context.as_dict(), default=str)


def deserialize_tenant_context(raw: str) -> TenantExecutionContext:
    data = json.loads(raw)

    policy_data = data.get("policy") or {}
    policy = TenantExecutionPolicy(**policy_data)

    return TenantExecutionContext(
        tenant_id=data["tenant_id"],
        tenant_name=data.get("tenant_name"),
        execution_id=data.get("execution_id") or str(uuid.uuid4()),
        correlation_id=data.get("correlation_id") or str(uuid.uuid4()),
        user_id=data.get("user_id"),
        actor=data.get("actor") or "system",
        autonomy_mode=data.get("autonomy_mode") or policy.default_autonomy_mode,
        case_id=data.get("case_id"),
        graph_id=data.get("graph_id"),
        evidence_ids=data.get("evidence_ids") or [],
        policy=policy,
        created_at_ms=data.get("created_at_ms") or int(time.time() * 1000),
        metadata=data.get("metadata") or {},
    )