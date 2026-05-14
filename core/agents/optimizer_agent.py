"""
core/agents/optimizer_agent.py

Adaptive autonomous optimization agent.

Capabilities:
- workflow tuning
- rollback reduction
- confidence learning
- path optimization
- escalation tuning
- verification tuning
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent, AgentExecutionResult


class OptimizerAgent(BaseAgent):
    AGENT_NAME = "optimizer_agent"

    EXECUTION_SCOPE = [
        "tune_workflow",
        "reduce_rollback",
        "learn_confidence",
        "optimize_path",
        "tune_escalation",
        "tune_verification",
    ]

    REQUIRED_PERMISSIONS = [
        "optimizer.read",
        "optimizer.recommend",
    ]

    DEFAULT_CONFIDENCE = 0.78

    def _execute(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:
        context = context or {}

        handlers = {
            "tune_workflow": self.tune_workflow,
            "reduce_rollback": self.reduce_rollback,
            "learn_confidence": self.learn_confidence,
            "optimize_path": self.optimize_path,
            "tune_escalation": self.tune_escalation,
            "tune_verification": self.tune_verification,
        }

        handler = handlers.get(action)

        if not handler:
            return AgentExecutionResult(
                success=False,
                action=action,
                agent_name=self.AGENT_NAME,
                error="unknown_action",
            )

        return handler(context)

    def tune_workflow(self, context: Dict[str, Any]) -> AgentExecutionResult:
        recommendation = {
            "recommendation": "increase_verification_after_containment",
            "reason": "Workflow tuning favors verification after containment-sensitive actions.",
            "confidence_delta": 0.04,
        }

        self.emit_event("OPTIMIZER_WORKFLOW_TUNED", recommendation)

        return AgentExecutionResult(
            success=True,
            action="tune_workflow",
            agent_name=self.AGENT_NAME,
            confidence=0.82,
            metadata=recommendation,
        )

    def reduce_rollback(self, context: Dict[str, Any]) -> AgentExecutionResult:
        rollback_rate = float(context.get("rollback_rate", 0.0) or 0.0)

        recommendation = {
            "rollback_rate": rollback_rate,
            "recommended_action": "raise_pre_execution_confidence_threshold"
            if rollback_rate >= 10
            else "maintain_current_threshold",
            "threshold_adjustment": 0.08 if rollback_rate >= 10 else 0.0,
        }

        self.emit_event("OPTIMIZER_ROLLBACK_REDUCTION_RECOMMENDED", recommendation)

        return AgentExecutionResult(
            success=True,
            action="reduce_rollback",
            agent_name=self.AGENT_NAME,
            confidence=0.80,
            metadata=recommendation,
        )

    def learn_confidence(self, context: Dict[str, Any]) -> AgentExecutionResult:
        success_count = int(context.get("success_count", 0) or 0)
        failure_count = int(context.get("failure_count", 0) or 0)

        total = max(success_count + failure_count, 1)
        learned_confidence = round(success_count / total, 4)

        payload = {
            "success_count": success_count,
            "failure_count": failure_count,
            "learned_confidence": learned_confidence,
        }

        self.emit_event("OPTIMIZER_CONFIDENCE_LEARNED", payload)

        return AgentExecutionResult(
            success=True,
            action="learn_confidence",
            agent_name=self.AGENT_NAME,
            confidence=learned_confidence,
            metadata=payload,
        )

    def optimize_path(self, context: Dict[str, Any]) -> AgentExecutionResult:
        failed_nodes = context.get("failed_nodes") or []
        rolled_back_nodes = context.get("rolled_back_nodes") or []

        recommendation = {
            "avoid_nodes": failed_nodes + rolled_back_nodes,
            "prefer_verified_paths": True,
            "require_governance_gate": True,
            "created_at_ms": int(time.time() * 1000),
        }

        self.emit_event("OPTIMIZER_PATH_OPTIMIZED", recommendation)

        return AgentExecutionResult(
            success=True,
            action="optimize_path",
            agent_name=self.AGENT_NAME,
            confidence=0.79,
            metadata=recommendation,
        )

    def tune_escalation(self, context: Dict[str, Any]) -> AgentExecutionResult:
        severity = str(context.get("severity", "LOW")).upper()
        export_control = bool(context.get("export_control") or context.get("category") == "EXPORT_CONTROL")

        route = "legal_and_executive" if export_control or severity == "CRITICAL" else "standard_soc"

        payload = {
            "severity": severity,
            "export_control": export_control,
            "recommended_route": route,
            "pager_required": severity == "CRITICAL",
        }

        self.emit_event("OPTIMIZER_ESCALATION_TUNED", payload)

        return AgentExecutionResult(
            success=True,
            action="tune_escalation",
            agent_name=self.AGENT_NAME,
            confidence=0.86,
            metadata=payload,
        )

    def tune_verification(self, context: Dict[str, Any]) -> AgentExecutionResult:
        containment_type = context.get("containment_type") or context.get("action")
        severity = str(context.get("severity", "LOW")).upper()

        frequency = "MAXIMUM" if severity == "CRITICAL" else "ELEVATED" if severity == "HIGH" else "NORMAL"

        payload = {
            "containment_type": containment_type,
            "severity": severity,
            "verification_frequency": frequency,
            "require_post_action_validation": True,
        }

        self.emit_event("OPTIMIZER_VERIFICATION_TUNED", payload)

        return AgentExecutionResult(
            success=True,
            action="tune_verification",
            agent_name=self.AGENT_NAME,
            confidence=0.84,
            metadata=payload,
        )