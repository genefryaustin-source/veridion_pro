from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

import requests


def _now_ms() -> int:
    return int(time.time() * 1000)


class IntuneAdapter:
    """
    Microsoft Intune / Microsoft Graph endpoint orchestration adapter.

    Supports:
    - isolate endpoint
    - release endpoint
    - trigger device scan
    - preserve workstation state
    - collect forensic package
    - remote lock
    - wipe device
    - retire device
    - quarantine device
    - device intelligence retrieval

    IMPORTANT:
    This adapter assumes:
    - approval enforcement already occurred upstream
    - governance handled by orchestration layer
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
    # Endpoint Isolation
    # ------------------------------------------------------------------

    def isolate_endpoint(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Endpoint isolation",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Isolation is modeled operationally here because Intune itself
        does not provide full EDR network isolation like Defender/CrowdStrike.

        This creates:
        - audit-safe containment event
        - operational quarantine marker
        - future Defender/CrowdStrike orchestration hook
        """

        return self._execute_action(
            method="POST",
            url=f"{self.GRAPH_BETA_URL}/deviceManagement/managedDevices/{device_id}/syncDevice",
            action="ISOLATE_ENDPOINT",
            device_id=device_id,
            body={
                "containment_state": "ISOLATED",
                "reason": reason,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def release_endpoint(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Release endpoint isolation",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_action(
            method="POST",
            url=f"{self.GRAPH_BETA_URL}/deviceManagement/managedDevices/{device_id}/syncDevice",
            action="RELEASE_ENDPOINT",
            device_id=device_id,
            body={
                "containment_state": "RELEASED",
                "reason": reason,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # Device Scan / Collection
    # ------------------------------------------------------------------

    def trigger_device_scan(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Trigger device scan",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_action(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/deviceManagement/managedDevices/{device_id}/syncDevice",
            action="TRIGGER_DEVICE_SCAN",
            device_id=device_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    request_endpoint_scan = trigger_device_scan

    def collect_defender_scan(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Collect Defender telemetry",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="DEFENDER_SCAN_COLLECTION_REQUESTED",
            details={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "reason": reason,
                "dry_run": dry_run,
            },
        )

    # ------------------------------------------------------------------
    # Forensic Preservation
    # ------------------------------------------------------------------

    def preserve_workstation_state(
        self,
        *,
        device_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        requested_by: str = "containment_engine",
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        details = details or {}

        device_id = (
            device_id
            or details.get("device_id")
            or details.get("target_device")
        )

        return self._record_marker(
            case_id=case_id,
            actor=requested_by,
            marker="WORKSTATION_STATE_PRESERVATION_REQUESTED",
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
        actor: str = "intune_adapter",
        reason: str = "Collect forensic package",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="FORENSIC_PACKAGE_COLLECTION_REQUESTED",
            details={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "reason": reason,
                "dry_run": dry_run,
            },
        )

    def snapshot_device(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Create device snapshot",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="DEVICE_SNAPSHOT_REQUESTED",
            details={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "reason": reason,
                "dry_run": dry_run,
            },
        )

    # ------------------------------------------------------------------
    # Remote Device Control
    # ------------------------------------------------------------------

    def remote_lock(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Remote device lock",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_action(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/deviceManagement/managedDevices/{device_id}/remoteLock",
            action="REMOTE_LOCK",
            device_id=device_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def sync_device(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Sync device",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_action(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/deviceManagement/managedDevices/{device_id}/syncDevice",
            action="SYNC_DEVICE",
            device_id=device_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    def wipe_device(
        self,
        *,
        device_id: str,
        keep_enrollment_data: bool = False,
        keep_user_data: bool = False,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Wipe device",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_action(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/deviceManagement/managedDevices/{device_id}/wipe",
            action="WIPE_DEVICE",
            device_id=device_id,
            body={
                "keepEnrollmentData": keep_enrollment_data,
                "keepUserData": keep_user_data,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    def retire_device(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Retire device",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute_action(
            method="POST",
            url=f"{self.GRAPH_BASE_URL}/deviceManagement/managedDevices/{device_id}/retire",
            action="RETIRE_DEVICE",
            device_id=device_id,
            body={},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            destructive=True,
        )

    # ------------------------------------------------------------------
    # Quarantine
    # ------------------------------------------------------------------

    def quarantine_device(
        self,
        *,
        device_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "intune_adapter",
        reason: str = "Quarantine device",
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="DEVICE_QUARANTINE_REQUESTED",
            details={
                "device_id": device_id,
                "tenant_id": tenant_id,
                "reason": reason,
                "dry_run": dry_run,
            },
        )

    move_device_to_quarantine_group = quarantine_device

    # ------------------------------------------------------------------
    # Device Intelligence
    # ------------------------------------------------------------------

    def get_device_health(
        self,
        *,
        device_id: str,
    ) -> Dict[str, Any]:
        return self._get_device(device_id)

    def get_device_risk(
        self,
        *,
        device_id: str,
    ) -> Dict[str, Any]:
        return self._get_device(device_id)

    def get_device_compliance(
        self,
        *,
        device_id: str,
    ) -> Dict[str, Any]:
        return self._get_device(device_id)

    def get_device_primary_user(
        self,
        *,
        device_id: str,
    ) -> Dict[str, Any]:
        return self._request(
            method="GET",
            url=f"{self.GRAPH_BASE_URL}/deviceManagement/managedDevices/{device_id}/users",
        )

    # ------------------------------------------------------------------
    # ContainmentEngine Compatibility
    # ------------------------------------------------------------------

    def contain_endpoint(
        self,
        *,
        case_id: Any = None,
        requested_by: str = "containment_engine",
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        details = details or {}

        return self.isolate_endpoint(
            device_id=details.get("device_id")
            or details.get("target_device"),
            case_id=case_id,
            tenant_id=tenant_id,
            actor=requested_by,
            reason=details.get("reason")
            or "ContainmentEngine isolate endpoint",
            dry_run=details.get(
                "dry_run",
                self.dry_run_default,
            ),
        )

    network_isolate_endpoint = contain_endpoint

    # ------------------------------------------------------------------
    # Internal Graph Actions
    # ------------------------------------------------------------------

    def _execute_action(
        self,
        *,
        method: str,
        url: str,
        action: str,
        device_id: Optional[str],
        body: Optional[Dict[str, Any]],
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        reason: str,
        dry_run: Optional[bool],
        destructive: bool = False,
    ) -> Dict[str, Any]:
        execution_id = (
            f"INTUNE-{uuid.uuid4().hex[:12].upper()}"
        )

        dry_run = (
            self.dry_run_default
            if dry_run is None
            else bool(dry_run)
        )

        metadata = {
            "execution_id": execution_id,
            "adapter": "IntuneAdapter",
            "action": action,
            "device_id": device_id,
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
            event_type="INTUNE_ACTION_STARTED",
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
                event_type="INTUNE_ACTION_DRY_RUN",
                actor=actor,
                details=result,
            )

            self._publish(
                event_type="INTUNE_ACTION_DRY_RUN",
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
                **metadata,
                "status": "executed",
                "response": response,
                "completed_at_ms": _now_ms(),
            }

            self._audit(
                case_id=case_id,
                event_type="INTUNE_ACTION_EXECUTED",
                actor=actor,
                details=result,
            )

            self._publish(
                event_type="INTUNE_ACTION_EXECUTED",
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
                event_type="INTUNE_ACTION_FAILED",
                actor=actor,
                details=result,
            )

            self._publish(
                event_type="INTUNE_ACTION_FAILED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

    def _get_device(
        self,
        device_id: str,
    ) -> Dict[str, Any]:
        return self._request(
            method="GET",
            url=f"{self.GRAPH_BASE_URL}/deviceManagement/managedDevices/{device_id}",
        )

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

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
                    source="intune_adapter",
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