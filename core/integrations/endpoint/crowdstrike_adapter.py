from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

import requests


def _now_ms() -> int:
    return int(time.time() * 1000)


class CrowdStrikeAdapter:
    """
    CrowdStrike Falcon orchestration adapter.

    Supports:
    - network containment
    - endpoint isolation
    - RTR commands
    - IOC push
    - detection ingestion
    - telemetry retrieval
    - forensic collection hooks

    Used by:
    - ContainmentEngine
    - AutonomousResponseEngine
    - PlaybookOrchestrator
    - Investigation Copilot
    """

    AUTH_URL = (
        "https://api.crowdstrike.com/oauth2/token"
    )

    API_BASE = (
        "https://api.crowdstrike.com"
    )

    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        dry_run_default: bool = True,
        timeout_seconds: int = 30,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token

        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates

        self.dry_run_default = (
            dry_run_default
        )

        self.timeout_seconds = (
            timeout_seconds
        )

    # ------------------------------------------------------------------
    # Endpoint Isolation
    # ------------------------------------------------------------------

    def isolate_endpoint(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "crowdstrike_adapter",
        reason: str = "Endpoint containment",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Falcon containment:
        contain = network containment
        """

        return self._execute_action(
            method="POST",
            endpoint="/devices/entities/devices-actions/v2",
            action="ISOLATE_ENDPOINT",
            target_id=device_id,
            body={
                "action_name": "contain",
                "ids": [device_id],
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    contain_endpoint = isolate_endpoint
    network_isolate_endpoint = isolate_endpoint

    def release_endpoint(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "crowdstrike_adapter",
        reason: str = "Release endpoint containment",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:

        return self._execute_action(
            method="POST",
            endpoint="/devices/entities/devices-actions/v2",
            action="RELEASE_ENDPOINT",
            target_id=device_id,
            body={
                "action_name": "lift_containment",
                "ids": [device_id],
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    # ------------------------------------------------------------------
    # RTR COMMANDS
    # ------------------------------------------------------------------

    def execute_rtr_command(
        self,
        *,
        device_id: str,
        command: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "crowdstrike_adapter",
        reason: str = "RTR command execution",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:

        return self._execute_action(
            method="POST",
            endpoint="/real-time-response/entities/admin-command/v1",
            action="RTR_COMMAND",
            target_id=device_id,
            body={
                "base_command": command,
                "device_id": device_id,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    def collect_memory_dump(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "crowdstrike_adapter",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:

        return self.execute_rtr_command(
            device_id=device_id,
            command="memdump",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason="Collect memory dump",
            dry_run=dry_run,
        )

    def collect_process_list(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "crowdstrike_adapter",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:

        return self.execute_rtr_command(
            device_id=device_id,
            command="ps",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason="Collect process list",
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # IOC MANAGEMENT
    # ------------------------------------------------------------------

    def push_ioc(
        self,
        *,
        indicator_type: str,
        indicator_value: str,
        severity: str = "high",
        action: str = "detect",
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "crowdstrike_adapter",
        reason: str = "Push IOC",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:

        body = {
            "indicators": [
                {
                    "type": indicator_type,
                    "value": indicator_value,
                    "action": action,
                    "severity": severity,
                }
            ]
        }

        return self._execute_action(
            method="POST",
            endpoint="/iocs/entities/indicators/v1",
            action="PUSH_IOC",
            target_id=indicator_value,
            body=body,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=False,
        )

    # ------------------------------------------------------------------
    # DETECTIONS
    # ------------------------------------------------------------------

    def get_detection(
        self,
        *,
        detection_id: str,
    ) -> Dict[str, Any]:

        return self._request(
            method="GET",
            endpoint=(
                "/detects/entities/summaries/GET/v1"
                f"?ids={detection_id}"
            ),
        )

    def search_detections(
        self,
        *,
        filter_query: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:

        query = (
            f"/detects/queries/detects/v1"
            f"?limit={limit}"
        )

        if filter_query:
            query += f"&filter={filter_query}"

        return self._request(
            method="GET",
            endpoint=query,
        )

    # ------------------------------------------------------------------
    # DEVICE INTELLIGENCE
    # ------------------------------------------------------------------

    def get_device(
        self,
        *,
        device_id: str,
    ) -> Dict[str, Any]:

        return self._request(
            method="GET",
            endpoint=(
                "/devices/entities/devices/v2"
                f"?ids={device_id}"
            ),
        )

    def get_device_telemetry(
        self,
        *,
        device_id: str,
    ) -> Dict[str, Any]:

        return self.get_device(
            device_id=device_id,
        )

    def get_host_risk(
        self,
        *,
        device_id: str,
    ) -> Dict[str, Any]:

        return self._record_only(
            marker="HOST_RISK_REQUESTED",
            details={
                "device_id": device_id,
            },
        )

    # ------------------------------------------------------------------
    # Forensics / Preservation
    # ------------------------------------------------------------------

    def preserve_workstation_state(
        self,
        *,
        case_id: Optional[Any] = None,
        requested_by: str = "containment_engine",
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        details = details or {}

        device_id = (
            details.get("device_id")
            or details.get("target_device")
        )

        return self._record_marker(
            case_id=case_id,
            actor=requested_by,
            marker=(
                "CROWDSTRIKE_FORENSIC_"
                "PRESERVATION_REQUESTED"
            ),
            details={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "details": details,
            },
        )

    def collect_forensic_package(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "crowdstrike_adapter",
    ) -> Dict[str, Any]:

        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker=(
                "CROWDSTRIKE_FORENSIC_"
                "PACKAGE_REQUESTED"
            ),
            details={
                "device_id": device_id,
                "tenant_id": tenant_id,
            },
        )

    # ------------------------------------------------------------------
    # ContainmentEngine Compatibility
    # ------------------------------------------------------------------

    def request_endpoint_scan(
        self,
        *,
        case_id: Optional[Any] = None,
        requested_by: str = "containment_engine",
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        details = details or {}

        return self.execute_rtr_command(
            device_id=(
                details.get("device_id")
                or details.get("target_device")
            ),
            command="scan",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=requested_by,
            reason="ContainmentEngine endpoint scan",
            dry_run=details.get(
                "dry_run",
                self.dry_run_default,
            ),
        )

    # ------------------------------------------------------------------
    # Core Execution
    # ------------------------------------------------------------------

    def _execute_action(
        self,
        *,
        method: str,
        endpoint: str,
        action: str,
        target_id: Optional[str],
        body: Optional[Dict[str, Any]],
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        reason: str,
        dry_run: Optional[bool],
        destructive: bool = False,
    ) -> Dict[str, Any]:

        execution_id = (
            f"FALCON-{uuid.uuid4().hex[:12].upper()}"
        )

        dry_run = (
            self.dry_run_default
            if dry_run is None
            else bool(dry_run)
        )

        metadata = {
            "execution_id": execution_id,
            "adapter": "CrowdStrikeAdapter",
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

        self._audit(
            case_id=case_id,
            event_type=(
                "CROWDSTRIKE_ACTION_STARTED"
            ),
            actor=actor,
            details={
                **metadata,
                "body": body,
            },
        )

        if dry_run:

            result = {
                **metadata,
                "status": "dry_run",
                "body": body,
            }

            self._audit(
                case_id=case_id,
                event_type=(
                    "CROWDSTRIKE_ACTION_DRY_RUN"
                ),
                actor=actor,
                details=result,
            )

            self._publish(
                event_type=(
                    "CROWDSTRIKE_ACTION_DRY_RUN"
                ),
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

        try:

            response = self._request(
                method=method,
                endpoint=endpoint,
                body=body,
            )

            result = {
                **metadata,
                "status": "executed",
                "response": response,
                "completed_at_ms": _now_ms(),
            }

            self._audit(
                case_id=case_id,
                event_type=(
                    "CROWDSTRIKE_ACTION_EXECUTED"
                ),
                actor=actor,
                details=result,
            )

            self._publish(
                event_type=(
                    "CROWDSTRIKE_ACTION_EXECUTED"
                ),
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

        except Exception as exc:

            result = {
                **metadata,
                "status": "failed",
                "error": str(exc),
                "failed_at_ms": _now_ms(),
            }

            self._audit(
                case_id=case_id,
                event_type=(
                    "CROWDSTRIKE_ACTION_FAILED"
                ),
                actor=actor,
                details=result,
            )

            self._publish(
                event_type=(
                    "CROWDSTRIKE_ACTION_FAILED"
                ),
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _request(
        self,
        *,
        method: str,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method=method,
            url=f"{self.API_BASE}{endpoint}",
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
                f"CrowdStrike API failed "
                f"({response.status_code}): {text}"
            )

        return {
            "status_code": response.status_code,
            "json": parsed,
            "text": text,
        }

    def _get_access_token(self) -> str:

        if self.access_token:
            return self.access_token

        if not (
            self.client_id
            and self.client_secret
        ):
            raise RuntimeError(
                "CrowdStrike credentials missing."
            )

        response = requests.post(
            self.AUTH_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=self.timeout_seconds,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                f"CrowdStrike auth failed: "
                f"{response.text}"
            )

        data = response.json()

        token = data.get("access_token")

        if not token:
            raise RuntimeError(
                "CrowdStrike access token missing."
            )

        self.access_token = token

        return token

    # ------------------------------------------------------------------
    # Audit / Events
    # ------------------------------------------------------------------

    def _audit(
        self,
        *,
        case_id: Optional[Any],
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:

        if self.ledger is None:
            return

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

    def _publish(
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
                    source="crowdstrike_adapter",
                )

            except Exception:
                pass

        if (
            self.live_updates is not None
            and case_id is not None
        ):

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

    def _record_marker(
        self,
        *,
        case_id: Optional[Any],
        actor: str,
        marker: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:

        self._audit(
            case_id=case_id,
            event_type=marker,
            actor=actor,
            details=details,
        )

        return {
            "marker": marker,
            "recorded": True,
            "timestamp_ms": _now_ms(),
        }

    def _record_only(
        self,
        *,
        marker: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {
            "marker": marker,
            "details": details,
            "timestamp_ms": _now_ms(),
        }