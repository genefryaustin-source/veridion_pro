# core/db/migration_runner.py

import hashlib
import sqlite3
import time
from pathlib import Path


MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _checksum(sql: str) -> str:
    return hashlib.sha256(sql.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# 🔥 SCHEMA HELPERS
# ---------------------------------------------------------

def column_exists(
    con,
    table_name: str,
    column_name: str,
) -> bool:

    rows = con.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    cols = [r[1] for r in rows]

    return column_name in cols


def safe_add_column(
    con,
    table_name: str,
    column_def: str,
):

    col_name = column_def.split()[0]

    if column_exists(
        con,
        table_name,
        col_name,
    ):

        print(
            f"ℹ️ COLUMN EXISTS: "
            f"{table_name}.{col_name}"
        )

        return

    sql = (
        f"ALTER TABLE {table_name} "
        f"ADD COLUMN {column_def}"
    )

    print(
        f"🧱 ADDING COLUMN: "
        f"{table_name}.{col_name}"
    )

    con.execute(sql)


# ---------------------------------------------------------
# 🔥 SCHEMA MIGRATIONS TABLE
# ---------------------------------------------------------

def ensure_schema_migrations_table(
    db_path: str
):

    with sqlite3.connect(db_path) as con:

        con.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                filename TEXT,
                checksum TEXT,
                applied_at_ms INTEGER
            )
        """)

        cols = [
            r[1]
            for r in con.execute(
                "PRAGMA table_info(schema_migrations)"
            ).fetchall()
        ]

        if "filename" not in cols:

            con.execute("""
                ALTER TABLE schema_migrations
                ADD COLUMN filename TEXT
            """)

        if "checksum" not in cols:

            con.execute("""
                ALTER TABLE schema_migrations
                ADD COLUMN checksum TEXT
            """)

        if "applied_at_ms" not in cols:

            con.execute("""
                ALTER TABLE schema_migrations
                ADD COLUMN applied_at_ms INTEGER
            """)

        con.commit()


# ---------------------------------------------------------
# 🔥 APPLIED MIGRATIONS
# ---------------------------------------------------------

def get_applied_migrations(
    con
) -> dict:

    rows = con.execute("""
        SELECT version, checksum
        FROM schema_migrations
    """).fetchall()

    return {
        r[0]: r[1]
        for r in rows
    }


# ---------------------------------------------------------
# 🔥 MAIN MIGRATION RUNNER
# ---------------------------------------------------------

def run_migrations(
    db_path: str
):

    ensure_schema_migrations_table(
        db_path
    )

    if not MIGRATIONS_DIR.exists():

        MIGRATIONS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    migration_files = sorted(
        MIGRATIONS_DIR.glob("*.sql")
    )

    with sqlite3.connect(db_path) as con:

        con.execute(
            "PRAGMA foreign_keys = ON;"
        )

        applied = get_applied_migrations(
            con
        )

        for path in migration_files:

            version = (
                path.stem.split("_")[0]
            )

            sql = path.read_text(
                encoding="utf-8"
            )

            checksum = _checksum(sql)

            # -------------------------------------------------
            # 🔥 CHECKSUM VALIDATION
            # -------------------------------------------------

            if version in applied:

                if applied[version] != checksum:

                    raise RuntimeError(
                        f"Migration checksum mismatch "
                        f"for {path.name}. "
                        "Do not edit already-applied migrations."
                    )

                continue

            print(
                f"🧱 Applying migration: "
                f"{path.name}"
            )

            try:

                statements = [
                    s.strip()
                    for s in sql.split(";")
                    if s.strip()
                ]

                for stmt in statements:

                    try:

                        con.execute(stmt)

                    except sqlite3.OperationalError as e:

                        # -------------------------------------
                        # SAFE ADDITIVE MIGRATIONS
                        # -------------------------------------

                        if (
                            "duplicate column name"
                            in str(e).lower()
                        ):

                            print(
                                "ℹ️ COLUMN ALREADY EXISTS:",
                                stmt
                            )

                            continue

                        raise

                # ---------------------------------------------
                # 🔥 RECORD MIGRATION
                # ---------------------------------------------

                con.execute("""
                    INSERT INTO schema_migrations (
                        version,
                        filename,
                        checksum,
                        applied_at_ms
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    version,
                    path.name,
                    checksum,
                    _now_ms(),
                ))

                con.commit()

            except Exception as e:

                con.rollback()

                print(
                    "❌ MIGRATION FAILED:",
                    path.name,
                    str(e)
                )

                raise

    print("✅ Database migrations complete")