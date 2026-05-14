from core.storage.factory import build_storage

storage = build_storage()

with storage.ledger._connect() as con:

    con.execute(
        """
        DELETE FROM pipeline_jobs
        WHERE stage = 'DETECT'
          AND evidence_id IS NULL
        """
    )

    con.commit()

print("Old DETECT jobs removed")