"""
core/agents/agent_registry.py

Centralized registry for autonomous SOC agents.

Provides:
- agent discovery
- runtime registration
- enable/disable state
- tenant policy controls
- capability lookup
- governance-aware filtering
- health telemetry
- optimizer hooks
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type


from core.agents.base_agent import BaseAgent

from core.agents.containment_agent import ContainmentAgent
from core.agents.governance_agent import GovernanceAgent
from core.agents.verification_agent import VerificationAgent
from core.agents.escalation_agent import EscalationAgent


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


# ============================================================
# REGISTRY RECORD
# ============================================================

@dataclass
class AgentRegistryRecord:

    agent_name: str

    agent_class: Type[BaseAgent]

    enabled: bool = True

    healthy: bool = True

    tenant_enabled: Dict[str, bool] = field(default_factory=dict)

    capabilities: List[str] = field(default_factory=list)

    execution_scope: List[str] = field(default_factory=list)

    required_permissions: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    last_health_check_ms: Optional[int] = None

    last_error: Optional[str] = None


# ============================================================
# AGENT REGISTRY
# ============================================================

class AgentRegistry:

    """
    Centralized SOC autonomous agent registry.
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ):

        self.storage = storage

        self.config = config or {}

        self.registry: Dict[str, AgentRegistryRecord] = {}

        self.agent_instances: Dict[str, BaseAgent] = {}

        self.initialize_builtin_agents()

    # ========================================================
    # EVENTING
    # ========================================================

    def emit_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:

        dispatch_event(
            event_type=event_type,
            payload=payload or {},
            source="agent_registry",
        )

    # ========================================================
    # BUILTIN REGISTRATION
    # ========================================================

    def initialize_builtin_agents(self) -> None:

        self.register_agent(ContainmentAgent)

        self.register_agent(GovernanceAgent)

        self.register_agent(VerificationAgent)

        self.register_agent(EscalationAgent)

        self.emit_event(
            "BUILTIN_AGENTS_REGISTERED",
            {
                "count": len(self.registry),
            },
        )

    # ========================================================
    # REGISTRATION
    # ========================================================

    def register_agent(
        self,
        agent_class: Type[BaseAgent],
        enabled: bool = True,
    ) -> bool:

        try:

            agent_name = getattr(
                agent_class,
                "AGENT_NAME",
                agent_class.__name__,
            )

            execution_scope = list(
                getattr(
                    agent_class,
                    "EXECUTION_SCOPE",
                    [],
                )
            )

            required_permissions = list(
                getattr(
                    agent_class,
                    "REQUIRED_PERMISSIONS",
                    [],
                )
            )

            capabilities = list(set(
                execution_scope + required_permissions
            ))

            record = AgentRegistryRecord(
                agent_name=agent_name,
                agent_class=agent_class,
                enabled=enabled,
                capabilities=capabilities,
                execution_scope=execution_scope,
                required_permissions=required_permissions,
            )

            self.registry[agent_name] = record

            self.emit_event(
                "AGENT_REGISTERED",
                {
                    "agent_name": agent_name,
                    "enabled": enabled,
                },
            )

            return True

        except Exception:

            self.emit_event(
                "AGENT_REGISTRATION_FAILED",
                {
                    "agent_class": str(agent_class),
                    "error": traceback.format_exc(),
                },
            )

            return False

    def unregister_agent(
        self,
        agent_name: str,
    ) -> bool:

        if agent_name not in self.registry:
            return False

        try:

            del self.registry[agent_name]

            if agent_name in self.agent_instances:
                del self.agent_instances[agent_name]

            self.emit_event(
                "AGENT_UNREGISTERED",
                {
                    "agent_name": agent_name,
                },
            )

            return True

        except Exception:

            self.emit_event(
                "AGENT_UNREGISTER_FAILED",
                {
                    "agent_name": agent_name,
                    "error": traceback.format_exc(),
                },
            )

            return False

    # ========================================================
    # LOOKUP
    # ========================================================

    def get_agent_record(
        self,
        agent_name: str,
    ) -> Optional[AgentRegistryRecord]:

        return self.registry.get(agent_name)

    def get_agent(
        self,
        agent_name: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[BaseAgent]:

        record = self.registry.get(agent_name)

        if not record:
            return None

        if not record.enabled:
            return None

        if tenant_id:

            tenant_enabled = record.tenant_enabled.get(
                tenant_id,
                True,
            )

            if not tenant_enabled:
                return None

        if agent_name in self.agent_instances:
            return self.agent_instances[agent_name]

        try:

            instance = record.agent_class(
                storage=self.storage,
                config=self.config,
            )

            self.agent_instances[agent_name] = instance

            return instance

        except Exception:

            record.healthy = False
            record.last_error = traceback.format_exc()

            self.emit_event(
                "AGENT_INSTANTIATION_FAILED",
                {
                    "agent_name": agent_name,
                    "error": record.last_error,
                },
            )

            return None

    # ========================================================
    # ENABLE / DISABLE
    # ========================================================

    def enable_agent(
        self,
        agent_name: str,
    ) -> bool:

        record = self.registry.get(agent_name)

        if not record:
            return False

        record.enabled = True

        self.emit_event(
            "AGENT_ENABLED",
            {
                "agent_name": agent_name,
            },
        )

        return True

    def disable_agent(
        self,
        agent_name: str,
    ) -> bool:

        record = self.registry.get(agent_name)

        if not record:
            return False

        record.enabled = False

        self.emit_event(
            "AGENT_DISABLED",
            {
                "agent_name": agent_name,
            },
        )

        return True

    # ========================================================
    # TENANT POLICY
    # ========================================================

    def enable_agent_for_tenant(
        self,
        agent_name: str,
        tenant_id: str,
    ) -> bool:

        record = self.registry.get(agent_name)

        if not record:
            return False

        record.tenant_enabled[tenant_id] = True

        self.emit_event(
            "TENANT_AGENT_ENABLED",
            {
                "agent_name": agent_name,
                "tenant_id": tenant_id,
            },
        )

        return True

    def disable_agent_for_tenant(
        self,
        agent_name: str,
        tenant_id: str,
    ) -> bool:

        record = self.registry.get(agent_name)

        if not record:
            return False

        record.tenant_enabled[tenant_id] = False

        self.emit_event(
            "TENANT_AGENT_DISABLED",
            {
                "agent_name": agent_name,
                "tenant_id": tenant_id,
            },
        )

        return True

    def is_agent_enabled_for_tenant(
        self,
        agent_name: str,
        tenant_id: str,
    ) -> bool:

        record = self.registry.get(agent_name)

        if not record:
            return False

        if not record.enabled:
            return False

        return record.tenant_enabled.get(
            tenant_id,
            True,
        )

    # ========================================================
    # CAPABILITY LOOKUP
    # ========================================================

    def get_agents_by_capability(
        self,
        capability: str,
        tenant_id: Optional[str] = None,
    ) -> List[str]:

        matches = []

        for name, record in self.registry.items():

            if not record.enabled:
                continue

            if tenant_id:

                if not self.is_agent_enabled_for_tenant(
                    name,
                    tenant_id,
                ):
                    continue

            if capability in record.capabilities:
                matches.append(name)

        return matches

    def get_agent_for_action(
        self,
        action: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[str]:

        for name, record in self.registry.items():

            if not record.enabled:
                continue

            if tenant_id:

                if not self.is_agent_enabled_for_tenant(
                    name,
                    tenant_id,
                ):
                    continue

            if action in record.execution_scope:
                return name

        return None

    # ========================================================
    # HEALTH
    # ========================================================

    def perform_health_check(
        self,
        agent_name: str,
    ) -> bool:

        record = self.registry.get(agent_name)

        if not record:
            return False

        try:

            agent = self.get_agent(agent_name)

            if not agent:
                record.healthy = False
                return False

            record.healthy = True

            record.last_health_check_ms = int(
                time.time() * 1000
            )

            self.emit_event(
                "AGENT_HEALTHY",
                {
                    "agent_name": agent_name,
                },
            )

            return True

        except Exception:

            record.healthy = False

            record.last_error = traceback.format_exc()

            self.emit_event(
                "AGENT_UNHEALTHY",
                {
                    "agent_name": agent_name,
                    "error": record.last_error,
                },
            )

            return False

    def perform_global_health_check(self) -> Dict[str, bool]:

        results = {}

        for agent_name in self.registry.keys():
            results[agent_name] = self.perform_health_check(
                agent_name
            )

        return results

    # ========================================================
    # TELEMETRY
    # ========================================================

    def get_registry_summary(self) -> Dict[str, Any]:

        enabled = 0
        healthy = 0

        agents = []

        for name, record in self.registry.items():

            if record.enabled:
                enabled += 1

            if record.healthy:
                healthy += 1

            agents.append({
                "agent_name": name,
                "enabled": record.enabled,
                "healthy": record.healthy,
                "capabilities": record.capabilities,
                "execution_scope": record.execution_scope,
                "required_permissions": record.required_permissions,
                "last_health_check_ms": record.last_health_check_ms,
                "last_error": record.last_error,
            })

        return {
            "total_agents": len(self.registry),
            "enabled_agents": enabled,
            "healthy_agents": healthy,
            "agents": agents,
        }

    # ========================================================
    # OPTIMIZER HOOKS
    # ========================================================

    def record_agent_feedback(
        self,
        agent_name: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.emit_event(
            "AGENT_OPTIMIZER_FEEDBACK",
            {
                "agent_name": agent_name,
                "success": success,
                "metadata": metadata or {},
            },
        )

    # ========================================================
    # FUTURE AGENT DISCOVERY
    # ========================================================

    def discover_plugin_agents(self) -> List[str]:
        """
        Future:
        - dynamic plugin loading
        - marketplace agents
        - tenant custom agents
        - remote autonomous agents
        """

        return []