"""
core/runtime/sovereign_runtime_visual_replay_engine.py

Sovereign Runtime Visual Replay Engine

Replayable sovereign cognition visualization layer.

This subsystem reconstructs:
- runtime cognition history
- governance history
- mission simulation history
- operational simulation history
- survivability evolution
- recovery evolution
- failover propagation
- autonomy adaptation evolution
- strategic cognition evolution

IMPORTANT:
This subsystem DOES NOT:
- mutate runtime state
- trigger autonomous execution
- execute containment
- execute failovers

It ONLY:
- reconstructs replay timelines
- generates replay frames
- builds cognition playback streams
- records replay lineage/evidence
- provides explainable replay intelligence
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_runtime_visual_replay_engine"
)

REPLAY_STATE_IDLE = "IDLE"
REPLAY_STATE_RUNNING = "RUNNING"
REPLAY_STATE_PAUSED = "PAUSED"
REPLAY_STATE_COMPLETED = "COMPLETED"

FRAME_TYPE_RUNTIME = "RUNTIME"
FRAME_TYPE_GOVERNANCE = "GOVERNANCE"
FRAME_TYPE_SIMULATION = "SIMULATION"
FRAME_TYPE_MISSION = "MISSION"
FRAME_TYPE_AUTONOMY = "AUTONOMY"
FRAME_TYPE_FAILOVER = "FAILOVER"
FRAME_TYPE_RECOVERY = "RECOVERY"

PLAYBACK_MODE_TIMELINE = "TIMELINE"
PLAYBACK_MODE_BRANCHING = "BRANCHING"
PLAYBACK_MODE_MISSION = "MISSION"
PLAYBACK_MODE_GOVERNANCE = "GOVERNANCE"

DEFAULT_REPLAY_SPEED = 1.0


class ReplaySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReplayDomain(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    AUTONOMY = "AUTONOMY"
    RESILIENCE = "RESILIENCE"
    TELEMETRY = "TELEMETRY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    MISSION = "MISSION"
    SIMULATION = "SIMULATION"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ReplayFrame:
    """
    Single replay visualization frame.
    """

    frame_id: str

    frame_index: int

    frame_type: str

    title: str
    summary: str

    replay_state: str

    severity: str
    confidence: float

    timeline_position: float

    governance_pressure_score: float = 0.0
    survivability_score: float = 100.0
    operational_pressure_score: float = 0.0
    mission_risk_score: float = 0.0

    mission_state: Optional[str] = None
    simulation_state: Optional[str] = None

    branch_id: Optional[str] = None
    branch_name: Optional[str] = None

    source_engine: Optional[str] = None

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class ReplayTimeline:
    """
    Replay timeline.
    """

    replay_id: str

    replay_name: str

    playback_mode: str

    replay_state: str

    total_frames: int

    replay_speed: float

    replay_duration_ms: int

    mission_id: Optional[str] = None

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    frames: List[ReplayFrame] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class SovereignRuntimeReplayAssessment:
    """
    Replay assessment.
    """

    assessment_id: str

    replay_id: str

    replay_state: str

    playback_mode: str

    replay_success_probability: float

    explainability_score: float

    replay_integrity_score: float

    operational_visibility_score: float

    governance_visibility_score: float

    mission_visibility_score: float

    branch_visibility_score: float

    selected_frame_id: Optional[str]

    severity: str

    confidence: float

    total_frames: int

    mission_id: Optional[str]

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    replay_timeline: ReplayTimeline

    recommended_actions: List[
        Dict[str, Any]
    ]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class SovereignRuntimeReplaySnapshot:
    engine_name: str

    total_replays_created: int

    total_frames_processed: int

    last_replay_id: Optional[str]

    last_replay_state: Optional[str]

    last_updated_ms: int


class SovereignRuntimeVisualReplayEngine:
    """
    Replayable sovereign cognition engine.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._replay_count = 0

        self._frame_count = 0

        self._assessments: List[
            SovereignRuntimeReplayAssessment
        ] = []

    # ========================================================
    # PUBLIC API
    # ========================================================

    def build_replay(
        self,
        replay_events: Sequence[
            Dict[str, Any]
        ],
        *,
        replay_name: str = (
            "Runtime Replay"
        ),
        playback_mode: str = (
            PLAYBACK_MODE_TIMELINE
        ),
        replay_speed: float = (
            DEFAULT_REPLAY_SPEED
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignRuntimeReplayAssessment
    ):
        """
        Build sovereign replay timeline.
        """

        replay_id = str(uuid.uuid4())

        frames = self._build_frames(
            replay_events,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=(
                correlation_id
            ),
        )

        self._frame_count += len(frames)

        replay_duration_ms = (
            len(frames) * 1000
        )

        timeline = ReplayTimeline(
            replay_id=replay_id,
            replay_name=replay_name,
            playback_mode=(
                playback_mode
            ),
            replay_state=(
                REPLAY_STATE_COMPLETED
            ),
            total_frames=len(frames),
            replay_speed=max(
                0.1,
                float(replay_speed),
            ),
            replay_duration_ms=(
                replay_duration_ms
            ),
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=(
                correlation_id
            ),
            frames=frames,
        )

        replay_success_probability = (
            self
            ._replay_success_probability(
                frames
            )
        )

        explainability_score = (
            self._explainability_score(
                frames
            )
        )

        replay_integrity_score = (
            self
            ._replay_integrity_score(
                frames
            )
        )

        operational_visibility = (
            self
            ._operational_visibility_score(
                frames
            )
        )

        governance_visibility = (
            self
            ._governance_visibility_score(
                frames
            )
        )

        mission_visibility = (
            self
            ._mission_visibility_score(
                frames
            )
        )

        branch_visibility = (
            self
            ._branch_visibility_score(
                frames
            )
        )

        selected_frame = (
            frames[-1]
            if frames
            else None
        )

        assessment = (
            SovereignRuntimeReplayAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                replay_id=replay_id,
                replay_state=(
                    REPLAY_STATE_COMPLETED
                ),
                playback_mode=(
                    playback_mode
                ),
                replay_success_probability=(
                    replay_success_probability
                ),
                explainability_score=(
                    explainability_score
                ),
                replay_integrity_score=(
                    replay_integrity_score
                ),
                operational_visibility_score=(
                    operational_visibility
                ),
                governance_visibility_score=(
                    governance_visibility
                ),
                mission_visibility_score=(
                    mission_visibility
                ),
                branch_visibility_score=(
                    branch_visibility
                ),
                selected_frame_id=(
                    selected_frame.frame_id
                    if selected_frame
                    else None
                ),
                severity=(
                    selected_frame.severity
                    if selected_frame
                    else ReplaySeverity
                    .INFO.value
                ),
                confidence=(
                    selected_frame.confidence
                    if selected_frame
                    else 1.0
                ),
                total_frames=len(frames),
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                replay_timeline=timeline,
                recommended_actions=(
                    self
                    ._recommended_actions(
                        frames
                    )
                ),
                rationale=self._build_rationale(
                    total_frames=len(
                        frames
                    ),
                    replay_success_probability=(
                        replay_success_probability
                    ),
                    explainability_score=(
                        explainability_score
                    ),
                    replay_integrity_score=(
                        replay_integrity_score
                    ),
                    playback_mode=(
                        playback_mode
                    ),
                ),
                metadata={
                    "frame_types": sorted(
                        {
                            frame.frame_type
                            for frame in frames
                        }
                    ),
                },
            )
        )

        self._record_assessment(
            assessment,
            context=context,
        )

        self._replay_count += 1

        return assessment

    def submit(
        self,
        replay_events: Sequence[
            Dict[str, Any]
        ],
        *,
        replay_name: str = (
            "Runtime Replay"
        ),
        playback_mode: str = (
            PLAYBACK_MODE_TIMELINE
        ),
        replay_speed: float = (
            DEFAULT_REPLAY_SPEED
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignRuntimeReplayAssessment
    ):

        return self.build_replay(
            replay_events,
            replay_name=replay_name,
            playback_mode=(
                playback_mode
            ),
            replay_speed=replay_speed,
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=(
                correlation_id
            ),
            context=context,
        )

    def get_recent_replays(
        self,
        *,
        limit: int = 25,
    ) -> List[
        SovereignRuntimeReplayAssessment
    ]:

        limit = max(1, int(limit))

        return list(
            reversed(
                self._assessments[-limit:]
            )
        )

    def snapshot(
        self,
    ) -> (
        SovereignRuntimeReplaySnapshot
    ):

        latest = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            SovereignRuntimeReplaySnapshot(
                engine_name=self.engine_name,
                total_replays_created=(
                    self._replay_count
                ),
                total_frames_processed=(
                    self._frame_count
                ),
                last_replay_id=(
                    latest.replay_id
                    if latest
                    else None
                ),
                last_replay_state=(
                    latest.replay_state
                    if latest
                    else None
                ),
                last_updated_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # ========================================================
    # FRAME BUILDING
    # ========================================================

    def _build_frames(
        self,
        replay_events: Sequence[
            Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> List[ReplayFrame]:

        frames: List[
            ReplayFrame
        ] = []

        total = max(
            1,
            len(replay_events),
        )

        for index, item in enumerate(
            replay_events
        ):

            frame_type = str(
                item.get(
                    "frame_type",
                    FRAME_TYPE_RUNTIME,
                )
            ).upper()

            frames.append(
                ReplayFrame(
                    frame_id=str(
                        uuid.uuid4()
                    ),
                    frame_index=index,
                    frame_type=frame_type,
                    title=str(
                        item.get(
                            "title",
                            f"Replay Frame {index}",
                        )
                    ),
                    summary=str(
                        item.get(
                            "summary",
                            "",
                        )
                    ),
                    replay_state=(
                        REPLAY_STATE_COMPLETED
                    ),
                    severity=self._safe_severity(
                        item.get(
                            "severity"
                        )
                    ),
                    confidence=(
                        self
                        ._clamp_probability(
                            item.get(
                                "confidence",
                                1.0,
                            )
                        )
                    ),
                    timeline_position=(
                        index / total
                    ),
                    governance_pressure_score=(
                        self._clamp_score(
                            item.get(
                                "governance_pressure_score",
                                0.0,
                            )
                        )
                    ),
                    survivability_score=(
                        self._clamp_score(
                            item.get(
                                "survivability_score",
                                100.0,
                            )
                        )
                    ),
                    operational_pressure_score=(
                        self._clamp_score(
                            item.get(
                                "operational_pressure_score",
                                0.0,
                            )
                        )
                    ),
                    mission_risk_score=(
                        self._clamp_score(
                            item.get(
                                "mission_risk_score",
                                0.0,
                            )
                        )
                    ),
                    mission_state=item.get(
                        "mission_state"
                    ),
                    simulation_state=item.get(
                        "simulation_state"
                    ),
                    branch_id=item.get(
                        "branch_id"
                    ),
                    branch_name=item.get(
                        "branch_name"
                    ),
                    source_engine=item.get(
                        "source_engine"
                    ),
                    tenant_id=(
                        tenant_id
                        or item.get(
                            "tenant_id"
                        )
                    ),
                    case_id=(
                        case_id
                        or item.get(
                            "case_id"
                        )
                    ),
                    correlation_id=(
                        correlation_id
                        or item.get(
                            "correlation_id"
                        )
                    ),
                    metadata=dict(
                        item.get(
                            "metadata",
                            {},
                        )
                        or {}
                    ),
                )
            )

        return frames

    # ========================================================
    # SCORING
    # ========================================================

    def _replay_success_probability(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> float:

        if not frames:
            return 0.0

        return self._clamp_probability(
            sum(
                frame.confidence
                for frame in frames
            )
            / len(frames)
        )

    def _explainability_score(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> float:

        if not frames:
            return 0.0

        scored = 0.0

        for frame in frames:

            if frame.summary:
                scored += 1.0

            if frame.source_engine:
                scored += 1.0

            if frame.branch_name:
                scored += 1.0

        return self._clamp_score(
            (
                scored
                / (
                    len(frames) * 3
                )
            )
            * 100
        )

    def _replay_integrity_score(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> float:

        if not frames:
            return 0.0

        integrity = 100.0

        for frame in frames:

            if not frame.summary:
                integrity -= 2.0

            if not frame.source_engine:
                integrity -= 2.0

        return self._clamp_score(
            integrity
        )

    def _operational_visibility_score(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> float:

        operational = [
            frame
            for frame in frames
            if frame.frame_type
            in {
                FRAME_TYPE_RUNTIME,
                FRAME_TYPE_SIMULATION,
                FRAME_TYPE_FAILOVER,
            }
        ]

        return self._visibility_score(
            operational,
            len(frames),
        )

    def _governance_visibility_score(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> float:

        governance = [
            frame
            for frame in frames
            if frame.frame_type
            == FRAME_TYPE_GOVERNANCE
        ]

        return self._visibility_score(
            governance,
            len(frames),
        )

    def _mission_visibility_score(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> float:

        mission = [
            frame
            for frame in frames
            if frame.frame_type
            == FRAME_TYPE_MISSION
        ]

        return self._visibility_score(
            mission,
            len(frames),
        )

    def _branch_visibility_score(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> float:

        branching = [
            frame
            for frame in frames
            if frame.branch_id
        ]

        return self._visibility_score(
            branching,
            len(frames),
        )

    @staticmethod
    def _visibility_score(
        subset: Sequence[Any],
        total: int,
    ) -> float:

        if total <= 0:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                (
                    len(subset)
                    / total
                )
                * 100,
            ),
        )

    # ========================================================
    # ACTIONS
    # ========================================================

    def _recommended_actions(
        self,
        frames: Sequence[
            ReplayFrame
        ],
    ) -> List[Dict[str, Any]]:

        actions = [
            {
                "action": (
                    "record_replay_lineage"
                )
            },
            {
                "action": (
                    "record_replay_evidence"
                )
            },
        ]

        if any(
            frame.branch_id
            for frame in frames
        ):
            actions.append(
                {
                    "action": (
                        "review_branching_paths"
                    )
                }
            )

        if any(
            frame.mission_state
            in {
                "CRITICAL",
                "FAILED",
            }
            for frame in frames
        ):
            actions.append(
                {
                    "action": (
                        "review_mission_degradation"
                    )
                }
            )

        return actions

    # ========================================================
    # RATIONALE
    # ========================================================

    @staticmethod
    def _build_rationale(
        *,
        total_frames: int,
        replay_success_probability: (
            float
        ),
        explainability_score: float,
        replay_integrity_score: (
            float
        ),
        playback_mode: str,
    ) -> str:

        return (
            f"Sovereign replay "
            f"timeline generated "
            f"{total_frames} frame(s) "
            f"using playback mode "
            f"{playback_mode}. "
            f"Replay success "
            f"probability "
            f"{replay_success_probability:.2f}; "
            f"explainability score "
            f"{explainability_score:.2f}; "
            f"replay integrity "
            f"score "
            f"{replay_integrity_score:.2f}."
        )

    # ========================================================
    # RECORDING
    # ========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignRuntimeReplayAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

        self._write_to_memory(
            assessment,
            context=context,
        )

        self._write_to_lineage(
            assessment,
            context=context,
        )

        self._write_to_evidence(
            assessment,
            context=context,
        )

        self._emit_event(
            assessment,
            context=context,
        )

    def _write_to_memory(
        self,
        assessment: (
            SovereignRuntimeReplayAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if (
            self.operational_memory_engine
            is None
        ):
            return

        payload = {
            "type": (
                "SOVEREIGN_RUNTIME_REPLAY_ASSESSMENT"
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                self.operational_memory_engine,
                "append_memory",
            ):
                self.operational_memory_engine.append_memory(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Replay memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignRuntimeReplayAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": (
                "RUNTIME_REPLAY"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "context": {
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                self.lineage_engine,
                "record_lineage",
            ):
                self.lineage_engine.record_lineage(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Replay lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignRuntimeReplayAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if (
            self
            .fedramp_evidence_lineage_engine
            is None
        ):
            return

        payload = {
            "evidence_type": (
                "RUNTIME_REPLAY"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "evidence_payload": {
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                self
                .fedramp_evidence_lineage_engine,
                "record_evidence",
            ):
                self.fedramp_evidence_lineage_engine.record_evidence(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Replay evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignRuntimeReplayAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.event_bus is None:
            return

        payload = {
            "event_type": (
                "SOVEREIGN_RUNTIME_REPLAY_ASSESSMENT"
            ),
            "engine_name": (
                self.engine_name
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                self.event_bus,
                "emit",
            ):
                self.event_bus.emit(
                    (
                        "SOVEREIGN_RUNTIME_REPLAY_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Replay event emit failed: {exc}"
            )

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or ReplaySeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in ReplaySeverity
        }

        return (
            value
            if value in valid
            else ReplaySeverity
            .INFO.value
        )

    @staticmethod
    def _clamp_score(
        value: Any,
    ) -> float:

        try:
            score = float(value)

        except Exception:
            score = 0.0

        return max(
            0.0,
            min(100.0, score),
        )

    @staticmethod
    def _clamp_probability(
        value: Any,
    ) -> float:

        try:
            score = float(value)

        except Exception:
            score = 0.0

        return max(
            0.0,
            min(1.0, score),
        )


def build_sovereign_runtime_visual_replay_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> (
    SovereignRuntimeVisualReplayEngine
):

    return (
        SovereignRuntimeVisualReplayEngine(
            event_bus=event_bus,
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )