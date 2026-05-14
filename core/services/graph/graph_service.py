from __future__ import annotations

import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_upper(value: Any) -> str:
    return str(value or "").upper().strip()


class GraphService:
    """
    Case / evidence / entity graph intelligence service.

    Core model:
        CASE -> EVIDENCE
        EVIDENCE -> ENTITY
        ENTITY -> ENTITY
        ENTITY -> CASE
        CASE -> CASE

    Designed for:
    - relationship scoring
    - evidence pivots
    - entity pivots
    - linked case discovery
    - graph risk support
    - analyst graph exploration
    """

    def __init__(
        self,
        ledger: Any,
        entity_resolution_service: Any = None,
    ):
        self.ledger = ledger
        self.entity_resolution_service = entity_resolution_service

    # ------------------------------------------------------------------
    # Main Public API
    # ------------------------------------------------------------------

    def build_case_graph(
        self,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        case = self._get_case(case_id)
        evidence = self._get_case_evidence(case_id)
        entities = self.extract_entities(case=case, evidence=evidence)
        entities = self.resolve_entities(entities)

        linked_cases = self.find_linked_cases(
            case_id=case_id,
            entities=entities,
            evidence=evidence,
            tenant_id=tenant_id,
        )

        nodes = []
        edges = []

        case_node_id = f"case:{case_id}"

        nodes.append({
            "id": case_node_id,
            "type": "CASE",
            "label": case.get("title") or str(case_id),
            "case_id": case_id,
            "severity": case.get("severity") or case.get("priority"),
            "status": case.get("status"),
        })

        for ev in evidence:
            ev_id = ev.get("evidence_id") or ev.get("id") or ev.get("sha256")
            if not ev_id:
                continue

            evidence_node_id = f"evidence:{ev_id}"

            nodes.append({
                "id": evidence_node_id,
                "type": "EVIDENCE",
                "label": ev.get("filename") or ev.get("name") or str(ev_id),
                "evidence_id": ev_id,
                "sha256": ev.get("sha256"),
            })

            edges.append({
                "source": case_node_id,
                "target": evidence_node_id,
                "type": "CASE_HAS_EVIDENCE",
                "score": 100,
            })

        for entity in entities:
            entity_node_id = f"entity:{entity}"

            nodes.append({
                "id": entity_node_id,
                "type": "ENTITY",
                "label": entity,
            })

            edges.append({
                "source": case_node_id,
                "target": entity_node_id,
                "type": "CASE_HAS_ENTITY",
                "score": 80,
            })

        for linked in linked_cases:
            linked_case_id = linked.get("case_id")
            if not linked_case_id:
                continue

            linked_node_id = f"case:{linked_case_id}"

            nodes.append({
                "id": linked_node_id,
                "type": "CASE",
                "label": linked.get("title") or str(linked_case_id),
                "case_id": linked_case_id,
            })

            edges.append({
                "source": case_node_id,
                "target": linked_node_id,
                "type": linked.get("relationship") or "CASE_LINKED_CASE",
                "score": linked.get("score", 50),
                "shared_entities": linked.get("shared_entities", []),
                "shared_hashes": linked.get("shared_hashes", []),
            })

        return {
            "case_id": case_id,
            "nodes": self._dedupe_nodes(nodes),
            "edges": self._dedupe_edges(edges),
            "linked_cases": linked_cases,
            "entities": entities,
            "evidence_count": len(evidence),
            "generated_at_ms": _now_ms(),
        }

    def find_linked_cases(
        self,
        case_id: Any,
        entities: Optional[List[str]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        case = self._get_case(case_id)

        if entities is None:
            evidence = evidence or self._get_case_evidence(case_id)
            entities = self.extract_entities(case=case, evidence=evidence)

        evidence = evidence or self._get_case_evidence(case_id)

        entities = self.resolve_entities(entities)

        current_entity_set = {
            _safe_upper(e)
            for e in entities
            if e
        }

        current_hashes = {
            str(ev.get("sha256"))
            for ev in evidence
            if ev.get("sha256")
        }

        current_filenames = {
            _safe_upper(ev.get("filename") or ev.get("name"))
            for ev in evidence
            if ev.get("filename") or ev.get("name")
        }

        linked = []

        all_cases = self._get_all_cases(tenant_id=tenant_id)

        for other in all_cases:
            other_id = other.get("case_id") or other.get("id")

            if str(other_id) == str(case_id):
                continue

            other_evidence = self._get_case_evidence(other_id)

            other_entities = self.extract_entities(
                case=other,
                evidence=other_evidence,
            )

            other_entities = self.resolve_entities(other_entities)

            other_entity_set = {
                _safe_upper(e)
                for e in other_entities
                if e
            }

            other_hashes = {
                str(ev.get("sha256"))
                for ev in other_evidence
                if ev.get("sha256")
            }

            other_filenames = {
                _safe_upper(ev.get("filename") or ev.get("name"))
                for ev in other_evidence
                if ev.get("filename") or ev.get("name")
            }

            shared_entities = sorted(list(current_entity_set & other_entity_set))
            shared_hashes = sorted(list(current_hashes & other_hashes))
            shared_filenames = sorted(list(current_filenames & other_filenames))

            score = self.score_case_relationship(
                shared_entities=shared_entities,
                shared_hashes=shared_hashes,
                shared_filenames=shared_filenames,
                other_case=other,
            )

            if score <= 0:
                continue

            linked.append({
                "case_id": other_id,
                "title": other.get("title"),
                "relationship": self._relationship_type(
                    shared_entities=shared_entities,
                    shared_hashes=shared_hashes,
                    shared_filenames=shared_filenames,
                ),
                "score": score,
                "shared_entities": shared_entities,
                "shared_hashes": shared_hashes,
                "shared_filenames": shared_filenames,
                "severity": other.get("severity") or other.get("priority"),
                "status": other.get("status"),
            })

        linked.sort(
            key=lambda x: int(x.get("score") or 0),
            reverse=True,
        )

        return linked

    def score_case_relationship(
        self,
        *,
        shared_entities: List[str],
        shared_hashes: List[str],
        shared_filenames: List[str],
        other_case: Optional[Dict[str, Any]] = None,
    ) -> int:
        score = 0

        score += min(len(shared_entities) * 20, 60)
        score += min(len(shared_hashes) * 50, 100)
        score += min(len(shared_filenames) * 15, 45)

        severity = _safe_upper(
            (other_case or {}).get("severity")
            or (other_case or {}).get("priority")
        )

        if severity == "CRITICAL":
            score += 15
        elif severity == "HIGH":
            score += 10

        return min(score, 100)

    def get_entity_pivots(
        self,
        entity: str,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        resolved = self.resolve_entities([entity])
        entity_key = _safe_upper(resolved[0] if resolved else entity)

        cases = self._get_all_cases(tenant_id=tenant_id)

        matched_cases = []
        matched_evidence = []

        for case in cases:
            case_id = case.get("case_id") or case.get("id")
            evidence = self._get_case_evidence(case_id)

            entities = self.extract_entities(
                case=case,
                evidence=evidence,
            )
            entities = self.resolve_entities(entities)

            entity_set = {
                _safe_upper(e)
                for e in entities
            }

            if entity_key in entity_set:
                matched_cases.append({
                    "case_id": case_id,
                    "title": case.get("title"),
                    "severity": case.get("severity") or case.get("priority"),
                    "status": case.get("status"),
                })

                for ev in evidence:
                    matched_evidence.append({
                        "case_id": case_id,
                        "evidence_id": ev.get("evidence_id") or ev.get("id"),
                        "filename": ev.get("filename") or ev.get("name"),
                        "sha256": ev.get("sha256"),
                    })

        return {
            "entity": entity_key,
            "matched_cases": matched_cases,
            "matched_evidence": matched_evidence,
            "case_count": len(matched_cases),
            "evidence_count": len(matched_evidence),
            "generated_at_ms": _now_ms(),
        }

    def get_evidence_pivots(
        self,
        sha256: str,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        cases = self._get_all_cases(tenant_id=tenant_id)

        matched_cases = []
        matched_evidence = []

        for case in cases:
            case_id = case.get("case_id") or case.get("id")
            evidence = self._get_case_evidence(case_id)

            for ev in evidence:
                if str(ev.get("sha256")) == str(sha256):
                    matched_cases.append({
                        "case_id": case_id,
                        "title": case.get("title"),
                        "severity": case.get("severity") or case.get("priority"),
                        "status": case.get("status"),
                    })

                    matched_evidence.append({
                        "case_id": case_id,
                        "evidence_id": ev.get("evidence_id") or ev.get("id"),
                        "filename": ev.get("filename") or ev.get("name"),
                        "sha256": ev.get("sha256"),
                    })

        return {
            "sha256": sha256,
            "matched_cases": matched_cases,
            "matched_evidence": matched_evidence,
            "case_count": len(matched_cases),
            "evidence_count": len(matched_evidence),
            "generated_at_ms": _now_ms(),
        }

    def summarize_graph(
        self,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        graph = self.build_case_graph(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        node_types = Counter(
            node.get("type")
            for node in graph.get("nodes", [])
        )

        edge_types = Counter(
            edge.get("type")
            for edge in graph.get("edges", [])
        )

        linked_cases = graph.get("linked_cases", [])

        max_relationship_score = 0

        if linked_cases:
            max_relationship_score = max(
                int(c.get("score") or 0)
                for c in linked_cases
            )

        return {
            "case_id": case_id,
            "node_counts": dict(node_types),
            "edge_counts": dict(edge_types),
            "linked_case_count": len(linked_cases),
            "entity_count": len(graph.get("entities", [])),
            "evidence_count": graph.get("evidence_count", 0),
            "max_relationship_score": max_relationship_score,
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Entity Extraction
    # ------------------------------------------------------------------

    def extract_entities(
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

            blob = " ".join([
                str(ev.get("subject") or ""),
                str(ev.get("sender") or ""),
                str(ev.get("recipient") or ""),
                str(ev.get("filename") or ""),
                str(ev.get("name") or ""),
                str(ev.get("metadata") or ""),
                str(ev.get("details") or ""),
            ]).upper()

            markers = [
                "ITAR",
                "EAR",
                "EAR99",
                "CUI",
                "EXPORT_CONTROL",
                "EXPORT CONTROL",
                "CONTROLLED TECHNICAL INFORMATION",
                "CTI",
                "USML",
                "LOCKHEED",
                "LOCKHEED MARTIN",
                "LMT",
                "BOEING",
                "RAYTHEON",
                "RTX",
                "NORTHROP",
                "NORTHROP GRUMMAN",
                "SUPPLIER",
                "DEFENSE ARTICLE",
                "DEFENSE SERVICE",
            ]

            for marker in markers:
                if marker in blob:
                    raw.append(marker)

        cleaned = []

        for item in raw:
            if item is None:
                continue

            if isinstance(item, dict):
                value = (
                    item.get("name")
                    or item.get("value")
                    or item.get("label")
                    or item.get("entity")
                )
            else:
                value = str(item)

            value = value.strip()

            if value:
                cleaned.append(value)

        return sorted(list(set(cleaned)))

    def resolve_entities(
        self,
        entities: List[str],
    ) -> List[str]:
        if self.entity_resolution_service is not None:
            for method_name in [
                "resolve_entities",
                "normalize_entities",
                "dedupe_entities",
            ]:
                method = getattr(self.entity_resolution_service, method_name, None)
                if callable(method):
                    try:
                        return method(entities)
                    except Exception:
                        pass

        alias_map = {
            "LOCKHEED": "LOCKHEED MARTIN",
            "LMT": "LOCKHEED MARTIN",
            "LOCKHEED MARTIN": "LOCKHEED MARTIN",
            "RAYTHEON": "RTX",
            "RAYTHEON TECHNOLOGIES": "RTX",
            "RTX": "RTX",
            "NORTHROP": "NORTHROP GRUMMAN",
            "NGC": "NORTHROP GRUMMAN",
            "NORTHROP GRUMMAN": "NORTHROP GRUMMAN",
            "BOEING": "BOEING",
            "EXPORT CONTROL": "EXPORT_CONTROL",
            "CONTROLLED TECHNICAL INFORMATION": "CTI",
        }

        resolved = []

        for entity in entities:
            key = _safe_upper(entity)
            if not key:
                continue
            resolved.append(alias_map.get(key, key))

        return sorted(list(set(resolved)))

    # ------------------------------------------------------------------
    # Ledger Adapters
    # ------------------------------------------------------------------

    def _get_case(self, case_id: Any) -> Dict[str, Any]:
        for method_name in [
            "get_case",
            "get_case_by_id",
            "fetch_case",
            "read_case",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    result = method(case_id)
                    if result:
                        return result
                except Exception:
                    pass

        return {
            "case_id": case_id,
            "title": str(case_id),
            "status": "UNKNOWN",
        }

    def _get_case_evidence(
        self,
        case_id: Any,
    ) -> List[Dict[str, Any]]:
        for method_name in [
            "get_case_evidence",
            "list_case_evidence",
            "fetch_case_evidence",
        ]:
            method = getattr(self.ledger, method_name, None)

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
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    if tenant_id:
                        return method(tenant_id=tenant_id)
                    return method()
                except TypeError:
                    try:
                        return method(tenant_id)
                    except Exception:
                        pass
                except Exception:
                    pass

        return []

    # ------------------------------------------------------------------
    # Dedupe Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _dedupe_nodes(
        nodes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        seen: Set[str] = set()
        out = []

        for node in nodes:
            node_id = str(node.get("id"))

            if not node_id or node_id in seen:
                continue

            seen.add(node_id)
            out.append(node)

        return out

    @staticmethod
    def _dedupe_edges(
        edges: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        seen: Set[Tuple[str, str, str]] = set()
        out = []

        for edge in edges:
            key = (
                str(edge.get("source")),
                str(edge.get("target")),
                str(edge.get("type")),
            )

            if key in seen:
                continue

            seen.add(key)
            out.append(edge)

        return out

    @staticmethod
    def _relationship_type(
        *,
        shared_entities: List[str],
        shared_hashes: List[str],
        shared_filenames: List[str],
    ) -> str:
        if shared_hashes:
            return "SHARED_EVIDENCE_HASH"

        if shared_entities and shared_filenames:
            return "SHARED_ENTITY_AND_FILENAME"

        if shared_entities:
            return "SHARED_ENTITY"

        if shared_filenames:
            return "SHARED_FILENAME"

        return "RELATED_CASE"