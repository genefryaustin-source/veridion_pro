from core.classify.detect import detect_cui
from core.services.evidence_analysis import analyze_evidence_text

from core.detection.schema import normalize_detection


# ---------------------------------------
# 🔇 NOISE FILTER (EMAIL FALSE POSITIVES)
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

def analyze_text(text: str) -> dict:
    """
    Unified detection entry point.
    Combines legacy + advanced detection safely.
    """

    results = []

    # ---------------------------------------
    # 🔹 RUN DETECTION ENGINES
    # ---------------------------------------
    try:
        r1 = detect_cui(text)
        results.append(r1)
    except Exception as e:
        print("⚠️ detect_cui failed:", e)

    try:
        r2 = analyze_evidence_text(text)
        results.append(r2)
    except Exception as e:
        print("⚠️ analyze_evidence_text failed:", e)

    # ---------------------------------------
    # 🔹 NORMALIZE INPUTS
    # ---------------------------------------
    normalized = [normalize_detection(r) for r in results if r]


    # ---------------------------------------
    # 🔥 MERGE (FIXED)
    # ---------------------------------------
    combined = {
        "flags": set(),  # OK (strings)
        "matches": [],  # MUST be list (dicts)
        "rule_hits": [],
        "scores": {},
    }

    seen_hits = set()
    seen_matches = set()

    for r in normalized:

        # ✅ FLAGS (strings → safe for set)
        combined["flags"].update(r.get("flags", []))

        # ✅ MATCHES (dicts → dedupe manually)
        for m in r.get("matches", []):
            key = str(m)  # safe hash
            if key not in seen_matches:
                seen_matches.add(key)
                combined["matches"].append(m)

        # ✅ RULE HITS (already correct)
        for hit in r.get("rule_hits", []):
            key = (
                hit.get("rule"),
                hit.get("match"),
                hit.get("category"),
            )

            if key not in seen_hits:
                seen_hits.add(key)
                combined["rule_hits"].append(hit)

        # ✅ SCORES (safe max merge)
        for k, v in r.get("scores", {}).items():
            combined["scores"][k] = max(
                combined["scores"].get(k, 0),
                v
            )

    # ---------------------------------------
    # 🔥 FINAL NORMALIZATION
    # ---------------------------------------
    combined["flags"] = list(combined["flags"])
    combined["hit_count"] = len(combined["rule_hits"])

    return normalize_detection(combined)