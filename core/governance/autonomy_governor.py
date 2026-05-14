"""
core/governance/autonomy_governor.py

Autonomy Governor.

AI command-authority safety layer.

Decides:
    "Should autonomous execution continue right now?"

Controls:
- autonomy throttling
- lockdown escalation
- rollback pressure
- governance drift
- confidence collapse
- connector outage pressure
- sandbox block pressure
- escalation spikes
- legal/export pressure
- execution freeze conditions
- dynamic approval enforcement

Feeds:
- governance war room
- autonomy control panel
- execution grid
- optimizer agent
- graph memory
"""

from __future__ import annotations

import time
import uuid
import sqlite3
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


try:
    from core.events.event_subscribers import (
        dispatch_event,
        get_recent_events,
    )
except Exception:
    def dispatch_event(*args, **kwargs):
        return None

    def get_recent_events(limit: int = 500, event_type: Optional[str] = None):
        return []


try:
    from core.runtime.distributed_execution_queue import (
        DistributedExecutionQueue,
        STATUS_PENDING,
        STATUS_RETRY,
        STATUS_RUNNING,
        STATUS_LEASED,
        STATUS_FAILED,
        STATUS_DEAD_LETTER,
    )
except Exception:
    DistributedExecutionQueue = None
    STATUS_PENDING = "PENDING"
    STATUS_RETRY = "RETRY"
    STATUS_RUNNING = "RUNNING"
    STATUS_LEASED = "LEASED"
    STATUS_FAILED = "FAILED"
    STATUS_DEAD_LETTER = "DEAD_LETTER"


try:
    from core.connectors.connector_health_monitor import (
        get_connector_health_monitor,
        HEALTH_HEALTHY,
        HEALTH_DEGRADED,
        HEALTH_OUTAGE,
    )
except Exception:
    get_connector_health_monitor = None
    HEALTH_HEALTHY = "HEALTHY"
    HEALTH_DEGRADED = "DEGRADED"
    HEALTH_OUTAGE = "OUTAGE"


try:
    from core.ai.orchestration.graph_memory import GraphMemory
except Exception:
    GraphMemory = None


DEFAULT_DB_PATH = "data/autonomy_governor.db"
DEFAULT_QUEUE_DB_PATH = "data/distributed_execution_queue.db"


DECISION_CONTINUE = "CONTINUE"
DECISION_THROTTLE = "THROTTLE"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISION_FREEZE = "FREEZE"
DECISION_LOCKDOWN = "LOCKDOWN"

MODE_MANUAL = "MANUAL"
MODE_ASSISTED = "ASSISTED"
MODE_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
MODE_FULL_AUTONOMY = "FULL_AUTONOMY"
MODE_LOCKDOWN = "LOCKDOWN"


@dataclass
class AutonomyGovernorThresholds:
    rollback_pressure_throttle: float = 15.0
    rollback_pressure_freeze: float = 30.0
    rollback_pressure_lockdown: float = 50.0

    governance_drift_throttle: float = 20.0
    governance_drift_freeze: float = 45.0
    governance_drift_lockdown: float = 70.0

    connector_outage_freeze_count: int = 2
    connector_degraded_throttle_count: int = 2

    sandbox_block_throttle_count: int = 5
    sandbox_block_freeze_count: int = 15

    dead_letter_throttle_count: int = 3
    dead_letter_freeze_count: int = 10

    escalation_spike_throttle_count: int = 5
    escalation_spike_freeze_count: int = 15

    legal_export_freeze_count: int = 5

    confidence_throttle_below: float = 60.0
    confidence_freeze_below: float = 35.0

    queue_pressure_throttle: int = 50
    queue_pressure_freeze: int = 200

    recent_event_limit: int = 1000


@dataclass
class AutonomyGovernorDecision:
    decision: str
    allowed: bool
    autonomy_mode: str
    recommended_mode: str
    reason: str
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    require_approval: bool = False
    freeze_execution: bool = False
    enter_lockdown: bool = False
    throttle_factor: float = 1.0

    rollback_pressure: float = 0.0
    governance_drift: float = 0.0
    optimizer_confidence: float = 0.0
    queue_pressure: int = 0
    connector_outages: int = 0
    connector_degraded: int = 0
    sandbox_blocks: int = 0
    dead_letters: int = 0
    escalation_spike: int = 0
    legal_export_pressure: int = 0

    findings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutonomyGovernor:
    """
    Central safety governor for autonomous execution.
    """

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        queue_db_path: str = DEFAULT_QUEUE_DB_PATH,
        thresholds: Optional[AutonomyGovernorThresholds] = None,
        queue: Optional[Any] = None,
    ):
        self.db_path = db_path
        self.queue_db_path = queue_db_path
        self.thresholds = thresholds or AutonomyGovernorThresholds()

        self.queue = queue or (
            DistributedExecutionQueue(db_path=queue_db_path)
            if DistributedExecutionQueue is not None
            else None
        )

        self.health_monitor = (
            get_connector_health_monitor()
            if get_connector_health_monitor
            else None
        )

        self.graph_memory = GraphMemory() if GraphMemory else None

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
                CREATE TABLE IF NOT EXISTS autonomy_governor_decisions (
                    decision_id TEXT PRIMARY KEY,
                    decision TEXT NOT NULL,
                    allowed INTEGER,
                    autonomy_mode TEXT,
                    recommended_mode TEXT,
                    reason TEXT,
                    require_approval INTEGER,
                    freeze_execution INTEGER,
                    enter_lockdown INTEGER,
                    throttle_factor REAL,
                    rollback_pressure REAL,
                    governance_drift REAL,
                    optimizer_confidence REAL,
                    queue_pressure INTEGER,
                    connector_outages INTEGER,
                    connector_degraded INTEGER,
                    sandbox_blocks INTEGER,
                    dead_letters INTEGER,
                    escalation_spike INTEGER,
                    legal_export_pressure INTEGER,
                    findings_json TEXT,
                    metadata_json TEXT,
                    created_at_ms INTEGER
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_governor_created
                ON autonomy_governor_decisions(created_at_ms)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_governor_decision
                ON autonomy_governor_decisions(decision)
            """)

            conn.commit()

    # ========================================================
    # EVENTING
    # ========================================================

    def emit_event(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        dispatch_event(
            event_type=event_type,
            payload=payload or {},
            source="autonomy_governor",
        )

    # ========================================================
    # MAIN EVALUATION
    # ========================================================

    def evaluate(
        self,
        autonomy_mode: str = MODE_ASSISTED,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        persist: bool = True,
    ) -> AutonomyGovernorDecision:

        context = context or {}
        autonomy_mode = str(autonomy_mode or MODE_ASSISTED).upper()

        telemetry = self.collect_telemetry(
            tenant_id=tenant_id,
            context=context,
        )

        findings: List[str] = []

        rollback_pressure = telemetry["rollback_pressure"]
        governance_drift = telemetry["governance_drift"]
        optimizer_confidence = telemetry["optimizer_confidence"]
        queue_pressure = telemetry["queue_pressure"]
        connector_outages = telemetry["connector_outages"]
        connector_degraded = telemetry["connector_degraded"]
        sandbox_blocks = telemetry["sandbox_blocks"]
        dead_letters = telemetry["dead_letters"]
        escalation_spike = telemetry["escalation_spike"]
        legal_export_pressure = telemetry["legal_export_pressure"]

        decision = DECISION_CONTINUE
        allowed = True
        recommended_mode = autonomy_mode
        reason = "autonomy_governor_continue"
        require_approval = False
        freeze_execution = False
        enter_lockdown = False
        throttle_factor = 1.0

        # ----------------------------------------------------
        # LOCKDOWN CONDITIONS
        # ----------------------------------------------------

        if rollback_pressure >= self.thresholds.rollback_pressure_lockdown:
            findings.append("rollback_pressure_lockdown_threshold_exceeded")
            decision = DECISION_LOCKDOWN

        if governance_drift >= self.thresholds.governance_drift_lockdown:
            findings.append("governance_drift_lockdown_threshold_exceeded")
            decision = DECISION_LOCKDOWN

        # ----------------------------------------------------
        # FREEZE CONDITIONS
        # ----------------------------------------------------

        if decision != DECISION_LOCKDOWN:
            if rollback_pressure >= self.thresholds.rollback_pressure_freeze:
                findings.append("rollback_pressure_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if governance_drift >= self.thresholds.governance_drift_freeze:
                findings.append("governance_drift_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if connector_outages >= self.thresholds.connector_outage_freeze_count:
                findings.append("connector_outage_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if sandbox_blocks >= self.thresholds.sandbox_block_freeze_count:
                findings.append("sandbox_block_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if dead_letters >= self.thresholds.dead_letter_freeze_count:
                findings.append("dead_letter_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if escalation_spike >= self.thresholds.escalation_spike_freeze_count:
                findings.append("escalation_spike_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if legal_export_pressure >= self.thresholds.legal_export_freeze_count:
                findings.append("legal_export_pressure_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if optimizer_confidence and optimizer_confidence < self.thresholds.confidence_freeze_below:
                findings.append("optimizer_confidence_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

            if queue_pressure >= self.thresholds.queue_pressure_freeze:
                findings.append("queue_pressure_freeze_threshold_exceeded")
                decision = DECISION_FREEZE

        # ----------------------------------------------------
        # THROTTLE CONDITIONS
        # ----------------------------------------------------

        if decision not in {DECISION_LOCKDOWN, DECISION_FREEZE}:
            if rollback_pressure >= self.thresholds.rollback_pressure_throttle:
                findings.append("rollback_pressure_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

            if governance_drift >= self.thresholds.governance_drift_throttle:
                findings.append("governance_drift_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

            if connector_degraded >= self.thresholds.connector_degraded_throttle_count:
                findings.append("connector_degraded_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

            if sandbox_blocks >= self.thresholds.sandbox_block_throttle_count:
                findings.append("sandbox_block_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

            if dead_letters >= self.thresholds.dead_letter_throttle_count:
                findings.append("dead_letter_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

            if escalation_spike >= self.thresholds.escalation_spike_throttle_count:
                findings.append("escalation_spike_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

            if optimizer_confidence and optimizer_confidence < self.thresholds.confidence_throttle_below:
                findings.append("optimizer_confidence_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

            if queue_pressure >= self.thresholds.queue_pressure_throttle:
                findings.append("queue_pressure_throttle_threshold_exceeded")
                decision = DECISION_THROTTLE

        # ----------------------------------------------------
        # DECISION NORMALIZATION
        # ----------------------------------------------------

        if decision == DECISION_LOCKDOWN:
            allowed = False
            recommended_mode = MODE_LOCKDOWN
            reason = "lockdown_required_by_governor"
            require_approval = True
            freeze_execution = True
            enter_lockdown = True
            throttle_factor = 0.0

        elif decision == DECISION_FREEZE:
            allowed = False
            recommended_mode = MODE_MANUAL
            reason = "execution_freeze_required_by_governor"
            require_approval = True
            freeze_execution = True
            throttle_factor = 0.0

        elif decision == DECISION_THROTTLE:
            allowed = True
            recommended_mode = self._downgrade_mode(autonomy_mode)
            reason = "autonomy_throttle_required_by_governor"
            require_approval = True
            throttle_factor = 0.35

        elif autonomy_mode == MODE_FULL_AUTONOMY and legal_export_pressure > 0:
            decision = DECISION_REQUIRE_APPROVAL
            allowed = False
            recommended_mode = MODE_SUPERVISED_AUTONOMY
            reason = "legal_export_pressure_requires_approval"
            require_approval = True
            throttle_factor = 0.0
            findings.append("full_autonomy_blocked_due_to_legal_export_pressure")

        result = AutonomyGovernorDecision(
            decision=decision,
            allowed=allowed,
            autonomy_mode=autonomy_mode,
            recommended_mode=recommended_mode,
            reason=reason,
            require_approval=require_approval,
            freeze_execution=freeze_execution,
            enter_lockdown=enter_lockdown,
            throttle_factor=throttle_factor,
            rollback_pressure=rollback_pressure,
            governance_drift=governance_drift,
            optimizer_confidence=optimizer_confidence,
            queue_pressure=queue_pressure,
            connector_outages=connector_outages,
            connector_degraded=connector_degraded,
            sandbox_blocks=sandbox_blocks,
            dead_letters=dead_letters,
            escalation_spike=escalation_spike,
            legal_export_pressure=legal_export_pressure,
            findings=findings,
            metadata={
                "tenant_id": tenant_id,
                "context": context,
                "telemetry": telemetry,
            },
        )

        if persist:
            self.record_decision(result)

        self.emit_event(
            "AUTONOMY_GOVERNOR_DECISION",
            result.__dict__,
        )

        return result

    # ========================================================
    # TELEMETRY COLLECTION
    # ========================================================

    def collect_telemetry(
        self,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        events = get_recent_events(
            limit=self.thresholds.recent_event_limit,
        )

        queue_stats = self._queue_stats(tenant_id)
        connector_stats = self._connector_stats()

        rollback_pressure = self._calculate_rollback_pressure(events)
        governance_drift = self._calculate_governance_drift(events)
        optimizer_confidence = self._calculate_optimizer_confidence(events)

        sandbox_blocks = self._count_events(
            events,
            [
                "EXECUTION_SANDBOX_BLOCKED",
                "AUTONOMOUS_ACTION_BLOCKED_BY_SANDBOX",
            ],
        )

        escalation_spike = self._count_events_containing(
            events,
            [
                "ESCALATION",
                "SLA_ESCALATION",
                "EXECUTIVE_ESCALATION",
            ],
        )

        legal_export_pressure = self._count_events_containing(
            events,
            [
                "EXPORT_CONTROL",
                "LEGAL",
                "ITAR",
                "EAR",
            ],
        )

        queue_pressure = (
            int(queue_stats.get("pending", 0))
            + int(queue_stats.get("retry", 0))
            + int(queue_stats.get("running", 0))
            + int(queue_stats.get("leased", 0))
        )

        return {
            "rollback_pressure": rollback_pressure,
            "governance_drift": governance_drift,
            "optimizer_confidence": optimizer_confidence,
            "queue_pressure": queue_pressure,
            "connector_outages": int(connector_stats.get("outage", 0)),
            "connector_degraded": int(connector_stats.get("degraded", 0)),
            "sandbox_blocks": sandbox_blocks,
            "dead_letters": int(queue_stats.get("dead_letter", 0)),
            "escalation_spike": escalation_spike,
            "legal_export_pressure": legal_export_pressure,
            "queue_stats": queue_stats,
            "connector_stats": connector_stats,
        }

    def _queue_stats(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        if self.queue is None:
            return {}

        try:
            return self.queue.get_stats(tenant_id=tenant_id)
        except Exception:
            return {}

    def _connector_stats(self) -> Dict[str, Any]:
        if self.health_monitor is None:
            return {}

        try:
            return self.health_monitor.stats()
        except Exception:
            return {}

    # ========================================================
    # METRICS
    # ========================================================

    def _calculate_rollback_pressure(self, events: List[Dict[str, Any]]) -> float:
        execution_events = [
            e for e in events
            if "EXECUTION" in str(e.get("event_type", ""))
            or "ACTION_ROUTER_EXECUTION" in str(e.get("event_type", ""))
        ]

        rollback_events = [
            e for e in events
            if "ROLLBACK" in str(e.get("event_type", ""))
        ]

        if not execution_events:
            return 0.0

        return round((len(rollback_events) / max(len(execution_events), 1)) * 100.0, 2)

    def _calculate_governance_drift(self, events: List[Dict[str, Any]]) -> float:
        drift_events = [
            e for e in events
            if any(
                marker in str(e.get("event_type", ""))
                for marker in [
                    "POLICY_BLOCKED",
                    "SANDBOX_BLOCKED",
                    "APPROVAL_REQUIRED",
                    "GOVERNANCE_DRIFT",
                    "BLOCKED",
                    "FAILED",
                ]
            )
        ]

        if not events:
            return 0.0

        return round((len(drift_events) / len(events)) * 100.0, 2)

    def _calculate_optimizer_confidence(self, events: List[Dict[str, Any]]) -> float:
        confidence_values = []

        for event in events:
            payload = event.get("payload") or {}

            if not isinstance(payload, dict):
                continue

            for key in [
                "confidence",
                "optimizer_confidence",
                "learned_confidence",
            ]:
                if key in payload:
                    try:
                        val = float(payload[key])
                        if val <= 1:
                            val *= 100.0
                        confidence_values.append(val)
                    except Exception:
                        pass

        if not confidence_values:
            return 75.0

        return round(sum(confidence_values) / len(confidence_values), 2)

    def _count_events(
        self,
        events: List[Dict[str, Any]],
        event_types: List[str],
    ) -> int:
        event_type_set = set(event_types)

        return len([
            e for e in events
            if str(e.get("event_type")) in event_type_set
        ])

    def _count_events_containing(
        self,
        events: List[Dict[str, Any]],
        markers: List[str],
    ) -> int:
        count = 0

        for event in events:
            blob = json.dumps(event, default=str).upper()

            if any(marker.upper() in blob for marker in markers):
                count += 1

        return count

    # ========================================================
    # PERSISTENCE
    # ========================================================

    def record_decision(self, decision: AutonomyGovernorDecision) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO autonomy_governor_decisions (
                    decision_id,
                    decision,
                    allowed,
                    autonomy_mode,
                    recommended_mode,
                    reason,
                    require_approval,
                    freeze_execution,
                    enter_lockdown,
                    throttle_factor,
                    rollback_pressure,
                    governance_drift,
                    optimizer_confidence,
                    queue_pressure,
                    connector_outages,
                    connector_degraded,
                    sandbox_blocks,
                    dead_letters,
                    escalation_spike,
                    legal_export_pressure,
                    findings_json,
                    metadata_json,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.decision,
                    int(decision.allowed),
                    decision.autonomy_mode,
                    decision.recommended_mode,
                    decision.reason,
                    int(decision.require_approval),
                    int(decision.freeze_execution),
                    int(decision.enter_lockdown),
                    float(decision.throttle_factor),
                    float(decision.rollback_pressure),
                    float(decision.governance_drift),
                    float(decision.optimizer_confidence),
                    int(decision.queue_pressure),
                    int(decision.connector_outages),
                    int(decision.connector_degraded),
                    int(decision.sandbox_blocks),
                    int(decision.dead_letters),
                    int(decision.escalation_spike),
                    int(decision.legal_export_pressure),
                    json.dumps(decision.findings, default=str),
                    json.dumps(decision.metadata, default=str),
                    decision.timestamp_ms,
                ),
            )
            conn.commit()

    def list_decisions(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM autonomy_governor_decisions
                ORDER BY created_at_ms DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        out = []

        for row in rows:
            item = dict(row)

            try:
                item["findings"] = json.loads(item.pop("findings_json") or "[]")
            except Exception:
                item["findings"] = []

            try:
                item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
            except Exception:
                item["metadata"] = {}

            out.append(item)

        return out

    # ========================================================
    # GOVERNANCE ACTION HELPERS
    # ========================================================

    def should_allow_execution(
        self,
        autonomy_mode: str = MODE_ASSISTED,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        decision = self.evaluate(
            autonomy_mode=autonomy_mode,
            tenant_id=tenant_id,
            context=context,
            persist=True,
        )

        return decision.allowed

    def should_freeze_execution(
        self,
        autonomy_mode: str = MODE_ASSISTED,
        tenant_id: Optional[str] = None,
    ) -> bool:
        decision = self.evaluate(
            autonomy_mode=autonomy_mode,
            tenant_id=tenant_id,
            persist=True,
        )

        return decision.freeze_execution

    def should_enter_lockdown(
        self,
        autonomy_mode: str = MODE_ASSISTED,
        tenant_id: Optional[str] = None,
    ) -> bool:
        decision = self.evaluate(
            autonomy_mode=autonomy_mode,
            tenant_id=tenant_id,
            persist=True,
        )

        return decision.enter_lockdown

    # ========================================================
    # MODE HELPERS
    # ========================================================

    def _downgrade_mode(self, mode: str) -> str:
        mode = str(mode or MODE_ASSISTED).upper()

        if mode == MODE_FULL_AUTONOMY:
            return MODE_SUPERVISED_AUTONOMY

        if mode == MODE_SUPERVISED_AUTONOMY:
            return MODE_ASSISTED

        if mode == MODE_ASSISTED:
            return MODE_MANUAL

        return MODE_MANUAL


# ============================================================
# SINGLETON HELPERS
# ============================================================

_DEFAULT_GOVERNOR: Optional[AutonomyGovernor] = None


def get_autonomy_governor(
    db_path: str = DEFAULT_DB_PATH,
    queue_db_path: str = DEFAULT_QUEUE_DB_PATH,
    queue: Optional[Any] = None,
) -> AutonomyGovernor:
    global _DEFAULT_GOVERNOR

    if _DEFAULT_GOVERNOR is None:
        _DEFAULT_GOVERNOR = AutonomyGovernor(
            db_path=db_path,
            queue_db_path=queue_db_path,
            queue=queue,
        )

    return _DEFAULT_GOVERNOR


def evaluate_autonomy(
    autonomy_mode: str = MODE_ASSISTED,
    tenant_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> AutonomyGovernorDecision:
    return get_autonomy_governor().evaluate(
        autonomy_mode=autonomy_mode,
        tenant_id=tenant_id,
        context=context,
    )