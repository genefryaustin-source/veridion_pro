"""
core/connectors/sentinelone_connector.py

SentinelOne Connector for Veridion Pro / CUI GovCloud App.

Supports:
- ISOLATE_ENDPOINT
- UNISOLATE_ENDPOINT
- CONTAIN_HOST
- RELEASE_HOST
- GET_AGENT
- SEARCH_AGENTS
- GET_THREATS
- ADD_IOC
- REMOVE_IOC
- KILL_PROCESS
- LIST_PROCESSES

Safe by default:
- simulation_mode=True through BaseConnector
- safety guardrails execute before real execution
- rollback-aware endpoint containment
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


ACTION_ISOLATE_ENDPOINT = "ISOLATE_ENDPOINT"
ACTION_UNISOLATE_ENDPOINT = "UNISOLATE_ENDPOINT"
ACTION_CONTAIN_HOST = "CONTAIN_HOST"
ACTION_RELEASE_HOST = "RELEASE_HOST"

ACTION_GET_AGENT = "GET_AGENT"
ACTION_SEARCH_AGENTS = "SEARCH_AGENTS"

ACTION_GET_THREATS = "GET_THREATS"

ACTION_ADD_IOC = "ADD_IOC"
ACTION_REMOVE_IOC = "REMOVE_IOC"

ACTION_KILL_PROCESS = "KILL_PROCESS"
ACTION_LIST_PROCESSES = "LIST_PROCESSES"

DEFAULT_BASE_URL = "https://usea1-partners.sentinelone.net/web/api/v2.1"


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


class SentinelOneConnector(BaseConnector):

    connector_id = "sentinelone"
    connector_name = "SentinelOne Connector"
    vendor = "SentinelOne"

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
            or DEFAULT_BASE_URL
        ).rstrip("/")

        self.api_token = (
            self.config.get("api_token")
            or self.config.get("token")
        )

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

            ACTION_ISOLATE_ENDPOINT:
                ConnectorCapability(
                    name=ACTION_ISOLATE_ENDPOINT,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=True,
                    description="Disconnect SentinelOne agent from network.",
                ),

            ACTION_UNISOLATE_ENDPOINT:
                ConnectorCapability(
                    name=ACTION_UNISOLATE_ENDPOINT,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Reconnect SentinelOne agent.",
                ),

            ACTION_CONTAIN_HOST:
                ConnectorCapability(
                    name=ACTION_CONTAIN_HOST,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=True,
                    description="Alias for isolate endpoint.",
                ),

            ACTION_RELEASE_HOST:
                ConnectorCapability(
                    name=ACTION_RELEASE_HOST,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Alias for unisolate endpoint.",
                ),

            ACTION_GET_AGENT:
                ConnectorCapability(
                    name=ACTION_GET_AGENT,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="Get SentinelOne agent details.",
                ),

            ACTION_SEARCH_AGENTS:
                ConnectorCapability(
                    name=ACTION_SEARCH_AGENTS,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="Search SentinelOne agents.",
                ),

            ACTION_GET_THREATS:
                ConnectorCapability(
                    name=ACTION_GET_THREATS,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="Retrieve SentinelOne threats.",
                ),

            ACTION_ADD_IOC:
                ConnectorCapability(
                    name=ACTION_ADD_IOC,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Create IOC/threat intelligence object.",
                ),

            ACTION_REMOVE_IOC:
                ConnectorCapability(
                    name=ACTION_REMOVE_IOC,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=True,
                    destructive=False,
                    description="Remove IOC/threat intelligence object.",
                ),

            ACTION_KILL_PROCESS:
                ConnectorCapability(
                    name=ACTION_KILL_PROCESS,
                    supported=True,
                    requires_approval=True,
                    supports_rollback=False,
                    destructive=True,
                    description="Kill process via Deep Visibility/Ranger workflow.",
                ),

            ACTION_LIST_PROCESSES:
                ConnectorCapability(
                    name=ACTION_LIST_PROCESSES,
                    supported=True,
                    requires_approval=False,
                    supports_rollback=False,
                    destructive=False,
                    description="List running processes.",
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

        if not self.api_token:

            self.auth_state = ConnectorAuthState(
                authenticated=False,
                auth_type="api_token",
                metadata={
                    "error": "Missing SentinelOne API token.",
                },
            )

            return self.auth_state

        self.auth_state = ConnectorAuthState(
            authenticated=True,
            auth_type="api_token",
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

        if action in {
            ACTION_ISOLATE_ENDPOINT,
            ACTION_CONTAIN_HOST,
        }:

            return self._network_action(
                action=ACTION_ISOLATE_ENDPOINT,
                operation="disconnect",
                payload=payload,
                execution_id=execution_id,
            )

        if action in {
            ACTION_UNISOLATE_ENDPOINT,
            ACTION_RELEASE_HOST,
        }:

            return self._network_action(
                action=ACTION_UNISOLATE_ENDPOINT,
                operation="connect",
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_GET_AGENT:

            return self._get_agent(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_SEARCH_AGENTS:

            return self._search_agents(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_GET_THREATS:

            return self._get_threats(
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

        if action == ACTION_KILL_PROCESS:

            return self._kill_process(
                payload=payload,
                execution_id=execution_id,
            )

        if action == ACTION_LIST_PROCESSES:

            return self._list_processes(
                payload=payload,
                execution_id=execution_id,
            )

        return self._failed(
            action,
            execution_id,
            f"Unsupported SentinelOne action: {action}",
        )

    # ------------------------------------------------------------------
    # NETWORK CONTAINMENT
    # ------------------------------------------------------------------

    def _network_action(
        self,
        *,
        action: str,
        operation: str,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        agent_ids = self._agent_ids(payload)

        if not agent_ids:

            return self._failed(
                action,
                execution_id,
                "agent_id or ids required.",
            )

        response = self._request(
            "POST",
            f"/agents/actions/{operation}",
            json_body={
                "filter": {
                    "ids": agent_ids,
                }
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
            ACTION_UNISOLATE_ENDPOINT
            if operation == "disconnect"
            else ACTION_ISOLATE_ENDPOINT
        )

        event_type = (
            "ENDPOINT_ISOLATED"
            if operation == "disconnect"
            else "ENDPOINT_RELEASED"
        )

        self._emit(
            event_type,
            {
                "execution_id": execution_id,
                "connector_id": self.connector_id,
                "tenant_id": self.tenant_id,
                "agent_ids": agent_ids,
                "action": action,
            },
            severity=(
                "HIGH"
                if operation == "disconnect"
                else "MEDIUM"
            ),
        )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_COMPLETED,
            message=f"SentinelOne action completed: {operation}",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=",".join(agent_ids),
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": rollback_action,
                "ids": agent_ids,
                "tenant_id": self.tenant_id,
            },
            raw=response,
        )

    # ------------------------------------------------------------------
    # AGENTS
    # ------------------------------------------------------------------

    def _get_agent(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        agent_ids = self._agent_ids(payload)

        if not agent_ids:

            return self._failed(
                ACTION_GET_AGENT,
                execution_id,
                "agent_id or ids required.",
            )

        response = self._request(
            "GET",
            "/agents",
            params={
                "ids": ",".join(agent_ids),
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_GET_AGENT,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_AGENT,
            status=STATUS_COMPLETED,
            message="SentinelOne agent details retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=",".join(agent_ids),
            simulated=False,
            raw=response,
        )

    def _search_agents(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        query = (
            payload.get("query")
            or payload.get("filter")
            or ""
        )

        limit = min(
            max(
                int(payload.get("limit") or 25),
                1,
            ),
            500,
        )

        response = self._request(
            "GET",
            "/agents",
            params={
                "query": query,
                "limit": limit,
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_SEARCH_AGENTS,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_SEARCH_AGENTS,
            status=STATUS_COMPLETED,
            message="SentinelOne agent search completed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=query,
            simulated=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # THREATS
    # ------------------------------------------------------------------

    def _get_threats(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        limit = min(
            max(
                int(payload.get("limit") or 25),
                1,
            ),
            500,
        )

        response = self._request(
            "GET",
            "/threats",
            params={
                "limit": limit,
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_GET_THREATS,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_GET_THREATS,
            status=STATUS_COMPLETED,
            message="SentinelOne threats retrieved.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            simulated=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # IOC
    # ------------------------------------------------------------------

    def _add_ioc(
        self,
        *,
        payload: Dict[str, Any],
        execution_id: str,
    ) -> ConnectorExecutionResult:

        ioc_value = (
            payload.get("value")
            or payload.get("indicator")
        )

        ioc_type = (
            payload.get("type")
            or payload.get("indicator_type")
        )

        if not ioc_value or not ioc_type:

            return self._failed(
                ACTION_ADD_IOC,
                execution_id,
                "IOC type and value required.",
            )

        response = self._request(
            "POST",
            "/threat-intelligence/iocs",
            json_body={
                "value": ioc_value,
                "type": ioc_type,
                "description": (
                    payload.get("description")
                    or "Added by Veridion Pro"
                ),
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_ADD_IOC,
                execution_id,
                response["message"],
                raw=response,
            )

        ioc_id = (
            (
                response.get("json")
                or {}
            ).get("id")
        )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_ADD_IOC,
            status=STATUS_COMPLETED,
            message="SentinelOne IOC added.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=ioc_value,
            simulated=False,
            rollback_available=True,
            rollback_payload={
                "action": ACTION_REMOVE_IOC,
                "ids": [ioc_id] if ioc_id else [],
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
            for x in _as_list(
                payload.get("ids")
                or payload.get("ioc_ids")
            )
            if _safe_str(x)
        ]

        if not ids:

            return self._failed(
                ACTION_REMOVE_IOC,
                execution_id,
                "IOC ids required.",
            )

        response = self._request(
            "DELETE",
            "/threat-intelligence/iocs",
            json_body={
                "ids": ids,
            },
        )

        if not response["ok"]:

            return self._failed(
                ACTION_REMOVE_IOC,
                execution_id,
                response["message"],
                raw=response,
            )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=ACTION_REMOVE_IOC,
            status=STATUS_COMPLETED,
            message="SentinelOne IOC removed.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=",".join(ids),
            simulated=False,
            raw=response,
        )

    # ------------------------------------------------------------------
    # RTR PLACEHOLDERS
    # ------------------------------------------------------------------

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
                "SentinelOne remote process kill "
                "requires Deep Visibility/Ranger "
                "workflow orchestration."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            simulated=False,
            raw={"payload": payload},
        )

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
                "SentinelOne process enumeration "
                "requires Deep Visibility workflows."
            ),
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            simulated=False,
            raw={"payload": payload},
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
            ACTION_ISOLATE_ENDPOINT,
            ACTION_UNISOLATE_ENDPOINT,
        }:

            agent_ids = self._agent_ids(payload)

            response = self._request(
                "GET",
                "/agents",
                params={
                    "ids": ",".join(agent_ids),
                },
            )

            agents = (
                (
                    response.get("json")
                    or {}
                ).get("data")
                or []
            )

            expected_isolated = (
                action == ACTION_ISOLATE_ENDPOINT
            )

            states = []

            for agent in agents:

                disconnected = bool(
                    agent.get("networkStatus")
                    == "disconnected"
                    or agent.get("isIsolated")
                    is True
                )

                states.append(disconnected)

            ok = (
                response["ok"]
                and bool(states)
                and all(
                    s == expected_isolated
                    for s in states
                )
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
                    "SentinelOne containment verification passed."
                    if ok
                    else "SentinelOne containment verification failed."
                ),
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=",".join(agent_ids),
                simulated=False,
                verification_ok=ok,
                raw={
                    "states": states,
                    "response": response,
                },
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

        if action in {
            ACTION_ISOLATE_ENDPOINT,
            ACTION_CONTAIN_HOST,
        }:

            return {
                "action": ACTION_UNISOLATE_ENDPOINT,
                "ids": self._agent_ids(payload),
                "tenant_id": self.tenant_id,
            }

        if action in {
            ACTION_UNISOLATE_ENDPOINT,
            ACTION_RELEASE_HOST,
        }:

            return {
                "action": ACTION_ISOLATE_ENDPOINT,
                "ids": self._agent_ids(payload),
                "tenant_id": self.tenant_id,
            }

        if action == ACTION_ADD_IOC:

            return {
                "action": ACTION_REMOVE_IOC,
                "ids": payload.get("ioc_ids") or [],
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
            ACTION_ISOLATE_ENDPOINT,
            ACTION_UNISOLATE_ENDPOINT,
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
            f"No SentinelOne rollback implementation for {rollback_action}.",
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

        if not self.api_token:

            return {
                "ok": False,
                "status_code": 0,
                "message": (
                    "SentinelOne API token unavailable."
                ),
            }

        url = f"{self.base_url}{path}"

        headers = {
            "Authorization": (
                f"ApiToken {self.api_token}"
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

    def _agent_ids(
        self,
        payload: Dict[str, Any],
    ) -> List[str]:

        values = (
            payload.get("ids")
            or payload.get("agent_ids")
            or payload.get("agent_id")
            or payload.get("endpoint_ids")
            or payload.get("endpoint_id")
        )

        return [
            _safe_str(v)
            for v in _as_list(values)
            if _safe_str(v)
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