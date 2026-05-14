"""
core/security/execution_sandbox.py

Autonomous Execution Safety Kernel.

Purpose:
- prevent dangerous autonomous actions
- enforce rate limits
- enforce blast-radius limits
- enforce tenant boundaries
- restrict connectors
- enforce destructive-action quotas
- validate rollback availability
- prevent action replay
- provide FULL_AUTONOMY safety gates

This should be called before real connector execution.
"""

from __future__ import annotations

import time
import uuid
import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


DEFAULT_DB_PATH = "data/execution_sandbox.db"

DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


@dataclass
class SandboxPolicy:
    tenant_id: str = "default"

    enabled: bool = True

    max_actions_per_minute: int = 30
    max_destructive_per_hour: int = 5
    max_endpoint_containments_per_hour: int = 10
    max_identity_actions_per_hour: int = 5

    max_unique_targets_per_hour: int = 25
    max_cases_touched_per_hour: int = 20

    require_rollback_for_destructive: bool = True
    require_approval_for_critical: bool = True
    allow_full_autonomy_destructive: bool = False

    allowed_connectors: List[str] = field(default_factory=lambda: [
        "crowdstrike",
        "microsoft_graph",
    ])

    blocked_actions: List[str] = field(default_factory=list)

    destructive_actions: List[str] = field(default_factory=lambda: [
        "contain_host",
        "endpoint_quarantine",
        "disable_user",
        "revoke_sessions",
        "token_revocation",
        "session_kill",
        "mailbox_quarantine",
        "message_purge",
        "delete_file",
        "kill_process",
    ])

    endpoint_actions: List[str] = field(default_factory=lambda: [
        "contain_host",
        "endpoint_quarantine",
        "process_kill",
        "rtr_command",
    ])

    identity_actions: List[str] = field(default_factory=lambda: [
        "disable_user",
        "revoke_sessions",
        "token_revocation",
        "session_kill",
        "mailbox_quarantine",
    ])


@dataclass
class SandboxDecision:
    decision: str
    allowed: bool
    requires_approval: bool = False
    reason: str = ""
    sandbox_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionSandbox:
    """
    Safety kernel for all autonomous execution.
    """

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        policy: Optional[SandboxPolicy] = None,
    ):
        self.db_path = db_path
        self.policy = policy or SandboxPolicy()
        self.ensure_schema()

    # ========================================================
    # DB
    # ========================================================

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sandbox_action_log (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    action TEXT NOT NULL,
                    connector TEXT,
                    target TEXT,
                    case_id TEXT,
                    graph_id TEXT,
                    severity TEXT,
                    destructive INTEGER,
                    endpoint_action INTEGER,
                    identity_action INTEGER,
                    decision TEXT,
                    reason TEXT,
                    created_at_ms INTEGER NOT NULL
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_sandbox_tenant ON sandbox_action_log(tenant_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sandbox_time ON sandbox_action_log(created_at_ms)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sandbox_hash ON sandbox_action_log(action_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sandbox_action ON sandbox_action_log(action)")
            conn.commit()

    # ========================================================
    # MAIN EVALUATION
    # ========================================================

    def evaluate(
        self,
        tenant_id: str,
        action: str,
        connector: Optional[str] = None,
        target: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        rollback_supported: bool = False,
    ) -> SandboxDecision:
        context = context or {}

        if not self.policy.enabled:
            return self._allow("sandbox_disabled", tenant_id, action, connector, target, context)

        tenant_id = tenant_id or self.policy.tenant_id
        severity = str(context.get("severity") or SEVERITY_LOW).upper()
        autonomy_mode = str(context.get("autonomy_mode") or "MANUAL").upper()

        destructive = self.is_destructive(action)
        endpoint_action = self.is_endpoint_action(action)
        identity_action = self.is_identity_action(action)

        if action in self.policy.blocked_actions:
            return self._block("action_explicitly_blocked", tenant_id, action, connector, target, context)

        if connector and connector not in self.policy.allowed_connectors:
            return self._block("connector_not_allowed", tenant_id, action, connector, target, context)

        if severity == SEVERITY_CRITICAL and self.policy.require_approval_for_critical:
            if autonomy_mode != "LOCKDOWN":
                return self._approval(
                    "critical_action_requires_approval",
                    tenant_id,
                    action,
                    connector,
                    target,
                    context,
                )

        if destructive:
            if autonomy_mode == "FULL_AUTONOMY" and not self.policy.allow_full_autonomy_destructive:
                return self._approval(
                    "full_autonomy_destructive_requires_approval",
                    tenant_id,
                    action,
                    connector,
                    target,
                    context,
                )

            if self.policy.require_rollback_for_destructive and not rollback_supported:
                return self._block(
                    "destructive_action_requires_rollback_support",
                    tenant_id,
                    action,
                    connector,
                    target,
                    context,
                )

        replay = self.detect_replay(
            tenant_id=tenant_id,
            action=action,
            connector=connector,
            target=target,
            context=context,
        )

        if replay:
            return self._block("action_replay_detected", tenant_id, action, connector, target, context)

        if self.count_actions(tenant_id, 60_000) >= self.policy.max_actions_per_minute:
            return self._block("rate_limit_actions_per_minute_exceeded", tenant_id, action, connector, target, context)

        if destructive and self.count_destructive(tenant_id, 3_600_000) >= self.policy.max_destructive_per_hour:
            return self._block("destructive_quota_exceeded", tenant_id, action, connector, target, context)

        if endpoint_action and self.count_endpoint_actions(tenant_id, 3_600_000) >= self.policy.max_endpoint_containments_per_hour:
            return self._block("endpoint_action_quota_exceeded", tenant_id, action, connector, target, context)

        if identity_action and self.count_identity_actions(tenant_id, 3_600_000) >= self.policy.max_identity_actions_per_hour:
            return self._block("identity_action_quota_exceeded", tenant_id, action, connector, target, context)

        if self.count_unique_targets(tenant_id, 3_600_000) >= self.policy.max_unique_targets_per_hour:
            return self._block("blast_radius_unique_targets_exceeded", tenant_id, action, connector, target, context)

        if self.count_cases_touched(tenant_id, 3_600_000) >= self.policy.max_cases_touched_per_hour:
            return self._block("blast_radius_cases_touched_exceeded", tenant_id, action, connector, target, context)

        return self._allow("sandbox_allowed", tenant_id, action, connector, target, context)

    # ========================================================
    # RECORDING
    # ========================================================

    def record_decision(
        self,
        decision: SandboxDecision,
        tenant_id: str,
        action: str,
        connector: Optional[str],
        target: Optional[str],
        context: Dict[str, Any],
    ) -> None:
        action_hash = self.action_hash(
            tenant_id=tenant_id,
            action=action,
            connector=connector,
            target=target,
            context=context,
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sandbox_action_log (
                    id, tenant_id, action_hash, action, connector,
                    target, case_id, graph_id, severity,
                    destructive, endpoint_action, identity_action,
                    decision, reason, created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.sandbox_id,
                    tenant_id,
                    action_hash,
                    action,
                    connector,
                    target,
                    str(context.get("case_id")) if context.get("case_id") is not None else None,
                    str(context.get("graph_id")) if context.get("graph_id") is not None else None,
                    str(context.get("severity") or SEVERITY_LOW).upper(),
                    int(self.is_destructive(action)),
                    int(self.is_endpoint_action(action)),
                    int(self.is_identity_action(action)),
                    decision.decision,
                    decision.reason,
                    decision.timestamp_ms,
                ),
            )
            conn.commit()

        dispatch_event(
            "EXECUTION_SANDBOX_DECISION_RECORDED",
            {
                "tenant_id": tenant_id,
                "action": action,
                "connector": connector,
                "target": target,
                "decision": decision.decision,
                "reason": decision.reason,
                "sandbox_id": decision.sandbox_id,
            },
            source="execution_sandbox",
        )

    def evaluate_and_record(
        self,
        tenant_id: str,
        action: str,
        connector: Optional[str] = None,
        target: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        rollback_supported: bool = False,
    ) -> SandboxDecision:
        context = context or {}

        decision = self.evaluate(
            tenant_id=tenant_id,
            action=action,
            connector=connector,
            target=target,
            context=context,
            rollback_supported=rollback_supported,
        )

        self.record_decision(
            decision=decision,
            tenant_id=tenant_id,
            action=action,
            connector=connector,
            target=target,
            context=context,
        )

        return decision

    # ========================================================
    # DETECTION / COUNTS
    # ========================================================

    def action_hash(
        self,
        tenant_id: str,
        action: str,
        connector: Optional[str],
        target: Optional[str],
        context: Dict[str, Any],
    ) -> str:
        stable = {
            "tenant_id": tenant_id,
            "action": action,
            "connector": connector,
            "target": target,
            "case_id": context.get("case_id"),
            "graph_id": context.get("graph_id"),
            "evidence_id": context.get("evidence_id"),
        }

        raw = json.dumps(stable, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def detect_replay(
        self,
        tenant_id: str,
        action: str,
        connector: Optional[str],
        target: Optional[str],
        context: Dict[str, Any],
        window_ms: int = 10 * 60_000,
    ) -> bool:
        cutoff = self._now_ms() - window_ms
        action_hash = self.action_hash(tenant_id, action, connector, target, context)

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM sandbox_action_log
                WHERE tenant_id = ?
                  AND action_hash = ?
                  AND created_at_ms >= ?
                  AND decision IN (?, ?)
                """,
                (
                    tenant_id,
                    action_hash,
                    cutoff,
                    DECISION_ALLOW,
                    DECISION_REQUIRE_APPROVAL,
                ),
            ).fetchone()

        return int(row["c"] or 0) > 0

    def count_actions(self, tenant_id: str, window_ms: int) -> int:
        return self._count(tenant_id, window_ms)

    def count_destructive(self, tenant_id: str, window_ms: int) -> int:
        return self._count(tenant_id, window_ms, "destructive = 1")

    def count_endpoint_actions(self, tenant_id: str, window_ms: int) -> int:
        return self._count(tenant_id, window_ms, "endpoint_action = 1")

    def count_identity_actions(self, tenant_id: str, window_ms: int) -> int:
        return self._count(tenant_id, window_ms, "identity_action = 1")

    def count_unique_targets(self, tenant_id: str, window_ms: int) -> int:
        cutoff = self._now_ms() - window_ms

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(DISTINCT target) AS c
                FROM sandbox_action_log
                WHERE tenant_id = ?
                  AND created_at_ms >= ?
                  AND target IS NOT NULL
                  AND decision = ?
                """,
                (tenant_id, cutoff, DECISION_ALLOW),
            ).fetchone()

        return int(row["c"] or 0)

    def count_cases_touched(self, tenant_id: str, window_ms: int) -> int:
        cutoff = self._now_ms() - window_ms

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(DISTINCT case_id) AS c
                FROM sandbox_action_log
                WHERE tenant_id = ?
                  AND created_at_ms >= ?
                  AND case_id IS NOT NULL
                  AND decision = ?
                """,
                (tenant_id, cutoff, DECISION_ALLOW),
            ).fetchone()

        return int(row["c"] or 0)

    def _count(
        self,
        tenant_id: str,
        window_ms: int,
        extra_where: Optional[str] = None,
    ) -> int:
        cutoff = self._now_ms() - window_ms

        where = """
            tenant_id = ?
            AND created_at_ms >= ?
            AND decision = ?
        """

        if extra_where:
            where += f" AND {extra_where}"

        with self._connect() as conn:
            row = conn.execute(
                f"""
                SELECT COUNT(*) AS c
                FROM sandbox_action_log
                WHERE {where}
                """,
                (tenant_id, cutoff, DECISION_ALLOW),
            ).fetchone()

        return int(row["c"] or 0)

    # ========================================================
    # CLASSIFICATION
    # ========================================================

    def is_destructive(self, action: str) -> bool:
        return action in self.policy.destructive_actions

    def is_endpoint_action(self, action: str) -> bool:
        return action in self.policy.endpoint_actions

    def is_identity_action(self, action: str) -> bool:
        return action in self.policy.identity_actions

    # ========================================================
    # DECISION HELPERS
    # ========================================================

    def _allow(
        self,
        reason: str,
        tenant_id: str,
        action: str,
        connector: Optional[str],
        target: Optional[str],
        context: Dict[str, Any],
    ) -> SandboxDecision:
        return SandboxDecision(
            decision=DECISION_ALLOW,
            allowed=True,
            reason=reason,
            metadata=self._metadata(tenant_id, action, connector, target, context),
        )

    def _block(
        self,
        reason: str,
        tenant_id: str,
        action: str,
        connector: Optional[str],
        target: Optional[str],
        context: Dict[str, Any],
    ) -> SandboxDecision:
        dispatch_event(
            "EXECUTION_SANDBOX_BLOCKED",
            {
                "tenant_id": tenant_id,
                "action": action,
                "connector": connector,
                "target": target,
                "reason": reason,
            },
            source="execution_sandbox",
        )

        return SandboxDecision(
            decision=DECISION_BLOCK,
            allowed=False,
            reason=reason,
            metadata=self._metadata(tenant_id, action, connector, target, context),
        )

    def _approval(
        self,
        reason: str,
        tenant_id: str,
        action: str,
        connector: Optional[str],
        target: Optional[str],
        context: Dict[str, Any],
    ) -> SandboxDecision:
        dispatch_event(
            "EXECUTION_SANDBOX_APPROVAL_REQUIRED",
            {
                "tenant_id": tenant_id,
                "action": action,
                "connector": connector,
                "target": target,
                "reason": reason,
            },
            source="execution_sandbox",
        )

        return SandboxDecision(
            decision=DECISION_REQUIRE_APPROVAL,
            allowed=False,
            requires_approval=True,
            reason=reason,
            metadata=self._metadata(tenant_id, action, connector, target, context),
        )

    def _metadata(
        self,
        tenant_id: str,
        action: str,
        connector: Optional[str],
        target: Optional[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "action": action,
            "connector": connector,
            "target": target,
            "case_id": context.get("case_id"),
            "graph_id": context.get("graph_id"),
            "severity": context.get("severity"),
            "autonomy_mode": context.get("autonomy_mode"),
            "destructive": self.is_destructive(action),
            "endpoint_action": self.is_endpoint_action(action),
            "identity_action": self.is_identity_action(action),
        }

    def _now_ms(self) -> int:
        return int(time.time() * 1000)


# ============================================================
# SINGLETON HELPERS
# ============================================================

_DEFAULT_SANDBOX: Optional[ExecutionSandbox] = None


def get_execution_sandbox() -> ExecutionSandbox:
    global _DEFAULT_SANDBOX

    if _DEFAULT_SANDBOX is None:
        _DEFAULT_SANDBOX = ExecutionSandbox()

    return _DEFAULT_SANDBOX


def sandbox_check(
    tenant_id: str,
    action: str,
    connector: Optional[str] = None,
    target: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    rollback_supported: bool = False,
) -> SandboxDecision:
    return get_execution_sandbox().evaluate_and_record(
        tenant_id=tenant_id,
        action=action,
        connector=connector,
        target=target,
        context=context or {},
        rollback_supported=rollback_supported,
    )