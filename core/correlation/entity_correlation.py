import json


ENTITY_PRIORITY = [

    ("ssns", "SSN_MATCH"),

    ("contracts", "CONTRACT_MATCH"),

    ("export_refs", "EXPORT_REF_MATCH"),

    ("emails", "EMAIL_ENTITY_MATCH"),

    ("ips", "IP_ENTITY_MATCH"),

    ("phones", "PHONE_ENTITY_MATCH"),

]


def correlate_entities(
    con,
    evidence_id,
    entities,
):

    correlations = []

    for entity_type, correlation_type in ENTITY_PRIORITY:

        values = entities.get(entity_type)

        if not values:
            continue

        for value in values:

            normalized = (
                str(value)
                .strip()
                .lower()
            )

            rows = con.execute(
                """
                SELECT DISTINCT
                    evidence_id
                FROM evidence_entities
                WHERE normalized_value = ?
                """,
                (normalized,)
            ).fetchall()

            for row in rows:

                related_evidence_id = row[0]

                if (
                    related_evidence_id
                    == evidence_id
                ):
                    continue

                correlation = {

                    "type": correlation_type,

                    "entity_type": entity_type,

                    "entity_value": value,

                    "related_evidence_id": related_evidence_id,
                }

                correlations.append(
                    correlation
                )

    return correlations