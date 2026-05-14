"""
core/connectors/connector_registry.py

Connector Registry for Veridion Pro / CUI GovCloud App.

Purpose:
- Central connector discovery + routing
- Action → connector resolution
- Multi-connector fallback support
- Capability-aware orchestration
- Tenant-aware connector selection
- Governance-aware execution routing

Used by:
- autonomous_response_engine.py
- action_plugins/
- rollback_orchestrator.py
- governance systems
- execution_verifier.py
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from core.connectors.base_connector import (
    BaseConnector,
)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_TENANT = "default"

ACTION_DISABLE_USER = "DISABLE_USER"
ACTION_REVOKE_SESSIONS = "REVOKE_SESSIONS"
ACTION_QUARANTINE_EMAIL = "QUARANTINE_EMAIL"
ACTION_ISOLATE_ENDPOINT = "ISOLATE_ENDPOINT"
ACTION_DISABLE_MAILBOX = "DISABLE_MAILBOX"
ACTION_DELETE_EMAIL = "DELETE_EMAIL"
ACTION_SEAL_EVIDENCE = "SEAL_EVIDENCE"
ACTION_RESTORE_USER = "RESTORE_USER"
ACTION_UNISOLATE_ENDPOINT = "UNISOLATE_ENDPOINT"

SEVERITY_INFO = "INFO"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


# =============================================================================
# Registry Models
# =============================================================================

@dataclass
class ConnectorRegistration:
    connector: BaseConnector
    connector_id: str
    tenant_id: str

    actions: Set[str] = field(default_factory=set)
    priority: int = 100
    enabled: bool = True

    tags: Set[str] = field(default_factory=set)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def supports(self, action: str) -> bool:
        action = str(action or "").upper()

        if action in self.actions:
            return True

        return self.connector.supports(action)


@dataclass
class ConnectorResolution:
    ok: bool
    action: str

    connector: Optional[BaseConnector] = None
    connector_id: Optional[str] = None

    tenant_id: str = DEFAULT_TENANT

    message: str = ""
    reason: str = ""

    candidates: List[str] = field(default_factory=list)

    requires_approval: bool = True
    supports_rollback: bool = False
    destructive: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Connector Registry
# =============================================================================

class ConnectorRegistry:

    def __init__(
        self,
        *,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:

        self.storage = storage
        self.event_bus = event_bus

        self._lock = threading.RLock()

        self._registrations: Dict[
            str,
            Dict[str, ConnectorRegistration]
        ] = {}

        self._action_index: Dict[
            str,
            Set[str]
        ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        connector: BaseConnector,
        *,
        actions: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
        priority: int = 100,
        enabled: bool = True,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConnectorRegistration:

        tenant_id = tenant_id or connector.tenant_id or DEFAULT_TENANT

        connector_id = connector.connector_id

        action_set = {
            str(a).upper()
            for a in (actions or [])
        }

        if not action_set:
            action_set = set(
                connector.capabilities().keys()
            )

        registration = ConnectorRegistration(
            connector=connector,
            connector_id=connector_id,
            tenant_id=tenant_id,
            actions=action_set,
            priority=priority,
            enabled=enabled,
            tags=set(tags or []),
            metadata=metadata or {},
        )

        with self._lock:

            tenant_map = self._registrations.setdefault(
                tenant_id,
                {}
            )

            tenant_map[connector_id] = registration

            for action in action_set:

                action = action.upper()

                connector_ids = self._action_index.setdefault(
                    action,
                    set(),
                )

                connector_ids.add(
                    connector_id
                )

        self._emit(
            "CONNECTOR_REGISTERED",
            {
                "connector_id": connector_id,
                "tenant_id": tenant_id,
                "actions": sorted(action_set),
                "priority": priority,
            },
        )

        return registration

    def unregister(
        self,
        connector_id: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> bool:

        removed = False

        with self._lock:

            tenant_map = self._registrations.get(
                tenant_id,
                {}
            )

            registration = tenant_map.pop(
                connector_id,
                None,
            )

            if registration:

                removed = True

                for action in registration.actions:

                    action_ids = self._action_index.get(
                        action,
                        set(),
                    )

                    action_ids.discard(
                        connector_id
                    )

        if removed:

            self._emit(
                "CONNECTOR_UNREGISTERED",
                {
                    "connector_id": connector_id,
                    "tenant_id": tenant_id,
                },
            )

        return removed

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def resolve(
        self,
        *,
        action: str,
        tenant_id: str = DEFAULT_TENANT,
        preferred_connector: Optional[str] = None,
        required_tags: Optional[List[str]] = None,
    ) -> ConnectorResolution:

        action = str(action or "").upper()

        candidates = self.find_candidates(
            action=action,
            tenant_id=tenant_id,
            required_tags=required_tags,
        )

        if preferred_connector:

            preferred_connector = str(
                preferred_connector
            )

            candidates = [
                r for r in candidates
                if r.connector_id == preferred_connector
            ]

        if not candidates:

            return ConnectorResolution(
                ok=False,
                action=action,
                tenant_id=tenant_id,
                message=f"No connector available for action {action}",
                reason="NO_CONNECTOR",
            )

        candidates = sorted(
            candidates,
            key=lambda r: r.priority,
        )

        selected = candidates[0]

        connector = selected.connector

        return ConnectorResolution(
            ok=True,
            action=action,
            connector=connector,
            connector_id=selected.connector_id,
            tenant_id=tenant_id,
            message=f"Resolved {action} to {selected.connector_id}",
            candidates=[
                r.connector_id
                for r in candidates
            ],
            requires_approval=connector.requires_approval(
                action
            ),
            supports_rollback=connector.supports_rollback(
                action
            ),
            destructive=connector.is_destructive(
                action
            ),
            metadata={
                "priority": selected.priority,
                "tags": sorted(selected.tags),
            },
        )

    def find_candidates(
        self,
        *,
        action: str,
        tenant_id: str = DEFAULT_TENANT,
        required_tags: Optional[List[str]] = None,
    ) -> List[ConnectorRegistration]:

        action = str(action or "").upper()

        required_tags = {
            str(t).lower()
            for t in (required_tags or [])
        }

        results: List[
            ConnectorRegistration
        ] = []

        with self._lock:

            tenant_map = self._registrations.get(
                tenant_id,
                {}
            )

            for registration in tenant_map.values():

                if not registration.enabled:
                    continue

                if not registration.supports(
                    action
                ):
                    continue

                if required_tags:

                    reg_tags = {
                        t.lower()
                        for t in registration.tags
                    }

                    if not required_tags.issubset(
                        reg_tags
                    ):
                        continue

                results.append(
                    registration
                )

        return results

    def get_connector(
        self,
        connector_id: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Optional[BaseConnector]:

        with self._lock:

            tenant_map = self._registrations.get(
                tenant_id,
                {}
            )

            registration = tenant_map.get(
                connector_id
            )

            if not registration:
                return None

            return registration.connector

    # ------------------------------------------------------------------
    # Execution Helpers
    # ------------------------------------------------------------------

    def execute(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str = "connector_registry",
        tenant_id: str = DEFAULT_TENANT,
        preferred_connector: Optional[str] = None,
    ) -> Dict[str, Any]:

        resolution = self.resolve(
            action=action,
            tenant_id=tenant_id,
            preferred_connector=preferred_connector,
        )

        if not resolution.ok:

            return {
                "ok": False,
                "status": "NO_CONNECTOR",
                "message": resolution.message,
                "resolution": resolution,
            }

        connector = resolution.connector

        if connector is None:

            return {
                "ok": False,
                "status": "INVALID_CONNECTOR",
                "message": "Connector missing.",
                "resolution": resolution,
            }

        result = connector.execute(
            action=action,
            payload=payload,
            actor=actor,
        )

        self._emit(
            "CONNECTOR_REGISTRY_EXECUTED",
            {
                "action": action,
                "tenant_id": tenant_id,
                "connector_id": resolution.connector_id,
                "execution_result": result.to_dict(),
            },
        )

        return {
            "ok": result.ok,
            "status": result.status,
            "message": result.message,
            "connector_id": resolution.connector_id,
            "result": result,
            "resolution": resolution,
        }

    def rollback(
        self,
        *,
        connector_id: str,
        action: str,
        payload: Dict[str, Any],
        actor: str = "connector_registry",
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:

        connector = self.get_connector(
            connector_id,
            tenant_id=tenant_id,
        )

        if connector is None:

            return {
                "ok": False,
                "status": "CONNECTOR_NOT_FOUND",
                "message": f"Connector {connector_id} not found.",
            }

        result = connector.rollback(
            action=action,
            payload=payload,
            actor=actor,
        )

        self._emit(
            "CONNECTOR_REGISTRY_ROLLBACK",
            {
                "action": action,
                "tenant_id": tenant_id,
                "connector_id": connector_id,
                "rollback_result": result.to_dict(),
            },
        )

        return {
            "ok": result.ok,
            "status": result.status,
            "message": result.message,
            "connector_id": connector_id,
            "result": result,
        }

    # ------------------------------------------------------------------
    # Registry Views
    # ------------------------------------------------------------------

    def list_connectors(
        self,
        *,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        rows: List[
            Dict[str, Any]
        ] = []

        with self._lock:

            tenant_ids = (
                [tenant_id]
                if tenant_id
                else list(
                    self._registrations.keys()
                )
            )

            for tid in tenant_ids:

                tenant_map = self._registrations.get(
                    tid,
                    {}
                )

                for reg in tenant_map.values():

                    rows.append(
                        {
                            "tenant_id": tid,
                            "connector_id": reg.connector_id,
                            "connector_name": reg.connector.connector_name,
                            "vendor": reg.connector.vendor,
                            "priority": reg.priority,
                            "enabled": reg.enabled,
                            "actions": sorted(
                                reg.actions
                            ),
                            "tags": sorted(
                                reg.tags
                            ),
                        }
                    )

        return rows

    def capabilities_matrix(
        self,
        *,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        matrix: Dict[
            str,
            List[str]
        ] = {}

        connectors = self.list_connectors(
            tenant_id=tenant_id
        )

        for row in connectors:

            for action in row["actions"]:

                action = str(action).upper()

                ids = matrix.setdefault(
                    action,
                    [],
                )

                ids.append(
                    row["connector_id"]
                )

        return matrix

    # ------------------------------------------------------------------
    # Event Helpers
    # ------------------------------------------------------------------

    def _emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
        severity: str = SEVERITY_INFO,
    ) -> None:

        if self.event_bus is None:
            return

        try:

            self.event_bus.publish(
                event_type=event_type,
                tenant_id=payload.get(
                    "tenant_id",
                    DEFAULT_TENANT,
                ),
                source="connector_registry",
                severity=severity,
                payload=payload,
            )

        except TypeError:

            try:

                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=payload.get(
                        "tenant_id",
                        DEFAULT_TENANT,
                    ),
                    source="connector_registry",
                )

            except Exception:
                pass

        except Exception:
            pass

    def stats(self) -> Dict[str, Any]:

        connectors = []

        total = 0
        enabled = 0
        degraded = 0
        simulation = 0

        quarantined = 0
        failed = 0
        healthy = 0

        registry = getattr(
            self,
            "_connectors",
            {},
        )

        for connector_id, connector in registry.items():

            total += 1

            connector_healthy = bool(
                getattr(
                    connector,
                    "healthy",
                    True,
                )
            )

            simulation_mode = bool(
                getattr(
                    connector,
                    "simulation_mode",
                    False,
                )
            )

            quarantined_state = bool(
                getattr(
                    connector,
                    "quarantined",
                    False,
                )
            )

            failed_state = bool(
                getattr(
                    connector,
                    "failed",
                    False,
                )
            )

            if connector_healthy:
                enabled += 1
                healthy += 1
            else:
                degraded += 1

            if simulation_mode:
                simulation += 1

            if quarantined_state:
                quarantined += 1

            if failed_state:
                failed += 1

            connectors.append({

                "connector_id": connector_id,

                "healthy": connector_healthy,

                "simulation_mode": simulation_mode,

                "quarantined": quarantined_state,

                "failed": failed_state,

                "connector_type": getattr(
                    connector,
                    "connector_type",
                    None,
                ),

                "tenant_id": getattr(
                    connector,
                    "tenant_id",
                    None,
                ),
            })

        return {

            "total": total,

            "enabled": enabled,

            "healthy": healthy,

            "degraded": degraded,

            "simulation": simulation,

            "quarantined": quarantined,

            "failed": failed,

            "connectors": connectors,
        }


# =============================================================================
# Global Registry
# =============================================================================

_DEFAULT_REGISTRY: Optional[
    ConnectorRegistry
] = None


def get_connector_registry(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
) -> ConnectorRegistry:

    global _DEFAULT_REGISTRY

    if reset or _DEFAULT_REGISTRY is None:

        _DEFAULT_REGISTRY = ConnectorRegistry(
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_REGISTRY


# =============================================================================
# Convenience Helpers
# =============================================================================

def resolve_connector(
    *,
    action: str,
    tenant_id: str = DEFAULT_TENANT,
    preferred_connector: Optional[str] = None,
) -> ConnectorResolution:

    registry = get_connector_registry()

    return registry.resolve(
        action=action,
        tenant_id=tenant_id,
        preferred_connector=preferred_connector,
    )


def execute_connector_action(
    *,
    action: str,
    payload: Dict[str, Any],
    actor: str = "connector_registry",
    tenant_id: str = DEFAULT_TENANT,
    preferred_connector: Optional[str] = None,
) -> Dict[str, Any]:

    registry = get_connector_registry()

    return registry.execute(
        action=action,
        payload=payload,
        actor=actor,
        tenant_id=tenant_id,
        preferred_connector=preferred_connector,
    )