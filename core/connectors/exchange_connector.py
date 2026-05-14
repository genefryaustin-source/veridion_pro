from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional


class ExchangeConnector:
    """
    Exchange / Microsoft 365 mail containment connector.

    Current mode: safe simulated connector.
    Future real mode: Microsoft Graph / Exchange Online PowerShell / Purview.
    """

    CONNECTOR_NAME = "exchange"

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

    def quarantine_mailbox(self, mailbox: str, reason: str = "") -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "quarantine_mailbox",
            "mailbox": mailbox,
            "reason": reason,
            "quarantine_active": True,
            "mail_flow_suspended": True,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def restore_mailbox(self, mailbox: str, reason: str = "") -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "restore_mailbox",
            "mailbox": mailbox,
            "reason": reason,
            "quarantine_active": False,
            "mail_flow_restored": True,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def purge_messages(
        self,
        mailbox: str,
        message_ids: Optional[List[str]] = None,
        reason: str = "",
    ) -> Dict[str, Any]:
        message_ids = message_ids or []

        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "purge_messages",
            "mailbox": mailbox,
            "message_ids": message_ids,
            "purged_count": len(message_ids),
            "reason": reason,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def suspend_delivery(self, mailbox: str, reason: str = "") -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "suspend_delivery",
            "mailbox": mailbox,
            "mail_flow_suspended": True,
            "reason": reason,
            "simulated": self.simulate,
            "executed_at_ms": int(time.time() * 1000),
        }

    def verify_quarantine(self, mailbox: str) -> Dict[str, Any]:
        return {
            "success": True,
            "connector": self.CONNECTOR_NAME,
            "operation": "verify_quarantine",
            "mailbox": mailbox,
            "quarantine_active": True,
            "mailbox_accessible": False,
            "mail_flow_suspended": True,
            "simulated": self.simulate,
            "verified_at_ms": int(time.time() * 1000),
        }