from core.cases.case_evidence_service import (
    build_case_evidence_context
)


def build_case_context(
    storage,
    case_id,
):

    ledger = storage.ledger

    data = ledger.get_case_details(
        case_id
    )

    case = data.get("case") or []
    alerts = data.get("alerts") or []
    evidence = data.get("evidence") or []

    evidence_ctx = build_case_evidence_context(
        ledger=ledger,
        evidence=evidence,
    )

    notes = []

    if hasattr(
        ledger,
        "get_case_notes"
    ):

        notes = (
            ledger.get_case_notes(
                case_id
            ) or []
        )

    timeline = []

    if hasattr(
        ledger,
        "get_case_timeline"
    ):

        timeline = (
            ledger.get_case_timeline(
                case_id
            ) or []
        )

    entities = []

    if hasattr(
        ledger,
        "get_case_entities"
    ):

        entities = (
            ledger.get_case_entities(
                case_id
            ) or []
        )

    relationships = []

    if hasattr(
        ledger,
        "get_case_relationships"
    ):

        relationships = (
            ledger.get_case_relationships(
                case_id
            ) or []
        )

    return {
        "case": case,
        "alerts": alerts,
        "evidence": evidence,
        "evidence_ctx": evidence_ctx,
        "notes": notes,
        "timeline": timeline,
        "entities": entities,
        "relationships": relationships,
    }