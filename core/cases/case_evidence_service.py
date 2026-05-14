import re
from typing import Any, Dict, List, Tuple

from core.utils.text_extraction import extract_text_from_bytes


SENSITIVE_PATTERNS = [
    ("CUI", r"\bCUI\b", 25),
    ("SSN", r"\b\d{3}-\d{2}-\d{4}\b", 40),
    ("EMAIL", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", 5),
    ("PASSWORD", r"\b(password|secret|token|api key|private key|secret key)\b", 35),
    ("EXPORT_CONTROL", r"\b(ITAR|EAR99|USML|export controlled|defense article)\b", 30),
]


def _safe_evidence_id(e: Dict[str, Any]) -> str:
    return str(e.get("evidence_id") or e.get("id") or "")


def _safe_name(e: Dict[str, Any]) -> str:
    return (
        e.get("suggested_name")
        or e.get("filename")
        or e.get("name")
        or f"Evidence {_safe_evidence_id(e)}"
    )


def dedupe_evidence(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    clean = []

    for e in evidence or []:
        if not isinstance(e, dict):
            continue

        eid = _safe_evidence_id(e)

        if not eid:
            continue

        if eid in seen:
            continue

        seen.add(eid)
        clean.append(e)

    return clean


def detect_sensitive_matches(text: str) -> List[Dict[str, Any]]:
    matches = []

    if not text:
        return matches

    for label, pattern, weight in SENSITIVE_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matches.append({
                "label": label,
                "value": m.group(),
                "start": m.start(),
                "end": m.end(),
                "weight": weight,
            })

    return matches


def score_matches(matches: List[Dict[str, Any]]) -> Tuple[int, str]:
    score = 0

    for m in matches or []:
        score += int(m.get("weight") or 0)

    score = min(score, 100)

    if score >= 75:
        return score, "CRITICAL"
    if score >= 50:
        return score, "HIGH"
    if score >= 25:
        return score, "MEDIUM"
    return score, "LOW"


def extract_evidence_text(ledger, evidence_item: Dict[str, Any], limit: int = 10000) -> str:
    eid = _safe_evidence_id(evidence_item)

    if not eid:
        return ""

    if not hasattr(ledger, "get_evidence_bytes"):
        return ""

    try:
        data = ledger.get_evidence_bytes(eid)

        if not data:
            return ""

        filename = _safe_name(evidence_item)

        try:
            text = extract_text_from_bytes(data, filename=filename)
        except TypeError:
            text = extract_text_from_bytes(data)

        return (text or "")[:limit]

    except Exception as ex:
        print(f"EVIDENCE TEXT EXTRACTION FAILED for {eid}: {ex}")
        return ""


def build_evidence_record(ledger, e: Dict[str, Any]) -> Dict[str, Any]:
    eid = _safe_evidence_id(e)
    name = _safe_name(e)

    text = extract_evidence_text(ledger, e)
    matches = detect_sensitive_matches(text)
    score, level = score_matches(matches)

    return {
        "id": eid,
        "name": name,
        "raw": e,
        "text": text,
        "matches": matches,
        "score": score,
        "level": level,
        "created_at_ms": e.get("created_at_ms") or e.get("created_ms") or 0,
        "sha256": e.get("sha256"),
        "source": e.get("source") or e.get("source_system") or "Unknown",
    }


def build_case_evidence_context(ledger, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    clean = dedupe_evidence(evidence)

    records = [
        build_evidence_record(ledger, e)
        for e in clean
    ]

    records.sort(
        key=lambda r: (
            r.get("score") or 0,
            r.get("created_at_ms") or 0,
        ),
        reverse=True,
    )

    clusters = cluster_evidence_records(records)

    return {
        "records": records,
        "clusters": clusters,
        "total": len(records),
        "critical": sum(1 for r in records if r["level"] == "CRITICAL"),
        "high": sum(1 for r in records if r["level"] == "HIGH"),
        "medium": sum(1 for r in records if r["level"] == "MEDIUM"),
        "low": sum(1 for r in records if r["level"] == "LOW"),
    }


def cluster_evidence_records(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    clusters = {}

    for r in records:
        labels = sorted(set(
            m.get("label")
            for m in r.get("matches", [])
            if m.get("label")
        ))

        if not labels:
            key = "General / Low Signal"
        else:
            key = " + ".join(labels)

        clusters.setdefault(key, []).append(r)

    return clusters


def render_highlighted_text(text: str, matches: List[Dict[str, Any]], filter_label: str | None = None) -> str:
    if not text:
        return ""

    active = []

    for m in matches or []:
        if filter_label and m.get("label") != filter_label:
            continue

        if isinstance(m.get("start"), int) and isinstance(m.get("end"), int):
            active.append(m)

    active.sort(key=lambda x: x["start"])

    output = ""
    last = 0

    color_map = {
        "CUI": "#ff4d4d",
        "SSN": "#ff9900",
        "EMAIL": "#3399ff",
        "PASSWORD": "#cc00ff",
        "EXPORT_CONTROL": "#ff3333",
    }

    for m in active:
        start = max(0, m["start"])
        end = min(len(text), m["end"])

        if start < last:
            continue

        label = m.get("label", "MATCH")
        color = color_map.get(label, "#777")

        output += text[last:start]
        output += (
            f"<span style='background:{color}; color:white; "
            f"padding:2px 4px; border-radius:4px;'>"
            f"[{label}] {text[start:end]}</span>"
        )

        last = end

    output += text[last:]

    return output