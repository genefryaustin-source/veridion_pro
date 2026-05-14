"""
core/ai/orchestration/action_plugins/mailbox_quarantine.py
"""

from __future__ import annotations

from typing import Dict, Any

from core.ai.orchestration.action_plugins.base_plugin import (
    ActionPlugin,
    PluginResult,
)


class MailboxQuarantinePlugin(ActionPlugin):

    plugin_id = "mailbox_quarantine"

    plugin_name = "Mailbox Quarantine Plugin"

    supported_actions = [
        "QUARANTINE_EMAIL",
        "RESTORE_EMAIL",
    ]

    requires_approval = True
    destructive = False

    def execute(
        self,
        payload: Dict[str, Any],
    ) -> PluginResult:

        message_id = (
            payload.get("message_id")
            or payload.get("email_id")
        )

        if not message_id:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action="QUARANTINE_EMAIL",
                message="message_id is required",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="QUARANTINE_EMAIL",
            message=f"Email quarantine simulated for {message_id}",
            rollback_payload={
                "action": "RESTORE_EMAIL",
                "message_id": message_id,
                "tenant_id": payload.get("tenant_id"),
            },
            verification={
                "simulated": True,
                "email_quarantined": True,
            },
        )

    def rollback(
        self,
        payload: Dict[str, Any],
    ) -> PluginResult:

        message_id = payload.get("message_id")

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="RESTORE_EMAIL",
            message=f"Email restoration simulated for {message_id}",
            verification={
                "simulated": True,
                "email_restored": True,
            },
        )