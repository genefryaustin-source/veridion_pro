"""
core/ai/orchestration/action_plugins/plugin_registry.py
"""

from __future__ import annotations

from typing import Dict, List, Optional

from core.ai.orchestration.action_plugins.base_plugin import ActionPlugin
from core.ai.orchestration.action_plugins.endpoint_isolation import (
    EndpointIsolationPlugin,
)

from core.ai.orchestration.action_plugins.mailbox_quarantine import (
    MailboxQuarantinePlugin,
)

from core.ai.orchestration.action_plugins.session_revocation import (
    SessionRevocationPlugin,
)

from core.ai.orchestration.action_plugins.user_disablement import (
    UserDisablementPlugin,
)

from core.ai.orchestration.action_plugins.evidence_sealing import (
    EvidenceSealingPlugin,
)

# =============================================================================
# ACTION PLUGIN REGISTRY
# =============================================================================

class ActionPluginRegistry:

    def __init__(self):
        self._plugins: Dict[str, ActionPlugin] = {}
        self._action_map: Dict[str, str] = {}

    # -------------------------------------------------------------------------
    # REGISTER
    # -------------------------------------------------------------------------

    def register(self, plugin: ActionPlugin) -> None:
        self._plugins[plugin.plugin_id] = plugin

        for action in plugin.supported_actions:
            self._action_map[action] = plugin.plugin_id



    # -------------------------------------------------------------------------
    # GET PLUGIN
    # -------------------------------------------------------------------------

    def get_plugin(
        self,
        plugin_id: str,
    ) -> Optional[ActionPlugin]:
        return self._plugins.get(plugin_id)

    # -------------------------------------------------------------------------
    # GET PLUGIN FOR ACTION
    # -------------------------------------------------------------------------

    def get_plugin_for_action(
        self,
        action: str,
    ) -> Optional[ActionPlugin]:

        plugin_id = self._action_map.get(action)

        if not plugin_id:
            return None

        return self._plugins.get(plugin_id)

    # -------------------------------------------------------------------------
    # LIST PLUGINS
    # -------------------------------------------------------------------------

    def list_plugins(self) -> List[dict]:
        return [
            {
                "plugin_id": plugin.plugin_id,
                "plugin_name": plugin.plugin_name,
                "supported_actions": plugin.supported_actions,
                "requires_approval": plugin.requires_approval,
                "destructive": plugin.destructive,
            }
            for plugin in self._plugins.values()
        ]

    # -------------------------------------------------------------------------
    # EXECUTE
    # -------------------------------------------------------------------------

    def execute(self, payload: dict):
        action = payload.get("action")

        plugin = self.get_plugin_for_action(action)

        if not plugin:
            raise ValueError(
                f"No plugin registered for action: {action}"
            )

        validation = plugin.validate(payload)

        if not validation.ok:
            return validation

        return plugin.execute(payload)


# =============================================================================
# GLOBAL REGISTRY
# =============================================================================

_DEFAULT_REGISTRY: Optional[ActionPluginRegistry] = None


def get_action_plugin_registry() -> ActionPluginRegistry:
    global _DEFAULT_REGISTRY

    if _DEFAULT_REGISTRY is None:
        registry = ActionPluginRegistry()

        registry.register(
            EndpointIsolationPlugin()
        )

        registry.register(
            MailboxQuarantinePlugin()
        )

        registry.register(
            SessionRevocationPlugin()
        )

        registry.register(
            UserDisablementPlugin()
        )

        registry.register(
            EvidenceSealingPlugin()
        )

        _DEFAULT_REGISTRY = registry