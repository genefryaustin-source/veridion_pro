import json
import time


def persist_correlations(
    con,
    run_id,
    source_evidence_id,
    correlations,
):

    now_ms = int(time.time() * 1000)

    for c in correlations:

        try:

            target_evidence_id = c.get(
                "related_evidence_id"
            )

            if not target_evidence_id:
                continue

            if (
                target_evidence_id
                == source_evidence_id
            ):
                continue

            # ---------------------------------------
            # 🔥 CANONICAL EDGE ORDERING
            # ---------------------------------------

            edge_a = min(
                source_evidence_id,
                target_evidence_id,
            )

            edge_b = max(
                source_evidence_id,
                target_evidence_id,
            )

            correlation_type = c.get(
                "type"
            )

            correlation_value = c.get(
                "entity_value"
            )

            # ---------------------------------------
            # 🔥 PREVENT DUPLICATE EDGES
            # ---------------------------------------

            existing = con.execute(
                """
                SELECT 1
                FROM evidence_correlations
                WHERE source_evidence_id = ?
                AND target_evidence_id = ?
                AND correlation_type = ?
                AND correlation_value = ?
                LIMIT 1
                """,
                (
                    edge_a,
                    edge_b,
                    correlation_type,
                    correlation_value,
                )
            ).fetchone()

            if existing:

                print(
                    "♻️ CORRELATION EDGE EXISTS:",
                    correlation_type,
                    correlation_value,
                )

                continue

            # ---------------------------------------
            # 🔥 INSERT GRAPH EDGE
            # ---------------------------------------

            con.execute(
                """
                INSERT INTO evidence_correlations (

                    run_id,

                    source_evidence_id,
                    target_evidence_id,

                    correlation_type,
                    correlation_value,

                    confidence,

                    created_at_ms,

                    metadata_json

                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,

                    edge_a,
                    edge_b,

                    correlation_type,
                    correlation_value,

                    "HIGH",

                    now_ms,

                    json.dumps(c),
                )
            )

            print(
                "🔗 CORRELATION EDGE PERSISTED:",
                correlation_type,
                correlation_value,
            )

        except Exception as e:

            print(
                "⚠️ CORRELATION PERSIST FAILED:",
                e,
            )