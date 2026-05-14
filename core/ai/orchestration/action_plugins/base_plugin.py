"""
core/ai/orchestration/action_plugins/base_plugin.py
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List


def _now_ms() -> int:
    return int(time.time() * 1000)


# =============================================================================
# PLUGIN RESULT
# =============================================================================

@dataclass
class PluginResult:
    ok: bool
    plugin_id: str
    action: str
    message: str

    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rollback_payload: Dict[str, Any] = field(default_factory=dict)
    verification: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=_now_ms)


# =============================================================================
# BASE ACTION PLUGIN
# =============================================================================

class ActionPlugin:
    """
    Base contract for ALL execution plugins.
    """

    plugin_id: str = "base_plugin"
    plugin_name: str = "Base Plugin"

    supported_actions: List[str] = []

    requires_approval: bool = True
    destructive: bool = False

    # -------------------------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------------------------

    def validate(self, payload: Dict[str, Any]) -> PluginResult:
        action = payload.get("action")

        if action not in self.supported_actions:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action=str(action),
                message=f"Unsupported action: {action}",
            )

        tenant_id = payload.get("tenant_id")

        if not tenant_id:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action=str(action),
                message="tenant_id is required",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action=str(action),
            message="Validation successful",
        )

    # -------------------------------------------------------------------------
    # EXECUTE
    # -------------------------------------------------------------------------

    def execute(self, payload: Dict[str, Any]) -> PluginResult:
        raise NotImplementedError(
            f"{self.plugin_name} must implement execute()"
        )

    # -------------------------------------------------------------------------
    # VERIFY
    # -------------------------------------------------------------------------

    def verify(self, payload: Dict[str, Any]) -> PluginResult:
        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action=str(payload.get('action')),
            message="Verification successful",
        )

    # -------------------------------------------------------------------------
    # ROLLBACK
    # -------------------------------------------------------------------------

    def rollback(self, payload: Dict[str, Any]) -> PluginResult:
        return PluginResult(
            ok=False,
            plugin_id=self.plugin_id,
            action=str(payload.get('action')),
            message="Rollback not implemented",
        )