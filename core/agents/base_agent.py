"""
core/agents/base_agent.py

Foundation contract for ALL autonomous SOC agents.

Defines:
- identity
- permissions
- execution scopes
- governance hooks
- coordination contracts
- telemetry integration
- rollback support
- audit-safe execution

ALL future agents inherit from this class.
"""

from __future__ import annotations

import time
import uuid
import traceback

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# SAFE EVENT IMPORTS
# ============================================================

try:
    from core.events.event_subscribers import dispatch_event
except Exception:

    def dispatch_event(*args, **kwargs):
        return None


# ============================================================
# AUTONOMY MODES
# ============================================================

MODE_MANUAL = "MANUAL"
MODE_ASSISTED = "ASSISTED"
MODE_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
MODE_FULL_AUTONOMY = "FULL_AUTONOMY"
MODE_LOCKDOWN = "LOCKDOWN"


# ============================================================
# EXECUTION RESULT
# ============================================================

@dataclass
class AgentExecutionResult:

    success: bool

    action: str

    agent_name: str

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    message: str = ""

    confidence: float = 0.0

    evidence_ids: List[str] = field(default_factory=list)

    rollback_supported: bool = False

    rollback_data: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    error: Optional[str] = None


# ============================================================
# BASE AGENT
# ============================================================

class BaseAgent:

    AGENT_NAME = "base_agent"

    AGENT_DESCRIPTION = "Base autonomous SOC agent"

    EXECUTION_SCOPE = []

    REQUIRED_PERMISSIONS = []

    ALLOWED_AUTONOMY_MODES = [
        MODE_SUPERVISED_AUTONOMY,
        MODE_FULL_AUTONOMY,
        MODE_LOCKDOWN,
    ]

    ENABLE_ROLLBACK = True

    ENABLE_AUDIT_LOGGING = True

    ENABLE_EVENT_STREAMING = True

    DEFAULT_CONFIDENCE = 0.50

    def __init__(
        self,
        storage: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ):

        self.storage = storage

        self.config = config or {}

        self.agent_id = str(uuid.uuid4())

        self.created_at_ms = int(time.time() * 1000)

    # ========================================================
    # GOVERNANCE
    # ========================================================

    def get_current_autonomy_mode(self) -> str:

        try:
            from core.ai.orchestration.autonomy_modes import (
                get_autonomy_mode
            )

            mode = get_autonomy_mode()

            if hasattr(mode, "name"):
                return str(mode.name).upper()

            return str(mode).upper()

        except Exception:
            return MODE_MANUAL

    def is_execution_allowed(self) -> bool:

        mode = self.get_current_autonomy_mode()

        return mode in self.ALLOWED_AUTONOMY_MODES

    def validate_permissions(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:

        return True

    def validate_governance(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:

        if not self.is_execution_allowed():
            return False

        return True

    # ========================================================
    # TELEMETRY
    # ========================================================

    def emit_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:

        payload = payload or {}

        payload["agent_name"] = self.AGENT_NAME
        payload["agent_id"] = self.agent_id

        dispatch_event(
            event_type=event_type,
            payload=payload,
            source=self.AGENT_NAME,
        )

    # ========================================================
    # EXECUTION
    # ========================================================

    def execute(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:

        context = context or {}

        execution_id = str(uuid.uuid4())

        self.emit_event(
            "AGENT_EXECUTION_STARTED",
            {
                "action": action,
                "execution_id": execution_id,
            },
        )

        try:

            if not self.validate_governance(action, context):

                result = AgentExecutionResult(
                    success=False,
                    action=action,
                    agent_name=self.AGENT_NAME,
                    execution_id=execution_id,
                    message="Governance validation failed.",
                    confidence=0.0,
                    error="governance_validation_failed",
                )

                self.emit_event(
                    "AGENT_EXECUTION_BLOCKED",
                    {
                        "action": action,
                        "execution_id": execution_id,
                    },
                )

                return result

            result = self._execute(
                action=action,
                context=context,
            )

            self.emit_event(
                "AGENT_EXECUTION_COMPLETED",
                {
                    "action": action,
                    "execution_id": execution_id,
                    "success": result.success,
                },
            )

            return result

        except Exception:

            error = traceback.format_exc()

            self.emit_event(
                "AGENT_EXECUTION_FAILED",
                {
                    "action": action,
                    "execution_id": execution_id,
                    "error": error,
                },
            )

            return AgentExecutionResult(
                success=False,
                action=action,
                agent_name=self.AGENT_NAME,
                execution_id=execution_id,
                confidence=0.0,
                error=error,
            )

    def _execute(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:

        raise NotImplementedError

    # ========================================================
    # ROLLBACK
    # ========================================================

    def rollback(
        self,
        rollback_data: Dict[str, Any],
    ) -> bool:

        return False