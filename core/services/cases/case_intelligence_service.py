import json
import statistics
from typing import Dict, Any, List


# ---------------------------------------------------------
# SAFE HELPERS
# ---------------------------------------------------------

CRITICAL_CATEGORIES = {
    "EXPORT_CONTROL",
    "ITAR",
    "CONTROLLED_TECHNICAL_INFORMATION",
}

HIGH_CATEGORIES = {
    "CUI",
    "PII",
    "PHI",
    "FINANCIAL_DATA",
    "CREDENTIAL",
}


def _safe_json(value):
    if not value:
        return {}

    if isinstance(value, dict):
        return value

    try:
        return json.loads(value)
    except Exception:
        return {}


def _safe_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


# ---------------------------------------------------------
# MAIN INTELLIGENCE ENGINE
# ---------------------------------------------------------

def analyze_case_intelligence(storage, case_id) -> Dict[str, Any]:
    """
    Primary intelligence orchestration function.

    This powers:
    - intelligence_tab.py
    - risk scoring
    - escalation logic
    - executive summaries
    - future AI orchestration
    """

    ledger = storage.ledger

    findings = []
    recommendations = []
    evidence_items = []
    categories = set()
    severities = []
    timeline = []

    risk_score = 0

    # ---------------------------------------------------------
    # LOAD EVIDENCE
    # ---------------------------------------------------------

    try:
        evidence_rows = ledger.get_case_evidence(case_id)
    except Exception:
        evidence_rows = []

    # ---------------------------------------------------------
    # PROCESS EVIDENCE
    # ---------------------------------------------------------

    for row in evidence_rows:

        evidence_id = row.get("evidence_id")

        try:
            evidence = ledger.get_evidence_record(evidence_id)
        except Exception:
            evidence = None

        if not evidence:
            continue

        evidence_items.append(evidence)

        metadata = _safe_json(
            evidence.get("metadata_json")
            or evidence.get("metadata")
        )

        detection = _safe_json(
            metadata.get("cui_detection")
            or metadata.get("detection")
            or {}
        )

        # ---------------------------------------------------------
        # CATEGORY EXTRACTION
        # ---------------------------------------------------------

        detected_categories = set(
            _safe_list(
                detection.get("categories")
                or detection.get("flags")
                or []
            )
        )

        categories.update(detected_categories)

        hit_count = detection.get("hit_count", 0)

        severity = str(
            detection.get("severity", "LOW")
        ).upper()

        severities.append(severity)

        # ---------------------------------------------------------
        # RISK SCORING
        # ---------------------------------------------------------

        if detected_categories & CRITICAL_CATEGORIES:
            risk_score += 40

            findings.append(
                f"Critical export-control material detected in evidence {evidence_id}"
            )

            recommendations.append(
                "Immediate legal/compliance escalation recommended"
            )

        elif detected_categories & HIGH_CATEGORIES:
            risk_score += 20

            findings.append(
                f"Sensitive regulated data detected in evidence {evidence_id}"
            )

        elif hit_count > 0:
            risk_score += 10

        # ---------------------------------------------------------
        # MATCH DETAILS
        # ---------------------------------------------------------

        matches = _safe_list(
            detection.get("matches")
        )

        if matches:
            findings.append(
                f"{len(matches)} detection matches identified in evidence {evidence_id}"
            )

        # ---------------------------------------------------------
        # TIMELINE EVENTS
        # ---------------------------------------------------------

        timeline.append({
            "timestamp": evidence.get("created_at_ms"),
            "event": f"Evidence added: {evidence_id}",
            "severity": severity,
        })

    # ---------------------------------------------------------
    # ALERT ANALYSIS
    # ---------------------------------------------------------

    try:
        alerts = ledger.get_case_alerts(case_id)
    except Exception:
        alerts = []

    alert_count = len(alerts)

    if alert_count >= 5:
        risk_score += 15
        findings.append(
            f"Case contains elevated alert volume ({alert_count})"
        )

    # ---------------------------------------------------------
    # CASE EVENTS
    # ---------------------------------------------------------

    try:
        case_events = ledger.get_case_events(case_id)
    except Exception:
        case_events = []

    for evt in case_events:

        event_type = evt.get("event_type", "")

        timeline.append({
            "timestamp": evt.get("created_at_ms"),
            "event": event_type,
            "severity": evt.get("severity", "INFO"),
        })

        if "ESCALATED" in event_type.upper():
            risk_score += 10

        if "CONTAINMENT" in event_type.upper():
            findings.append(
                "Containment actions were executed"
            )

    # ---------------------------------------------------------
    # ANALYST OVERRIDE DETECTION
    # ---------------------------------------------------------

    try:
        overrides = ledger.get_case_overrides(case_id)
    except Exception:
        overrides = []

    if overrides:
        risk_score += 5

        findings.append(
            f"{len(overrides)} analyst override(s) detected"
        )

        recommendations.append(
            "Review analyst override rationale"
        )

    # ---------------------------------------------------------
    # NORMALIZE SCORE
    # ---------------------------------------------------------

    risk_score = min(risk_score, 100)

    # ---------------------------------------------------------
    # DETERMINE SEVERITY
    # ---------------------------------------------------------

    if risk_score >= 75:
        severity = "CRITICAL"

    elif risk_score >= 50:
        severity = "HIGH"

    elif risk_score >= 25:
        severity = "MEDIUM"

    else:
        severity = "LOW"

    # ---------------------------------------------------------
    # SUMMARY GENERATION
    # ---------------------------------------------------------

    summary = (
        f"Case {case_id} contains "
        f"{len(evidence_items)} evidence item(s), "
        f"{alert_count} alert(s), "
        f"and computed risk severity of {severity}."
    )

    # ---------------------------------------------------------
    # RETURN STRUCTURE
    # ---------------------------------------------------------

    return {
        "case_id": case_id,
        "risk_score": risk_score,
        "severity": severity,
        "summary": summary,
        "findings": findings,
        "recommendations": recommendations,
        "categories": sorted(list(categories)),
        "timeline": sorted(
            timeline,
            key=lambda x: x.get("timestamp") or 0
        ),
        "evidence_count": len(evidence_items),
        "alert_count": alert_count,
        "override_count": len(overrides),
    }