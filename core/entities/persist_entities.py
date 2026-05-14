import json
import time


def persist_entities(
    con,
    run_id,
    evidence_id,
    entities,
):

    now_ms = int(time.time() * 1000)

    for entity_type, values in entities.items():

        if entity_type == "entity_count":
            continue

        if not isinstance(values, list):
            continue

        for value in values:

            try:

                normalized = (
                    str(value)
                    .strip()
                    .lower()
                )

                con.execute(
                    """
                    INSERT INTO evidence_entities (
                        run_id,
                        evidence_id,
                        entity_type,
                        entity_value,
                        normalized_value,
                        created_at_ms,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        evidence_id,
                        entity_type,
                        str(value),
                        normalized,
                        now_ms,
                        json.dumps({}),
                    )
                )

            except Exception as e:

                print(
                    "⚠️ ENTITY PERSIST FAILED:",
                    entity_type,
                    value,
                    e,
                )