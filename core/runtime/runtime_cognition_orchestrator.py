"""
core/runtime/runtime_cognition_orchestrator.py

Runtime Cognition Orchestrator.

Purpose:
- cognition coordination and orchestration layer
- deterministic cognition pipelines
- mission-aware cognition routing
- cognition rate control
- cognition storm prevention
- runtime cognition telemetry

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no direct destructive runtime actions
- recommendation / orchestration first
- explicit dependency injection
"""

from __future__ import annotations

import time
import uuid

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from typing import (
    Any,
    Dict,
    List,
    Optional,
)


DEFAULT_TENANT = "default"

COGNITION_LOW = "LOW"
COGNITION_MEDIUM = "MEDIUM"
COGNITION_HIGH = "HIGH"
COGNITION_CRITICAL = "CRITICAL"

PLAN_PENDING = "PENDING"
PLAN_RUNNING = "RUNNING"
PLAN_COMPLETED = "COMPLETED"
PLAN_FAILED = "FAILED"
PLAN_SKIPPED = "SKIPPED"
PLAN_RATE_LIMITED = "RATE_LIMITED"

STEP_PENDING = "PENDING"
STEP_RUNNING = "RUNNING"
STEP_COMPLETED = "COMPLETED"
STEP_FAILED = "FAILED"
STEP_SKIPPED = "SKIPPED"

COGNITION_MODE_NORMAL = "NORMAL"
COGNITION_MODE_CONSERVATIVE = "CONSERVATIVE"
COGNITION_MODE_CONTINUITY = "CONTINUITY"
COGNITION_MODE_LOCKDOWN = "LOCKDOWN"


def _now_ms() -> int:
    return int(time.time() * 1000)


# =========================================================
# MODELS
# =========================================================

@dataclass
class CognitionStep:

    step_id: str

    engine_name: str

    action: str

    priority: str = COGNITION_MEDIUM

    status: str = STEP_PENDING

    started_at_ms: Optional[int] = None

    completed_at_ms: Optional[int] = None

    result: Dict[str, Any] = field(default_factory=dict)

    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CognitionPlan:

    plan_id: str

    tenant_id: str

    trigger: str

    mode: str

    priority: str

    status: str = PLAN_PENDING

    workload: Dict[str, Any] = field(default_factory=dict)

    steps: List[CognitionStep] = field(default_factory=list)

    telemetry: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=_now_ms)

    started_at_ms: Optional[int] = None

    completed_at_ms: Optional[int] = None

    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:

        data = asdict(self)

        data["steps"] = [
            s.to_dict()
            if hasattr(s, "to_dict")
            else s
            for s in self.steps
        ]

        return data


@dataclass
class CognitionOrchestrationStatus:

    tenant_id: str

    mode: str

    active_plans: int

    completed_plans: int

    failed_plans: int

    rate_limited_plans: int

    last_plan_id: Optional[str] = None

    last_updated_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =========================================================
# ORCHESTRATOR
# =========================================================

class RuntimeCognitionOrchestrator:

    """
    Coordinates cognition execution across:
    - learning
    - prediction
    - reasoning
    - strategy
    - sovereignty
    - continuity
    - runtime intelligence
    """

    def __init__(
        self,

        autonomous_runtime_intelligence_engine: Any = None,

        runtime_fabric_learning_engine: Any = None,

        predictive_runtime_stability_engine: Any = None,

        autonomous_execution_cognition_engine: Any = None,

        sovereign_operational_reasoning_engine: Any = None,

        adaptive_operational_strategy_engine: Any = None,

        sovereignty_decision_engine: Any = None,

        adaptive_sovereign_policy_engine: Any = None,

        runtime_recovery_manager: Any = None,

        autonomy_governor: Any = None,

        storage: Any = None,

        event_bus: Any = None,

        min_plan_interval_ms: int = 10_000,

        max_steps_per_plan: int = 8,
    ):

        self.storage = storage

        self.event_bus = event_bus

        self.autonomous_runtime_intelligence_engine = (
            autonomous_runtime_intelligence_engine
            or getattr(
                storage,
                "autonomous_runtime_intelligence_engine",
                None,
            )
        )

        self.runtime_fabric_learning_engine = (
            runtime_fabric_learning_engine
            or getattr(
                storage,
                "runtime_fabric_learning_engine",
                None,
            )
        )

        self.predictive_runtime_stability_engine = (
            predictive_runtime_stability_engine
            or getattr(
                storage,
                "predictive_runtime_stability_engine",
                None,
            )
        )

        self.autonomous_execution_cognition_engine = (
            autonomous_execution_cognition_engine
            or getattr(
                storage,
                "autonomous_execution_cognition_engine",
                None,
            )
        )

        self.sovereign_operational_reasoning_engine = (
            sovereign_operational_reasoning_engine
            or getattr(
                storage,
                "sovereign_operational_reasoning_engine",
                None,
            )
        )

        self.adaptive_operational_strategy_engine = (
            adaptive_operational_strategy_engine
            or getattr(
                storage,
                "adaptive_operational_strategy_engine",
                None,
            )
        )

        self.sovereignty_decision_engine = (
            sovereignty_decision_engine
            or getattr(
                storage,
                "sovereignty_decision_engine",
                None,
            )
        )

        self.adaptive_sovereign_policy_engine = (
            adaptive_sovereign_policy_engine
            or getattr(
                storage,
                "adaptive_sovereign_policy_engine",
                None,
            )
        )

        self.runtime_recovery_manager = (
            runtime_recovery_manager
            or getattr(
                storage,
                "runtime_recovery_manager",
                None,
            )
        )

        self.autonomy_governor = (
            autonomy_governor
            or getattr(
                storage,
                "autonomy_governor_v2",
                None,
            )
        )

        self.min_plan_interval_ms = int(
            min_plan_interval_ms
        )

        self.max_steps_per_plan = int(
            max_steps_per_plan
        )

        self._plans: List[
            CognitionPlan
        ] = []

        self._last_plan_at_ms: Dict[
            str,
            int,
        ] = {}

        self._status_by_tenant: Dict[
            str,
            CognitionOrchestrationStatus,
        ] = {}

        self._register_event_handlers()

    # =====================================================
    # PUBLIC API
    # =====================================================

    def orchestrate(
        self,

        tenant_id: str = DEFAULT_TENANT,

        trigger: str = "manual",

        workload: Optional[
            Dict[str, Any]
        ] = None,

        priority: str = COGNITION_MEDIUM,

        force: bool = False,
    ) -> CognitionPlan:

        workload = dict(workload or {})

        mode = self._derive_mode(
            tenant_id=tenant_id,
            workload=workload,
            priority=priority,
        )

        if (
            not force
            and self._is_rate_limited(
                tenant_id
            )
        ):

            plan = CognitionPlan(
                plan_id=(
                    f"COG-PLAN-"
                    f"{uuid.uuid4().hex[:12].upper()}"
                ),
                tenant_id=tenant_id,
                trigger=trigger,
                mode=mode,
                priority=priority,
                status=PLAN_RATE_LIMITED,
                workload=workload,
                telemetry={
                    "reason": (
                        "min_plan_interval_not_elapsed"
                    ),
                    "min_plan_interval_ms": (
                        self.min_plan_interval_ms
                    ),
                },
            )

            self._plans.append(plan)

            self._trim()

            self._update_status(
                tenant_id=tenant_id,
                last_plan_id=plan.plan_id,
            )

            return plan

        plan = self._build_plan(
            tenant_id=tenant_id,
            trigger=trigger,
            workload=workload,
            priority=priority,
            mode=mode,
        )

        self._plans.append(plan)

        self._trim()

        self._execute_plan(plan)

        self._last_plan_at_ms[
            tenant_id
        ] = _now_ms()

        self._update_status(
            tenant_id=tenant_id,
            last_plan_id=plan.plan_id,
        )

        return plan

    def orchestrate_continuity_mode(
        self,

        tenant_id: str = DEFAULT_TENANT,

        trigger: str = "continuity_mode",

        workload: Optional[
            Dict[str, Any]
        ] = None,

        force: bool = True,
    ) -> CognitionPlan:

        data = dict(workload or {})

        data["continuity_required"] = True

        data["mission_priority"] = (
            COGNITION_CRITICAL
        )

        return self.orchestrate(
            tenant_id=tenant_id,
            trigger=trigger,
            workload=data,
            priority=COGNITION_CRITICAL,
            force=force,
        )

    def orchestrate_sovereign_review(
        self,

        tenant_id: str = DEFAULT_TENANT,

        trigger: str = "sovereign_review",

        workload: Optional[
            Dict[str, Any]
        ] = None,

        force: bool = False,
    ) -> CognitionPlan:

        data = dict(workload or {})

        data["sovereignty_required"] = True

        data.setdefault(
            "categories",
            ["CUI"],
        )

        return self.orchestrate(
            tenant_id=tenant_id,
            trigger=trigger,
            workload=data,
            priority=COGNITION_HIGH,
            force=force,
        )

    # =====================================================
    # PLAN BUILDING
    # =====================================================

    def _build_plan(
        self,

        tenant_id: str,

        trigger: str,

        workload: Dict[str, Any],

        priority: str,

        mode: str,
    ) -> CognitionPlan:

        steps: List[
            CognitionStep
        ] = []

        def add(
            engine_name: str,
            action: str,
            step_priority: str,
        ) -> None:

            if (
                len(steps)
                >= self.max_steps_per_plan
            ):
                return

            steps.append(
                CognitionStep(
                    step_id=(
                        f"COG-STEP-"
                        f"{uuid.uuid4().hex[:12].upper()}"
                    ),
                    engine_name=engine_name,
                    action=action,
                    priority=step_priority,
                )
            )

        add(
            "runtime_fabric_learning_engine",
            "ingest_current_state",
            COGNITION_MEDIUM,
        )

        add(
            "predictive_runtime_stability_engine",
            "assess",
            COGNITION_MEDIUM,
        )

        if mode in {
            COGNITION_MODE_NORMAL,
            COGNITION_MODE_CONSERVATIVE,
            COGNITION_MODE_CONTINUITY,
            COGNITION_MODE_LOCKDOWN,
        }:

            add(
                "autonomous_execution_cognition_engine",
                "assess",
                COGNITION_HIGH,
            )

        if mode in {
            COGNITION_MODE_CONSERVATIVE,
            COGNITION_MODE_CONTINUITY,
            COGNITION_MODE_LOCKDOWN,
        }:

            add(
                "sovereignty_decision_engine",
                "assess",
                COGNITION_HIGH,
            )

            add(
                "adaptive_sovereign_policy_engine",
                "assess",
                COGNITION_HIGH,
            )

        add(
            "sovereign_operational_reasoning_engine",
            "assess",
            COGNITION_HIGH,
        )

        add(
            "adaptive_operational_strategy_engine",
            "assess",
            COGNITION_HIGH,
        )

        add(
            "autonomous_runtime_intelligence_engine",
            "synthesize",
            COGNITION_HIGH,
        )

        if (
            mode
            == COGNITION_MODE_LOCKDOWN
        ):

            add(
                "runtime_recovery_manager",
                "auto_recover",
                COGNITION_CRITICAL,
            )

        return CognitionPlan(
            plan_id=(
                f"COG-PLAN-"
                f"{uuid.uuid4().hex[:12].upper()}"
            ),
            tenant_id=tenant_id,
            trigger=trigger,
            mode=mode,
            priority=priority,
            workload=workload,
            steps=steps,
            telemetry={
                "step_count": len(steps),
                "created_by": (
                    "runtime_cognition_orchestrator"
                ),
            },
        )

    # =====================================================
    # MODE DERIVATION
    # =====================================================

    def _derive_mode(
        self,

        tenant_id: str,

        workload: Dict[str, Any],

        priority: str,
    ) -> str:

        categories = {
            str(c).upper()
            for c in workload.get(
                "categories",
                [],
            )
        }

        if (
            priority
            == COGNITION_CRITICAL
        ):
            return COGNITION_MODE_LOCKDOWN

        if (
            workload.get(
                "continuity_required"
            )
            is True
        ):
            return COGNITION_MODE_CONTINUITY

        if categories.intersection(
            {
                "CUI",
                "ITAR",
                "EXPORT_CONTROLLED",
                "CLASSIFIED",
                "FEDRAMP_HIGH",
                "MISSION_CRITICAL",
            }
        ):
            return (
                COGNITION_MODE_CONSERVATIVE
            )

        return COGNITION_MODE_NORMAL

    # =====================================================
    # PLAN EXECUTION
    # =====================================================

    def _execute_plan(
        self,
        plan: CognitionPlan,
    ) -> None:

        plan.status = PLAN_RUNNING

        plan.started_at_ms = _now_ms()

        self._emit(
            "RUNTIME_COGNITION_PLAN_STARTED",
            plan.to_dict(),
        )

        try:

            for step in plan.steps:

                self._execute_step(
                    plan=plan,
                    step=step,
                )

            failed_steps = [
                s
                for s in plan.steps
                if s.status == STEP_FAILED
            ]

            plan.status = (
                PLAN_FAILED
                if failed_steps
                else PLAN_COMPLETED
            )

            plan.completed_at_ms = _now_ms()

        except Exception as exc:

            plan.status = PLAN_FAILED

            plan.error = str(exc)

            plan.completed_at_ms = _now_ms()

        self._emit(
            "RUNTIME_COGNITION_PLAN_COMPLETED",
            plan.to_dict(),
        )

    def _execute_step(
        self,

        plan: CognitionPlan,

        step: CognitionStep,
    ) -> None:

        step.status = STEP_RUNNING

        step.started_at_ms = _now_ms()

        try:

            engine = self._engine_for(
                step.engine_name
            )

            if engine is None:

                step.status = STEP_SKIPPED

                step.result = {
                    "reason": (
                        "engine_unavailable"
                    ),
                    "engine": (
                        step.engine_name
                    ),
                }

                step.completed_at_ms = (
                    _now_ms()
                )

                return

            step.result = (
                self._invoke_engine(
                    engine=engine,
                    engine_name=(
                        step.engine_name
                    ),
                    action=step.action,
                    tenant_id=(
                        plan.tenant_id
                    ),
                    workload=(
                        plan.workload
                    ),
                    trigger=(
                        plan.trigger
                    ),
                )
            )

            step.status = STEP_COMPLETED

            step.completed_at_ms = _now_ms()

        except Exception as exc:

            step.status = STEP_FAILED

            step.error = str(exc)

            step.completed_at_ms = _now_ms()

    # =====================================================
    # ENGINE INVOCATION
    # =====================================================

    def _invoke_engine(
        self,

        engine: Any,

        engine_name: str,

        action: str,

        tenant_id: str,

        workload: Dict[str, Any],

        trigger: str,
    ) -> Dict[str, Any]:

        if (
            action
            == "ingest_current_state"
        ):

            result = (
                engine.ingest_current_state(
                    tenant_id=tenant_id,
                )
            )

            return self._to_dict(result)

        if action == "assess":

            if (
                engine_name
                == (
                    "sovereign_operational_reasoning_engine"
                )
            ):

                result = engine.assess(
                    tenant_id=tenant_id,
                    objective=(
                        "runtime_cognition_orchestration"
                    ),
                    workload={
                        **workload,
                        "source": (
                            "runtime_cognition_orchestrator"
                        ),
                        "trigger": trigger,
                    },
                )

            elif (
                engine_name
                == (
                    "adaptive_operational_strategy_engine"
                )
            ):

                result = engine.assess(
                    tenant_id=tenant_id,
                    objective=(
                        "runtime_cognition_orchestration"
                    ),
                    workload={
                        **workload,
                        "source": (
                            "runtime_cognition_orchestrator"
                        ),
                        "trigger": trigger,
                    },
                )

            elif (
                engine_name
                == "sovereignty_decision_engine"
            ):

                result = engine.assess(
                    tenant_id=tenant_id,
                    workload={
                        **workload,
                        "source": (
                            "runtime_cognition_orchestrator"
                        ),
                        "trigger": trigger,
                    },
                )

            elif (
                engine_name
                == (
                    "adaptive_sovereign_policy_engine"
                )
            ):

                result = engine.assess(
                    tenant_id=tenant_id,
                    workload={
                        **workload,
                        "source": (
                            "runtime_cognition_orchestrator"
                        ),
                        "trigger": trigger,
                    },
                )

            elif (
                engine_name
                == (
                    "autonomous_execution_cognition_engine"
                )
            ):

                result = engine.assess(
                    tenant_id=tenant_id,
                    workload={
                        **workload,
                        "source": (
                            "runtime_cognition_orchestrator"
                        ),
                        "trigger": trigger,
                    },
                )

            else:

                result = engine.assess(
                    tenant_id=tenant_id,
                )

            return self._to_dict(result)

        if action == "synthesize":

            result = (
                engine.synthesize_runtime_intelligence(
                    tenant_id=tenant_id,
                    trigger_event={
                        "source": (
                            "runtime_cognition_orchestrator"
                        ),
                        "trigger": trigger,
                        "workload": workload,
                    },
                )
            )

            return self._to_dict(result)

        if action == "auto_recover":

            result = engine.auto_recover(
                tenant_id=tenant_id,
                actor=(
                    "runtime_cognition_orchestrator"
                ),
                force=False,
            )

            return self._to_dict(result)

        return {
            "ok": False,
            "reason": (
                "unsupported_action"
            ),
            "engine": engine_name,
            "action": action,
        }

    # =====================================================
    # ENGINE LOOKUP
    # =====================================================

    def _engine_for(
        self,
        engine_name: str,
    ) -> Any:

        return {

            "autonomous_runtime_intelligence_engine":
                self.autonomous_runtime_intelligence_engine,

            "runtime_fabric_learning_engine":
                self.runtime_fabric_learning_engine,

            "predictive_runtime_stability_engine":
                self.predictive_runtime_stability_engine,

            "autonomous_execution_cognition_engine":
                self.autonomous_execution_cognition_engine,

            "sovereign_operational_reasoning_engine":
                self.sovereign_operational_reasoning_engine,

            "adaptive_operational_strategy_engine":
                self.adaptive_operational_strategy_engine,

            "sovereignty_decision_engine":
                self.sovereignty_decision_engine,

            "adaptive_sovereign_policy_engine":
                self.adaptive_sovereign_policy_engine,

            "runtime_recovery_manager":
                self.runtime_recovery_manager,

        }.get(engine_name)

    # =====================================================
    # RATE CONTROL
    # =====================================================

    def _is_rate_limited(
        self,
        tenant_id: str,
    ) -> bool:

        last = self._last_plan_at_ms.get(
            tenant_id
        )

        if not last:
            return False

        return (
            (_now_ms() - last)
            < self.min_plan_interval_ms
        )

    # =====================================================
    # EVENT REGISTRATION
    # =====================================================

    def _register_event_handlers(
        self,
    ) -> None:

        if self.event_bus is None:
            return

        for event_type in [

            "EXECUTION_FAILED",

            "RUNTIME_DEGRADED",

            "SOVEREIGN_BOUNDARY_VIOLATION",

            "FEDERATION_LINK_LOST",

            "RECOVERY_TRIGGERED",

            "ROLLBACK_TRIGGERED",

            "EXECUTION_TIMEOUT",

            "WORKER_STALLED",

            "GOVERNANCE_OVERRIDE",

            "AUTONOMY_DRIFT_DETECTED",

            "PREDICTIVE_STABILITY_WARNING",
        ]:

            try:

                self.event_bus.subscribe(
                    event_type,
                    self._handle_runtime_event,
                )

            except Exception:
                pass

    # =====================================================
    # EVENT PROCESSING
    # =====================================================

    def _handle_runtime_event(
        self,
        event: Dict[str, Any],
    ) -> None:

        tenant_id = (
            event.get("tenant_id")
            or event.get("tenant")
            or DEFAULT_TENANT
        )

        event_type = str(
            event.get("event_type")
            or event.get("type")
            or "runtime_event"
        )

        priority = COGNITION_HIGH

        if event_type in {

            "SOVEREIGN_BOUNDARY_VIOLATION",

            "FEDERATION_LINK_LOST",

            "EXECUTION_TIMEOUT",

            "WORKER_STALLED",
        }:

            priority = (
                COGNITION_CRITICAL
            )

        self.orchestrate(
            tenant_id=tenant_id,
            trigger=event_type,
            workload={
                "source_event": event,
                "source": "runtime_event",
                "continuity_required": (
                    priority
                    == COGNITION_CRITICAL
                ),
            },
            priority=priority,
            force=(
                priority
                == COGNITION_CRITICAL
            ),
        )

    # =====================================================
    # STATUS
    # =====================================================

    def orchestration_status(
        self,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:

        if (
            tenant_id
            not in self._status_by_tenant
        ):

            self._update_status(
                tenant_id=tenant_id
            )

        return (
            self._status_by_tenant[
                tenant_id
            ].to_dict()
        )

    def list_plans(
        self,

        limit: int = 100,

        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        rows = self._plans

        if tenant_id:

            rows = [
                p
                for p in rows
                if p.tenant_id == tenant_id
            ]

        rows = sorted(
            rows,
            key=lambda p: p.created_at_ms,
            reverse=True,
        )

        return [
            p.to_dict()
            for p in rows[:limit]
        ]

    def latest_plan(
        self,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Optional[Dict[str, Any]]:

        rows = [
            p
            for p in self._plans
            if p.tenant_id == tenant_id
        ]

        if not rows:
            return None

        return sorted(
            rows,
            key=lambda p: p.created_at_ms,
            reverse=True,
        )[0].to_dict()

    # =====================================================
    # STATUS UPDATE
    # =====================================================

    def _update_status(
        self,

        tenant_id: str,

        last_plan_id: Optional[
            str
        ] = None,
    ) -> None:

        tenant_plans = [
            p
            for p in self._plans
            if p.tenant_id == tenant_id
        ]

        self._status_by_tenant[
            tenant_id
        ] = CognitionOrchestrationStatus(

            tenant_id=tenant_id,

            mode=self._derive_mode(
                tenant_id=tenant_id,
                workload={},
                priority=COGNITION_MEDIUM,
            ),

            active_plans=len([
                p
                for p in tenant_plans
                if p.status == PLAN_RUNNING
            ]),

            completed_plans=len([
                p
                for p in tenant_plans
                if p.status == PLAN_COMPLETED
            ]),

            failed_plans=len([
                p
                for p in tenant_plans
                if p.status == PLAN_FAILED
            ]),

            rate_limited_plans=len([
                p
                for p in tenant_plans
                if p.status == PLAN_RATE_LIMITED
            ]),

            last_plan_id=last_plan_id,
        )

    # =====================================================
    # UTILITIES
    # =====================================================

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
                source=(
                    "runtime_cognition_orchestrator"
                ),
                severity=(
                    payload.get("priority")
                    or "INFO"
                ),
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

    def _to_dict(
        self,
        value: Any,
    ) -> Dict[str, Any]:

        if value is None:
            return {}

        if hasattr(value, "to_dict"):
            return value.to_dict()

        if isinstance(value, dict):
            return value

        if hasattr(value, "__dict__"):
            return dict(value.__dict__)

        return {
            "value": str(value),
        }

    def _trim(self) -> None:

        self._plans = self._plans[-500:]


# =========================================================
# SINGLETON
# =========================================================

_DEFAULT_RUNTIME_COGNITION_ORCHESTRATOR: Optional[
    RuntimeCognitionOrchestrator
] = None


def get_runtime_cognition_orchestrator(

    autonomous_runtime_intelligence_engine: Any = None,

    runtime_fabric_learning_engine: Any = None,

    predictive_runtime_stability_engine: Any = None,

    autonomous_execution_cognition_engine: Any = None,

    sovereign_operational_reasoning_engine: Any = None,

    adaptive_operational_strategy_engine: Any = None,

    sovereignty_decision_engine: Any = None,

    adaptive_sovereign_policy_engine: Any = None,

    runtime_recovery_manager: Any = None,

    autonomy_governor: Any = None,

    storage: Any = None,

    event_bus: Any = None,

        min_plan_interval_ms: int = 10_000,

        max_steps_per_plan: int = 8,

        reset: bool = False,
) -> RuntimeCognitionOrchestrator:
    global _DEFAULT_RUNTIME_COGNITION_ORCHESTRATOR

    if (
            reset
            or (
            _DEFAULT_RUNTIME_COGNITION_ORCHESTRATOR
            is None
    )
    ):
        _DEFAULT_RUNTIME_COGNITION_ORCHESTRATOR = (
            RuntimeCognitionOrchestrator(

                autonomous_runtime_intelligence_engine=(
                    autonomous_runtime_intelligence_engine
                ),

                runtime_fabric_learning_engine=(
                    runtime_fabric_learning_engine
                ),

                predictive_runtime_stability_engine=(
                    predictive_runtime_stability_engine
                ),

                autonomous_execution_cognition_engine=(
                    autonomous_execution_cognition_engine
                ),

                sovereign_operational_reasoning_engine=(
                    sovereign_operational_reasoning_engine
                ),

                adaptive_operational_strategy_engine=(
                    adaptive_operational_strategy_engine
                ),

                sovereignty_decision_engine=(
                    sovereignty_decision_engine
                ),

                adaptive_sovereign_policy_engine=(
                    adaptive_sovereign_policy_engine
                ),

                runtime_recovery_manager=(
                    runtime_recovery_manager
                ),

                autonomy_governor=(
                    autonomy_governor
                ),

                storage=storage,

                event_bus=event_bus,

                min_plan_interval_ms=(
                    min_plan_interval_ms
                ),

                max_steps_per_plan=(
                    max_steps_per_plan
                ),
            )
        )

    return (
        _DEFAULT_RUNTIME_COGNITION_ORCHESTRATOR
    )