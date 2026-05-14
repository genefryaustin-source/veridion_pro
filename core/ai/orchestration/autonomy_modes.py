from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# ============================================================
# AUTONOMY MODES
# ============================================================

MANUAL = "MANUAL"

ASSISTED = "ASSISTED"

SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"

FULL_AUTONOMY = "FULL_AUTONOMY"

LOCKDOWN = "LOCKDOWN"


# ============================================================
# MODE CONFIGURATION
# ============================================================

@dataclass
class AutonomyModeConfig:

    name: str

    auto_execute: bool = False

    require_approval: bool = True

    allow_rollback: bool = True

    allow_high_risk_actions: bool = False

    allow_identity_actions: bool = False

    allow_network_actions: bool = False

    allow_mail_actions: bool = False

    allow_endpoint_actions: bool = False

    allow_evidence_actions: bool = True

    escalation_required_on_failure: bool = True

    description: str = ""


# ============================================================
# MODE DEFINITIONS
# ============================================================

AUTONOMY_MODES: Dict[str, AutonomyModeConfig] = {

    MANUAL: AutonomyModeConfig(

        name=MANUAL,

        auto_execute=False,

        require_approval=True,

        allow_high_risk_actions=False,

        allow_identity_actions=False,

        allow_network_actions=False,

        allow_mail_actions=False,

        allow_endpoint_actions=False,

        allow_evidence_actions=True,

        description=(
            "Human approval required for all operational actions."
        ),
    ),

    ASSISTED: AutonomyModeConfig(

        name=ASSISTED,

        auto_execute=False,

        require_approval=True,

        allow_high_risk_actions=False,

        allow_identity_actions=False,

        allow_network_actions=False,

        allow_mail_actions=True,

        allow_endpoint_actions=True,

        allow_evidence_actions=True,

        description=(
            "AI may recommend actions but humans approve execution."
        ),
    ),

    SUPERVISED_AUTONOMY: AutonomyModeConfig(

        name=SUPERVISED_AUTONOMY,

        auto_execute=True,

        require_approval=False,

        allow_high_risk_actions=False,

        allow_identity_actions=True,

        allow_network_actions=True,

        allow_mail_actions=True,

        allow_endpoint_actions=True,

        allow_evidence_actions=True,

        description=(
            "AI executes low/medium-risk containment with governance oversight."
        ),
    ),

    FULL_AUTONOMY: AutonomyModeConfig(

        name=FULL_AUTONOMY,

        auto_execute=True,

        require_approval=False,

        allow_high_risk_actions=True,

        allow_identity_actions=True,

        allow_network_actions=True,

        allow_mail_actions=True,

        allow_endpoint_actions=True,

        allow_evidence_actions=True,

        description=(
            "AI fully autonomous operational execution enabled."
        ),
    ),

    LOCKDOWN: AutonomyModeConfig(

        name=LOCKDOWN,

        auto_execute=True,

        require_approval=False,

        allow_high_risk_actions=True,

        allow_identity_actions=True,

        allow_network_actions=True,

        allow_mail_actions=True,

        allow_endpoint_actions=True,

        allow_evidence_actions=True,

        escalation_required_on_failure=True,

        description=(
            "Emergency autonomous containment mode."
        ),
    ),
}


# ============================================================
# HELPERS
# ============================================================

def get_autonomy_mode(
    mode: str,
) -> AutonomyModeConfig:

    return AUTONOMY_MODES.get(
        str(mode).upper(),
        AUTONOMY_MODES[MANUAL],
    )


def list_autonomy_modes():

    return list(AUTONOMY_MODES.keys())