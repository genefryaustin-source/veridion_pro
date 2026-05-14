"""
core/runtime/runtime_policy_manager.py

Runtime Policy Manager.

Purpose:
- enforce runtime architecture rules
- detect runtime drift
- enforce service boundaries
- validate tenant isolation
- detect unsafe DB usage patterns
- enforce UI/runtime separation
- track architecture violations
- govern runtime execution behavior

This becomes:
the runtime governance enforcement layer.
"""

from __future__ import annotations

import inspect
import sqlite3
import threading
import time
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# POLICY CONSTANTS
# ============================================================

POLICY_OK = "OK"
POLICY_WARNING = "WARNING"
POLICY_VIOLATION = "VIOLATION"
POLICY_QUARANTINED = "QUARANTINED"

MODE_PERMISSIVE = "PERMISSIVE"
MODE_STRICT = "STRICT"
MODE_GOVCLOUD = "GOVCLOUD"

DEFAULT_TENANT = "default"


# ============================================================
# HELPERS
# ============================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


# ============================================================
# POLICY EVENT
# ============================================================

@dataclass
class RuntimePolicyEvent:
    event_id: str
    event_type: str
    severity: str
    message: str

    source_service: Optional[str] = None

    tenant_id: str = DEFAULT_TENANT

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# POLICY MANAGER
# ============================================================

class RuntimePolicyManager:
    """
    Runtime architecture enforcement layer.

    Enforces:
    - explicit service ownership
    - registry-managed services
    - UI/runtime separation
    - DB thread safety
    - deterministic orchestration
    - tenant isolation
    """

    def __init__(
        self,
        *,
        registry: Any,
        lifecycle: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        policy_mode: str = MODE_PERMISSIVE,
    ) -> None:

        self.registry = registry
        self.lifecycle = lifecycle
        self.storage = storage
        self.event_bus = event_bus

        self.policy_mode = (
            policy_mode
        )

        self._lock = threading.RLock()

        self._events: List[
            RuntimePolicyEvent
        ] = []

        self._quarantined_services = set()

    # ========================================================
    # EVENT RECORDING
    # ========================================================

    def _record(
        self,
        *,
        event_type: str,
        severity: str,
        message: str,
        source_service: Optional[str] = None,
        tenant_id: str = DEFAULT_TENANT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimePolicyEvent:

        event = RuntimePolicyEvent(
            event_id=f"RPE-{uuid.uuid4().hex[:12].upper()}",
            event_type=event_type,
            severity=severity,
            message=message,
            source_service=source_service,
            tenant_id=tenant_id,
            metadata=metadata or {},
        )

        with self._lock:
            self._events.append(event)

        self._emit(
            event_type,
            payload=event.to_dict(),
        )

        return event

    # ========================================================
    # SERVICE GOVERNANCE
    # ========================================================

    def validate_service_registration(
        self,
        service_name: str,
    ) -> Dict[str, Any]:

        record = self.registry.get_record(
            service_name
        )

        if record is None:

            self._record(
                event_type="UNREGISTERED_SERVICE",
                severity=POLICY_VIOLATION,
                message=(
                    f"Service '{service_name}' "
                    "is not registry managed."
                ),
                source_service=service_name,
            )

            return {
                "ok": False,
                "reason": "service_not_registered",
            }

        return {
            "ok": True,
            "service_name": service_name,
        }

    def detect_orphaned_services(
        self,
    ) -> Dict[str, Any]:

        orphaned = []

        services = self.registry.list_services()

        for record in services:

            if (
                self.lifecycle is not None
                and record.service_name
                not in self.lifecycle._records
            ):

                orphaned.append(
                    record.service_name
                )

                self._record(
                    event_type="ORPHANED_SERVICE",
                    severity=POLICY_WARNING,
                    message=(
                        f"Service '{record.service_name}' "
                        "is not lifecycle managed."
                    ),
                    source_service=record.service_name,
                )

        return {
            "ok": len(orphaned) == 0,
            "orphaned_services": orphaned,
        }

    # ========================================================
    # STORAGE GOVERNANCE
    # ========================================================

    def validate_storage_mutation(
        self,
        *,
        actor: str,
        attribute: str,
    ) -> Dict[str, Any]:

        dangerous = {
            "execution_queue",
            "execution_router",
            "worker_orchestrator",
            "execution_graph_engine",
            "graph_replay_engine",
            "lease_watchdog",
            "runtime_service_registry",
            "runtime_lifecycle_manager",
        }

        if attribute not in dangerous:
            return {"ok": True}

        self._record(
            event_type="DIRECT_RUNTIME_MUTATION",
            severity=POLICY_WARNING,
            message=(
                f"Direct storage mutation detected: "
                f"{attribute}"
            ),
            source_service=actor,
            metadata={
                "attribute": attribute,
            },
        )

        if self.policy_mode == MODE_STRICT:

            return {
                "ok": False,
                "reason": (
                    "direct_runtime_mutation"
                ),
            }

        return {"ok": True}

    # ========================================================
    # SQLITE SAFETY
    # ========================================================

    def validate_sqlite_connection(
        self,
        *,
        conn: Any,
        source_service: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not isinstance(
            conn,
            sqlite3.Connection,
        ):
            return {"ok": True}

        try:

            conn.execute(
                "SELECT 1"
            ).fetchone()

        except sqlite3.ProgrammingError as exc:

            self._record(
                event_type="SQLITE_THREAD_VIOLATION",
                severity=POLICY_VIOLATION,
                message=str(exc),
                source_service=source_service,
            )

            return {
                "ok": False,
                "reason": (
                    "sqlite_thread_violation"
                ),
                "error": str(exc),
            }

        return {"ok": True}

    def detect_persistent_connections(
        self,
        service: Any,
        *,
        source_service: str,
    ) -> Dict[str, Any]:

        dangerous_attrs = []

        for attr in dir(service):

            if attr.startswith("__"):
                continue

            try:
                value = getattr(
                    service,
                    attr,
                )

                if isinstance(
                    value,
                    sqlite3.Connection,
                ):
                    dangerous_attrs.append(
                        attr
                    )

            except Exception:
                continue

        if dangerous_attrs:

            self._record(
                event_type="PERSISTENT_SQLITE_CONNECTION",
                severity=POLICY_VIOLATION,
                message=(
                    "Persistent sqlite connection "
                    "detected."
                ),
                source_service=source_service,
                metadata={
                    "attributes":
                        dangerous_attrs,
                },
            )

            return {
                "ok": False,
                "attributes":
                    dangerous_attrs,
            }

        return {"ok": True}

    # ========================================================
    # SESSION STATE GOVERNANCE
    # ========================================================

    def validate_session_state_usage(
        self,
        *,
        key: str,
        source_service: str,
    ) -> Dict[str, Any]:

        dangerous = {
            "execution_queue",
            "worker_state",
            "graph_runtime",
            "mission_runtime",
            "lease_runtime",
            "distributed_runtime",
        }

        if key not in dangerous:
            return {"ok": True}

        self._record(
            event_type="SESSION_STATE_RUNTIME_USAGE",
            severity=POLICY_WARNING,
            message=(
                "Runtime state stored inside "
                "session_state."
            ),
            source_service=source_service,
            metadata={
                "session_key": key,
            },
        )

        if self.policy_mode == MODE_STRICT:

            return {
                "ok": False,
                "reason":
                    "runtime_state_in_session",
            }

        return {"ok": True}

    # ========================================================
    # TENANT GOVERNANCE
    # ========================================================

    def validate_tenant_access(
        self,
        *,
        source_tenant: str,
        target_tenant: str,
        source_service: str,
    ) -> Dict[str, Any]:

        if (
            source_tenant
            == target_tenant
        ):
            return {"ok": True}

        self._record(
            event_type="CROSS_TENANT_ACCESS",
            severity=POLICY_VIOLATION,
            message=(
                "Cross-tenant runtime access "
                "detected."
            ),
            source_service=source_service,
            metadata={
                "source_tenant":
                    source_tenant,

                "target_tenant":
                    target_tenant,
            },
        )

        if self.policy_mode in {
            MODE_STRICT,
            MODE_GOVCLOUD,
        }:

            return {
                "ok": False,
                "reason":
                    "cross_tenant_access",
            }

        return {"ok": True}

    # ========================================================
    # DETERMINISM GOVERNANCE
    # ========================================================

    def validate_graph_determinism(
        self,
        *,
        graph_payload: Dict[str, Any],
        source_service: str,
    ) -> Dict[str, Any]:

        violations = []

        dangerous_keys = {
            "random_seed",
            "runtime_random",
            "implicit_context",
            "global_context",
        }

        for key in graph_payload.keys():

            if key in dangerous_keys:
                violations.append(key)

        if violations:

            self._record(
                event_type="NONDETERMINISTIC_GRAPH",
                severity=POLICY_WARNING,
                message=(
                    "Potential nondeterministic "
                    "graph payload detected."
                ),
                source_service=source_service,
                metadata={
                    "violations":
                        violations,
                },
            )

        return {
            "ok": len(violations) == 0,
            "violations": violations,
        }

    # ========================================================
    # EVENT GOVERNANCE
    # ========================================================

    def validate_direct_mutation(
        self,
        *,
        source_service: str,
        target_service: str,
        operation: str,
    ) -> Dict[str, Any]:

        dangerous_ops = {
            "append",
            "pop",
            "clear",
            "extend",
            "remove",
            "update",
        }

        if operation not in dangerous_ops:
            return {"ok": True}

        self._record(
            event_type="DIRECT_SHARED_MUTATION",
            severity=POLICY_WARNING,
            message=(
                "Direct shared state mutation "
                "detected."
            ),
            source_service=source_service,
            metadata={
                "target_service":
                    target_service,

                "operation":
                    operation,
            },
        )

        return {"ok": True}

    # ========================================================
    # QUARANTINE
    # ========================================================

    def quarantine_service(
        self,
        service_name: str,
        *,
        reason: str,
    ) -> Dict[str, Any]:

        self._quarantined_services.add(
            service_name
        )

        try:

            self.registry.quarantine(
                service_name,
                reason=reason,
            )

        except Exception:
            pass

        self._record(
            event_type="SERVICE_QUARANTINED",
            severity=POLICY_QUARANTINED,
            message=reason,
            source_service=service_name,
        )

        return {
            "ok": True,
            "service_name":
                service_name,
            "reason":
                reason,
        }

    def clear_quarantine(
        self,
        service_name: str,
    ) -> Dict[str, Any]:

        self._quarantined_services.discard(
            service_name
        )

        try:

            self.registry.clear_quarantine(
                service_name,
            )

        except Exception:
            pass

        self._record(
            event_type="SERVICE_RESTORED",
            severity=POLICY_OK,
            message=(
                "Service restored."
            ),
            source_service=service_name,
        )

        return {
            "ok": True,
            "service_name":
                service_name,
        }

    # ========================================================
    # HEALTH
    # ========================================================

    def audit_runtime(
        self,
    ) -> Dict[str, Any]:

        orphaned = (
            self.detect_orphaned_services()
        )

        services = (
            self.registry.list_services()
        )

        persistent_conn_violations = []

        for record in services:

            result = (
                self.detect_persistent_connections(
                    record.service,
                    source_service=(
                        record.service_name
                    ),
                )
            )

            if not result.get("ok"):
                persistent_conn_violations.append(
                    record.service_name
                )

        return {

            "ok":
                (
                    orphaned.get("ok")
                    and len(
                        persistent_conn_violations
                    ) == 0
                ),

            "orphaned_services":
                orphaned.get(
                    "orphaned_services",
                    [],
                ),

            "persistent_connection_violations":
                persistent_conn_violations,

            "quarantined_services":
                list(
                    self._quarantined_services
                ),

            "event_count":
                len(self._events),
        }

    # ========================================================
    # READS
    # ========================================================

    def list_events(
        self,
        *,
        severity: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:

        with self._lock:

            events = list(self._events)

        if severity:

            events = [
                e for e in events
                if e.severity == severity
            ]

        events = sorted(
            events,
            key=lambda e: e.created_at_ms,
            reverse=True,
        )

        return [
            e.to_dict()
            for e in events[:limit]
        ]

    def policy_status(
        self,
    ) -> Dict[str, Any]:

        return {

            "policy_mode":
                self.policy_mode,

            "quarantined_services":
                list(
                    self._quarantined_services
                ),

            "event_count":
                len(self._events),

            "violation_count":
                len([
                    e for e in self._events
                    if e.severity
                    == POLICY_VIOLATION
                ]),

            "warning_count":
                len([
                    e for e in self._events
                    if e.severity
                    == POLICY_WARNING
                ]),
        }

    # ========================================================
    # EVENTS
    # ========================================================

    def _emit(
        self,
        event_type: str,
        *,
        payload: Dict[str, Any],
    ) -> None:

        if self.event_bus is None:
            return

        try:

            self.event_bus.publish(
                event_type=event_type,
                source="runtime_policy_manager",
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


# ============================================================
# SINGLETON ACCESSOR
# ============================================================

_DEFAULT_RUNTIME_POLICY_MANAGER = None


def get_runtime_policy_manager(
    *,
    registry: Any,
    lifecycle: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    policy_mode: str = MODE_PERMISSIVE,
    reset: bool = False,
) -> RuntimePolicyManager:

    global _DEFAULT_RUNTIME_POLICY_MANAGER

    if (
        reset
        or _DEFAULT_RUNTIME_POLICY_MANAGER
        is None
    ):

        _DEFAULT_RUNTIME_POLICY_MANAGER = (
            RuntimePolicyManager(
                registry=registry,
                lifecycle=lifecycle,
                storage=storage,
                event_bus=event_bus,
                policy_mode=policy_mode,
            )
        )

    return _DEFAULT_RUNTIME_POLICY_MANAGER