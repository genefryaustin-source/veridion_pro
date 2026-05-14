"""
core/connectors/google_workspace_connector.py

Google Workspace Connector for Veridion Pro / CUI GovCloud App.

Supports:
- DISABLE_USER
- ENABLE_USER
- REVOKE_SESSIONS
- GET_USER
- SEARCH_USERS
- SEARCH_GMAIL
- DELETE_EMAIL
- QUARANTINE_EMAIL
- GET_DRIVE_FILE
- LOCK_DRIVE_FILE
- ADD_DRIVE_LABEL

Safe by default:
- simulation_mode=True through BaseConnector
- safety guardrails execute before real actions
- rollback-aware mailbox and identity actions
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

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
ACTION_REVOKE_SESSIONS = "REVOKE_SESSIONS"

ACTION_GET_USER = "GET_USER"
ACTION_SEARCH_USERS = "SEARCH_USERS"

ACTION_SEARCH_GMAIL = "SEARCH_GMAIL"
ACTION_DELETE_EMAIL = "DELETE_EMAIL"
ACTION_QUARANTINE_EMAIL = "QUARANTINE_EMAIL"

ACTION_GET_DRIVE_FILE = "GET_DRIVE_FILE"
ACTION_LOCK_DRIVE_FILE = "LOCK_DRIVE_FILE"
ACTION_ADD_DRIVE_LABEL = "ADD_DRIVE_LABEL"

DEFAULT_BASE_URL = "https://admin.googleapis.com"
DEFAULT_GMAIL_BASE = "https://gmail.googleapis.com"
DEFAULT_DRIVE_BASE = "https://www.googleapis.com"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    return [value]


class GoogleWorkspaceConnector(BaseConnector):

    connector_id = "google_workspace"
    connector_name = "Google Workspace Connector"
    vendor = "Google"

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

        self.access_token = (
            self.config.get("access_token")
        )

        self.base_url = (
            self.config.get("base_url")
            or DEFAULT_BASE_URL
        ).rstrip("/")

        self.gmail_base = (
            self.config.get("gmail_base")
            or DEFAULT_GMAIL_BASE
        ).rstrip("/")

        self.drive_base = (
            self.config.get("drive_base")
            or DEFAULT_DRIVE_BASE
        ).rstrip("/")

        self.timeout = int(
            self.config.get("timeout", 30)
        )

    # ------------------------------------------------------------------
    # CAPABILITIES
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> Dict[str, ConnectorCapability]:

        return {

            ACTION_DISABLE_USER:
                ConnectorCapability(
                    name=ACTION_DISABLE_USER,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=True,
                    description="Suspend Google Workspace user.",
                ),

            ACTION_ENABLE_USER:
                ConnectorCapability(
                    name=ACTION_ENABLE_USER,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Unsuspend Google Workspace user.",
                ),

            ACTION_REVOKE_SESSIONS:
                ConnectorCapability(
                    name=ACTION_REVOKE_SESSIONS,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=False,
                    destructive=True,
                    description="Revoke user sessions/tokens.",
                ),

            ACTION_GET_USER:
                ConnectorCapability(
                    name=ACTION_GET_USER,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="Get Workspace user.",
                ),

            ACTION_SEARCH_USERS:
                ConnectorCapability(
                    name=ACTION_SEARCH_USERS,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="Search Workspace users.",
                ),

            ACTION_SEARCH_GMAIL:
                ConnectorCapability(
                    name=ACTION_SEARCH_GMAIL,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="Search Gmail mailbox.",
                ),

            ACTION_DELETE_EMAIL:
                ConnectorCapability(
                    name=ACTION_DELETE_EMAIL,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=False,
                    destructive=True,
                    description="Delete Gmail message.",
                ),

            ACTION_QUARANTINE_EMAIL:
                ConnectorCapability(
                    name=ACTION_QUARANTINE_EMAIL,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Move Gmail message to quarantine label.",
                ),

            ACTION_GET_DRIVE_FILE:
                ConnectorCapability(
                    name=ACTION_GET_DRIVE_FILE,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="Retrieve Drive file metadata.",
                ),

            ACTION_LOCK_DRIVE_FILE:
                ConnectorCapability(
                    name=ACTION_LOCK_DRIVE_FILE,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Restrict Drive file modifications.",
                ),

            ACTION_ADD_DRIVE_LABEL:
                ConnectorCapability(
                    name=ACTION_ADD_DRIVE_LABEL,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Apply Drive governance label.",
                ),
        }

    # ------------------------------------------------------------------
    # AUTH
    # ------------------------------------------------------------------

    def authenticate(
        self,
    ) -> ConnectorAuthState:

        if self.simulation_mode:

            self.auth_state = ConnectorAuthState(
                authenticated=True,
                auth_type="simulation",
                metadata={
                    "simulation_mode": True,
                },
            )

            return self.auth_state

        if not self.access_token:

            self.auth_state = ConnectorAuthState(
                authenticated=False,
                auth_type="oauth2_bearer",
                metadata={
                    "error": "Missing Google access token.",
                },
            )

            return self.auth_state

        self.auth_state = ConnectorAuthState(
            authenticated=True,
            auth_type="oauth2_bearer",
            metadata={
                "base_url": self.base_url,
            },
        )

        return self.auth_state

    def ensure_authenticated(
        self,
    ) -> ConnectorAuthState:

        if not self.auth_state.authenticated:
            return self.authenticate()

        return self.auth_state

    # ------------------------------------------------------------------
    # EXECUTION
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

        if action == ACTION_DISABLE_USER:

            return self._set_user_state(
                action=ACTION_DISABLE_USER,
                suspended=True,
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_ENABLE_USER:

            return self._set_user_state(
                action=ACTION_ENABLE_USER,
                suspended=False,
                payload=payload,
                execution_id=execution_id,
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

        if action == ACTION_SEARCH_GMAIL:

            return self._search_gmail(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_DELETE_EMAIL:

            return self._delete_email(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_QUARANTINE_EMAIL:

            return self._quarantine_email(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_GET_DRIVE_FILE:

            return self._get_drive_file(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_LOCK_DRIVE_FILE:

            return self._lock_drive_file(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_ADD_DRIVE_LABEL:

            return self._add_drive_label(
                payload=payload,
                execution_id=execution_id,
            )

        return self._failed(
            action,
            execution_id,
            f"Unsupported Google Workspace action: {action}",
        )

    # ------------------------------------------------------------------
    # USERS
    # ------------------------------------------------------------------

    def _set_user_state(
        self,
        *,
        action: str,
        suspended: bool,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user = self._user(payload)

        if not user:

            return self._failed(
                action,
                execution_id,
                "user/email required.",
            )

        response = self._request(
            "PUT",
            f"{self.base_url}/admin/directory/v1/users/{user}",
            json_body={
                "suspended": suspended,
            },
        )

        if not response["ok"]:

            return self._failed(
                action,
                execution_id,
                response["message"],
                raw=response,
            )

        rollback_action = (
            ACTION_ENABLE_USER
            if suspended
            else ACTION_DISABLE_USER
        )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_COMPLETED,
            message=(
                "Google Workspace user suspended."
                if suspended
                else "Google Workspace user enabled."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": rollback_action,
                "user": user,
                "tenant_id": self.tenant_id,
            },
            raw=response,
        )

    def _revoke_sessions(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user = self._user(payload)

        if not user:

            return self._failed(
                ACTION_REVOKE_SESSIONS,
                execution_id,
                "user/email required.",
            )

        response = self._request(
            "POST",
            f"{self.base_url}/admin/directory/v1/users/{user}/signOut",
        )

        if not response["ok"]:

            return self._failed(
                ACTION_REVOKE_SESSIONS,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_REVOKE_SESSIONS,
            status=STATUS_COMPLETED,
            message="Google Workspace sessions revoked.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user,
            simulated=False,
            rollback_available=False,
            raw=response,
        )

    def _get_user(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user = self._user(payload)

        if not user:

            return self._failed(
                ACTION_GET_USER,
                execution_id,
                "user/email required.",
            )

        response = self._request(
            "GET",
            f"{self.base_url}/admin/directory/v1/users/{user}",
        )

        if not response["ok"]:

            return self._failed(
                ACTION_GET_USER,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_USER,
            status=STATUS_COMPLETED,
            message="Workspace user retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user,
            simulated=False,
            raw=response,
        )

    def _search_users(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        query = (
            payload.get("query")
            or ""
        )

        response = self._request(
            "GET",
            f"{self.base_url}/admin/directory/v1/users",
            params={
                "query": query,
                "maxResults": min(
                    max(
                        int(payload.get("limit") or 25),
                        1,
                    ),
                    500,
                ),
                "customer": "my_customer",
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_SEARCH_USERS,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_SEARCH_USERS,
            status=STATUS_COMPLETED,
            message="Workspace user search completed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=query,
            simulated=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # GMAIL
    # ------------------------------------------------------------------

    def _search_gmail(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user = self._user(payload)

        query = (
            payload.get("query")
            or ""
        )

        response = self._request(
            "GET",
            f"{self.gmail_base}/gmail/v1/users/{user}/messages",
            params={
                "q": query,
                "maxResults": min(
                    max(
                        int(payload.get("limit") or 25),
                        1,
                    ),
                    500,
                ),
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_SEARCH_GMAIL,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_SEARCH_GMAIL,
            status=STATUS_COMPLETED,
            message="Gmail search completed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user,
            simulated=False,
            raw=response,
        )

    def _delete_email(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user = self._user(payload)

        message_id = (
            payload.get("message_id")
        )

        if not user or not message_id:

            return self._failed(
                ACTION_DELETE_EMAIL,
                execution_id,
                "user and message_id required.",
            )

        response = self._request(
            "DELETE",
            f"{self.gmail_base}/gmail/v1/users/{user}/messages/{message_id}",
        )

        if not response["ok"]:

            return self._failed(
                ACTION_DELETE_EMAIL,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_DELETE_EMAIL,
            status=STATUS_COMPLETED,
            message="Gmail message deleted.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=message_id,
            simulated=False,
            rollback_available=False,
            raw=response,
        )

    def _quarantine_email(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user = self._user(payload)

        message_id = (
            payload.get("message_id")
        )

        quarantine_label = (
            payload.get("quarantine_label")
            or "QUARANTINE"
        )

        if not user or not message_id:

            return self._failed(
                ACTION_QUARANTINE_EMAIL,
                execution_id,
                "user and message_id required.",
            )

        response = self._request(
            "POST",
            f"{self.gmail_base}/gmail/v1/users/{user}/messages/{message_id}/modify",
            json_body={
                "addLabelIds": [
                    quarantine_label,
                ]
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_QUARANTINE_EMAIL,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_QUARANTINE_EMAIL,
            status=STATUS_COMPLETED,
            message="Gmail message quarantined.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=message_id,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": "REMOVE_GMAIL_LABEL",
                "message_id": message_id,
                "label": quarantine_label,
                "user": user,
                "tenant_id": self.tenant_id,
            },
            raw=response,
        )

    # ------------------------------------------------------------------
    # DRIVE
    # ------------------------------------------------------------------

    def _get_drive_file(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        file_id = (
            payload.get("file_id")
        )

        if not file_id:

            return self._failed(
                ACTION_GET_DRIVE_FILE,
                execution_id,
                "file_id required.",
            )

        response = self._request(
            "GET",
            f"{self.drive_base}/drive/v3/files/{file_id}",
        )

        if not response["ok"]:

            return self._failed(
                ACTION_GET_DRIVE_FILE,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_DRIVE_FILE,
            status=STATUS_COMPLETED,
            message="Drive file retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=file_id,
            simulated=False,
            raw=response,
        )

    def _lock_drive_file(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        file_id = (
            payload.get("file_id")
        )

        if not file_id:

            return self._failed(
                ACTION_LOCK_DRIVE_FILE,
                execution_id,
                "file_id required.",
            )

        response = self._request(
            "PATCH",
            f"{self.drive_base}/drive/v3/files/{file_id}",
            json_body={
                "copyRequiresWriterPermission": True,
                "writersCanShare": False,
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_LOCK_DRIVE_FILE,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_LOCK_DRIVE_FILE,
            status=STATUS_COMPLETED,
            message="Drive file locked.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=file_id,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": "UNLOCK_DRIVE_FILE",
                "file_id": file_id,
                "tenant_id": self.tenant_id,
            },
            raw=response,
        )

    def _add_drive_label(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        file_id = (
            payload.get("file_id")
        )

        label = (
            payload.get("label")
            or "CUI"
        )

        if not file_id:

            return self._failed(
                ACTION_ADD_DRIVE_LABEL,
                execution_id,
                "file_id required.",
            )

        response = self._request(
            "POST",
            f"{self.drive_base}/drive/v3/files/{file_id}/modifyLabels",
            json_body={
                "labelModifications": [
                    {
                        "fieldId": label,
                    }
                ]
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_ADD_DRIVE_LABEL,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_ADD_DRIVE_LABEL,
            status=STATUS_COMPLETED,
            message="Drive label added.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=file_id,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": "REMOVE_DRIVE_LABEL",
                "file_id": file_id,
                "label": label,
                "tenant_id": self.tenant_id,
            },
            raw=response,
        )

    # ------------------------------------------------------------------
    # VERIFY
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

        if action in {
            ACTION_DISABLE_USER,
            ACTION_ENABLE_USER,
        }:

            user = self._user(payload)

            response = self._request(
                "GET",
                f"{self.base_url}/admin/directory/v1/users/{user}",
            )

            data = (
                response.get("json")
                or {}
            )

            suspended = bool(
                data.get("suspended")
            )

            expected = (
                action == ACTION_DISABLE_USER
            )

            ok = (
                response["ok"]
                and suspended == expected
            )

            return ConnectorExecutionResult(
                ok=ok,
                connector_id=self.connector_id,
                action=action,
                status=(
                    STATUS_COMPLETED
                    if ok
                    else STATUS_FAILED
                ),
                message=(
                    "Workspace user verification passed."
                    if ok
                    else "Workspace user verification failed."
                ),
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=user,
                simulated=False,
                verification_ok=ok,
                raw=response,
            )

        return super()._verify_real(
            action=action,
            payload=payload,
            execution_result=execution_result,
            actor=actor,
        )

    # ------------------------------------------------------------------
    # ROLLBACK
    # ------------------------------------------------------------------

    def build_rollback_payload(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        action = _safe_str(action).upper()

        if action == ACTION_DISABLE_USER:

            return {
                "action": ACTION_ENABLE_USER,
                "user": self._user(payload),
                "tenant_id": self.tenant_id,
            }

        if action == ACTION_ENABLE_USER:

            return {
                "action": ACTION_DISABLE_USER,
                "user": self._user(payload),
                "tenant_id": self.tenant_id,
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

        if rollback_action in {
            ACTION_ENABLE_USER,
            ACTION_DISABLE_USER,
        }:

            return self._execute_real(
                action=rollback_action,
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        return self._failed(
            rollback_action,
            execution_id,
            f"No rollback implementation for {rollback_action}.",
        )

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Any] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        self.ensure_authenticated()

        if not self.access_token:

            return {
                "ok": False,
                "status_code": 0,
                "message": (
                    "Google access token unavailable."
                ),
            }

        headers = {
            "Authorization": (
                f"Bearer {self.access_token}"
            ),
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

        ok = (
            200
            <= response.status_code
            < 300
        )

        return {
            "ok": ok,
            "status_code": response.status_code,
            "message": (
                "OK"
                if ok
                else text[:1000]
            ),
            "json": data,
            "text": text[:2000],
            "url": url,
            "method": method.upper(),
        }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _user(
        self,
        payload: Dict[str, Any],
    ) -> str:

        return _safe_str(
            payload.get("user")
            or payload.get("email")
            or payload.get("principal")
            or payload.get("user_id")
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