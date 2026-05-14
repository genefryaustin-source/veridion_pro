# core/db/export_schema.py

import sqlite3
from pathlib import Path

DB_PATH = Path("data/ledger.db")
OUTPUT_PATH = Path("core/db/schema.sql")

if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found: {DB_PATH}")

con = sqlite3.connect(DB_PATH)

try:
    rows = con.execute("""
        SELECT type, name, sql
        FROM sqlite_master
        WHERE sql IS NOT NULL
        AND type IN (
            'table',
            'index',
            'trigger'
        )
        AND name NOT LIKE 'sqlite_%'
        ORDER BY
            CASE type
                WHEN 'table' THEN 1
                WHEN 'index' THEN 2
                WHEN 'trigger' THEN 3
            END,
            name
    """).fetchall()

    schema_lines = []

    schema_lines.append("-- ====================================")
    schema_lines.append("-- VERIDION PRO CANONICAL SCHEMA")
    schema_lines.append("-- AUTO-GENERATED FROM LIVE DATABASE")
    schema_lines.append("-- ====================================\n")

    for obj_type, name, sql in rows:

        if not sql:
            continue

        schema_lines.append(f"-- {obj_type.upper()}: {name}")
        schema_lines.append(f"{sql};\n")

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        "\n".join(schema_lines),
        encoding="utf-8"
    )

    print(f"✅ Schema exported to: {OUTPUT_PATH}")

finally:
    con.close()