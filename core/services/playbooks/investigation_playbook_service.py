from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_upper(value: Any) -> str:
    return str(value or "").upper().strip()


class InvestigationPlaybookService:
    """
    SOAR-lite operational orchestration layer.

    Handles:
    - playbook matching
    - workflow generation
    - operational stages
    - approval-aware actions
    - analyst guidance
    - escalation orchestration

    Future integrations:
    - SIEM
    - EDR
    - ServiceNow
    - Slack / Teams
    - Endpoint containment
    - Account disablement
    """

    # ------------------------------------------------------------------
    # Playbook Registry
    # ------------------------------------------------------------------

    PLAYBOOKS = {

        # ==============================================================
        # EXPORT CONTROL
        # ==============================================================

        "EXPORT_CONTROL": {

            "name": "Export Control Investigation",

            "description": (
                "Investigation workflow for ITAR/EAR/"
                "controlled technical data exposure."
            ),

            "triggers": [
                "ITAR",
                "EAR",
                "EAR99",
                "EXPORT_CONTROL",
                "CTI",
            ],

            "severity": "CRITICAL",

            "stages": [
                "TRIAGE",
                "LEGAL_REVIEW",
                "EVIDENCE_PRESERVATION",
                "EXPORT_REVIEW",
                "CONTAINMENT",
                "FORENSICS",
                "CLOSURE",
            ],

            "actions": [
                {
                    "action": "Escalate to Legal",
                    "priority": "CRITICAL",
                    "requires_approval": True,
                    "approval_type": "LEGAL_REVIEW",
                },
                {
                    "action": "Request Export Review",
                    "priority": "CRITICAL",
                    "requires_approval": True,
                    "approval_type": "EXPORT_CONTROL_REVIEW",
                },
                {
                    "action": "Preserve Evidence",
                    "priority": "CRITICAL",
                },
                {
                    "action": "Restrict Case Access",
                    "priority": "HIGH",
                },
            ],
        },

        # ==============================================================
        # INSIDER THREAT
        # ==============================================================

        "INSIDER_THREAT": {

            "name": "Insider Threat Investigation",

            "description": (
                "Workflow for insider-risk indicators, "
                "credential misuse, mass exports, and exfiltration."
            ),

            "triggers": [
                "USB",
                "PERSONAL_EMAIL",
                "MASS_DOWNLOAD",
                "TOKEN",
                "PASSWORD",
                "API_KEY",
            ],

            "severity": "HIGH",

            "stages": [
                "TRIAGE",
                "CONTAINMENT",
                "ACCESS_REVIEW",
                "FORENSICS",
                "HR_COORDINATION",
                "LEGAL_REVIEW",
                "CLOSURE",
            ],

            "actions": [
                {
                    "action": "Request Endpoint Scan",
                    "priority": "HIGH",
                },
                {
                    "action": "Contain User",
                    "priority": "HIGH",
                    "requires_approval": True,
                    "approval_type": "CONTAINMENT_APPROVAL",
                },
                {
                    "action": "Initiate Access Review",
                    "priority": "HIGH",
                },
                {
                    "action": "Assign Tier-3 Analyst",
                    "priority": "HIGH",
                },
            ],
        },

        # ==============================================================
        # CAMPAIGN INVESTIGATION
        # ==============================================================

        "CAMPAIGN_INVESTIGATION": {

            "name": "Campaign Investigation",

            "description": (
                "Cross-case coordinated activity investigation."
            ),

            "triggers": [
                "CAMPAIGN",
                "LINKED_CASES",
                "SHARED_HASHES",
                "REPEATED_ENTITIES",
            ],

            "severity": "HIGH",

            "stages": [
                "TRIAGE",
                "GRAPH_EXPANSION",
                "CORRELATION",
                "CONTAINMENT",
                "FORENSICS",
                "CLOSURE",
            ],

            "actions": [
                {
                    "action": "Expand Graph Relationships",
                    "priority": "HIGH",
                },
                {
                    "action": "Open Campaign Investigation",
                    "priority": "HIGH",
                },
                {
                    "action": "Cluster Related Evidence",
                    "priority": "HIGH",
                },
                {
                    "action": "Escalate Coordinated Activity",
                    "priority": "HIGH",
                },
            ],
        },

        # ==============================================================
        # CREDENTIAL COMPROMISE
        # ==============================================================

        "CREDENTIAL_COMPROMISE": {

            "name": "Credential Compromise",

            "description": (
                "Credential exposure / compromise response workflow."
            ),

            "triggers": [
                "PASSWORD",
                "API_KEY",
                "TOKEN",
                "SECRET_KEY",
                "CREDENTIAL",
            ],

            "severity": "HIGH",

            "stages": [
                "TRIAGE",
                "CONTAINMENT",
                "ACCESS_REVIEW",
                "ROTATION",
                "FORENSICS",
                "RECOVERY",
                "CLOSURE",
            ],

            "actions": [
                {
                    "action": "Revoke Credentials",
                    "priority": "CRITICAL",
                },
                {
                    "action": "Initiate Access Audit",
                    "priority": "HIGH",
                },
                {
                    "action": "Contain User",
                    "priority": "HIGH",
                    "requires_approval": True,
                    "approval_type": "CONTAINMENT_APPROVAL",
                },
            ],
        },
    }

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        ledger: Any = None,
        escalation_service: Any = None,
        approval_service: Any = None,
    ):
        self.ledger = ledger
        self.escalation_service = escalation_service
        self.approval_service = approval_service

    # ------------------------------------------------------------------
    # Main APIs
    # ------------------------------------------------------------------

    def find_playbook_for_case(
        self,
        *,
        case: Dict[str, Any],
        entities: Optional[List[str]] = None,
        indicators: Optional[List[str]] = None,
        campaign: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:

        entities = entities or []
        indicators = indicators or []
        campaign = campaign or {}

        combined = set([
            _safe_upper(x)
            for x in entities + indicators
        ])

        if campaign.get("campaign_id"):
            combined.add("CAMPAIGN")

        # --------------------------------------------------------------
        # Export Control
        # --------------------------------------------------------------

        if any(
            x in combined
            for x in [
                "ITAR",
                "EAR",
                "EAR99",
                "EXPORT_CONTROL",
                "CTI",
            ]
        ):
            return self._build_playbook(
                "EXPORT_CONTROL"
            )

        # --------------------------------------------------------------
        # Credential Compromise
        # --------------------------------------------------------------

        if any(
            x in combined
            for x in [
                "PASSWORD",
                "TOKEN",
                "API_KEY",
                "SECRET_KEY",
            ]
        ):
            return self._build_playbook(
                "CREDENTIAL_COMPROMISE"
            )

        # --------------------------------------------------------------
        # Insider Threat
        # --------------------------------------------------------------

        if any(
            x in combined
            for x in [
                "USB",
                "PERSONAL_EMAIL",
                "MASS_DOWNLOAD",
            ]
        ):
            return self._build_playbook(
                "INSIDER_THREAT"
            )

        # --------------------------------------------------------------
        # Campaign
        # --------------------------------------------------------------

        if "CAMPAIGN" in combined:
            return self._build_playbook(
                "CAMPAIGN_INVESTIGATION"
            )

        return None

    def find_playbook_for_action(
        self,
        *,
        action: str,
        case: Optional[Dict[str, Any]] = None,
        entities: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:

        action = _safe_upper(action)

        for key, pb in self.PLAYBOOKS.items():

            for pb_action in pb.get("actions", []):

                if _safe_upper(
                    pb_action.get("action")
                ) == action:

                    return self._build_playbook(key)

        return None

    def generate_playbook_actions(
        self,
        *,
        playbook_name: str,
    ) -> List[Dict[str, Any]]:

        playbook = self.PLAYBOOKS.get(
            playbook_name
        )

        if not playbook:
            return []

        actions = []

        for action in playbook.get("actions", []):

            actions.append({
                **action,
                "generated_at_ms": _now_ms(),
                "playbook": playbook_name,
            })

        return actions

    def generate_playbook_steps(
        self,
        *,
        playbook_name: str,
    ) -> List[Dict[str, Any]]:

        playbook = self.PLAYBOOKS.get(
            playbook_name
        )

        if not playbook:
            return []

        steps = []

        for idx, stage in enumerate(
            playbook.get("stages", [])
        ):

            steps.append({
                "step": idx + 1,
                "stage": stage,
                "title": self._humanize_stage(stage),
                "instructions": self._stage_instructions(stage),
                "required_role": self._stage_role(stage),
            })

        return steps

    # ------------------------------------------------------------------
    # Action Execution
    # ------------------------------------------------------------------

    def execute_playbook_action(
        self,
        *,
        action: Dict[str, Any],
        case_id: Any,
        actor: str = "system",
    ) -> Dict[str, Any]:

        action_name = action.get("action")

        requires_approval = bool(
            action.get("requires_approval")
        )

        approval_type = action.get(
            "approval_type"
        )

        result = {
            "case_id": case_id,
            "action": action_name,
            "executed": False,
            "approval_requested": False,
            "timestamp_ms": _now_ms(),
        }

        # --------------------------------------------------------------
        # Approval
        # --------------------------------------------------------------

        if requires_approval and self.approval_service:

            try:

                if hasattr(
                    self.approval_service,
                    "request_approval",
                ):

                    approval = (
                        self.approval_service
                        .request_approval(
                            case_id=case_id,
                            approval_type=approval_type,
                            requested_by=actor,
                            details=action,
                        )
                    )

                    result["approval_requested"] = True
                    result["approval"] = approval

            except Exception as exc:
                result["approval_error"] = str(exc)

        # --------------------------------------------------------------
        # Escalation
        # --------------------------------------------------------------

        if (
            action_name == "Escalate to Legal"
            and self.escalation_service
        ):

            try:

                if hasattr(
                    self.escalation_service,
                    "auto_escalate_case",
                ):

                    escalation = (
                        self.escalation_service
                        .auto_escalate_case(
                            case_id=case_id,
                            reason="Playbook escalation",
                            actor=actor,
                        )
                    )

                    result["escalation"] = escalation

            except Exception as exc:
                result["escalation_error"] = str(exc)

        result["executed"] = True

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_playbook(
        self,
        playbook_name: str,
    ) -> Dict[str, Any]:

        pb = self.PLAYBOOKS.get(
            playbook_name,
            {}
        )

        return {
            "playbook_name": playbook_name,
            "name": pb.get("name"),
            "description": pb.get("description"),
            "severity": pb.get("severity"),
            "triggers": pb.get("triggers", []),
            "stages": pb.get("stages", []),
            "actions": pb.get("actions", []),
            "generated_at_ms": _now_ms(),
        }

    def _humanize_stage(
        self,
        stage: str,
    ) -> str:

        return (
            stage
            .replace("_", " ")
            .title()
        )

    def _stage_role(
        self,
        stage: str,
    ) -> str:

        stage = _safe_upper(stage)

        mapping = {

            "TRIAGE": "Analyst",

            "CONTAINMENT": "Senior Analyst",

            "LEGAL_REVIEW": "Legal",

            "EXPORT_REVIEW": "Export Control Officer",

            "FORENSICS": "Forensics Analyst",

            "ACCESS_REVIEW": "IAM Administrator",

            "GRAPH_EXPANSION": "Intelligence Analyst",

            "CORRELATION": "Intelligence Analyst",

            "RECOVERY": "Incident Response",

            "CLOSURE": "Manager",
        }

        return mapping.get(
            stage,
            "Analyst",
        )

    def _stage_instructions(
        self,
        stage: str,
    ) -> str:

        stage = _safe_upper(stage)

        instructions = {

            "TRIAGE": (
                "Validate indicators and determine "
                "initial severity."
            ),

            "LEGAL_REVIEW": (
                "Coordinate with legal/export "
                "control teams before disclosure."
            ),

            "EXPORT_REVIEW": (
                "Assess export classification and "
                "regulatory implications."
            ),

            "EVIDENCE_PRESERVATION": (
                "Preserve evidence and maintain "
                "chain of custody."
            ),

            "CONTAINMENT": (
                "Reduce operational risk and "
                "prevent further exposure."
            ),

            "FORENSICS": (
                "Perform detailed forensic "
                "analysis and timeline reconstruction."
            ),

            "GRAPH_EXPANSION": (
                "Expand graph pivots and identify "
                "linked entities/cases."
            ),

            "CORRELATION": (
                "Correlate activity across "
                "related investigations."
            ),

            "ACCESS_REVIEW": (
                "Audit permissions, credentials, "
                "and privileged access."
            ),

            "ROTATION": (
                "Rotate exposed credentials and "
                "invalidate active sessions."
            ),

            "RECOVERY": (
                "Restore systems and verify "
                "environment integrity."
            ),

            "CLOSURE": (
                "Finalize documentation and "
                "obtain closure approvals."
            ),
        }

        return instructions.get(
            stage,
            "Perform operational investigation tasks."
        )