"""
core/ai/orchestration/action_plugins/safe_builtin_plugins.py

Safe placeholder plugins.

These do NOT perform destructive external actions yet.
They create verified execution results and rollback payloads so the governance
system can be wired before real CrowdStrike/Entra/O365 integrations are enabled.
"""

from __future__ import annotations

from typing import Any, Dict

from core.ai.orchestration.action_plugins.base_plugin import ActionPlugin, PluginResult


class DisableUserPlugin(ActionPlugin):
    plugin_id = "disable_user"
    plugin_name = "Disable User"
    supported_actions = ["DISABLE_USER"]
    requires_approval = True
    destructive = True

    def execute(self, payload: Dict[str, Any]) -> PluginResult:
        user_id = payload.get("user_id") or payload.get("target_user")

        if not user_id:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action="DISABLE_USER",
                message="user_id or target_user is required.",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="DISABLE_USER",
            message=f"Simulated user disable completed for {user_id}.",
            rollback_payload={
                "action": "ENABLE_USER",
                "user_id": user_id,
                "tenant_id": payload.get("tenant_id"),
            },
            verification={
                "simulated": True,
                "user_disabled": True,
            },
        )


class RevokeTokenPlugin(ActionPlugin):
    plugin_id = "revoke_token"
    plugin_name = "Revoke Token / Sessions"
    supported_actions = ["REVOKE_TOKEN", "REVOKE_SESSIONS"]
    requires_approval = True
    destructive = True

    def execute(self, payload: Dict[str, Any]) -> PluginResult:
        principal = payload.get("principal") or payload.get("user_id")

        if not principal:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action=str(payload.get("action")),
                message="principal or user_id is required.",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action=str(payload.get("action")),
            message=f"Simulated token/session revocation completed for {principal}.",
            rollback_payload={
                "action": "NO_ROLLBACK_AVAILABLE",
                "principal": principal,
                "tenant_id": payload.get("tenant_id"),
            },
            verification={
                "simulated": True,
                "sessions_revoked": True,
            },
        )


class QuarantineEmailPlugin(ActionPlugin):
    plugin_id = "quarantine_email"
    plugin_name = "Quarantine Email"
    supported_actions = ["QUARANTINE_EMAIL"]
    requires_approval = True
    destructive = False

    def execute(self, payload: Dict[str, Any]) -> PluginResult:
        message_id = payload.get("message_id") or payload.get("email_id")

        if not message_id:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action="QUARANTINE_EMAIL",
                message="message_id or email_id is required.",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="QUARANTINE_EMAIL",
            message=f"Simulated email quarantine completed for {message_id}.",
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


class BlockIpPlugin(ActionPlugin):
    plugin_id = "block_ip"
    plugin_name = "Block IP"
    supported_actions = ["BLOCK_IP"]
    requires_approval = True
    destructive = True

    def execute(self, payload: Dict[str, Any]) -> PluginResult:
        ip = payload.get("ip") or payload.get("ip_address")

        if not ip:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action="BLOCK_IP",
                message="ip or ip_address is required.",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="BLOCK_IP",
            message=f"Simulated IP block completed for {ip}.",
            rollback_payload={
                "action": "UNBLOCK_IP",
                "ip": ip,
                "tenant_id": payload.get("tenant_id"),
            },
            verification={
                "simulated": True,
                "ip_blocked": True,
            },
        )


class SealEvidencePlugin(ActionPlugin):
    plugin_id = "seal_evidence"
    plugin_name = "Seal Evidence"
    supported_actions = ["SEAL_EVIDENCE"]
    requires_approval = False
    destructive = False

    def execute(self, payload: Dict[str, Any]) -> PluginResult:
        evidence_id = payload.get("evidence_id")

        if not evidence_id:
            return PluginResult(
                ok=False,
                plugin_id=self.plugin_id,
                action="SEAL_EVIDENCE",
                message="evidence_id is required.",
            )

        return PluginResult(
            ok=True,
            plugin_id=self.plugin_id,
            action="SEAL_EVIDENCE",
            message=f"Simulated evidence seal completed for {evidence_id}.",
            rollback_payload={
                "action": "NO_ROLLBACK_REQUIRED",
                "evidence_id": evidence_id,
                "tenant_id": payload.get("tenant_id"),
            },
            verification={
                "simulated": True,
                "evidence_sealed": True,
            },
        )