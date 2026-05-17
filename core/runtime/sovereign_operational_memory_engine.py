"""
core/runtime/sovereign_operational_memory_engine.py

Sovereign Operational Memory Engine.

Purpose:
- durable strategic operational memory
- mission survivability learning memory
- sovereignty outcome memory
- governance outcome memory
- runtime continuity memory
- strategic adaptation memory
- future AI coordination substrate

Architecture Rules:
- no Streamlit/session_state
- explicit dependency injection
- append-style memory records
- no destructive runtime actions
- service-owned memory state
- future-compatible with OSCAL / SSP / POA&M evidence exports
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


DEFAULT_TENANT = "default"

MEMORY_KIND_RUNTIME = "RUNTIME"
MEMORY_KIND_MISSION = "MISSION"
MEMORY_KIND_SOVEREIGNTY = "SOVEREIGNTY"
MEMORY_KIND_GOVERNANCE = "GOVERNANCE"
MEMORY_KIND_CONTINUITY = "CONTINUITY"
MEMORY_KIND_STRATEGY = "STRATEGY"
MEMORY_KIND_PREDICTION = "PREDICTION"
MEMORY_KIND_RECOVERY = "RECOVERY"
MEMORY_KIND_COMPLIANCE = "COMPLIANCE"

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL = "PARTIAL"
OUTCOME_FAILED = "FAILED"
OUTCOME_BLOCKED = "BLOCKED"
OUTCOME_UNKNOWN = "UNKNOWN"

SIGNIFICANCE_LOW = "LOW"
SIGNIFICANCE_MEDIUM = "MEDIUM"
SIGNIFICANCE_HIGH = "HIGH"
SIGNIFICANCE_CRITICAL = "CRITICAL"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class SovereignMemoryRecord:
    record_id: str
    tenant_id: str
    memory_kind: str
    subject: str
    outcome: str = OUTCOME_UNKNOWN
    significance: str = SIGNIFICANCE_MEDIUM
    summary: str = ""
    source: str = "sovereign_operational_memory_engine"
    evidence_refs: List[str] = field(default_factory=list)
    control_refs: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SovereignMemoryPattern:
    pattern_id: str
    tenant_id: str
    pattern_type: str
    significance: str
    confidence: float
    summary: str
    record_count: int = 0
    related_records: List[str] = field(default_factory=list)
    recommended_focus: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SovereignMemoryAssessment:
    assessment_id: str
    tenant_id: str
    memory_health: str
    confidence: float
    record_count: int
    pattern_count: int
    patterns: List[SovereignMemoryPattern] = field(default_factory=list)
    recommended_focus: List[str] = field(default_factory=list)
    compliance_memory_index: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["patterns"] = [
            p.to_dict() if hasattr(p, "to_dict") else p
            for p in self.patterns
        ]
        return data


class SovereignOperationalMemoryEngine:
    def __init__(
        self,
        *,
        autonomous_mission_continuity_engine: Any = None,
        runtime_cognition_orchestrator: Any = None,
        autonomous_runtime_intelligence_engine: Any = None,
        adaptive_operational_strategy_engine: Any = None,
        sovereign_operational_reasoning_engine: Any = None,
        predictive_runtime_stability_engine: Any = None,
        runtime_fabric_learning_engine: Any = None,
        runtime_recovery_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
        self.event_bus = event_bus

        self.autonomous_mission_continuity_engine = (
            autonomous_mission_continuity_engine
            or getattr(storage, "autonomous_mission_continuity_engine", None)
        )
        self.runtime_cognition_orchestrator = (
            runtime_cognition_orchestrator
            or getattr(storage, "runtime_cognition_orchestrator", None)
        )
        self.autonomous_runtime_intelligence_engine = (
            autonomous_runtime_intelligence_engine
            or getattr(storage, "autonomous_runtime_intelligence_engine", None)
        )
        self.adaptive_operational_strategy_engine = (
            adaptive_operational_strategy_engine
            or getattr(storage, "adaptive_operational_strategy_engine", None)
        )
        self.sovereign_operational_reasoning_engine = (
            sovereign_operational_reasoning_engine
            or getattr(storage, "sovereign_operational_reasoning_engine", None)
        )
        self.predictive_runtime_stability_engine = (
            predictive_runtime_stability_engine
            or getattr(storage, "predictive_runtime_stability_engine", None)
        )
        self.runtime_fabric_learning_engine = (
            runtime_fabric_learning_engine
            or getattr(storage, "runtime_fabric_learning_engine", None)
        )
        self.runtime_recovery_manager = (
            runtime_recovery_manager
            or getattr(storage, "runtime_recovery_manager", None)
        )

        self._records: List[SovereignMemoryRecord] = []
        self._patterns: List[SovereignMemoryPattern] = []
        self._assessments: List[SovereignMemoryAssessment] = []

        self._register_handlers()

    # ========================================================
    # MEMORY RECORDING
    # ========================================================

    def remember(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        memory_kind: str,
        subject: str,
        outcome: str = OUTCOME_UNKNOWN,
        significance: str = SIGNIFICANCE_MEDIUM,
        summary: str = "",
        source: str = "external",
        evidence_refs: Optional[List[str]] = None,
        control_refs: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SovereignMemoryRecord:
        record = SovereignMemoryRecord(
            record_id=f"SOV-MEM-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            memory_kind=memory_kind,
            subject=subject,
            outcome=outcome,
            significance=significance,
            summary=summary,
            source=source,
            evidence_refs=evidence_refs or [],
            control_refs=control_refs or [],
            tags=tags or [],
            metadata=metadata or {},
        )

        self._records.append(record)
        self._records = self._records[-10000:]

        self._emit(
            "SOVEREIGN_OPERATIONAL_MEMORY_RECORDED",
            record.to_dict(),
        )

        return record

    def ingest_current_state(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        created: List[SovereignMemoryRecord] = []

        created.extend(
            self._ingest_mission_continuity(
                tenant_id=tenant_id,
            )
        )

        created.extend(
            self._ingest_runtime_intelligence(
                tenant_id=tenant_id,
            )
        )

        created.extend(
            self._ingest_cognition_orchestration(
                tenant_id=tenant_id,
            )
        )

        created.extend(
            self._ingest_strategy_state(
                tenant_id=tenant_id,
            )
        )

        created.extend(
            self._ingest_reasoning_state(
                tenant_id=tenant_id,
            )
        )

        created.extend(
            self._ingest_predictive_state(
                tenant_id=tenant_id,
            )
        )

        payload = {
            "ok": True,
            "tenant_id": tenant_id,
            "created_records": len(created),
            "record_ids": [
                r.record_id for r in created
            ],
        }

        self._emit(
            "SOVEREIGN_OPERATIONAL_MEMORY_INGESTED",
            payload,
        )

        return payload

    # ========================================================
    # INGEST HELPERS
    # ========================================================

    def _ingest_mission_continuity(
        self,
        *,
        tenant_id: str,
    ) -> List[SovereignMemoryRecord]:
        if self.autonomous_mission_continuity_engine is None:
            return []

        records = []

        try:
            plans = self.autonomous_mission_continuity_engine.list_plans()
        except Exception:
            return []

        for plan in plans[-25:]:
            records.append(
                self.remember(
                    tenant_id=tenant_id,
                    memory_kind=MEMORY_KIND_MISSION,
                    subject=plan.get("mission_id", "runtime_fabric"),
                    outcome=self._outcome_from_status(
                        plan.get("mission_status")
                    ),
                    significance=self._significance_from_risk(
                        plan.get("continuity_risk")
                    ),
                    summary=(
                        f"Mission continuity status={plan.get('mission_status')} "
                        f"risk={plan.get('continuity_risk')} "
                        f"score={plan.get('continuity_score')}."
                    ),
                    source="autonomous_mission_continuity_engine",
                    tags=[
                        "mission_continuity",
                        "survivability",
                    ],
                    metadata=plan,
                )
            )

        return records

    def _ingest_runtime_intelligence(
        self,
        *,
        tenant_id: str,
    ) -> List[SovereignMemoryRecord]:
        if self.autonomous_runtime_intelligence_engine is None:
            return []

        try:
            snapshot = self.autonomous_runtime_intelligence_engine.get_runtime_snapshot(
                tenant_id
            )
        except Exception:
            snapshot = None

        if snapshot is None:
            return []

        data = snapshot.to_dict() if hasattr(snapshot, "to_dict") else dict(snapshot.__dict__)

        return [
            self.remember(
                tenant_id=tenant_id,
                memory_kind=MEMORY_KIND_RUNTIME,
                subject="runtime_intelligence_snapshot",
                outcome=OUTCOME_UNKNOWN,
                significance=SIGNIFICANCE_MEDIUM,
                summary="Captured unified sovereign runtime intelligence snapshot.",
                source="autonomous_runtime_intelligence_engine",
                tags=[
                    "runtime_intelligence",
                    "synthesis",
                ],
                metadata=data,
            )
        ]

    def _ingest_cognition_orchestration(
        self,
        *,
        tenant_id: str,
    ) -> List[SovereignMemoryRecord]:
        if self.runtime_cognition_orchestrator is None:
            return []

        try:
            plans = self.runtime_cognition_orchestrator.list_plans(
                limit=25,
                tenant_id=tenant_id,
            )
        except Exception:
            return []

        records = []

        for plan in plans:
            records.append(
                self.remember(
                    tenant_id=tenant_id,
                    memory_kind=MEMORY_KIND_RUNTIME,
                    subject=plan.get("trigger", "cognition_plan"),
                    outcome=self._outcome_from_plan_status(
                        plan.get("status")
                    ),
                    significance=SIGNIFICANCE_HIGH
                    if plan.get("priority") in {"HIGH", "CRITICAL"}
                    else SIGNIFICANCE_MEDIUM,
                    summary=(
                        f"Cognition plan {plan.get('plan_id')} "
                        f"status={plan.get('status')} "
                        f"mode={plan.get('mode')}."
                    ),
                    source="runtime_cognition_orchestrator",
                    tags=[
                        "cognition_orchestration",
                        "runtime_plan",
                    ],
                    metadata=plan,
                )
            )

        return records

    def _ingest_strategy_state(
        self,
        *,
        tenant_id: str,
    ) -> List[SovereignMemoryRecord]:
        if self.adaptive_operational_strategy_engine is None:
            return []

        try:
            assessments = self.adaptive_operational_strategy_engine.list_assessments(
                limit=10
            )
        except Exception:
            return []

        records = []

        for item in assessments:
            records.append(
                self.remember(
                    tenant_id=tenant_id,
                    memory_kind=MEMORY_KIND_STRATEGY,
                    subject=item.get("strategy_state", "strategy_assessment"),
                    outcome=self._outcome_from_state(
                        item.get("strategy_state")
                    ),
                    significance=self._significance_from_state(
                        item.get("strategy_state")
                    ),
                    summary=item.get(
                        "summary",
                        "Adaptive operational strategy assessment recorded.",
                    ),
                    source="adaptive_operational_strategy_engine",
                    tags=[
                        "adaptive_strategy",
                        "strategy_evolution",
                    ],
                    metadata=item,
                )
            )

        return records

    def _ingest_reasoning_state(
        self,
        *,
        tenant_id: str,
    ) -> List[SovereignMemoryRecord]:
        if self.sovereign_operational_reasoning_engine is None:
            return []

        try:
            assessments = self.sovereign_operational_reasoning_engine.list_assessments(
                limit=10
            )
        except Exception:
            return []

        records = []

        for item in assessments:
            records.append(
                self.remember(
                    tenant_id=tenant_id,
                    memory_kind=MEMORY_KIND_SOVEREIGNTY,
                    subject=item.get("reasoning_state", "sovereign_reasoning"),
                    outcome=self._outcome_from_state(
                        item.get("reasoning_state")
                    ),
                    significance=self._significance_from_state(
                        item.get("reasoning_state")
                    ),
                    summary=item.get(
                        "summary",
                        "Sovereign operational reasoning assessment recorded.",
                    ),
                    source="sovereign_operational_reasoning_engine",
                    tags=[
                        "sovereign_reasoning",
                        "mission_reasoning",
                    ],
                    metadata=item,
                )
            )

        return records

    def _ingest_predictive_state(
        self,
        *,
        tenant_id: str,
    ) -> List[SovereignMemoryRecord]:
        if self.predictive_runtime_stability_engine is None:
            return []

        try:
            assessments = self.predictive_runtime_stability_engine.list_assessments(
                limit=10
            )
        except Exception:
            return []

        records = []

        for item in assessments:
            records.append(
                self.remember(
                    tenant_id=tenant_id,
                    memory_kind=MEMORY_KIND_PREDICTION,
                    subject=item.get("predictive_state", "predictive_runtime_state"),
                    outcome=self._outcome_from_state(
                        item.get("predictive_state")
                    ),
                    significance=self._significance_from_state(
                        item.get("predictive_state")
                    ),
                    summary=(
                        f"Predictive runtime state={item.get('predictive_state')} "
                        f"stability={item.get('stability_score')}."
                    ),
                    source="predictive_runtime_stability_engine",
                    tags=[
                        "prediction",
                        "runtime_stability",
                    ],
                    metadata=item,
                )
            )

        return records

    # ========================================================
    # ASSESSMENT
    # ========================================================

    def assess_memory(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> SovereignMemoryAssessment:
        records = [
            r for r in self._records
            if r.tenant_id == tenant_id
        ]

        patterns = self._derive_patterns(
            tenant_id=tenant_id,
            records=records,
        )

        compliance_index = self._build_compliance_memory_index(
            tenant_id=tenant_id,
            records=records,
        )

        health = self._memory_health(
            records=records,
            patterns=patterns,
        )

        confidence = self._confidence(
            records=records,
            patterns=patterns,
        )

        focus = self._recommended_focus(
            patterns=patterns,
            compliance_index=compliance_index,
        )

        assessment = SovereignMemoryAssessment(
            assessment_id=f"SOV-MEM-ASSESS-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            memory_health=health,
            confidence=confidence,
            record_count=len(records),
            pattern_count=len(patterns),
            patterns=patterns,
            recommended_focus=focus,
            compliance_memory_index=compliance_index,
        )

        self._patterns.extend(patterns)
        self._patterns = self._patterns[-1000:]

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._emit(
            "SOVEREIGN_OPERATIONAL_MEMORY_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    # ========================================================
    # PATTERNS
    # ========================================================

    def _derive_patterns(
        self,
        *,
        tenant_id: str,
        records: List[SovereignMemoryRecord],
    ) -> List[SovereignMemoryPattern]:
        patterns: List[SovereignMemoryPattern] = []

        patterns.extend(
            self._failure_patterns(
                tenant_id=tenant_id,
                records=records,
            )
        )

        patterns.extend(
            self._continuity_patterns(
                tenant_id=tenant_id,
                records=records,
            )
        )

        patterns.extend(
            self._governance_patterns(
                tenant_id=tenant_id,
                records=records,
            )
        )

        return patterns

    def _failure_patterns(
        self,
        *,
        tenant_id: str,
        records: List[SovereignMemoryRecord],
    ) -> List[SovereignMemoryPattern]:
        bad = [
            r for r in records
            if r.outcome in {OUTCOME_FAILED, OUTCOME_BLOCKED}
        ]

        if len(bad) < 3:
            return []

        return [
            SovereignMemoryPattern(
                pattern_id=f"SOV-MEM-PAT-{uuid.uuid4().hex[:12].upper()}",
                tenant_id=tenant_id,
                pattern_type="RECURRING_OPERATIONAL_FAILURE",
                significance=SIGNIFICANCE_HIGH,
                confidence=min(0.95, 0.5 + len(bad) * 0.05),
                summary="Recurring operational failure or blocked outcomes detected.",
                record_count=len(bad),
                related_records=[
                    r.record_id for r in bad[-20:]
                ],
                recommended_focus=[
                    "recovery",
                    "governance",
                    "continuity",
                ],
            )
        ]

    def _continuity_patterns(
        self,
        *,
        tenant_id: str,
        records: List[SovereignMemoryRecord],
    ) -> List[SovereignMemoryPattern]:
        continuity = [
            r for r in records
            if r.memory_kind in {
                MEMORY_KIND_CONTINUITY,
                MEMORY_KIND_MISSION,
            }
            and r.significance in {
                SIGNIFICANCE_HIGH,
                SIGNIFICANCE_CRITICAL,
            }
        ]

        if len(continuity) < 2:
            return []

        return [
            SovereignMemoryPattern(
                pattern_id=f"SOV-MEM-PAT-{uuid.uuid4().hex[:12].upper()}",
                tenant_id=tenant_id,
                pattern_type="MISSION_CONTINUITY_PRESSURE",
                significance=SIGNIFICANCE_HIGH,
                confidence=min(0.9, 0.45 + len(continuity) * 0.08),
                summary="Mission continuity pressure appears repeatedly in memory.",
                record_count=len(continuity),
                related_records=[
                    r.record_id for r in continuity[-20:]
                ],
                recommended_focus=[
                    "mission_survivability",
                    "runtime_stabilization",
                ],
            )
        ]

    def _governance_patterns(
        self,
        *,
        tenant_id: str,
        records: List[SovereignMemoryRecord],
    ) -> List[SovereignMemoryPattern]:
        governance = [
            r for r in records
            if r.memory_kind == MEMORY_KIND_GOVERNANCE
            or "governance" in {
                str(t).lower() for t in r.tags
            }
        ]

        if len(governance) < 3:
            return []

        return [
            SovereignMemoryPattern(
                pattern_id=f"SOV-MEM-PAT-{uuid.uuid4().hex[:12].upper()}",
                tenant_id=tenant_id,
                pattern_type="GOVERNANCE_RECURRING_PRESSURE",
                significance=SIGNIFICANCE_MEDIUM,
                confidence=min(0.85, 0.4 + len(governance) * 0.05),
                summary="Governance pressure appears repeatedly in operational memory.",
                record_count=len(governance),
                related_records=[
                    r.record_id for r in governance[-20:]
                ],
                recommended_focus=[
                    "policy_review",
                    "approval_workflow",
                    "fedramp_evidence",
                ],
            )
        ]

    # ========================================================
    # COMPLIANCE INDEX
    # ========================================================

    def _build_compliance_memory_index(
        self,
        *,
        tenant_id: str,
        records: List[SovereignMemoryRecord],
    ) -> Dict[str, Any]:
        index = {
            "tenant_id": tenant_id,
            "record_count": len(records),
            "control_refs": {},
            "evidence_refs": {},
            "memory_kinds": {},
            "fedramp_candidate_records": 0,
            "cmmc_candidate_records": 0,
            "poam_candidate_records": 0,
        }

        for record in records:
            index["memory_kinds"][record.memory_kind] = (
                index["memory_kinds"].get(record.memory_kind, 0) + 1
            )

            for control in record.control_refs:
                index["control_refs"][control] = (
                    index["control_refs"].get(control, 0) + 1
                )

            for evidence in record.evidence_refs:
                index["evidence_refs"][evidence] = (
                    index["evidence_refs"].get(evidence, 0) + 1
                )

            tags = {str(t).lower() for t in record.tags}

            if tags.intersection(
                {"fedramp", "oscal", "ssp", "control", "audit"}
            ):
                index["fedramp_candidate_records"] += 1

            if tags.intersection(
                {"cmmc", "cui", "nist800171"}
            ):
                index["cmmc_candidate_records"] += 1

            if record.outcome in {OUTCOME_FAILED, OUTCOME_BLOCKED}:
                index["poam_candidate_records"] += 1

        return index

    # ========================================================
    # SCORING
    # ========================================================

    def _memory_health(
        self,
        *,
        records: List[SovereignMemoryRecord],
        patterns: List[SovereignMemoryPattern],
    ) -> str:
        if not records:
            return "EMPTY"

        if any(p.significance == SIGNIFICANCE_CRITICAL for p in patterns):
            return SIGNIFICANCE_CRITICAL

        if len(patterns) >= 3:
            return SIGNIFICANCE_HIGH

        if len(patterns) >= 1:
            return SIGNIFICANCE_MEDIUM

        return SIGNIFICANCE_LOW

    def _confidence(
        self,
        *,
        records: List[SovereignMemoryRecord],
        patterns: List[SovereignMemoryPattern],
    ) -> float:
        record_component = min(len(records) * 0.01, 0.45)
        pattern_component = min(len(patterns) * 0.08, 0.30)

        return round(
            max(
                0.05,
                min(0.95, 0.25 + record_component + pattern_component),
            ),
            3,
        )

    def _recommended_focus(
        self,
        *,
        patterns: List[SovereignMemoryPattern],
        compliance_index: Dict[str, Any],
    ) -> List[str]:
        focus = set()

        for pattern in patterns:
            focus.update(pattern.recommended_focus)

        if compliance_index.get("poam_candidate_records", 0) > 0:
            focus.add("poam_review")

        if compliance_index.get("fedramp_candidate_records", 0) > 0:
            focus.add("fedramp_evidence")

        if compliance_index.get("cmmc_candidate_records", 0) > 0:
            focus.add("cmmc_alignment")

        return sorted(focus)

    # ========================================================
    # STATUS / READS
    # ========================================================

    def memory_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        tenant_records = [
            r for r in self._records
            if r.tenant_id == tenant_id
        ]

        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "tenant_id": tenant_id,
            "record_count": len(tenant_records),
            "pattern_count": len(self._patterns),
            "assessment_count": len(self._assessments),
            "latest_assessment": latest,
        }

    def list_records(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 100,
        memory_kind: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows = self._records

        if tenant_id:
            rows = [
                r for r in rows
                if r.tenant_id == tenant_id
            ]

        if memory_kind:
            rows = [
                r for r in rows
                if r.memory_kind == memory_kind
            ]

        rows = sorted(
            rows,
            key=lambda r: r.created_at_ms,
            reverse=True,
        )

        return [
            r.to_dict() for r in rows[:limit]
        ]

    def list_patterns(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = self._patterns

        if tenant_id:
            rows = [
                p for p in rows
                if p.tenant_id == tenant_id
            ]

        rows = sorted(
            rows,
            key=lambda p: p.created_at_ms,
            reverse=True,
        )

        return [
            p.to_dict() for p in rows[:limit]
        ]

    def list_assessments(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = self._assessments

        if tenant_id:
            rows = [
                a for a in rows
                if a.tenant_id == tenant_id
            ]

        rows = sorted(
            rows,
            key=lambda a: a.created_at_ms,
            reverse=True,
        )

        return [
            a.to_dict() for a in rows[:limit]
        ]

    # ========================================================
    # CLASSIFICATION HELPERS
    # ========================================================

    def _outcome_from_plan_status(
        self,
        status: Any,
    ) -> str:
        status = str(status or "").upper()

        if status in {"COMPLETED", "STABLE"}:
            return OUTCOME_SUCCESS

        if status in {"ACTIVE", "DEGRADED", "PARTIAL"}:
            return OUTCOME_PARTIAL

        if status in {"FAILED", "FAILING", "CRITICAL"}:
            return OUTCOME_FAILED

        if status in {"BLOCKED", "RATE_LIMITED"}:
            return OUTCOME_BLOCKED

        return OUTCOME_UNKNOWN

    def _outcome_from_status(
        self,
        status: Any,
    ) -> str:
        status = str(status or "").upper()

        if status in {"STABLE", "HEALTHY", "LOW"}:
            return OUTCOME_SUCCESS

        if status in {"DEGRADED", "MEDIUM", "WATCH"}:
            return OUTCOME_PARTIAL

        if status in {"CRITICAL", "FAILING", "HIGH"}:
            return OUTCOME_FAILED

        return OUTCOME_UNKNOWN

    def _outcome_from_state(
        self,
        state: Any,
    ) -> str:
        state = str(state or "").upper()

        if state in {"STABLE", "LOW", "HEALTHY"}:
            return OUTCOME_SUCCESS

        if state in {"WATCH", "MEDIUM", "DEGRADED", "DRIFTING"}:
            return OUTCOME_PARTIAL

        if state in {"HIGH", "CRITICAL", "UNSTABLE", "FAILING"}:
            return OUTCOME_FAILED

        return OUTCOME_UNKNOWN

    def _significance_from_risk(
        self,
        risk: Any,
    ) -> str:
        risk = str(risk or "").upper()

        if risk in {"CRITICAL", "FAILING"}:
            return SIGNIFICANCE_CRITICAL

        if risk in {"HIGH", "DEGRADED"}:
            return SIGNIFICANCE_HIGH

        if risk in {"MEDIUM", "WATCH"}:
            return SIGNIFICANCE_MEDIUM

        return SIGNIFICANCE_LOW

    def _significance_from_state(
        self,
        state: Any,
    ) -> str:
        state = str(state or "").upper()

        if state in {"CRITICAL", "FAILING"}:
            return SIGNIFICANCE_CRITICAL

        if state in {"HIGH", "UNSTABLE", "DEGRADED", "DRIFTING"}:
            return SIGNIFICANCE_HIGH

        if state in {"WATCH", "MEDIUM"}:
            return SIGNIFICANCE_MEDIUM

        return SIGNIFICANCE_LOW

    # ========================================================
    # EVENTS
    # ========================================================

    def _register_handlers(self) -> None:
        if self.event_bus is None:
            return

        for event_type in [
            "MISSION_CONTINUITY_PLAN_UPDATED",
            "RUNTIME_INTELLIGENCE_UPDATED",
            "RUNTIME_COGNITION_PLAN_COMPLETED",
            "SOVEREIGN_OPERATIONAL_REASONING_ASSESSED",
            "ADAPTIVE_OPERATIONAL_STRATEGY_ASSESSED",
            "PREDICTIVE_RUNTIME_STABILITY_ASSESSED",
            "RECOVERY_TRIGGERED",
            "ROLLBACK_TRIGGERED",
            "GOVERNANCE_OVERRIDE",
        ]:
            try:
                self.event_bus.subscribe(
                    event_type,
                    self._handle_event,
                )
            except Exception:
                pass

    def _handle_event(
        self,
        event: Dict[str, Any],
    ) -> None:
        tenant_id = (
            event.get("tenant_id")
            or event.get("payload", {}).get("tenant_id")
            or DEFAULT_TENANT
        )

        event_type = str(
            event.get("event_type")
            or event.get("type")
            or "runtime_event"
        )

        self.remember(
            tenant_id=tenant_id,
            memory_kind=self._memory_kind_for_event(event_type),
            subject=event_type,
            outcome=OUTCOME_UNKNOWN,
            significance=SIGNIFICANCE_MEDIUM,
            summary=f"Runtime event captured in sovereign operational memory: {event_type}",
            source="event_bus",
            tags=[
                "event_memory",
                event_type.lower(),
            ],
            metadata=event,
        )

    def _memory_kind_for_event(
        self,
        event_type: str,
    ) -> str:
        event_type = str(event_type or "").upper()

        if "MISSION" in event_type or "CONTINUITY" in event_type:
            return MEMORY_KIND_MISSION

        if "SOVEREIGN" in event_type:
            return MEMORY_KIND_SOVEREIGNTY

        if "GOVERNANCE" in event_type:
            return MEMORY_KIND_GOVERNANCE

        if "PREDICTIVE" in event_type:
            return MEMORY_KIND_PREDICTION

        if "RECOVERY" in event_type or "ROLLBACK" in event_type:
            return MEMORY_KIND_RECOVERY

        return MEMORY_KIND_RUNTIME

    def _emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                source="sovereign_operational_memory_engine",
                severity=payload.get("significance") or "INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_SOVEREIGN_OPERATIONAL_MEMORY_ENGINE: Optional[
    SovereignOperationalMemoryEngine
] = None


def get_sovereign_operational_memory_engine(
    *,
    autonomous_mission_continuity_engine: Any = None,
    runtime_cognition_orchestrator: Any = None,
    autonomous_runtime_intelligence_engine: Any = None,
    adaptive_operational_strategy_engine: Any = None,
    sovereign_operational_reasoning_engine: Any = None,
    predictive_runtime_stability_engine: Any = None,
    runtime_fabric_learning_engine: Any = None,
    runtime_recovery_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> SovereignOperationalMemoryEngine:
    global _DEFAULT_SOVEREIGN_OPERATIONAL_MEMORY_ENGINE

    if reset or _DEFAULT_SOVEREIGN_OPERATIONAL_MEMORY_ENGINE is None:
        _DEFAULT_SOVEREIGN_OPERATIONAL_MEMORY_ENGINE = (
            SovereignOperationalMemoryEngine(
                autonomous_mission_continuity_engine=autonomous_mission_continuity_engine,
                runtime_cognition_orchestrator=runtime_cognition_orchestrator,
                autonomous_runtime_intelligence_engine=autonomous_runtime_intelligence_engine,
                adaptive_operational_strategy_engine=adaptive_operational_strategy_engine,
                sovereign_operational_reasoning_engine=sovereign_operational_reasoning_engine,
                predictive_runtime_stability_engine=predictive_runtime_stability_engine,
                runtime_fabric_learning_engine=runtime_fabric_learning_engine,
                runtime_recovery_manager=runtime_recovery_manager,
                storage=storage,
                event_bus=event_bus,
            )
        )

    return _DEFAULT_SOVEREIGN_OPERATIONAL_MEMORY_ENGINE