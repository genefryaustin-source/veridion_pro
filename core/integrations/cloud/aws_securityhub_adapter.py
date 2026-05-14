from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


def _now_ms() -> int:
    return int(time.time() * 1000)


class AWSSecurityHubAdapter:
    """
    AWS Security Hub / GovCloud orchestration adapter.

    Supports:
    - ingest Security Hub findings
    - update findings
    - correlate cloud alerts
    - push containment markers
    - trigger Lambda workflows
    - incident tagging
    - severity normalization
    - cloud investigation enrichment

    Used by:
    - AutonomousResponseEngine
    - PlaybookOrchestrator
    - CaseIntelligenceService
    - CopilotService
    """

    def __init__(
        self,
        *,
        region_name: str = "us-gov-west-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        profile_name: Optional[str] = None,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        dry_run_default: bool = True,
    ):
        self.region_name = region_name
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.dry_run_default = dry_run_default

        session_kwargs = {
            "region_name": region_name,
        }

        if profile_name:
            session_kwargs["profile_name"] = (
                profile_name
            )

        if aws_access_key_id:
            session_kwargs[
                "aws_access_key_id"
            ] = aws_access_key_id

        if aws_secret_access_key:
            session_kwargs[
                "aws_secret_access_key"
            ] = aws_secret_access_key

        if aws_session_token:
            session_kwargs[
                "aws_session_token"
            ] = aws_session_token

        self.session = boto3.Session(
            **session_kwargs
        )

        self.securityhub = (
            self.session.client(
                "securityhub",
                region_name=region_name,
            )
        )

        self.lambda_client = (
            self.session.client(
                "lambda",
                region_name=region_name,
            )
        )

    # ------------------------------------------------------------------
    # Findings
    # ------------------------------------------------------------------

    def get_findings(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        max_results: int = 100,
    ) -> Dict[str, Any]:
        try:
            response = self.securityhub.get_findings(
                Filters=filters or {},
                MaxResults=max_results,
            )

            return {
                "status": "success",
                "count": len(
                    response.get(
                        "Findings",
                        [],
                    )
                ),
                "findings": response.get(
                    "Findings",
                    [],
                ),
                "timestamp_ms": _now_ms(),
            }

        except Exception as exc:
            return {
                "status": "failed",
                "error": str(exc),
                "timestamp_ms": _now_ms(),
            }

    def get_finding(
        self,
        *,
        finding_id: str,
    ) -> Dict[str, Any]:
        result = self.get_findings(
            filters={
                "Id": [
                    {
                        "Value": finding_id,
                        "Comparison": "EQUALS",
                    }
                ]
            },
            max_results=1,
        )

        findings = result.get(
            "findings",
            [],
        )

        return {
            "status": result.get("status"),
            "finding": findings[0]
            if findings
            else None,
            "timestamp_ms": _now_ms(),
        }

    def ingest_findings_into_case(
        self,
        *,
        case_id: Any,
        finding_filters: Optional[
            Dict[str, Any]
        ] = None,
        tenant_id: Optional[str] = None,
        actor: str = (
            "aws_securityhub_adapter"
        ),
    ) -> Dict[str, Any]:
        findings_result = self.get_findings(
            filters=finding_filters,
        )

        findings = findings_result.get(
            "findings",
            [],
        )

        normalized = []

        for finding in findings:
            normalized.append(
                self._normalize_finding(
                    finding
                )
            )

        result = {
            "status": "success",
            "case_id": case_id,
            "tenant_id": tenant_id,
            "finding_count": len(normalized),
            "findings": normalized,
            "timestamp_ms": _now_ms(),
        }

        self._audit(
            case_id=case_id,
            event_type=(
                "AWS_SECURITYHUB_"
                "FINDINGS_INGESTED"
            ),
            actor=actor,
            details=result,
        )

        self._publish(
            event_type=(
                "AWS_SECURITYHUB_"
                "FINDINGS_INGESTED"
            ),
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=result,
        )

        return result

    # ------------------------------------------------------------------
    # Findings Updates
    # ------------------------------------------------------------------

    def update_finding_workflow(
        self,
        *,
        finding_id: str,
        product_arn: str,
        workflow_status: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = (
            "aws_securityhub_adapter"
        ),
        reason: str = (
            "Update Security Hub workflow"
        ),
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute(
            action=(
                "UPDATE_FINDING_WORKFLOW"
            ),
            target_id=finding_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            operation=lambda: (
                self.securityhub.batch_update_findings(
                    FindingIdentifiers=[
                        {
                            "Id": finding_id,
                            "ProductArn": product_arn,
                        }
                    ],
                    Workflow={
                        "Status": workflow_status,
                    },
                )
            ),
        )

    def add_finding_note(
        self,
        *,
        finding_id: str,
        product_arn: str,
        note: str,
        updated_by: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = (
            "aws_securityhub_adapter"
        ),
        reason: str = (
            "Add Security Hub note"
        ),
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute(
            action="ADD_FINDING_NOTE",
            target_id=finding_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            operation=lambda: (
                self.securityhub.batch_update_findings(
                    FindingIdentifiers=[
                        {
                            "Id": finding_id,
                            "ProductArn": product_arn,
                        }
                    ],
                    Note={
                        "Text": note,
                        "UpdatedBy": updated_by,
                    },
                )
            ),
        )

    # ------------------------------------------------------------------
    # Cloud Correlation
    # ------------------------------------------------------------------

    def correlate_cloud_alerts(
        self,
        *,
        case_id: Any,
        account_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        severity_label: Optional[str] = None,
        tenant_id: Optional[str] = None,
        actor: str = (
            "aws_securityhub_adapter"
        ),
    ) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}

        if account_id:
            filters["AwsAccountId"] = [
                {
                    "Value": account_id,
                    "Comparison": "EQUALS",
                }
            ]

        if resource_id:
            filters["ResourceId"] = [
                {
                    "Value": resource_id,
                    "Comparison": "EQUALS",
                }
            ]

        if severity_label:
            filters["SeverityLabel"] = [
                {
                    "Value": severity_label,
                    "Comparison": "EQUALS",
                }
            ]

        findings = self.get_findings(
            filters=filters,
            max_results=250,
        )

        result = {
            "status": "success",
            "case_id": case_id,
            "tenant_id": tenant_id,
            "correlated_count": findings.get(
                "count",
                0,
            ),
            "filters": filters,
            "timestamp_ms": _now_ms(),
        }

        self._audit(
            case_id=case_id,
            event_type=(
                "AWS_SECURITYHUB_"
                "CORRELATION_COMPLETED"
            ),
            actor=actor,
            details=result,
        )

        return result

    # ------------------------------------------------------------------
    # Lambda Orchestration
    # ------------------------------------------------------------------

    def trigger_lambda_workflow(
        self,
        *,
        function_name: str,
        payload: Dict[str, Any],
        invocation_type: str = "Event",
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = (
            "aws_securityhub_adapter"
        ),
        reason: str = (
            "Trigger Lambda workflow"
        ),
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return self._execute(
            action="TRIGGER_LAMBDA",
            target_id=function_name,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            operation=lambda: (
                self.lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType=invocation_type,
                    Payload=json.dumps(
                        payload
                    ).encode("utf-8"),
                )
            ),
        )

    # ------------------------------------------------------------------
    # Incident Tagging
    # ------------------------------------------------------------------

    def tag_incident(
        self,
        *,
        finding_id: str,
        product_arn: str,
        tags: Dict[str, str],
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = (
            "aws_securityhub_adapter"
        ),
        reason: str = (
            "Tag Security Hub incident"
        ),
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        note = (
            "Incident Tags: "
            + json.dumps(tags)
        )

        return self.add_finding_note(
            finding_id=finding_id,
            product_arn=product_arn,
            note=note,
            updated_by=actor,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
        )

    # ------------------------------------------------------------------
    # Severity Normalization
    # ------------------------------------------------------------------

    def normalize_severity(
        self,
        *,
        finding: Dict[str, Any],
    ) -> Dict[str, Any]:
        severity = (
            finding.get("Severity")
            or {}
        )

        label = str(
            severity.get("Label")
            or "UNKNOWN"
        ).upper()

        normalized = {
            "INFORMATIONAL": "LOW",
            "LOW": "LOW",
            "MEDIUM": "MEDIUM",
            "HIGH": "HIGH",
            "CRITICAL": "CRITICAL",
        }

        return {
            "original": label,
            "normalized": normalized.get(
                label,
                "UNKNOWN",
            ),
        }

    # ------------------------------------------------------------------
    # Internal Execution
    # ------------------------------------------------------------------

    def _execute(
        self,
        *,
        action: str,
        target_id: str,
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        reason: str,
        dry_run: Optional[bool],
        operation: Any,
    ) -> Dict[str, Any]:
        execution_id = (
            f"AWSSEC-{uuid.uuid4().hex[:12].upper()}"
        )

        dry_run = (
            self.dry_run_default
            if dry_run is None
            else bool(dry_run)
        )

        metadata = {
            "execution_id": execution_id,
            "adapter": (
                "AWSSecurityHubAdapter"
            ),
            "action": action,
            "target_id": target_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "actor": actor,
            "reason": reason,
            "dry_run": dry_run,
            "timestamp_ms": _now_ms(),
        }

        self._audit(
            case_id=case_id,
            event_type=(
                "AWS_SECURITYHUB_"
                "ACTION_STARTED"
            ),
            actor=actor,
            details=metadata,
        )

        if dry_run:
            result = {
                **metadata,
                "status": "dry_run",
            }

            self._audit(
                case_id=case_id,
                event_type=(
                    "AWS_SECURITYHUB_"
                    "ACTION_DRY_RUN"
                ),
                actor=actor,
                details=result,
            )

            self._publish(
                event_type=(
                    "AWS_SECURITYHUB_"
                    "ACTION_DRY_RUN"
                ),
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

        try:
            response = operation()

            result = {
                **metadata,
                "status": "executed",
                "response": self._safe_response(
                    response
                ),
                "completed_at_ms": _now_ms(),
            }

            self._audit(
                case_id=case_id,
                event_type=(
                    "AWS_SECURITYHUB_"
                    "ACTION_EXECUTED"
                ),
                actor=actor,
                details=result,
            )

            self._publish(
                event_type=(
                    "AWS_SECURITYHUB_"
                    "ACTION_EXECUTED"
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
                    "AWS_SECURITYHUB_"
                    "ACTION_FAILED"
                ),
                actor=actor,
                details=result,
            )

            self._publish(
                event_type=(
                    "AWS_SECURITYHUB_"
                    "ACTION_FAILED"
                ),
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalize_finding(
        self,
        finding: Dict[str, Any],
    ) -> Dict[str, Any]:
        severity = (
            self.normalize_severity(
                finding=finding
            )
        )

        return {
            "finding_id": finding.get("Id"),
            "title": finding.get("Title"),
            "description": finding.get(
                "Description"
            ),
            "severity": severity,
            "account_id": finding.get(
                "AwsAccountId"
            ),
            "resources": finding.get(
                "Resources",
                [],
            ),
            "types": finding.get(
                "Types",
                [],
            ),
            "created_at": finding.get(
                "CreatedAt"
            ),
            "updated_at": finding.get(
                "UpdatedAt"
            ),
            "workflow": finding.get(
                "Workflow",
                {},
            ),
        }

    def _safe_response(
        self,
        response: Any,
    ) -> Dict[str, Any]:
        try:
            return json.loads(
                json.dumps(
                    response,
                    default=str,
                )
            )
        except Exception:
            return {
                "response": str(response)
            }

    # ------------------------------------------------------------------
    # Audit / Realtime
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
                    source=(
                        "aws_securityhub_adapter"
                    ),
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