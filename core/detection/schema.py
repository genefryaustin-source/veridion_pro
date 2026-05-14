from typing import Dict, Any


def normalize_detection(raw: dict | None) -> dict:
    if not isinstance(raw, dict):
        raw = {}

    flags = raw.get("flags") or []
    matches = raw.get("matches") or []
    rule_hits = raw.get("rule_hits") or []

    # ---------------------------------------
    # 🔥 DERIVE CATEGORIES PROPERLY
    # ---------------------------------------
    categories = set(raw.get("categories") or [])

    for m in matches:
        if isinstance(m, str):
            categories.add(m)

    for r in rule_hits:
        if isinstance(r, dict):
            categories.add(r.get("category"))

    categories = [c for c in categories if c]

    # ---------------------------------------
    # 🔥 HIT COUNT
    # ---------------------------------------
    hit_count = raw.get("hit_count")

    if hit_count is None:
        hit_count = len(rule_hits) if rule_hits else len(matches)


    # ---------------------------------------
    # 🔥 PRIMARY CATEGORY PRIORITY MODEL
    # ---------------------------------------
    CATEGORY_PRIORITY = {

        "EXPORT_CONTROL": 100,

        "CONTROLLED_TECHNICAL_INFORMATION": 95,

        "ITAR": 95,

        "EAR99": 94,

        "CUI": 90,

        "PHI": 85,

        "PII_SSN": 80,

        "PII": 75,

        "FINANCIAL_DATA": 70,

        "PERSONAL_DATA": 60,

        "IP": 50,

        "UNCATEGORIZED": 0,
    }

    primary_category = (
        raw.get("primary_category")
    )

    if not primary_category and categories:
        primary_category = max(
            categories,
            key=lambda c: CATEGORY_PRIORITY.get(
                c,
                1
            )
        )

    # ---------------------------------------
    # 🔥 DETECTION FLAGS
    # ---------------------------------------
    CUI_CATEGORIES = {
        "CUI",
        "EXPORT_CONTROL",
        "CONTROLLED_TECHNICAL_INFORMATION",
        "ITAR",
        "EAR99",
    }

    # ✅ ANY REAL DETECTION
    has_detection = hit_count > 0

    # ✅ STRICT CUI DETERMINATION
    has_cui = (
            hit_count > 0
            and primary_category in CUI_CATEGORIES
    )

    # ---------------------------------------
    # 🔥 SEVERITY MODEL (CORRECTED)
    # ---------------------------------------
    severity = "NONE"

    if not has_detection:
        severity = "NONE"

    elif "CREDENTIAL" in categories:
        severity = "CRITICAL"

    elif primary_category == "EXPORT_CONTROL":
        severity = "CRITICAL"

    elif primary_category == "CONTROLLED_TECHNICAL_INFORMATION":
        severity = "HIGH"

    elif primary_category == "CUI":
        severity = "HIGH"

    elif primary_category == "PHI":
        severity = "HIGH"

    elif primary_category == "PII_SSN":
        severity = "HIGH"

    elif primary_category == "PERSONAL_DATA":
        severity = "MEDIUM"

    elif primary_category == "FINANCIAL_DATA":
        severity = "MEDIUM"

    elif primary_category == "CUI_MISMARKED":
        severity = "HIGH"

    else:
        severity = "LOW"

    return {
        "has_detection": has_detection,
        "has_cui": has_cui,
        "flags": categories,
        "categories": categories,
        "matches": matches,
        "rule_hits": rule_hits,
        "hit_count": hit_count,
        "primary_category": primary_category or "UNCATEGORIZED",
        "severity": severity,
        "confidence": raw.get("confidence", "LOW"),
        "scores": raw.get("scores", {}),
        "raw": raw,
    }