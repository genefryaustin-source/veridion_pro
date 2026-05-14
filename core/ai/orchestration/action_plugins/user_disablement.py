"""
core/ai/orchestration/action_plugins/user_disablement.py
"""

from __future__ import annotations

from typing import Dict, Any

from core.ai.orchestration.action_plugins.base_plugin import (
    ActionPlugin,
    PluginResult,
)


class UserDisablementPlugin(ActionPlugin):

    plugin_id = "user_disablement"

    plugin_name = "User Disablement Plugin"

    supported_actions = [
        "DISABLE_USER",
        "ENABLE_USER",
    ]

    requires_approval = True
    destructive = True

    def execute(
        self,
        payload: Dict[str, Any],
    ) -> PluginResult:

        user_id = (
            payload.get("user_id")
            or payload.get("target_user")
        )

        if not user_id:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action="DISABLE_USER",
                message="user_id required",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="DISABLE_USER",
            message=f"User disablement simulated for {user_id}",
            rollback_payload={
                "action": "ENABLE_USER",
                "user_id": user_id,
            },
            verification={
                "simulated": True,
                "user_disabled": True,
            },
        )

    def rollback(
        self,
        payload: Dict[str, Any],
    ) -> PluginResult:

        user_id = payload.get("user_id")

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="ENABLE_USER",
            message=f"User enablement simulated for {user_id}",
            verification={
                "simulated": True,
                "user_restored": True,
            },
        )