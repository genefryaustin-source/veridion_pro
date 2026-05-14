from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

import requests


def _now_ms() -> int:
    return int(time.time() * 1000)


class ExchangeAdapter:
    """
    Microsoft Exchange / Graph mailbox orchestration adapter.

    Supports:
    - mailbox quarantine markers
    - legal hold markers
    - mailbox preservation
    - message purge requests
    - mailbox evidence export requests
    - mailbox intelligence retrieval

    Destructive actions default to dry-run and should be approval-gated upstream.
    """

    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
    GRAPH_BETA_URL = "https://graph.microsoft.com/beta"

    def __init__(
        self,
        *,
        access_token: Optional[str] = None,
        token_provider: Any = None,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        dry_run_default: bool = True,
        timeout_seconds: int = 30,
    ):
        self.access_token = access_token
        self.token_provider = token_provider
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.dry_run_default = dry_run_default
        self.timeout_seconds = timeout_seconds

    # ------------------------------------------------------------------
    # Mailbox Containment
    # ------------------------------------------------------------------

    def quarantine_mailbox(self, *, mailbox_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Mailbox quarantine", dry_run=None):
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="EXCHANGE_MAILBOX_QUARANTINE_REQUESTED",
            details={"mailbox_id": mailbox_id, "tenant_id": tenant_id, "reason": reason, "dry_run": dry_run},
        )

    def restrict_mailbox(self, *, mailbox_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Restrict mailbox", dry_run=None):
        return self.quarantine_mailbox(
            mailbox_id=mailbox_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def hold_mailbox(self, *, mailbox_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Mailbox legal hold", dry_run=None):
        return self.legal_hold(
            mailbox_id=mailbox_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # Evidence Preservation / Legal Hold
    # ------------------------------------------------------------------

    def legal_hold(self, *, mailbox_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Legal hold requested", dry_run=None):
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="EXCHANGE_LEGAL_HOLD_REQUESTED",
            details={"mailbox_id": mailbox_id, "tenant_id": tenant_id, "reason": reason, "dry_run": dry_run},
        )

    def preserve_mailbox(self, *, mailbox_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Preserve mailbox", dry_run=None):
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="EXCHANGE_MAILBOX_PRESERVATION_REQUESTED",
            details={"mailbox_id": mailbox_id, "tenant_id": tenant_id, "reason": reason, "dry_run": dry_run},
        )

    def export_mailbox_evidence(self, *, mailbox_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Export mailbox evidence", dry_run=None):
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="EXCHANGE_MAILBOX_EXPORT_REQUESTED",
            details={"mailbox_id": mailbox_id, "tenant_id": tenant_id, "reason": reason, "dry_run": dry_run},
        )

    # ------------------------------------------------------------------
    # Message Actions
    # ------------------------------------------------------------------

    def purge_message(self, *, mailbox_id: str, message_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Purge message", dry_run=None):
        return self._execute(
            method="DELETE",
            url=f"{self.GRAPH_BASE_URL}/users/{mailbox_id}/messages/{message_id}",
            action="PURGE_MESSAGE",
            mailbox_id=mailbox_id,
            message_id=message_id,
            body=None,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    def move_message_to_junk(self, *, mailbox_id: str, message_id: str, case_id=None, tenant_id=None, actor="exchange_adapter", reason="Move message to junk", dry_run=None):
        return self._execute(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/users/{mailbox_id}/messages/{message_id}/move",
            action="MOVE_MESSAGE_TO_JUNK",
            mailbox_id=mailbox_id,
            message_id=message_id,
            body={"destinationId": "junkemail"},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # Mailbox Intelligence
    # ------------------------------------------------------------------

    def get_mailbox_messages(self, *, mailbox_id: str, top: int = 25) -> Dict[str, Any]:
        return self._request(method="GET", url=f"{self.GRAPH_BASE_URL}/users/{mailbox_id}/messages?$top={top}")

    def get_message(self, *, mailbox_id: str, message_id: str) -> Dict[str, Any]:
        return self._request(method="GET", url=f"{self.GRAPH_BASE_URL}/users/{mailbox_id}/messages/{message_id}")

    def search_mailbox(self, *, mailbox_id: str, query: str, top: int = 25) -> Dict[str, Any]:
        return self._request(
            method="GET",
            url=f"{self.GRAPH_BASE_URL}/users/{mailbox_id}/messages?$search=\"{query}\"&$top={top}",
        )

    # ------------------------------------------------------------------
    # ContainmentEngine Compatibility
    # ------------------------------------------------------------------

    def quarantine_mailbox_from_case(self, *, case_id=None, requested_by="containment_engine", tenant_id=None, details=None):
        details = details or {}
        mailbox_id = details.get("mailbox_id") or details.get("target_mailbox") or details.get("user_id")

        if not mailbox_id:
            return {"status": "missing_mailbox_id", "case_id": case_id, "timestamp_ms": _now_ms()}

        return self.quarantine_mailbox(
            mailbox_id=mailbox_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=requested_by,
            reason=details.get("reason") or "ContainmentEngine mailbox quarantine",
            dry_run=details.get("dry_run", self.dry_run_default),
        )

    def restrict_mailbox_from_case(self, *, case_id=None, requested_by="containment_engine", tenant_id=None, details=None):
        return self.quarantine_mailbox_from_case(
            case_id=case_id,
            requested_by=requested_by,
            tenant_id=tenant_id,
            details=details,
        )

    def hold_mailbox_from_case(self, *, case_id=None, requested_by="containment_engine", tenant_id=None, details=None):
        details = details or {}
        mailbox_id = details.get("mailbox_id") or details.get("target_mailbox") or details.get("user_id")

        if not mailbox_id:
            return {"status": "missing_mailbox_id", "case_id": case_id, "timestamp_ms": _now_ms()}

        return self.legal_hold(
            mailbox_id=mailbox_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=requested_by,
            reason=details.get("reason") or "ContainmentEngine legal hold",
            dry_run=details.get("dry_run", self.dry_run_default),
        )

    # ------------------------------------------------------------------
    # Core Execution
    # ------------------------------------------------------------------

    def _execute(self, *, method, url, action, mailbox_id, message_id=None, body=None, case_id=None, tenant_id=None, actor="exchange_adapter", reason="", dry_run=None, destructive=False):
        execution_id = f"EXCHANGE-{uuid.uuid4().hex[:12].upper()}"
        dry_run = self.dry_run_default if dry_run is None else bool(dry_run)

        metadata = {
            "execution_id": execution_id,
            "adapter": "ExchangeAdapter",
            "action": action,
            "mailbox_id": mailbox_id,
            "message_id": message_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "actor": actor,
            "reason": reason,
            "destructive": destructive,
            "dry_run": dry_run,
            "timestamp_ms": _now_ms(),
        }

        self._audit(case_id=case_id, event_type="EXCHANGE_ACTION_STARTED", actor=actor, details={**metadata, "body": body})

        if dry_run:
            result = {**metadata, "status": "dry_run", "body": body}
            self._audit(case_id=case_id, event_type="EXCHANGE_ACTION_DRY_RUN", actor=actor, details=result)
            self._publish(event_type="EXCHANGE_ACTION_DRY_RUN", case_id=case_id, tenant_id=tenant_id, actor=actor, payload=result)
            return result

        try:
            response = self._request(method=method, url=url, body=body)
            result = {**metadata, "status": "executed", "response": response, "completed_at_ms": _now_ms()}
            self._audit(case_id=case_id, event_type="EXCHANGE_ACTION_EXECUTED", actor=actor, details=result)
            self._publish(event_type="EXCHANGE_ACTION_EXECUTED", case_id=case_id, tenant_id=tenant_id, actor=actor, payload=result)
            return result

        except Exception as exc:
            result = {**metadata, "status": "failed", "error": str(exc), "failed_at_ms": _now_ms()}
            self._audit(case_id=case_id, event_type="EXCHANGE_ACTION_FAILED", actor=actor, details=result)
            self._publish(event_type="EXCHANGE_ACTION_FAILED", case_id=case_id, tenant_id=tenant_id, actor=actor, payload=result)
            return result

    def _request(self, *, method: str, url: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        token = self._get_access_token()

        response = requests.request(
            method=method,
            url=url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body if body else None,
            timeout=self.timeout_seconds,
        )

        text = response.text

        try:
            parsed = response.json() if text else None
        except Exception:
            parsed = None

        if response.status_code >= 400:
            raise RuntimeError(f"Exchange Graph request failed ({response.status_code}): {text}")

        return {"status_code": response.status_code, "json": parsed, "text": text}

    def _get_access_token(self) -> str:
        if self.token_provider is not None:
            token = self.token_provider()
            if isinstance(token, dict):
                token = token.get("access_token") or token.get("token")
            if token:
                return str(token)

        if self.access_token:
            return self.access_token

        raise RuntimeError("No Microsoft Graph access token configured.")

    # ------------------------------------------------------------------
    # Audit / Events
    # ------------------------------------------------------------------

    def _audit(self, *, case_id, event_type, actor, details):
        if self.ledger is None:
            return

        for method_name in ["add_case_event", "create_case_event", "record_case_event"]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    method(case_id=case_id, event_type=event_type, actor=actor, details=details)
                    return
                except TypeError:
                    try:
                        method(case_id, event_type, actor, details)
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

    def _publish(self, *, event_type, case_id, tenant_id, actor, payload):
        if self.event_bus is not None:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=actor,
                    source="exchange_adapter",
                )
            except Exception:
                pass

        if self.live_updates is not None and case_id is not None:
            try:
                self.live_updates.broadcast_case_update(
                    case_id=case_id,
                    tenant_id=tenant_id,
                    event_type=event_type,
                    payload=payload,
                    actor=actor,
                )
            except Exception:
                pass

    def _record_marker(self, *, case_id, actor, marker, details):
        self._audit(case_id=case_id, event_type=marker, actor=actor, details=details)
        self._publish(
            event_type=marker,
            case_id=case_id,
            tenant_id=details.get("tenant_id"),
            actor=actor,
            payload=details,
        )
        return {"marker": marker, "recorded": True, "timestamp_ms": _now_ms()}