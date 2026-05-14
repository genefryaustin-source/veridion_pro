"""
core/connectors/connector_execution_fabric.py

Connector Execution Fabric.

This is the execution mesh between:
- connector registry
- connector health monitor
- action router
- distributed queue
- failover execution

Responsibilities:
- connector selection
- failover chains
- degraded-mode rerouting
- retry orchestration
- outage-aware routing
- tenant-aware routing
- execution telemetry
- connector cooldown windows
- weighted routing
- latency-aware selection

Design:
- Works with BaseConnector-compatible connectors
- Uses connector_registry when available
- Uses connector_health_monitor when available
- Can fall back to direct connector dict if needed
"""

from __future__ import annotations

import time
import uuid
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


try:
    from core.connectors.base_connector import (
        ConnectorActionResult,
        STATUS_SUCCESS,
        STATUS_FAILED,
        STATUS_BLOCKED,
        STATUS_SKIPPED,
    )
except Exception:
    ConnectorActionResult = None
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"
    STATUS_BLOCKED = "BLOCKED"
    STATUS_SKIPPED = "SKIPPED"


try:
    from core.connectors.connector_registry import get_connector_registry
except Exception:
    get_connector_registry = None


try:
    from core.connectors.connector_health_monitor import (
        get_connector_health_monitor,
        HEALTH_HEALTHY,
        HEALTH_DEGRADED,
        HEALTH_OUTAGE,
    )
except Exception:
    get_connector_health_monitor = None
    HEALTH_HEALTHY = "HEALTHY"
    HEALTH_DEGRADED = "DEGRADED"
    HEALTH_OUTAGE = "OUTAGE"


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


FABRIC_STATUS_SUCCESS = "SUCCESS"
FABRIC_STATUS_FAILED = "FAILED"
FABRIC_STATUS_BLOCKED = "BLOCKED"
FABRIC_STATUS_SKIPPED = "SKIPPED"
FABRIC_STATUS_NO_ROUTE = "NO_ROUTE"
FABRIC_STATUS_ALL_FAILED = "ALL_FAILED"


@dataclass
class ConnectorExecutionAttempt:
    connector_name: str
    action: str
    target: Optional[str] = None
    success: bool = False
    status: str = STATUS_FAILED
    latency_ms: float = 0.0
    error: Optional[str] = None
    message: str = ""
    raw_response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectorFabricResult:
    success: bool
    status: str
    action: str
    target: Optional[str] = None
    selected_connector: Optional[str] = None
    connector_action: Optional[str] = None
    fabric_execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    attempts: List[ConnectorExecutionAttempt] = field(default_factory=list)

    connector_result: Optional[Any] = None

    rollback_supported: bool = False
    rollback_connector: Optional[str] = None
    rollback_action: Optional[str] = None
    rollback_data: Dict[str, Any] = field(default_factory=dict)

    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectorExecutionFabric:
    """
    Connector execution mesh.

    Preferred invocation:
        fabric.execute(
            capability="contain_host",
            action="contain_host",
            target=aid,
            payload=context,
            tenant_id="default",
            allow_destructive=False,
        )
    """

    def __init__(
        self,
        connectors: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.connectors = connectors or {}
        self.config = config or {}

        self.registry = get_connector_registry() if get_connector_registry else None
        self.health_monitor = get_connector_health_monitor() if get_connector_health_monitor else None

        self.cooldowns: Dict[str, int] = {}

        fabric_cfg = self.config.get("connector_fabric", {})

        self.max_attempts = int(fabric_cfg.get("max_attempts", 3))
        self.retry_delay_ms = int(fabric_cfg.get("retry_delay_ms", 250))
        self.cooldown_ms = int(fabric_cfg.get("cooldown_ms", 60_000))
        self.allow_degraded = bool(fabric_cfg.get("allow_degraded", True))
        self.prefer_low_latency = bool(fabric_cfg.get("prefer_low_latency", True))

    # ========================================================
    # TELEMETRY
    # ========================================================

    def emit_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        dispatch_event(
            event_type=event_type,
            payload=payload or {},
            source="connector_execution_fabric",
        )

    # ========================================================
    # PUBLIC EXECUTION
    # ========================================================

    def execute(
        self,
        capability: str,
        action: str,
        target: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        preferred_connector: Optional[str] = None,
        connector_order: Optional[List[str]] = None,
        allow_destructive: bool = False,
        max_attempts: Optional[int] = None,
    ) -> ConnectorFabricResult:
        payload = payload or {}
        tenant_id = tenant_id or payload.get("tenant_id") or "default"
        execution_id = str(uuid.uuid4())
        max_attempts = max_attempts or self.max_attempts

        self.emit_event(
            "CONNECTOR_FABRIC_EXECUTION_STARTED",
            {
                "fabric_execution_id": execution_id,
                "capability": capability,
                "action": action,
                "target": target,
                "tenant_id": tenant_id,
                "preferred_connector": preferred_connector,
            },
        )

        route = self.resolve_route(
            capability=capability,
            tenant_id=tenant_id,
            preferred_connector=preferred_connector,
            connector_order=connector_order,
        )

        if not route:
            result = ConnectorFabricResult(
                success=False,
                status=FABRIC_STATUS_NO_ROUTE,
                action=action,
                target=target,
                connector_action=action,
                fabric_execution_id=execution_id,
                error="no_connector_route",
                message=f"No connector route available for capability: {capability}",
                metadata={
                    "capability": capability,
                    "tenant_id": tenant_id,
                },
            )

            self.emit_event(
                "CONNECTOR_FABRIC_NO_ROUTE",
                result.__dict__,
            )

            return result

        attempts: List[ConnectorExecutionAttempt] = []
        last_connector_result = None

        for connector_name in route[:max_attempts]:
            connector = self.get_connector(connector_name)

            if connector is None:
                attempts.append(
                    ConnectorExecutionAttempt(
                        connector_name=connector_name,
                        action=action,
                        target=target,
                        success=False,
                        status=STATUS_FAILED,
                        error="connector_unavailable",
                        message="Connector unavailable or quarantined.",
                    )
                )
                continue

            if self.is_in_cooldown(connector_name):
                attempts.append(
                    ConnectorExecutionAttempt(
                        connector_name=connector_name,
                        action=action,
                        target=target,
                        success=False,
                        status=STATUS_SKIPPED,
                        error="connector_in_cooldown",
                        message="Connector skipped due to cooldown.",
                    )
                )
                continue

            if not self.is_connector_eligible(connector_name):
                attempts.append(
                    ConnectorExecutionAttempt(
                        connector_name=connector_name,
                        action=action,
                        target=target,
                        success=False,
                        status=STATUS_SKIPPED,
                        error="connector_not_eligible",
                        message="Connector skipped due to health state.",
                    )
                )
                continue

            started = time.perf_counter()

            try:
                connector_result = connector.execute(
                    action=action,
                    target=target,
                    payload=payload,
                    allow_destructive=allow_destructive,
                )

                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                last_connector_result = connector_result

                attempt = ConnectorExecutionAttempt(
                    connector_name=connector_name,
                    action=action,
                    target=target,
                    success=bool(getattr(connector_result, "success", False)),
                    status=str(getattr(connector_result, "status", STATUS_FAILED)),
                    latency_ms=latency_ms,
                    error=getattr(connector_result, "error", None),
                    message=getattr(connector_result, "message", ""),
                    raw_response=getattr(connector_result, "raw_response", {}) or {},
                )

                attempts.append(attempt)

                if attempt.success:
                    self.record_success(connector_name, latency_ms)

                    result = ConnectorFabricResult(
                        success=True,
                        status=getattr(connector_result, "status", STATUS_SUCCESS),
                        action=action,
                        target=target,
                        selected_connector=connector_name,
                        connector_action=action,
                        fabric_execution_id=execution_id,
                        attempts=attempts,
                        connector_result=connector_result,
                        rollback_supported=bool(getattr(connector_result, "rollback_supported", False)),
                        rollback_connector=connector_name if getattr(connector_result, "rollback_supported", False) else None,
                        rollback_action=getattr(connector_result, "rollback_action", None),
                        rollback_data=getattr(connector_result, "rollback_data", {}) or {},
                        message=getattr(connector_result, "message", ""),
                        error=getattr(connector_result, "error", None),
                        metadata={
                            "capability": capability,
                            "tenant_id": tenant_id,
                            "route": route,
                        },
                    )

                    self.emit_event(
                        "CONNECTOR_FABRIC_EXECUTION_COMPLETED",
                        self._result_payload(result),
                    )

                    return result

                self.record_failure(
                    connector_name=connector_name,
                    error=attempt.error or attempt.message,
                )

                self.emit_event(
                    "CONNECTOR_FABRIC_ATTEMPT_FAILED",
                    attempt.__dict__,
                )

                if self.should_cooldown(attempt):
                    self.apply_cooldown(
                        connector_name,
                        reason=attempt.error or attempt.message,
                    )

                self._sleep_retry_delay()

            except Exception:
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                error = traceback.format_exc()

                attempt = ConnectorExecutionAttempt(
                    connector_name=connector_name,
                    action=action,
                    target=target,
                    success=False,
                    status=STATUS_FAILED,
                    latency_ms=latency_ms,
                    error=error,
                    message="Connector execution raised an exception.",
                )

                attempts.append(attempt)

                self.record_failure(
                    connector_name=connector_name,
                    error=error,
                )

                self.emit_event(
                    "CONNECTOR_FABRIC_ATTEMPT_EXCEPTION",
                    attempt.__dict__,
                )

                self.apply_cooldown(connector_name, reason=error)
                self._sleep_retry_delay()

        result = ConnectorFabricResult(
            success=False,
            status=FABRIC_STATUS_ALL_FAILED,
            action=action,
            target=target,
            connector_action=action,
            fabric_execution_id=execution_id,
            attempts=attempts,
            connector_result=last_connector_result,
            message="All connector execution attempts failed.",
            error=self._last_error(attempts),
            metadata={
                "capability": capability,
                "tenant_id": tenant_id,
                "route": route,
            },
        )

        self.emit_event(
            "CONNECTOR_FABRIC_EXECUTION_FAILED",
            self._result_payload(result),
        )

        return result

    # ========================================================
    # ROUTING
    # ========================================================

    def resolve_route(
        self,
        capability: str,
        tenant_id: Optional[str] = None,
        preferred_connector: Optional[str] = None,
        connector_order: Optional[List[str]] = None,
    ) -> List[str]:
        if connector_order:
            return self.rank_route(connector_order)

        route: List[str] = []

        if preferred_connector:
            route.append(preferred_connector)

        if self.registry:
            try:
                route.extend(
                    self.registry.get_failover_chain(
                        capability=capability,
                        tenant_id=tenant_id,
                    )
                )
            except Exception:
                pass

        if not route:
            route.extend(self.find_local_capability_route(capability))

        deduped = []
        seen = set()

        for name in route:
            if not name or name in seen:
                continue
            seen.add(name)
            deduped.append(name)

        return self.rank_route(deduped)

    def find_local_capability_route(self, capability: str) -> List[str]:
        matches = []

        for name, connector in self.connectors.items():
            supported = getattr(connector, "SUPPORTED_ACTIONS", []) or []

            if capability in supported:
                matches.append(name)

        return matches

    def rank_route(self, route: List[str]) -> List[str]:
        def score(name: str) -> Tuple[int, float, int]:
            health_rank = 0
            latency = 0.0
            cooldown_rank = 0

            if self.health_monitor:
                state = self.health_monitor.get_state(name)

                if state.health == HEALTH_HEALTHY:
                    health_rank = 0
                elif state.health == HEALTH_DEGRADED:
                    health_rank = 1
                elif state.health == HEALTH_OUTAGE:
                    health_rank = 9
                else:
                    health_rank = 5

                latency = float(getattr(state, "avg_latency_ms", 0.0) or 0.0)

            if self.is_in_cooldown(name):
                cooldown_rank = 10

            return (cooldown_rank, health_rank, latency if self.prefer_low_latency else 0)

        return sorted(route, key=score)

    # ========================================================
    # CONNECTOR LOOKUP
    # ========================================================

    def get_connector(self, connector_name: str) -> Optional[Any]:
        if self.registry:
            try:
                connector = self.registry.get(connector_name)
                if connector is not None:
                    return connector
            except Exception:
                pass

        return self.connectors.get(connector_name)

    # ========================================================
    # HEALTH / COOLDOWN
    # ========================================================

    def is_connector_eligible(self, connector_name: str) -> bool:
        if not self.health_monitor:
            return True

        state = self.health_monitor.get_state(connector_name)

        if state.health == HEALTH_OUTAGE:
            return False

        if state.health == HEALTH_DEGRADED and not self.allow_degraded:
            return False

        return True

    def record_success(self, connector_name: str, latency_ms: float) -> None:
        if self.health_monitor:
            self.health_monitor.record_success(connector_name, latency_ms)

        self.emit_event(
            "CONNECTOR_FABRIC_HEALTH_SUCCESS",
            {
                "connector": connector_name,
                "latency_ms": latency_ms,
            },
        )

    def record_failure(self, connector_name: str, error: Optional[str] = None) -> None:
        auth_failure = self._looks_like_auth_failure(error or "")

        if self.health_monitor:
            self.health_monitor.record_failure(
                connector_name=connector_name,
                error=error or "",
                auth_failure=auth_failure,
            )

        self.emit_event(
            "CONNECTOR_FABRIC_HEALTH_FAILURE",
            {
                "connector": connector_name,
                "error": error,
                "auth_failure": auth_failure,
            },
        )

    def should_cooldown(self, attempt: ConnectorExecutionAttempt) -> bool:
        if not attempt.error:
            return False

        error = attempt.error.lower()

        return any(
            token in error
            for token in [
                "timeout",
                "rate limit",
                "429",
                "503",
                "temporarily unavailable",
                "connection",
                "auth",
                "unauthorized",
                "forbidden",
            ]
        )

    def apply_cooldown(self, connector_name: str, reason: str = "") -> None:
        until = int(time.time() * 1000) + self.cooldown_ms
        self.cooldowns[connector_name] = until

        self.emit_event(
            "CONNECTOR_FABRIC_COOLDOWN_APPLIED",
            {
                "connector": connector_name,
                "cooldown_until_ms": until,
                "reason": reason,
            },
        )

    def is_in_cooldown(self, connector_name: str) -> bool:
        until = self.cooldowns.get(connector_name)
        if not until:
            return False

        return int(time.time() * 1000) < until

    # ========================================================
    # HELPERS
    # ========================================================

    def _sleep_retry_delay(self) -> None:
        if self.retry_delay_ms <= 0:
            return

        time.sleep(self.retry_delay_ms / 1000)

    def _looks_like_auth_failure(self, error: str) -> bool:
        lower = error.lower()
        return any(
            token in lower
            for token in [
                "401",
                "403",
                "unauthorized",
                "forbidden",
                "invalid_client",
                "invalid_grant",
                "token",
                "auth",
            ]
        )

    def _last_error(self, attempts: List[ConnectorExecutionAttempt]) -> Optional[str]:
        for attempt in reversed(attempts):
            if attempt.error:
                return attempt.error
            if attempt.message:
                return attempt.message
        return None

    def _result_payload(self, result: ConnectorFabricResult) -> Dict[str, Any]:
        payload = result.__dict__.copy()

        payload["attempts"] = [
            attempt.__dict__
            for attempt in result.attempts
        ]

        connector_result = payload.get("connector_result")
        if connector_result is not None and hasattr(connector_result, "__dict__"):
            payload["connector_result"] = connector_result.__dict__

        return payload


# ============================================================
# SINGLETON
# ============================================================

_DEFAULT_FABRIC: Optional[ConnectorExecutionFabric] = None


def get_connector_execution_fabric(
    connectors: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> ConnectorExecutionFabric:
    global _DEFAULT_FABRIC

    if _DEFAULT_FABRIC is None:
        _DEFAULT_FABRIC = ConnectorExecutionFabric(
            connectors=connectors,
            config=config,
        )

    elif connectors:
        _DEFAULT_FABRIC.connectors.update(connectors)

    return _DEFAULT_FABRIC