"""
core/ai/orchestration/action_plugins/endpoint_isolation.py
"""

from __future__ import annotations

from typing import Dict, Any

from core.ai.orchestration.action_plugins.base_plugin import (
    ActionPlugin,
    PluginResult,
)


class EndpointIsolationPlugin(ActionPlugin):

    plugin_id = "endpoint_isolation"

    plugin_name = "Endpoint Isolation Plugin"

    supported_actions = [
        "ISOLATE_ENDPOINT",
        "UNISOLATE_ENDPOINT",
    ]

    requires_approval = True
    destructive = True

    def execute(
        self,
        payload: Dict[str, Any],
    ) -> PluginResult:

        endpoint_id = (
            payload.get("endpoint_id")
            or payload.get("device_id")
            or payload.get("host_id")
        )

        if not endpoint_id:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action="ISOLATE_ENDPOINT",
                message="endpoint_id is required",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="ISOLATE_ENDPOINT",
            message=f"Endpoint isolation simulated for {endpoint_id}",
            rollback_payload={
                "action": "UNISOLATE_ENDPOINT",
                "endpoint_id": endpoint_id,
                "tenant_id": payload.get("tenant_id"),
            },
            verification={
                "simulated": True,
                "endpoint_isolated": True,
            },
            raw={
                "endpoint_id": endpoint_id,
            },
        )

    def rollback(
        self,
        payload: Dict[str, Any],
    ) -> PluginResult:

        endpoint_id = payload.get("endpoint_id")

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="UNISOLATE_ENDPOINT",
            message=f"Endpoint un-isolation simulated for {endpoint_id}",
            verification={
                "simulated": True,
                "endpoint_restored": True,
            },
        )