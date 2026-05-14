from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


class OrchestrationMemory:
    """
    Long-term operational memory for AI orchestration.

    Tracks:
    - autonomous execution history
    - analyst overrides
    - tenant behavior patterns
    - approval tendencies
    - containment outcomes
    - escalation outcomes
    - rollback frequency
    - recurring operational trends
    """

    def __init__(
        self,
        *,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
    ):
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self._ensure_tables()

    # ------------------------------------------------------------------
    # Execution Memory
    # ------------------------------------------------------------------

    def record_execution_outcome(
        self,
        *,
        action: str,
        outcome: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "orchestration_memory",
        adapter: Optional[str] = None,
        execution_id: Optional[str] = None,
        confidence: Optional[int] = None,
        risk_score: Optional[int] = None,
        rollback_occurred: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "memory_id": self._new_memory_id("MEMEXEC"),
            "memory_type": "EXECUTION_OUTCOME",
            "case_id": case_id,
            "tenant_id": tenant_id,
            "action": _upper(action),
            "outcome": _upper(outcome),
            "actor": actor,
            "adapter": adapter,
            "execution_id": execution_id,
            "confidence": confidence,
            "risk_score": risk_score,
            "rollback_occurred": int(bool(rollback_occurred)),
            "metadata_json": json.dumps(metadata or {}),
            "created_at_ms": _now_ms(),
        }

        self._insert_memory(record)
        self._publish("ORCHESTRATION_MEMORY_RECORDED", case_id, tenant_id, actor, record)
        return record

    # ------------------------------------------------------------------
    # Analyst Feedback / Overrides
    # ------------------------------------------------------------------

    def record_analyst_override(
        self,
        *,
        case_id: Any,
        override_type: str,
        original_recommendation: Dict[str, Any],
        analyst_action: Dict[str, Any],
        analyst: str,
        tenant_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        record = {
            "memory_id": self._new_memory_id("MEMOVR"),
            "memory_type": "ANALYST_OVERRIDE",
            "case_id": case_id,
            "tenant_id": tenant_id,
            "action": _upper(original_recommendation.get("action")),
            "outcome": _upper(override_type),
            "actor": analyst,
            "adapter": None,
            "execution_id": None,
            "confidence": original_recommendation.get("confidence"),
            "risk_score": None,
            "rollback_occurred": 0,
            "metadata_json": json.dumps({
                "original_recommendation": original_recommendation,
                "analyst_action": analyst_action,
                "reason": reason,
            }),
            "created_at_ms": _now_ms(),
        }

        self._insert_memory(record)
        self._publish("ANALYST_OVERRIDE_RECORDED", case_id, tenant_id, analyst, record)
        return record

    # ------------------------------------------------------------------
    # Approval Memory
    # ------------------------------------------------------------------

    def record_approval_outcome(
        self,
        *,
        approval_type: str,
        action: str,
        outcome: str,
        approver_role: Optional[str] = None,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        actor: str = "orchestration_memory",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.record_execution_outcome(
            action=action,
            outcome=f"APPROVAL_{outcome}",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            execution_id=approval_id,
            metadata={
                "approval_type": approval_type,
                "approver_role": approver_role,
                **(metadata or {}),
            },
        )

    # ------------------------------------------------------------------
    # Operational Trend Memory
    # ------------------------------------------------------------------

    def record_operational_trend(
        self,
        *,
        trend_type: str,
        key: str,
        value: Any,
        tenant_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        actor: str = "orchestration_memory",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "trend_id": self._new_memory_id("TREND"),
            "trend_type": _upper(trend_type),
            "trend_key": _upper(key),
            "trend_value": str(value),
            "tenant_id": tenant_id,
            "case_id": case_id,
            "actor": actor,
            "metadata_json": json.dumps(metadata or {}),
            "created_at_ms": _now_ms(),
        }

        self._insert_trend(record)
        self._publish("ORCHESTRATION_TREND_RECORDED", case_id, tenant_id, actor, record)
        return record

    # ------------------------------------------------------------------
    # Tenant Behavior Summary
    # ------------------------------------------------------------------

    def get_tenant_behavior_profile(
        self,
        *,
        tenant_id: str,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        rows = self.search_memory(tenant_id=tenant_id, limit=limit)

        total = len(rows)
        approvals = [r for r in rows if str(r.get("outcome", "")).startswith("APPROVAL_")]
        overrides = [r for r in rows if r.get("memory_type") == "ANALYST_OVERRIDE"]
        failures = [r for r in rows if r.get("outcome") in {"FAILED", "ERROR", "BLOCKED"}]
        rollbacks = [r for r in rows if int(r.get("rollback_occurred") or 0) == 1]

        action_counts: Dict[str, int] = {}
        outcome_counts: Dict[str, int] = {}

        for row in rows:
            action = row.get("action") or "UNKNOWN"
            outcome = row.get("outcome") or "UNKNOWN"
            action_counts[action] = action_counts.get(action, 0) + 1
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

        preference = self._infer_tenant_preference(
            approval_count=len(approvals),
            override_count=len(overrides),
            failure_count=len(failures),
            rollback_count=len(rollbacks),
            total=total,
        )

        return {
            "tenant_id": tenant_id,
            "total_memory_records": total,
            "approval_events": len(approvals),
            "analyst_overrides": len(overrides),
            "failures": len(failures),
            "rollbacks": len(rollbacks),
            "action_counts": action_counts,
            "outcome_counts": outcome_counts,
            "inferred_preference": preference,
            "generated_at_ms": _now_ms(),
        }

    def get_approval_tendencies(
        self,
        *,
        tenant_id: Optional[str] = None,
        approval_type: Optional[str] = None,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        rows = self.search_memory(
            tenant_id=tenant_id,
            memory_type="EXECUTION_OUTCOME",
            limit=limit,
        )

        approval_rows = []

        for row in rows:
            meta = self._json(row.get("metadata_json"))
            if not str(row.get("outcome", "")).startswith("APPROVAL_"):
                continue

            if approval_type and meta.get("approval_type") != approval_type:
                continue

            approval_rows.append(row)

        approved = [
            r for r in approval_rows
            if r.get("outcome") in {"APPROVAL_APPROVED", "APPROVAL_GRANTED"}
        ]

        rejected = [
            r for r in approval_rows
            if r.get("outcome") in {"APPROVAL_REJECTED", "APPROVAL_DENIED"}
        ]

        return {
            "tenant_id": tenant_id,
            "approval_type": approval_type,
            "total": len(approval_rows),
            "approved": len(approved),
            "rejected": len(rejected),
            "approval_rate": (
                round(len(approved) / len(approval_rows), 3)
                if approval_rows
                else 0
            ),
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_memory(
        self,
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        memory_type: Optional[str] = None,
        action: Optional[str] = None,
        outcome: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if self.ledger is None:
            return []

        self._ensure_tables()

        try:
            query = """
                SELECT *
                FROM orchestration_memory
                WHERE 1 = 1
            """
            params: List[Any] = []

            if tenant_id is not None:
                query += " AND tenant_id = ?"
                params.append(tenant_id)

            if case_id is not None:
                query += " AND case_id = ?"
                params.append(str(case_id))

            if memory_type is not None:
                query += " AND memory_type = ?"
                params.append(_upper(memory_type))

            if action is not None:
                query += " AND action = ?"
                params.append(_upper(action))

            if outcome is not None:
                query += " AND outcome = ?"
                params.append(_upper(outcome))

            query += " ORDER BY created_at_ms DESC LIMIT ?"
            params.append(limit)

            with self.ledger._connect() as con:
                rows = con.execute(query, params).fetchall()
                return [dict(r) for r in rows]

        except Exception:
            return []

    def search_trends(
        self,
        *,
        tenant_id: Optional[str] = None,
        trend_type: Optional[str] = None,
        trend_key: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if self.ledger is None:
            return []

        self._ensure_tables()

        try:
            query = """
                SELECT *
                FROM orchestration_trends
                WHERE 1 = 1
            """
            params: List[Any] = []

            if tenant_id is not None:
                query += " AND tenant_id = ?"
                params.append(tenant_id)

            if trend_type is not None:
                query += " AND trend_type = ?"
                params.append(_upper(trend_type))

            if trend_key is not None:
                query += " AND trend_key = ?"
                params.append(_upper(trend_key))

            query += " ORDER BY created_at_ms DESC LIMIT ?"
            params.append(limit)

            with self.ledger._connect() as con:
                rows = con.execute(query, params).fetchall()
                return [dict(r) for r in rows]

        except Exception:
            return []

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _insert_memory(
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
                    INSERT INTO orchestration_memory (
                        memory_id,
                        memory_type,
                        case_id,
                        tenant_id,
                        action,
                        outcome,
                        actor,
                        adapter,
                        execution_id,
                        confidence,
                        risk_score,
                        rollback_occurred,
                        metadata_json,
                        created_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("memory_id"),
                        record.get("memory_type"),
                        str(record.get("case_id")) if record.get("case_id") is not None else None,
                        record.get("tenant_id"),
                        record.get("action"),
                        record.get("outcome"),
                        record.get("actor"),
                        record.get("adapter"),
                        record.get("execution_id"),
                        record.get("confidence"),
                        record.get("risk_score"),
                        record.get("rollback_occurred"),
                        record.get("metadata_json"),
                        record.get("created_at_ms"),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _insert_trend(
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
                    INSERT INTO orchestration_trends (
                        trend_id,
                        trend_type,
                        trend_key,
                        trend_value,
                        tenant_id,
                        case_id,
                        actor,
                        metadata_json,
                        created_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("trend_id"),
                        record.get("trend_type"),
                        record.get("trend_key"),
                        record.get("trend_value"),
                        record.get("tenant_id"),
                        str(record.get("case_id")) if record.get("case_id") is not None else None,
                        record.get("actor"),
                        record.get("metadata_json"),
                        record.get("created_at_ms"),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _ensure_tables(self) -> None:
        if self.ledger is None:
            return

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orchestration_memory (
                        memory_id TEXT PRIMARY KEY,
                        memory_type TEXT,
                        case_id TEXT,
                        tenant_id TEXT,
                        action TEXT,
                        outcome TEXT,
                        actor TEXT,
                        adapter TEXT,
                        execution_id TEXT,
                        confidence INTEGER,
                        risk_score INTEGER,
                        rollback_occurred INTEGER DEFAULT 0,
                        metadata_json TEXT,
                        created_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orchestration_trends (
                        trend_id TEXT PRIMARY KEY,
                        trend_type TEXT,
                        trend_key TEXT,
                        trend_value TEXT,
                        tenant_id TEXT,
                        case_id TEXT,
                        actor TEXT,
                        metadata_json TEXT,
                        created_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_orch_memory_tenant
                    ON orchestration_memory(tenant_id)
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_orch_memory_case
                    ON orchestration_memory(case_id)
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_orch_memory_action
                    ON orchestration_memory(action)
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_orch_trends_tenant
                    ON orchestration_trends(tenant_id)
                    """
                )

                con.commit()

        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _infer_tenant_preference(
        self,
        *,
        approval_count: int,
        override_count: int,
        failure_count: int,
        rollback_count: int,
        total: int,
    ) -> str:
        if total == 0:
            return "INSUFFICIENT_DATA"

        approval_ratio = approval_count / total
        override_ratio = override_count / total
        failure_ratio = failure_count / total
        rollback_ratio = rollback_count / total

        if approval_ratio >= 0.45 or override_ratio >= 0.25:
            return "APPROVAL_HEAVY"

        if failure_ratio >= 0.20 or rollback_ratio >= 0.15:
            return "CONSERVATIVE_AUTONOMY"

        if approval_ratio <= 0.15 and failure_ratio <= 0.10:
            return "AUTONOMY_TOLERANT"

        return "BALANCED"

    def _json(
        self,
        value: Any,
    ) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value

        if not value:
            return {}

        try:
            return json.loads(value)
        except Exception:
            return {}

    def _new_memory_id(
        self,
        prefix: str,
    ) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"

    def _publish(
        self,
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
                    source="orchestration_memory",
                )
            except Exception:
                pass

        if self.live_updates is not None:
            try:
                if case_id is not None:
                    self.live_updates.broadcast_case_update(
                        case_id=case_id,
                        tenant_id=tenant_id,
                        event_type=event_type,
                        payload=payload,
                        actor=actor,
                    )
                elif tenant_id is not None:
                    self.live_updates.broadcast_tenant_update(
                        tenant_id=tenant_id,
                        event_type=event_type,
                        payload=payload,
                        actor=actor,
                    )
            except Exception:
                pass