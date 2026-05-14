"""
core/connectors/okta_connector.py

Okta Connector for Veridion Pro / CUI GovCloud App.

Supports:
- DISABLE_USER
- ENABLE_USER
- SUSPEND_USER
- UNSUSPEND_USER
- DEACTIVATE_USER
- REACTIVATE_USER
- REVOKE_SESSIONS
- GET_USER
- SEARCH_USERS
- LIST_SESSIONS

Safe by default:
- simulation_mode=True through BaseConnector
- destructive calls require governance approval upstream
- safety guardrails execute in BaseConnector before real actions
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional
from urllib.parse import quote

import requests

from core.connectors.base_connector import (
    BaseConnector,
    ConnectorAuthState,
    ConnectorCapability,
    ConnectorExecutionResult,
    STATUS_COMPLETED,
    STATUS_FAILED,
)


ACTION_DISABLE_USER = "DISABLE_USER"
ACTION_ENABLE_USER = "ENABLE_USER"
ACTION_SUSPEND_USER = "SUSPEND_USER"
ACTION_UNSUSPEND_USER = "UNSUSPEND_USER"
ACTION_DEACTIVATE_USER = "DEACTIVATE_USER"
ACTION_REACTIVATE_USER = "REACTIVATE_USER"
ACTION_REVOKE_SESSIONS = "REVOKE_SESSIONS"
ACTION_GET_USER = "GET_USER"
ACTION_SEARCH_USERS = "SEARCH_USERS"
ACTION_LIST_SESSIONS = "LIST_SESSIONS"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


class OktaConnector(BaseConnector):
    connector_id = "okta"
    connector_name = "Okta Connector"
    vendor = "Okta"

    def __init__(
        self,
        *,
        tenant_id: str = "default",
        config: Optional[Dict[str, Any]] = None,
        event_bus: Any = None,
        storage: Any = None,
        simulation_mode: bool = True,
    ) -> None:
        super().__init__(
            tenant_id=tenant_id,
            config=config or {},
            event_bus=event_bus,
            storage=storage,
            simulation_mode=simulation_mode,
        )

        self.okta_domain = (
            self.config.get("okta_domain")
            or self.config.get("base_url")
            or ""
        ).rstrip("/")

        self.api_token = (
            self.config.get("api_token")
            or self.config.get("token")
        )

        self.timeout = int(self.config.get("timeout", 30))

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(self) -> Dict[str, ConnectorCapability]:
        return {
            ACTION_DISABLE_USER: ConnectorCapability(
                name=ACTION_DISABLE_USER,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=True,
                description="Suspend an Okta user. Alias for SUSPEND_USER.",
            ),
            ACTION_ENABLE_USER: ConnectorCapability(
                name=ACTION_ENABLE_USER,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=False,
                description="Unsuspend or reactivate an Okta user where possible.",
            ),
            ACTION_SUSPEND_USER: ConnectorCapability(
                name=ACTION_SUSPEND_USER,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=True,
                description="Suspend an ACTIVE Okta user.",
            ),
            ACTION_UNSUSPEND_USER: ConnectorCapability(
                name=ACTION_UNSUSPEND_USER,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=False,
                description="Unsuspend an Okta user.",
            ),
            ACTION_DEACTIVATE_USER: ConnectorCapability(
                name=ACTION_DEACTIVATE_USER,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=True,
                description="Deactivate an Okta user.",
            ),
            ACTION_REACTIVATE_USER: ConnectorCapability(
                name=ACTION_REACTIVATE_USER,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=False,
                description="Reactivate a deactivated Okta user.",
            ),
            ACTION_REVOKE_SESSIONS: ConnectorCapability(
                name=ACTION_REVOKE_SESSIONS,
                supported=True,
                requires_approval=True,
                supports_rollback=False,
                destructive=True,
                description="Clear all Okta user sessions and optionally OAuth/OIDC tokens.",
            ),
            ACTION_GET_USER: ConnectorCapability(
                name=ACTION_GET_USER,
                supported=True,
                requires_approval=False,
                supports_rollback=False,
                destructive=False,
                description="Retrieve an Okta user.",
            ),
            ACTION_SEARCH_USERS: ConnectorCapability(
                name=ACTION_SEARCH_USERS,
                supported=True,
                requires_approval=False,
                supports_rollback=False,
                destructive=False,
                description="Search/list Okta users.",
            ),
            ACTION_LIST_SESSIONS: ConnectorCapability(
                name=ACTION_LIST_SESSIONS,
                supported=True,
                requires_approval=False,
                supports_rollback=False,
                destructive=False,
                description="List sessions when supported by configured Okta API context.",
            ),
        }

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def authenticate(self) -> ConnectorAuthState:
        if self.simulation_mode:
            self.auth_state = ConnectorAuthState(
                authenticated=True,
                auth_type="simulation",
                metadata={"simulation_mode": True},
            )
            return self.auth_state

        if not self.okta_domain or not self.api_token:
            self.auth_state = ConnectorAuthState(
                authenticated=False,
                auth_type="ssws_token",
                metadata={
                    "error": "Missing okta_domain or api_token.",
                },
            )
            return self.auth_state

        self.auth_state = ConnectorAuthState(
            authenticated=True,
            auth_type="ssws_token",
            metadata={
                "okta_domain": self.okta_domain,
            },
        )
        return self.auth_state

    def ensure_authenticated(self) -> ConnectorAuthState:
        if not self.auth_state.authenticated:
            return self.authenticate()
        return self.auth_state

    # ------------------------------------------------------------------
    # Real execution
    # ------------------------------------------------------------------

    def _execute_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:
        action = _safe_str(action).upper()

        if action in {ACTION_DISABLE_USER, ACTION_SUSPEND_USER}:
            return self._lifecycle_action(
                action=ACTION_SUSPEND_USER,
                lifecycle="suspend",
                payload=payload,
                execution_id=execution_id,
            )

        if action in {ACTION_ENABLE_USER, ACTION_UNSUSPEND_USER}:
            return self._enable_user(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_DEACTIVATE_USER:
            return self._lifecycle_action(
                action=ACTION_DEACTIVATE_USER,
                lifecycle="deactivate",
                payload=payload,
                execution_id=execution_id,
                params={"sendEmail": "false"},
            )

        if action == ACTION_REACTIVATE_USER:
            return self._lifecycle_action(
                action=ACTION_REACTIVATE_USER,
                lifecycle="reactivate",
                payload=payload,
                execution_id=execution_id,
                params={"sendEmail": "false"},
            )

        if action == ACTION_REVOKE_SESSIONS:
            return self._revoke_sessions(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_GET_USER:
            return self._get_user(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_SEARCH_USERS:
            return self._search_users(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_LIST_SESSIONS:
            return self._list_sessions(
                payload=payload,
                execution_id=execution_id,
            )

        return self._failed(
            action,
            execution_id,
            f"Unsupported Okta action: {action}",
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _lifecycle_action(
        self,
        *,
        action: str,
        lifecycle: str,
        payload: Dict[str, Any],
        execution_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> ConnectorExecutionResult:
        user_id = self._require_user_id(payload)

        if not user_id:
            return self._failed(action, execution_id, "user_id is required.")

        response = self._request(
            "POST",
            f"/api/v1/users/{quote(user_id)}/lifecycle/{lifecycle}",
            params=params or {},
        )

        if not response["ok"]:
            return self._failed(action, execution_id, response["message"], raw=response)

        rollback_payload = self.build_rollback_payload(
            action=action,
            payload=payload,
        )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_COMPLETED,
            message=f"Okta lifecycle action completed: {lifecycle}.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            rollback_available=bool(rollback_payload),
            rollback_payload=rollback_payload,
            raw=response,
        )

    def _enable_user(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        user_id = self._require_user_id(payload)

        if not user_id:
            return self._failed(ACTION_ENABLE_USER, execution_id, "user_id is required.")

        current = self._request("GET", f"/api/v1/users/{quote(user_id)}")
        status = _safe_str((current.get("json") or {}).get("status")).upper()

        if status == "SUSPENDED":
            return self._lifecycle_action(
                action=ACTION_UNSUSPEND_USER,
                lifecycle="unsuspend",
                payload=payload,
                execution_id=execution_id,
            )

        if status in {"DEPROVISIONED", "DEACTIVATED"}:
            return self._lifecycle_action(
                action=ACTION_REACTIVATE_USER,
                lifecycle="reactivate",
                payload=payload,
                execution_id=execution_id,
                params={"sendEmail": "false"},
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_ENABLE_USER,
            status=STATUS_COMPLETED,
            message=f"User already in non-disabled status: {status or 'UNKNOWN'}.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            rollback_available=False,
            raw={"current": current},
        )

    def _revoke_sessions(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        user_id = self._require_user_id(payload)
        oauth_tokens = bool(payload.get("oauth_tokens", True))

        if not user_id:
            return self._failed(ACTION_REVOKE_SESSIONS, execution_id, "user_id is required.")

        response = self._request(
            "DELETE",
            f"/api/v1/users/{quote(user_id)}/sessions",
            params={"oauthTokens": str(oauth_tokens).lower()},
        )

        if not response["ok"]:
            return self._failed(ACTION_REVOKE_SESSIONS, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_REVOKE_SESSIONS,
            status=STATUS_COMPLETED,
            message="Okta user sessions cleared.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            rollback_available=False,
            rollback_payload={
                "action": "NO_ROLLBACK_AVAILABLE",
                "reason": "Session revocation cannot be reversed.",
                "user_id": user_id,
            },
            raw=response,
        )

    def _get_user(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        user_id = self._require_user_id(payload)

        if not user_id:
            return self._failed(ACTION_GET_USER, execution_id, "user_id is required.")

        response = self._request(
            "GET",
            f"/api/v1/users/{quote(user_id)}",
        )

        if not response["ok"]:
            return self._failed(ACTION_GET_USER, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_USER,
            status=STATUS_COMPLETED,
            message="Okta user retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            raw=response,
        )

    def _search_users(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        query = payload.get("query") or payload.get("search") or ""
        limit = min(max(int(payload.get("limit") or 25), 1), 200)

        params = {"limit": limit}

        if query:
            params["search"] = query

        response = self._request(
            "GET",
            "/api/v1/users",
            params=params,
        )

        if not response["ok"]:
            return self._failed(ACTION_SEARCH_USERS, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_SEARCH_USERS,
            status=STATUS_COMPLETED,
            message="Okta user search completed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=query,
            simulated=False,
            raw=response,
        )

    def _list_sessions(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        user_id = self._require_user_id(payload)

        if not user_id:
            return self._failed(ACTION_LIST_SESSIONS, execution_id, "user_id is required.")

        response = self._request(
            "GET",
            f"/api/v1/users/{quote(user_id)}/sessions",
        )

        if not response["ok"]:
            return self._failed(ACTION_LIST_SESSIONS, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_LIST_SESSIONS,
            status=STATUS_COMPLETED,
            message="Okta sessions retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def _verify_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        execution_result: ConnectorExecutionResult,
        actor: str,
    ) -> ConnectorExecutionResult:
        action = _safe_str(action).upper()
        user_id = self._require_user_id(payload)

        if action in {
            ACTION_DISABLE_USER,
            ACTION_SUSPEND_USER,
            ACTION_ENABLE_USER,
            ACTION_UNSUSPEND_USER,
            ACTION_DEACTIVATE_USER,
            ACTION_REACTIVATE_USER,
        }:
            response = self._request(
                "GET",
                f"/api/v1/users/{quote(user_id)}",
            )

            status = _safe_str((response.get("json") or {}).get("status")).upper()

            expected_sets = {
                ACTION_DISABLE_USER: {"SUSPENDED"},
                ACTION_SUSPEND_USER: {"SUSPENDED"},
                ACTION_ENABLE_USER: {"ACTIVE", "PROVISIONED", "STAGED"},
                ACTION_UNSUSPEND_USER: {"ACTIVE", "PROVISIONED", "STAGED"},
                ACTION_DEACTIVATE_USER: {"DEPROVISIONED"},
                ACTION_REACTIVATE_USER: {"PROVISIONED", "STAGED", "ACTIVE"},
            }

            ok = response["ok"] and status in expected_sets.get(action, set())

            return ConnectorExecutionResult(
                ok=ok,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_COMPLETED if ok else STATUS_FAILED,
                message="Okta user status verification passed." if ok else "Okta user status verification failed.",
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=user_id,
                simulated=False,
                verification_ok=ok,
                raw={
                    "expected": sorted(expected_sets.get(action, set())),
                    "actual": status,
                    "response": response,
                },
            )

        if action == ACTION_REVOKE_SESSIONS:
            return ConnectorExecutionResult(
                ok=True,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_COMPLETED,
                message="Session revocation API accepted; verification treated as accepted.",
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=user_id,
                simulated=False,
                verification_ok=True,
            )

        return super()._verify_real(
            action=action,
            payload=payload,
            execution_result=execution_result,
            actor=actor,
        )

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------

    def build_rollback_payload(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        action = _safe_str(action).upper()
        user_id = self._require_user_id(payload)

        if action in {ACTION_DISABLE_USER, ACTION_SUSPEND_USER}:
            return {
                "action": ACTION_UNSUSPEND_USER,
                "user_id": user_id,
                "tenant_id": self.tenant_id,
            }

        if action == ACTION_DEACTIVATE_USER:
            return {
                "action": ACTION_REACTIVATE_USER,
                "user_id": user_id,
                "tenant_id": self.tenant_id,
            }

        if action in {ACTION_ENABLE_USER, ACTION_UNSUSPEND_USER, ACTION_REACTIVATE_USER}:
            return {
                "action": ACTION_SUSPEND_USER,
                "user_id": user_id,
                "tenant_id": self.tenant_id,
            }

        if action == ACTION_REVOKE_SESSIONS:
            return {
                "action": "NO_ROLLBACK_AVAILABLE",
                "reason": "Session revocation cannot be reversed.",
                "user_id": user_id,
            }

        return {}

    def _rollback_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:
        rollback_action = _safe_str(action).upper()

        if rollback_action in {ACTION_UNSUSPEND_USER, ACTION_REACTIVATE_USER, ACTION_SUSPEND_USER}:
            return self._execute_real(
                action=rollback_action,
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        return self._failed(
            rollback_action,
            execution_id,
            f"No Okta rollback implementation for {rollback_action}.",
        )

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.ensure_authenticated()

        if not self.okta_domain or not self.api_token:
            return {
                "ok": False,
                "status_code": 0,
                "message": "Okta domain or API token unavailable.",
            }

        url = f"{self.okta_domain}{path}"

        headers = {
            "Authorization": f"SSWS {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=self.timeout,
        )

        text = response.text or ""
        data = None

        if text:
            try:
                data = response.json()
            except Exception:
                data = None

        ok = 200 <= response.status_code < 300

        return {
            "ok": ok,
            "status_code": response.status_code,
            "message": "OK" if ok else text[:1000],
            "json": data,
            "text": text[:2000],
            "url": url,
            "method": method.upper(),
        }

    def _require_user_id(self, payload: Dict[str, Any]) -> str:
        return _safe_str(
            payload.get("user_id")
            or payload.get("target_user")
            or payload.get("principal")
            or payload.get("login")
            or payload.get("email")
            or payload.get("userName")
        )

    def _failed(
        self,
        action: str,
        execution_id: str,
        message: str,
        *,
        raw: Optional[Dict[str, Any]] = None,
    ) -> ConnectorExecutionResult:
        return ConnectorExecutionResult(
            ok=False,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_FAILED,
            message=message,
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            simulated=self.simulation_mode,
            raw=raw or {},
        )