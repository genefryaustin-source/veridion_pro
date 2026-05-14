"""
core/runtime/runtime_service_registry.py

Central Runtime Service Registry.

Purpose:
- eliminate hidden runtime globals
- controlled service ownership
- runtime dependency boundaries
- service discovery
- lifecycle tracking
- health/state tracking
- tenant-safe runtime resolution
- future federation support

Architectural Goal:
Services communicate through:
- explicit APIs
- event bus
- registry resolution

NOT:
- shared mutable state
- implicit globals
- singleton sprawl
"""

from __future__ import annotations

import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


SERVICE_UNKNOWN = "UNKNOWN"
SERVICE_INITIALIZING = "INITIALIZING"
SERVICE_READY = "READY"
SERVICE_DEGRADED = "DEGRADED"
SERVICE_UNAVAILABLE = "UNAVAILABLE"
SERVICE_QUARANTINED = "QUARANTINED"
SERVICE_STOPPED = "STOPPED"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeServiceRecord:
    service_name: str
    service: Any

    owner: str = "system"

    version: str = "1.0"

    description: Optional[str] = None

    tenant_id: str = DEFAULT_TENANT

    status: str = SERVICE_READY

    tags: List[str] = field(default_factory=list)

    dependencies: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=_now_ms)

    updated_at_ms: int = field(default_factory=_now_ms)

    last_heartbeat_ms: Optional[int] = None

    quarantine_reason: Optional[str] = None

    error_count: int = 0

    warning_count: int = 0

    health_score: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)

        # Avoid serializing giant runtime objects
        data["service"] = str(type(self.service))

        return data


class RuntimeServiceRegistry:
    """
    Controlled runtime service boundary.

    This replaces:
    - implicit globals
    - uncontrolled storage mutation
    - hidden singleton assumptions

    with:
    - explicit runtime registration
    - service ownership
    - controlled resolution
    - lifecycle awareness
    """

    def __init__(
        self,
        *,
        event_bus: Any = None,
    ) -> None:

        self.event_bus = event_bus

        self._lock = threading.RLock()

        self._services: Dict[str, RuntimeServiceRecord] = {}

        self._tenant_services: Dict[
            str,
            Dict[str, RuntimeServiceRecord]
        ] = {}

    # ========================================================
    # REGISTRATION
    # ========================================================

    def register(
        self,
        service_name: str,
        service: Any,
        *,
        owner: str = "system",
        version: str = "1.0",
        description: Optional[str] = None,
        tenant_id: str = DEFAULT_TENANT,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = True,
    ) -> RuntimeServiceRecord:

        if not service_name:
            raise ValueError(
                "service_name is required."
            )

        with self._lock:

            if (
                not overwrite
                and service_name in self._services
            ):
                raise ValueError(
                    f"Service already registered: {service_name}"
                )

            record = RuntimeServiceRecord(
                service_name=service_name,
                service=service,
                owner=owner,
                version=version,
                description=description,
                tenant_id=tenant_id or DEFAULT_TENANT,
                tags=tags or [],
                dependencies=dependencies or [],
                metadata=metadata or {},
                status=SERVICE_READY,
            )

            self._services[
                service_name
            ] = record

            tenant_bucket = (
                self._tenant_services
                .setdefault(
                    tenant_id or DEFAULT_TENANT,
                    {},
                )
            )

            tenant_bucket[
                service_name
            ] = record

            self._emit(
                "RUNTIME_SERVICE_REGISTERED",
                payload={
                    "service_name": service_name,
                    "tenant_id": tenant_id,
                    "owner": owner,
                },
            )

            return record

    # ========================================================
    # RESOLUTION
    # ========================================================

    def get(
        self,
        service_name: str,
        *,
        default: Any = None,
    ) -> Any:

        with self._lock:

            record = self._services.get(
                service_name
            )

            if not record:
                return default

            return record.service

    def get_record(
        self,
        service_name: str,
    ) -> Optional[RuntimeServiceRecord]:

        with self._lock:

            return self._services.get(
                service_name
            )

    def get_for_tenant(
        self,
        tenant_id: str,
        service_name: str,
        *,
        default: Any = None,
    ) -> Any:

        with self._lock:

            tenant_services = (
                self._tenant_services.get(
                    tenant_id or DEFAULT_TENANT,
                    {},
                )
            )

            record = tenant_services.get(
                service_name
            )

            if not record:
                return default

            return record.service

    # ========================================================
    # STATUS MANAGEMENT
    # ========================================================

    def set_status(
        self,
        service_name: str,
        status: str,
        *,
        reason: Optional[str] = None,
    ) -> bool:

        with self._lock:

            record = self._services.get(
                service_name
            )

            if not record:
                return False

            record.status = status
            record.updated_at_ms = _now_ms()

            if status == SERVICE_QUARANTINED:
                record.quarantine_reason = reason

            self._emit(
                "RUNTIME_SERVICE_STATUS_CHANGED",
                payload={
                    "service_name": service_name,
                    "status": status,
                    "reason": reason,
                },
            )

            return True

    def heartbeat(
        self,
        service_name: str,
    ) -> bool:

        with self._lock:

            record = self._services.get(
                service_name
            )

            if not record:
                return False

            record.last_heartbeat_ms = (
                _now_ms()
            )

            record.updated_at_ms = (
                _now_ms()
            )

            return True

    def quarantine(
        self,
        service_name: str,
        *,
        reason: str,
    ) -> bool:

        return self.set_status(
            service_name,
            SERVICE_QUARANTINED,
            reason=reason,
        )

    def clear_quarantine(
        self,
        service_name: str,
    ) -> bool:

        with self._lock:

            record = self._services.get(
                service_name
            )

            if not record:
                return False

            record.quarantine_reason = None

            record.status = SERVICE_READY

            record.updated_at_ms = (
                _now_ms()
            )

            self._emit(
                "RUNTIME_SERVICE_RESTORED",
                payload={
                    "service_name": service_name,
                },
            )

            return True

    # ========================================================
    # HEALTH MANAGEMENT
    # ========================================================

    def report_error(
        self,
        service_name: str,
        *,
        reason: Optional[str] = None,
    ) -> bool:

        with self._lock:

            record = self._services.get(
                service_name
            )

            if not record:
                return False

            record.error_count += 1

            record.health_score = max(
                0.0,
                record.health_score - 5.0,
            )

            record.updated_at_ms = (
                _now_ms()
            )

            if record.health_score < 50:
                record.status = (
                    SERVICE_DEGRADED
                )

            self._emit(
                "RUNTIME_SERVICE_ERROR",
                payload={
                    "service_name": service_name,
                    "reason": reason,
                    "error_count": (
                        record.error_count
                    ),
                },
            )

            return True

    def report_warning(
        self,
        service_name: str,
        *,
        reason: Optional[str] = None,
    ) -> bool:

        with self._lock:

            record = self._services.get(
                service_name
            )

            if not record:
                return False

            record.warning_count += 1

            record.health_score = max(
                0.0,
                record.health_score - 1.0,
            )

            record.updated_at_ms = (
                _now_ms()
            )

            self._emit(
                "RUNTIME_SERVICE_WARNING",
                payload={
                    "service_name": service_name,
                    "reason": reason,
                    "warning_count": (
                        record.warning_count
                    ),
                },
            )

            return True

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_dependencies(
        self,
        service_name: str,
    ) -> Dict[str, Any]:

        with self._lock:

            record = self._services.get(
                service_name
            )

            if not record:
                return {
                    "ok": False,
                    "reason": "service_not_found",
                }

            missing = []

            for dep in record.dependencies:

                if dep not in self._services:
                    missing.append(dep)

            return {
                "ok": len(missing) == 0,
                "service_name": service_name,
                "missing_dependencies": missing,
            }

    # ========================================================
    # READS
    # ========================================================

    def list_services(
        self,
        *,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[RuntimeServiceRecord]:

        with self._lock:

            if tenant_id:

                records = list(
                    self._tenant_services.get(
                        tenant_id,
                        {},
                    ).values()
                )

            else:

                records = list(
                    self._services.values()
                )

            if status:

                records = [
                    r for r in records
                    if r.status == status
                ]

            return records

    def service_stats(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            records = list(
                self._services.values()
            )

            return {

                "total_services":
                    len(records),

                "ready":
                    len([
                        r for r in records
                        if r.status == SERVICE_READY
                    ]),

                "degraded":
                    len([
                        r for r in records
                        if r.status == SERVICE_DEGRADED
                    ]),

                "quarantined":
                    len([
                        r for r in records
                        if r.status == SERVICE_QUARANTINED
                    ]),

                "unavailable":
                    len([
                        r for r in records
                        if r.status == SERVICE_UNAVAILABLE
                    ]),
            }

    def topology(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            return {
                name: {
                    "dependencies":
                        record.dependencies,

                    "status":
                        record.status,

                    "tenant_id":
                        record.tenant_id,

                    "owner":
                        record.owner,

                    "health_score":
                        record.health_score,
                }
                for name, record
                in self._services.items()
            }

    # ========================================================
    # REMOVAL
    # ========================================================

    def unregister(
        self,
        service_name: str,
    ) -> bool:

        with self._lock:

            record = self._services.pop(
                service_name,
                None,
            )

            if not record:
                return False

            tenant_bucket = (
                self._tenant_services.get(
                    record.tenant_id,
                    {},
                )
            )

            tenant_bucket.pop(
                service_name,
                None,
            )

            self._emit(
                "RUNTIME_SERVICE_UNREGISTERED",
                payload={
                    "service_name": service_name,
                },
            )

            return True

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
                source="runtime_service_registry",
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


_DEFAULT_RUNTIME_SERVICE_REGISTRY = None


def get_runtime_service_registry(
    *,
    event_bus: Any = None,
    reset: bool = False,
) -> RuntimeServiceRegistry:

    global _DEFAULT_RUNTIME_SERVICE_REGISTRY

    if (
        reset
        or _DEFAULT_RUNTIME_SERVICE_REGISTRY is None
    ):

        _DEFAULT_RUNTIME_SERVICE_REGISTRY = (
            RuntimeServiceRegistry(
                event_bus=event_bus,
            )
        )

    return _DEFAULT_RUNTIME_SERVICE_REGISTRY