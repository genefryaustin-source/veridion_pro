"""
core/ai/orchestration/mission_planner.py
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


MISSION_PENDING = "PENDING"
MISSION_APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
MISSION_APPROVED = "APPROVED"
MISSION_RUNNING = "RUNNING"
MISSION_COMPLETED = "COMPLETED"
MISSION_FAILED = "FAILED"
MISSION_CANCELLED = "CANCELLED"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


def _json_loads(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value

    try:
        return json.loads(value or "{}")
    except Exception:
        return {}


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

    return getattr(
        storage_or_ledger,
        "ledger",
        storage_or_ledger,
    )


@dataclass
class MissionPlan:

    mission_id: str

    tenant_id: str = DEFAULT_TENANT

    name: str = ""

    description: str = ""

    objective: str = ""

    priority: str = "MEDIUM"

    status: str = MISSION_PENDING

    created_by: str = "system"

    mission_type: str = "GENERIC"

    targets: List[Dict[str, Any]] = field(default_factory=list)

    execution_plan: List[Dict[str, Any]] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    risk_score: int = 0

    requires_approval: bool = False

    approval_id: Optional[str] = None

    created_at_ms: int = field(default_factory=_now_ms)

    updated_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MissionPlanner:

    def __init__(
        self,
        storage: Any = None,
        *,
        event_bus: Any = None,
        governance: Any = None,
    ) -> None:

        self.storage = storage

        self.ledger = _get_ledger(storage)

        self.event_bus = (
            event_bus
            or getattr(
                storage,
                "event_bus",
                None,
            )
        )

        self.governance = (
            governance
            or getattr(
                storage,
                "governance",
                None,
            )
        )

        self.db_path = self._resolve_db_path()

        self.ensure_schema()

    def _resolve_db_path(self) -> str:

        ledger = self.ledger

        if ledger is not None:

            for attr in (
                "db_path",
                "database_path",
                "path",
                "_db_path",
            ):

                path = getattr(
                    ledger,
                    attr,
                    None,
                )

                if path:
                    return path

        if isinstance(self.storage, str):
            return self.storage

        return "data/ledger.db"

    def _connect(self) -> sqlite3.Connection:

        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30,
        )

        try:

            conn.execute(
                "PRAGMA journal_mode=WAL;"
            )

            conn.execute(
                "PRAGMA synchronous=NORMAL;"
            )

            conn.execute(
                "PRAGMA foreign_keys=ON;"
            )

        except Exception:
            pass

        return conn

    def ensure_schema(self) -> None:

        with self._connect() as conn:

            # -------------------------------------------------
            # MAIN TABLE
            # -------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mission_plans (
                    mission_id TEXT PRIMARY KEY,
                    tenant_id TEXT,
                    name TEXT,
                    description TEXT,
                    objective TEXT,
                    priority TEXT,
                    status TEXT,
                    created_by TEXT,
                    mission_type TEXT,
                    targets_json TEXT,
                    execution_plan_json TEXT,
                    metadata_json TEXT,
                    risk_score INTEGER DEFAULT 0,
                    requires_approval INTEGER DEFAULT 0,
                    approval_id TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL
                )
                """
            )

            # -------------------------------------------------
            # SAFE SCHEMA MIGRATIONS
            # -------------------------------------------------

            existing_cols = {

                row[1]

                for row in conn.execute(
                    "PRAGMA table_info(mission_plans)"
                ).fetchall()
            }

            required_columns = {

                "updated_at_ms":
                    """
                    ALTER TABLE mission_plans
                    ADD COLUMN updated_at_ms INTEGER
                    """,

                "risk_score":
                    """
                    ALTER TABLE mission_plans
                    ADD COLUMN risk_score INTEGER DEFAULT 0
                    """,

                "requires_approval":
                    """
                    ALTER TABLE mission_plans
                    ADD COLUMN requires_approval INTEGER DEFAULT 0
                    """,

                "approval_id":
                    """
                    ALTER TABLE mission_plans
                    ADD COLUMN approval_id TEXT
                    """,

                "targets_json":
                    """
                    ALTER TABLE mission_plans
                    ADD COLUMN targets_json TEXT
                    """,

                "execution_plan_json":
                    """
                    ALTER TABLE mission_plans
                    ADD COLUMN execution_plan_json TEXT
                    """,

                "metadata_json":
                    """
                    ALTER TABLE mission_plans
                    ADD COLUMN metadata_json TEXT
                    """,
            }

            for col, sql in required_columns.items():

                if col not in existing_cols:

                    try:

                        conn.execute(sql)

                    except Exception:
                        pass

            # -------------------------------------------------
            # INDEXES
            # -------------------------------------------------

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mission_status
                ON mission_plans(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mission_tenant
                ON mission_plans(tenant_id)
                """
            )

            conn.commit()

    def create_mission(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        name: str,
        description: str = "",
        objective: str = "",
        priority: str = "MEDIUM",
        created_by: str = "system",
        mission_type: str = "GENERIC",
        targets: Optional[List[Dict[str, Any]]] = None,
        execution_plan: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        risk_score: int = 0,
        requires_approval: bool = False,
        approval_id: Optional[str] = None,
    ) -> MissionPlan:

        mission = MissionPlan(
            mission_id=f"MISSION-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id or DEFAULT_TENANT,
            name=name,
            description=description,
            objective=objective,
            priority=priority,
            created_by=created_by,
            mission_type=mission_type,
            targets=targets or [],
            execution_plan=execution_plan or [],
            metadata=metadata or {},
            risk_score=risk_score,
            requires_approval=requires_approval,
            approval_id=approval_id,
            status=(
                MISSION_APPROVAL_REQUIRED
                if requires_approval
                else MISSION_PENDING
            ),
        )

        with self._connect() as conn:

            conn.execute(
                """
                INSERT INTO mission_plans (
                    mission_id,
                    tenant_id,
                    name,
                    description,
                    objective,
                    priority,
                    status,
                    created_by,
                    mission_type,
                    targets_json,
                    execution_plan_json,
                    metadata_json,
                    risk_score,
                    requires_approval,
                    approval_id,
                    created_at_ms,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mission.mission_id,
                    mission.tenant_id,
                    mission.name,
                    mission.description,
                    mission.objective,
                    mission.priority,
                    mission.status,
                    mission.created_by,
                    mission.mission_type,
                    _json_dumps(mission.targets),
                    _json_dumps(mission.execution_plan),
                    _json_dumps(mission.metadata),
                    mission.risk_score,
                    int(mission.requires_approval),
                    mission.approval_id,
                    mission.created_at_ms,
                    mission.updated_at_ms,
                ),
            )

            conn.commit()

        return mission

    def update_mission_status(
        self,
        mission_id: str,
        status: str,
    ) -> bool:

        with self._connect() as conn:

            conn.execute(
                """
                UPDATE mission_plans
                SET status=?,
                    updated_at_ms=?
                WHERE mission_id=?
                """,
                (
                    status,
                    _now_ms(),
                    mission_id,
                ),
            )

            conn.commit()

        return True

    def get_mission(
        self,
        mission_id: str,
    ) -> Optional[Dict[str, Any]]:

        with self._connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM mission_plans
                WHERE mission_id=?
                LIMIT 1
                """,
                (mission_id,),
            ).fetchone()

            if not row:
                return None

            cols = [

                d[1]

                for d in conn.execute(
                    "PRAGMA table_info(mission_plans)"
                ).fetchall()
            ]

        data = dict(zip(cols, row))

        data["targets"] = _json_loads(
            data.pop("targets_json", "[]")
        )

        data["execution_plan"] = _json_loads(
            data.pop("execution_plan_json", "[]")
        )

        data["metadata"] = _json_loads(
            data.pop("metadata_json", "{}")
        )

        data["requires_approval"] = bool(
            data.get("requires_approval")
        )

        return data

    def list_missions(
        self,
        *,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:

        clauses = []
        params: List[Any] = []

        if tenant_id:
            clauses.append("tenant_id=?")
            params.append(tenant_id)

        if status:
            clauses.append("status=?")
            params.append(status)

        where_clause = ""

        if clauses:
            where_clause = (
                "WHERE "
                + " AND ".join(clauses)
            )

        params.append(limit)

        with self._connect() as conn:

            rows = conn.execute(
                f"""
                SELECT *
                FROM mission_plans
                {where_clause}
                ORDER BY updated_at_ms DESC
                LIMIT ?
                """,
                params,
            ).fetchall()

            cols = [

                d[1]

                for d in conn.execute(
                    "PRAGMA table_info(mission_plans)"
                ).fetchall()
            ]

        missions: List[Dict[str, Any]] = []

        for row in rows:

            data = dict(zip(cols, row))

            data["targets"] = _json_loads(
                data.pop("targets_json", "[]")
            )

            data["execution_plan"] = _json_loads(
                data.pop(
                    "execution_plan_json",
                    "[]",
                )
            )

            data["metadata"] = _json_loads(
                data.pop("metadata_json", "{}")
            )

            data["requires_approval"] = bool(
                data.get("requires_approval")
            )

            missions.append(data)

        return missions


_DEFAULT_MISSION_PLANNER: Optional[
    MissionPlanner
] = None


def get_mission_planner(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
    governance: Any = None,
) -> MissionPlanner:

    global _DEFAULT_MISSION_PLANNER

    if (
        reset
        or _DEFAULT_MISSION_PLANNER is None
    ):

        _DEFAULT_MISSION_PLANNER = MissionPlanner(
            storage=storage,
            event_bus=event_bus,
            governance=governance,
        )

    return _DEFAULT_MISSION_PLANNER