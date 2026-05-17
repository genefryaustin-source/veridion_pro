"""
core/bootstrap/sovereign_runtime_bootstrap.py

Unified Sovereign Runtime Bootstrap

Composition layer that wires together sovereign cognition engines,
governance engines, assurance engines, command-center copilot, and UI-facing
runtime services.

Safe bootstrap module.
Does not execute cyber operations.
Does not mutate infrastructure.
"""

from __future__ import annotations

import time
import uuid

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SovereignRuntime:
    runtime_id: str
    created_at_ms: int

    event_bus: Optional[Any] = None
    storage: Optional[Any] = None

    runtime_cognition_engine: Optional[Any] = None
    simulation_engine: Optional[Any] = None
    forecasting_engine: Optional[Any] = None
    evolution_engine: Optional[Any] = None

    cyber_defense_simulation_mesh: Optional[Any] = None
    campaign_engine: Optional[Any] = None
    battle_management_engine: Optional[Any] = None
    war_gaming_engine: Optional[Any] = None
    resilience_mesh: Optional[Any] = None
    threat_evolution_engine: Optional[Any] = None
    adversarial_reasoning_engine: Optional[Any] = None
    autonomous_defense_director: Optional[Any] = None
    operational_command_mesh: Optional[Any] = None
    operational_governor: Optional[Any] = None
    sovereignty_assurance_engine: Optional[Any] = None
    command_center_copilot: Optional[Any] = None

    operational_memory_engine: Optional[Any] = None
    lineage_engine: Optional[Any] = None
    fedramp_evidence_lineage_engine: Optional[Any] = None
    governance_guardrails_engine: Optional[Any] = None
    execution_verification_mesh: Optional[Any] = None
    telemetry_engine: Optional[Any] = None
    realtime_hub: Optional[Any] = None

    registry: Dict[str, Any] = field(default_factory=dict)
    health: Dict[str, Any] = field(default_factory=dict)

    def get(self, name: str) -> Optional[Any]:
        return self.registry.get(name)

    def has(self, name: str) -> bool:
        return self.registry.get(name) is not None

    def snapshot(self) -> Dict[str, Any]:
        return {
            "runtime_id": self.runtime_id,
            "created_at_ms": self.created_at_ms,
            "engine_count": len(
                [value for value in self.registry.values() if value is not None]
            ),
            "registered_engines": sorted(self.registry.keys()),
            "health": self.health,
        }


def build_sovereign_runtime(
    *,
    storage: Optional[Any] = None,
    event_bus: Optional[Any] = None,
    runtime_cognition_engine: Optional[Any] = None,
    simulation_engine: Optional[Any] = None,
    forecasting_engine: Optional[Any] = None,
    evolution_engine: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
    governance_guardrails_engine: Optional[Any] = None,
    execution_verification_mesh: Optional[Any] = None,
    telemetry_engine: Optional[Any] = None,
    realtime_hub: Optional[Any] = None,
) -> SovereignRuntime:
    cyber_defense_simulation_mesh = _safe_build(
        "cyber_defense_simulation_mesh",
        "core.runtime.sovereign_cyber_defense_simulation_mesh",
        "build_sovereign_cyber_defense_simulation_mesh",
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    campaign_engine = _safe_build(
        "campaign_engine",
        "core.runtime.sovereign_autonomous_campaign_engine",
        "build_sovereign_autonomous_campaign_engine",
        event_bus=event_bus,
        cyber_defense_simulation_mesh=cyber_defense_simulation_mesh,
        runtime_evolution_engine=evolution_engine,
        operational_forecasting_engine=forecasting_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    battle_management_engine = _safe_build(
        "battle_management_engine",
        "core.runtime.sovereign_battle_management_engine",
        "build_sovereign_battle_management_engine",
        event_bus=event_bus,
        campaign_engine=campaign_engine,
        cyber_defense_simulation_mesh=cyber_defense_simulation_mesh,
        runtime_evolution_engine=evolution_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    war_gaming_engine = _safe_build(
        "war_gaming_engine",
        "core.runtime.sovereign_operational_war_gaming_engine",
        "build_sovereign_operational_war_gaming_engine",
        event_bus=event_bus,
        battle_management_engine=battle_management_engine,
        campaign_engine=campaign_engine,
        runtime_evolution_engine=evolution_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    resilience_mesh = _safe_build(
        "resilience_mesh",
        "core.runtime.sovereign_cyber_resilience_mesh",
        "build_sovereign_cyber_resilience_mesh",
        event_bus=event_bus,
        war_gaming_engine=war_gaming_engine,
        battle_management_engine=battle_management_engine,
        digital_twin_engine=None,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    threat_evolution_engine = _safe_build(
        "threat_evolution_engine",
        "core.runtime.sovereign_threat_evolution_engine",
        "build_sovereign_threat_evolution_engine",
        event_bus=event_bus,
        war_gaming_engine=war_gaming_engine,
        resilience_mesh=resilience_mesh,
        battle_management_engine=battle_management_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    adversarial_reasoning_engine = _safe_build(
        "adversarial_reasoning_engine",
        "core.runtime.sovereign_adversarial_reasoning_engine",
        "build_sovereign_adversarial_reasoning_engine",
        event_bus=event_bus,
        threat_evolution_engine=threat_evolution_engine,
        resilience_mesh=resilience_mesh,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    autonomous_defense_director = _safe_build(
        "autonomous_defense_director",
        "core.runtime.sovereign_autonomous_defense_director",
        "build_sovereign_autonomous_defense_director",
        event_bus=event_bus,
        adversarial_reasoning_engine=adversarial_reasoning_engine,
        threat_evolution_engine=threat_evolution_engine,
        resilience_mesh=resilience_mesh,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    operational_command_mesh = _safe_build(
        "operational_command_mesh",
        "core.runtime.sovereign_operational_command_mesh",
        "build_sovereign_operational_command_mesh",
        event_bus=event_bus,
        autonomous_defense_director=autonomous_defense_director,
        adversarial_reasoning_engine=adversarial_reasoning_engine,
        threat_evolution_engine=threat_evolution_engine,
        resilience_mesh=resilience_mesh,
        battle_management_engine=battle_management_engine,
        war_gaming_engine=war_gaming_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    operational_governor = _safe_build(
        "operational_governor",
        "core.runtime.sovereign_autonomous_operational_governor",
        "build_sovereign_autonomous_operational_governor",
        event_bus=event_bus,
        operational_command_mesh=operational_command_mesh,
        autonomous_defense_director=autonomous_defense_director,
        adversarial_reasoning_engine=adversarial_reasoning_engine,
        governance_guardrails_engine=governance_guardrails_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    sovereignty_assurance_engine = _safe_build(
        "sovereignty_assurance_engine",
        "core.runtime.sovereign_sovereignty_assurance_engine",
        "build_sovereign_sovereignty_assurance_engine",
        event_bus=event_bus,
        operational_governor=operational_governor,
        operational_command_mesh=operational_command_mesh,
        autonomous_defense_director=autonomous_defense_director,
        governance_guardrails_engine=governance_guardrails_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
    )

    command_center_copilot = _safe_build(
        "command_center_copilot",
        "core.runtime.sovereign_command_center_copilot",
        "build_sovereign_command_center_copilot",
        event_bus=event_bus,
        runtime_cognition_engine=runtime_cognition_engine,
        simulation_engine=simulation_engine,
        forecasting_engine=forecasting_engine,
        evolution_engine=evolution_engine,
        war_gaming_engine=war_gaming_engine,
        battle_management_engine=battle_management_engine,
        adversarial_reasoning_engine=adversarial_reasoning_engine,
        autonomous_defense_director=autonomous_defense_director,
        operational_governor=operational_governor,
        sovereignty_assurance_engine=sovereignty_assurance_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )

    runtime = SovereignRuntime(
        runtime_id=str(uuid.uuid4()),
        created_at_ms=int(time.time() * 1000),
        event_bus=event_bus,
        storage=storage,
        runtime_cognition_engine=runtime_cognition_engine,
        simulation_engine=simulation_engine,
        forecasting_engine=forecasting_engine,
        evolution_engine=evolution_engine,
        cyber_defense_simulation_mesh=cyber_defense_simulation_mesh,
        campaign_engine=campaign_engine,
        battle_management_engine=battle_management_engine,
        war_gaming_engine=war_gaming_engine,
        resilience_mesh=resilience_mesh,
        threat_evolution_engine=threat_evolution_engine,
        adversarial_reasoning_engine=adversarial_reasoning_engine,
        autonomous_defense_director=autonomous_defense_director,
        operational_command_mesh=operational_command_mesh,
        operational_governor=operational_governor,
        sovereignty_assurance_engine=sovereignty_assurance_engine,
        command_center_copilot=command_center_copilot,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
        governance_guardrails_engine=governance_guardrails_engine,
        execution_verification_mesh=execution_verification_mesh,
        telemetry_engine=telemetry_engine,
        realtime_hub=realtime_hub,
    )

    runtime.registry = _build_registry(runtime)
    runtime.health = _build_health(runtime)

    _emit_bootstrap_event(runtime)

    return runtime


def get_or_create_sovereign_runtime(
    *,
    reset: bool = False,
    **kwargs: Any,
) -> SovereignRuntime:
    global _DEFAULT_SOVEREIGN_RUNTIME

    if reset or _DEFAULT_SOVEREIGN_RUNTIME is None:
        _DEFAULT_SOVEREIGN_RUNTIME = build_sovereign_runtime(**kwargs)

    return _DEFAULT_SOVEREIGN_RUNTIME


_DEFAULT_SOVEREIGN_RUNTIME: Optional[SovereignRuntime] = None


def _safe_build(
    registry_name: str,
    module_path: str,
    builder_name: str,
    **kwargs: Any,
) -> Optional[Any]:
    try:
        module = __import__(module_path, fromlist=[builder_name])
        builder = getattr(module, builder_name)
        return builder(**kwargs)

    except ModuleNotFoundError as exc:
        print(f"⚠️ Sovereign bootstrap skipped {registry_name}: {exc}")
        return None

    except ImportError as exc:
        print(f"⚠️ Sovereign bootstrap import failed for {registry_name}: {exc}")
        return None

    except AttributeError as exc:
        print(f"⚠️ Sovereign bootstrap builder missing for {registry_name}: {exc}")
        return None

    except TypeError as exc:
        print(f"⚠️ Sovereign bootstrap argument mismatch for {registry_name}: {exc}")
        return None

    except Exception as exc:
        print(f"⚠️ Sovereign bootstrap failed for {registry_name}: {exc}")
        return None


def _build_registry(runtime: SovereignRuntime) -> Dict[str, Any]:
    return {
        "runtime_cognition_engine": runtime.runtime_cognition_engine,
        "simulation_engine": runtime.simulation_engine,
        "forecasting_engine": runtime.forecasting_engine,
        "evolution_engine": runtime.evolution_engine,
        "cyber_defense_simulation_mesh": runtime.cyber_defense_simulation_mesh,
        "campaign_engine": runtime.campaign_engine,
        "battle_management_engine": runtime.battle_management_engine,
        "war_gaming_engine": runtime.war_gaming_engine,
        "resilience_mesh": runtime.resilience_mesh,
        "threat_evolution_engine": runtime.threat_evolution_engine,
        "adversarial_reasoning_engine": runtime.adversarial_reasoning_engine,
        "autonomous_defense_director": runtime.autonomous_defense_director,
        "operational_command_mesh": runtime.operational_command_mesh,
        "operational_governor": runtime.operational_governor,
        "sovereignty_assurance_engine": runtime.sovereignty_assurance_engine,
        "command_center_copilot": runtime.command_center_copilot,
        "operational_memory_engine": runtime.operational_memory_engine,
        "lineage_engine": runtime.lineage_engine,
        "fedramp_evidence_lineage_engine": runtime.fedramp_evidence_lineage_engine,
        "governance_guardrails_engine": runtime.governance_guardrails_engine,
        "execution_verification_mesh": runtime.execution_verification_mesh,
        "telemetry_engine": runtime.telemetry_engine,
        "realtime_hub": runtime.realtime_hub,
    }


def _build_health(runtime: SovereignRuntime) -> Dict[str, Any]:
    engines = runtime.registry

    available = {
        name: value is not None
        for name, value in engines.items()
    }

    return {
        "runtime_id": runtime.runtime_id,
        "created_at_ms": runtime.created_at_ms,
        "available": available,
        "available_count": sum(1 for value in available.values() if value),
        "missing_count": sum(1 for value in available.values() if not value),
        "status": "READY" if any(available.values()) else "EMPTY",
    }


def _emit_bootstrap_event(runtime: SovereignRuntime) -> None:
    if runtime.event_bus is None:
        return

    payload = {
        "event_type": "SOVEREIGN_RUNTIME_BOOTSTRAPPED",
        "runtime_id": runtime.runtime_id,
        "created_at_ms": runtime.created_at_ms,
        "health": runtime.health,
    }

    try:
        if hasattr(runtime.event_bus, "emit"):
            runtime.event_bus.emit(
                "SOVEREIGN_RUNTIME_BOOTSTRAPPED",
                payload,
            )
    except Exception as exc:
        print(f"⚠️ Sovereign runtime bootstrap event emit failed: {exc}")