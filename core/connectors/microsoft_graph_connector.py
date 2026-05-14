"""
core/connectors/microsoft_graph_connector.py

Microsoft Graph Connector for Veridion Pro / CUI GovCloud App.

Supports:
- DISABLE_USER
- ENABLE_USER
- REVOKE_SESSIONS
- QUARANTINE_EMAIL
- DELETE_EMAIL
- SEARCH_MAILBOX
- GET_USER
- GET_MESSAGE
- LIST_SESSIONS

Safe by default:
- simulation_mode=True by default through BaseConnector
- destructive calls require governance approval upstream
- rollback payloads generated where possible
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
    STATUS_SIMULATED,
)


GRAPH_PUBLIC_BASE_URL = "https://graph.microsoft.com/v1.0"

GRAPH_PUBLIC_TOKEN_URL = (
    "https://login.microsoftonline.com/"
    "{tenant_id}/oauth2/v2.0/token"
)


ACTION_DISABLE_USER = "DISABLE_USER"
ACTION_ENABLE_USER = "ENABLE_USER"
ACTION_REVOKE_SESSIONS = "REVOKE_SESSIONS"
ACTION_QUARANTINE_EMAIL = "QUARANTINE_EMAIL"
ACTION_DELETE_EMAIL = "DELETE_EMAIL"
ACTION_SEARCH_MAILBOX = "SEARCH_MAILBOX"
ACTION_GET_USER = "GET_USER"
ACTION_GET_MESSAGE = "GET_MESSAGE"
ACTION_LIST_SESSIONS = "LIST_SESSIONS"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_str(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    try:
        return str(value)
    except Exception:
        return default


def _bool(value: Any) -> bool:
    return bool(value)


class MicrosoftGraphConnector(BaseConnector):

    connector_id = "microsoft_graph"

    connector_name = (
        "Microsoft Graph Connector"
    )

    vendor = "Microsoft"

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        *,
        tenant_id: str = "default",
        config: Optional[
            Dict[str, Any]
        ] = None,
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

        self.graph_base_url = (
            self.config.get(
                "graph_base_url"
            )
            or GRAPH_PUBLIC_BASE_URL
        )

        self.azure_tenant_id = (
            self.config.get(
                "azure_tenant_id"
            )
            or self.config.get(
                "tenant"
            )
        )

        self.client_id = self.config.get(
            "client_id"
        )

        self.client_secret = self.config.get(
            "client_secret"
        )

        self.access_token = self.config.get(
            "access_token"
        )

        self.timeout = int(
            self.config.get(
                "timeout",
                30,
            )
        )

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> Dict[
        str,
        ConnectorCapability,
    ]:

        return {

            ACTION_DISABLE_USER:
                ConnectorCapability(
                    name=ACTION_DISABLE_USER,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=True,
                    description=(
                        "Disable a Microsoft "
                        "Entra user."
                    ),
                ),

            ACTION_ENABLE_USER:
                ConnectorCapability(
                    name=ACTION_ENABLE_USER,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description=(
                        "Enable a Microsoft "
                        "Entra user."
                    ),
                ),

            ACTION_REVOKE_SESSIONS:
                ConnectorCapability(
                    name=ACTION_REVOKE_SESSIONS,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=False,
                    destructive=True,
                    description=(
                        "Revoke Microsoft "
                        "Graph sessions."
                    ),
                ),

            ACTION_QUARANTINE_EMAIL:
                ConnectorCapability(
                    name=ACTION_QUARANTINE_EMAIL,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description=(
                        "Move a message "
                        "to quarantine."
                    ),
                ),

            ACTION_DELETE_EMAIL:
                ConnectorCapability(
                    name=ACTION_DELETE_EMAIL,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=False,
                    destructive=True,
                    description=(
                        "Delete mailbox "
                        "message."
                    ),
                ),

            ACTION_SEARCH_MAILBOX:
                ConnectorCapability(
                    name=ACTION_SEARCH_MAILBOX,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description=(
                        "Search mailbox."
                    ),
                ),

            ACTION_GET_USER:
                ConnectorCapability(
                    name=ACTION_GET_USER,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description=(
                        "Retrieve user."
                    ),
                ),

            ACTION_GET_MESSAGE:
                ConnectorCapability(
                    name=ACTION_GET_MESSAGE,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description=(
                        "Retrieve message."
                    ),
                ),

            ACTION_LIST_SESSIONS:
                ConnectorCapability(
                    name=ACTION_LIST_SESSIONS,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description=(
                        "List sessions."
                    ),
                ),
        }

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(
        self,
    ) -> ConnectorAuthState:

        if self.simulation_mode:

            self.auth_state = (
                ConnectorAuthState(
                    authenticated=True,
                    auth_type="simulation",
                    metadata={
                        "simulation_mode": True
                    },
                )
            )

            return self.auth_state

        if self.access_token:

            self.auth_state = (
                ConnectorAuthState(
                    authenticated=True,
                    auth_type="bearer",
                    metadata={
                        "provided_token": True
                    },
                )
            )

            return self.auth_state

        if (
            not self.azure_tenant_id
            or not self.client_id
            or not self.client_secret
        ):

            self.auth_state = (
                ConnectorAuthState(
                    authenticated=False,
                    auth_type="client_credentials",
                    metadata={
                        "error": (
                            "Missing "
                            "Graph credentials."
                        )
                    },
                )
            )

            return self.auth_state

        token_url = (
            GRAPH_PUBLIC_TOKEN_URL.format(
                tenant_id=self.azure_tenant_id
            )
        )

        response = requests.post(
            token_url,
            data={
                "client_id":
                    self.client_id,
                "client_secret":
                    self.client_secret,
                "scope":
                    "https://graph.microsoft.com/.default",
                "grant_type":
                    "client_credentials",
            },
            timeout=self.timeout,
        )

        if response.status_code >= 400:

            self.auth_state = (
                ConnectorAuthState(
                    authenticated=False,
                    auth_type="client_credentials",
                    metadata={
                        "status_code":
                            response.status_code,
                        "body":
                            response.text[:1000],
                    },
                )
            )

            return self.auth_state

        data = response.json()

        self.access_token = data.get(
            "access_token"
        )

        self.auth_state = (
            ConnectorAuthState(
                authenticated=bool(
                    self.access_token
                ),
                auth_type=(
                    "client_credentials"
                ),
                token_expires_at_ms=(
                    _now_ms()
                    + int(
                        data.get(
                            "expires_in",
                            3600,
                        )
                    ) * 1000
                ),
                metadata={
                    "token_type":
                        data.get(
                            "token_type"
                        )
                },
            )
        )

        return self.auth_state

    def ensure_authenticated(
        self,
    ) -> ConnectorAuthState:

        if self.simulation_mode:
            return self.authenticate()

        if (
            self.auth_state.authenticated
            and self.auth_state.token_expires_at_ms
            and self.auth_state.token_expires_at_ms
            > _now_ms() + 60_000
        ):
            return self.auth_state

        return self.authenticate()

    # ------------------------------------------------------------------
    # Real Execution
    # ------------------------------------------------------------------

    def _execute_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        action = _safe_str(
            action
        ).upper()

        if action == ACTION_DISABLE_USER:

            return self._disable_or_enable_user(
                enabled=False,
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_ENABLE_USER:

            return self._disable_or_enable_user(
                enabled=True,
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_REVOKE_SESSIONS:

            return self._revoke_sessions(
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_QUARANTINE_EMAIL:

            return self._quarantine_email(
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_DELETE_EMAIL:

            return self._delete_email(
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_SEARCH_MAILBOX:

            return self._search_mailbox(
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_GET_USER:

            return self._get_user(
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_GET_MESSAGE:

            return self._get_message(
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        if action == ACTION_LIST_SESSIONS:

            return self._list_sessions(
                payload=payload,
                actor=actor,
                execution_id=execution_id,
            )

        return ConnectorExecutionResult(
            ok=False,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_FAILED,
            message=(
                f"Unsupported "
                f"action: {action}"
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            simulated=False,
        )

    # ------------------------------------------------------------------
    # Graph Actions
    # ------------------------------------------------------------------

    def _disable_or_enable_user(
        self,
        *,
        enabled: bool,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user_id = self._require_user_id(
            payload
        )

        action = (
            ACTION_ENABLE_USER
            if enabled
            else ACTION_DISABLE_USER
        )

        if not user_id:

            return self._failed(
                action,
                execution_id,
                "user_id is required.",
            )

        response = self._request(
            "PATCH",
            f"/users/{quote(user_id)}",
            json_body={
                "accountEnabled":
                    enabled
            },
        )

        if not response["ok"]:

            return self._failed(
                action,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_COMPLETED,
            message=(
                f"User "
                f"{'enabled' if enabled else 'disabled'}."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action":
                    ACTION_DISABLE_USER
                    if enabled
                    else ACTION_ENABLE_USER,
                "user_id":
                    user_id,
                "tenant_id":
                    self.tenant_id,
            },
            raw=response,
        )

    def _revoke_sessions(
        self,
        *,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user_id = self._require_user_id(
            payload
        )

        if not user_id:

            return self._failed(
                ACTION_REVOKE_SESSIONS,
                execution_id,
                "user_id is required.",
            )

        response = self._request(
            "POST",
            f"/users/{quote(user_id)}/revokeSignInSessions",
            json_body={},
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
            message=(
                "Sessions revoked."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            rollback_available=False,
            rollback_payload={
                "action":
                    "NO_ROLLBACK_AVAILABLE",
                "reason":
                    "Session revocation "
                    "cannot be reversed.",
            },
            raw=response,
        )

    # ------------------------------------------------------------------
    # Email Actions
    # ------------------------------------------------------------------

    def _quarantine_email(
        self,
        *,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        mailbox = (
            payload.get("mailbox")
            or payload.get("user_id")
        )

        message_id = payload.get(
            "message_id"
        )

        destination_folder = (
            payload.get(
                "destination_folder"
            )
            or payload.get(
                "folder_id"
            )
            or "deleteditems"
        )

        if not mailbox:

            return self._failed(
                ACTION_QUARANTINE_EMAIL,
                execution_id,
                (
                    "mailbox "
                    "is required."
                ),
            )

        if not message_id:

            return self._failed(
                ACTION_QUARANTINE_EMAIL,
                execution_id,
                (
                    "message_id "
                    "is required."
                ),
            )

        response = self._request(
            "POST",
            (
                f"/users/{quote(mailbox)}"
                f"/messages/{quote(message_id)}"
                f"/move"
            ),
            json_body={
                "destinationId":
                    destination_folder
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_QUARANTINE_EMAIL,
                execution_id,
                response["message"],
                raw=response,
            )

        moved_message = (
            response.get("json")
            or {}
        )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_QUARANTINE_EMAIL,
            status=STATUS_COMPLETED,
            message=(
                "Message quarantined."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=message_id,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action":
                    "RESTORE_EMAIL",
                "mailbox":
                    mailbox,
                "message_id":
                    moved_message.get("id")
                    or message_id,
            },
            raw=response,
        )

    def _delete_email(
        self,
        *,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        mailbox = (
            payload.get("mailbox")
            or payload.get("user_id")
        )

        message_id = payload.get(
            "message_id"
        )

        if not mailbox:

            return self._failed(
                ACTION_DELETE_EMAIL,
                execution_id,
                (
                    "mailbox "
                    "is required."
                ),
            )

        if not message_id:

            return self._failed(
                ACTION_DELETE_EMAIL,
                execution_id,
                (
                    "message_id "
                    "is required."
                ),
            )

        response = self._request(
            "DELETE",
            (
                f"/users/{quote(mailbox)}"
                f"/messages/{quote(message_id)}"
            ),
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
            message="Message deleted.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=message_id,
            simulated=False,
            rollback_available=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # Query Actions
    # ------------------------------------------------------------------

    def _search_mailbox(
        self,
        *,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        mailbox = (
            payload.get("mailbox")
            or payload.get("user_id")
        )

        query = (
            payload.get("query")
            or payload.get("search")
            or ""
        )

        top = int(
            payload.get("top")
            or 25
        )

        if not mailbox:

            return self._failed(
                ACTION_SEARCH_MAILBOX,
                execution_id,
                (
                    "mailbox "
                    "is required."
                ),
            )

        params = {
            "$top":
                min(max(top, 1), 100),
            "$select":
                (
                    "id,subject,from,"
                    "receivedDateTime,"
                    "internetMessageId,"
                    "hasAttachments"
                ),
            "$orderby":
                "receivedDateTime desc",
        }

        if query:
            params["$search"] = (
                f'"{query}"'
            )

        response = self._request(
            "GET",
            (
                f"/users/{quote(mailbox)}"
                f"/messages"
            ),
            params=params,
        )

        if not response["ok"]:

            return self._failed(
                ACTION_SEARCH_MAILBOX,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_SEARCH_MAILBOX,
            status=STATUS_COMPLETED,
            message="Mailbox search completed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=mailbox,
            simulated=False,
            raw=response,
        )

    def _get_user(
        self,
        *,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user_id = self._require_user_id(
            payload
        )

        if not user_id:

            return self._failed(
                ACTION_GET_USER,
                execution_id,
                "user_id is required.",
            )

        response = self._request(
            "GET",
            f"/users/{quote(user_id)}",
            params={
                "$select":
                    (
                        "id,displayName,"
                        "userPrincipalName,"
                        "mail,"
                        "accountEnabled"
                    )
            },
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
            message="User retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            raw=response,
        )

    def _get_message(
        self,
        *,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        mailbox = (
            payload.get("mailbox")
            or payload.get("user_id")
        )

        message_id = payload.get(
            "message_id"
        )

        if not mailbox:

            return self._failed(
                ACTION_GET_MESSAGE,
                execution_id,
                (
                    "mailbox "
                    "is required."
                ),
            )

        if not message_id:

            return self._failed(
                ACTION_GET_MESSAGE,
                execution_id,
                (
                    "message_id "
                    "is required."
                ),
            )

        response = self._request(
            "GET",
            (
                f"/users/{quote(mailbox)}"
                f"/messages/{quote(message_id)}"
            ),
        )

        if not response["ok"]:

            return self._failed(
                ACTION_GET_MESSAGE,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_MESSAGE,
            status=STATUS_COMPLETED,
            message="Message retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=message_id,
            simulated=False,
            raw=response,
        )

    def _list_sessions(
        self,
        *,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:

        user_id = self._require_user_id(
            payload
        )

        if not user_id:

            return self._failed(
                ACTION_LIST_SESSIONS,
                execution_id,
                "user_id is required.",
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_LIST_SESSIONS,
            status=STATUS_COMPLETED,
            message=(
                "Session listing "
                "placeholder."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=user_id,
            simulated=False,
            raw={
                "user_id":
                    user_id
            },
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def _verify_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        execution_result:
            ConnectorExecutionResult,
        actor: str,
    ) -> ConnectorExecutionResult:

        action = _safe_str(
            action
        ).upper()

        if action in {
            ACTION_DISABLE_USER,
            ACTION_ENABLE_USER,
        }:

            user_id = (
                self._require_user_id(
                    payload
                )
            )

            expected = (
                action
                == ACTION_ENABLE_USER
            )

            response = self._request(
                "GET",
                f"/users/{quote(user_id)}",
                params={
                    "$select":
                        (
                            "id,"
                            "accountEnabled"
                        )
                },
            )

            actual = None

            if response["ok"]:

                actual = (
                    response
                    .get("json", {})
                    .get(
                        "accountEnabled"
                    )
                )

            ok = (
                response["ok"]
                and bool(actual)
                == expected
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
                    "Verification "
                    "passed."
                    if ok
                    else
                    "Verification "
                    "failed."
                ),
                execution_id=(
                    execution_result
                    .execution_id
                ),
                tenant_id=self.tenant_id,
                target_id=user_id,
                simulated=False,
                verification_ok=ok,
                raw={
                    "expected":
                        expected,
                    "actual":
                        actual,
                    "response":
                        response,
                },
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

        action = _safe_str(
            action
        ).upper()

        if action == ACTION_DISABLE_USER:

            return {
                "action":
                    ACTION_ENABLE_USER,
                "user_id":
                    self._require_user_id(
                        payload
                    ),
                "tenant_id":
                    self.tenant_id,
            }

        if action == ACTION_ENABLE_USER:

            return {
                "action":
                    ACTION_DISABLE_USER,
                "user_id":
                    self._require_user_id(
                        payload
                    ),
                "tenant_id":
                    self.tenant_id,
            }

        return {}

    # ------------------------------------------------------------------
    # HTTP Helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[
            Dict[str, Any]
        ] = None,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        self.ensure_authenticated()

        if not self.access_token:

            return {
                "ok": False,
                "status_code": 0,
                "message":
                    (
                        "Access token "
                        "unavailable."
                    ),
            }

        url = (
            f"{self.graph_base_url}"
            f"{path}"
        )

        headers = {
            "Authorization":
                (
                    f"Bearer "
                    f"{self.access_token}"
                ),
            "Content-Type":
                "application/json",
            "Accept":
                "application/json",
        }

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=json_body,
            params=params,
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
            "ok":
                ok,
            "status_code":
                response.status_code,
            "message":
                (
                    "OK"
                    if ok
                    else text[:1000]
                ),
            "json":
                data,
            "text":
                text[:2000],
            "url":
                url,
            "method":
                method.upper(),
        }

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _require_user_id(
        self,
        payload: Dict[str, Any],
    ) -> str:

        return _safe_str(
            payload.get("user_id")
            or payload.get(
                "target_user"
            )
            or payload.get(
                "principal"
            )
            or payload.get(
                "userPrincipalName"
            )
        )

    def _failed(
        self,
        action: str,
        execution_id: str,
        message: str,
        *,
        raw: Optional[
            Dict[str, Any]
        ] = None,
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