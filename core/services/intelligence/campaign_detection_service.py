from __future__ import annotations

import hashlib
import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_upper(value: Any) -> str:
    return str(value or "").upper().strip()


class CampaignDetectionService:
    """
    Campaign / coordinated activity detection engine.

    Identifies:
    - repeated entities
    - repeated senders
    - repeated evidence hashes
    - recurring export-control indicators
    - coordinated insider activity
    - cross-case operational clusters

    This becomes:
    intelligence correlation layer.
    """

    def __init__(
        self,
        ledger: Any,
        graph_service: Any = None,
        entity_resolution_service: Any = None,
    ):
        self.ledger = ledger
        self.graph_service = graph_service
        self.entity_resolution_service = entity_resolution_service

    # ------------------------------------------------------------------
    # Main Public APIs
    # ------------------------------------------------------------------

    def detect_campaign(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        entities: List[str],
        linked_cases: Optional[List[Dict[str, Any]]] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        linked_cases = linked_cases or []

        case_id = case.get("case_id") or case.get("id")

        resolved_entities = self._resolve_entities(entities)

        shared_hashes = self._find_shared_hashes(
            evidence=evidence,
            tenant_id=tenant_id,
        )

        repeated_senders = self._find_repeated_senders(
            evidence=evidence,
            tenant_id=tenant_id,
        )

        repeated_entities = self._find_repeated_entities(
            entities=resolved_entities,
            tenant_id=tenant_id,
        )

        insider_indicators = self._detect_insider_patterns(
            case=case,
            evidence=evidence,
            entities=resolved_entities,
        )

        export_indicators = self._detect_export_patterns(
            case=case,
            evidence=evidence,
            entities=resolved_entities,
        )

        coordinated_activity = self._detect_coordinated_activity(
            linked_cases=linked_cases,
            repeated_entities=repeated_entities,
            shared_hashes=shared_hashes,
            repeated_senders=repeated_senders,
        )

        confidence = self._calculate_campaign_confidence(
            linked_cases=linked_cases,
            repeated_entities=repeated_entities,
            shared_hashes=shared_hashes,
            repeated_senders=repeated_senders,
            insider_indicators=insider_indicators,
            export_indicators=export_indicators,
        )

        campaign_id = None

        if confidence >= 40:
            campaign_id = self._build_campaign_id(
                case_id=case_id,
                entities=resolved_entities,
                hashes=shared_hashes,
            )

        campaign_type = self._determine_campaign_type(
            insider_indicators=insider_indicators,
            export_indicators=export_indicators,
            coordinated_activity=coordinated_activity,
        )

        return {
            "campaign_id": campaign_id,
            "campaign_type": campaign_type,
            "confidence": confidence,
            "linked_case_count": len(linked_cases),
            "shared_hashes": shared_hashes,
            "repeated_senders": repeated_senders,
            "repeated_entities": repeated_entities,
            "insider_indicators": insider_indicators,
            "export_indicators": export_indicators,
            "coordinated_activity": coordinated_activity,
            "requires_escalation": confidence >= 70,
            "recommended_severity": self._recommended_severity(
                confidence=confidence,
                export_indicators=export_indicators,
                insider_indicators=insider_indicators,
            ),
            "generated_at_ms": _now_ms(),
            "engine": "CampaignDetectionService",
        }

    def scan_all_cases(
        self,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Global campaign sweep across all investigations.
        """

        cases = self._get_all_cases(tenant_id=tenant_id)

        campaigns = []

        for case in cases:
            try:
                case_id = case.get("case_id") or case.get("id")

                evidence = self._get_case_evidence(case_id)

                entities = self._extract_entities(
                    case=case,
                    evidence=evidence,
                )

                linked_cases = self._find_linked_cases(
                    case_id=case_id,
                    entities=entities,
                    evidence=evidence,
                    tenant_id=tenant_id,
                )

                campaign = self.detect_campaign(
                    case=case,
                    evidence=evidence,
                    entities=entities,
                    linked_cases=linked_cases,
                    tenant_id=tenant_id,
                )

                if campaign.get("campaign_id"):
                    campaigns.append({
                        "case_id": case_id,
                        "title": case.get("title"),
                        "campaign": campaign,
                    })

            except Exception:
                pass

        campaigns.sort(
            key=lambda x: int(
                x["campaign"].get("confidence") or 0
            ),
            reverse=True,
        )

        return campaigns

    # ------------------------------------------------------------------
    # Pattern Detection
    # ------------------------------------------------------------------

    def _find_shared_hashes(
        self,
        *,
        evidence: List[Dict[str, Any]],
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        hashes = set()

        for ev in evidence:
            sha = ev.get("sha256")
            if sha:
                hashes.add(str(sha))

        if not hashes:
            return []

        results = []

        all_cases = self._get_all_cases(tenant_id=tenant_id)

        for sha in hashes:

            matched_cases = []

            for case in all_cases:
                case_id = case.get("case_id") or case.get("id")

                other_evidence = self._get_case_evidence(case_id)

                for ev in other_evidence:
                    if str(ev.get("sha256")) == sha:
                        matched_cases.append({
                            "case_id": case_id,
                            "title": case.get("title"),
                        })
                        break

            if len(matched_cases) >= 2:
                results.append({
                    "sha256": sha,
                    "case_count": len(matched_cases),
                    "cases": matched_cases,
                })

        return results

    def _find_repeated_senders(
        self,
        *,
        evidence: List[Dict[str, Any]],
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        senders = set()

        for ev in evidence:
            sender = (
                ev.get("sender")
                or ev.get("from")
                or ev.get("email_from")
            )

            if sender:
                senders.add(str(sender).lower())

        if not senders:
            return []

        all_cases = self._get_all_cases(tenant_id=tenant_id)

        repeated = []

        for sender in senders:

            matched_cases = []

            for case in all_cases:
                case_id = case.get("case_id") or case.get("id")

                other_evidence = self._get_case_evidence(case_id)

                for ev in other_evidence:

                    other_sender = (
                        ev.get("sender")
                        or ev.get("from")
                        or ev.get("email_from")
                    )

                    if str(other_sender).lower() == sender:
                        matched_cases.append({
                            "case_id": case_id,
                            "title": case.get("title"),
                        })
                        break

            if len(matched_cases) >= 2:
                repeated.append({
                    "sender": sender,
                    "case_count": len(matched_cases),
                    "cases": matched_cases,
                })

        return repeated

    def _find_repeated_entities(
        self,
        *,
        entities: List[str],
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        if not entities:
            return []

        resolved = self._resolve_entities(entities)

        all_cases = self._get_all_cases(tenant_id=tenant_id)

        repeated = []

        for entity in resolved:

            matched_cases = []

            for case in all_cases:

                case_entities = (
                    case.get("entities")
                    or case.get("related_entities")
                    or []
                )

                case_entities = self._resolve_entities(case_entities)

                entity_set = {
                    _safe_upper(e)
                    for e in case_entities
                }

                if _safe_upper(entity) in entity_set:
                    matched_cases.append({
                        "case_id": case.get("case_id") or case.get("id"),
                        "title": case.get("title"),
                    })

            if len(matched_cases) >= 2:
                repeated.append({
                    "entity": entity,
                    "case_count": len(matched_cases),
                    "cases": matched_cases,
                })

        return repeated

    # ------------------------------------------------------------------
    # Insider / Export Detection
    # ------------------------------------------------------------------

    def _detect_insider_patterns(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        entities: List[str],
    ) -> List[Dict[str, Any]]:

        indicators = []

        blob = " ".join([
            str(case),
            str(evidence),
            " ".join(entities),
        ]).lower()

        patterns = {
            "personal_email_usage": [
                "gmail.com",
                "yahoo.com",
                "icloud.com",
                "proton.me",
            ],
            "credential_exposure": [
                "password",
                "api key",
                "secret key",
                "token",
            ],
            "mass_download_activity": [
                "mass download",
                "bulk export",
                "large transfer",
            ],
            "removable_media_usage": [
                "usb",
                "thumb drive",
                "removable media",
            ],
            "after_hours_activity": [
                "after hours",
                "weekend access",
                "late night",
            ],
        }

        for indicator, terms in patterns.items():

            for term in terms:

                if term in blob:
                    indicators.append({
                        "indicator": indicator,
                        "matched_term": term,
                        "severity": "HIGH",
                    })
                    break

        return indicators

    def _detect_export_patterns(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        entities: List[str],
    ) -> List[Dict[str, Any]]:

        indicators = []

        blob = " ".join([
            str(case),
            str(evidence),
            " ".join(entities),
        ]).upper()

        export_terms = [
            "ITAR",
            "EAR",
            "EAR99",
            "EXPORT CONTROL",
            "EXPORT_CONTROL",
            "CONTROLLED TECHNICAL INFORMATION",
            "CTI",
            "USML",
            "DEFENSE ARTICLE",
            "DEFENSE SERVICE",
        ]

        for term in export_terms:

            if term in blob:
                indicators.append({
                    "indicator": "export_control",
                    "matched_term": term,
                    "severity": "CRITICAL",
                })

        return indicators

    # ------------------------------------------------------------------
    # Coordinated Activity
    # ------------------------------------------------------------------

    def _detect_coordinated_activity(
        self,
        *,
        linked_cases: List[Dict[str, Any]],
        repeated_entities: List[Dict[str, Any]],
        shared_hashes: List[Dict[str, Any]],
        repeated_senders: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        signals = []

        if len(linked_cases) >= 3:
            signals.append("multiple_linked_cases")

        if shared_hashes:
            signals.append("shared_evidence_hashes")

        if repeated_senders:
            signals.append("repeated_senders")

        if repeated_entities:
            signals.append("shared_entities")

        confidence = min(
            100,
            len(signals) * 25,
        )

        return {
            "signals": signals,
            "confidence": confidence,
            "is_coordinated": confidence >= 50,
        }

    # ------------------------------------------------------------------
    # Confidence / Classification
    # ------------------------------------------------------------------

    def _calculate_campaign_confidence(
        self,
        *,
        linked_cases: List[Dict[str, Any]],
        repeated_entities: List[Dict[str, Any]],
        shared_hashes: List[Dict[str, Any]],
        repeated_senders: List[Dict[str, Any]],
        insider_indicators: List[Dict[str, Any]],
        export_indicators: List[Dict[str, Any]],
    ) -> int:

        score = 0

        score += min(len(linked_cases) * 10, 30)
        score += min(len(repeated_entities) * 8, 20)
        score += min(len(shared_hashes) * 25, 50)
        score += min(len(repeated_senders) * 12, 25)
        score += min(len(insider_indicators) * 10, 25)
        score += min(len(export_indicators) * 15, 35)

        return min(score, 100)

    def _determine_campaign_type(
        self,
        *,
        insider_indicators: List[Dict[str, Any]],
        export_indicators: List[Dict[str, Any]],
        coordinated_activity: Dict[str, Any],
    ) -> str:

        if export_indicators:
            return "EXPORT_CONTROL_CAMPAIGN"

        if insider_indicators:
            return "INSIDER_THREAT_CAMPAIGN"

        if coordinated_activity.get("is_coordinated"):
            return "COORDINATED_ACTIVITY"

        return "GENERAL_CAMPAIGN"

    def _recommended_severity(
        self,
        *,
        confidence: int,
        export_indicators: List[Dict[str, Any]],
        insider_indicators: List[Dict[str, Any]],
    ) -> str:

        if export_indicators:
            return "CRITICAL"

        if confidence >= 80:
            return "CRITICAL"

        if confidence >= 60:
            return "HIGH"

        if insider_indicators:
            return "HIGH"

        if confidence >= 40:
            return "MEDIUM"

        return "LOW"

    # ------------------------------------------------------------------
    # Campaign ID
    # ------------------------------------------------------------------

    def _build_campaign_id(
        self,
        *,
        case_id: Any,
        entities: List[str],
        hashes: List[Dict[str, Any]],
    ) -> str:

        parts = [
            str(case_id),
        ]

        for entity in entities[:5]:
            parts.append(str(entity))

        for h in hashes[:3]:
            parts.append(str(h.get("sha256")))

        raw = "|".join(parts)

        digest = hashlib.sha256(
            raw.encode()
        ).hexdigest()[:12]

        return f"CAMP-{digest.upper()}"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_entities(
        self,
        entities: List[str],
    ) -> List[str]:

        if self.entity_resolution_service is not None:

            for method_name in [
                "resolve_entities",
                "normalize_entities",
            ]:

                method = getattr(
                    self.entity_resolution_service,
                    method_name,
                    None,
                )

                if callable(method):
                    try:
                        return method(entities)
                    except Exception:
                        pass

        alias_map = {
            "LOCKHEED": "LOCKHEED MARTIN",
            "LMT": "LOCKHEED MARTIN",
            "RAYTHEON": "RTX",
            "NORTHROP": "NORTHROP GRUMMAN",
        }

        resolved = []

        for entity in entities:
            key = _safe_upper(entity)
            resolved.append(
                alias_map.get(key, key)
            )

        return sorted(list(set(resolved)))

    def _extract_entities(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> List[str]:

        raw = []

        for field in [
            "entities",
            "related_entities",
            "detected_entities",
            "tags",
            "categories",
            "flags",
        ]:
            value = case.get(field)

            if isinstance(value, list):
                raw.extend(value)

        for ev in evidence:
            for field in [
                "entities",
                "detected_entities",
                "tags",
                "categories",
                "flags",
            ]:
                value = ev.get(field)

                if isinstance(value, list):
                    raw.extend(value)

        cleaned = []

        for item in raw:
            if item is None:
                continue

            if isinstance(item, dict):
                value = (
                    item.get("name")
                    or item.get("value")
                    or item.get("label")
                )
            else:
                value = str(item)

            value = value.strip()

            if value:
                cleaned.append(value)

        return sorted(list(set(cleaned)))

    # ------------------------------------------------------------------
    # Graph Adapters
    # ------------------------------------------------------------------

    def _find_linked_cases(
        self,
        *,
        case_id: Any,
        entities: List[str],
        evidence: List[Dict[str, Any]],
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        if self.graph_service is not None:

            for method_name in [
                "find_linked_cases",
                "get_linked_cases",
            ]:

                method = getattr(
                    self.graph_service,
                    method_name,
                    None,
                )

                if callable(method):
                    try:
                        return method(
                            case_id=case_id,
                            entities=entities,
                            evidence=evidence,
                            tenant_id=tenant_id,
                        )
                    except Exception:
                        pass

        return []

    # ------------------------------------------------------------------
    # Ledger Adapters
    # ------------------------------------------------------------------

    def _get_case_evidence(
        self,
        case_id: Any,
    ) -> List[Dict[str, Any]]:

        for method_name in [
            "get_case_evidence",
            "list_case_evidence",
            "fetch_case_evidence",
        ]:

            method = getattr(
                self.ledger,
                method_name,
                None,
            )

            if callable(method):
                try:
                    result = method(case_id)
                    if result:
                        return result
                except Exception:
                    pass

        return []

    def _get_all_cases(
        self,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        for method_name in [
            "get_cases",
            "list_cases",
            "fetch_cases",
            "get_all_cases",
        ]:

            method = getattr(
                self.ledger,
                method_name,
                None,
            )

            if callable(method):
                try:
                    if tenant_id:
                        return method(
                            tenant_id=tenant_id
                        )

                    return method()

                except TypeError:
                    try:
                        return method(tenant_id)
                    except Exception:
                        pass

                except Exception:
                    pass

        return []