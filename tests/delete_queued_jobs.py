from core.storage.factory import build_storage

storage = build_storage()

with storage.ledger._connect() as con:

    con.execute("DELETE FROM pipeline_jobs")
    con.execute("DELETE FROM pipeline_events")

    con.commit()

print("Pipeline queue cleared")