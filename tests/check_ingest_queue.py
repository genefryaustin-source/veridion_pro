from core.storage.factory import build_storage

storage = build_storage()

with storage.ledger._connect() as con:

    rows = con.execute(
        """
        SELECT
            job_id,
            stage,
            status,
            parent_job_id,
            evidence_id,
            created_at_ms
        FROM pipeline_jobs
        ORDER BY created_at_ms DESC
        LIMIT 20
        """
    ).fetchall()

    print("\n=== PIPELINE JOBS ===\n")

    for r in rows:
        print(dict(r))