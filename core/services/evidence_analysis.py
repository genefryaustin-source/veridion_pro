import re
from core.classify.rules import run_rules, score_hits, resolve_category


# ---------------------------------------
# 🔇 NOISE FILTER (ADD THIS AT TOP)
# ---------------------------------------
def is_noise_email(text: str) -> bool:
    text = (text or "").lower()

    noise_patterns = [
        "paypal",
        "unsubscribe",
        "view online",
        "direct deposit",
        "newsletter",
        "marketing",
    ]

    return any(p in text for p in noise_patterns)


def analyze_evidence_text(text: str):
    text = text or ""
    text_lower = text.lower()

    # ---------------------------------------
    # 🔇 NOISE EMAIL FILTER (RUN FIRST)
    # ---------------------------------------
    if is_noise_email(text_lower):
        return {
            "has_cui": False,
            "flags": [],
            "categories": [],
            "matches": [],
            "rule_hits": [],
            "hit_count": 0,
            "primary_category": "NOISE",
            "scores": {},
            "confidence": "LOW",
            "severity": "NONE",
            "raw": {"reason": "noise_email_filtered"},
        }

    # ---------------------------------------
    # 🚀 PRIMARY RULE ENGINE
    # ---------------------------------------
    hits = run_rules(text)
    scores = score_hits(hits)
    primary_category = resolve_category(scores)

    categories = list(set([h.get("category") for h in hits if h.get("category")]))
    hit_count = len(hits)

    # ---------------------------------------
    # 🔐 LEGACY / SUPPLEMENTAL SIGNALS
    # ---------------------------------------
    flags = []
    matches = []

    if any(k in text_lower for k in ["password", "passwd", "pwd"]):
        flags.append("CREDENTIAL")
        matches.append({"type": "credential", "value": "keyword"})

    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
        flags.append("PII_SSN")
        matches.append({"type": "ssn", "value": "pattern"})

    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        flags.append("EMAIL")
        matches.append({"type": "email", "value": "pattern"})

    if re.search(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", text):
        flags.append("FINANCIAL")
        matches.append({"type": "card", "value": "pattern"})

    # ---------------------------------------
    # 🔥 SAFER EXPORT CONTROL BOOST
    # ---------------------------------------
    EXPORT_TERMS = [
        "itar",
        "export controlled",
        "defense article",
        "usml",
        "ear99",
        "export administration regulations",
    ]

    if any(term in text_lower for term in EXPORT_TERMS):
        scores["EXPORT_CONTROL"] = scores.get("EXPORT_CONTROL", 0) + 2

    # ---------------------------------------
    # 🧠 FINAL CATEGORY RESOLVE
    # ---------------------------------------
    primary_category = resolve_category(scores)

    # ---------------------------------------
    # 🔥 CORRECT CUI LOGIC
    # ---------------------------------------
    CUI_CATEGORIES = {
        "CUI",
        "EXPORT_CONTROL",
        "CONTROLLED_TECHNICAL_INFORMATION",
        "ITAR",
        "EAR99",
    }

    # ---------------------------------------
    # ✅ TRUE CUI DETERMINATION (FIXED)
    # ---------------------------------------
    has_cui = hit_count > 0

    # ---------------------------------------
    # 🔥 SEVERITY MODEL (CONSISTENT)
    # ---------------------------------------
    # ---------------------------------------
    # 🔥 SEVERITY MODEL (CONSISTENT)
    # ---------------------------------------
    severity = "NONE"

    if not has_cui:
        severity = "NONE"

    elif "CREDENTIAL" in flags:
        severity = "CRITICAL"

    elif primary_category == "EXPORT_CONTROL":
        severity = "CRITICAL" if hit_count >= 1 else "HIGH"

    elif primary_category == "CUI":
        severity = "HIGH" if hit_count >= 2 else "MEDIUM"

    elif primary_category == "FINANCIAL_DATA":
        severity = "MEDIUM"

    else:
        severity = "LOW"

    #if "CREDENTIAL" in flags:
        #severity = "CRITICAL"
    #elif primary_category == "EXPORT_CONTROL":
        #severity = "CRITICAL"
    #elif primary_category == "CUI":
        #severity = "HIGH"
    #elif "PII_SSN" in flags:
        #severity = "HIGH"
    #elif "FINANCIAL" in flags:
        #severity = "MEDIUM"

    # ---------------------------------------
    # 🧠 CONFIDENCE
    # ---------------------------------------
    confidence = "LOW"
    if hit_count >= 5:
        confidence = "HIGH"
    elif hit_count >= 2:
        confidence = "MEDIUM"

    # ---------------------------------------
    # 🧪 DEBUG
    # ---------------------------------------
    if has_cui:
        print(f"🚨 PRIMARY CATEGORY: {primary_category}")
        print(f"🧠 SCORES: {scores}")
        print(f"🧠 RULE HITS: {hits}")

    # ---------------------------------------
    # ✅ FINAL OUTPUT (STANDARDIZED)
    # ---------------------------------------
    return {
        "has_cui": has_cui,
        "primary_category": primary_category or "UNCATEGORIZED",
        "categories": categories,
        "flags": flags,
        "scores": scores,
        "hit_count": hit_count,
        "matches": matches,
        "rule_hits": hits,
        "confidence": confidence,
        "severity": severity,
        "raw": {
            "hits": hits,
            "text_length": len(text),
        },
    }