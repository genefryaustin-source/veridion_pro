"""
core/runtime/safety_guardrails.py

Hard Safety Guardrails for Veridion Pro / CUI GovCloud App.

Purpose:
- Global autonomy kill switch
- Tenant-level autonomy freeze
- Execution quotas
- Action throttling
- Recursive rollback prevention
- Containment storm prevention
- Emergency freeze mode
- Hard-stop enforcement before real connector execution
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


DECISION_ALLOW = "ALLOW"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISION_REQUIRE_EXECUTIVE_APPROVAL = "REQUIRE_EXECUTIVE_APPROVAL"
DECISION_BLOCK = "BLOCK"

EVENT_SAFETY_CHECK_COMPLETED = "SAFETY_CHECK_COMPLETED"
EVENT_SAFETY_LOCK_TRIGGERED = "SAFETY_LOCK_TRIGGERED"
EVENT_AUTONOMY_DISABLED = "AUTONOMY_DISABLED"
EVENT_EXECUTION_QUOTA_EXCEEDED = "EXECUTION_QUOTA_EXCEEDED"
EVENT_RECURSIVE_ROLLBACK_BLOCKED = "RECURSIVE_ROLLBACK_BLOCKED"
EVENT_CONTAINMENT_STORM_DETECTED = "CONTAINMENT_STORM_DETECTED"
EVENT_ACTION_THROTTLED = "ACTION_THROTTLED"
EVENT_EMERGENCY_FREEZE_ENABLED = "EMERGENCY_FREEZE_ENABLED"
EVENT_EMERGENCY_FREEZE_DISABLED = "EMERGENCY_FREEZE_DISABLED"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

DEFAULT_TENANT = "default"

DESTRUCTIVE_ACTIONS = {
    "DISABLE_USER",
    "REVOKE_SESSIONS",
    "DELETE_EMAIL",
    "PURGE_EMAIL",
    "ISOLATE_ENDPOINT",
    "DEVICE_WIPE",
    "BLOCK_IP",
}

CONTAINMENT_ACTIONS = {
    "DISABLE_USER",
    "REVOKE_SESSIONS",
    "QUARANTINE_EMAIL",
    "DELETE_EMAIL",
    "PURGE_EMAIL",
    "ISOLATE_ENDPOINT",
    "BLOCK_IP",
    "DEVICE_WIPE",
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
    try:
        if value is None:
            return default
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


def _get_ledger(storage_or_ledger: Any) -> Any:
    if storage_or_ledger is None:
        return None
    return getattr(storage_or_ledger, "ledger", storage_or_ledger)


@dataclass
class SafetyGuardrailPolicy:
    tenant_id: str = DEFAULT_TENANT
    global_autonomy_enabled: bool = True
    tenant_autonomy_enabled: bool = True
    emergency_freeze_enabled: bool = False

    max_actions_per_hour: int = 50
    max_actions_per_day: int = 250
    max_destructive_actions_per_hour: int = 5
    max_rollback_depth: int = 2
    max_chain_depth: int = 5
    max_targets_per_action: int = 10

    cooldown_seconds_by_action: Dict[str, int] = field(
        default_factory=lambda: {
            "DISABLE_USER": 60,
            "REVOKE_SESSIONS": 30,
            "QUARANTINE_EMAIL": 15,
            "DELETE_EMAIL": 60,
            "ISOLATE_ENDPOINT": 90,
            "DEVICE_WIPE": 300,
        }
    )

    containment_storm_window_ms: int = 10 * 60 * 1000
    containment_storm_threshold: int = 25

    updated_by: str = "system"
    updated_at_ms: int = field(default_factory=_now_ms)


@dataclass
class SafetyDecision:
    decision_id: str
    tenant_id: str
    action: str
    decision: str
    allowed: bool
    blocked: bool
    requires_approval: bool
    requires_executive_approval: bool
    reason: str
    risk_level: str = RISK_LOW
    findings: List[Dict[str, Any]] = field(default_factory=list)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SafetyGuardrails:
    def __init__(self, storage: Any = None, *, event_bus: Any = None) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.db_path = self._resolve_db_path()
        self.ensure_schema()

    def _resolve_db_path(self) -> str:
        ledger = self.ledger

        if ledger is not None:
            for attr in ("db_path", "database_path", "path", "_db_path"):
                path = getattr(ledger, attr, None)
                if path:
                    return path

        if isinstance(self.storage, str):
            return self.storage

        return "data/ledger.db"

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
        )

        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        except Exception:
            pass

        return conn

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS safety_guardrail_policies (
                    tenant_id TEXT PRIMARY KEY,
                    global_autonomy_enabled INTEGER DEFAULT 1,
                    tenant_autonomy_enabled INTEGER DEFAULT 1,
                    emergency_freeze_enabled INTEGER DEFAULT 0,
                    max_actions_per_hour INTEGER DEFAULT 50,
                    max_actions_per_day INTEGER DEFAULT 250,
                    max_destructive_actions_per_hour INTEGER DEFAULT 5,
                    max_rollback_depth INTEGER DEFAULT 2,
                    max_chain_depth INTEGER DEFAULT 5,
                    max_targets_per_action INTEGER DEFAULT 10,
                    cooldown_seconds_by_action_json TEXT,
                    containment_storm_window_ms INTEGER DEFAULT 600000,
                    containment_storm_threshold INTEGER DEFAULT 25,
                    updated_by TEXT,
                    updated_at_ms INTEGER NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS safety_guardrail_decisions (
                    decision_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    allowed INTEGER NOT NULL,
                    blocked INTEGER NOT NULL,
                    requires_approval INTEGER NOT NULL,
                    requires_executive_approval INTEGER NOT NULL,
                    reason TEXT,
                    risk_level TEXT,
                    findings_json TEXT,
                    payload_json TEXT,
                    created_at_ms INTEGER NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS safety_execution_events (
                    event_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor TEXT,
                    execution_id TEXT,
                    case_id TEXT,
                    connector_id TEXT,
                    destructive INTEGER DEFAULT 0,
                    rollback_depth INTEGER DEFAULT 0,
                    chain_depth INTEGER DEFAULT 0,
                    target_count INTEGER DEFAULT 1,
                    created_at_ms INTEGER NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_safety_events_tenant_action_time
                ON safety_execution_events(tenant_id, action, created_at_ms)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_safety_decisions_tenant_time
                ON safety_guardrail_decisions(tenant_id, created_at_ms)
                """
            )

            conn.commit()

    def get_policy(self, tenant_id: str = DEFAULT_TENANT) -> SafetyGuardrailPolicy:
        tenant_id = tenant_id or DEFAULT_TENANT

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM safety_guardrail_policies
                WHERE tenant_id=?
                LIMIT 1
                """,
                (tenant_id,),
            ).fetchone()

            if not row and tenant_id != DEFAULT_TENANT:
                row = conn.execute(
                    """
                    SELECT *
                    FROM safety_guardrail_policies
                    WHERE tenant_id=?
                    LIMIT 1
                    """,
                    (DEFAULT_TENANT,),
                ).fetchone()

            if not row:
                return SafetyGuardrailPolicy(tenant_id=tenant_id)

            data = self._row_to_dict(conn, "safety_guardrail_policies", row)

        return SafetyGuardrailPolicy(
            tenant_id=tenant_id,
            global_autonomy_enabled=bool(data.get("global_autonomy_enabled")),
            tenant_autonomy_enabled=bool(data.get("tenant_autonomy_enabled")),
            emergency_freeze_enabled=bool(data.get("emergency_freeze_enabled")),
            max_actions_per_hour=_safe_int(data.get("max_actions_per_hour"), 50),
            max_actions_per_day=_safe_int(data.get("max_actions_per_day"), 250),
            max_destructive_actions_per_hour=_safe_int(
                data.get("max_destructive_actions_per_hour"),
                5,
            ),
            max_rollback_depth=_safe_int(data.get("max_rollback_depth"), 2),
            max_chain_depth=_safe_int(data.get("max_chain_depth"), 5),
            max_targets_per_action=_safe_int(data.get("max_targets_per_action"), 10),
            cooldown_seconds_by_action=_json_loads(
                data.get("cooldown_seconds_by_action_json"),
                {},
            )
            or SafetyGuardrailPolicy().cooldown_seconds_by_action,
            containment_storm_window_ms=_safe_int(
                data.get("containment_storm_window_ms"),
                600000,
            ),
            containment_storm_threshold=_safe_int(
                data.get("containment_storm_threshold"),
                25,
            ),
            updated_by=data.get("updated_by") or "system",
            updated_at_ms=_safe_int(data.get("updated_at_ms"), _now_ms()),
        )

    def save_policy(self, policy: SafetyGuardrailPolicy) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO safety_guardrail_policies (
                    tenant_id,
                    global_autonomy_enabled,
                    tenant_autonomy_enabled,
                    emergency_freeze_enabled,
                    max_actions_per_hour,
                    max_actions_per_day,
                    max_destructive_actions_per_hour,
                    max_rollback_depth,
                    max_chain_depth,
                    max_targets_per_action,
                    cooldown_seconds_by_action_json,
                    containment_storm_window_ms,
                    containment_storm_threshold,
                    updated_by,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    policy.tenant_id,
                    int(policy.global_autonomy_enabled),
                    int(policy.tenant_autonomy_enabled),
                    int(policy.emergency_freeze_enabled),
                    policy.max_actions_per_hour,
                    policy.max_actions_per_day,
                    policy.max_destructive_actions_per_hour,
                    policy.max_rollback_depth,
                    policy.max_chain_depth,
                    policy.max_targets_per_action,
                    _json_dumps(policy.cooldown_seconds_by_action),
                    policy.containment_storm_window_ms,
                    policy.containment_storm_threshold,
                    policy.updated_by,
                    _now_ms(),
                ),
            )
            conn.commit()

    def check_action(
        self,
        *,
        tenant_id: str,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "safety_guardrails",
        execution_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        connector_id: Optional[str] = None,
        autonomous: bool = True,
    ) -> SafetyDecision:
        tenant_id = tenant_id or DEFAULT_TENANT
        action = _safe_str(action).upper()
        payload = payload or {}
        policy = self.get_policy(tenant_id)

        findings: List[Dict[str, Any]] = []

        destructive = action in DESTRUCTIVE_ACTIONS

        rollback_depth = max(
            _safe_int(payload.get("rollback_depth"), 0),
            _safe_int(
                payload.get("chain", {}).get("rollback_depth")
                if isinstance(payload.get("chain"), dict)
                else 0,
                0,
            ),
        )

        chain_depth = max(
            _safe_int(payload.get("chain_depth"), 0),
            _safe_int(
                payload.get("chain", {}).get("depth")
                if isinstance(payload.get("chain"), dict)
                else 0,
                0,
            ),
        )

        target_count = self._target_count(payload)

        if autonomous and not policy.global_autonomy_enabled:
            return self._block(
                tenant_id,
                action,
                "Global autonomy is disabled.",
                findings,
                payload,
                event_type=EVENT_AUTONOMY_DISABLED,
                risk_level=RISK_CRITICAL,
            )

        if autonomous and not policy.tenant_autonomy_enabled:
            return self._block(
                tenant_id,
                action,
                "Tenant autonomy is disabled.",
                findings,
                payload,
                event_type=EVENT_AUTONOMY_DISABLED,
                risk_level=RISK_CRITICAL,
            )

        if autonomous and policy.emergency_freeze_enabled:
            return self._block(
                tenant_id,
                action,
                "Emergency freeze mode is active.",
                findings,
                payload,
                event_type=EVENT_SAFETY_LOCK_TRIGGERED,
                risk_level=RISK_CRITICAL,
            )

        if rollback_depth > policy.max_rollback_depth:
            findings.append(
                {
                    "type": "ROLLBACK_DEPTH_EXCEEDED",
                    "rollback_depth": rollback_depth,
                    "max_rollback_depth": policy.max_rollback_depth,
                }
            )
            return self._block(
                tenant_id,
                action,
                "Recursive rollback depth exceeded.",
                findings,
                payload,
                event_type=EVENT_RECURSIVE_ROLLBACK_BLOCKED,
                risk_level=RISK_CRITICAL,
            )

        if chain_depth > policy.max_chain_depth:
            findings.append(
                {
                    "type": "CHAIN_DEPTH_EXCEEDED",
                    "chain_depth": chain_depth,
                    "max_chain_depth": policy.max_chain_depth,
                }
            )
            return self._block(
                tenant_id,
                action,
                "Execution chain depth exceeded.",
                findings,
                payload,
                event_type=EVENT_SAFETY_LOCK_TRIGGERED,
                risk_level=RISK_CRITICAL,
            )

        if target_count > policy.max_targets_per_action:
            findings.append(
                {
                    "type": "TARGET_COUNT_EXCEEDED",
                    "target_count": target_count,
                    "max_targets_per_action": policy.max_targets_per_action,
                }
            )
            return self._require_executive(
                tenant_id,
                action,
                "Target count exceeds safety guardrail limit.",
                findings,
                payload,
            )

        hourly_count = self._count_events(
            tenant_id=tenant_id,
            since_ms=_now_ms() - 60 * 60 * 1000,
        )

        if hourly_count >= policy.max_actions_per_hour:
            findings.append(
                {
                    "type": "HOURLY_QUOTA_EXCEEDED",
                    "hourly_count": hourly_count,
                    "max_actions_per_hour": policy.max_actions_per_hour,
                }
            )
            return self._block(
                tenant_id,
                action,
                "Hourly execution quota exceeded.",
                findings,
                payload,
                event_type=EVENT_EXECUTION_QUOTA_EXCEEDED,
                risk_level=RISK_HIGH,
            )

        daily_count = self._count_events(
            tenant_id=tenant_id,
            since_ms=_now_ms() - 24 * 60 * 60 * 1000,
        )

        if daily_count >= policy.max_actions_per_day:
            findings.append(
                {
                    "type": "DAILY_QUOTA_EXCEEDED",
                    "daily_count": daily_count,
                    "max_actions_per_day": policy.max_actions_per_day,
                }
            )
            return self._block(
                tenant_id,
                action,
                "Daily execution quota exceeded.",
                findings,
                payload,
                event_type=EVENT_EXECUTION_QUOTA_EXCEEDED,
                risk_level=RISK_CRITICAL,
            )

        destructive_hourly = self._count_events(
            tenant_id=tenant_id,
            since_ms=_now_ms() - 60 * 60 * 1000,
            destructive_only=True,
        )

        if destructive and destructive_hourly >= policy.max_destructive_actions_per_hour:
            findings.append(
                {
                    "type": "DESTRUCTIVE_QUOTA_EXCEEDED",
                    "destructive_hourly": destructive_hourly,
                    "max_destructive_actions_per_hour": policy.max_destructive_actions_per_hour,
                }
            )
            return self._block(
                tenant_id,
                action,
                "Destructive action hourly quota exceeded.",
                findings,
                payload,
                event_type=EVENT_EXECUTION_QUOTA_EXCEEDED,
                risk_level=RISK_CRITICAL,
            )

        cooldown = _safe_int(policy.cooldown_seconds_by_action.get(action), 0)

        if cooldown > 0:
            last_action_ms = self._last_action_ms(tenant_id, action)

            if last_action_ms and (_now_ms() - last_action_ms) < cooldown * 1000:
                findings.append(
                    {
                        "type": "ACTION_COOLDOWN_ACTIVE",
                        "cooldown_seconds": cooldown,
                        "last_action_ms": last_action_ms,
                    }
                )
                return self._block(
                    tenant_id,
                    action,
                    "Action throttled by cooldown window.",
                    findings,
                    payload,
                    event_type=EVENT_ACTION_THROTTLED,
                    risk_level=RISK_MEDIUM,
                )

        if action in CONTAINMENT_ACTIONS:
            containment_count = self._count_events(
                tenant_id=tenant_id,
                since_ms=_now_ms() - policy.containment_storm_window_ms,
                actions=CONTAINMENT_ACTIONS,
            )

            if containment_count >= policy.containment_storm_threshold:
                findings.append(
                    {
                        "type": "CONTAINMENT_STORM_DETECTED",
                        "containment_count": containment_count,
                        "threshold": policy.containment_storm_threshold,
                        "window_ms": policy.containment_storm_window_ms,
                    }
                )
                return self._require_executive(
                    tenant_id,
                    action,
                    "Containment storm threshold exceeded.",
                    findings,
                    payload,
                    event_type=EVENT_CONTAINMENT_STORM_DETECTED,
                )

        decision = SafetyDecision(
            decision_id=f"SAFE-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            action=action,
            decision=DECISION_ALLOW,
            allowed=True,
            blocked=False,
            requires_approval=False,
            requires_executive_approval=False,
            reason="Safety guardrails allow execution.",
            risk_level=RISK_LOW,
            findings=findings,
        )

        self._persist_decision(decision, payload)

        self.record_execution_event(
            tenant_id=tenant_id,
            action=action,
            actor=actor,
            execution_id=execution_id,
            case_id=case_id,
            connector_id=connector_id,
            destructive=destructive,
            rollback_depth=rollback_depth,
            chain_depth=chain_depth,
            target_count=target_count,
        )

        self._emit(
            EVENT_SAFETY_CHECK_COMPLETED,
            tenant_id=tenant_id,
            severity=RISK_LOW,
            payload=decision.to_dict(),
        )

        return decision

    def record_execution_event(
        self,
        *,
        tenant_id: str,
        action: str,
        actor: str,
        execution_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        connector_id: Optional[str] = None,
        destructive: bool = False,
        rollback_depth: int = 0,
        chain_depth: int = 0,
        target_count: int = 1,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO safety_execution_events (
                    event_id,
                    tenant_id,
                    action,
                    actor,
                    execution_id,
                    case_id,
                    connector_id,
                    destructive,
                    rollback_depth,
                    chain_depth,
                    target_count,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"SEV-{uuid.uuid4().hex[:12].upper()}",
                    tenant_id or DEFAULT_TENANT,
                    _safe_str(action).upper(),
                    actor,
                    execution_id,
                    str(case_id) if case_id is not None else None,
                    connector_id,
                    int(destructive),
                    int(rollback_depth),
                    int(chain_depth),
                    int(target_count),
                    _now_ms(),
                ),
            )
            conn.commit()

    def enable_emergency_freeze(
        self,
        tenant_id: str = DEFAULT_TENANT,
        *,
        actor: str = "system",
        reason: str = "",
    ) -> SafetyGuardrailPolicy:
        policy = self.get_policy(tenant_id)
        policy.emergency_freeze_enabled = True
        policy.updated_by = actor
        self.save_policy(policy)

        self._emit(
            EVENT_EMERGENCY_FREEZE_ENABLED,
            tenant_id=tenant_id,
            severity=RISK_CRITICAL,
            payload={"tenant_id": tenant_id, "actor": actor, "reason": reason},
        )

        return policy

    def disable_emergency_freeze(
        self,
        tenant_id: str = DEFAULT_TENANT,
        *,
        actor: str = "system",
        reason: str = "",
    ) -> SafetyGuardrailPolicy:
        policy = self.get_policy(tenant_id)
        policy.emergency_freeze_enabled = False
        policy.updated_by = actor
        self.save_policy(policy)

        self._emit(
            EVENT_EMERGENCY_FREEZE_DISABLED,
            tenant_id=tenant_id,
            severity=RISK_MEDIUM,
            payload={"tenant_id": tenant_id, "actor": actor, "reason": reason},
        )

        return policy

    def disable_tenant_autonomy(
        self,
        tenant_id: str,
        *,
        actor: str = "system",
        reason: str = "",
    ) -> SafetyGuardrailPolicy:
        policy = self.get_policy(tenant_id)
        policy.tenant_autonomy_enabled = False
        policy.updated_by = actor
        self.save_policy(policy)

        self._emit(
            EVENT_AUTONOMY_DISABLED,
            tenant_id=tenant_id,
            severity=RISK_CRITICAL,
            payload={"tenant_id": tenant_id, "actor": actor, "reason": reason},
        )

        return policy

    def _block(
        self,
        tenant_id: str,
        action: str,
        reason: str,
        findings: List[Dict[str, Any]],
        payload: Dict[str, Any],
        *,
        event_type: str,
        risk_level: str,
    ) -> SafetyDecision:
        decision = SafetyDecision(
            decision_id=f"SAFE-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            action=action,
            decision=DECISION_BLOCK,
            allowed=False,
            blocked=True,
            requires_approval=False,
            requires_executive_approval=False,
            reason=reason,
            risk_level=risk_level,
            findings=findings,
        )

        self._persist_decision(decision, payload)

        self._emit(
            event_type,
            tenant_id=tenant_id,
            severity=risk_level,
            payload=decision.to_dict(),
        )

        return decision

    def _require_executive(
        self,
        tenant_id: str,
        action: str,
        reason: str,
        findings: List[Dict[str, Any]],
        payload: Dict[str, Any],
        *,
        event_type: str = EVENT_SAFETY_LOCK_TRIGGERED,
    ) -> SafetyDecision:
        decision = SafetyDecision(
            decision_id=f"SAFE-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            action=action,
            decision=DECISION_REQUIRE_EXECUTIVE_APPROVAL,
            allowed=False,
            blocked=False,
            requires_approval=True,
            requires_executive_approval=True,
            reason=reason,
            risk_level=RISK_CRITICAL,
            findings=findings,
        )

        self._persist_decision(decision, payload)

        self._emit(
            event_type,
            tenant_id=tenant_id,
            severity=RISK_CRITICAL,
            payload=decision.to_dict(),
        )

        return decision

    def _target_count(self, payload: Dict[str, Any]) -> int:
        max_count = 1

        for key in (
            "targets",
            "user_ids",
            "mailboxes",
            "message_ids",
            "endpoint_ids",
            "device_ids",
            "ips",
        ):
            value = payload.get(key)

            if isinstance(value, list):
                max_count = max(max_count, len(value))

        max_count = max(
            max_count,
            _safe_int(payload.get("target_count"), 0),
            _safe_int(payload.get("count"), 0),
        )

        return max_count

    def _count_events(
        self,
        *,
        tenant_id: str,
        since_ms: int,
        destructive_only: bool = False,
        actions: Optional[set[str]] = None,
    ) -> int:
        clauses = ["tenant_id=?", "created_at_ms>=?"]
        params: List[Any] = [tenant_id, since_ms]

        if destructive_only:
            clauses.append("destructive=1")

        if actions:
            placeholders = ",".join(["?"] * len(actions))
            clauses.append(f"action IN ({placeholders})")
            params.extend(list(actions))

        with self._connect() as conn:
            row = conn.execute(
                f"""
                SELECT COUNT(*)
                FROM safety_execution_events
                WHERE {' AND '.join(clauses)}
                """,
                params,
            ).fetchone()

        return int(row[0] if row else 0)

    def _last_action_ms(self, tenant_id: str, action: str) -> Optional[int]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT created_at_ms
                FROM safety_execution_events
                WHERE tenant_id=? AND action=?
                ORDER BY created_at_ms DESC
                LIMIT 1
                """,
                (tenant_id, action),
            ).fetchone()

        if not row:
            return None

        return _safe_int(row[0])

    def _persist_decision(self, decision: SafetyDecision, payload: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO safety_guardrail_decisions (
                    decision_id,
                    tenant_id,
                    action,
                    decision,
                    allowed,
                    blocked,
                    requires_approval,
                    requires_executive_approval,
                    reason,
                    risk_level,
                    findings_json,
                    payload_json,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.tenant_id,
                    decision.action,
                    decision.decision,
                    int(decision.allowed),
                    int(decision.blocked),
                    int(decision.requires_approval),
                    int(decision.requires_executive_approval),
                    decision.reason,
                    decision.risk_level,
                    _json_dumps(decision.findings),
                    _json_dumps(payload),
                    decision.created_at_ms,
                ),
            )
            conn.commit()

    def list_recent_decisions(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if tenant_id:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM safety_guardrail_decisions
                    WHERE tenant_id=?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                    """,
                    (tenant_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM safety_guardrail_decisions
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

            cols = [
                d[1]
                for d in conn.execute(
                    "PRAGMA table_info(safety_guardrail_decisions)"
                ).fetchall()
            ]

        return [dict(zip(cols, row)) for row in rows]

    def _row_to_dict(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        row: Any,
    ) -> Dict[str, Any]:
        cols = [
            d[1]
            for d in conn.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
        ]

        return dict(zip(cols, row))

    def _emit(
        self,
        event_type: str,
        *,
        tenant_id: str,
        payload: Dict[str, Any],
        severity: str = RISK_LOW,
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source="safety_guardrails",
                severity=severity,
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="safety_guardrails",
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_GUARDRAILS: Optional[SafetyGuardrails] = None


def get_safety_guardrails(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
) -> SafetyGuardrails:
    global _DEFAULT_GUARDRAILS

    if reset or _DEFAULT_GUARDRAILS is None:
        _DEFAULT_GUARDRAILS = SafetyGuardrails(
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_GUARDRAILS


def check_action_safety(
    storage: Any,
    *,
    tenant_id: str,
    action: str,
    payload: Optional[Dict[str, Any]] = None,
    actor: str = "safety_guardrails",
    execution_id: Optional[str] = None,
    case_id: Optional[Any] = None,
    connector_id: Optional[str] = None,
    autonomous: bool = True,
) -> SafetyDecision:
    guardrails = get_safety_guardrails(storage)

    return guardrails.check_action(
        tenant_id=tenant_id,
        action=action,
        payload=payload,
        actor=actor,
        execution_id=execution_id,
        case_id=case_id,
        connector_id=connector_id,
        autonomous=autonomous,
    )