# clone_clean_ledger_preserve_immutability.py

import sqlite3
import shutil
from pathlib import Path

OLD_DB = Path("data/ledger.db")
NEW_DB = Path("data/ledger_clean.db")
BACKUP_DB = Path("data/ledger_before_clean_clone.db")

PRESERVE_TABLES = {
    "oauth_tokens",
    "connected_mailboxes",
    "imap_configs",
    "users",
    "tenants",
    "settings",
    "roles",
    "api_keys",
    "alert_settings",
    "retry_policy",
    "supervisor_config",
}

if not OLD_DB.exists():
    raise FileNotFoundError(f"Missing DB: {OLD_DB}")

if NEW_DB.exists():
    NEW_DB.unlink()

shutil.copy2(OLD_DB, BACKUP_DB)
shutil.copy2(OLD_DB, NEW_DB)

print(f"✅ Backup created: {BACKUP_DB}")
print(f"✅ Working clone created: {NEW_DB}")

con = sqlite3.connect(NEW_DB)
cur = con.cursor()

try:
    cur.execute("PRAGMA foreign_keys = OFF;")

    # -------------------------------------------------
    # CAPTURE IMMUTABLE TRIGGERS
    # -------------------------------------------------
    immutable_triggers = []

    rows = cur.execute("""
        SELECT name, tbl_name, sql
        FROM sqlite_master
        WHERE type = 'trigger'
        ORDER BY name
    """).fetchall()

    for name, table_name, sql in rows:
        sql_text = (sql or "").upper()

        if (
            "IMMUTABLE_LEDGER" in sql_text
            or "APPEND-ONLY" in sql_text
            or "RAISE(ABORT" in sql_text
        ):
            immutable_triggers.append({
                "name": name,
                "table": table_name,
                "sql": sql,
            })

    print("\n🔒 IMMUTABLE TRIGGERS CAPTURED:")
    if immutable_triggers:
        for trig in immutable_triggers:
            print(f"  {trig['name']} ON {trig['table']}")
    else:
        print("  None found")

    # -------------------------------------------------
    # DROP IMMUTABLE TRIGGERS TEMPORARILY
    # -------------------------------------------------
    print("\n🔓 TEMPORARILY DROPPING IMMUTABLE TRIGGERS:")

    for trig in immutable_triggers:
        print(f"  Dropping {trig['name']}")
        cur.execute(f'DROP TRIGGER IF EXISTS "{trig["name"]}"')

    # -------------------------------------------------
    # GET TABLES
    # -------------------------------------------------
    tables = [
        r[0]
        for r in cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()
    ]

    print("\n📋 TABLES BEFORE CLEAN:")

    for t in tables:
        try:
            count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            print(f"  {t}: {count}")
        except Exception as e:
            print(f"  {t}: ERROR {e}")

    # -------------------------------------------------
    # CLEAR RUNTIME DATA
    # -------------------------------------------------
    print("\n🧹 CLEARING RUNTIME TABLES:")

    for t in tables:
        if t in PRESERVE_TABLES:
            print(f"  KEEPING {t}")
            continue

        try:
            before = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            print(f"  CLEARING {t} ({before} rows)")
            cur.execute(f'DELETE FROM "{t}"')
        except Exception as e:
            print(f"  FAILED {t}: {e}")

    # -------------------------------------------------
    # RESET AUTOINCREMENT FOR CLEARED TABLES ONLY
    # -------------------------------------------------
    try:
        for t in tables:
            if t not in PRESERVE_TABLES:
                cur.execute("DELETE FROM sqlite_sequence WHERE name = ?", (t,))
    except Exception as e:
        print("sqlite_sequence reset skipped:", e)

    # -------------------------------------------------
    # RECREATE IMMUTABLE TRIGGERS
    # -------------------------------------------------
    print("\n🔒 RECREATING IMMUTABLE TRIGGERS:")

    for trig in immutable_triggers:
        if not trig["sql"]:
            print(f"  SKIPPED {trig['name']} because SQL was empty")
            continue

        print(f"  Recreating {trig['name']}")
        cur.execute(trig["sql"])

    con.commit()

    # -------------------------------------------------
    # VERIFY TABLE COUNTS
    # -------------------------------------------------
    print("\n✅ VERIFY CLEAN CLONE:")

    for t in tables:
        try:
            count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            label = "PRESERVED" if t in PRESERVE_TABLES else "CLEARED"
            print(f"  {label}: {t}: {count}")
        except Exception as e:
            print(f"  {t}: ERROR {e}")

    # -------------------------------------------------
    # VERIFY IMMUTABLE TRIGGERS RESTORED
    # -------------------------------------------------
    restored = cur.execute("""
        SELECT name, tbl_name
        FROM sqlite_master
        WHERE type = 'trigger'
        ORDER BY name
    """).fetchall()

    restored_names = {r[0] for r in restored}

    print("\n🔒 IMMUTABILITY RESTORE CHECK:")

    for trig in immutable_triggers:
        if trig["name"] in restored_names:
            print(f"  ✅ Restored {trig['name']}")
        else:
            print(f"  ❌ Missing {trig['name']}")

finally:
    try:
        cur.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass

    con.close()

print("\n✅ CLEAN FORENSIC CLONE COMPLETE")
print("\nNEXT STEPS:")
print("1. Stop Streamlit, workers, and supervisor")
print("2. Rename data/ledger.db to data/ledger_dirty_old.db")
print("3. Rename data/ledger_clean.db to data/ledger.db")
print("4. Delete data/ledger.db-wal and data/ledger.db-shm if present")
print("5. Restart the app")