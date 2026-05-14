import time
import json

def persist_analysis(con, run_id, evidence_id, result):


    con.execute("""
        INSERT INTO evidence_events (
            evidence_id,
            run_id,
            event_type,
            created_at_ms,
            data_json
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        evidence_id,
        run_id,
        "EVIDENCE_CUI_ANALYSIS",
        int(time.time() * 1000),
        json.dumps(result)
    ))

    con.commit()  # 🔥 CRITICAL

