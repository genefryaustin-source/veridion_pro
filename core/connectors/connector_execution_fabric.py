"""
core/connectors/connector_execution_fabric.py

Governed Connector Execution Fabric

This fabric receives governed execution packages from:

    sovereign_execution_router.py
        ↓
    connector_execution_fabric.py
        ↓
    registered connectors

Responsibilities:
- connector selection
- health-aware routing
- failover-aware execution
- governance-aware retry control
- verification-aware completion
- lineage/evidence hooks
- degraded-mode execution constraints

IMPORTANT:
This fabric may call connector objects, but it does NOT bypass governance.
It expects execution requests to arrive already packaged by the sovereign
execution router.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_FABRIC_NAME = "connector_execution_fabric"

EXECUTION_STATUS_ACCEPTED = "ACCEPTED"
EXECUTION_STATUS_BLOCKED = "BLOCKED"
EXECUTION_STATUS_DEFERRED = "DEFERRED"
EXECUTION_STATUS_EXECUTED = "EXECUTED"
EXECUTION_STATUS_FAILED = "FAILED"
EXECUTION_STATUS_FAILOVER_USED = "FAILOVER_USED"
EXECUTION_STATUS_VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"
EXECUTION_STATUS_VERIFICATION_FAILED = "VERIFICATION_FAILED"
EXECUTION_STATUS_VERIFIED = "VERIFIED"

CONNECTOR_HEALTH_HEALTHY = "HEALTHY"
CONNECTOR_HEALTH_DEGRADED = "DEGRADED"
CONNECTOR_HEALTH_UNAVAILABLE = "UNAVAILABLE"
CONNECTOR_HEALTH_UNKNOWN = "UNKNOWN"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"


class ConnectorExecutionAction(str, Enum):
    OBSERVE = "OBSERVE"
    INVESTIGATE = "INVESTIGATE"
    ENRICH = "ENRICH"
    ESCALATE = "ESCALATE"
    NOTIFY = "NOTIFY"
    CONTAIN = "CONTAIN"
    ISOLATE_ENDPOINT = "ISOLATE_ENDPOINT"
    REVOKE_SESSION = "REVOKE_SESSION"
    DISABLE_USER = "DISABLE_USER"
    QUARANTINE_EMAIL = "QUARANTINE_EMAIL"
    DELETE_EMAIL = "DELETE_EMAIL"
    PURGE_MAILBOX = "PURGE_MAILBOX"
    BLOCK_NETWORK_TRAFFIC = "BLOCK_NETWORK_TRAFFIC"
    UPDATE_POLICY = "UPDATE_POLICY"
    ROLLBACK = "ROLLBACK"
    UNKNOWN = "UNKNOWN"


class ConnectorTarget(str, Enum):
    MICROSOFT_GRAPH = "MICROSOFT_GRAPH"
    GOOGLE_WORKSPACE = "GOOGLE_WORKSPACE"
    CROWDSTRIKE = "CROWDSTRIKE"
    SENTINELONE = "SENTINELONE"
    AWS = "AWS"
    LOCAL_AGENT = "LOCAL_AGENT"
    GENERIC_CONNECTOR = "GENERIC_CONNECTOR"
    NONE = "NONE"


@dataclass(frozen=True)
class ConnectorHealthState:
    connector_name: str
    health: str
    failure_count: int = 0
    success_count: int = 0
    last_latency_ms: Optional[int] = None
    last_error: Optional[str] = None
    last_updated_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class ConnectorExecutionResult:
    result_id: str
    execution_package_id: Optional[str]
    status: str
    action_type: str
    selected_connector: str
    attempted_connectors: List[str]
    failover_used: bool
    verification_required: bool
    verification_succeeded: Optional[bool]
    rollback_recommended: bool
    rationale: str
    connector_response: Dict[str, Any]
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class ConnectorExecutionFabricSnapshot:
    fabric_name: str
    total_packages_seen: int
    total_results_created: int
    registered_connectors: List[str]
    last_result_id: Optional[str]
    last_status: Optional[str]
    last_selected_connector: Optional[str]
    last_updated_ms: int


class ConnectorExecutionFabric:
    """
    Governance-aware connector execution mesh.

    Connectors may expose any of:
    - execute(package)
    - execute(package, context={...})
    - submit(package)
    - route(package)
    - verify(result/package)
    """

    def __init__(
        self,
        *,
        fabric_name: str = DEFAULT_FABRIC_NAME,
        connectors: Optional[Dict[str, Any]] = None,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
        max_retry_attempts: int = 1,
        allow_failover: bool = True,
    ) -> None:
        self.fabric_name = fabric_name
        self.connectors: Dict[str, Any] = {
            self._safe_connector_name(k): v
            for k, v in dict(connectors or {}).items()
        }

        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self.max_retry_attempts = max(0, int(max_retry_attempts))
        self.allow_failover = allow_failover

        self._packages_seen = 0
        self._results: List[ConnectorExecutionResult] = []
        self._health: Dict[str, ConnectorHealthState] = {
            name: ConnectorHealthState(
                connector_name=name,
                health=CONNECTOR_HEALTH_UNKNOWN,
            )
            for name in self.connectors
        }

    # --------------------------------------------------------
    # CONNECTOR REGISTRATION
    # --------------------------------------------------------

    def register_connector(self, name: str, connector: Any) -> None:
        safe_name = self._safe_connector_name(name)
        self.connectors[safe_name] = connector
        self._health.setdefault(
            safe_name,
            ConnectorHealthState(
                connector_name=safe_name,
                health=CONNECTOR_HEALTH_UNKNOWN,
            ),
        )

    def unregister_connector(self, name: str) -> None:
        safe_name = self._safe_connector_name(name)
        self.connectors.pop(safe_name, None)

    # --------------------------------------------------------
    # PUBLIC EXECUTION API
    # --------------------------------------------------------

    def submit(
        self,
        package: Any,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConnectorExecutionResult:
        return self.execute(package, context=context)

    def route(
        self,
        package: Any,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConnectorExecutionResult:
        return self.execute(package, context=context)

    def execute(
        self,
        package: Any,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConnectorExecutionResult:
        """
        Execute governed package through selected connector.

        Execution is blocked if the package is not safe to run.
        """

        self._packages_seen += 1

        pkg = self._package_to_dict(package)
        safety_status = self._preflight_status(pkg)

        if safety_status != EXECUTION_STATUS_ACCEPTED:
            result = self._blocked_or_deferred_result(pkg, safety_status)
            self._record_result(result, context=context)
            return result

        action_type = self._safe_action_type(pkg.get("action_type"))
        selected_connector = self._safe_connector_name(
            pkg.get("selected_connector")
        )

        candidates = self._candidate_connectors(pkg, selected_connector)
        attempted: List[str] = []
        last_response: Dict[str, Any] = {}
        last_error: Optional[str] = None
        failover_used = False

        for idx, connector_name in enumerate(candidates):
            connector = self.connectors.get(connector_name)
            if connector is None:
                attempted.append(connector_name)
                last_error = f"Connector not registered: {connector_name}"
                self._mark_failure(connector_name, last_error)
                continue

            if not self._connector_is_usable(connector_name, pkg):
                attempted.append(connector_name)
                last_error = f"Connector not usable: {connector_name}"
                continue

            if idx > 0:
                failover_used = True

            for attempt in range(self._allowed_attempts(action_type)):
                attempted.append(connector_name)
                started = time.time()

                try:
                    response = self._invoke_connector(
                        connector,
                        package,
                        context=context or {},
                    )
                    latency_ms = int((time.time() - started) * 1000)

                    last_response = self._normalize_connector_response(
                        response
                    )
                    self._mark_success(connector_name, latency_ms)

                    verification_required = bool(
                        pkg.get("verification_metadata", {}).get(
                            "verification_required",
                            True,
                        )
                    )

                    verification_succeeded = None
                    status = EXECUTION_STATUS_EXECUTED

                    if verification_required:
                        verification_succeeded = self._verify_execution(
                            connector,
                            package,
                            last_response,
                            context=context or {},
                        )
                        status = (
                            EXECUTION_STATUS_VERIFIED
                            if verification_succeeded
                            else EXECUTION_STATUS_VERIFICATION_FAILED
                        )

                    result = ConnectorExecutionResult(
                        result_id=str(uuid.uuid4()),
                        execution_package_id=pkg.get(
                            "execution_package_id"
                        ),
                        status=(
                            EXECUTION_STATUS_FAILOVER_USED
                            if failover_used and status == EXECUTION_STATUS_EXECUTED
                            else status
                        ),
                        action_type=action_type,
                        selected_connector=connector_name,
                        attempted_connectors=list(attempted),
                        failover_used=failover_used,
                        verification_required=verification_required,
                        verification_succeeded=verification_succeeded,
                        rollback_recommended=(
                            verification_succeeded is False
                            or status == EXECUTION_STATUS_VERIFICATION_FAILED
                        ),
                        rationale=self._result_rationale(
                            pkg,
                            connector_name,
                            status,
                            failover_used,
                        ),
                        connector_response=last_response,
                        tenant_id=pkg.get("tenant_id"),
                        case_id=pkg.get("case_id"),
                        correlation_id=pkg.get("correlation_id"),
                    )

                    self._record_result(result, context=context)
                    return result

                except Exception as exc:
                    last_error = str(exc)
                    self._mark_failure(connector_name, last_error)

                    if not self._retry_allowed(action_type, attempt):
                        break

        result = ConnectorExecutionResult(
            result_id=str(uuid.uuid4()),
            execution_package_id=pkg.get("execution_package_id"),
            status=EXECUTION_STATUS_FAILED,
            action_type=action_type,
            selected_connector=selected_connector,
            attempted_connectors=list(attempted),
            failover_used=failover_used,
            verification_required=bool(
                pkg.get("verification_metadata", {}).get(
                    "verification_required",
                    True,
                )
            ),
            verification_succeeded=False,
            rollback_recommended=True,
            rationale=(
                "Connector execution failed after governed routing. "
                f"Last error: {last_error or 'unknown'}"
            ),
            connector_response=last_response,
            tenant_id=pkg.get("tenant_id"),
            case_id=pkg.get("case_id"),
            correlation_id=pkg.get("correlation_id"),
        )

        self._record_result(result, context=context)
        return result

    # --------------------------------------------------------
    # PREFLIGHT / ROUTING
    # --------------------------------------------------------

    def _preflight_status(self, pkg: Dict[str, Any]) -> str:
        route_status = str(pkg.get("route_status") or "").upper()
        selected_route = str(pkg.get("selected_route") or "").upper()

        if route_status in {
            "BLOCKED",
            "REQUIRES_APPROVAL",
            "REQUIRES_GOVERNANCE",
            "REQUIRES_ROLLBACK_PLAN",
            "REQUIRES_CONTINUITY_REVIEW",
            "DEFERRED",
        }:
            return route_status

        if selected_route != "CONNECTOR_FABRIC":
            return EXECUTION_STATUS_DEFERRED

        safety = dict(pkg.get("safety_metadata") or {})
        rollback = dict(pkg.get("rollback_metadata") or {})

        if safety.get("blocked"):
            return EXECUTION_STATUS_BLOCKED

        if not safety.get("allowed", True):
            return EXECUTION_STATUS_DEFERRED

        if rollback.get("rollback_required") and not rollback.get(
            "rollback_available"
        ):
            return "REQUIRES_ROLLBACK_PLAN"

        return EXECUTION_STATUS_ACCEPTED

    def _candidate_connectors(
        self,
        pkg: Dict[str, Any],
        selected_connector: str,
    ) -> List[str]:
        candidates: List[str] = []

        if selected_connector and selected_connector != ConnectorTarget.NONE.value:
            candidates.append(selected_connector)

        fallback = [
            self._safe_connector_name(item)
            for item in list(pkg.get("fallback_connectors", []) or [])
        ]

        if self.allow_failover and pkg.get("safety_metadata", {}).get(
            "failover_allowed",
            True,
        ):
            candidates.extend(fallback)

        if not candidates:
            candidates.append(ConnectorTarget.GENERIC_CONNECTOR.value)

        return list(dict.fromkeys(candidates))

    def _connector_is_usable(
        self,
        connector_name: str,
        pkg: Dict[str, Any],
    ) -> bool:
        health = self._health.get(connector_name)

        if health is None:
            return True

        if health.health == CONNECTOR_HEALTH_UNAVAILABLE:
            return False

        blast_radius = str(pkg.get("blast_radius") or "").upper()
        degraded_mode = bool(pkg.get("safety_metadata", {}).get("degraded_mode"))

        if degraded_mode and blast_radius in {RISK_HIGH, RISK_CRITICAL}:
            return False

        return True

    # --------------------------------------------------------
    # CONNECTOR INVOCATION
    # --------------------------------------------------------

    def _invoke_connector(
        self,
        connector: Any,
        package: Any,
        *,
        context: Dict[str, Any],
    ) -> Any:
        if hasattr(connector, "execute"):
            try:
                return connector.execute(package, context=context)
            except TypeError:
                return connector.execute(package)

        if hasattr(connector, "submit"):
            try:
                return connector.submit(package, context=context)
            except TypeError:
                return connector.submit(package)

        if hasattr(connector, "route"):
            try:
                return connector.route(package, context=context)
            except TypeError:
                return connector.route(package)

        if callable(connector):
            return connector(package)

        raise RuntimeError("Connector does not expose execute/submit/route.")

    def _verify_execution(
        self,
        connector: Any,
        package: Any,
        connector_response: Dict[str, Any],
        *,
        context: Dict[str, Any],
    ) -> bool:
        if connector_response.get("verified") is True:
            return True

        if connector_response.get("verification_succeeded") is True:
            return True

        if hasattr(connector, "verify"):
            try:
                verification = connector.verify(
                    package,
                    connector_response,
                    context=context,
                )
            except TypeError:
                verification = connector.verify(package, connector_response)

            if isinstance(verification, bool):
                return verification

            if isinstance(verification, dict):
                return bool(
                    verification.get("verified")
                    or verification.get("verification_succeeded")
                )

        return bool(connector_response.get("success", False))

    # --------------------------------------------------------
    # RETRY POLICY
    # --------------------------------------------------------

    def _allowed_attempts(self, action_type: str) -> int:
        if action_type in {
            ConnectorExecutionAction.PURGE_MAILBOX.value,
            ConnectorExecutionAction.DELETE_EMAIL.value,
            ConnectorExecutionAction.DISABLE_USER.value,
            ConnectorExecutionAction.UPDATE_POLICY.value,
        }:
            return 1

        return 1 + self.max_retry_attempts

    def _retry_allowed(self, action_type: str, attempt_index: int) -> bool:
        if attempt_index >= self.max_retry_attempts:
            return False

        if action_type in {
            ConnectorExecutionAction.PURGE_MAILBOX.value,
            ConnectorExecutionAction.DELETE_EMAIL.value,
            ConnectorExecutionAction.DISABLE_USER.value,
            ConnectorExecutionAction.UPDATE_POLICY.value,
        }:
            return False

        return True

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    def _mark_success(self, connector_name: str, latency_ms: int) -> None:
        old = self._health.get(connector_name)
        self._health[connector_name] = ConnectorHealthState(
            connector_name=connector_name,
            health=CONNECTOR_HEALTH_HEALTHY,
            failure_count=old.failure_count if old else 0,
            success_count=(old.success_count if old else 0) + 1,
            last_latency_ms=latency_ms,
            last_error=None,
        )

    def _mark_failure(self, connector_name: str, error: str) -> None:
        old = self._health.get(connector_name)
        failure_count = (old.failure_count if old else 0) + 1

        health = (
            CONNECTOR_HEALTH_UNAVAILABLE
            if failure_count >= 3
            else CONNECTOR_HEALTH_DEGRADED
        )

        self._health[connector_name] = ConnectorHealthState(
            connector_name=connector_name,
            health=health,
            failure_count=failure_count,
            success_count=old.success_count if old else 0,
            last_latency_ms=old.last_latency_ms if old else None,
            last_error=error,
        )

    def get_connector_health(
        self,
        connector_name: Optional[str] = None,
    ) -> Dict[str, ConnectorHealthState] | Optional[ConnectorHealthState]:
        if connector_name:
            return self._health.get(self._safe_connector_name(connector_name))
        return dict(self._health)

    # --------------------------------------------------------
    # RECORDING
    # --------------------------------------------------------

    def _record_result(
        self,
        result: ConnectorExecutionResult,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._results.append(result)
        self._write_to_memory(result, context=context)
        self._write_to_lineage(result, context=context)
        self._write_to_evidence(result, context=context)
        self._emit_event(result, context=context)

    def _write_to_memory(
        self,
        result: ConnectorExecutionResult,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "CONNECTOR_EXECUTION_RESULT",
            "result": asdict(result),
            "context": context or {},
        }

        try:
            if hasattr(memory, "append_memory"):
                memory.append_memory(payload)
            elif hasattr(memory, "record"):
                memory.record(payload)
            elif hasattr(memory, "write"):
                memory.write(payload)
        except Exception as exc:
            print(f"⚠️ Connector fabric memory write failed: {exc}")

    def _write_to_lineage(
        self,
        result: ConnectorExecutionResult,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "EXECUTION",
            "lineage_status": "RECORDED",
            "source_engine": self.fabric_name,
            "summary": result.rationale,
            "severity": "HIGH" if result.rollback_recommended else "INFO",
            "confidence": 1.0 if result.status == EXECUTION_STATUS_VERIFIED else 0.75,
            "mission_priority": 0,
            "tenant_id": result.tenant_id,
            "case_id": result.case_id,
            "correlation_id": result.correlation_id,
            "constraints": [
                "verification_required"
                if result.verification_required
                else "verification_not_required"
            ],
            "context": {
                "type": "CONNECTOR_EXECUTION_RESULT",
                "result": asdict(result),
                "context": context or {},
            },
            "metadata": {
                "status": result.status,
                "selected_connector": result.selected_connector,
                "failover_used": result.failover_used,
                "rollback_recommended": result.rollback_recommended,
            },
        }

        try:
            if hasattr(lineage, "record_lineage"):
                lineage.record_lineage(payload)
            elif hasattr(lineage, "append_lineage"):
                lineage.append_lineage(payload)
            elif hasattr(lineage, "record"):
                lineage.record(payload)
        except Exception as exc:
            print(f"⚠️ Connector fabric lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        result: ConnectorExecutionResult,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        evidence = self.fedramp_evidence_lineage_engine
        if evidence is None:
            return

        evidence_type = (
            "VERIFICATION_RESULT"
            if result.verification_required
            else "DECISION_ROUTE_PLAN"
        )

        payload = {
            "evidence_type": evidence_type,
            "evidence_status": (
                "VERIFIED"
                if result.status == EXECUTION_STATUS_VERIFIED
                else "RECORDED"
            ),
            "source_engine": self.fabric_name,
            "summary": result.rationale,
            "severity": "HIGH" if result.rollback_recommended else "INFO",
            "confidence": 1.0 if result.status == EXECUTION_STATUS_VERIFIED else 0.75,
            "mission_priority": 0,
            "tenant_id": result.tenant_id,
            "case_id": result.case_id,
            "correlation_id": result.correlation_id,
            "constraints": [
                "post_execution_verification"
                if result.verification_required
                else "verification_not_required"
            ],
            "evidence_payload": {
                "type": "CONNECTOR_EXECUTION_RESULT",
                "result": asdict(result),
                "context": context or {},
            },
            "metadata": {
                "selected_connector": result.selected_connector,
                "attempted_connectors": list(result.attempted_connectors),
                "failover_used": result.failover_used,
                "rollback_recommended": result.rollback_recommended,
            },
        }

        try:
            if hasattr(evidence, "record_evidence"):
                evidence.record_evidence(payload)
            elif hasattr(evidence, "append_evidence"):
                evidence.append_evidence(payload)
            elif hasattr(evidence, "record"):
                evidence.record(payload)
        except Exception as exc:
            print(f"⚠️ Connector fabric evidence write failed: {exc}")

    def _emit_event(
        self,
        result: ConnectorExecutionResult,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "CONNECTOR_EXECUTION_RESULT",
            "fabric_name": self.fabric_name,
            "result": asdict(result),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit("CONNECTOR_EXECUTION_RESULT", payload)
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish("CONNECTOR_EXECUTION_RESULT", payload)
        except Exception as exc:
            print(f"⚠️ Connector fabric event emit failed: {exc}")

    # --------------------------------------------------------
    # SNAPSHOTS
    # --------------------------------------------------------

    def get_recent_results(
        self,
        *,
        limit: int = 25,
    ) -> List[ConnectorExecutionResult]:
        limit = max(1, int(limit))
        return list(reversed(self._results[-limit:]))

    def snapshot(self) -> ConnectorExecutionFabricSnapshot:
        last = self._results[-1] if self._results else None

        return ConnectorExecutionFabricSnapshot(
            fabric_name=self.fabric_name,
            total_packages_seen=self._packages_seen,
            total_results_created=len(self._results),
            registered_connectors=sorted(self.connectors.keys()),
            last_result_id=last.result_id if last else None,
            last_status=last.status if last else None,
            last_selected_connector=last.selected_connector if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def _blocked_or_deferred_result(
        self,
        pkg: Dict[str, Any],
        status: str,
    ) -> ConnectorExecutionResult:
        return ConnectorExecutionResult(
            result_id=str(uuid.uuid4()),
            execution_package_id=pkg.get("execution_package_id"),
            status=(
                EXECUTION_STATUS_BLOCKED
                if status == "BLOCKED"
                else EXECUTION_STATUS_DEFERRED
            ),
            action_type=self._safe_action_type(pkg.get("action_type")),
            selected_connector=self._safe_connector_name(
                pkg.get("selected_connector")
            ),
            attempted_connectors=[],
            failover_used=False,
            verification_required=bool(
                pkg.get("verification_metadata", {}).get(
                    "verification_required",
                    True,
                )
            ),
            verification_succeeded=None,
            rollback_recommended=False,
            rationale=f"Connector execution not allowed. Preflight status: {status}.",
            connector_response={},
            tenant_id=pkg.get("tenant_id"),
            case_id=pkg.get("case_id"),
            correlation_id=pkg.get("correlation_id"),
        )

    @staticmethod
    def _package_to_dict(package: Any) -> Dict[str, Any]:
        if isinstance(package, dict):
            return dict(package)

        if hasattr(package, "__dataclass_fields__"):
            return asdict(package)

        if hasattr(package, "__dict__"):
            return dict(package.__dict__)

        raise TypeError("Unsupported execution package type.")

    @staticmethod
    def _normalize_connector_response(response: Any) -> Dict[str, Any]:
        if response is None:
            return {"success": True, "response": None}

        if isinstance(response, dict):
            return dict(response)

        if hasattr(response, "__dataclass_fields__"):
            return asdict(response)

        if hasattr(response, "__dict__"):
            return dict(response.__dict__)

        return {"success": True, "response": response}

    @staticmethod
    def _result_rationale(
        pkg: Dict[str, Any],
        connector_name: str,
        status: str,
        failover_used: bool,
    ) -> str:
        return (
            f"Execution package {pkg.get('execution_package_id')} routed to "
            f"{connector_name}. Status: {status}. "
            f"Failover used: {failover_used}."
        )

    @staticmethod
    def _safe_connector_name(value: Any) -> str:
        value = str(value or ConnectorTarget.GENERIC_CONNECTOR.value).upper()
        valid = {item.value for item in ConnectorTarget}
        return value if value in valid else value

    @staticmethod
    def _safe_action_type(value: Any) -> str:
        value = str(value or ConnectorExecutionAction.UNKNOWN.value).upper()
        valid = {item.value for item in ConnectorExecutionAction}
        return value if value in valid else ConnectorExecutionAction.UNKNOWN.value

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(1.0, score))


# ============================================================
# FACTORY
# ============================================================

def build_connector_execution_fabric(
    *,
    connectors: Optional[Dict[str, Any]] = None,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
    max_retry_attempts: int = 1,
    allow_failover: bool = True,
) -> ConnectorExecutionFabric:
    return ConnectorExecutionFabric(
        connectors=connectors,
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
        max_retry_attempts=max_retry_attempts,
        allow_failover=allow_failover,
    )