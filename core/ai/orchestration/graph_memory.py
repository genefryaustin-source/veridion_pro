"""
core/ai/orchestration/graph_memory.py

Persistent learning memory for execution graphs.

Tracks:
- graph success/failure
- rollback-heavy branches
- false-positive containment
- escalation timing
- verification confidence
- tenant preferences
- policy effectiveness
- containment effectiveness
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


@dataclass
class GraphMemoryRecord:
    graph_id: str
    tenant_id: str = "default"
    graph_type: str = "unknown"
    success: bool = False
    status: str = "UNKNOWN"
    rollback_count: int = 0
    failed_nodes: List[str] = field(default_factory=list)
    executed_nodes: List[str] = field(default_factory=list)
    verification_confidence: float = 0.0
    escalation_triggered: bool = False
    containment_effective: Optional[bool] = None
    policy_decision: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GraphMemory:
    def __init__(self, db_path: str = "data/graph_memory.db"):
        self.db_path = db_path
        self.ensure_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS graph_memory (
                    id TEXT PRIMARY KEY,
                    graph_id TEXT,
                    tenant_id TEXT,
                    graph_type TEXT,
                    success INTEGER,
                    status TEXT,
                    rollback_count INTEGER,
                    failed_nodes_json TEXT,
                    executed_nodes_json TEXT,
                    verification_confidence REAL,
                    escalation_triggered INTEGER,
                    containment_effective INTEGER,
                    policy_decision TEXT,
                    metadata_json TEXT,
                    created_at_ms INTEGER
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_memory_tenant ON graph_memory(tenant_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_memory_graph ON graph_memory(graph_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_memory_success ON graph_memory(success)")
            conn.commit()

    def record_graph_result(self, record: GraphMemoryRecord) -> str:
        row_id = str(uuid.uuid4())

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO graph_memory (
                    id, graph_id, tenant_id, graph_type, success, status,
                    rollback_count, failed_nodes_json, executed_nodes_json,
                    verification_confidence, escalation_triggered,
                    containment_effective, policy_decision, metadata_json,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row_id,
                    record.graph_id,
                    record.tenant_id,
                    record.graph_type,
                    1 if record.success else 0,
                    record.status,
                    int(record.rollback_count),
                    json.dumps(record.failed_nodes),
                    json.dumps(record.executed_nodes),
                    float(record.verification_confidence),
                    1 if record.escalation_triggered else 0,
                    None if record.containment_effective is None else int(bool(record.containment_effective)),
                    record.policy_decision,
                    json.dumps(record.metadata),
                    int(time.time() * 1000),
                ),
            )
            conn.commit()

        return row_id

    def summarize_tenant_learning(self, tenant_id: str = "default") -> Dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT success, rollback_count, escalation_triggered,
                       containment_effective, verification_confidence
                FROM graph_memory
                WHERE tenant_id = ?
                """,
                (tenant_id,),
            ).fetchall()

        total = len(rows)
        if total == 0:
            return {
                "tenant_id": tenant_id,
                "total_graphs": 0,
                "success_rate": 0.0,
                "rollback_rate": 0.0,
                "avg_verification_confidence": 0.0,
                "containment_effectiveness": 0.0,
                "escalation_rate": 0.0,
            }

        success_count = sum(1 for r in rows if r[0])
        rollback_total = sum(int(r[1] or 0) for r in rows)
        escalation_count = sum(1 for r in rows if r[2])
        confidence_values = [float(r[4] or 0.0) for r in rows]

        containment_values = [r[3] for r in rows if r[3] is not None]
        containment_effective = (
            sum(1 for v in containment_values if v) / max(len(containment_values), 1)
        )

        return {
            "tenant_id": tenant_id,
            "total_graphs": total,
            "success_rate": round(success_count / total, 4),
            "rollback_rate": round(rollback_total / total, 4),
            "avg_verification_confidence": round(sum(confidence_values) / max(len(confidence_values), 1), 4),
            "containment_effectiveness": round(containment_effective, 4),
            "escalation_rate": round(escalation_count / total, 4),
        }

    def recommend_policy_adjustments(self, tenant_id: str = "default") -> Dict[str, Any]:
        summary = self.summarize_tenant_learning(tenant_id)

        recommendations = []

        if summary["rollback_rate"] >= 0.25:
            recommendations.append("Increase pre-execution verification before containment.")

        if summary["success_rate"] < 0.75 and summary["total_graphs"] >= 5:
            recommendations.append("Throttle autonomy mode for this tenant until graph reliability improves.")

        if summary["containment_effectiveness"] < 0.70 and summary["total_graphs"] >= 5:
            recommendations.append("Require analyst approval before endpoint containment.")

        if summary["avg_verification_confidence"] < 0.60 and summary["total_graphs"] >= 5:
            recommendations.append("Increase verification frequency and add secondary validation.")

        return {
            "tenant_id": tenant_id,
            "summary": summary,
            "recommendations": recommendations,
        }