# core/db/bootstrap.py

from pathlib import Path

from core.db.migration_runner import run_migrations
from core.db.schema_validator import validate_schema


def bootstrap_database(db_path: str):
    db = Path(db_path)

    if not db.parent.exists():
        db.parent.mkdir(parents=True, exist_ok=True)

    print("🧱 Bootstrapping database")
    print(f"📍 DB Path: {db_path}")

    run_migrations(db_path)

    report = validate_schema(
        db_path=db_path,
        auto_patch=True,
    )

    if report["missing_tables"]:
        print("🚨 Missing tables:", report["missing_tables"])

    if report["missing_columns"]:
        print("⚠️ Missing columns:", report["missing_columns"])

    if report["patched_columns"]:
        print("🩹 Patched columns:", report["patched_columns"])

    if report["missing_triggers"]:
        print("🚨 Missing immutable triggers:", report["missing_triggers"])

    print("✅ Database bootstrap complete")

    return report