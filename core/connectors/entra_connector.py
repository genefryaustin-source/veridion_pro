from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional


class EntraConnector:
    """
    Microsoft Entra ID identity containment connector.

    Current mode: safe simulated connector.
    Future real mode: Microsoft Graph API.
    """

    CONNECTOR_NAME = "entra"

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        simulate: bool = True,
    ):
        self.tenant_id = tenant_id or os.getenv("MS_TENANT_ID")
        self.client_id = client_id or os.getenv("MS_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("MS_CLIENT_SECRET")
        self.simulate = simulate

    def disable_user(self, user_id: str, reason: str = "") -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "disable_user",
            "user_id": user_id,
            "reason": reason,
            "account_enabled": False,
            "sign_in_blocked": True,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def enable_user(self, user_id: str, reason: str = "") -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "enable_user",
            "user_id": user_id,
            "reason": reason,
            "account_enabled": True,
            "sign_in_blocked": False,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def revoke_sessions(self, user_id: str, reason: str = "") -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "revoke_sessions",
            "user_id": user_id,
            "reason": reason,
            "sessions_revoked": True,
            "refresh_tokens_invalidated": True,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def force_password_reset(self, user_id: str, reason: str = "") -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "force_password_reset",
            "user_id": user_id,
            "reason": reason,
            "password_reset_required": True,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def verify_user_disabled(self, user_id: str) -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "verify_user_disabled",
            "user_id": user_id,
            "account_enabled": False,
            "sign_in_allowed": False,
            "simulated": self.simulate,
            "verified_at_ms": int(time.time() * 1000),
        }