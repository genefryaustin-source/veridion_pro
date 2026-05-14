"""
core/policy/agent_policy_engine.py

Real execution governance for autonomous agents.

Controls:
- which agents may act
- under what conditions
- which tenants
- which severity
- which autonomy mode
- approval requirements
- escalation thresholds
- rollback thresholds
- legal requirements
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


MODE_MANUAL = "MANUAL"
MODE_ASSISTED = "ASSISTED"
MODE_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
MODE_FULL_AUTONOMY = "FULL_AUTONOMY"
MODE_LOCKDOWN = "LOCKDOWN"

DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISION_ESCALATE = "ESCALATE"


@dataclass
class AgentPolicyDecision:
    decision: str
    allowed: bool
    requires_approval: bool = False
    requires_escalation: bool = False
    requires_legal: bool = False
    reason: str = ""
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentPolicyRule:
    rule_id: str
    agent_name: str
    action: str
    allowed_modes: List[str]
    min_severity: str = "LOW"
    tenant_id: Optional[str] = None
    requires_approval: bool = False
    requires_legal: bool = False
    destructive: bool = False
    enabled: bool = True


class AgentPolicyEngine:
    def __init__(self, rules: Optional[List[AgentPolicyRule]] = None):
        self.rules = rules or self.default_rules()

    def evaluate(
        self,
        agent_name: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentPolicyDecision:
        context = context or {}

        mode = str(context.get("autonomy_mode") or MODE_MANUAL).upper()
        tenant_id = context.get("tenant_id")
        severity = str(context.get("severity") or "LOW").upper()
        export_control = bool(context.get("export_control") or context.get("category") == "EXPORT_CONTROL")

        matching_rules = [
            r for r in self.rules
            if r.enabled
            and r.agent_name == agent_name
            and r.action == action
            and (r.tenant_id is None or r.tenant_id == tenant_id)
        ]

        if not matching_rules:
            return AgentPolicyDecision(
                decision=DECISION_BLOCK,
                allowed=False,
                reason="no_matching_policy_rule",
                metadata=context,
            )

        rule = matching_rules[0]

        if mode not in rule.allowed_modes:
            return AgentPolicyDecision(
                decision=DECISION_BLOCK,
                allowed=False,
                reason=f"mode_not_allowed:{mode}",
                metadata={"rule": rule.__dict__, "context": context},
            )

        if rule.destructive and mode in {MODE_MANUAL, MODE_ASSISTED}:
            return AgentPolicyDecision(
                decision=DECISION_REQUIRE_APPROVAL,
                allowed=False,
                requires_approval=True,
                reason="destructive_action_requires_approval",
                metadata={"rule": rule.__dict__, "context": context},
            )

        if export_control:
            return AgentPolicyDecision(
                decision=DECISION_ESCALATE,
                allowed=mode in {MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN},
                requires_approval=True,
                requires_escalation=True,
                requires_legal=True,
                reason="export_control_requires_legal_escalation",
                metadata={"rule": rule.__dict__, "context": context},
            )

        if severity == "CRITICAL" and action in {"contain_host", "endpoint_quarantine", "mailbox_isolation"}:
            return AgentPolicyDecision(
                decision=DECISION_ALLOW if mode in {MODE_FULL_AUTONOMY, MODE_LOCKDOWN} else DECISION_REQUIRE_APPROVAL,
                allowed=mode in {MODE_FULL_AUTONOMY, MODE_LOCKDOWN},
                requires_approval=mode not in {MODE_FULL_AUTONOMY, MODE_LOCKDOWN},
                requires_escalation=True,
                reason="critical_containment_policy",
                metadata={"rule": rule.__dict__, "context": context},
            )

        if rule.requires_legal:
            return AgentPolicyDecision(
                decision=DECISION_ESCALATE,
                allowed=False,
                requires_approval=True,
                requires_escalation=True,
                requires_legal=True,
                reason="legal_required_by_rule",
                metadata={"rule": rule.__dict__, "context": context},
            )

        if rule.requires_approval:
            return AgentPolicyDecision(
                decision=DECISION_REQUIRE_APPROVAL,
                allowed=False,
                requires_approval=True,
                reason="approval_required_by_rule",
                metadata={"rule": rule.__dict__, "context": context},
            )

        return AgentPolicyDecision(
            decision=DECISION_ALLOW,
            allowed=True,
            reason="policy_allowed",
            metadata={"rule": rule.__dict__, "context": context},
        )

    def default_rules(self) -> List[AgentPolicyRule]:
        return [
            AgentPolicyRule(
                rule_id="containment_endpoint_quarantine",
                agent_name="containment_agent",
                action="endpoint_quarantine",
                allowed_modes=[MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
                destructive=True,
                requires_approval=True,
            ),
            AgentPolicyRule(
                rule_id="containment_mailbox_isolation",
                agent_name="containment_agent",
                action="mailbox_isolation",
                allowed_modes=[MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
                destructive=True,
                requires_approval=True,
            ),
            AgentPolicyRule(
                rule_id="containment_token_revocation",
                agent_name="containment_agent",
                action="token_revocation",
                allowed_modes=[MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
                destructive=True,
                requires_approval=True,
            ),
            AgentPolicyRule(
                rule_id="verification_all",
                agent_name="verification_agent",
                action="verify_containment",
                allowed_modes=[MODE_ASSISTED, MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
            ),
            AgentPolicyRule(
                rule_id="escalation_legal",
                agent_name="escalation_agent",
                action="legal_routing",
                allowed_modes=[MODE_ASSISTED, MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
                requires_legal=True,
            ),
            AgentPolicyRule(
                rule_id="escalation_export_control",
                agent_name="escalation_agent",
                action="export_control_escalation",
                allowed_modes=[MODE_ASSISTED, MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
                requires_legal=True,
            ),
            AgentPolicyRule(
                rule_id="optimizer_recommend",
                agent_name="optimizer_agent",
                action="optimize_path",
                allowed_modes=[MODE_ASSISTED, MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
            ),
            AgentPolicyRule(
                rule_id="evidence_enrich",
                agent_name="evidence_agent",
                action="enrich_evidence",
                allowed_modes=[MODE_ASSISTED, MODE_SUPERVISED_AUTONOMY, MODE_FULL_AUTONOMY, MODE_LOCKDOWN],
            ),
        ]