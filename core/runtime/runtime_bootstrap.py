"""
core/runtime/runtime_bootstrap.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from core.runtime.runtime_service_registry import get_runtime_service_registry
from core.runtime.runtime_lifecycle_manager import (
    get_runtime_lifecycle_manager,
    MODE_DEVELOPMENT,
)
from core.runtime.runtime_policy_manager import get_runtime_policy_manager
from core.runtime.runtime_health_manager import get_runtime_health_manager
from core.runtime.runtime_dependency_graph import get_runtime_dependency_graph
from core.runtime.runtime_recovery_manager import get_runtime_recovery_manager

from core.runtime.distributed_execution_queue import get_distributed_execution_queue
from core.runtime.distributed_execution_router import get_distributed_execution_router
from core.runtime.worker_orchestrator import get_worker_orchestrator
from core.runtime.lease_watchdog import get_lease_watchdog
from core.runtime.execution_backpressure_controller import (
    get_execution_backpressure_controller,
)
from core.runtime.execution_graph_engine import get_execution_graph_engine
from core.runtime.autonomous_runtime_supervisor import (
    get_autonomous_runtime_supervisor,
)
from core.runtime.runtime_federation_manager import (
    get_runtime_federation_manager,
)

from core.runtime.sovereign_runtime_bootstrap import (
    define_sovereign_runtime_services,
    bootstrap_sovereign_runtime,
)

from core.runtime.runtime_cognition_bootstrap import (
    define_runtime_cognition_services,
    bootstrap_runtime_cognition,
)


@dataclass
class RuntimeBootstrapResult:
    ok: bool
    runtime_mode: str
    initialized_services: Dict[str, Any] = field(default_factory=dict)
    failed_services: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "runtime_mode": self.runtime_mode,
            "initialized_services": list(self.initialized_services.keys()),
            "failed_services": self.failed_services,
            "metadata": self.metadata,
        }


def bootstrap_runtime(
    *,
    storage: Any,
    event_bus: Any,
    runtime_mode: str = MODE_DEVELOPMENT,
    db_path: str = "data/distributed_execution_queue.db",
    enable_federation: bool = False,
    reset: bool = False,
) -> RuntimeBootstrapResult:
    initialized: Dict[str, Any] = {}
    failed: Dict[str, str] = {}

    # ========================================================
    # REGISTRY
    # ========================================================

    registry = get_runtime_service_registry(
        event_bus=event_bus,
        reset=reset,
    )

    storage.runtime_service_registry = registry
    initialized["runtime_service_registry"] = registry

    registry.register(
        "runtime_bootstrap",
        bootstrap_runtime,
        owner="system",
        metadata={
            "runtime_mode": runtime_mode,
        },
    )

    # ========================================================
    # LIFECYCLE
    # ========================================================

    lifecycle = get_runtime_lifecycle_manager(
        registry=registry,
        storage=storage,
        event_bus=event_bus,
        runtime_mode=runtime_mode,
        reset=reset,
    )

    storage.runtime_lifecycle_manager = lifecycle
    initialized["runtime_lifecycle_manager"] = lifecycle

    # ========================================================
    # DEFINE CORE GOVERNANCE SERVICES
    # ========================================================

    lifecycle.define_service("runtime_policy_manager")

    lifecycle.define_service(
        "runtime_health_manager",
        dependencies=[
            "runtime_policy_manager",
        ],
    )

    lifecycle.define_service(
        "runtime_dependency_graph",
        dependencies=[
            "runtime_health_manager",
        ],
    )

    lifecycle.define_service(
        "runtime_recovery_manager",
        dependencies=[
            "runtime_health_manager",
            "runtime_dependency_graph",
            "runtime_policy_manager",
        ],
    )

    # ========================================================
    # DEFINE CORE EXECUTION SERVICES
    # ========================================================

    lifecycle.define_service("execution_queue")

    lifecycle.define_service(
        "execution_router",
        dependencies=[
            "execution_queue",
        ],
    )

    lifecycle.define_service(
        "worker_orchestrator",
        dependencies=[
            "execution_queue",
            "execution_router",
        ],
    )

    lifecycle.define_service(
        "lease_watchdog",
        dependencies=[
            "execution_queue",
            "worker_orchestrator",
        ],
    )

    lifecycle.define_service(
        "execution_backpressure_controller",
        dependencies=[
            "execution_queue",
            "worker_orchestrator",
            "lease_watchdog",
        ],
    )

    lifecycle.define_service(
        "execution_graph_engine",
        dependencies=[
            "execution_queue",
        ],
    )

    lifecycle.define_service(
        "autonomous_runtime_supervisor",
        dependencies=[
            "runtime_health_manager",
            "runtime_dependency_graph",
            "runtime_recovery_manager",
            "execution_backpressure_controller",
            "lease_watchdog",
        ],
    )

    lifecycle.define_service(
        "runtime_federation_manager",
        dependencies=[
            "autonomous_runtime_supervisor",
            "runtime_health_manager",
        ],
    )

    # ========================================================
    # DEFINE SOVEREIGN RUNTIME SERVICES
    # ========================================================

    define_sovereign_runtime_services(
        lifecycle=lifecycle,
    )

    # ========================================================
    # DEFINE RUNTIME COGNITION SERVICES
    # ========================================================

    define_runtime_cognition_services(
        lifecycle=lifecycle,
    )

    # ========================================================
    # POLICY MANAGER
    # ========================================================

    try:
        runtime_policy_manager = get_runtime_policy_manager(
            registry=registry,
            lifecycle=lifecycle,
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.runtime_policy_manager = runtime_policy_manager

        registry.register(
            "runtime_policy_manager",
            runtime_policy_manager,
            owner="runtime_bootstrap",
        )

        lifecycle.start_service("runtime_policy_manager")

        initialized["runtime_policy_manager"] = runtime_policy_manager

    except Exception as exc:
        failed["runtime_policy_manager"] = str(exc)

    # ========================================================
    # HEALTH MANAGER
    # ========================================================

    try:
        runtime_health_manager = get_runtime_health_manager(
            registry=registry,
            lifecycle=lifecycle,
            policy_manager=getattr(storage, "runtime_policy_manager", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.runtime_health_manager = runtime_health_manager

        registry.register(
            "runtime_health_manager",
            runtime_health_manager,
            owner="runtime_bootstrap",
            dependencies=[
                "runtime_policy_manager",
            ],
        )

        lifecycle.start_service("runtime_health_manager")

        initialized["runtime_health_manager"] = runtime_health_manager

    except Exception as exc:
        failed["runtime_health_manager"] = str(exc)

    # ========================================================
    # DEPENDENCY GRAPH
    # ========================================================

    try:
        runtime_dependency_graph = get_runtime_dependency_graph(
            registry=registry,
            lifecycle=lifecycle,
            health_manager=getattr(storage, "runtime_health_manager", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.runtime_dependency_graph = runtime_dependency_graph

        registry.register(
            "runtime_dependency_graph",
            runtime_dependency_graph,
            owner="runtime_bootstrap",
            dependencies=[
                "runtime_health_manager",
            ],
        )

        lifecycle.start_service("runtime_dependency_graph")

        initialized["runtime_dependency_graph"] = runtime_dependency_graph

    except Exception as exc:
        failed["runtime_dependency_graph"] = str(exc)

    # ========================================================
    # EXECUTION QUEUE
    # ========================================================

    try:
        execution_queue = get_distributed_execution_queue(
            db_path=db_path,
            reset=reset,
        )

        storage.execution_queue = execution_queue

        registry.register(
            "execution_queue",
            execution_queue,
            owner="runtime_bootstrap",
            metadata={
                "runtime_mode": runtime_mode,
            },
        )

        lifecycle.start_service("execution_queue")

        initialized["execution_queue"] = execution_queue

    except Exception as exc:
        failed["execution_queue"] = str(exc)

    # ========================================================
    # EXECUTION ROUTER
    # ========================================================

    try:
        execution_router = get_distributed_execution_router(
            queue=getattr(storage, "execution_queue", None),
            worker_orchestrator=getattr(storage, "worker_orchestrator", None),
            sovereign_execution_controller=getattr(
                storage,
                "sovereign_execution_controller",
                None,
            ),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.execution_router = execution_router

        registry.register(
            "execution_router",
            execution_router,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
            ],
        )

        lifecycle.start_service("execution_router")

        initialized["execution_router"] = execution_router

    except Exception as exc:
        failed["execution_router"] = str(exc)

    # ========================================================
    # WORKER ORCHESTRATOR
    # ========================================================

    try:
        worker_orchestrator = get_worker_orchestrator(
            db_path=db_path,
            queue=getattr(storage, "execution_queue", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.worker_orchestrator = worker_orchestrator

        registry.register(
            "worker_orchestrator",
            worker_orchestrator,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
                "execution_router",
            ],
        )

        lifecycle.start_service("worker_orchestrator")

        initialized["worker_orchestrator"] = worker_orchestrator

    except Exception as exc:
        failed["worker_orchestrator"] = str(exc)

    try:
        if getattr(storage, "execution_router", None) is not None:
            storage.execution_router.worker_orchestrator = getattr(
                storage,
                "worker_orchestrator",
                None,
            )
    except Exception:
        pass

    # ========================================================
    # LEASE WATCHDOG
    # ========================================================

    try:
        lease_watchdog = get_lease_watchdog(
            queue=getattr(storage, "execution_queue", None),
            worker_orchestrator=getattr(storage, "worker_orchestrator", None),
            router=getattr(storage, "execution_router", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.lease_watchdog = lease_watchdog

        registry.register(
            "lease_watchdog",
            lease_watchdog,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
                "worker_orchestrator",
            ],
        )

        lifecycle.start_service("lease_watchdog")

        initialized["lease_watchdog"] = lease_watchdog

    except Exception as exc:
        failed["lease_watchdog"] = str(exc)

    # ========================================================
    # BACKPRESSURE CONTROLLER
    # ========================================================

    try:
        backpressure = get_execution_backpressure_controller(
            queue=getattr(storage, "execution_queue", None),
            worker_orchestrator=getattr(storage, "worker_orchestrator", None),
            watchdog=getattr(storage, "lease_watchdog", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.backpressure_controller = backpressure

        registry.register(
            "execution_backpressure_controller",
            backpressure,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
                "worker_orchestrator",
                "lease_watchdog",
            ],
        )

        lifecycle.start_service("execution_backpressure_controller")

        initialized["execution_backpressure_controller"] = backpressure

    except Exception as exc:
        failed["execution_backpressure_controller"] = str(exc)

    try:
        if getattr(storage, "worker_orchestrator", None) is not None:
            storage.worker_orchestrator.backpressure_controller = getattr(
                storage,
                "backpressure_controller",
                None,
            )

        if getattr(storage, "execution_router", None) is not None:
            storage.execution_router.backpressure_controller = getattr(
                storage,
                "backpressure_controller",
                None,
            )
    except Exception:
        pass

    # ========================================================
    # EXECUTION GRAPH ENGINE
    # ========================================================

    try:
        execution_graph_engine = get_execution_graph_engine(
            db_path=db_path,
            queue=getattr(storage, "execution_queue", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.execution_graph_engine = execution_graph_engine

        registry.register(
            "execution_graph_engine",
            execution_graph_engine,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
            ],
        )

        lifecycle.start_service("execution_graph_engine")

        initialized["execution_graph_engine"] = execution_graph_engine

    except Exception as exc:
        failed["execution_graph_engine"] = str(exc)

    # ========================================================
    # RECOVERY MANAGER
    # ========================================================

    try:
        runtime_recovery_manager = get_runtime_recovery_manager(
            registry=registry,
            lifecycle=lifecycle,
            health_manager=getattr(storage, "runtime_health_manager", None),
            dependency_graph=getattr(storage, "runtime_dependency_graph", None),
            policy_manager=getattr(storage, "runtime_policy_manager", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.runtime_recovery_manager = runtime_recovery_manager

        registry.register(
            "runtime_recovery_manager",
            runtime_recovery_manager,
            owner="runtime_bootstrap",
            dependencies=[
                "runtime_health_manager",
                "runtime_dependency_graph",
                "runtime_policy_manager",
            ],
        )

        lifecycle.start_service("runtime_recovery_manager")

        initialized["runtime_recovery_manager"] = runtime_recovery_manager

    except Exception as exc:
        failed["runtime_recovery_manager"] = str(exc)

    # ========================================================
    # AUTONOMOUS RUNTIME SUPERVISOR
    # ========================================================

    try:
        autonomous_runtime_supervisor = get_autonomous_runtime_supervisor(
            registry=registry,
            lifecycle=lifecycle,
            health_manager=getattr(storage, "runtime_health_manager", None),
            dependency_graph=getattr(storage, "runtime_dependency_graph", None),
            policy_manager=getattr(storage, "runtime_policy_manager", None),
            recovery_manager=getattr(storage, "runtime_recovery_manager", None),
            backpressure_controller=getattr(storage, "backpressure_controller", None),
            watchdog=getattr(storage, "lease_watchdog", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.autonomous_runtime_supervisor = autonomous_runtime_supervisor

        registry.register(
            "autonomous_runtime_supervisor",
            autonomous_runtime_supervisor,
            owner="runtime_bootstrap",
            dependencies=[
                "runtime_health_manager",
                "runtime_dependency_graph",
                "runtime_recovery_manager",
                "execution_backpressure_controller",
                "lease_watchdog",
            ],
        )

        lifecycle.start_service("autonomous_runtime_supervisor")

        autonomous_runtime_supervisor.start(
            interval_seconds=30.0,
        )

        initialized["autonomous_runtime_supervisor"] = autonomous_runtime_supervisor

    except Exception as exc:
        failed["autonomous_runtime_supervisor"] = str(exc)

    # ========================================================
    # OPTIONAL FEDERATION MANAGER
    # ========================================================

    if enable_federation:
        try:
            runtime_federation_manager = get_runtime_federation_manager(
                registry=registry,
                lifecycle=lifecycle,
                health_manager=getattr(storage, "runtime_health_manager", None),
                supervisor=getattr(storage, "autonomous_runtime_supervisor", None),
                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )

            storage.runtime_federation_manager = runtime_federation_manager

            registry.register(
                "runtime_federation_manager",
                runtime_federation_manager,
                owner="runtime_bootstrap",
                dependencies=[
                    "autonomous_runtime_supervisor",
                    "runtime_health_manager",
                ],
                metadata={
                    "federation_enabled": True,
                },
            )

            lifecycle.start_service("runtime_federation_manager")

            initialized["runtime_federation_manager"] = runtime_federation_manager

        except Exception as exc:
            failed["runtime_federation_manager"] = str(exc)

    else:
        storage.runtime_federation_manager = getattr(
            storage,
            "runtime_federation_manager",
            None,
        )

    # ========================================================
    # SOVEREIGN RUNTIME BOOTSTRAP
    # ========================================================

    bootstrap_sovereign_runtime(
        storage=storage,
        registry=registry,
        lifecycle=lifecycle,
        event_bus=event_bus,
        initialized=initialized,
        failed=failed,
        reset=reset,
    )

    # ========================================================
    # RUNTIME COGNITION BOOTSTRAP
    # ========================================================

    bootstrap_runtime_cognition(
        storage=storage,
        registry=registry,
        lifecycle=lifecycle,
        event_bus=event_bus,
        initialized=initialized,
        failed=failed,
        reset=reset,
        bootstrap_tenant_id="default",
        run_initial_assessments=True,
    )

    # ========================================================
    # FINAL CORE CROSS-REFERENCES
    # ========================================================

    try:
        if getattr(storage, "execution_router", None) is not None:
            storage.execution_router.sovereign_execution_controller = getattr(
                storage,
                "sovereign_execution_controller",
                None,
            )

        if getattr(storage, "worker_orchestrator", None) is not None:
            storage.worker_orchestrator.backpressure_controller = getattr(
                storage,
                "backpressure_controller",
                None,
            )

        if getattr(storage, "execution_router", None) is not None:
            storage.execution_router.backpressure_controller = getattr(
                storage,
                "backpressure_controller",
                None,
            )

    except Exception:
        pass

    # ========================================================
    # RESULT
    # ========================================================

    ok = len(failed) == 0

    return RuntimeBootstrapResult(
        ok=ok,
        runtime_mode=runtime_mode,
        initialized_services=initialized,
        failed_services=failed,
        metadata={
            "service_count": len(initialized),
            "failed_count": len(failed),
            "federation_enabled": enable_federation,
            "sovereign_runtime_bootstrap": "enabled",
            "runtime_cognition_bootstrap": "enabled",
        },
    )