# core/ai/orchestration/adaptive_policy_optimizer.py

from __future__ import annotations

import json
import threading
import time
from typing import Any, Dict, Optional

from core.events.event_bus import (
    get_event_bus,
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    VERIFICATION_FAILED,
    ROLLBACK_TRIGGERED,
    ROLLBACK_COMPLETED,
    APPROVAL_REJECTED,
    ANALYST_OVERRIDE,
    CASE_ESCALATED,
)


DEFAULT_POLICY_STATE = {
    "automation_confidence": 1.0,
    "approval_threshold": 0.70,
    "autonomy_level": 1.0,
    "rollback_sensitivity": 0.50,
    "escalation_sensitivity": 0.50,
}


class AdaptivePolicyOptimizer:
    """
    Adaptive governance learning engine.

    Learns continuously from:
    - execution outcomes
    - rollback activity
    - analyst overrides
    - escalation patterns
    - approval rejections
    - verification failures
    """

    def __init__(
            self,
            storage: Any = None,
            ledger: Any = None,
            governance: Any = None,
            event_bus: Any = None,
    ):
        self.storage = storage

        self.ledger = (
                ledger
                or getattr(
            storage,
            "ledger",
            None,
        )
                or storage
        )

        self.governance = (
                governance
                or getattr(
            storage,
            "governance",
            None,
        )
        )

        self.event_bus = (
                event_bus
                or getattr(
            storage,
            "event_bus",
            None,
        )
                or get_event_bus()
        )

        self._lock = threading.RLock()

        self.metrics: Dict[str, Any] = {}

        self.policy_state: Dict[str, Any] = dict(
            DEFAULT_POLICY_STATE
        )

        self._load_state()

        self._register_subscriptions()

    def optimize_tenant_policy(
            self,
            tenant_id: str = "default",
            dry_run: bool = True,
            lookback_limit: int = 100,
            include_recommendations: bool = True,
            include_metrics: bool = True,
            **kwargs,
    ) -> Dict[str, Any]:

        recommendations = []

        metrics = getattr(
            self,
            "metrics",
            {},
        )

        policy_state = getattr(
            self,
            "policy_state",
            {},
        )

        rollback_rate = float(
            metrics.get(
                "rollback_rate",
                0.0,
            )
        )

        approval_delay = float(
            metrics.get(
                "approval_delay_minutes",
                0.0,
            )
        )

        false_positive_rate = float(
            metrics.get(
                "false_positive_rate",
                0.0,
            )
        )

        if include_recommendations:

            if rollback_rate > 0.25:
                recommendations.append({

                    "type": "safety",

                    "recommendation":
                        "Increase approval requirements "
                        "for destructive actions.",

                    "severity": "HIGH",
                })

            if approval_delay > 30:
                recommendations.append({

                    "type": "workflow",

                    "recommendation":
                        "Enable delegated approval routing.",

                    "severity": "MEDIUM",
                })

            if false_positive_rate > 0.20:
                recommendations.append({

                    "type": "detection",

                    "recommendation":
                        "Reduce autonomous containment "
                        "confidence thresholds.",

                    "severity": "HIGH",
                })

        result = {

            "tenant_id": tenant_id,

            "dry_run": dry_run,

            "lookback_limit": lookback_limit,

            "recommendations": recommendations,

            "policy_state": policy_state,

            "optimized_at_ms": int(
                time.time() * 1000
            ),
        }

        if include_metrics:
            result["metrics"] = metrics

        if kwargs:
            result["extra_args"] = kwargs

        return result



    # =====================================================
    # EVENT BUS REGISTRATION
    # =====================================================

    def _register_subscriptions(self) -> None:

        self.event_bus.subscribe(
            EXECUTION_COMPLETED,
            self.handle_execution_completed,
        )

        self.event_bus.subscribe(
            EXECUTION_FAILED,
            self.handle_execution_failed,
        )

        self.event_bus.subscribe(
            VERIFICATION_FAILED,
            self.handle_verification_failed,
        )

        self.event_bus.subscribe(
            ROLLBACK_TRIGGERED,
            self.handle_rollback_triggered,
        )

        self.event_bus.subscribe(
            ROLLBACK_COMPLETED,
            self.handle_rollback_completed,
        )

        self.event_bus.subscribe(
            APPROVAL_REJECTED,
            self.handle_approval_rejected,
        )

        self.event_bus.subscribe(
            ANALYST_OVERRIDE,
            self.handle_analyst_override,
        )

        self.event_bus.subscribe(
            CASE_ESCALATED,
            self.handle_case_escalated,
        )

    # =====================================================
    # PERSISTENCE
    # =====================================================

    def _load_state(self) -> None:

        if not self.governance:
            return

        try:

            events = self.governance.get_governance_events(
                limit=1,
                event_type="OPTIMIZER_STATE_SNAPSHOT",
            )

            if not events:
                return

            latest = events[-1]

            details = latest.get("details") or {}

            self.metrics = details.get("metrics") or {}
            self.policy_state = details.get("policy_state") or dict(
                DEFAULT_POLICY_STATE
            )

        except Exception as e:
            print("Optimizer state load error:", e)

    def _persist_state(self) -> None:

        if not self.governance:
            return

        try:

            self.governance.record_governance_event(
                event_type="OPTIMIZER_STATE_SNAPSHOT",
                severity="INFO",
                status="SNAPSHOT",
                actor="adaptive_policy_optimizer",
                action="persist_state",
                details={
                    "metrics": self.metrics,
                    "policy_state": self.policy_state,
                    "persisted_at_ms": int(time.time() * 1000),
                },
            )

        except Exception as e:
            print("Optimizer persist error:", e)

    # =====================================================
    # EVENT HANDLERS
    # =====================================================

    def handle_execution_completed(self, event):
        """
        Learn from successful executions.
        """

        try:

            with self._lock:

                payload = event.payload or {}
                action = payload.get("action")

                self.metrics["execution_successes"] = (
                    self.metrics.get("execution_successes", 0)
                    + 1
                )

                success_rates = self.metrics.setdefault(
                    "successful_actions",
                    {},
                )

                success_rates[action] = (
                    success_rates.get(action, 0)
                    + 1
                )

                current_confidence = self.policy_state.get(
                    "automation_confidence",
                    1.0,
                )

                self.policy_state[
                    "automation_confidence"
                ] = min(
                    1.0,
                    current_confidence + 0.01,
                )

                self._persist_state()

        except Exception as e:
            print(
                "Optimizer execution success learning error:",
                e,
            )

    def handle_execution_failed(self, event):
        """
        Learn from execution failures.
        """

        try:

            with self._lock:

                payload = event.payload or {}

                tenant_id = event.tenant_id
                action = payload.get("action")
                decision_id = payload.get("decision_id")

                self.metrics["execution_failures"] = (
                    self.metrics.get("execution_failures", 0)
                    + 1
                )

                failures = self.metrics.setdefault(
                    "action_failure_counts",
                    {},
                )

                failures[action] = (
                    failures.get(action, 0)
                    + 1
                )

                current_confidence = self.policy_state.get(
                    "automation_confidence",
                    1.0,
                )

                self.policy_state[
                    "automation_confidence"
                ] = max(
                    0.1,
                    current_confidence - 0.05,
                )

                current_threshold = self.policy_state.get(
                    "approval_threshold",
                    0.70,
                )

                self.policy_state[
                    "approval_threshold"
                ] = min(
                    0.95,
                    current_threshold + 0.02,
                )

                if self.governance:

                    self.governance.record_governance_event(
                        event_type="OPTIMIZER_LEARNING_UPDATE",
                        tenant_id=tenant_id,
                        decision_id=decision_id,
                        severity="MEDIUM",
                        status="LEARNED",
                        actor="adaptive_policy_optimizer",
                        action="execution_failure_learning",
                        details={
                            "action": action,
                            "automation_confidence": self.policy_state[
                                "automation_confidence"
                            ],
                            "approval_threshold": self.policy_state[
                                "approval_threshold"
                            ],
                            "failure_count": failures[action],
                        },
                    )

                self._persist_state()

        except Exception as e:

            print(
                "Optimizer handle_execution_failed error:",
                e,
            )

    def handle_verification_failed(self, event):
        """
        Learn from verification instability.
        """

        try:

            with self._lock:

                self.metrics["verification_failures"] = (
                    self.metrics.get(
                        "verification_failures",
                        0,
                    )
                    + 1
                )

                current_confidence = self.policy_state.get(
                    "automation_confidence",
                    1.0,
                )

                self.policy_state[
                    "automation_confidence"
                ] = max(
                    0.1,
                    current_confidence - 0.04,
                )

                self._persist_state()

        except Exception as e:
            print(
                "Optimizer verification learning error:",
                e,
            )

    def handle_rollback_triggered(self, event):
        """
        Learn from rollback activity.
        """

        try:

            with self._lock:

                payload = event.payload or {}
                action = payload.get("action")

                self.metrics["rollback_count"] = (
                    self.metrics.get("rollback_count", 0)
                    + 1
                )

                rollback_rates = self.metrics.setdefault(
                    "rollback_rates",
                    {},
                )

                rollback_rates[action] = (
                    rollback_rates.get(action, 0)
                    + 1
                )

                current_autonomy = self.policy_state.get(
                    "autonomy_level",
                    1.0,
                )

                self.policy_state[
                    "autonomy_level"
                ] = max(
                    0.1,
                    current_autonomy - 0.10,
                )

                current_sensitivity = self.policy_state.get(
                    "rollback_sensitivity",
                    0.50,
                )

                self.policy_state[
                    "rollback_sensitivity"
                ] = min(
                    1.0,
                    current_sensitivity + 0.05,
                )

                self._persist_state()

        except Exception as e:

            print(
                "Optimizer rollback learning error:",
                e,
            )

    def handle_rollback_completed(self, event):
        """
        Learn from successful rollback recovery.
        """

        try:

            with self._lock:

                self.metrics["rollback_completed"] = (
                    self.metrics.get(
                        "rollback_completed",
                        0,
                    )
                    + 1
                )

                self._persist_state()

        except Exception as e:
            print(
                "Optimizer rollback completion learning error:",
                e,
            )

    def handle_approval_rejected(self, event):
        """
        Learn from governance rejection.
        """

        try:

            with self._lock:

                self.metrics["approval_rejections"] = (
                    self.metrics.get(
                        "approval_rejections",
                        0,
                    )
                    + 1
                )

                current_threshold = self.policy_state.get(
                    "approval_threshold",
                    0.70,
                )

                self.policy_state[
                    "approval_threshold"
                ] = min(
                    0.95,
                    current_threshold + 0.03,
                )

                self._persist_state()

        except Exception as e:
            print(
                "Optimizer approval rejection learning error:",
                e,
            )

    def handle_analyst_override(self, event):
        """
        Learn from analyst overrides.
        """

        try:

            with self._lock:

                self.metrics["analyst_overrides"] = (
                    self.metrics.get(
                        "analyst_overrides",
                        0,
                    )
                    + 1
                )

                current_confidence = self.policy_state.get(
                    "automation_confidence",
                    1.0,
                )

                self.policy_state[
                    "automation_confidence"
                ] = max(
                    0.1,
                    current_confidence - 0.03,
                )

                self._persist_state()

        except Exception as e:

            print(
                "Optimizer override learning error:",
                e,
            )

    def handle_case_escalated(self, event):
        """
        Learn from escalation instability.
        """

        try:

            with self._lock:

                self.metrics["case_escalations"] = (
                    self.metrics.get(
                        "case_escalations",
                        0,
                    )
                    + 1
                )

                current_sensitivity = self.policy_state.get(
                    "escalation_sensitivity",
                    0.50,
                )

                self.policy_state[
                    "escalation_sensitivity"
                ] = min(
                    1.0,
                    current_sensitivity + 0.05,
                )

                self._persist_state()

        except Exception as e:
            print(
                "Optimizer escalation learning error:",
                e,
            )

    # =====================================================
    # PUBLIC API
    # =====================================================

    def get_policy_state(self) -> Dict[str, Any]:
        return dict(self.policy_state)

    def get_metrics(self) -> Dict[str, Any]:
        return dict(self.metrics)

    def export_learning_snapshot(self) -> Dict[str, Any]:

        return {
            "metrics": self.metrics,
            "policy_state": self.policy_state,
            "exported_at_ms": int(time.time() * 1000),
        }


def get_adaptive_policy_optimizer(storage: Any):
    return AdaptivePolicyOptimizer(storage)

