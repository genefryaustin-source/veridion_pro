"""
core/runtime/runtime_cognition_bootstrap.py

Runtime cognition bootstrap layer.

Purpose:
- isolate runtime cognition initialization from core runtime bootstrap
- initialize operational learning, predictive cognition, execution cognition,
  sovereign operational reasoning, and adaptive operational strategy services
- preserve deterministic bootstrap visibility through initialized/failed maps

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden app-level global mutation
- explicit storage-owned runtime cognition services
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.runtime.runtime_fabric_learning_engine import (
    get_runtime_fabric_learning_engine,
)
from core.runtime.predictive_runtime_stability_engine import (
    get_predictive_runtime_stability_engine,
)
from core.runtime.autonomous_execution_cognition_engine import (
    get_autonomous_execution_cognition_engine,
)
from core.runtime.sovereign_operational_reasoning_engine import (
    get_sovereign_operational_reasoning_engine,
)
from core.runtime.adaptive_operational_strategy_engine import (
    get_adaptive_operational_strategy_engine,
)
from core.runtime.autonomous_runtime_intelligence_engine import (
    get_autonomous_runtime_intelligence_engine,
)

from core.runtime.runtime_cognition_orchestrator import (
    get_runtime_cognition_orchestrator,
)
from core.runtime.autonomous_mission_continuity_engine import (
    get_autonomous_mission_continuity_engine,
)

from core.runtime.sovereign_operational_memory_engine import (
    get_sovereign_operational_memory_engine,
)



def define_runtime_cognition_services(
    *,
    lifecycle: Any,
) -> None:
    """
    Define runtime cognition services and dependency relationships.
    This should be called after core and sovereign runtime service definitions.
    """

    lifecycle.define_service(
        "runtime_fabric_learning_engine",
        dependencies=[
            "sovereignty_decision_engine",
            "adaptive_sovereign_policy_engine",
            "sovereign_mesh_optimizer",
            "autonomous_cluster_balancer",
            "cross_runtime_execution_relay",
            "federated_execution_router",
            "distributed_runtime_cluster_manager",
            "execution_domain_manager",
            "runtime_recovery_manager",
        ],
    )

    lifecycle.define_service(
        "predictive_runtime_stability_engine",
        dependencies=[
            "runtime_fabric_learning_engine",
            "sovereignty_decision_engine",
            "adaptive_sovereign_policy_engine",
            "sovereign_mesh_optimizer",
            "autonomous_cluster_balancer",
            "cross_runtime_execution_relay",
            "federated_execution_router",
            "distributed_runtime_cluster_manager",
            "execution_domain_manager",
            "runtime_federation_manager",
        ],
    )

    lifecycle.define_service(
        "autonomous_execution_cognition_engine",
        dependencies=[
            "predictive_runtime_stability_engine",
            "runtime_fabric_learning_engine",
            "sovereignty_decision_engine",
            "adaptive_sovereign_policy_engine",
            "sovereign_mesh_optimizer",
            "autonomous_cluster_balancer",
            "cross_runtime_execution_relay",
            "federated_execution_router",
            "sovereign_execution_controller",
            "distributed_runtime_cluster_manager",
            "execution_domain_manager",
            "runtime_federation_manager",
            "runtime_recovery_manager",
            "autonomy_governor_v2",
        ],
    )

    lifecycle.define_service(
        "sovereign_operational_reasoning_engine",
        dependencies=[
            "autonomous_execution_cognition_engine",
            "predictive_runtime_stability_engine",
            "runtime_fabric_learning_engine",
            "sovereignty_decision_engine",
            "adaptive_sovereign_policy_engine",
            "sovereign_mesh_optimizer",
            "cross_runtime_execution_relay",
            "runtime_recovery_manager",
            "autonomy_governor_v2",
        ],
    )

    lifecycle.define_service(
        "adaptive_operational_strategy_engine",
        dependencies=[
            "sovereign_operational_reasoning_engine",
            "autonomous_execution_cognition_engine",
            "predictive_runtime_stability_engine",
            "runtime_fabric_learning_engine",
            "adaptive_sovereign_policy_engine",
            "sovereign_mesh_optimizer",
            "cross_runtime_execution_relay",
            "runtime_recovery_manager",
            "autonomy_governor_v2",
        ],
    )
    # ========================================================
    # AUTONOMOUS RUNTIME INTELLIGENCE ENGINE
    # ========================================================

    lifecycle.define_service(
        "autonomous_runtime_intelligence_engine",
        dependencies=[
            "runtime_fabric_learning_engine",
            "predictive_runtime_stability_engine",
            "autonomous_execution_cognition_engine",
            "sovereign_operational_reasoning_engine",
            "adaptive_operational_strategy_engine",
            "sovereignty_decision_engine",
            "adaptive_sovereign_policy_engine",
            "sovereign_mesh_optimizer",
            "autonomous_cluster_balancer",
            "cross_runtime_execution_relay",
            "federated_execution_router",
            "sovereign_execution_controller",
            "distributed_runtime_cluster_manager",
            "runtime_federation_manager",
            "runtime_recovery_manager",
            "autonomy_governor_v2",
        ],
    )

    # ========================================================
    # RUNTIME COGNITION ORCHESTRATOR
    # ========================================================

    lifecycle.define_service(
        "runtime_cognition_orchestrator",
        dependencies=[
            "autonomous_runtime_intelligence_engine",
            "runtime_fabric_learning_engine",
            "predictive_runtime_stability_engine",
            "autonomous_execution_cognition_engine",
            "sovereign_operational_reasoning_engine",
            "adaptive_operational_strategy_engine",
            "sovereignty_decision_engine",
            "adaptive_sovereign_policy_engine",
            "runtime_recovery_manager",
            "autonomy_governor_v2",
        ],
    )
    # ========================================================
    # AUTONOMOUS MISSION CONTINUITY ENGINE
    # ========================================================

    lifecycle.define_service(
        "autonomous_mission_continuity_engine",
        dependencies=[
            "runtime_cognition_orchestrator",
            "autonomous_runtime_intelligence_engine",
            "runtime_recovery_manager",
            "runtime_federation_manager",
            "distributed_runtime_cluster_manager",
            "federated_execution_router",
            "sovereign_execution_controller",
            "predictive_runtime_stability_engine",
            "sovereign_operational_reasoning_engine",
            "adaptive_operational_strategy_engine",
            "autonomy_governor_v2",
        ],
    )

    # ========================================================
    # SOVEREIGN OPERATIONAL MEMORY ENGINE
    # ========================================================

    lifecycle.define_service(
        "sovereign_operational_memory_engine",
        dependencies=[
            "autonomous_mission_continuity_engine",
            "runtime_cognition_orchestrator",
            "autonomous_runtime_intelligence_engine",
            "adaptive_operational_strategy_engine",
            "sovereign_operational_reasoning_engine",
            "predictive_runtime_stability_engine",
            "runtime_fabric_learning_engine",
            "runtime_recovery_manager",
        ],
    )




def bootstrap_runtime_cognition(
    *,
    storage: Any,
    registry: Any,
    lifecycle: Any,
    event_bus: Any,
    initialized: Dict[str, Any],
    failed: Dict[str, str],
    reset: bool = False,
    bootstrap_tenant_id: str = "default",
    run_initial_assessments: bool = True,
) -> None:
    """
    Initialize runtime cognition services.

    This function intentionally mutates:
    - storage
    - initialized
    - failed

    so bootstrap_runtime.py can remain the single high-level orchestrator.
    """

    # ========================================================
    # RUNTIME FABRIC LEARNING ENGINE
    # ========================================================

    try:
        runtime_fabric_learning_engine = get_runtime_fabric_learning_engine(
            sovereignty_decision_engine=getattr(
                storage,
                "sovereignty_decision_engine",
                None,
            ),
            adaptive_policy_engine=getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            ),
            mesh_optimizer=getattr(storage, "sovereign_mesh_optimizer", None),
            cluster_balancer=getattr(storage, "autonomous_cluster_balancer", None),
            execution_relay=getattr(storage, "cross_runtime_execution_relay", None),
            federated_router=getattr(storage, "federated_execution_router", None),
            cluster_manager=getattr(
                storage,
                "distributed_runtime_cluster_manager",
                None,
            ),
            domain_manager=getattr(storage, "execution_domain_manager", None),
            recovery_manager=getattr(storage, "runtime_recovery_manager", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.runtime_fabric_learning_engine = runtime_fabric_learning_engine

        registry.register(
            "runtime_fabric_learning_engine",
            runtime_fabric_learning_engine,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "sovereignty_decision_engine",
                "adaptive_sovereign_policy_engine",
                "sovereign_mesh_optimizer",
                "autonomous_cluster_balancer",
                "cross_runtime_execution_relay",
                "federated_execution_router",
                "distributed_runtime_cluster_manager",
                "execution_domain_manager",
                "runtime_recovery_manager",
            ],
        )

        lifecycle.start_service("runtime_fabric_learning_engine")

        initialized["runtime_fabric_learning_engine"] = runtime_fabric_learning_engine

    except Exception as exc:
        failed["runtime_fabric_learning_engine"] = str(exc)

    # ========================================================
    # PREDICTIVE RUNTIME STABILITY ENGINE
    # ========================================================

    try:
        predictive_runtime_stability_engine = get_predictive_runtime_stability_engine(
            learning_engine=getattr(storage, "runtime_fabric_learning_engine", None),
            sovereignty_decision_engine=getattr(
                storage,
                "sovereignty_decision_engine",
                None,
            ),
            adaptive_policy_engine=getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            ),
            mesh_optimizer=getattr(storage, "sovereign_mesh_optimizer", None),
            cluster_balancer=getattr(storage, "autonomous_cluster_balancer", None),
            execution_relay=getattr(storage, "cross_runtime_execution_relay", None),
            federated_router=getattr(storage, "federated_execution_router", None),
            cluster_manager=getattr(
                storage,
                "distributed_runtime_cluster_manager",
                None,
            ),
            domain_manager=getattr(storage, "execution_domain_manager", None),
            federation_manager=getattr(storage, "runtime_federation_manager", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.predictive_runtime_stability_engine = predictive_runtime_stability_engine

        registry.register(
            "predictive_runtime_stability_engine",
            predictive_runtime_stability_engine,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "runtime_fabric_learning_engine",
                "sovereignty_decision_engine",
                "adaptive_sovereign_policy_engine",
                "sovereign_mesh_optimizer",
                "autonomous_cluster_balancer",
                "cross_runtime_execution_relay",
                "federated_execution_router",
                "distributed_runtime_cluster_manager",
                "execution_domain_manager",
                "runtime_federation_manager",
            ],
        )

        lifecycle.start_service("predictive_runtime_stability_engine")

        initialized["predictive_runtime_stability_engine"] = (
            predictive_runtime_stability_engine
        )

    except Exception as exc:
        failed["predictive_runtime_stability_engine"] = str(exc)

    # ========================================================
    # AUTONOMOUS EXECUTION COGNITION ENGINE
    # ========================================================

    try:
        autonomous_execution_cognition_engine = (
            get_autonomous_execution_cognition_engine(
                sovereignty_decision_engine=getattr(
                    storage,
                    "sovereignty_decision_engine",
                    None,
                ),
                predictive_engine=getattr(
                    storage,
                    "predictive_runtime_stability_engine",
                    None,
                ),
                learning_engine=getattr(
                    storage,
                    "runtime_fabric_learning_engine",
                    None,
                ),
                adaptive_policy_engine=getattr(
                    storage,
                    "adaptive_sovereign_policy_engine",
                    None,
                ),
                mesh_optimizer=getattr(storage, "sovereign_mesh_optimizer", None),
                cluster_balancer=getattr(
                    storage,
                    "autonomous_cluster_balancer",
                    None,
                ),
                execution_relay=getattr(
                    storage,
                    "cross_runtime_execution_relay",
                    None,
                ),
                federated_router=getattr(
                    storage,
                    "federated_execution_router",
                    None,
                ),
                sovereign_controller=getattr(
                    storage,
                    "sovereign_execution_controller",
                    None,
                ),
                cluster_manager=getattr(
                    storage,
                    "distributed_runtime_cluster_manager",
                    None,
                ),
                domain_manager=getattr(storage, "execution_domain_manager", None),
                federation_manager=getattr(
                    storage,
                    "runtime_federation_manager",
                    None,
                ),
                recovery_manager=getattr(storage, "runtime_recovery_manager", None),
                autonomy_governor=getattr(storage, "autonomy_governor_v2", None),
                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.autonomous_execution_cognition_engine = (
            autonomous_execution_cognition_engine
        )

        registry.register(
            "autonomous_execution_cognition_engine",
            autonomous_execution_cognition_engine,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "predictive_runtime_stability_engine",
                "runtime_fabric_learning_engine",
                "sovereignty_decision_engine",
                "adaptive_sovereign_policy_engine",
                "sovereign_mesh_optimizer",
                "autonomous_cluster_balancer",
                "cross_runtime_execution_relay",
                "federated_execution_router",
                "sovereign_execution_controller",
                "distributed_runtime_cluster_manager",
                "execution_domain_manager",
                "runtime_federation_manager",
                "runtime_recovery_manager",
                "autonomy_governor_v2",
            ],
        )

        lifecycle.start_service("autonomous_execution_cognition_engine")

        initialized["autonomous_execution_cognition_engine"] = (
            autonomous_execution_cognition_engine
        )

    except Exception as exc:
        failed["autonomous_execution_cognition_engine"] = str(exc)

    # ========================================================
    # SOVEREIGN OPERATIONAL REASONING ENGINE
    # ========================================================

    try:
        sovereign_operational_reasoning_engine = (
            get_sovereign_operational_reasoning_engine(
                execution_cognition_engine=getattr(
                    storage,
                    "autonomous_execution_cognition_engine",
                    None,
                ),
                predictive_engine=getattr(
                    storage,
                    "predictive_runtime_stability_engine",
                    None,
                ),
                learning_engine=getattr(
                    storage,
                    "runtime_fabric_learning_engine",
                    None,
                ),
                sovereignty_decision_engine=getattr(
                    storage,
                    "sovereignty_decision_engine",
                    None,
                ),
                adaptive_policy_engine=getattr(
                    storage,
                    "adaptive_sovereign_policy_engine",
                    None,
                ),
                mesh_optimizer=getattr(storage, "sovereign_mesh_optimizer", None),
                execution_relay=getattr(
                    storage,
                    "cross_runtime_execution_relay",
                    None,
                ),
                autonomy_governor=getattr(storage, "autonomy_governor_v2", None),
                recovery_manager=getattr(storage, "runtime_recovery_manager", None),
                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.sovereign_operational_reasoning_engine = (
            sovereign_operational_reasoning_engine
        )

        registry.register(
            "sovereign_operational_reasoning_engine",
            sovereign_operational_reasoning_engine,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "autonomous_execution_cognition_engine",
                "predictive_runtime_stability_engine",
                "runtime_fabric_learning_engine",
                "sovereignty_decision_engine",
                "adaptive_sovereign_policy_engine",
                "sovereign_mesh_optimizer",
                "cross_runtime_execution_relay",
                "runtime_recovery_manager",
                "autonomy_governor_v2",
            ],
        )

        lifecycle.start_service("sovereign_operational_reasoning_engine")

        initialized["sovereign_operational_reasoning_engine"] = (
            sovereign_operational_reasoning_engine
        )

    except Exception as exc:
        failed["sovereign_operational_reasoning_engine"] = str(exc)

    # ========================================================
    # ADAPTIVE OPERATIONAL STRATEGY ENGINE
    # ========================================================

    try:
        adaptive_operational_strategy_engine = get_adaptive_operational_strategy_engine(
            operational_reasoning_engine=getattr(
                storage,
                "sovereign_operational_reasoning_engine",
                None,
            ),
            execution_cognition_engine=getattr(
                storage,
                "autonomous_execution_cognition_engine",
                None,
            ),
            predictive_engine=getattr(
                storage,
                "predictive_runtime_stability_engine",
                None,
            ),
            learning_engine=getattr(storage, "runtime_fabric_learning_engine", None),
            adaptive_policy_engine=getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            ),
            mesh_optimizer=getattr(storage, "sovereign_mesh_optimizer", None),
            execution_relay=getattr(storage, "cross_runtime_execution_relay", None),
            autonomy_governor=getattr(storage, "autonomy_governor_v2", None),
            recovery_manager=getattr(storage, "runtime_recovery_manager", None),
            storage=storage,
            event_bus=event_bus,
            reset=reset,
        )

        storage.adaptive_operational_strategy_engine = (
            adaptive_operational_strategy_engine
        )

        registry.register(
            "adaptive_operational_strategy_engine",
            adaptive_operational_strategy_engine,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "sovereign_operational_reasoning_engine",
                "autonomous_execution_cognition_engine",
                "predictive_runtime_stability_engine",
                "runtime_fabric_learning_engine",
                "adaptive_sovereign_policy_engine",
                "sovereign_mesh_optimizer",
                "cross_runtime_execution_relay",
                "runtime_recovery_manager",
                "autonomy_governor_v2",
            ],
        )

        lifecycle.start_service("adaptive_operational_strategy_engine")

        initialized["adaptive_operational_strategy_engine"] = (
            adaptive_operational_strategy_engine
        )

    except Exception as exc:
        failed["adaptive_operational_strategy_engine"] = str(exc)

    # ========================================================
    # AUTONOMOUS RUNTIME INTELLIGENCE ENGINE
    # ========================================================

    try:

        autonomous_runtime_intelligence_engine = (
            get_autonomous_runtime_intelligence_engine(

                runtime_fabric_learning_engine=getattr(
                    storage,
                    "runtime_fabric_learning_engine",
                    None,
                ),

                predictive_runtime_stability_engine=getattr(
                    storage,
                    "predictive_runtime_stability_engine",
                    None,
                ),

                autonomous_execution_cognition_engine=getattr(
                    storage,
                    "autonomous_execution_cognition_engine",
                    None,
                ),

                sovereign_operational_reasoning_engine=getattr(
                    storage,
                    "sovereign_operational_reasoning_engine",
                    None,
                ),

                adaptive_operational_strategy_engine=getattr(
                    storage,
                    "adaptive_operational_strategy_engine",
                    None,
                ),

                sovereignty_decision_engine=getattr(
                    storage,
                    "sovereignty_decision_engine",
                    None,
                ),

                adaptive_sovereign_policy_engine=getattr(
                    storage,
                    "adaptive_sovereign_policy_engine",
                    None,
                ),

                sovereign_mesh_optimizer=getattr(
                    storage,
                    "sovereign_mesh_optimizer",
                    None,
                ),

                autonomous_cluster_balancer=getattr(
                    storage,
                    "autonomous_cluster_balancer",
                    None,
                ),

                cross_runtime_execution_relay=getattr(
                    storage,
                    "cross_runtime_execution_relay",
                    None,
                ),

                federated_execution_router=getattr(
                    storage,
                    "federated_execution_router",
                    None,
                ),

                sovereign_execution_controller=getattr(
                    storage,
                    "sovereign_execution_controller",
                    None,
                ),

                distributed_runtime_cluster_manager=getattr(
                    storage,
                    "distributed_runtime_cluster_manager",
                    None,
                ),

                autonomy_governor_v2=getattr(
                    storage,
                    "autonomy_governor_v2",
                    None,
                ),

                runtime_recovery_manager=getattr(
                    storage,
                    "runtime_recovery_manager",
                    None,
                ),

                runtime_health_manager=getattr(
                    storage,
                    "runtime_health_manager",
                    None,
                ),

                runtime_federation_manager=getattr(
                    storage,
                    "runtime_federation_manager",
                    None,
                ),

                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.autonomous_runtime_intelligence_engine = (
            autonomous_runtime_intelligence_engine
        )

        registry.register(
            "autonomous_runtime_intelligence_engine",
            autonomous_runtime_intelligence_engine,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "runtime_fabric_learning_engine",
                "predictive_runtime_stability_engine",
                "autonomous_execution_cognition_engine",
                "sovereign_operational_reasoning_engine",
                "adaptive_operational_strategy_engine",
                "sovereignty_decision_engine",
                "adaptive_sovereign_policy_engine",
            ],
        )

        lifecycle.start_service(
            "autonomous_runtime_intelligence_engine"
        )

        autonomous_runtime_intelligence_engine.start()

        initialized[
            "autonomous_runtime_intelligence_engine"
        ] = autonomous_runtime_intelligence_engine

    except Exception as exc:

        failed[
            "autonomous_runtime_intelligence_engine"
        ] = str(exc)
    # ========================================================
    # RUNTIME COGNITION ORCHESTRATOR
    # ========================================================

    try:

        runtime_cognition_orchestrator = (
            get_runtime_cognition_orchestrator(

                autonomous_runtime_intelligence_engine=getattr(
                    storage,
                    "autonomous_runtime_intelligence_engine",
                    None,
                ),

                runtime_fabric_learning_engine=getattr(
                    storage,
                    "runtime_fabric_learning_engine",
                    None,
                ),

                predictive_runtime_stability_engine=getattr(
                    storage,
                    "predictive_runtime_stability_engine",
                    None,
                ),

                autonomous_execution_cognition_engine=getattr(
                    storage,
                    "autonomous_execution_cognition_engine",
                    None,
                ),

                sovereign_operational_reasoning_engine=getattr(
                    storage,
                    "sovereign_operational_reasoning_engine",
                    None,
                ),

                adaptive_operational_strategy_engine=getattr(
                    storage,
                    "adaptive_operational_strategy_engine",
                    None,
                ),

                sovereignty_decision_engine=getattr(
                    storage,
                    "sovereignty_decision_engine",
                    None,
                ),

                adaptive_sovereign_policy_engine=getattr(
                    storage,
                    "adaptive_sovereign_policy_engine",
                    None,
                ),

                runtime_recovery_manager=getattr(
                    storage,
                    "runtime_recovery_manager",
                    None,
                ),

                autonomy_governor=getattr(
                    storage,
                    "autonomy_governor_v2",
                    None,
                ),

                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.runtime_cognition_orchestrator = (
            runtime_cognition_orchestrator
        )

        registry.register(
            "runtime_cognition_orchestrator",
            runtime_cognition_orchestrator,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "autonomous_runtime_intelligence_engine",
                "runtime_fabric_learning_engine",
                "predictive_runtime_stability_engine",
                "autonomous_execution_cognition_engine",
                "sovereign_operational_reasoning_engine",
                "adaptive_operational_strategy_engine",
                "sovereignty_decision_engine",
                "adaptive_sovereign_policy_engine",
            ],
        )

        lifecycle.start_service(
            "runtime_cognition_orchestrator"
        )

        initialized[
            "runtime_cognition_orchestrator"
        ] = runtime_cognition_orchestrator

    except Exception as exc:

        failed[
            "runtime_cognition_orchestrator"
        ] = str(exc)
    # ========================================================
    # AUTONOMOUS MISSION CONTINUITY ENGINE
    # ========================================================

    try:

        autonomous_mission_continuity_engine = (
            get_autonomous_mission_continuity_engine(

                runtime_cognition_orchestrator=getattr(
                    storage,
                    "runtime_cognition_orchestrator",
                    None,
                ),

                autonomous_runtime_intelligence_engine=getattr(
                    storage,
                    "autonomous_runtime_intelligence_engine",
                    None,
                ),

                runtime_recovery_manager=getattr(
                    storage,
                    "runtime_recovery_manager",
                    None,
                ),

                runtime_federation_manager=getattr(
                    storage,
                    "runtime_federation_manager",
                    None,
                ),

                distributed_runtime_cluster_manager=getattr(
                    storage,
                    "distributed_runtime_cluster_manager",
                    None,
                ),

                federated_execution_router=getattr(
                    storage,
                    "federated_execution_router",
                    None,
                ),

                sovereign_execution_controller=getattr(
                    storage,
                    "sovereign_execution_controller",
                    None,
                ),

                predictive_runtime_stability_engine=getattr(
                    storage,
                    "predictive_runtime_stability_engine",
                    None,
                ),

                sovereign_operational_reasoning_engine=getattr(
                    storage,
                    "sovereign_operational_reasoning_engine",
                    None,
                ),

                adaptive_operational_strategy_engine=getattr(
                    storage,
                    "adaptive_operational_strategy_engine",
                    None,
                ),

                autonomy_governor_v2=getattr(
                    storage,
                    "autonomy_governor_v2",
                    None,
                ),

                storage=storage,
                event_bus=event_bus,
                reset=reset,
            )
        )

        storage.autonomous_mission_continuity_engine = (
            autonomous_mission_continuity_engine
        )

        registry.register(
            "autonomous_mission_continuity_engine",
            autonomous_mission_continuity_engine,
            owner="runtime_cognition_bootstrap",
            dependencies=[
                "runtime_cognition_orchestrator",
                "autonomous_runtime_intelligence_engine",
                "runtime_recovery_manager",
                "runtime_federation_manager",
            ],
        )

        lifecycle.start_service(
            "autonomous_mission_continuity_engine"
        )

        initialized[
            "autonomous_mission_continuity_engine"
        ] = autonomous_mission_continuity_engine

    except Exception as exc:

        failed[
            "autonomous_mission_continuity_engine"
        ] = str(exc)

        # ========================================================
        # SOVEREIGN OPERATIONAL MEMORY ENGINE
        # ========================================================

        try:

            sovereign_operational_memory_engine = (
                get_sovereign_operational_memory_engine(

                    autonomous_mission_continuity_engine=getattr(
                        storage,
                        "autonomous_mission_continuity_engine",
                        None,
                    ),

                    runtime_cognition_orchestrator=getattr(
                        storage,
                        "runtime_cognition_orchestrator",
                        None,
                    ),

                    autonomous_runtime_intelligence_engine=getattr(
                        storage,
                        "autonomous_runtime_intelligence_engine",
                        None,
                    ),

                    adaptive_operational_strategy_engine=getattr(
                        storage,
                        "adaptive_operational_strategy_engine",
                        None,
                    ),

                    sovereign_operational_reasoning_engine=getattr(
                        storage,
                        "sovereign_operational_reasoning_engine",
                        None,
                    ),

                    predictive_runtime_stability_engine=getattr(
                        storage,
                        "predictive_runtime_stability_engine",
                        None,
                    ),

                    runtime_fabric_learning_engine=getattr(
                        storage,
                        "runtime_fabric_learning_engine",
                        None,
                    ),

                    runtime_recovery_manager=getattr(
                        storage,
                        "runtime_recovery_manager",
                        None,
                    ),

                    storage=storage,
                    event_bus=event_bus,
                    reset=reset,
                )
            )

            storage.sovereign_operational_memory_engine = (
                sovereign_operational_memory_engine
            )

            registry.register(
                "sovereign_operational_memory_engine",
                sovereign_operational_memory_engine,
                owner="runtime_cognition_bootstrap",
                dependencies=[
                    "autonomous_mission_continuity_engine",
                    "runtime_cognition_orchestrator",
                    "autonomous_runtime_intelligence_engine",
                ],
            )

            lifecycle.start_service(
                "sovereign_operational_memory_engine"
            )

            initialized[
                "sovereign_operational_memory_engine"
            ] = sovereign_operational_memory_engine

        except Exception as exc:

            failed[
                "sovereign_operational_memory_engine"
            ] = str(exc)


    refresh_runtime_cognition_references(storage=storage)

    if run_initial_assessments:
        run_runtime_cognition_startup_assessments(
            storage=storage,
            tenant_id=bootstrap_tenant_id,
        )


def refresh_runtime_cognition_references(
    *,
    storage: Any,
) -> None:
    """
    Refresh cognition cross references after all cognition services are initialized.
    """

    try:
        if getattr(storage, "runtime_fabric_learning_engine", None) is not None:
            storage.runtime_fabric_learning_engine.sovereignty_decision_engine = getattr(
                storage,
                "sovereignty_decision_engine",
                None,
            )
            storage.runtime_fabric_learning_engine.adaptive_policy_engine = getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            )
            storage.runtime_fabric_learning_engine.mesh_optimizer = getattr(
                storage,
                "sovereign_mesh_optimizer",
                None,
            )
            storage.runtime_fabric_learning_engine.cluster_balancer = getattr(
                storage,
                "autonomous_cluster_balancer",
                None,
            )
            storage.runtime_fabric_learning_engine.execution_relay = getattr(
                storage,
                "cross_runtime_execution_relay",
                None,
            )
            storage.runtime_fabric_learning_engine.federated_router = getattr(
                storage,
                "federated_execution_router",
                None,
            )
            storage.runtime_fabric_learning_engine.cluster_manager = getattr(
                storage,
                "distributed_runtime_cluster_manager",
                None,
            )
            storage.runtime_fabric_learning_engine.domain_manager = getattr(
                storage,
                "execution_domain_manager",
                None,
            )
            storage.runtime_fabric_learning_engine.recovery_manager = getattr(
                storage,
                "runtime_recovery_manager",
                None,
            )
    except Exception:
        pass

    try:
        if getattr(storage, "predictive_runtime_stability_engine", None) is not None:
            storage.predictive_runtime_stability_engine.learning_engine = getattr(
                storage,
                "runtime_fabric_learning_engine",
                None,
            )
            storage.predictive_runtime_stability_engine.sovereignty_decision_engine = getattr(
                storage,
                "sovereignty_decision_engine",
                None,
            )
            storage.predictive_runtime_stability_engine.adaptive_policy_engine = getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            )
            storage.predictive_runtime_stability_engine.mesh_optimizer = getattr(
                storage,
                "sovereign_mesh_optimizer",
                None,
            )
            storage.predictive_runtime_stability_engine.cluster_balancer = getattr(
                storage,
                "autonomous_cluster_balancer",
                None,
            )
            storage.predictive_runtime_stability_engine.execution_relay = getattr(
                storage,
                "cross_runtime_execution_relay",
                None,
            )
            storage.predictive_runtime_stability_engine.federated_router = getattr(
                storage,
                "federated_execution_router",
                None,
            )
            storage.predictive_runtime_stability_engine.cluster_manager = getattr(
                storage,
                "distributed_runtime_cluster_manager",
                None,
            )
            storage.predictive_runtime_stability_engine.domain_manager = getattr(
                storage,
                "execution_domain_manager",
                None,
            )
            storage.predictive_runtime_stability_engine.federation_manager = getattr(
                storage,
                "runtime_federation_manager",
                None,
            )
    except Exception:
        pass

    try:
        if getattr(storage, "autonomous_execution_cognition_engine", None) is not None:
            storage.autonomous_execution_cognition_engine.sovereignty_decision_engine = getattr(
                storage,
                "sovereignty_decision_engine",
                None,
            )
            storage.autonomous_execution_cognition_engine.predictive_engine = getattr(
                storage,
                "predictive_runtime_stability_engine",
                None,
            )
            storage.autonomous_execution_cognition_engine.learning_engine = getattr(
                storage,
                "runtime_fabric_learning_engine",
                None,
            )
            storage.autonomous_execution_cognition_engine.adaptive_policy_engine = getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            )
            storage.autonomous_execution_cognition_engine.mesh_optimizer = getattr(
                storage,
                "sovereign_mesh_optimizer",
                None,
            )
            storage.autonomous_execution_cognition_engine.cluster_balancer = getattr(
                storage,
                "autonomous_cluster_balancer",
                None,
            )
            storage.autonomous_execution_cognition_engine.execution_relay = getattr(
                storage,
                "cross_runtime_execution_relay",
                None,
            )
            storage.autonomous_execution_cognition_engine.federated_router = getattr(
                storage,
                "federated_execution_router",
                None,
            )
            storage.autonomous_execution_cognition_engine.sovereign_controller = getattr(
                storage,
                "sovereign_execution_controller",
                None,
            )
            storage.autonomous_execution_cognition_engine.cluster_manager = getattr(
                storage,
                "distributed_runtime_cluster_manager",
                None,
            )
            storage.autonomous_execution_cognition_engine.domain_manager = getattr(
                storage,
                "execution_domain_manager",
                None,
            )
            storage.autonomous_execution_cognition_engine.federation_manager = getattr(
                storage,
                "runtime_federation_manager",
                None,
            )
            storage.autonomous_execution_cognition_engine.recovery_manager = getattr(
                storage,
                "runtime_recovery_manager",
                None,
            )
            storage.autonomous_execution_cognition_engine.autonomy_governor = getattr(
                storage,
                "autonomy_governor_v2",
                None,
            )
    except Exception:
        pass

    try:
        if getattr(storage, "sovereign_operational_reasoning_engine", None) is not None:
            storage.sovereign_operational_reasoning_engine.execution_cognition_engine = getattr(
                storage,
                "autonomous_execution_cognition_engine",
                None,
            )
            storage.sovereign_operational_reasoning_engine.predictive_engine = getattr(
                storage,
                "predictive_runtime_stability_engine",
                None,
            )
            storage.sovereign_operational_reasoning_engine.learning_engine = getattr(
                storage,
                "runtime_fabric_learning_engine",
                None,
            )
            storage.sovereign_operational_reasoning_engine.sovereignty_decision_engine = getattr(
                storage,
                "sovereignty_decision_engine",
                None,
            )
            storage.sovereign_operational_reasoning_engine.adaptive_policy_engine = getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            )
            storage.sovereign_operational_reasoning_engine.mesh_optimizer = getattr(
                storage,
                "sovereign_mesh_optimizer",
                None,
            )
            storage.sovereign_operational_reasoning_engine.execution_relay = getattr(
                storage,
                "cross_runtime_execution_relay",
                None,
            )
            storage.sovereign_operational_reasoning_engine.autonomy_governor = getattr(
                storage,
                "autonomy_governor_v2",
                None,
            )
            storage.sovereign_operational_reasoning_engine.recovery_manager = getattr(
                storage,
                "runtime_recovery_manager",
                None,
            )
    except Exception:
        pass

    try:
        if getattr(storage, "adaptive_operational_strategy_engine", None) is not None:
            storage.adaptive_operational_strategy_engine.operational_reasoning_engine = getattr(
                storage,
                "sovereign_operational_reasoning_engine",
                None,
            )
            storage.adaptive_operational_strategy_engine.execution_cognition_engine = getattr(
                storage,
                "autonomous_execution_cognition_engine",
                None,
            )
            storage.adaptive_operational_strategy_engine.predictive_engine = getattr(
                storage,
                "predictive_runtime_stability_engine",
                None,
            )
            storage.adaptive_operational_strategy_engine.learning_engine = getattr(
                storage,
                "runtime_fabric_learning_engine",
                None,
            )
            storage.adaptive_operational_strategy_engine.adaptive_policy_engine = getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            )
            storage.adaptive_operational_strategy_engine.mesh_optimizer = getattr(
                storage,
                "sovereign_mesh_optimizer",
                None,
            )
            storage.adaptive_operational_strategy_engine.execution_relay = getattr(
                storage,
                "cross_runtime_execution_relay",
                None,
            )
            storage.adaptive_operational_strategy_engine.autonomy_governor = getattr(
                storage,
                "autonomy_governor_v2",
                None,
            )
            storage.adaptive_operational_strategy_engine.recovery_manager = getattr(
                storage,
                "runtime_recovery_manager",
                None,
            )
    except Exception:
        pass


def run_runtime_cognition_startup_assessments(
    *,
    storage: Any,
    tenant_id: str = "default",
) -> None:
    """
    Run startup ingestion/assessment calls after cognition references are wired.
    These are intentionally best-effort only.
    """

    try:
        if getattr(storage, "runtime_fabric_learning_engine", None) is not None:
            storage.runtime_fabric_learning_engine.ingest_current_state(
                tenant_id=tenant_id,
            )
    except Exception:
        pass

    try:
        if getattr(storage, "predictive_runtime_stability_engine", None) is not None:
            storage.predictive_runtime_stability_engine.assess(
                tenant_id=tenant_id,
            )
    except Exception:
        pass

    try:
        if getattr(storage, "autonomous_execution_cognition_engine", None) is not None:
            storage.autonomous_execution_cognition_engine.assess(
                tenant_id=tenant_id,
                workload={
                    "action": "BOOTSTRAP_RUNTIME_COGNITION",
                    "source": "runtime_cognition_bootstrap",
                },
            )
    except Exception:
        pass

    try:
        if getattr(storage, "sovereign_operational_reasoning_engine", None) is not None:
            storage.sovereign_operational_reasoning_engine.assess(
                tenant_id=tenant_id,
                objective="maintain_sovereign_runtime_operations",
                workload={
                    "action": "BOOTSTRAP_SOVEREIGN_REASONING",
                    "source": "runtime_cognition_bootstrap",
                    "categories": [
                        "CUI",
                        "FEDRAMP_HIGH",
                    ],
                    "continuity_required": True,
                    "sovereignty_required": True,
                    "governance_required": True,
                },
            )
    except Exception:
        pass

    try:
        if getattr(storage, "adaptive_operational_strategy_engine", None) is not None:
            storage.adaptive_operational_strategy_engine.ingest_current_state(
                tenant_id=tenant_id,
            )
    except Exception:
        pass

    try:
        if getattr(storage, "adaptive_operational_strategy_engine", None) is not None:
            storage.adaptive_operational_strategy_engine.assess(
                tenant_id=tenant_id,
                objective="adaptive_sovereign_operational_evolution",
                workload={
                    "action": "BOOTSTRAP_ADAPTIVE_OPERATIONAL_STRATEGY",
                    "source": "runtime_cognition_bootstrap",
                    "categories": [
                        "CUI",
                        "FEDRAMP_HIGH",
                    ],
                },
            )
    except Exception:
        pass