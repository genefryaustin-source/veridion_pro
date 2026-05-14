"""
tools/repair_governance_schema.py

Safely repairs governance/orchestration schema drift.

This script:
1. Opens the existing SQLite ledger DB.
2. Backs it up first.
3. Prints existing governance-related schema objects.
4. Drops ONLY governance/orchestration tables and indexes.
5. Rebuilds them using GovernanceRepository.ensure_schema().
6. Runs a small test write/read.

Run from project root:

    python tools/repair_governance_schema.py
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "ledger.db"


GOVERNANCE_TABLES = [
    "governance_events",
    "approval_requests",
    "orchestration_decisions",
    "analyst_overrides",
    "rollback_events",
    "execution_traces",
]


GOVERNANCE_INDEXES = [
    "idx_approval_status",
    "idx_approval_case",
    "idx_approval_decision",
    "idx_decisions_case",
    "idx_decisions_tenant",
    "idx_decisions_created",
    "idx_overrides_case",
    "idx_overrides_decision",
    "idx_gov_events_case",
    "idx_gov_events_decision",
    "idx_gov_events_created",
    "idx_rollbacks_case",
    "idx_rollbacks_decision",
    "idx_traces_decision",
    "idx_traces_case",
    "idx_traces_created",
]


SEARCH_TERMS = [
    "governance",
    "approval",
    "rollback",
    "decision",
    "override",
    "trace",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def ensure_project_imports() -> None:
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def backup_database(db_path: Path) -> Path:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    backup_dir = PROJECT_ROOT / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"ledger_governance_repair_backup_{stamp}.db"

    shutil.copy2(db_path, backup_path)

    return backup_path


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def print_governance_schema(conn: sqlite3.Connection) -> None:
    print_header("CURRENT GOVERNANCE-RELATED SQLITE OBJECTS")

    rows = conn.execute("""
        SELECT name, type, sql
        FROM sqlite_master
        WHERE type IN ('table', 'index', 'view', 'trigger')
        ORDER BY type, name
    """).fetchall()

    found = False

    for row in rows:
        name = str(row["name"] or "").lower()
        sql = str(row["sql"] or "")

        if any(term in name for term in SEARCH_TERMS):
            found = True
            print("\n------------------------------")
            print("NAME:", row["name"])
            print("TYPE:", row["type"])
            print("------------------------------")
            print(sql)

    if not found:
        print("No governance-related objects found.")


def print_table_columns(conn: sqlite3.Connection) -> None:
    print_header("CURRENT GOVERNANCE TABLE COLUMNS")

    for table in GOVERNANCE_TABLES:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()

        if not exists:
            print(f"\n{table}: does not exist")
            continue

        print(f"\n{table}:")
        columns = conn.execute(f"PRAGMA table_info({table})").fetchall()

        for col in columns:
            print(
                f"  - {col['name']} | type={col['type']} | "
                f"notnull={col['notnull']} | default={col['dflt_value']} | pk={col['pk']}"
            )


def drop_governance_objects(conn: sqlite3.Connection) -> None:
    print_header("DROPPING GOVERNANCE-ONLY OBJECTS")

    for index_name in GOVERNANCE_INDEXES:
        print(f"Dropping index if exists: {index_name}")
        conn.execute(f"DROP INDEX IF EXISTS {index_name}")

    for table_name in GOVERNANCE_TABLES:
        print(f"Dropping table if exists: {table_name}")
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.commit()


def rebuild_governance_schema(conn: sqlite3.Connection) -> None:
    print_header("REBUILDING GOVERNANCE SCHEMA")

    ensure_project_imports()

    from core.storage.governance_repository import GovernanceRepository

    repo = GovernanceRepository(conn)
    repo.ensure_schema()

    print("Governance schema rebuilt successfully.")


def smoke_test(conn: sqlite3.Connection) -> None:
    print_header("RUNNING GOVERNANCE SMOKE TEST")

    ensure_project_imports()

    from core.storage.governance_repository import GovernanceRepository

    repo = GovernanceRepository(conn)

    decision_id = repo.record_orchestration_decision(
        recommendation="Governance schema smoke test recommendation",
        final_action="NOOP_TEST",
        severity="INFO",
        confidence=1.0,
        details={
            "source": "tools/repair_governance_schema.py",
            "purpose": "schema repair validation",
        },
    )

    event_id = repo.record_governance_event(
        event_type="SYSTEM_TEST",
        action="Governance repository repair smoke test",
        severity="INFO",
        decision_id=decision_id,
        actor="repair_script",
    )

    replay = repo.get_forensic_replay(limit=10)

    print("Created decision_id:", decision_id)
    print("Created event_id:", event_id)
    print("Replay events returned:", len(replay))

    if not replay:
        raise RuntimeError("Smoke test failed: forensic replay returned no events.")

    print("Smoke test passed.")


def main() -> None:
    print_header("GOVERNANCE SCHEMA REPAIR STARTING")
    print("Project root:", PROJECT_ROOT)
    print("Database:", DB_PATH)

    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}")
        sys.exit(1)

    backup_path = backup_database(DB_PATH)
    print("Backup created:", backup_path)

    conn = get_connection(DB_PATH)

    try:
        print_governance_schema(conn)
        print_table_columns(conn)

        print_header("CONFIRMATION")
        print("This will DROP and REBUILD ONLY these governance/orchestration tables:")
        for table in GOVERNANCE_TABLES:
            print(" -", table)

        print("\nIt will NOT drop evidence, custody, cases, alerts, runs, attachments, or oauth tables.")

        confirm = input("\nType REPAIR to continue: ").strip()

        if confirm != "REPAIR":
            print("Aborted. No changes made.")
            return

        drop_governance_objects(conn)
        rebuild_governance_schema(conn)

        print_governance_schema(conn)
        print_table_columns(conn)

        smoke_test(conn)

        print_header("REPAIR COMPLETE")
        print("Governance schema repaired successfully.")
        print("Backup location:", backup_path)

    finally:
        conn.close()


if __name__ == "__main__":
    main()