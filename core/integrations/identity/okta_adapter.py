from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

import requests


def _now_ms() -> int:
    return int(time.time() * 1000)


class OktaAdapter:
    def __init__(
        self,
        *,
        okta_domain: str,
        api_token: Optional[str] = None,
        token_provider: Any = None,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        dry_run_default: bool = True,
        timeout_seconds: int = 30,
    ):
        self.okta_domain = okta_domain.rstrip("/")
        self.api_token = api_token
        self.token_provider = token_provider
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.dry_run_default = dry_run_default
        self.timeout_seconds = timeout_seconds

    # ------------------------------------------------------------------
    # Identity Containment
    # ------------------------------------------------------------------

    def disable_user(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Disable user", dry_run=None):
        return self.suspend_user(user_id=user_id, case_id=case_id, tenant_id=tenant_id, actor=actor, reason=reason, dry_run=dry_run)

    def suspend_user(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Suspend user", dry_run=None):
        return self._execute(
            method="POST",
            path=f"/api/v1/users/{user_id}/lifecycle/suspend",
            action="SUSPEND_USER",
            target_id=user_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    def unsuspend_user(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Unsuspend user", dry_run=None):
        return self._execute(
            method="POST",
            path=f"/api/v1/users/{user_id}/lifecycle/unsuspend",
            action="UNSUSPEND_USER",
            target_id=user_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def deactivate_user(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Deactivate user", dry_run=None):
        return self._execute(
            method="POST",
            path=f"/api/v1/users/{user_id}/lifecycle/deactivate",
            action="DEACTIVATE_USER",
            target_id=user_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    # ------------------------------------------------------------------
    # Sessions / MFA
    # ------------------------------------------------------------------

    def revoke_sessions(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Revoke sessions", dry_run=None):
        return self._execute(
            method="DELETE",
            path=f"/api/v1/users/{user_id}/sessions",
            action="REVOKE_SESSIONS",
            target_id=user_id,
            body=None,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def clear_mfa_sessions(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Clear MFA sessions", dry_run=None):
        return self._execute(
            method="DELETE",
            path=f"/api/v1/users/{user_id}/sessions",
            action="CLEAR_MFA_SESSIONS",
            target_id=user_id,
            body=None,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def reset_factors(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Reset MFA factors", dry_run=None):
        return self._execute(
            method="POST",
            path=f"/api/v1/users/{user_id}/lifecycle/reset_factors",
            action="RESET_FACTORS",
            target_id=user_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    def enforce_mfa(self, *, user_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Enforce MFA", dry_run=None):
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="OKTA_MFA_ENFORCEMENT_REQUESTED",
            details={"user_id": user_id, "tenant_id": tenant_id, "reason": reason, "dry_run": dry_run},
        )

    # ------------------------------------------------------------------
    # Groups / Risk Tagging
    # ------------------------------------------------------------------

    def add_user_to_group(self, *, user_id: str, group_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Add user to group", dry_run=None):
        return self._execute(
            method="PUT",
            path=f"/api/v1/groups/{group_id}/users/{user_id}",
            action="ADD_USER_TO_GROUP",
            target_id=user_id,
            body={"group_id": group_id},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def remove_user_from_group(self, *, user_id: str, group_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Remove user from group", dry_run=None):
        return self._execute(
            method="DELETE",
            path=f"/api/v1/groups/{group_id}/users/{user_id}",
            action="REMOVE_USER_FROM_GROUP",
            target_id=user_id,
            body={"group_id": group_id},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def move_to_quarantine_group(self, *, user_id: str, quarantine_group_id: str, case_id=None, tenant_id=None, actor="okta_adapter", reason="Move to quarantine group", dry_run=None):
        return self.add_user_to_group(
            user_id=user_id,
            group_id=quarantine_group_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def tag_high_risk_user(self, *, user_id: str, tag: str = "HIGH_RISK_INVESTIGATION", case_id=None, tenant_id=None, actor="okta_adapter", reason="Tag high-risk user", dry_run=None):
        return self._execute(
            method="POST",
            path=f"/api/v1/users/{user_id}",
            action="TAG_HIGH_RISK_USER",
            target_id=user_id,
            body={"profile": {"investigationRiskTag": tag}},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    mark_under_investigation = tag_high_risk_user

    # ------------------------------------------------------------------
    # Intelligence
    # ------------------------------------------------------------------

    def get_user(self, *, user_id: str) -> Dict[str, Any]:
        return self._request(method="GET", path=f"/api/v1/users/{user_id}")

    def get_user_groups(self, *, user_id: str) -> Dict[str, Any]:
        return self._request(method="GET", path=f"/api/v1/users/{user_id}/groups")

    def get_authentication_events(self, *, user_id: str, limit: int = 100) -> Dict[str, Any]:
        return self._request(method="GET", path=f"/api/v1/logs?filter=actor.id eq \"{user_id}\"&limit={limit}")

    def get_user_risk(self, *, user_id: str) -> Dict[str, Any]:
        return self._record_only("OKTA_USER_RISK_REQUESTED", {"user_id": user_id})

    # ------------------------------------------------------------------
    # ContainmentEngine Compatibility
    # ------------------------------------------------------------------

    def disable_account(self, *, case_id=None, requested_by="containment_engine", tenant_id=None, details=None):
        details = details or {}
        return self.disable_user(
            user_id=details.get("user_id") or details.get("target_user"),
            case_id=case_id,
            tenant_id=tenant_id,
            actor=requested_by,
            reason=details.get("reason") or "ContainmentEngine disable account",
            dry_run=details.get("dry_run", self.dry_run_default),
        )

    def contain_user(self, *, case_id=None, requested_by="containment_engine", tenant_id=None, details=None):
        details = details or {}
        user_id = details.get("user_id") or details.get("target_user")

        if not user_id:
            return {"status": "missing_user_id", "case_id": case_id, "timestamp_ms": _now_ms()}

        results = [
            self.revoke_sessions(
                user_id=user_id,
                case_id=case_id,
                tenant_id=tenant_id,
                actor=requested_by,
                reason="Containment workflow: revoke sessions",
                dry_run=details.get("dry_run", self.dry_run_default),
            )
        ]

        if details.get("suspend_user", True):
            results.append(
                self.suspend_user(
                    user_id=user_id,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=requested_by,
                    reason="Containment workflow: suspend user",
                    dry_run=details.get("dry_run", self.dry_run_default),
                )
            )

        if details.get("quarantine_group_id"):
            results.append(
                self.move_to_quarantine_group(
                    user_id=user_id,
                    quarantine_group_id=details["quarantine_group_id"],
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=requested_by,
                    reason="Containment workflow: quarantine group",
                    dry_run=details.get("dry_run", self.dry_run_default),
                )
            )

        return {"status": "completed", "case_id": case_id, "user_id": user_id, "results": results, "timestamp_ms": _now_ms()}

    revoke_credentials = revoke_sessions
    restrict_user = contain_user
    restrict_access = contain_user
    suspend_access = contain_user

    # ------------------------------------------------------------------
    # Core Execution
    # ------------------------------------------------------------------

    def _execute(self, *, method, path, action, target_id, body, case_id, tenant_id, actor, reason, dry_run, destructive=False):
        execution_id = f"OKTA-{uuid.uuid4().hex[:12].upper()}"
        dry_run = self.dry_run_default if dry_run is None else bool(dry_run)

        metadata = {
            "execution_id": execution_id,
            "adapter": "OktaAdapter",
            "action": action,
            "target_id": target_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "actor": actor,
            "reason": reason,
            "destructive": destructive,
            "dry_run": dry_run,
            "timestamp_ms": _now_ms(),
        }

        self._audit(case_id=case_id, event_type="OKTA_ACTION_STARTED", actor=actor, details={**metadata, "body": body})

        if dry_run:
            result = {**metadata, "status": "dry_run", "body": body}
            self._audit(case_id=case_id, event_type="OKTA_ACTION_DRY_RUN", actor=actor, details=result)
            self._publish(event_type="OKTA_ACTION_DRY_RUN", case_id=case_id, tenant_id=tenant_id, actor=actor, payload=result)
            return result

        try:
            response = self._request(method=method, path=path, body=body)
            result = {**metadata, "status": "executed", "response": response, "completed_at_ms": _now_ms()}
            self._audit(case_id=case_id, event_type="OKTA_ACTION_EXECUTED", actor=actor, details=result)
            self._publish(event_type="OKTA_ACTION_EXECUTED", case_id=case_id, tenant_id=tenant_id, actor=actor, payload=result)
            return result
        except Exception as exc:
            result = {**metadata, "status": "failed", "error": str(exc), "failed_at_ms": _now_ms()}
            self._audit(case_id=case_id, event_type="OKTA_ACTION_FAILED", actor=actor, details=result)
            self._publish(event_type="OKTA_ACTION_FAILED", case_id=case_id, tenant_id=tenant_id, actor=actor, payload=result)
            return result

    def _request(self, *, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        token = self._get_token()
        response = requests.request(
            method=method,
            url=f"{self.okta_domain}{path}",
            headers={
                "Authorization": f"SSWS {token}",
                "Accept": "application/json",
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
            raise RuntimeError(f"Okta API failed ({response.status_code}): {text}")

        return {"status_code": response.status_code, "json": parsed, "text": text}

    def _get_token(self) -> str:
        if self.token_provider is not None:
            token = self.token_provider()
            if isinstance(token, dict):
                token = token.get("api_token") or token.get("token")
            if token:
                return str(token)

        if self.api_token:
            return self.api_token

        raise RuntimeError("No Okta API token configured.")

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
                    source="okta_adapter",
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
        return {"marker": marker, "recorded": True, "timestamp_ms": _now_ms()}

    def _record_only(self, marker: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {"marker": marker, "details": details, "timestamp_ms": _now_ms()}