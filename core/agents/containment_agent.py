"""
core/agents/containment_agent.py

Autonomous containment operations.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.agents.base_agent import (
    BaseAgent,
    AgentExecutionResult,
)


class ContainmentAgent(BaseAgent):

    AGENT_NAME = "containment_agent"

    EXECUTION_SCOPE = [
        "mailbox_isolation",
        "endpoint_quarantine",
        "token_revocation",
        "session_kill",
        "containment_rollback",
    ]

    REQUIRED_PERMISSIONS = [
        "containment.execute",
    ]

    DEFAULT_CONFIDENCE = 0.85

    def _execute(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:

        context = context or {}

        handlers = {
            "mailbox_isolation": self.isolate_mailbox,
            "endpoint_quarantine": self.quarantine_endpoint,
            "token_revocation": self.revoke_tokens,
            "session_kill": self.kill_sessions,
            "containment_rollback": self.rollback_containment,
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

    # ========================================================
    # ACTIONS
    # ========================================================

    def isolate_mailbox(
        self,
        context: Dict[str, Any],
    ) -> AgentExecutionResult:

        mailbox = context.get("mailbox")

        self.emit_event(
            "MAILBOX_ISOLATED",
            {
                "mailbox": mailbox,
            },
        )

        return AgentExecutionResult(
            success=True,
            action="mailbox_isolation",
            agent_name=self.AGENT_NAME,
            confidence=0.90,
            rollback_supported=True,
            rollback_data=context,
            message=f"Mailbox isolated: {mailbox}",
        )

    def quarantine_endpoint(
        self,
        context: Dict[str, Any],
    ) -> AgentExecutionResult:

        endpoint = context.get("endpoint")

        self.emit_event(
            "ENDPOINT_QUARANTINED",
            {
                "endpoint": endpoint,
            },
        )

        return AgentExecutionResult(
            success=True,
            action="endpoint_quarantine",
            agent_name=self.AGENT_NAME,
            confidence=0.88,
            rollback_supported=True,
            rollback_data=context,
        )

    def revoke_tokens(
        self,
        context: Dict[str, Any],
    ) -> AgentExecutionResult:

        user = context.get("user")

        self.emit_event(
            "TOKENS_REVOKED",
            {
                "user": user,
            },
        )

        return AgentExecutionResult(
            success=True,
            action="token_revocation",
            agent_name=self.AGENT_NAME,
            confidence=0.92,
            rollback_supported=False,
        )

    def kill_sessions(
        self,
        context: Dict[str, Any],
    ) -> AgentExecutionResult:

        user = context.get("user")

        self.emit_event(
            "SESSIONS_TERMINATED",
            {
                "user": user,
            },
        )

        return AgentExecutionResult(
            success=True,
            action="session_kill",
            agent_name=self.AGENT_NAME,
            confidence=0.89,
        )

    def rollback_containment(
        self,
        context: Dict[str, Any],
    ) -> AgentExecutionResult:

        self.emit_event(
            "CONTAINMENT_ROLLBACK_EXECUTED",
            context,
        )

        return AgentExecutionResult(
            success=True,
            action="containment_rollback",
            agent_name=self.AGENT_NAME,
            confidence=0.70,
        )