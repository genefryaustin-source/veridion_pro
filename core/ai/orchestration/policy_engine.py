from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


class PolicyEngine:
    """
    Autonomous decision policy layer.

    Decides:
    - what AI may do
    - what AI must escalate
    - what AI may autonomously contain
    - tenant-specific governance
    - export-control restrictions
    - legal restrictions
    - CMMC / DFARS enforcement
    - blast-radius constraints
    - confidence-aware execution
    """

    EXPORT_CONTROL_TERMS = {
        "EXPORT_CONTROL",
        "ITAR",
        "EAR",
        "EAR99",
        "DFARS",
        "CUI",
        "CTI",
        "USML",
    }

    DESTRUCTIVE_ACTIONS = {
        "DISABLE_USER",
        "DEACTIVATE_USER",
        "WIPE_DEVICE",
        "RETIRE_DEVICE",
        "PURGE_MESSAGE",
        "DELETE_EVIDENCE",
        "EXPORT_EVIDENCE",
        "MERGE_INVESTIGATIONS",
    }

    SAFE_AUTONOMOUS_ACTIONS = {
        "REVOKE_SESSIONS",
        "PRESERVE_EVIDENCE",
        "REQUEST_ENDPOINT_SCAN",
        "SYNC_DEVICE",
        "REMOTE_LOCK",
        "ESCALATE_CASE",
        "LINK_RELATED_CASES",
        "CLUSTER_EVIDENCE",
    }

    CONDITIONAL_AUTONOMOUS_ACTIONS = {
        "ISOLATE_ENDPOINT",
        "QUARANTINE_MAILBOX",
        "SUSPEND_USER",
        "MOVE_MESSAGE_TO_JUNK",
        "TRIGGER_LAMBDA",
    }

    DEFAULT_POLICY = {
        "autonomy_level": "APPROVAL_FIRST",
        "max_devices_isolated": 5,
        "max_users_disabled": 3,
        "max_mailboxes_quarantined": 3,
        "max_messages_purged": 10,
        "require_approval_for_export_control": True,
        "require_approval_for_destructive": True,
        "require_legal_for_export_control": True,
        "full_audit_required": True,
        "min_confidence_auto": 85,
        "allow_critical_malware_isolation": True,
        "allow_session_revocation": True,
    }

    TENANT_POLICY_PROFILES = {
        "LOCKHEED": {
            "autonomy_level": "STRICT_EXPORT_CONTROL",
            "require_approval_for_export_control": True,
            "require_legal_for_export_control": True,
            "max_devices_isolated": 2,
            "max_users_disabled": 1,
            "min_confidence_auto": 92,
        },
        "BANK": {
            "autonomy_level": "AGGRESSIVE_CONTAINMENT",
            "max_devices_isolated": 10,
            "max_users_disabled": 2,
            "min_confidence_auto": 82,
            "allow_critical_malware_isolation": True,
        },
        "MSSP": {
            "autonomy_level": "APPROVAL_HEAVY",
            "max_devices_isolated": 3,
            "max_users_disabled": 1,
            "min_confidence_auto": 90,
        },
        "GOVCLOUD": {
            "autonomy_level": "FULL_AUDIT",
            "full_audit_required": True,
            "require_approval_for_export_control": True,
            "require_legal_for_export_control": True,
            "max_devices_isolated": 2,
            "max_users_disabled": 1,
            "min_confidence_auto": 94,
        },
    }

    def __init__(
        self,
        *,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        custom_tenant_policies: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.custom_tenant_policies = custom_tenant_policies or {}

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def evaluate_action(
        self,
        *,
        action: str,
        tenant_id: Optional[str] = None,
        severity: Optional[str] = None,
        confidence: Optional[int] = None,
        categories: Optional[List[str]] = None,
        blast_radius_score: Optional[int] = None,
        malware_detected: bool = False,
        targets: Optional[Dict[str, int]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        action = _upper(action)
        severity = _upper(severity)
        confidence = _safe_int(confidence, 0)
        categories = [_upper(c) for c in (categories or [])]
        blast_radius_score = _safe_int(blast_radius_score, 0)
        targets = targets or {}

        policy = self.get_policy_for_tenant(tenant_id)

        reasoning: List[str] = []

        export_control = self._has_export_control(categories, context)
        destructive = action in self.DESTRUCTIVE_ACTIONS
        safe_action = action in self.SAFE_AUTONOMOUS_ACTIONS
        conditional_action = action in self.CONDITIONAL_AUTONOMOUS_ACTIONS

        risk_score = self._calculate_risk_score(
            action=action,
            severity=severity,
            confidence=confidence,
            categories=categories,
            blast_radius_score=blast_radius_score,
            malware_detected=malware_detected,
            targets=targets,
            destructive=destructive,
            export_control=export_control,
        )

        approval_required = False
        legal_required = False
        allowed = False
        must_escalate = False

        if destructive and policy.get("require_approval_for_destructive", True):
            approval_required = True
            reasoning.append("Destructive action requires approval.")

        if export_control and policy.get("require_approval_for_export_control", True):
            approval_required = True
            reasoning.append("Export-control/CUI/DFARS category requires approval.")

        if export_control and policy.get("require_legal_for_export_control", True):
            legal_required = True
            reasoning.append("Export-control/CUI/DFARS category requires legal or export review.")

        if confidence < _safe_int(policy.get("min_confidence_auto"), 85):
            approval_required = True
            reasoning.append("AI confidence below autonomous execution threshold.")

        blast_result = self._check_blast_radius(
            action=action,
            targets=targets,
            policy=policy,
        )

        if not blast_result["within_limits"]:
            approval_required = True
            must_escalate = True
            reasoning.extend(blast_result["reasons"])

        if severity in {"HIGH", "CRITICAL"}:
            must_escalate = True
            reasoning.append("High/Critical severity requires escalation awareness.")

        if action == "ISOLATE_ENDPOINT" and malware_detected and severity == "CRITICAL":
            if policy.get("allow_critical_malware_isolation", True):
                allowed = True
                approval_required = False if not export_control else approval_required
                reasoning.append("Critical malware isolation is allowed by policy.")

        elif safe_action:
            allowed = True
            reasoning.append("Action is classified as safe autonomous operation.")

        elif conditional_action:
            allowed = (
                confidence >= _safe_int(policy.get("min_confidence_auto"), 85)
                and blast_result["within_limits"]
                and not export_control
            )
            if allowed:
                reasoning.append("Conditional autonomous action passed policy thresholds.")

        if destructive:
            allowed = False
            reasoning.append("Destructive action cannot be autonomously executed.")

        if approval_required or legal_required:
            allowed = False

        decision = {
            "action": action,
            "tenant_id": tenant_id,
            "policy": policy,
            "allowed": allowed,
            "approval_required": approval_required,
            "legal_required": legal_required,
            "must_escalate": must_escalate,
            "export_control": export_control,
            "destructive": destructive,
            "risk_score": risk_score,
            "risk_level": self._risk_level(risk_score),
            "confidence": confidence,
            "blast_radius_score": blast_radius_score,
            "targets": targets,
            "reasoning": reasoning or ["Policy evaluation completed."],
            "evaluated_at_ms": _now_ms(),
            "engine": "PolicyEngine",
        }

        self._publish_decision(decision)

        return decision

    # ------------------------------------------------------------------
    # Tenant Policies
    # ------------------------------------------------------------------

    def get_policy_for_tenant(
        self,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        policy = dict(self.DEFAULT_POLICY)

        tenant_key = _upper(tenant_id)

        if tenant_key in self.TENANT_POLICY_PROFILES:
            policy.update(self.TENANT_POLICY_PROFILES[tenant_key])

        if tenant_key in self.custom_tenant_policies:
            policy.update(self.custom_tenant_policies[tenant_key])

        return policy

    # ------------------------------------------------------------------
    # Batch / Blast Radius
    # ------------------------------------------------------------------

    def _check_blast_radius(
        self,
        *,
        action: str,
        targets: Dict[str, int],
        policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        reasons = []

        devices = _safe_int(targets.get("devices"), 0)
        users = _safe_int(targets.get("users"), 0)
        mailboxes = _safe_int(targets.get("mailboxes"), 0)
        messages = _safe_int(targets.get("messages"), 0)

        if action in {"ISOLATE_ENDPOINT", "REMOTE_LOCK", "WIPE_DEVICE"}:
            max_devices = _safe_int(policy.get("max_devices_isolated"), 5)
            if devices > max_devices:
                reasons.append(f"Device target count {devices} exceeds policy limit {max_devices}.")

        if action in {"DISABLE_USER", "SUSPEND_USER", "DEACTIVATE_USER"}:
            max_users = _safe_int(policy.get("max_users_disabled"), 3)
            if users > max_users:
                reasons.append(f"User target count {users} exceeds policy limit {max_users}.")

        if action in {"QUARANTINE_MAILBOX"}:
            max_mailboxes = _safe_int(policy.get("max_mailboxes_quarantined"), 3)
            if mailboxes > max_mailboxes:
                reasons.append(f"Mailbox target count {mailboxes} exceeds policy limit {max_mailboxes}.")

        if action in {"PURGE_MESSAGE"}:
            max_messages = _safe_int(policy.get("max_messages_purged"), 10)
            if messages > max_messages:
                reasons.append(f"Message target count {messages} exceeds policy limit {max_messages}.")

        return {
            "within_limits": len(reasons) == 0,
            "reasons": reasons,
        }

    # ------------------------------------------------------------------
    # Risk Scoring
    # ------------------------------------------------------------------

    def _calculate_risk_score(
        self,
        *,
        action: str,
        severity: str,
        confidence: int,
        categories: List[str],
        blast_radius_score: int,
        malware_detected: bool,
        targets: Dict[str, int],
        destructive: bool,
        export_control: bool,
    ) -> int:
        score = 0

        score += {
            "CRITICAL": 35,
            "HIGH": 25,
            "MEDIUM": 15,
            "LOW": 5,
        }.get(severity, 0)

        score += min(blast_radius_score // 3, 30)

        if destructive:
            score += 35

        if export_control:
            score += 30

        if malware_detected:
            score += 15

        target_count = sum(_safe_int(v) for v in targets.values())
        score += min(target_count * 2, 25)

        if confidence < 70:
            score += 20
        elif confidence < 85:
            score += 10

        if action in self.CONDITIONAL_AUTONOMOUS_ACTIONS:
            score += 10

        return min(score, 100)

    def _risk_level(
        self,
        score: int,
    ) -> str:
        if score >= 85:
            return "CRITICAL"
        if score >= 65:
            return "HIGH"
        if score >= 35:
            return "MEDIUM"
        return "LOW"

    # ------------------------------------------------------------------
    # Export-Control Detection
    # ------------------------------------------------------------------

    def _has_export_control(
        self,
        categories: List[str],
        context: Optional[Dict[str, Any]],
    ) -> bool:
        if set(categories).intersection(self.EXPORT_CONTROL_TERMS):
            return True

        blob = str(context or {}).upper()

        return any(term in blob for term in self.EXPORT_CONTROL_TERMS)

    # ------------------------------------------------------------------
    # Compatibility Helpers
    # ------------------------------------------------------------------

    def autonomous_allowed(
        self,
        **kwargs,
    ) -> bool:
        return bool(
            self.evaluate_action(**kwargs).get("allowed")
        )

    def requires_approval(
        self,
        **kwargs,
    ) -> bool:
        return bool(
            self.evaluate_action(**kwargs).get("approval_required")
        )

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _publish_decision(
        self,
        decision: Dict[str, Any],
    ) -> None:
        if self.event_bus is not None:
            try:
                self.event_bus.publish(
                    event_type="POLICY_DECISION_EVALUATED",
                    payload=decision,
                    case_id=(decision.get("context") or {}).get("case_id"),
                    tenant_id=decision.get("tenant_id"),
                    actor="policy_engine",
                    source="policy_engine",
                )
            except Exception:
                pass

        if self.live_updates is not None:
            try:
                self.live_updates.broadcast_tenant_update(
                    tenant_id=decision.get("tenant_id"),
                    event_type="POLICY_DECISION_EVALUATED",
                    payload=decision,
                    actor="policy_engine",
                )
            except Exception:
                pass