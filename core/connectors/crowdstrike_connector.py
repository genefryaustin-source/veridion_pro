"""
core/connectors/crowdstrike_connector.py

CrowdStrike Falcon Connector for Veridion Pro / CUI GovCloud App.

Supports:
- ISOLATE_ENDPOINT
- UNISOLATE_ENDPOINT
- CONTAIN_HOST
- RELEASE_HOST
- GET_HOST
- SEARCH_HOSTS
- GET_DETECTIONS
- ADD_IOC
- REMOVE_IOC
- LIST_PROCESSES
- KILL_PROCESS

Safe by default:
- simulation_mode=True through BaseConnector
- safety guardrails execute in BaseConnector before real actions
- destructive endpoint actions require governance approval upstream
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
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


ACTION_ISOLATE_ENDPOINT = "ISOLATE_ENDPOINT"
ACTION_UNISOLATE_ENDPOINT = "UNISOLATE_ENDPOINT"
ACTION_CONTAIN_HOST = "CONTAIN_HOST"
ACTION_RELEASE_HOST = "RELEASE_HOST"
ACTION_GET_HOST = "GET_HOST"
ACTION_SEARCH_HOSTS = "SEARCH_HOSTS"
ACTION_GET_DETECTIONS = "GET_DETECTIONS"
ACTION_ADD_IOC = "ADD_IOC"
ACTION_REMOVE_IOC = "REMOVE_IOC"
ACTION_LIST_PROCESSES = "LIST_PROCESSES"
ACTION_KILL_PROCESS = "KILL_PROCESS"


DEFAULT_BASE_URL = "https://api.crowdstrike.com"
TOKEN_PATH = "/oauth2/token"


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


class CrowdStrikeConnector(BaseConnector):
    connector_id = "crowdstrike"
    connector_name = "CrowdStrike Falcon Connector"
    vendor = "CrowdStrike"

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

        self.base_url = (
            self.config.get("base_url")
            or self.config.get("falcon_base_url")
            or DEFAULT_BASE_URL
        ).rstrip("/")

        self.client_id = self.config.get("client_id")
        self.client_secret = self.config.get("client_secret")
        self.access_token = self.config.get("access_token")
        self.timeout = int(self.config.get("timeout", 30))

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(self) -> Dict[str, ConnectorCapability]:
        return {
            ACTION_ISOLATE_ENDPOINT: ConnectorCapability(
                name=ACTION_ISOLATE_ENDPOINT,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=True,
                description="Contain/isolate a Falcon host.",
            ),
            ACTION_CONTAIN_HOST: ConnectorCapability(
                name=ACTION_CONTAIN_HOST,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=True,
                description="Alias for ISOLATE_ENDPOINT.",
            ),
            ACTION_UNISOLATE_ENDPOINT: ConnectorCapability(
                name=ACTION_UNISOLATE_ENDPOINT,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=False,
                description="Lift Falcon host containment.",
            ),
            ACTION_RELEASE_HOST: ConnectorCapability(
                name=ACTION_RELEASE_HOST,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=False,
                description="Alias for UNISOLATE_ENDPOINT.",
            ),
            ACTION_GET_HOST: ConnectorCapability(
                name=ACTION_GET_HOST,
                supported=True,
                requires_approval=False,
                supports_rollback=False,
                destructive=False,
                description="Get Falcon host details.",
            ),
            ACTION_SEARCH_HOSTS: ConnectorCapability(
                name=ACTION_SEARCH_HOSTS,
                supported=True,
                requires_approval=False,
                supports_rollback=False,
                destructive=False,
                description="Search Falcon hosts.",
            ),
            ACTION_GET_DETECTIONS: ConnectorCapability(
                name=ACTION_GET_DETECTIONS,
                supported=True,
                requires_approval=False,
                supports_rollback=False,
                destructive=False,
                description="Search Falcon detections.",
            ),
            ACTION_ADD_IOC: ConnectorCapability(
                name=ACTION_ADD_IOC,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=False,
                description="Create a custom IOC indicator.",
            ),
            ACTION_REMOVE_IOC: ConnectorCapability(
                name=ACTION_REMOVE_IOC,
                supported=True,
                requires_approval=True,
                supports_rollback=True,
                destructive=False,
                description="Delete custom IOC indicators.",
            ),
            ACTION_LIST_PROCESSES: ConnectorCapability(
                name=ACTION_LIST_PROCESSES,
                supported=True,
                requires_approval=False,
                supports_rollback=False,
                destructive=False,
                description="Placeholder for RTR process listing.",
            ),
            ACTION_KILL_PROCESS: ConnectorCapability(
                name=ACTION_KILL_PROCESS,
                supported=True,
                requires_approval=True,
                supports_rollback=False,
                destructive=True,
                description="Placeholder for RTR process termination.",
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

        if self.access_token:
            self.auth_state = ConnectorAuthState(
                authenticated=True,
                auth_type="bearer",
                metadata={"provided_token": True},
            )
            return self.auth_state

        if not self.client_id or not self.client_secret:
            self.auth_state = ConnectorAuthState(
                authenticated=False,
                auth_type="oauth2_client_credentials",
                metadata={"error": "Missing CrowdStrike client_id/client_secret."},
            )
            return self.auth_state

        response = requests.post(
            f"{self.base_url}{TOKEN_PATH}",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            self.auth_state = ConnectorAuthState(
                authenticated=False,
                auth_type="oauth2_client_credentials",
                metadata={
                    "status_code": response.status_code,
                    "body": response.text[:1000],
                },
            )
            return self.auth_state

        data = response.json()
        self.access_token = data.get("access_token")

        self.auth_state = ConnectorAuthState(
            authenticated=bool(self.access_token),
            auth_type="oauth2_client_credentials",
            token_expires_at_ms=_now_ms() + int(data.get("expires_in", 1800)) * 1000,
            metadata={
                "token_type": data.get("token_type"),
                "base_url": self.base_url,
            },
        )
        return self.auth_state

    def ensure_authenticated(self) -> ConnectorAuthState:
        if self.simulation_mode:
            return self.authenticate()

        if (
            self.auth_state.authenticated
            and self.auth_state.token_expires_at_ms
            and self.auth_state.token_expires_at_ms > _now_ms() + 60_000
        ):
            return self.auth_state

        return self.authenticate()

    # ------------------------------------------------------------------
    # Execution
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

        if action in {ACTION_ISOLATE_ENDPOINT, ACTION_CONTAIN_HOST}:
            return self._contain_or_release_host(
                action=ACTION_ISOLATE_ENDPOINT,
                command="contain",
                payload=payload,
                execution_id=execution_id,
            )

        if action in {ACTION_UNISOLATE_ENDPOINT, ACTION_RELEASE_HOST}:
            return self._contain_or_release_host(
                action=ACTION_UNISOLATE_ENDPOINT,
                command="lift_containment",
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_GET_HOST:
            return self._get_host(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_SEARCH_HOSTS:
            return self._search_hosts(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_GET_DETECTIONS:
            return self._get_detections(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_ADD_IOC:
            return self._add_ioc(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_REMOVE_IOC:
            return self._remove_ioc(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_LIST_PROCESSES:
            return self._list_processes(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_KILL_PROCESS:
            return self._kill_process(
                payload=payload,
                execution_id=execution_id,
            )

        return self._failed(action, execution_id, f"Unsupported CrowdStrike action: {action}")

    # ------------------------------------------------------------------
    # Host Containment
    # ------------------------------------------------------------------

    def _contain_or_release_host(
        self,
        *,
        action: str,
        command: str,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        host_ids = self._host_ids(payload)

        if not host_ids:
            return self._failed(action, execution_id, "host_id, device_id, aid, or ids is required.")

        response = self._request(
            "POST",
            "/devices/entities/devices-actions/v2",
            params={"action_name": command},
            json_body={"ids": host_ids},
        )

        if not response["ok"]:
            return self._failed(action, execution_id, response["message"], raw=response)

        rollback_action = (
            ACTION_UNISOLATE_ENDPOINT
            if command == "contain"
            else ACTION_ISOLATE_ENDPOINT
        )

        event_type = (
            "ENDPOINT_ISOLATED"
            if command == "contain"
            else "ENDPOINT_RELEASED"
        )

        self._emit(
            event_type,
            {
                "execution_id": execution_id,
                "connector_id": self.connector_id,
                "tenant_id": self.tenant_id,
                "host_ids": host_ids,
                "action": action,
            },
            severity="HIGH" if command == "contain" else "MEDIUM",
        )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_COMPLETED,
            message=f"CrowdStrike host action completed: {command}.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=",".join(host_ids),
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": rollback_action,
                "ids": host_ids,
                "tenant_id": self.tenant_id,
            },
            raw=response,
        )

    def _get_host(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        host_ids = self._host_ids(payload)

        if not host_ids:
            return self._failed(ACTION_GET_HOST, execution_id, "host_id, device_id, aid, or ids is required.")

        response = self._request(
            "GET",
            "/devices/entities/devices/v2",
            params=[("ids", hid) for hid in host_ids],
        )

        if not response["ok"]:
            return self._failed(ACTION_GET_HOST, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_HOST,
            status=STATUS_COMPLETED,
            message="CrowdStrike host details retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=",".join(host_ids),
            simulated=False,
            raw=response,
        )

    def _search_hosts(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        filter_value = (
            payload.get("filter")
            or payload.get("query")
            or payload.get("hostname_filter")
            or ""
        )

        limit = min(max(int(payload.get("limit") or 25), 1), 500)

        params = {
            "limit": limit,
        }

        if filter_value:
            params["filter"] = filter_value

        response = self._request(
            "GET",
            "/devices/queries/devices/v1",
            params=params,
        )

        if not response["ok"]:
            return self._failed(ACTION_SEARCH_HOSTS, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_SEARCH_HOSTS,
            status=STATUS_COMPLETED,
            message="CrowdStrike host search completed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=filter_value,
            simulated=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # Detections
    # ------------------------------------------------------------------

    def _get_detections(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        filter_value = payload.get("filter") or payload.get("query") or ""
        limit = min(max(int(payload.get("limit") or 25), 1), 500)

        params = {
            "limit": limit,
            "sort": payload.get("sort") or "first_behavior.desc",
        }

        if filter_value:
            params["filter"] = filter_value

        response = self._request(
            "GET",
            "/detects/queries/detects/v1",
            params=params,
        )

        if not response["ok"]:
            return self._failed(ACTION_GET_DETECTIONS, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_DETECTIONS,
            status=STATUS_COMPLETED,
            message="CrowdStrike detections query completed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=filter_value,
            simulated=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # IOC Management
    # ------------------------------------------------------------------

    def _add_ioc(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        indicator_type = payload.get("type") or payload.get("indicator_type")
        value = payload.get("value") or payload.get("indicator")
        action = payload.get("ioc_action") or payload.get("policy_action") or "detect"
        severity = payload.get("severity") or "medium"
        platform = payload.get("platform") or "windows"
        description = payload.get("description") or "Added by Veridion Pro."

        if not indicator_type or not value:
            return self._failed(ACTION_ADD_IOC, execution_id, "IOC type and value are required.")

        body = {
            "indicators": [
                {
                    "type": indicator_type,
                    "value": value,
                    "action": action,
                    "severity": severity,
                    "platforms": [platform] if isinstance(platform, str) else platform,
                    "description": description,
                    "source": payload.get("source") or "veridion_pro",
                }
            ]
        }

        response = self._request(
            "POST",
            "/iocs/entities/indicators/v1",
            json_body=body,
        )

        if not response["ok"]:
            return self._failed(ACTION_ADD_IOC, execution_id, response["message"], raw=response)

        resources = (response.get("json") or {}).get("resources") or []
        indicator_ids = [
            item.get("id")
            for item in resources
            if isinstance(item, dict) and item.get("id")
        ]

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_ADD_IOC,
            status=STATUS_COMPLETED,
            message="CrowdStrike IOC added.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=value,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": ACTION_REMOVE_IOC,
                "ids": indicator_ids,
                "value": value,
                "type": indicator_type,
                "tenant_id": self.tenant_id,
            },
            raw=response,
        )

    def _remove_ioc(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        ids = [
            _safe_str(x)
            for x in _as_list(payload.get("ids") or payload.get("indicator_ids") or payload.get("id"))
            if _safe_str(x)
        ]

        filter_value = payload.get("filter")

        if not ids and not filter_value:
            return self._failed(ACTION_REMOVE_IOC, execution_id, "IOC ids or filter is required.")

        params: Dict[str, Any] = {}

        if filter_value:
            params["filter"] = filter_value

        response = self._request(
            "DELETE",
            "/iocs/entities/indicators/v1",
            params=params,
            json_body={"ids": ids} if ids else None,
        )

        if not response["ok"]:
            return self._failed(ACTION_REMOVE_IOC, execution_id, response["message"], raw=response)

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_REMOVE_IOC,
            status=STATUS_COMPLETED,
            message="CrowdStrike IOC removed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=",".join(ids) if ids else filter_value,
            simulated=False,
            rollback_available=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # RTR Placeholders
    # ------------------------------------------------------------------

    def _list_processes(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        return ConnectorExecutionResult(
            ok=False,
            connector_id=self.connector_id,
            action=ACTION_LIST_PROCESSES,
            status=STATUS_FAILED,
            message=(
                "LIST_PROCESSES requires CrowdStrike RTR session orchestration. "
                "Stubbed until RTR workflow module is added."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            simulated=False,
            raw={"payload": payload},
        )

    def _kill_process(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:
        return ConnectorExecutionResult(
            ok=False,
            connector_id=self.connector_id,
            action=ACTION_KILL_PROCESS,
            status=STATUS_FAILED,
            message=(
                "KILL_PROCESS requires CrowdStrike RTR session orchestration. "
                "Stubbed until RTR workflow module is added."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            simulated=False,
            raw={"payload": payload},
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

        if action in {
            ACTION_ISOLATE_ENDPOINT,
            ACTION_CONTAIN_HOST,
            ACTION_UNISOLATE_ENDPOINT,
            ACTION_RELEASE_HOST,
        }:
            host_ids = self._host_ids(payload)

            response = self._request(
                "GET",
                "/devices/entities/devices/v2",
                params=[("ids", hid) for hid in host_ids],
            )

            resources = (response.get("json") or {}).get("resources") or []

            expected_contained = action in {ACTION_ISOLATE_ENDPOINT, ACTION_CONTAIN_HOST}

            states = []
            for host in resources:
                if not isinstance(host, dict):
                    continue
                states.append(
                    bool(
                        host.get("containment_status") == "contained"
                        or host.get("status") == "contained"
                        or host.get("reduced_functionality_mode") is True
                    )
                )

            ok = response["ok"] and bool(states) and all(
                state == expected_contained
                for state in states
            )

            return ConnectorExecutionResult(
                ok=ok,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_COMPLETED if ok else STATUS_FAILED,
                message="CrowdStrike containment verification passed." if ok else "CrowdStrike containment verification failed.",
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=",".join(host_ids),
                simulated=False,
                verification_ok=ok,
                raw={
                    "expected_contained": expected_contained,
                    "states": states,
                    "response": response,
                },
            )

        if action == ACTION_ADD_IOC:
            # IOC create API accepted; deeper verification can query indicators by filter in a later hardening pass.
            return ConnectorExecutionResult(
                ok=True,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_COMPLETED,
                message="CrowdStrike IOC API accepted; verification treated as accepted.",
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=execution_result.target_id,
                simulated=False,
                verification_ok=True,
            )

        if action == ACTION_REMOVE_IOC:
            return ConnectorExecutionResult(
                ok=True,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_COMPLETED,
                message="CrowdStrike IOC delete API accepted; verification treated as accepted.",
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=execution_result.target_id,
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

        if action in {ACTION_ISOLATE_ENDPOINT, ACTION_CONTAIN_HOST}:
            return {
                "action": ACTION_UNISOLATE_ENDPOINT,
                "ids": self._host_ids(payload),
                "tenant_id": self.tenant_id,
            }

        if action in {ACTION_UNISOLATE_ENDPOINT, ACTION_RELEASE_HOST}:
            return {
                "action": ACTION_ISOLATE_ENDPOINT,
                "ids": self._host_ids(payload),
                "tenant_id": self.tenant_id,
            }

        if action == ACTION_ADD_IOC:
            return {
                "action": ACTION_REMOVE_IOC,
                "ids": payload.get("indicator_ids") or payload.get("ids") or [],
                "tenant_id": self.tenant_id,
            }

        if action in {ACTION_KILL_PROCESS, ACTION_REMOVE_IOC}:
            return {
                "action": "NO_ROLLBACK_AVAILABLE",
                "reason": f"{action} cannot be reliably reversed.",
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
            ACTION_ISOLATE_ENDPOINT,
            ACTION_UNISOLATE_ENDPOINT,
            ACTION_CONTAIN_HOST,
            ACTION_RELEASE_HOST,
            ACTION_REMOVE_IOC,
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
            f"No CrowdStrike rollback implementation for {rollback_action}.",
        )

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Any] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.ensure_authenticated()

        if not self.access_token:
            return {
                "ok": False,
                "status_code": 0,
                "message": "CrowdStrike access token unavailable.",
            }

        url = f"{self.base_url}{path}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _host_ids(self, payload: Dict[str, Any]) -> List[str]:
        values = (
            payload.get("ids")
            or payload.get("host_ids")
            or payload.get("device_ids")
            or payload.get("aid")
            or payload.get("aids")
            or payload.get("host_id")
            or payload.get("device_id")
        )

        return [
            _safe_str(x)
            for x in _as_list(values)
            if _safe_str(x)
        ]

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