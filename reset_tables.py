
# nuclear_runtime_reset.py

import sqlite3
from pathlib import Path

DB = Path("data/ledger.db")

# =====================================================
# ONLY THESE SURVIVE
# =====================================================

KEEP_TABLES = {
    "oauth_tokens",
    "connected_mailboxes",
    "imap_configs",
    "users",
    "tenants",
    "settings",
    "roles",
    "api_keys",
    "sqlite_sequence",
}

con = sqlite3.connect(DB)
cur = con.cursor()

try:

    print("\n🔥 STARTING FULL RUNTIME PURGE")

    cur.execute("PRAGMA foreign_keys = OFF;")

    # -------------------------------------------------
    # GET ALL TABLES
    # -------------------------------------------------
    tables = [
        r[0]
        for r in cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()
    ]

    print("\n📋 ALL TABLES:")
    for t in tables:
        try:
            count = cur.execute(
                f'SELECT COUNT(*) FROM "{t}"'
            ).fetchone()[0]

            print(f"  {t}: {count}")

        except Exception as e:
            print(f"  {t}: ERROR {e}")

    # -------------------------------------------------
    # EVERYTHING NOT EXPLICITLY KEPT GETS PURGED
    # -------------------------------------------------
    purge_tables = [
        t for t in tables
        if t not in KEEP_TABLES
    ]

    print("\n☢️ PURGING TABLES:")

    for t in purge_tables:

        try:

            before = cur.execute(
                f'SELECT COUNT(*) FROM "{t}"'
            ).fetchone()[0]

            print(f"  Clearing {t} ({before} rows)")

            cur.execute(f'DELETE FROM "{t}"')

        except Exception as e:

            print(f"  FAILED {t}: {e}")

    # -------------------------------------------------
    # RESET SQLITE AUTOINCREMENT
    # -------------------------------------------------
    try:

        cur.execute("""
            DELETE FROM sqlite_sequence
        """)

    except Exception as e:

        print("sqlite_sequence reset skipped:", e)

    con.commit()

    # -------------------------------------------------
    # VERIFY
    # -------------------------------------------------
    print("\n✅ VERIFYING PURGE")

    for t in purge_tables:

        try:

            after = cur.execute(
                f'SELECT COUNT(*) FROM "{t}"'
            ).fetchone()[0]

            print(f"  {t}: {after}")

        except Exception as e:

            print(f"  {t}: ERROR {e}")

    print("\n✅ FULL FORENSIC RESET COMPLETE")

finally:

    try:
        cur.execute("PRAGMA foreign_keys = ON;")
    except:
        pass

    con.close()
