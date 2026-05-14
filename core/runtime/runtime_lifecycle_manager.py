"""
core/runtime/runtime_lifecycle_manager.py

Runtime Lifecycle Manager.

Purpose:
- centralized runtime startup
- dependency-aware initialization
- controlled shutdown/restart
- service health tracking
- runtime mode support
- remove orchestration bootstrap sprawl from app.py
"""

from __future__ import annotations

import time
import traceback
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional


LIFECYCLE_STOPPED = "STOPPED"
LIFECYCLE_STARTING = "STARTING"
LIFECYCLE_RUNNING = "RUNNING"
LIFECYCLE_DEGRADED = "DEGRADED"
LIFECYCLE_FAILED = "FAILED"
LIFECYCLE_STOPPING = "STOPPING"
LIFECYCLE_RESTARTING = "RESTARTING"

MODE_DEVELOPMENT = "DEVELOPMENT"
MODE_STANDALONE = "STANDALONE"
MODE_DISTRIBUTED = "DISTRIBUTED"
MODE_GOVCLOUD = "GOVCLOUD"
MODE_RECOVERY = "RECOVERY"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeLifecycleRecord:
    service_name: str
    status: str = LIFECYCLE_STOPPED
    dependencies: List[str] = field(default_factory=list)
    started_at_ms: Optional[int] = None
    stopped_at_ms: Optional[int] = None
    updated_at_ms: int = field(default_factory=_now_ms)
    restart_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeLifecycleResult:
    ok: bool
    service_name: str
    status: str
    message: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuntimeLifecycleManager:
    def __init__(
        self,
        *,
        registry: Any,
        storage: Any = None,
        event_bus: Any = None,
        runtime_mode: str = MODE_DEVELOPMENT,
    ) -> None:
        self.registry = registry
        self.storage = storage
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.runtime_mode = runtime_mode

        self._records: Dict[str, RuntimeLifecycleRecord] = {}
        self._start_hooks: Dict[str, Callable[..., Any]] = {}
        self._stop_hooks: Dict[str, Callable[..., Any]] = {}

    # ========================================================
    # SERVICE DEFINITIONS
    # ========================================================

    def define_service(
        self,
        service_name: str,
        *,
        dependencies: Optional[List[str]] = None,
        start_hook: Optional[Callable[..., Any]] = None,
        stop_hook: Optional[Callable[..., Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeLifecycleRecord:
        record = RuntimeLifecycleRecord(
            service_name=service_name,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        self._records[service_name] = record

        if start_hook is not None:
            self._start_hooks[service_name] = start_hook

        if stop_hook is not None:
            self._stop_hooks[service_name] = stop_hook

        return record

    # ========================================================
    # STARTUP
    # ========================================================

    def start_service(
        self,
        service_name: str,
        *,
        started_by: str = "runtime_lifecycle_manager",
    ) -> RuntimeLifecycleResult:
        record = self._records.get(service_name)

        if record is None:
            return RuntimeLifecycleResult(
                ok=False,
                service_name=service_name,
                status=LIFECYCLE_FAILED,
                message="Service is not defined in lifecycle manager.",
            )

        if record.status == LIFECYCLE_RUNNING:
            return RuntimeLifecycleResult(
                ok=True,
                service_name=service_name,
                status=LIFECYCLE_RUNNING,
                message="Service already running.",
            )

        deps = self.validate_dependencies(service_name)

        if not deps.get("ok"):
            record.status = LIFECYCLE_FAILED
            record.last_error = f"Missing dependencies: {deps.get('missing_dependencies')}"
            record.updated_at_ms = _now_ms()

            return RuntimeLifecycleResult(
                ok=False,
                service_name=service_name,
                status=LIFECYCLE_FAILED,
                message=record.last_error,
                metadata=deps,
            )

        record.status = LIFECYCLE_STARTING
        record.updated_at_ms = _now_ms()

        self._emit(
            "RUNTIME_SERVICE_STARTING",
            {
                "service_name": service_name,
                "started_by": started_by,
            },
        )

        try:
            hook = self._start_hooks.get(service_name)

            service = None

            if hook is not None:
                service = hook(
                    storage=self.storage,
                    registry=self.registry,
                    event_bus=self.event_bus,
                )

            if service is not None:
                self.registry.register(
                    service_name,
                    service,
                    owner=started_by,
                    dependencies=record.dependencies,
                    metadata=record.metadata,
                    overwrite=True,
                )

            record.status = LIFECYCLE_RUNNING
            record.started_at_ms = _now_ms()
            record.updated_at_ms = _now_ms()
            record.last_error = None

            self._emit(
                "RUNTIME_SERVICE_STARTED",
                {
                    "service_name": service_name,
                    "started_by": started_by,
                },
            )

            return RuntimeLifecycleResult(
                ok=True,
                service_name=service_name,
                status=LIFECYCLE_RUNNING,
                message="Service started successfully.",
            )

        except Exception as exc:
            err = str(exc)

            record.status = LIFECYCLE_FAILED
            record.last_error = err
            record.updated_at_ms = _now_ms()

            try:
                self.registry.report_error(
                    service_name,
                    reason=err,
                )
            except Exception:
                pass

            self._emit(
                "RUNTIME_SERVICE_START_FAILED",
                {
                    "service_name": service_name,
                    "error": err,
                    "traceback": traceback.format_exc(),
                },
            )

            return RuntimeLifecycleResult(
                ok=False,
                service_name=service_name,
                status=LIFECYCLE_FAILED,
                message="Service failed to start.",
                error=err,
            )

    def start_all(
        self,
        *,
        started_by: str = "runtime_lifecycle_manager",
    ) -> List[RuntimeLifecycleResult]:
        ordered = self.startup_order()
        results = []

        for service_name in ordered:
            result = self.start_service(
                service_name,
                started_by=started_by,
            )
            results.append(result)

            if not result.ok:
                self._emit(
                    "RUNTIME_STARTUP_DEGRADED",
                    {
                        "failed_service": service_name,
                        "result": result.to_dict(),
                    },
                )

        return results

    # ========================================================
    # SHUTDOWN
    # ========================================================

    def stop_service(
        self,
        service_name: str,
        *,
        stopped_by: str = "runtime_lifecycle_manager",
        force: bool = False,
    ) -> RuntimeLifecycleResult:
        record = self._records.get(service_name)

        if record is None:
            return RuntimeLifecycleResult(
                ok=False,
                service_name=service_name,
                status=LIFECYCLE_FAILED,
                message="Service is not defined in lifecycle manager.",
            )

        record.status = LIFECYCLE_STOPPING
        record.updated_at_ms = _now_ms()

        self._emit(
            "RUNTIME_SERVICE_STOPPING",
            {
                "service_name": service_name,
                "stopped_by": stopped_by,
                "force": force,
            },
        )

        try:
            hook = self._stop_hooks.get(service_name)

            if hook is not None:
                hook(
                    storage=self.storage,
                    registry=self.registry,
                    event_bus=self.event_bus,
                    force=force,
                )

            try:
                self.registry.set_status(
                    service_name,
                    "STOPPED",
                    reason="lifecycle_stop",
                )
            except Exception:
                pass

            record.status = LIFECYCLE_STOPPED
            record.stopped_at_ms = _now_ms()
            record.updated_at_ms = _now_ms()

            self._emit(
                "RUNTIME_SERVICE_STOPPED",
                {
                    "service_name": service_name,
                    "stopped_by": stopped_by,
                },
            )

            return RuntimeLifecycleResult(
                ok=True,
                service_name=service_name,
                status=LIFECYCLE_STOPPED,
                message="Service stopped successfully.",
            )

        except Exception as exc:
            err = str(exc)

            record.status = LIFECYCLE_FAILED
            record.last_error = err
            record.updated_at_ms = _now_ms()

            return RuntimeLifecycleResult(
                ok=False,
                service_name=service_name,
                status=LIFECYCLE_FAILED,
                message="Service failed to stop.",
                error=err,
            )

    def stop_all(
        self,
        *,
        stopped_by: str = "runtime_lifecycle_manager",
        force: bool = False,
    ) -> List[RuntimeLifecycleResult]:
        ordered = list(reversed(self.startup_order()))
        results = []

        for service_name in ordered:
            results.append(
                self.stop_service(
                    service_name,
                    stopped_by=stopped_by,
                    force=force,
                )
            )

        return results

    # ========================================================
    # RESTART
    # ========================================================

    def restart_service(
        self,
        service_name: str,
        *,
        restarted_by: str = "runtime_lifecycle_manager",
        force: bool = False,
    ) -> RuntimeLifecycleResult:
        record = self._records.get(service_name)

        if record is None:
            return RuntimeLifecycleResult(
                ok=False,
                service_name=service_name,
                status=LIFECYCLE_FAILED,
                message="Service is not defined in lifecycle manager.",
            )

        record.status = LIFECYCLE_RESTARTING
        record.restart_count += 1
        record.updated_at_ms = _now_ms()

        stop_result = self.stop_service(
            service_name,
            stopped_by=restarted_by,
            force=force,
        )

        if not stop_result.ok and not force:
            return stop_result

        return self.start_service(
            service_name,
            started_by=restarted_by,
        )

    # ========================================================
    # DEPENDENCIES
    # ========================================================

    def validate_dependencies(
        self,
        service_name: str,
    ) -> Dict[str, Any]:
        record = self._records.get(service_name)

        if record is None:
            return {
                "ok": False,
                "reason": "service_not_defined",
                "missing_dependencies": [],
            }

        missing = []

        for dep in record.dependencies:
            dep_record = self._records.get(dep)

            if dep_record is None:
                missing.append(dep)
                continue

            if dep_record.status not in {
                LIFECYCLE_RUNNING,
                LIFECYCLE_DEGRADED,
            }:
                missing.append(dep)

        return {
            "ok": len(missing) == 0,
            "service_name": service_name,
            "missing_dependencies": missing,
        }

    def startup_order(self) -> List[str]:
        visited = set()
        ordered: List[str] = []

        def visit(name: str) -> None:
            if name in visited:
                return

            visited.add(name)

            record = self._records.get(name)

            if record is None:
                return

            for dep in record.dependencies:
                visit(dep)

            ordered.append(name)

        for service_name in self._records.keys():
            visit(service_name)

        return ordered

    # ========================================================
    # HEALTH / STATUS
    # ========================================================

    def heartbeat(
        self,
        service_name: str,
    ) -> bool:
        record = self._records.get(service_name)

        if record is None:
            return False

        record.updated_at_ms = _now_ms()

        try:
            self.registry.heartbeat(service_name)
        except Exception:
            pass

        return True

    def mark_degraded(
        self,
        service_name: str,
        *,
        reason: str,
    ) -> bool:
        record = self._records.get(service_name)

        if record is None:
            return False

        record.status = LIFECYCLE_DEGRADED
        record.last_error = reason
        record.updated_at_ms = _now_ms()

        try:
            self.registry.set_status(
                service_name,
                "DEGRADED",
                reason=reason,
            )
        except Exception:
            pass

        return True

    def status(self) -> Dict[str, Any]:
        records = [
            r.to_dict()
            for r in self._records.values()
        ]

        return {
            "runtime_mode": self.runtime_mode,
            "services": records,
            "startup_order": self.startup_order(),
            "counts": {
                "total": len(records),
                "running": len([r for r in records if r["status"] == LIFECYCLE_RUNNING]),
                "degraded": len([r for r in records if r["status"] == LIFECYCLE_DEGRADED]),
                "failed": len([r for r in records if r["status"] == LIFECYCLE_FAILED]),
                "stopped": len([r for r in records if r["status"] == LIFECYCLE_STOPPED]),
            },
        }

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
                source="runtime_lifecycle_manager",
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


_DEFAULT_RUNTIME_LIFECYCLE_MANAGER: Optional[
    RuntimeLifecycleManager
] = None


def get_runtime_lifecycle_manager(
    *,
    registry: Any,
    storage: Any = None,
    event_bus: Any = None,
    runtime_mode: str = MODE_DEVELOPMENT,
    reset: bool = False,
) -> RuntimeLifecycleManager:
    global _DEFAULT_RUNTIME_LIFECYCLE_MANAGER

    if reset or _DEFAULT_RUNTIME_LIFECYCLE_MANAGER is None:
        _DEFAULT_RUNTIME_LIFECYCLE_MANAGER = RuntimeLifecycleManager(
            registry=registry,
            storage=storage,
            event_bus=event_bus,
            runtime_mode=runtime_mode,
        )

    return _DEFAULT_RUNTIME_LIFECYCLE_MANAGER