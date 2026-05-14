from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


class ApprovalGate:
    """
    Centralized execution authorization + governance layer.

    Responsibilities:
    - determine if approval required
    - autonomous execution policy
    - export-control governance
    - escalation-aware authorization
    - approval token generation
    - execution grant validation
    - approval lineage integration

    This becomes the enforcement layer between:
    AI orchestration
    and
    real execution adapters.
    """

    DEFAULT_POLICIES = {
        # ----------------------------------------------------------
        # Identity Actions
        # ----------------------------------------------------------
        "DISABLE_USER": {
            "approval_required": True,
            "required_approvals": [
                "MANAGER",
            ],
            "autonomous_allowed": False,
            "risk_level": "HIGH",
        },
        "REVOKE_SESSIONS": {
            "approval_required": False,
            "required_approvals": [],
            "autonomous_allowed": True,
            "risk_level": "MEDIUM",
        },
        "FORCE_PASSWORD_RESET": {
            "approval_required": True,
            "required_approvals": [
                "MANAGER",
            ],
            "autonomous_allowed": False,
            "risk_level": "HIGH",
        },
        # ----------------------------------------------------------
        # Endpoint Actions
        # ----------------------------------------------------------
        "ISOLATE_ENDPOINT": {
            "approval_required": False,
            "required_approvals": [],
            "autonomous_allowed": True,
            "risk_level": "CRITICAL",
        },
        "REMOTE_LOCK": {
            "approval_required": False,
            "required_approvals": [],
            "autonomous_allowed": True,
            "risk_level": "HIGH",
        },
        "WIPE_DEVICE": {
            "approval_required": True,
            "required_approvals": [
                "LEGAL",
                "MANAGER",
            ],
            "autonomous_allowed": False,
            "risk_level": "CRITICAL",
        },
        "RETIRE_DEVICE": {
            "approval_required": True,
            "required_approvals": [
                "MANAGER",
            ],
            "autonomous_allowed": False,
            "risk_level": "HIGH",
        },
        # ----------------------------------------------------------
        # Email Actions
        # ----------------------------------------------------------
        "PURGE_MESSAGE": {
            "approval_required": True,
            "required_approvals": [
                "SOC_LEAD",
            ],
            "autonomous_allowed": False,
            "risk_level": "HIGH",
        },
        "EXCHANGE_MAILBOX_QUARANTINE_REQUESTED": {
            "approval_required": True,
            "required_approvals": [
                "SOC_LEAD",
            ],
            "autonomous_allowed": False,
            "risk_level": "HIGH",
        },
        "EXCHANGE_LEGAL_HOLD_REQUESTED": {
            "approval_required": True,
            "required_approvals": [
                "LEGAL",
            ],
            "autonomous_allowed": False,
            "risk_level": "CRITICAL",
        },
        # ----------------------------------------------------------
        # Cloud / Infra
        # ----------------------------------------------------------
        "TRIGGER_LAMBDA": {
            "approval_required": False,
            "required_approvals": [],
            "autonomous_allowed": True,
            "risk_level": "MEDIUM",
        },
    }

    EXPORT_CONTROL_CATEGORIES = {
        "EXPORT_CONTROL",
        "ITAR",
        "DFARS",
        "CUI",
        "EAR",
        "EAR99",
    }

    HIGH_RISK_SEVERITIES = {
        "HIGH",
        "CRITICAL",
    }

    def __init__(
        self,
        *,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        approval_service: Any = None,
        execution_audit: Any = None,
        custom_policies: Optional[
            Dict[str, Dict[str, Any]]
        ] = None,
    ):
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.approval_service = (
            approval_service
        )
        self.execution_audit = (
            execution_audit
        )

        self.policies = dict(
            self.DEFAULT_POLICIES
        )

        if custom_policies:
            self.policies.update(
                custom_policies
            )

    # ------------------------------------------------------------------
    # Policy Evaluation
    # ------------------------------------------------------------------

    def requires_approval(
        self,
        *,
        action: str,
        severity: Optional[str] = None,
        categories: Optional[List[str]] = None,
        escalation_level: Optional[str] = None,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        policy = self._get_policy(action)

        categories = set(
            categories or []
        )

        approval_required = bool(
            policy.get(
                "approval_required",
                False,
            )
        )

        required_approvals = list(
            policy.get(
                "required_approvals",
                [],
            )
        )

        # ----------------------------------------------------------
        # Export-Control Governance
        # ----------------------------------------------------------

        export_control_hit = bool(
            categories.intersection(
                self.EXPORT_CONTROL_CATEGORIES
            )
        )

        if export_control_hit:
            approval_required = True

            if "LEGAL" not in required_approvals:
                required_approvals.append(
                    "LEGAL"
                )

            if (
                "EXPORT_CONTROL_REVIEW"
                not in required_approvals
            ):
                required_approvals.append(
                    "EXPORT_CONTROL_REVIEW"
                )

        # ----------------------------------------------------------
        # Critical Severity Enforcement
        # ----------------------------------------------------------

        if (
            severity
            and severity.upper()
            in self.HIGH_RISK_SEVERITIES
        ):
            if action in {
                "WIPE_DEVICE",
                "DEACTIVATE_USER",
                "PURGE_MESSAGE",
            }:
                approval_required = True

        # ----------------------------------------------------------
        # Escalation-Aware Logic
        # ----------------------------------------------------------

        escalation_override = False

        if (
            escalation_level
            and escalation_level.upper()
            in {
                "CRITICAL",
                "EMERGENCY",
            }
        ):
            escalation_override = True

        result = {
            "action": action,
            "approval_required": approval_required,
            "required_approvals": sorted(
                set(required_approvals)
            ),
            "export_control_hit": export_control_hit,
            "severity": severity,
            "escalation_level": escalation_level,
            "escalation_override": escalation_override,
            "tenant_id": tenant_id,
            "metadata": metadata or {},
            "evaluated_at_ms": _now_ms(),
        }

        return result

    # ------------------------------------------------------------------
    # Autonomous Execution
    # ------------------------------------------------------------------

    def autonomous_allowed(
        self,
        *,
        action: str,
        severity: Optional[str] = None,
        malware_detected: bool = False,
        categories: Optional[List[str]] = None,
        escalation_level: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        policy = self._get_policy(action)

        categories = set(
            categories or []
        )

        allowed = bool(
            policy.get(
                "autonomous_allowed",
                False,
            )
        )

        reasoning: List[str] = []

        if allowed:
            reasoning.append(
                "Policy allows autonomous execution."
            )

        # ----------------------------------------------------------
        # Malware Emergency Override
        # ----------------------------------------------------------

        if (
            action == "ISOLATE_ENDPOINT"
            and malware_detected
            and severity
            and severity.upper()
            == "CRITICAL"
        ):
            allowed = True

            reasoning.append(
                "Critical malware containment override enabled."
            )

        # ----------------------------------------------------------
        # Export-Control Restrictions
        # ----------------------------------------------------------

        if categories.intersection(
            self.EXPORT_CONTROL_CATEGORIES
        ):
            if action in {
                "EXPORT_MAILBOX",
                "WIPE_DEVICE",
                "PURGE_MESSAGE",
            }:
                allowed = False

                reasoning.append(
                    "Export-control governance blocks autonomous execution."
                )

        # ----------------------------------------------------------
        # Emergency Escalation Override
        # ----------------------------------------------------------

        if (
            escalation_level
            and escalation_level.upper()
            == "EMERGENCY"
        ):
            if action in {
                "ISOLATE_ENDPOINT",
                "REVOKE_SESSIONS",
                "REMOTE_LOCK",
            }:
                allowed = True

                reasoning.append(
                    "Emergency escalation override enabled."
                )

        result = {
            "action": action,
            "autonomous_allowed": allowed,
            "severity": severity,
            "malware_detected": malware_detected,
            "categories": list(categories),
            "escalation_level": escalation_level,
            "reasoning": reasoning,
            "metadata": metadata or {},
            "evaluated_at_ms": _now_ms(),
        }

        return result

    # ------------------------------------------------------------------
    # Approval Requests
    # ------------------------------------------------------------------

    def request_approval(
        self,
        *,
        action: str,
        actor: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        target_id: Optional[str] = None,
        severity: Optional[str] = None,
        categories: Optional[List[str]] = None,
        justification: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        evaluation = self.requires_approval(
            action=action,
            severity=severity,
            categories=categories,
            tenant_id=tenant_id,
            metadata=metadata,
        )

        approval_id = (
            f"APPROVAL-{uuid.uuid4().hex[:12].upper()}"
        )

        record = {
            "approval_id": approval_id,
            "action": action,
            "actor": actor,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "target_id": target_id,
            "severity": severity,
            "categories": categories or [],
            "required_approvals": evaluation.get(
                "required_approvals",
                [],
            ),
            "approval_required": evaluation.get(
                "approval_required",
                False,
            ),
            "status": "PENDING",
            "justification": justification,
            "metadata": metadata or {},
            "requested_at_ms": _now_ms(),
        }

        self._persist_approval(record)

        self._record_case_event(
            case_id=case_id,
            event_type="APPROVAL_REQUESTED",
            actor=actor,
            details=record,
        )

        self._publish(
            event_type="APPROVAL_REQUESTED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=record,
        )

        return record

    # ------------------------------------------------------------------
    # Approval Grants
    # ------------------------------------------------------------------

    def issue_execution_grant(
        self,
        *,
        approval_id: str,
        approved_by: str,
        grant_type: str = "STANDARD",
        expires_in_seconds: int = 3600,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        grant_id = (
            f"GRANT-{uuid.uuid4().hex[:12].upper()}"
        )

        now_ms = _now_ms()

        record = {
            "grant_id": grant_id,
            "approval_id": approval_id,
            "approved_by": approved_by,
            "grant_type": grant_type,
            "issued_at_ms": now_ms,
            "expires_at_ms": (
                now_ms
                + (expires_in_seconds * 1000)
            ),
            "metadata": metadata or {},
        }

        self._persist_grant(record)

        self._record_case_event(
            case_id=case_id,
            event_type="EXECUTION_GRANT_ISSUED",
            actor=approved_by,
            details=record,
        )

        self._publish(
            event_type="EXECUTION_GRANT_ISSUED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=approved_by,
            payload=record,
        )

        return record

    def validate_execution_grant(
        self,
        *,
        grant_id: str,
    ) -> Dict[str, Any]:
        record = self._get_grant(
            grant_id=grant_id
        )

        if not record:
            return {
                "valid": False,
                "reason": "Grant not found.",
            }

        now_ms = _now_ms()

        expires_at_ms = int(
            record.get("expires_at_ms", 0)
        )

        if now_ms > expires_at_ms:
            return {
                "valid": False,
                "reason": "Grant expired.",
                "grant": record,
            }

        return {
            "valid": True,
            "grant": record,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist_approval(
        self,
        record: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    INSERT INTO execution_approvals (
                        approval_id,
                        action,
                        actor,
                        case_id,
                        tenant_id,
                        target_id,
                        severity,
                        categories_json,
                        required_approvals_json,
                        approval_required,
                        status,
                        justification,
                        metadata_json,
                        requested_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("approval_id"),
                        record.get("action"),
                        record.get("actor"),
                        record.get("case_id"),
                        record.get("tenant_id"),
                        record.get("target_id"),
                        record.get("severity"),
                        json.dumps(
                            record.get("categories")
                        ),
                        json.dumps(
                            record.get(
                                "required_approvals"
                            )
                        ),
                        int(
                            bool(
                                record.get(
                                    "approval_required"
                                )
                            )
                        ),
                        record.get("status"),
                        record.get("justification"),
                        json.dumps(
                            record.get("metadata")
                        ),
                        record.get(
                            "requested_at_ms"
                        ),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _persist_grant(
        self,
        record: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    INSERT INTO execution_grants (
                        grant_id,
                        approval_id,
                        approved_by,
                        grant_type,
                        issued_at_ms,
                        expires_at_ms,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("grant_id"),
                        record.get("approval_id"),
                        record.get("approved_by"),
                        record.get("grant_type"),
                        record.get("issued_at_ms"),
                        record.get("expires_at_ms"),
                        json.dumps(
                            record.get("metadata")
                        ),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _get_grant(
        self,
        *,
        grant_id: str,
    ) -> Optional[Dict[str, Any]]:
        if self.ledger is None:
            return None

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                row = con.execute(
                    """
                    SELECT *
                    FROM execution_grants
                    WHERE grant_id = ?
                    LIMIT 1
                    """,
                    (grant_id,),
                ).fetchone()

                return dict(row) if row else None
        except Exception:
            return None

    def _ensure_tables(self) -> None:
        if self.ledger is None:
            return

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS execution_approvals (
                        approval_id TEXT PRIMARY KEY,
                        action TEXT,
                        actor TEXT,
                        case_id TEXT,
                        tenant_id TEXT,
                        target_id TEXT,
                        severity TEXT,
                        categories_json TEXT,
                        required_approvals_json TEXT,
                        approval_required INTEGER,
                        status TEXT,
                        justification TEXT,
                        metadata_json TEXT,
                        requested_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS execution_grants (
                        grant_id TEXT PRIMARY KEY,
                        approval_id TEXT,
                        approved_by TEXT,
                        grant_type TEXT,
                        issued_at_ms INTEGER,
                        expires_at_ms INTEGER,
                        metadata_json TEXT
                    )
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_exec_approvals_case
                    ON execution_approvals(case_id)
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_exec_approvals_status
                    ON execution_approvals(status)
                    """
                )

                con.commit()

        except Exception:
            pass

    # ------------------------------------------------------------------
    # Policies
    # ------------------------------------------------------------------

    def _get_policy(
        self,
        action: str,
    ) -> Dict[str, Any]:
        return self.policies.get(
            action,
            {
                "approval_required": True,
                "required_approvals": [
                    "SOC_LEAD"
                ],
                "autonomous_allowed": False,
                "risk_level": "UNKNOWN",
            },
        )

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _record_case_event(
        self,
        *,
        case_id: Optional[Any],
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
        if self.ledger is None or case_id is None:
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
                    source="approval_gate",
                )
            except Exception:
                pass

        if self.live_updates is not None and case_id is not None:
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