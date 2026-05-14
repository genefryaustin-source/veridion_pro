from core.storage.factory import build_storage

storage = build_storage()

with storage.ledger._connect() as con:

    rows = con.execute(
        "PRAGMA table_info(alerts)"
    ).fetchall()

    print("\n=== ALERTS TABLE ===\n")

    for r in rows:
        print(dict(r))

    fk_rows = con.execute(
        "PRAGMA foreign_key_list(alerts)"
    ).fetchall()

    print("\n=== ALERTS FOREIGN KEYS ===\n")

    for r in fk_rows:
        print(dict(r))