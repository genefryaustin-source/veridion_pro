"""
core/runtime/sovereign_runtime_bootstrap.py

Sovereign Runtime Bootstrap

Unified sovereign runtime composition layer.

This file provides BOTH:

1. build_sovereign_runtime_fabric()
   - Direct builder for the sovereign runtime fabric.

2. define_sovereign_runtime_services()
   bootstrap_sovereign_runtime()
   - Runtime lifecycle integration functions used by:
     core/runtime/runtime_bootstrap.py

This fixes imports like:

from core.runtime.sovereign_runtime_bootstrap import (
    define_sovereign_runtime_services,
    bootstrap_sovereign_runtime,
)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ==========================================================
# CORE SOVEREIGN ENGINE IMPORTS
# ==========================================================

from core.runtime.sovereign_global_command_integrator import (
    build_sovereign_global_command_integrator,
)

from core.runtime.sovereign_global_risk_forecasting_engine import (
    build_sovereign_global_risk_forecasting_engine,
)

from core.runtime.sovereign_strategic_synthesis_engine import (
    build_sovereign_strategic_synthesis_engine,
)

from core.runtime.sovereign_executive_decision_engine import (
    build_sovereign_executive_decision_engine,
)

from core.runtime.sovereign_autonomous_orchestration_engine import (
    build_sovereign_autonomous_orchestration_engine,
)

from core.runtime.sovereign_execution_governance_engine import (
    build_sovereign_execution_governance_engine,
)

from core.runtime.sovereign_execution_verification_engine import (
    build_sovereign_execution_verification_engine,
)

from core.runtime.sovereign_adaptive_learning_engine import (
    build_sovereign_adaptive_learning_engine,
)

from core.runtime.sovereign_policy_evolution_engine import (
    build_sovereign_policy_evolution_engine,
)


# ==========================================================
# OPTIONAL NEWER RUNTIME ENGINES
# ==========================================================

try:
    from core.runtime.sovereign_runtime_telemetry_bus import (
        build_sovereign_runtime_telemetry_bus,
    )
except Exception:
    build_sovereign_runtime_telemetry_bus = None


try:
    from core.runtime.sovereign_live_runtime_state_engine import (
        build_sovereign_live_runtime_state_engine,
    )
except Exception:
    build_sovereign_live_runtime_state_engine = None


try:
    from core.runtime.sovereign_cross_fabric_coordination_engine import (
        build_sovereign_cross_fabric_coordination_engine,
    )
except Exception:
    build_sovereign_cross_fabric_coordination_engine = None


# ==========================================================
# OPTIONAL SUPPORTING ENGINES
# ==========================================================

try:
    from core.ai.orchestration.orchestration_memory import (
        build_orchestration_memory,
    )
except Exception:
    build_orchestration_memory = None


# ==========================================================
# SERVICE NAMES
# ==========================================================

SVC_SOVEREIGN_RUNTIME_FABRIC = "sovereign_runtime_fabric"

SVC_SOVEREIGN_GLOBAL_COMMAND_INTEGRATOR = (
    "sovereign_global_command_integrator"
)

SVC_SOVEREIGN_GLOBAL_RISK_FORECASTING_ENGINE = (
    "sovereign_global_risk_forecasting_engine"
)

SVC_SOVEREIGN_STRATEGIC_SYNTHESIS_ENGINE = (
    "sovereign_strategic_synthesis_engine"
)

SVC_SOVEREIGN_EXECUTIVE_DECISION_ENGINE = (
    "sovereign_executive_decision_engine"
)

SVC_SOVEREIGN_AUTONOMOUS_ORCHESTRATION_ENGINE = (
    "sovereign_autonomous_orchestration_engine"
)

SVC_SOVEREIGN_EXECUTION_GOVERNANCE_ENGINE = (
    "sovereign_execution_governance_engine"
)

SVC_SOVEREIGN_EXECUTION_VERIFICATION_ENGINE = (
    "sovereign_execution_verification_engine"
)

SVC_SOVEREIGN_ADAPTIVE_LEARNING_ENGINE = (
    "sovereign_adaptive_learning_engine"
)

SVC_SOVEREIGN_POLICY_EVOLUTION_ENGINE = (
    "sovereign_policy_evolution_engine"
)

SVC_SOVEREIGN_RUNTIME_TELEMETRY_BUS = (
    "sovereign_runtime_telemetry_bus"
)

SVC_SOVEREIGN_LIVE_RUNTIME_STATE_ENGINE = (
    "sovereign_live_runtime_state_engine"
)

SVC_SOVEREIGN_CROSS_FABRIC_COORDINATION_ENGINE = (
    "sovereign_cross_fabric_coordination_engine"
)


# ==========================================================
# RUNTIME FABRIC DATACLASS
# ==========================================================

@dataclass
class SovereignRuntimeFabric:
    event_bus: Optional[Any] = None

    operational_memory_engine: Optional[Any] = None
    lineage_engine: Optional[Any] = None
    fedramp_evidence_lineage_engine: Optional[Any] = None

    sovereign_global_command_integrator: Optional[Any] = None
    sovereign_global_risk_forecasting_engine: Optional[Any] = None
    sovereign_strategic_synthesis_engine: Optional[Any] = None
    sovereign_executive_decision_engine: Optional[Any] = None
    sovereign_autonomous_orchestration_engine: Optional[Any] = None
    sovereign_execution_governance_engine: Optional[Any] = None
    sovereign_execution_verification_engine: Optional[Any] = None
    sovereign_adaptive_learning_engine: Optional[Any] = None
    sovereign_policy_evolution_engine: Optional[Any] = None

    sovereign_runtime_telemetry_bus: Optional[Any] = None
    sovereign_live_runtime_state_engine: Optional[Any] = None
    sovereign_cross_fabric_coordination_engine: Optional[Any] = None

    metadata: Optional[Dict[str, Any]] = None


# ==========================================================
# LIFECYCLE SERVICE DEFINITIONS
# ==========================================================

def define_sovereign_runtime_services(
    *,
    lifecycle: Any,
) -> None:
    """
    Defines sovereign runtime services inside the runtime lifecycle manager.

    This function is called by core/runtime/runtime_bootstrap.py before
    bootstrap_sovereign_runtime() initializes the concrete engine objects.
    """

    try:
        lifecycle.define_service(SVC_SOVEREIGN_RUNTIME_FABRIC)
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_GLOBAL_COMMAND_INTEGRATOR,
            dependencies=[
                SVC_SOVEREIGN_RUNTIME_FABRIC,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_GLOBAL_RISK_FORECASTING_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_GLOBAL_COMMAND_INTEGRATOR,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_STRATEGIC_SYNTHESIS_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_GLOBAL_RISK_FORECASTING_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_EXECUTIVE_DECISION_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_STRATEGIC_SYNTHESIS_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_AUTONOMOUS_ORCHESTRATION_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_EXECUTIVE_DECISION_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_EXECUTION_GOVERNANCE_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_AUTONOMOUS_ORCHESTRATION_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_EXECUTION_VERIFICATION_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_EXECUTION_GOVERNANCE_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_ADAPTIVE_LEARNING_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_EXECUTION_VERIFICATION_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_POLICY_EVOLUTION_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_ADAPTIVE_LEARNING_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_RUNTIME_TELEMETRY_BUS,
            dependencies=[
                SVC_SOVEREIGN_POLICY_EVOLUTION_ENGINE,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_LIVE_RUNTIME_STATE_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_RUNTIME_TELEMETRY_BUS,
            ],
        )
    except Exception:
        pass

    try:
        lifecycle.define_service(
            SVC_SOVEREIGN_CROSS_FABRIC_COORDINATION_ENGINE,
            dependencies=[
                SVC_SOVEREIGN_LIVE_RUNTIME_STATE_ENGINE,
            ],
        )
    except Exception:
        pass


# ==========================================================
# DIRECT FABRIC BUILDER
# ==========================================================

def build_sovereign_runtime_fabric(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> SovereignRuntimeFabric:
    """
    Builds the sovereign runtime fabric directly.

    This is useful for standalone bootstrapping or UI/demo wiring.
    """

    print("🚀 Building Sovereign Runtime Fabric...")

    # ======================================================
    # MEMORY
    # ======================================================

    if operational_memory_engine is None and build_orchestration_memory:
        try:
            operational_memory_engine = build_orchestration_memory()
            print("🧠 Operational memory initialized.")
        except Exception as exc:
            print(
                f"⚠️ Failed to initialize operational memory: {exc}"
            )

    # ======================================================
    # GLOBAL COMMAND
    # ======================================================

    sovereign_global_command_integrator = (
        build_sovereign_global_command_integrator(
            event_bus=event_bus,
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("🌍 Sovereign Global Command Integrator initialized.")

    # ======================================================
    # GLOBAL RISK FORECASTING
    # ======================================================

    sovereign_global_risk_forecasting_engine = (
        build_sovereign_global_risk_forecasting_engine(
            event_bus=event_bus,
            global_command_integrator=(
                sovereign_global_command_integrator
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("📈 Sovereign Global Risk Forecasting initialized.")

    # ======================================================
    # STRATEGIC SYNTHESIS
    # ======================================================

    sovereign_strategic_synthesis_engine = (
        build_sovereign_strategic_synthesis_engine(
            event_bus=event_bus,
            global_risk_forecasting_engine=(
                sovereign_global_risk_forecasting_engine
            ),
            global_command_integrator=(
                sovereign_global_command_integrator
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("🧠 Sovereign Strategic Synthesis initialized.")

    # ======================================================
    # EXECUTIVE DECISION
    # ======================================================

    sovereign_executive_decision_engine = (
        build_sovereign_executive_decision_engine(
            event_bus=event_bus,
            strategic_synthesis_engine=(
                sovereign_strategic_synthesis_engine
            ),
            global_risk_forecasting_engine=(
                sovereign_global_risk_forecasting_engine
            ),
            global_command_integrator=(
                sovereign_global_command_integrator
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("👑 Sovereign Executive Decision Engine initialized.")

    # ======================================================
    # AUTONOMOUS ORCHESTRATION
    # ======================================================

    sovereign_autonomous_orchestration_engine = (
        build_sovereign_autonomous_orchestration_engine(
            event_bus=event_bus,
            executive_decision_engine=(
                sovereign_executive_decision_engine
            ),
            strategic_synthesis_engine=(
                sovereign_strategic_synthesis_engine
            ),
            global_risk_forecasting_engine=(
                sovereign_global_risk_forecasting_engine
            ),
            global_command_integrator=(
                sovereign_global_command_integrator
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("🛰️ Sovereign Autonomous Orchestration initialized.")

    # ======================================================
    # EXECUTION GOVERNANCE
    # ======================================================

    sovereign_execution_governance_engine = (
        build_sovereign_execution_governance_engine(
            event_bus=event_bus,
            autonomous_orchestration_engine=(
                sovereign_autonomous_orchestration_engine
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("🛡️ Sovereign Execution Governance initialized.")

    # ======================================================
    # EXECUTION VERIFICATION
    # ======================================================

    sovereign_execution_verification_engine = (
        build_sovereign_execution_verification_engine(
            event_bus=event_bus,
            execution_governance_engine=(
                sovereign_execution_governance_engine
            ),
            orchestration_engine=(
                sovereign_autonomous_orchestration_engine
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("✅ Sovereign Execution Verification initialized.")

    # ======================================================
    # ADAPTIVE LEARNING
    # ======================================================

    sovereign_adaptive_learning_engine = (
        build_sovereign_adaptive_learning_engine(
            event_bus=event_bus,
            execution_verification_engine=(
                sovereign_execution_verification_engine
            ),
            execution_governance_engine=(
                sovereign_execution_governance_engine
            ),
            orchestration_engine=(
                sovereign_autonomous_orchestration_engine
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("📚 Sovereign Adaptive Learning initialized.")

    # ======================================================
    # POLICY EVOLUTION
    # ======================================================

    sovereign_policy_evolution_engine = (
        build_sovereign_policy_evolution_engine(
            event_bus=event_bus,
            adaptive_learning_engine=(
                sovereign_adaptive_learning_engine
            ),
            execution_governance_engine=(
                sovereign_execution_governance_engine
            ),
            execution_verification_engine=(
                sovereign_execution_verification_engine
            ),
            operational_memory_engine=operational_memory_engine,
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )

    print("⚙️ Sovereign Policy Evolution initialized.")

    # ======================================================
    # OPTIONAL TELEMETRY BUS
    # ======================================================

    sovereign_runtime_telemetry_bus = None

    if build_sovereign_runtime_telemetry_bus:
        try:
            sovereign_runtime_telemetry_bus = (
                build_sovereign_runtime_telemetry_bus(
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    lineage_engine=lineage_engine,
                    fedramp_evidence_lineage_engine=(
                        fedramp_evidence_lineage_engine
                    ),
                )
            )

            print("📡 Sovereign Runtime Telemetry Bus initialized.")

        except Exception as exc:
            print(
                f"⚠️ Sovereign Runtime Telemetry Bus failed: {exc}"
            )

    # ======================================================
    # OPTIONAL LIVE RUNTIME STATE
    # ======================================================

    sovereign_live_runtime_state_engine = None

    if build_sovereign_live_runtime_state_engine:
        try:
            sovereign_live_runtime_state_engine = (
                build_sovereign_live_runtime_state_engine(
                    telemetry_bus=sovereign_runtime_telemetry_bus,
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    lineage_engine=lineage_engine,
                    fedramp_evidence_lineage_engine=(
                        fedramp_evidence_lineage_engine
                    ),
                )
            )

            print("🧬 Sovereign Live Runtime State initialized.")

        except Exception as exc:
            print(
                f"⚠️ Sovereign Live Runtime State failed: {exc}"
            )

    # ======================================================
    # OPTIONAL CROSS-FABRIC COORDINATION
    # ======================================================

    sovereign_cross_fabric_coordination_engine = None

    if build_sovereign_cross_fabric_coordination_engine:
        try:
            sovereign_cross_fabric_coordination_engine = (
                build_sovereign_cross_fabric_coordination_engine(
                    telemetry_bus=sovereign_runtime_telemetry_bus,
                    live_runtime_state_engine=(
                        sovereign_live_runtime_state_engine
                    ),
                    policy_evolution_engine=(
                        sovereign_policy_evolution_engine
                    ),
                    adaptive_learning_engine=(
                        sovereign_adaptive_learning_engine
                    ),
                    execution_governance_engine=(
                        sovereign_execution_governance_engine
                    ),
                    event_bus=event_bus,
                    operational_memory_engine=(
                        operational_memory_engine
                    ),
                    lineage_engine=lineage_engine,
                    fedramp_evidence_lineage_engine=(
                        fedramp_evidence_lineage_engine
                    ),
                )
            )

            print("🛰️ Sovereign Cross-Fabric Coordination initialized.")

        except Exception as exc:
            print(
                f"⚠️ Sovereign Cross-Fabric Coordination failed: {exc}"
            )

    # ======================================================
    # FABRIC
    # ======================================================

    fabric = SovereignRuntimeFabric(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=(
            fedramp_evidence_lineage_engine
        ),
        sovereign_global_command_integrator=(
            sovereign_global_command_integrator
        ),
        sovereign_global_risk_forecasting_engine=(
            sovereign_global_risk_forecasting_engine
        ),
        sovereign_strategic_synthesis_engine=(
            sovereign_strategic_synthesis_engine
        ),
        sovereign_executive_decision_engine=(
            sovereign_executive_decision_engine
        ),
        sovereign_autonomous_orchestration_engine=(
            sovereign_autonomous_orchestration_engine
        ),
        sovereign_execution_governance_engine=(
            sovereign_execution_governance_engine
        ),
        sovereign_execution_verification_engine=(
            sovereign_execution_verification_engine
        ),
        sovereign_adaptive_learning_engine=(
            sovereign_adaptive_learning_engine
        ),
        sovereign_policy_evolution_engine=(
            sovereign_policy_evolution_engine
        ),
        sovereign_runtime_telemetry_bus=(
            sovereign_runtime_telemetry_bus
        ),
        sovereign_live_runtime_state_engine=(
            sovereign_live_runtime_state_engine
        ),
        sovereign_cross_fabric_coordination_engine=(
            sovereign_cross_fabric_coordination_engine
        ),
        metadata={
            "runtime_type": "SOVEREIGN_RUNTIME_FABRIC",
            "runtime_generation": "GEN-2",
            "capabilities": [
                "global_command",
                "global_forecasting",
                "strategic_synthesis",
                "executive_decision",
                "autonomous_orchestration",
                "execution_governance",
                "execution_verification",
                "adaptive_learning",
                "policy_evolution",
                "runtime_telemetry_bus",
                "live_runtime_state",
                "cross_fabric_coordination",
            ],
        },
    )

    print("🌐 Sovereign Runtime Fabric ONLINE.")

    return fabric


# ==========================================================
# RUNTIME BOOTSTRAP INTEGRATION
# ==========================================================

def bootstrap_sovereign_runtime(
    *,
    storage: Any,
    registry: Any,
    lifecycle: Any,
    event_bus: Any,
    initialized: Dict[str, Any],
    failed: Dict[str, str],
    reset: bool = False,
) -> Optional[SovereignRuntimeFabric]:
    """
    Initializes sovereign runtime services and attaches them to storage.

    This function is called by core/runtime/runtime_bootstrap.py.
    """

    try:
        fabric = build_sovereign_runtime_fabric(
            event_bus=event_bus,
            operational_memory_engine=getattr(
                storage,
                "operational_memory_engine",
                None,
            ),
            lineage_engine=getattr(
                storage,
                "lineage_engine",
                None,
            ),
            fedramp_evidence_lineage_engine=getattr(
                storage,
                "fedramp_evidence_lineage_engine",
                None,
            ),
        )

        # --------------------------------------------------
        # Attach fabric
        # --------------------------------------------------

        storage.runtime_fabric = fabric
        storage.sovereign_runtime_fabric = fabric

        initialized[SVC_SOVEREIGN_RUNTIME_FABRIC] = fabric

        try:
            registry.register(
                SVC_SOVEREIGN_RUNTIME_FABRIC,
                fabric,
                owner="sovereign_runtime_bootstrap",
                metadata=fabric.metadata or {},
            )
        except Exception:
            pass

        try:
            lifecycle.start_service(
                SVC_SOVEREIGN_RUNTIME_FABRIC
            )
        except Exception:
            pass

        # --------------------------------------------------
        # Attach individual engines
        # --------------------------------------------------

        service_map = {
            SVC_SOVEREIGN_GLOBAL_COMMAND_INTEGRATOR:
                fabric.sovereign_global_command_integrator,

            SVC_SOVEREIGN_GLOBAL_RISK_FORECASTING_ENGINE:
                fabric.sovereign_global_risk_forecasting_engine,

            SVC_SOVEREIGN_STRATEGIC_SYNTHESIS_ENGINE:
                fabric.sovereign_strategic_synthesis_engine,

            SVC_SOVEREIGN_EXECUTIVE_DECISION_ENGINE:
                fabric.sovereign_executive_decision_engine,

            SVC_SOVEREIGN_AUTONOMOUS_ORCHESTRATION_ENGINE:
                fabric.sovereign_autonomous_orchestration_engine,

            SVC_SOVEREIGN_EXECUTION_GOVERNANCE_ENGINE:
                fabric.sovereign_execution_governance_engine,

            SVC_SOVEREIGN_EXECUTION_VERIFICATION_ENGINE:
                fabric.sovereign_execution_verification_engine,

            SVC_SOVEREIGN_ADAPTIVE_LEARNING_ENGINE:
                fabric.sovereign_adaptive_learning_engine,

            SVC_SOVEREIGN_POLICY_EVOLUTION_ENGINE:
                fabric.sovereign_policy_evolution_engine,

            SVC_SOVEREIGN_RUNTIME_TELEMETRY_BUS:
                fabric.sovereign_runtime_telemetry_bus,

            SVC_SOVEREIGN_LIVE_RUNTIME_STATE_ENGINE:
                fabric.sovereign_live_runtime_state_engine,

            SVC_SOVEREIGN_CROSS_FABRIC_COORDINATION_ENGINE:
                fabric.sovereign_cross_fabric_coordination_engine,
        }

        for service_name, service_obj in service_map.items():
            if service_obj is None:
                continue

            setattr(storage, service_name, service_obj)
            initialized[service_name] = service_obj

            try:
                registry.register(
                    service_name,
                    service_obj,
                    owner="sovereign_runtime_bootstrap",
                    dependencies=[
                        SVC_SOVEREIGN_RUNTIME_FABRIC,
                    ],
                )
            except Exception:
                pass

            try:
                lifecycle.start_service(service_name)
            except Exception:
                pass

        print("✅ Sovereign runtime bootstrap completed.")

        return fabric

    except Exception as exc:
        failed["sovereign_runtime_bootstrap"] = str(exc)

        print(
            f"❌ Sovereign runtime bootstrap failed: {exc}"
        )

        return None