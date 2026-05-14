import re
from typing import Dict, List, Any


EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

PHONE_REGEX = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

IP_REGEX = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)

SSN_REGEX = re.compile(
    r"\b\d{3}-\d{2}-\d{4}\b"
)

CUI_REGEX = re.compile(
    r"\bCUI\b|Controlled Unclassified Information",
    re.IGNORECASE,
)

EXPORT_REGEX = re.compile(
    r"\bITAR\b|\bEAR99\b|\bUSML\b",
    re.IGNORECASE,
)

CONTRACT_REGEX = re.compile(

    r"\b(?:contract|po|purchase order)"
    r"[-:\s#]+"
    r"([A-Z0-9][A-Z0-9\-]{5,})\b",

    re.IGNORECASE,
)


def unique_clean(values):

    cleaned = []

    seen = set()

    for v in values:

        if not v:
            continue

        val = str(v).strip()

        if not val:
            continue

        if val in seen:
            continue

        seen.add(val)

        cleaned.append(val)

    return cleaned


def extract_entities(
    text: str,
) -> Dict[str, Any]:

    if not text:

        return {
            "emails": [],
            "phones": [],
            "ips": [],
            "ssns": [],
            "contracts": [],
            "cui_markings": [],
            "export_refs": [],
            "entity_count": 0,
        }

    emails = EMAIL_REGEX.findall(text)

    phones = PHONE_REGEX.findall(text)

    ips = IP_REGEX.findall(text)

    ssns = SSN_REGEX.findall(text)

    contracts = [
        m[0]
        for m in CONTRACT_REGEX.findall(text)
    ]

    cui_markings = CUI_REGEX.findall(text)

    export_refs = EXPORT_REGEX.findall(text)

    result = {

        "emails": unique_clean(emails),

        "phones": unique_clean(phones),

        "ips": unique_clean(ips),

        "ssns": unique_clean(ssns),

        "contracts": unique_clean(contracts),

        "cui_markings": unique_clean(cui_markings),

        "export_refs": unique_clean(export_refs),
    }

    result["entity_count"] = sum(
        len(v)
        for v in result.values()
        if isinstance(v, list)
    )

    return result