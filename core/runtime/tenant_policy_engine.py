"""
core/runtime/tenant_policy_engine.py

Tenant Policy Engine for Veridion Pro / CUI GovCloud App.

Purpose:
- Tenant-specific autonomy control
- Action approval requirements
- Export-control/legal routing
- Risk threshold enforcement
- Simulation/shadow-mode governance
- Runtime-safe policy decisions

Safe defaults:
- Destructive actions require approval
- Export-control requires legal review
- Unknown tenants default to ASSISTED mode
- FULL_AUTONOMY must be explicitly configured
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


MODE_MANUAL = "MANUAL"
MODE_ASSISTED = "ASSISTED"
MODE_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
MODE_FULL_AUTONOMY = "FULL_AUTONOMY"
MODE_LOCKDOWN = "LOCKDOWN"

DECISION_ALLOW = "ALLOW"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISION_BLOCK = "BLOCK"
DECISION_REQUIRE_LEGAL = "REQUIRE_LEGAL"

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

DEFAULT_TENANT_ID = "default"

DESTRUCTIVE_ACTIONS = {
    "DISABLE_USER",
    "ENABLE_USER",
    "REVOKE_TOKEN",
    "REVOKE_SESSIONS",
    "ISOLATE_ENDPOINT",
    "UNISOLATE_ENDPOINT",
    "BLOCK_IP",
    "UNBLOCK_IP",
}

SAFE_ACTIONS = {
    "SEAL_EVIDENCE",
}

MEDIUM_RISK_ACTIONS = {
    "QUARANTINE_EMAIL",
    "RESTORE_EMAIL",
}

EXPORT_CONTROL_CATEGORIES = {
    "ITAR",
    "EAR",
    "EAR99",
    "EXPORT_CONTROL",
    "CONTROLLED_TECHNICAL_INFORMATION",
    "CTI",
    "USML",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


def _json_loads(value: Any, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if default is None:
        default = {}

    if value is None:
        return default

    if isinstance(value, dict):
        return value

    try:
        return json.loads(value)
    except Exception:
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def _get_ledger(storage_or_ledger: Any) -> Any:
    if storage_or_ledger is None:
        return None
    return getattr(storage_or_ledger, "ledger", storage_or_ledger)


def _get_connection(storage_or_ledger: Any) -> sqlite3.Connection:
    ledger = _get_ledger(storage_or_ledger)

    if ledger is not None:
        for attr in ("conn", "_conn", "connection", "_connection"):
            conn = getattr(ledger, attr, None)
            if isinstance(conn, sqlite3.Connection):
                return conn

        for attr in ("db_path", "database_path", "path", "_db_path"):
            db_path = getattr(ledger, attr, None)
            if db_path:
                return sqlite3.connect(db_path, check_same_thread=False)

        connect_fn = getattr(ledger, "_connect", None)
        if callable(connect_fn):
            try:
                return connect_fn()
            except Exception:
                pass

    if isinstance(storage_or_ledger, str):
        return sqlite3.connect(storage_or_ledger, check_same_thread=False)

    return sqlite3.connect("data/ledger.db", check_same_thread=False)


@dataclass
class TenantPolicy:
    tenant_id: str = DEFAULT_TENANT_ID
    autonomy_mode: str = MODE_ASSISTED

    allow_full_autonomy: bool = False
    simulation_mode: bool = True
    shadow_mode: bool = False

    max_autonomous_risk_score: int = 40
    max_supervised_risk_score: int = 75

    require_approval_for_destructive: bool = True
    require_approval_for_high_risk: bool = True
    require_legal_for_export_control: bool = True
    require_dual_approval_for_critical: bool = True

    allowed_actions: List[str] = field(default_factory=list)
    blocked_actions: List[str] = field(default_factory=list)
    auto_approve_actions: List[str] = field(default_factory=lambda: ["SEAL_EVIDENCE"])

    policy_name: str = "Default Assisted Governance Policy"
    updated_by: str = "system"
    updated_at_ms: int = field(default_factory=_now_ms)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    decision: str
    allowed: bool
    requires_approval: bool
    requires_legal: bool
    requires_dual_approval: bool
    blocked: bool

    tenant_id: str
    action: str
    autonomy_mode: str

    reason: str
    risk_score: int = 0
    severity: str = SEVERITY_MEDIUM
    confidence: float = 0.0

    policy_id: Optional[str] = None
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at_ms: int = field(default_factory=_now_ms)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TenantPolicyEngine:
    def __init__(self, storage: Any = None) -> None:
        self.storage = storage
        self.conn = _get_connection(storage)
        self.ensure_schema()

    def ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tenant_policies (
                tenant_id TEXT PRIMARY KEY,
                policy_name TEXT,
                autonomy_mode TEXT NOT NULL,
                allow_full_autonomy INTEGER DEFAULT 0,
                simulation_mode INTEGER DEFAULT 1,
                shadow_mode INTEGER DEFAULT 0,
                max_autonomous_risk_score INTEGER DEFAULT 40,
                max_supervised_risk_score INTEGER DEFAULT 75,
                require_approval_for_destructive INTEGER DEFAULT 1,
                require_approval_for_high_risk INTEGER DEFAULT 1,
                require_legal_for_export_control INTEGER DEFAULT 1,
                require_dual_approval_for_critical INTEGER DEFAULT 1,
                allowed_actions_json TEXT,
                blocked_actions_json TEXT,
                auto_approve_actions_json TEXT,
                metadata_json TEXT,
                updated_by TEXT,
                updated_at_ms INTEGER NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tenant_policy_decisions (
                decision_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                action TEXT NOT NULL,
                decision TEXT NOT NULL,
                allowed INTEGER NOT NULL,
                requires_approval INTEGER NOT NULL,
                requires_legal INTEGER NOT NULL,
                requires_dual_approval INTEGER NOT NULL,
                blocked INTEGER NOT NULL,
                autonomy_mode TEXT,
                risk_score INTEGER,
                severity TEXT,
                confidence REAL,
                reason TEXT,
                policy_id TEXT,
                metadata_json TEXT,
                created_at_ms INTEGER NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tenant_policy_decisions_tenant
            ON tenant_policy_decisions(tenant_id)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tenant_policy_decisions_created
            ON tenant_policy_decisions(created_at_ms)
            """
        )

        self.conn.commit()

    def get_policy(self, tenant_id: str = DEFAULT_TENANT_ID) -> TenantPolicy:
        tenant_id = tenant_id or DEFAULT_TENANT_ID

        row = self.conn.execute(
            """
            SELECT *
            FROM tenant_policies
            WHERE tenant_id=?
            LIMIT 1
            """,
            (tenant_id,),
        ).fetchone()

        if not row and tenant_id != DEFAULT_TENANT_ID:
            row = self.conn.execute(
                """
                SELECT *
                FROM tenant_policies
                WHERE tenant_id=?
                LIMIT 1
                """,
                (DEFAULT_TENANT_ID,),
            ).fetchone()

        if not row:
            return TenantPolicy(tenant_id=tenant_id)

        data = self._row_to_dict("tenant_policies", row)

        return TenantPolicy(
            tenant_id=tenant_id,
            policy_name=data.get("policy_name") or "Tenant Governance Policy",
            autonomy_mode=data.get("autonomy_mode") or MODE_ASSISTED,
            allow_full_autonomy=bool(data.get("allow_full_autonomy")),
            simulation_mode=bool(data.get("simulation_mode")),
            shadow_mode=bool(data.get("shadow_mode")),
            max_autonomous_risk_score=_safe_int(data.get("max_autonomous_risk_score"), 40),
            max_supervised_risk_score=_safe_int(data.get("max_supervised_risk_score"), 75),
            require_approval_for_destructive=bool(data.get("require_approval_for_destructive")),
            require_approval_for_high_risk=bool(data.get("require_approval_for_high_risk")),
            require_legal_for_export_control=bool(data.get("require_legal_for_export_control")),
            require_dual_approval_for_critical=bool(data.get("require_dual_approval_for_critical")),
            allowed_actions=_json_loads(data.get("allowed_actions_json"), {}).get("actions", []),
            blocked_actions=_json_loads(data.get("blocked_actions_json"), {}).get("actions", []),
            auto_approve_actions=_json_loads(data.get("auto_approve_actions_json"), {}).get("actions", ["SEAL_EVIDENCE"]),
            updated_by=data.get("updated_by") or "system",
            updated_at_ms=_safe_int(data.get("updated_at_ms"), _now_ms()),
            metadata=_json_loads(data.get("metadata_json")),
        )

    def save_policy(self, policy: TenantPolicy) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO tenant_policies (
                tenant_id,
                policy_name,
                autonomy_mode,
                allow_full_autonomy,
                simulation_mode,
                shadow_mode,
                max_autonomous_risk_score,
                max_supervised_risk_score,
                require_approval_for_destructive,
                require_approval_for_high_risk,
                require_legal_for_export_control,
                require_dual_approval_for_critical,
                allowed_actions_json,
                blocked_actions_json,
                auto_approve_actions_json,
                metadata_json,
                updated_by,
                updated_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                policy.tenant_id,
                policy.policy_name,
                policy.autonomy_mode,
                int(policy.allow_full_autonomy),
                int(policy.simulation_mode),
                int(policy.shadow_mode),
                policy.max_autonomous_risk_score,
                policy.max_supervised_risk_score,
                int(policy.require_approval_for_destructive),
                int(policy.require_approval_for_high_risk),
                int(policy.require_legal_for_export_control),
                int(policy.require_dual_approval_for_critical),
                _json_dumps({"actions": policy.allowed_actions}),
                _json_dumps({"actions": policy.blocked_actions}),
                _json_dumps({"actions": policy.auto_approve_actions}),
                _json_dumps(policy.metadata),
                policy.updated_by,
                _now_ms(),
            ),
        )
        self.conn.commit()

    def evaluate_action(
        self,
        *,
        tenant_id: str,
        action: str,
        risk_score: int = 0,
        severity: str = SEVERITY_MEDIUM,
        confidence: float = 0.0,
        categories: Optional[List[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "tenant_policy_engine",
    ) -> PolicyDecision:
        tenant_id = tenant_id or DEFAULT_TENANT_ID
        action = _safe_str(action).upper()
        severity = _safe_str(severity, SEVERITY_MEDIUM).upper()
        categories_norm = {str(c).upper() for c in _as_list(categories)}
        payload = payload or {}

        policy = self.get_policy(tenant_id)
        mode = _safe_str(policy.autonomy_mode, MODE_ASSISTED).upper()

        metadata = {
            "actor": actor,
            "categories": sorted(categories_norm),
            "simulation_mode": policy.simulation_mode,
            "shadow_mode": policy.shadow_mode,
            "payload_summary": self._safe_payload_summary(payload),
        }

        if mode == MODE_LOCKDOWN:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_BLOCK,
                    allowed=False,
                    requires_approval=False,
                    requires_legal=False,
                    requires_dual_approval=False,
                    blocked=True,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Tenant is in LOCKDOWN mode.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if action in {a.upper() for a in policy.blocked_actions}:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_BLOCK,
                    allowed=False,
                    requires_approval=False,
                    requires_legal=False,
                    requires_dual_approval=False,
                    blocked=True,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason=f"Action {action} is explicitly blocked by tenant policy.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if self._is_export_control(categories_norm, payload) and policy.require_legal_for_export_control:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_REQUIRE_LEGAL,
                    allowed=False,
                    requires_approval=True,
                    requires_legal=True,
                    requires_dual_approval=True,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Export-control or ITAR category requires legal/governance approval.",
                    risk_score=max(risk_score, 95),
                    severity=SEVERITY_CRITICAL,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if action in SAFE_ACTIONS or action in {a.upper() for a in policy.auto_approve_actions}:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_ALLOW,
                    allowed=True,
                    requires_approval=False,
                    requires_legal=False,
                    requires_dual_approval=False,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Action is safe or tenant auto-approved.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if action in DESTRUCTIVE_ACTIONS and policy.require_approval_for_destructive:
            if mode != MODE_FULL_AUTONOMY or not policy.allow_full_autonomy:
                return self._record_decision(
                    PolicyDecision(
                        decision=DECISION_REQUIRE_APPROVAL,
                        allowed=False,
                        requires_approval=True,
                        requires_legal=False,
                        requires_dual_approval=severity == SEVERITY_CRITICAL,
                        blocked=False,
                        tenant_id=tenant_id,
                        action=action,
                        autonomy_mode=mode,
                        reason="Destructive action requires approval under tenant policy.",
                        risk_score=risk_score,
                        severity=severity,
                        confidence=confidence,
                        policy_id=policy.tenant_id,
                        metadata=metadata,
                    )
                )

        if severity == SEVERITY_CRITICAL and policy.require_dual_approval_for_critical:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_REQUIRE_APPROVAL,
                    allowed=False,
                    requires_approval=True,
                    requires_legal=False,
                    requires_dual_approval=True,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Critical-severity action requires dual approval.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if policy.require_approval_for_high_risk and risk_score > policy.max_supervised_risk_score:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_REQUIRE_APPROVAL,
                    allowed=False,
                    requires_approval=True,
                    requires_legal=False,
                    requires_dual_approval=severity == SEVERITY_CRITICAL,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Risk score exceeds supervised tenant threshold.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if mode in {MODE_MANUAL, MODE_ASSISTED}:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_REQUIRE_APPROVAL,
                    allowed=False,
                    requires_approval=True,
                    requires_legal=False,
                    requires_dual_approval=False,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason=f"{mode} mode requires approval for this action.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if mode == MODE_SUPERVISED_AUTONOMY and risk_score > policy.max_autonomous_risk_score:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_REQUIRE_APPROVAL,
                    allowed=False,
                    requires_approval=True,
                    requires_legal=False,
                    requires_dual_approval=False,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Risk score exceeds autonomous execution threshold.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if action in {a.upper() for a in policy.allowed_actions}:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_ALLOW,
                    allowed=True,
                    requires_approval=False,
                    requires_legal=False,
                    requires_dual_approval=False,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Action is explicitly allowed by tenant policy.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        if mode == MODE_FULL_AUTONOMY and policy.allow_full_autonomy:
            return self._record_decision(
                PolicyDecision(
                    decision=DECISION_ALLOW,
                    allowed=True,
                    requires_approval=False,
                    requires_legal=False,
                    requires_dual_approval=False,
                    blocked=False,
                    tenant_id=tenant_id,
                    action=action,
                    autonomy_mode=mode,
                    reason="Tenant FULL_AUTONOMY policy allows execution.",
                    risk_score=risk_score,
                    severity=severity,
                    confidence=confidence,
                    policy_id=policy.tenant_id,
                    metadata=metadata,
                )
            )

        return self._record_decision(
            PolicyDecision(
                decision=DECISION_REQUIRE_APPROVAL,
                allowed=False,
                requires_approval=True,
                requires_legal=False,
                requires_dual_approval=False,
                blocked=False,
                tenant_id=tenant_id,
                action=action,
                autonomy_mode=mode,
                reason="Default safe policy requires approval.",
                risk_score=risk_score,
                severity=severity,
                confidence=confidence,
                policy_id=policy.tenant_id,
                metadata=metadata,
            )
        )

    def set_autonomy_mode(
        self,
        tenant_id: str,
        mode: str,
        *,
        actor: str = "system",
        reason: str = "",
    ) -> TenantPolicy:
        tenant_id = tenant_id or DEFAULT_TENANT_ID
        mode = _safe_str(mode, MODE_ASSISTED).upper()

        if mode not in {
            MODE_MANUAL,
            MODE_ASSISTED,
            MODE_SUPERVISED_AUTONOMY,
            MODE_FULL_AUTONOMY,
            MODE_LOCKDOWN,
        }:
            raise ValueError(f"Invalid autonomy mode: {mode}")

        policy = self.get_policy(tenant_id)
        policy.autonomy_mode = mode
        policy.updated_by = actor
        policy.updated_at_ms = _now_ms()
        policy.metadata["last_mode_change_reason"] = reason

        if mode == MODE_FULL_AUTONOMY:
            policy.allow_full_autonomy = True

        self.save_policy(policy)
        return policy

    def create_default_policy(
        self,
        tenant_id: str = DEFAULT_TENANT_ID,
        *,
        actor: str = "system",
    ) -> TenantPolicy:
        policy = TenantPolicy(
            tenant_id=tenant_id,
            autonomy_mode=MODE_ASSISTED,
            allow_full_autonomy=False,
            simulation_mode=True,
            shadow_mode=False,
            max_autonomous_risk_score=40,
            max_supervised_risk_score=75,
            require_approval_for_destructive=True,
            require_approval_for_high_risk=True,
            require_legal_for_export_control=True,
            require_dual_approval_for_critical=True,
            auto_approve_actions=["SEAL_EVIDENCE"],
            blocked_actions=[],
            allowed_actions=[],
            updated_by=actor,
            metadata={
                "created_by": actor,
                "profile": "safe_default",
            },
        )
        self.save_policy(policy)
        return policy

    def create_policy_profile(
        self,
        tenant_id: str,
        profile: str,
        *,
        actor: str = "system",
    ) -> TenantPolicy:
        profile = _safe_str(profile, "safe").lower()

        if profile == "strict":
            policy = TenantPolicy(
                tenant_id=tenant_id,
                policy_name="Strict Governance Policy",
                autonomy_mode=MODE_MANUAL,
                allow_full_autonomy=False,
                simulation_mode=True,
                shadow_mode=False,
                max_autonomous_risk_score=20,
                max_supervised_risk_score=50,
                require_approval_for_destructive=True,
                require_approval_for_high_risk=True,
                require_legal_for_export_control=True,
                require_dual_approval_for_critical=True,
                auto_approve_actions=["SEAL_EVIDENCE"],
                updated_by=actor,
                metadata={"profile": profile},
            )
        elif profile == "mssp_aggressive":
            policy = TenantPolicy(
                tenant_id=tenant_id,
                policy_name="MSSP Aggressive Supervised Policy",
                autonomy_mode=MODE_SUPERVISED_AUTONOMY,
                allow_full_autonomy=False,
                simulation_mode=True,
                shadow_mode=False,
                max_autonomous_risk_score=65,
                max_supervised_risk_score=85,
                require_approval_for_destructive=True,
                require_approval_for_high_risk=True,
                require_legal_for_export_control=True,
                require_dual_approval_for_critical=True,
                auto_approve_actions=[
                    "SEAL_EVIDENCE",
                    "QUARANTINE_EMAIL",
                ],
                allowed_actions=[
                    "QUARANTINE_EMAIL",
                    "SEAL_EVIDENCE",
                ],
                updated_by=actor,
                metadata={"profile": profile},
            )
        elif profile == "full_autonomy_lab":
            policy = TenantPolicy(
                tenant_id=tenant_id,
                policy_name="Full Autonomy Lab Policy",
                autonomy_mode=MODE_FULL_AUTONOMY,
                allow_full_autonomy=True,
                simulation_mode=True,
                shadow_mode=True,
                max_autonomous_risk_score=90,
                max_supervised_risk_score=95,
                require_approval_for_destructive=True,
                require_approval_for_high_risk=False,
                require_legal_for_export_control=True,
                require_dual_approval_for_critical=True,
                auto_approve_actions=[
                    "SEAL_EVIDENCE",
                    "QUARANTINE_EMAIL",
                    "REVOKE_SESSIONS",
                ],
                allowed_actions=[
                    "SEAL_EVIDENCE",
                    "QUARANTINE_EMAIL",
                    "REVOKE_SESSIONS",
                ],
                blocked_actions=[
                    "DISABLE_USER",
                    "ISOLATE_ENDPOINT",
                    "BLOCK_IP",
                ],
                updated_by=actor,
                metadata={"profile": profile},
            )
        else:
            policy = self.create_default_policy(tenant_id, actor=actor)
            policy.metadata["profile"] = profile

        self.save_policy(policy)
        return policy

    def list_policies(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT *
            FROM tenant_policies
            ORDER BY tenant_id ASC
            """
        ).fetchall()

        return [
            self._row_to_dict("tenant_policies", row)
            for row in rows
        ]

    def list_decisions(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        if tenant_id:
            rows = self.conn.execute(
                """
                SELECT *
                FROM tenant_policy_decisions
                WHERE tenant_id=?
                ORDER BY created_at_ms DESC
                LIMIT ?
                """,
                (tenant_id, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT *
                FROM tenant_policy_decisions
                ORDER BY created_at_ms DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            self._row_to_dict("tenant_policy_decisions", row)
            for row in rows
        ]

    def _record_decision(self, decision: PolicyDecision) -> PolicyDecision:
        self.conn.execute(
            """
            INSERT INTO tenant_policy_decisions (
                decision_id,
                tenant_id,
                action,
                decision,
                allowed,
                requires_approval,
                requires_legal,
                requires_dual_approval,
                blocked,
                autonomy_mode,
                risk_score,
                severity,
                confidence,
                reason,
                policy_id,
                metadata_json,
                created_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision.decision_id,
                decision.tenant_id,
                decision.action,
                decision.decision,
                int(decision.allowed),
                int(decision.requires_approval),
                int(decision.requires_legal),
                int(decision.requires_dual_approval),
                int(decision.blocked),
                decision.autonomy_mode,
                decision.risk_score,
                decision.severity,
                decision.confidence,
                decision.reason,
                decision.policy_id,
                _json_dumps(decision.metadata),
                decision.created_at_ms,
            ),
        )
        self.conn.commit()
        return decision

    def _is_export_control(self, categories: set[str], payload: Dict[str, Any]) -> bool:
        if categories.intersection(EXPORT_CONTROL_CATEGORIES):
            return True

        text = json.dumps(payload or {}, default=str).lower()

        return any(
            marker in text
            for marker in [
                "itar",
                "ear99",
                "export controlled",
                "export-control",
                "defense article",
                "technical data",
                "usml",
            ]
        )

    def _safe_payload_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {
            "password",
            "token",
            "access_token",
            "refresh_token",
            "secret",
            "client_secret",
            "api_key",
            "private_key",
        }

        clean = {}

        for key, value in (payload or {}).items():
            if key.lower() in sensitive:
                clean[key] = "***REDACTED***"
            elif isinstance(value, (dict, list)):
                clean[key] = "[structured]"
            else:
                clean[key] = value

        return clean

    def _row_to_dict(self, table_name: str, row: Any) -> Dict[str, Any]:
        if row is None:
            return {}

        cols = [
            d[1]
            for d in self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]

        return dict(zip(cols, row))


def get_tenant_policy_engine(storage: Any = None) -> TenantPolicyEngine:
    return TenantPolicyEngine(storage)


def evaluate_tenant_action(
    storage: Any,
    *,
    tenant_id: str,
    action: str,
    risk_score: int = 0,
    severity: str = SEVERITY_MEDIUM,
    confidence: float = 0.0,
    categories: Optional[List[str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    actor: str = "tenant_policy_engine",
) -> PolicyDecision:
    engine = get_tenant_policy_engine(storage)
    return engine.evaluate_action(
        tenant_id=tenant_id,
        action=action,
        risk_score=risk_score,
        severity=severity,
        confidence=confidence,
        categories=categories,
        payload=payload,
        actor=actor,
    )


def bootstrap_default_tenant_policy(
    storage: Any,
    tenant_id: str = DEFAULT_TENANT_ID,
    *,
    profile: str = "safe",
    actor: str = "system",
) -> TenantPolicy:
    engine = get_tenant_policy_engine(storage)
    return engine.create_policy_profile(
        tenant_id=tenant_id,
        profile=profile,
        actor=actor,
    )