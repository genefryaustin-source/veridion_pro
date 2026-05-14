from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, Optional

import requests


def _now_ms() -> int:
    return int(time.time() * 1000)


class EntraAdapter:
    """
    Microsoft Entra ID / Microsoft Graph identity execution adapter.

    Supports:
    - disable user
    - enable user
    - force password reset
    - revoke sessions
    - MFA preference enforcement
    - remove user from group
    - tag high-risk user
    - move user to quarantine group

    Important:
    This adapter assumes approval has already been handled by the
    orchestration layer before destructive or high-risk actions run.
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
    # User Operations
    # ------------------------------------------------------------------

    def disable_user(
        self,
        *,
        user_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Identity containment",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._patch_user(
            user_id=user_id,
            body={"accountEnabled": False},
            action="DISABLE_USER",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def enable_user(
        self,
        *,
        user_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Restore account access",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._patch_user(
            user_id=user_id,
            body={"accountEnabled": True},
            action="ENABLE_USER",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def force_password_reset(
        self,
        *,
        user_id: str,
        temporary_password: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Force password reset",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._patch_user(
            user_id=user_id,
            body={
                "passwordProfile": {
                    "forceChangePasswordNextSignIn": True,
                    "password": temporary_password,
                }
            },
            action="FORCE_PASSWORD_RESET",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            sensitive=True,
        )

    def revoke_sessions(
        self,
        *,
        user_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Revoke active sign-in sessions",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_graph_action(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/users/{user_id}/revokeSignInSessions",
            action="REVOKE_SESSIONS",
            user_id=user_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def enforce_mfa(
        self,
        *,
        user_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Enable system-preferred MFA",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Uses Microsoft Graph beta authentication sign-in preferences.

        Microsoft currently documents this under /beta for some MFA state
        operations, so keep this behind approval/governance in production.
        """
        return self._execute_graph_action(
            method="PATCH",
            url=f"{self.GRAPH_BETA_URL}/users/{user_id}/authentication/signInPreferences",
            action="ENFORCE_MFA",
            user_id=user_id,
            body={
                "isSystemPreferredAuthenticationMethodEnabled": True,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def remove_user_from_group(
        self,
        *,
        user_id: str,
        group_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Remove user from group",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_graph_action(
            method="DELETE",
            url=f"{self.GRAPH_BASE_URL}/groups/{group_id}/members/{user_id}/$ref",
            action="REMOVE_USER_FROM_GROUP",
            user_id=user_id,
            body={
                "group_id": group_id,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # Risk Actions
    # ------------------------------------------------------------------

    def tag_high_risk_user(
        self,
        *,
        user_id: str,
        tag: str = "HIGH_RISK_INVESTIGATION",
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Tag user as high risk",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Stores a visible operational marker using extension-like metadata.

        In production, replace extensionAttribute with your real schema
        extension / custom security attribute strategy.
        """
        return self._patch_user(
            user_id=user_id,
            body={
                "onPremisesExtensionAttributes": {
                    "extensionAttribute15": tag,
                }
            },
            action="TAG_HIGH_RISK_USER",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def move_user_to_quarantine_group(
        self,
        *,
        user_id: str,
        quarantine_group_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "entra_adapter",
        reason: str = "Move user to quarantine group",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Adds user to quarantine group.

        If your policy requires removing all other privileged groups,
        call remove_user_from_group separately for each group after approval.
        """
        return self._execute_graph_action(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/groups/{quarantine_group_id}/members/$ref",
            action="MOVE_USER_TO_QUARANTINE_GROUP",
            user_id=user_id,
            body={
                "@odata.id": f"{self.GRAPH_BASE_URL}/directoryObjects/{user_id}",
                "quarantine_group_id": quarantine_group_id,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # ContainmentEngine-Compatible Aliases
    # ------------------------------------------------------------------

    def disable_account(
        self,
        *,
        case_id: Any = None,
        requested_by: str = "containment_engine",
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        details = details or {}
        return self.disable_user(
            user_id=details.get("user_id") or details.get("target_user"),
            case_id=case_id,
            tenant_id=tenant_id,
            actor=requested_by,
            reason=details.get("reason") or "ContainmentEngine disable account",
            dry_run=details.get("dry_run", self.dry_run_default),
        )

    def disable_user_from_case(
        self,
        case_id: Any,
    ) -> Dict[str, Any]:
        return {
            "status": "missing_user_id",
            "case_id": case_id,
            "message": "Pass details={'user_id': ...} for real Entra execution.",
            "timestamp_ms": _now_ms(),
        }

    def revoke_credentials(
        self,
        *,
        case_id: Any = None,
        requested_by: str = "containment_engine",
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        details = details or {}
        return self.revoke_sessions(
            user_id=details.get("user_id") or details.get("target_user"),
            case_id=case_id,
            tenant_id=tenant_id,
            actor=requested_by,
            reason=details.get("reason") or "ContainmentEngine revoke credentials",
            dry_run=details.get("dry_run", self.dry_run_default),
        )

    def contain_user(
        self,
        *,
        case_id: Any = None,
        requested_by: str = "containment_engine",
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        details = details or {}

        user_id = details.get("user_id") or details.get("target_user")

        if not user_id:
            return {
                "status": "missing_user_id",
                "case_id": case_id,
                "timestamp_ms": _now_ms(),
            }

        results = []

        results.append(
            self.revoke_sessions(
                user_id=user_id,
                case_id=case_id,
                tenant_id=tenant_id,
                actor=requested_by,
                reason="Containment workflow: revoke sessions",
                dry_run=details.get("dry_run", self.dry_run_default),
            )
        )

        if details.get("disable_account", False):
            results.append(
                self.disable_user(
                    user_id=user_id,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=requested_by,
                    reason="Containment workflow: disable user",
                    dry_run=details.get("dry_run", self.dry_run_default),
                )
            )

        if details.get("quarantine_group_id"):
            results.append(
                self.move_user_to_quarantine_group(
                    user_id=user_id,
                    quarantine_group_id=details["quarantine_group_id"],
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=requested_by,
                    reason="Containment workflow: quarantine group",
                    dry_run=details.get("dry_run", self.dry_run_default),
                )
            )

        return {
            "status": "completed",
            "case_id": case_id,
            "user_id": user_id,
            "results": results,
            "timestamp_ms": _now_ms(),
        }

    suspend_access = contain_user
    restrict_user = contain_user
    restrict_access = contain_user
    rotate_credentials = revoke_credentials

    # ------------------------------------------------------------------
    # Internal Graph Execution
    # ------------------------------------------------------------------

    def _patch_user(
        self,
        *,
        user_id: str,
        body: Dict[str, Any],
        action: str,
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        reason: str,
        dry_run: Optional[bool],
        sensitive: bool = False,
    ) -> Dict[str, Any]:
        return self._execute_graph_action(
            method="PATCH",
            url=f"{self.GRAPH_BASE_URL}/users/{user_id}",
            action=action,
            user_id=user_id,
            body=body,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            sensitive=sensitive,
        )

    def _execute_graph_action(
        self,
        *,
        method: str,
        url: str,
        action: str,
        user_id: Optional[str],
        body: Optional[Dict[str, Any]],
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        reason: str,
        dry_run: Optional[bool],
        sensitive: bool = False,
    ) -> Dict[str, Any]:
        execution_id = f"ENTRA-{uuid.uuid4().hex[:12].upper()}"

        dry_run = self.dry_run_default if dry_run is None else bool(dry_run)

        if not user_id:
            result = {
                "status": "missing_user_id",
                "execution_id": execution_id,
                "action": action,
                "timestamp_ms": _now_ms(),
            }

            self._audit_execution(
                case_id=case_id,
                event_type="ENTRA_ACTION_SKIPPED",
                actor=actor,
                details=result,
            )

            return result

        request_meta = {
            "execution_id": execution_id,
            "adapter": "EntraAdapter",
            "action": action,
            "method": method,
            "url": url,
            "user_id": user_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "actor": actor,
            "reason": reason,
            "dry_run": dry_run,
            "requested_at_ms": _now_ms(),
        }

        audit_body = "[REDACTED]" if sensitive else body

        self._audit_execution(
            case_id=case_id,
            event_type="ENTRA_ACTION_STARTED",
            actor=actor,
            details={
                **request_meta,
                "body": audit_body,
            },
        )

        if dry_run:
            result = {
                **request_meta,
                "status": "dry_run",
                "body": audit_body,
            }

            self._audit_execution(
                case_id=case_id,
                event_type="ENTRA_ACTION_DRY_RUN",
                actor=actor,
                details=result,
            )

            self._publish_realtime(
                event_type="ENTRA_ACTION_DRY_RUN",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

        try:
            response = self._request(
                method=method,
                url=url,
                body=body,
            )

            result = {
                **request_meta,
                "status": "executed",
                "http_status": response.get("status_code"),
                "response": response.get("json"),
                "response_text": response.get("text"),
                "completed_at_ms": _now_ms(),
            }

            self._audit_execution(
                case_id=case_id,
                event_type="ENTRA_ACTION_EXECUTED",
                actor=actor,
                details=result,
            )

            self._publish_realtime(
                event_type="ENTRA_ACTION_EXECUTED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload={
                    "execution_id": execution_id,
                    "action": action,
                    "user_id": user_id,
                    "http_status": result.get("http_status"),
                },
            )

            return result

        except Exception as exc:
            result = {
                **request_meta,
                "status": "failed",
                "error": str(exc),
                "failed_at_ms": _now_ms(),
            }

            self._audit_execution(
                case_id=case_id,
                event_type="ENTRA_ACTION_FAILED",
                actor=actor,
                details=result,
            )

            self._publish_realtime(
                event_type="ENTRA_ACTION_FAILED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

    def _request(
        self,
        *,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body if body else None,
            timeout=self.timeout_seconds,
        )

        text = response.text

        try:
            parsed = response.json() if text else None
        except Exception:
            parsed = None

        if response.status_code >= 400:
            raise RuntimeError(
                f"Microsoft Graph request failed "
                f"({response.status_code}): {text}"
            )

        return {
            "status_code": response.status_code,
            "json": parsed,
            "text": text,
        }

    def _get_access_token(self) -> str:
        if self.token_provider is not None:
            token = self.token_provider()

            if isinstance(token, dict):
                token = (
                    token.get("access_token")
                    or token.get("token")
                )

            if token:
                return str(token)

        if self.access_token:
            return self.access_token

        raise RuntimeError(
            "No Microsoft Graph access token configured."
        )

    # ------------------------------------------------------------------
    # Audit / Realtime
    # ------------------------------------------------------------------

    def _audit_execution(
        self,
        *,
        case_id: Optional[Any],
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        if case_id is not None:
            for method_name in [
                "add_case_event",
                "create_case_event",
                "record_case_event",
            ]:
                method = getattr(
                    self.ledger,
                    method_name,
                    None,
                )

                if callable(method):
                    try:
                        method(
                            case_id=case_id,
                            event_type=event_type,
                            actor=actor,
                            details=details,
                        )
                        return
                    except TypeError:
                        try:
                            method(
                                case_id,
                                event_type,
                                actor,
                                details,
                            )
                            return
                        except Exception:
                            pass
                    except Exception:
                        pass

        for method_name in [
            "record_integration_execution",
            "add_integration_execution",
            "record_event",
        ]:
            method = getattr(
                self.ledger,
                method_name,
                None,
            )

            if callable(method):
                try:
                    method(
                        event_type=event_type,
                        actor=actor,
                        details=details,
                    )
                    return
                except TypeError:
                    try:
                        method(event_type, actor, details)
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

    def _publish_realtime(
        self,
        *,
        event_type: str,
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is not None:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=actor,
                    source="entra_adapter",
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