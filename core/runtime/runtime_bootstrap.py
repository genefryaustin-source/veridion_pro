"""
core/runtime/runtime_bootstrap.py

Authoritative Runtime Bootstrap Layer.

Purpose:
- centralized runtime assembly
- deterministic startup ordering
- runtime dependency orchestration
- service registration
- lifecycle-managed startup
- architectural boundary enforcement

Architectural Goal:
app.py should eventually become:

    runtime = bootstrap_runtime(...)
    render_ui(...)

instead of:
- scattered runtime initialization
- ad hoc service construction
- session-state runtime management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ============================================================
# CORE RUNTIME IMPORTS
# ============================================================

from core.runtime.runtime_service_registry import (
    get_runtime_service_registry,
)

from core.runtime.runtime_lifecycle_manager import (
    get_runtime_lifecycle_manager,
    MODE_DEVELOPMENT,
)

from core.runtime.distributed_execution_queue import (
    get_distributed_execution_queue,
)

from core.runtime.distributed_execution_router import (
    get_distributed_execution_router,
)

from core.runtime.worker_orchestrator import (
    get_worker_orchestrator,
)

from core.runtime.lease_watchdog import (
    get_lease_watchdog,
)

from core.runtime.execution_backpressure_controller import (
    get_execution_backpressure_controller,
)

from core.runtime.execution_graph_engine import (
    get_execution_graph_engine,
)

from core.runtime.graph_replay_engine import (
    get_graph_replay_engine,
)


# ============================================================
# BOOTSTRAP RESULT
# ============================================================

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
            "initialized_services": list(
                self.initialized_services.keys()
            ),
            "failed_services": self.failed_services,
            "metadata": self.metadata,
        }


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_runtime(
    *,
    storage: Any,
    event_bus: Any,
    runtime_mode: str = MODE_DEVELOPMENT,
    db_path: str = "data/distributed_execution_queue.db",
    reset: bool = False,
) -> RuntimeBootstrapResult:
    """
    Central runtime bootstrap.

    This is the authoritative runtime assembly layer.
    """

    initialized = {}
    failed = {}

    # ========================================================
    # SERVICE REGISTRY
    # ========================================================

    registry = get_runtime_service_registry(
        event_bus=event_bus,
        reset=reset,
    )

    storage.runtime_service_registry = registry

    initialized[
        "runtime_service_registry"
    ] = registry

    # ========================================================
    # LIFECYCLE MANAGER
    # ========================================================

    lifecycle = get_runtime_lifecycle_manager(
        registry=registry,
        storage=storage,
        event_bus=event_bus,
        runtime_mode=runtime_mode,
        reset=reset,
    )

    storage.runtime_lifecycle_manager = lifecycle

    initialized[
        "runtime_lifecycle_manager"
    ] = lifecycle

    # ========================================================
    # DEFINE SERVICES
    # ========================================================

    lifecycle.define_service(
        "execution_queue",
    )

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
        ],
    )

    lifecycle.define_service(
        "execution_graph_engine",
        dependencies=[
            "execution_queue",
        ],
    )

    lifecycle.define_service(
        "graph_replay_engine",
        dependencies=[
            "execution_graph_engine",
            "execution_queue",
        ],
    )

    # ========================================================
    # EXECUTION QUEUE
    # ========================================================

    try:

        execution_queue = (
            get_distributed_execution_queue(
                db_path=db_path,
                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.execution_queue = (
            execution_queue
        )

        registry.register(
            "execution_queue",
            execution_queue,
            owner="runtime_bootstrap",
            metadata={
                "runtime_mode": runtime_mode,
            },
        )

        lifecycle.start_service(
            "execution_queue",
        )

        initialized[
            "execution_queue"
        ] = execution_queue

    except Exception as exc:

        failed[
            "execution_queue"
        ] = str(exc)

    # ========================================================
    # EXECUTION ROUTER
    # ========================================================

    try:

        execution_router = (
            get_distributed_execution_router(
                queue=storage.execution_queue,
                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.execution_router = (
            execution_router
        )

        registry.register(
            "execution_router",
            execution_router,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
            ],
        )

        lifecycle.start_service(
            "execution_router",
        )

        initialized[
            "execution_router"
        ] = execution_router

    except Exception as exc:

        failed[
            "execution_router"
        ] = str(exc)

    # ========================================================
    # WORKER ORCHESTRATOR
    # ========================================================

    try:

        worker_orchestrator = (
            get_worker_orchestrator(
                storage=storage,
                queue=storage.execution_queue,
                router=storage.execution_router,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.worker_orchestrator = (
            worker_orchestrator
        )

        registry.register(
            "worker_orchestrator",
            worker_orchestrator,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
                "execution_router",
            ],
        )

        lifecycle.start_service(
            "worker_orchestrator",
        )

        initialized[
            "worker_orchestrator"
        ] = worker_orchestrator

    except Exception as exc:

        failed[
            "worker_orchestrator"
        ] = str(exc)

    # ========================================================
    # LEASE WATCHDOG
    # ========================================================

    try:

        lease_watchdog = (
            get_lease_watchdog(
                storage=storage,
                queue=storage.execution_queue,
                orchestrator=storage.worker_orchestrator,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.lease_watchdog = (
            lease_watchdog
        )

        registry.register(
            "lease_watchdog",
            lease_watchdog,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
                "worker_orchestrator",
            ],
        )

        lifecycle.start_service(
            "lease_watchdog",
        )

        initialized[
            "lease_watchdog"
        ] = lease_watchdog

    except Exception as exc:

        failed[
            "lease_watchdog"
        ] = str(exc)

    # ========================================================
    # BACKPRESSURE CONTROLLER
    # ========================================================

    try:

        backpressure = (
            get_execution_backpressure_controller(
                storage=storage,
                queue=storage.execution_queue,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.backpressure_controller = (
            backpressure
        )

        registry.register(
            "execution_backpressure_controller",
            backpressure,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
            ],
        )

        lifecycle.start_service(
            "execution_backpressure_controller",
        )

        initialized[
            "execution_backpressure_controller"
        ] = backpressure

    except Exception as exc:

        failed[
            "execution_backpressure_controller"
        ] = str(exc)

    # ========================================================
    # EXECUTION GRAPH ENGINE
    # ========================================================

    try:

        execution_graph_engine = (
            get_execution_graph_engine(
                db_path=db_path,
                queue=storage.execution_queue,
                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.execution_graph_engine = (
            execution_graph_engine
        )

        registry.register(
            "execution_graph_engine",
            execution_graph_engine,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_queue",
            ],
        )

        lifecycle.start_service(
            "execution_graph_engine",
        )

        initialized[
            "execution_graph_engine"
        ] = execution_graph_engine

    except Exception as exc:

        failed[
            "execution_graph_engine"
        ] = str(exc)

    # ========================================================
    # GRAPH REPLAY ENGINE
    # ========================================================

    try:

        graph_replay_engine = (
            get_graph_replay_engine(
                db_path=db_path,
                graph_engine=storage.execution_graph_engine,
                queue=storage.execution_queue,
                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.graph_replay_engine = (
            graph_replay_engine
        )

        registry.register(
            "graph_replay_engine",
            graph_replay_engine,
            owner="runtime_bootstrap",
            dependencies=[
                "execution_graph_engine",
                "execution_queue",
            ],
        )

        lifecycle.start_service(
            "graph_replay_engine",
        )

        initialized[
            "graph_replay_engine"
        ] = graph_replay_engine

    except Exception as exc:

        failed[
            "graph_replay_engine"
        ] = str(exc)

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
        },
    )