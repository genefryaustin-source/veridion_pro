"""
core/runtime/blast_radius_analyzer.py

Blast Radius Analyzer for Veridion Pro / CUI GovCloud App.

Purpose:
- Estimate operational impact before execution
- Detect mass-action risk
- Identify privileged/high-value targets
- Prevent recursive containment and rollback storms
- Force governance escalation when scope is too large
- Emit telemetry for SOC/governance visibility
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set


RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

DECISION_ALLOW = "ALLOW"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISION_REQUIRE_DUAL_APPROVAL = "REQUIRE_DUAL_APPROVAL"
DECISION_REQUIRE_EXECUTIVE_APPROVAL = "REQUIRE_EXECUTIVE_APPROVAL"
DECISION_BLOCK = "BLOCK"

EVENT_BLAST_RADIUS_ANALYZED = "BLAST_RADIUS_ANALYZED"
EVENT_HIGH_RISK_ACTION_DETECTED = "HIGH_RISK_ACTION_DETECTED"
EVENT_AUTONOMY_BLOCKED = "AUTONOMY_BLOCKED"
EVENT_REQUIRES_EXECUTIVE_APPROVAL = "REQUIRES_EXECUTIVE_APPROVAL"

DESTRUCTIVE_ACTIONS = {
    "DISABLE_USER",
    "ENABLE_USER",
    "REVOKE_SESSIONS",
    "DELETE_EMAIL",
    "PURGE_EMAIL",
    "ISOLATE_ENDPOINT",
    "UNISOLATE_ENDPOINT",
    "BLOCK_IP",
    "DEVICE_WIPE",
}

IDENTITY_ACTIONS = {
    "DISABLE_USER",
    "ENABLE_USER",
    "REVOKE_SESSIONS",
}

EMAIL_ACTIONS = {
    "QUARANTINE_EMAIL",
    "DELETE_EMAIL",
    "PURGE_EMAIL",
    "SEARCH_MAILBOX",
}

ENDPOINT_ACTIONS = {
    "ISOLATE_ENDPOINT",
    "UNISOLATE_ENDPOINT",
    "DEVICE_WIPE",
}

PRIVILEGED_HINTS = {
    "admin",
    "administrator",
    "global admin",
    "security admin",
    "compliance admin",
    "owner",
    "breakglass",
    "break-glass",
    "root",
    "privileged",
}

EXECUTIVE_HINTS = {
    "ceo",
    "cfo",
    "coo",
    "cto",
    "cio",
    "ciso",
    "president",
    "founder",
    "general counsel",
    "legal",
}

SERVICE_ACCOUNT_HINTS = {
    "svc",
    "service",
    "automation",
    "bot",
    "daemon",
    "scanner",
    "connector",
    "integration",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


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
            path = getattr(ledger, attr, None)
            if path:
                return sqlite3.connect(path, check_same_thread=False)

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
class BlastRadiusFinding:
    finding_type: str
    severity: str
    message: str
    score_impact: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BlastRadiusResult:
    analysis_id: str
    tenant_id: str
    action: str

    risk_score: int
    risk_level: str
    decision: str

    target_count: int = 1
    privileged_targets: List[str] = field(default_factory=list)
    executive_targets: List[str] = field(default_factory=list)
    service_account_targets: List[str] = field(default_factory=list)

    recursive_risk: bool = False
    mass_action: bool = False
    tenant_wide: bool = False
    destructive: bool = False

    requires_approval: bool = False
    requires_dual_approval: bool = False
    requires_legal: bool = False
    requires_executive_approval: bool = False
    autonomy_blocked: bool = False

    findings: List[BlastRadiusFinding] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["findings"] = [asdict(f) for f in self.findings]
        return data


class BlastRadiusAnalyzer:
    def __init__(self, storage: Any = None, *, event_bus: Any = None) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.conn = _get_connection(storage)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.ensure_schema()

    def ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blast_radius_analyses (
                analysis_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                action TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                decision TEXT NOT NULL,
                target_count INTEGER DEFAULT 1,
                privileged_targets_json TEXT,
                executive_targets_json TEXT,
                service_account_targets_json TEXT,
                recursive_risk INTEGER DEFAULT 0,
                mass_action INTEGER DEFAULT 0,
                tenant_wide INTEGER DEFAULT 0,
                destructive INTEGER DEFAULT 0,
                autonomy_blocked INTEGER DEFAULT 0,
                findings_json TEXT,
                recommendations_json TEXT,
                payload_json TEXT,
                created_at_ms INTEGER NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_blast_radius_tenant
            ON blast_radius_analyses(tenant_id)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_blast_radius_action
            ON blast_radius_analyses(action)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_blast_radius_created
            ON blast_radius_analyses(created_at_ms)
            """
        )

        self.conn.commit()

    def analyze(
        self,
        *,
        tenant_id: str,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "blast_radius_analyzer",
        context: Optional[Dict[str, Any]] = None,
    ) -> BlastRadiusResult:
        payload = payload or {}
        context = context or {}
        tenant_id = tenant_id or "default"
        action = _safe_str(action).upper()
        analysis_id = f"BRA-{uuid.uuid4().hex[:12].upper()}"

        targets = self._extract_targets(payload, context)
        target_count = max(1, len(targets))

        destructive = action in DESTRUCTIVE_ACTIONS
        tenant_wide = self._is_tenant_wide(payload, context, targets)
        recursive_risk = self._detect_recursive_risk(action, payload, context)
        mass_action = self._is_mass_action(action, target_count, payload, context)

        privileged = self._filter_targets(targets, PRIVILEGED_HINTS)
        executive = self._filter_targets(targets, EXECUTIVE_HINTS)
        service_accounts = self._filter_targets(targets, SERVICE_ACCOUNT_HINTS)

        findings: List[BlastRadiusFinding] = []
        score = 10

        if destructive:
            score += 25
            findings.append(
                BlastRadiusFinding(
                    finding_type="DESTRUCTIVE_ACTION",
                    severity=RISK_HIGH,
                    message=f"{action} is classified as destructive.",
                    score_impact=25,
                )
            )

        if target_count > 1:
            impact = min(30, target_count * 3)
            score += impact
            findings.append(
                BlastRadiusFinding(
                    finding_type="MULTI_TARGET_ACTION",
                    severity=RISK_MEDIUM,
                    message=f"Action affects {target_count} target(s).",
                    score_impact=impact,
                    metadata={"target_count": target_count},
                )
            )

        if mass_action:
            score += 30
            findings.append(
                BlastRadiusFinding(
                    finding_type="MASS_ACTION",
                    severity=RISK_CRITICAL,
                    message="Action appears to be a mass-scope operation.",
                    score_impact=30,
                )
            )

        if tenant_wide:
            score += 35
            findings.append(
                BlastRadiusFinding(
                    finding_type="TENANT_WIDE_SCOPE",
                    severity=RISK_CRITICAL,
                    message="Action appears tenant-wide or broadly scoped.",
                    score_impact=35,
                )
            )

        if privileged:
            score += 25
            findings.append(
                BlastRadiusFinding(
                    finding_type="PRIVILEGED_TARGET",
                    severity=RISK_CRITICAL,
                    message="Privileged target detected.",
                    score_impact=25,
                    metadata={"targets": privileged},
                )
            )

        if executive:
            score += 20
            findings.append(
                BlastRadiusFinding(
                    finding_type="EXECUTIVE_TARGET",
                    severity=RISK_HIGH,
                    message="Executive or legal target detected.",
                    score_impact=20,
                    metadata={"targets": executive},
                )
            )

        if service_accounts:
            score += 15
            findings.append(
                BlastRadiusFinding(
                    finding_type="SERVICE_ACCOUNT_TARGET",
                    severity=RISK_HIGH,
                    message="Service/integration account target detected.",
                    score_impact=15,
                    metadata={"targets": service_accounts},
                )
            )

        if recursive_risk:
            score += 35
            findings.append(
                BlastRadiusFinding(
                    finding_type="RECURSIVE_OR_ROLLBACK_RISK",
                    severity=RISK_CRITICAL,
                    message="Recursive containment or rollback-loop risk detected.",
                    score_impact=35,
                )
            )

        if action in IDENTITY_ACTIONS:
            score += 10

        if action in ENDPOINT_ACTIONS:
            score += 15

        score = min(100, max(0, score))
        risk_level = self._risk_level(score)

        decision = self._decision_from_result(
            score=score,
            risk_level=risk_level,
            destructive=destructive,
            tenant_wide=tenant_wide,
            mass_action=mass_action,
            privileged=bool(privileged),
            executive=bool(executive),
            recursive_risk=recursive_risk,
        )

        recommendations = self._recommendations(
            action=action,
            decision=decision,
            risk_level=risk_level,
            tenant_wide=tenant_wide,
            mass_action=mass_action,
            privileged=bool(privileged),
            executive=bool(executive),
            recursive_risk=recursive_risk,
        )

        result = BlastRadiusResult(
            analysis_id=analysis_id,
            tenant_id=tenant_id,
            action=action,
            risk_score=score,
            risk_level=risk_level,
            decision=decision,
            target_count=target_count,
            privileged_targets=privileged,
            executive_targets=executive,
            service_account_targets=service_accounts,
            recursive_risk=recursive_risk,
            mass_action=mass_action,
            tenant_wide=tenant_wide,
            destructive=destructive,
            requires_approval=decision in {
                DECISION_REQUIRE_APPROVAL,
                DECISION_REQUIRE_DUAL_APPROVAL,
                DECISION_REQUIRE_EXECUTIVE_APPROVAL,
                DECISION_BLOCK,
            },
            requires_dual_approval=decision in {
                DECISION_REQUIRE_DUAL_APPROVAL,
                DECISION_REQUIRE_EXECUTIVE_APPROVAL,
            },
            requires_legal=(
                action in EMAIL_ACTIONS and tenant_wide
            ) or bool(payload.get("requires_legal")),
            requires_executive_approval=decision == DECISION_REQUIRE_EXECUTIVE_APPROVAL,
            autonomy_blocked=decision == DECISION_BLOCK,
            findings=findings,
            recommendations=recommendations,
        )

        self._persist(result, payload={**payload, "context": context})
        self._emit_result(result, actor=actor)

        return result

    def _extract_targets(self, payload: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        values: List[Any] = []

        for source in (payload, context):
            for key in (
                "target_id",
                "target_user",
                "principal",
                "user_id",
                "user_ids",
                "mailbox",
                "mailboxes",
                "message_id",
                "message_ids",
                "endpoint_id",
                "endpoint_ids",
                "device_id",
                "device_ids",
                "host_id",
                "host_ids",
                "ip",
                "ips",
                "targets",
            ):
                values.extend(_as_list(source.get(key)))

        cleaned = []
        for value in values:
            s = _safe_str(value).strip()
            if s and s.lower() not in {"none", "null", "*"}:
                cleaned.append(s)

        return sorted(set(cleaned))

    def _is_tenant_wide(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any],
        targets: List[str],
    ) -> bool:
        flags = [
            payload.get("tenant_wide"),
            payload.get("all_users"),
            payload.get("all_mailboxes"),
            payload.get("all_devices"),
            context.get("tenant_wide"),
        ]

        if any(bool(x) for x in flags):
            return True

        raw = json.dumps({**payload, **context}, default=str).lower()
        markers = [
            "all_users",
            "all mailboxes",
            "entire tenant",
            "tenant-wide",
            "all devices",
            "all endpoints",
        ]

        return any(marker in raw for marker in markers)

    def _is_mass_action(
        self,
        action: str,
        target_count: int,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        explicit_count = max(
            _safe_int(payload.get("count"), 0),
            _safe_int(payload.get("target_count"), 0),
            _safe_int(context.get("target_count"), 0),
        )

        count = max(target_count, explicit_count)

        if action in IDENTITY_ACTIONS and count >= 5:
            return True

        if action in EMAIL_ACTIONS and count >= 10:
            return True

        if action in ENDPOINT_ACTIONS and count >= 5:
            return True

        return count >= 25

    def _detect_recursive_risk(
        self,
        action: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        chain_depth = max(
            _safe_int(payload.get("chain_depth"), 0),
            _safe_int(context.get("chain_depth"), 0),
            _safe_int(payload.get("rollback_depth"), 0),
            _safe_int(context.get("rollback_depth"), 0),
        )

        if chain_depth >= 3:
            return True

        if payload.get("is_rollback") and payload.get("rollback_triggered_by_rollback"):
            return True

        raw = json.dumps({**payload, **context}, default=str).lower()

        markers = [
            "rollback loop",
            "recursive rollback",
            "recursive containment",
            "containment storm",
        ]

        return any(marker in raw for marker in markers)

    def _filter_targets(self, targets: List[str], hints: Set[str]) -> List[str]:
        matches = []

        for target in targets:
            low = target.lower()
            if any(hint in low for hint in hints):
                matches.append(target)

        return matches

    def _risk_level(self, score: int) -> str:
        if score >= 90:
            return RISK_CRITICAL
        if score >= 70:
            return RISK_HIGH
        if score >= 40:
            return RISK_MEDIUM
        return RISK_LOW

    def _decision_from_result(
        self,
        *,
        score: int,
        risk_level: str,
        destructive: bool,
        tenant_wide: bool,
        mass_action: bool,
        privileged: bool,
        executive: bool,
        recursive_risk: bool,
    ) -> str:
        if recursive_risk:
            return DECISION_BLOCK

        if tenant_wide or (mass_action and destructive):
            return DECISION_REQUIRE_EXECUTIVE_APPROVAL

        if privileged or executive:
            return DECISION_REQUIRE_DUAL_APPROVAL

        if score >= 90:
            return DECISION_REQUIRE_EXECUTIVE_APPROVAL

        if score >= 70:
            return DECISION_REQUIRE_DUAL_APPROVAL

        if score >= 40 or destructive:
            return DECISION_REQUIRE_APPROVAL

        return DECISION_ALLOW

    def _recommendations(
        self,
        *,
        action: str,
        decision: str,
        risk_level: str,
        tenant_wide: bool,
        mass_action: bool,
        privileged: bool,
        executive: bool,
        recursive_risk: bool,
    ) -> List[str]:
        recs: List[str] = []

        if decision == DECISION_BLOCK:
            recs.append("Block autonomous execution and require manual review.")

        if tenant_wide:
            recs.append("Require executive approval for tenant-wide operation.")

        if mass_action:
            recs.append("Split into smaller batches and re-run blast-radius analysis.")

        if privileged:
            recs.append("Require dual approval for privileged identity impact.")

        if executive:
            recs.append("Notify executive/legal governance reviewer before execution.")

        if recursive_risk:
            recs.append("Stop recursive containment or rollback chain before proceeding.")

        if action in IDENTITY_ACTIONS:
            recs.append("Verify break-glass and service accounts are excluded.")

        if action in EMAIL_ACTIONS:
            recs.append("Preserve evidence copy before mailbox modification.")

        if action in ENDPOINT_ACTIONS:
            recs.append("Confirm endpoint ownership and business criticality.")

        if not recs:
            recs.append("Blast radius acceptable under current policy.")

        return recs

    def _persist(self, result: BlastRadiusResult, *, payload: Dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO blast_radius_analyses (
                analysis_id,
                tenant_id,
                action,
                risk_score,
                risk_level,
                decision,
                target_count,
                privileged_targets_json,
                executive_targets_json,
                service_account_targets_json,
                recursive_risk,
                mass_action,
                tenant_wide,
                destructive,
                autonomy_blocked,
                findings_json,
                recommendations_json,
                payload_json,
                created_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.analysis_id,
                result.tenant_id,
                result.action,
                result.risk_score,
                result.risk_level,
                result.decision,
                result.target_count,
                _json_dumps(result.privileged_targets),
                _json_dumps(result.executive_targets),
                _json_dumps(result.service_account_targets),
                int(result.recursive_risk),
                int(result.mass_action),
                int(result.tenant_wide),
                int(result.destructive),
                int(result.autonomy_blocked),
                _json_dumps([asdict(f) for f in result.findings]),
                _json_dumps(result.recommendations),
                _json_dumps(payload),
                result.created_at_ms,
            ),
        )
        self.conn.commit()

    def _emit_result(self, result: BlastRadiusResult, *, actor: str) -> None:
        payload = result.to_dict()
        payload["actor"] = actor

        self._emit(
            EVENT_BLAST_RADIUS_ANALYZED,
            tenant_id=result.tenant_id,
            severity=result.risk_level,
            payload=payload,
        )

        if result.risk_level in {RISK_HIGH, RISK_CRITICAL}:
            self._emit(
                EVENT_HIGH_RISK_ACTION_DETECTED,
                tenant_id=result.tenant_id,
                severity=result.risk_level,
                payload=payload,
            )

        if result.autonomy_blocked:
            self._emit(
                EVENT_AUTONOMY_BLOCKED,
                tenant_id=result.tenant_id,
                severity=RISK_CRITICAL,
                payload=payload,
            )

        if result.requires_executive_approval:
            self._emit(
                EVENT_REQUIRES_EXECUTIVE_APPROVAL,
                tenant_id=result.tenant_id,
                severity=RISK_CRITICAL,
                payload=payload,
            )

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
                source="blast_radius_analyzer",
                severity=severity,
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="blast_radius_analyzer",
                )
            except Exception:
                pass
        except Exception:
            pass

    def list_recent(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        if tenant_id:
            rows = self.conn.execute(
                """
                SELECT *
                FROM blast_radius_analyses
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
                FROM blast_radius_analyses
                ORDER BY created_at_ms DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        cols = [
            d[1]
            for d in self.conn.execute("PRAGMA table_info(blast_radius_analyses)").fetchall()
        ]

        return [dict(zip(cols, row)) for row in rows]


_DEFAULT_ANALYZER: Optional[BlastRadiusAnalyzer] = None


def get_blast_radius_analyzer(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
) -> BlastRadiusAnalyzer:
    global _DEFAULT_ANALYZER

    if reset or _DEFAULT_ANALYZER is None:
        _DEFAULT_ANALYZER = BlastRadiusAnalyzer(
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_ANALYZER


def analyze_blast_radius(
    storage: Any,
    *,
    tenant_id: str,
    action: str,
    payload: Optional[Dict[str, Any]] = None,
    actor: str = "blast_radius_analyzer",
    context: Optional[Dict[str, Any]] = None,
) -> BlastRadiusResult:
    analyzer = get_blast_radius_analyzer(storage)
    return analyzer.analyze(
        tenant_id=tenant_id,
        action=action,
        payload=payload,
        actor=actor,
        context=context,
    )