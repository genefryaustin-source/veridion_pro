from __future__ import annotations

import hashlib
import re
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set


def _now_ms() -> int:
    return int(time.time() * 1000)


class EntityResolutionService:
    """
    Intelligence-grade entity resolution engine.

    Handles:
    - normalization
    - alias resolution
    - deduplication
    - canonical identity generation
    - enrichment
    - relationship mapping

    This becomes the backbone for:
    - graph intelligence
    - campaign detection
    - relationship scoring
    - analyst pivots
    - export-control tracing
    - insider-threat investigations
    """

    # ------------------------------------------------------------------
    # Canonical Alias Registry
    # ------------------------------------------------------------------

    DEFAULT_ALIAS_MAP = {

        # --------------------------------------------------------------
        # Lockheed
        # --------------------------------------------------------------

        "LOCKHEED": "LOCKHEED MARTIN",
        "LMT": "LOCKHEED MARTIN",
        "LOCKHEED MARTIN": "LOCKHEED MARTIN",
        "LOCKHEED MARTIN CORP": "LOCKHEED MARTIN",
        "LOCKHEED MARTIN CORPORATION": "LOCKHEED MARTIN",

        # --------------------------------------------------------------
        # RTX / Raytheon
        # --------------------------------------------------------------

        "RAYTHEON": "RAYTHEON TECHNOLOGIES",
        "RTX": "RAYTHEON TECHNOLOGIES",
        "RAYTHEON TECHNOLOGIES": "RAYTHEON TECHNOLOGIES",

        # --------------------------------------------------------------
        # Northrop
        # --------------------------------------------------------------

        "NORTHROP": "NORTHROP GRUMMAN",
        "NGC": "NORTHROP GRUMMAN",
        "NORTHROP GRUMMAN": "NORTHROP GRUMMAN",
        "NORTHROP GRUMMAN CORP": "NORTHROP GRUMMAN",

        # --------------------------------------------------------------
        # Boeing
        # --------------------------------------------------------------

        "BOEING": "BOEING",
        "THE BOEING COMPANY": "BOEING",

        # --------------------------------------------------------------
        # Export Control
        # --------------------------------------------------------------

        "EXPORT CONTROL": "EXPORT_CONTROL",
        "EXPORT-CONTROL": "EXPORT_CONTROL",
        "EXPORT_CONTROL": "EXPORT_CONTROL",

        "CONTROLLED TECHNICAL INFORMATION": "CTI",
        "CONTROLLED-TECHNICAL-INFORMATION": "CTI",
        "CTI": "CTI",

        # --------------------------------------------------------------
        # ITAR
        # --------------------------------------------------------------

        "INTERNATIONAL TRAFFIC IN ARMS REGULATIONS": "ITAR",
        "ITAR": "ITAR",

        # --------------------------------------------------------------
        # EAR
        # --------------------------------------------------------------

        "EXPORT ADMINISTRATION REGULATIONS": "EAR",
        "EAR": "EAR",
        "EAR99": "EAR99",
    }

    # ------------------------------------------------------------------
    # Entity Enrichment Registry
    # ------------------------------------------------------------------

    DEFAULT_ENTITY_METADATA = {

        "LOCKHEED MARTIN": {
            "entity_type": "DEFENSE_CONTRACTOR",
            "country": "US",
            "risk_level": "HIGH",
            "sector": "AEROSPACE_DEFENSE",
        },

        "RAYTHEON TECHNOLOGIES": {
            "entity_type": "DEFENSE_CONTRACTOR",
            "country": "US",
            "risk_level": "HIGH",
            "sector": "AEROSPACE_DEFENSE",
        },

        "NORTHROP GRUMMAN": {
            "entity_type": "DEFENSE_CONTRACTOR",
            "country": "US",
            "risk_level": "HIGH",
            "sector": "AEROSPACE_DEFENSE",
        },

        "BOEING": {
            "entity_type": "DEFENSE_CONTRACTOR",
            "country": "US",
            "risk_level": "HIGH",
            "sector": "AEROSPACE_DEFENSE",
        },

        "ITAR": {
            "entity_type": "EXPORT_CONTROL",
            "country": "US",
            "risk_level": "CRITICAL",
            "sector": "REGULATORY",
        },

        "EAR": {
            "entity_type": "EXPORT_CONTROL",
            "country": "US",
            "risk_level": "HIGH",
            "sector": "REGULATORY",
        },

        "EAR99": {
            "entity_type": "EXPORT_CONTROL",
            "country": "US",
            "risk_level": "HIGH",
            "sector": "REGULATORY",
        },

        "EXPORT_CONTROL": {
            "entity_type": "EXPORT_CONTROL",
            "country": "US",
            "risk_level": "CRITICAL",
            "sector": "REGULATORY",
        },

        "CTI": {
            "entity_type": "CONTROLLED_DATA",
            "country": "US",
            "risk_level": "CRITICAL",
            "sector": "REGULATORY",
        },
    }

    # ------------------------------------------------------------------
    # Relationship Registry
    # ------------------------------------------------------------------

    DEFAULT_RELATIONSHIPS = {

        "LOCKHEED MARTIN": [
            {
                "target": "F-35",
                "relationship": "PROGRAM",
            },
            {
                "target": "ITAR",
                "relationship": "EXPORT_CONTROL",
            },
        ],

        "RAYTHEON TECHNOLOGIES": [
            {
                "target": "PATRIOT",
                "relationship": "PROGRAM",
            },
            {
                "target": "ITAR",
                "relationship": "EXPORT_CONTROL",
            },
        ],

        "NORTHROP GRUMMAN": [
            {
                "target": "B-21",
                "relationship": "PROGRAM",
            },
        ],
    }

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        ledger: Any = None,
        custom_aliases: Optional[Dict[str, str]] = None,
    ):
        self.ledger = ledger

        self.alias_map = dict(self.DEFAULT_ALIAS_MAP)

        if custom_aliases:
            self.alias_map.update(custom_aliases)

    # ------------------------------------------------------------------
    # Public APIs
    # ------------------------------------------------------------------

    def resolve_entities(
        self,
        entities: List[Any],
    ) -> List[str]:
        """
        Normalize + alias-resolve + dedupe.
        """

        resolved = []

        for entity in entities:

            normalized = self.normalize_entity(entity)

            if not normalized:
                continue

            canonical = self.resolve_alias(normalized)

            resolved.append(canonical)

        return sorted(list(set(resolved)))

    def normalize_entities(
        self,
        entities: List[Any],
    ) -> List[str]:
        return self.resolve_entities(entities)

    def dedupe_entities(
        self,
        entities: List[Any],
    ) -> List[str]:
        return self.resolve_entities(entities)

    # ------------------------------------------------------------------
    # Core Resolution
    # ------------------------------------------------------------------

    def normalize_entity(
        self,
        entity: Any,
    ) -> str:

        if entity is None:
            return ""

        if isinstance(entity, dict):

            entity = (
                entity.get("name")
                or entity.get("value")
                or entity.get("label")
                or entity.get("entity")
                or ""
            )

        value = str(entity)

        value = value.upper()

        value = value.strip()

        # --------------------------------------------------------------
        # Remove punctuation
        # --------------------------------------------------------------

        value = re.sub(
            r"[^A-Z0-9\s\-_]",
            "",
            value,
        )

        # --------------------------------------------------------------
        # Collapse whitespace
        # --------------------------------------------------------------

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = value.strip()

        return value

    def resolve_alias(
        self,
        entity: str,
    ) -> str:

        entity = self.normalize_entity(entity)

        return self.alias_map.get(
            entity,
            entity,
        )

    # ------------------------------------------------------------------
    # Canonical IDs
    # ------------------------------------------------------------------

    def generate_entity_id(
        self,
        canonical_name: str,
    ) -> str:

        canonical_name = self.resolve_alias(canonical_name)

        digest = hashlib.sha256(
            canonical_name.encode()
        ).hexdigest()[:12]

        return f"ENT-{digest.upper()}"

    # ------------------------------------------------------------------
    # Enrichment
    # ------------------------------------------------------------------

    def enrich_entity(
        self,
        entity: str,
    ) -> Dict[str, Any]:

        canonical = self.resolve_alias(entity)

        entity_id = self.generate_entity_id(canonical)

        metadata = dict(
            self.DEFAULT_ENTITY_METADATA.get(
                canonical,
                {}
            )
        )

        aliases = self.get_aliases(canonical)

        relationships = self.get_relationships(canonical)

        return {
            "entity_id": entity_id,
            "canonical_name": canonical,
            "aliases": aliases,
            "relationships": relationships,
            "metadata": metadata,
            "generated_at_ms": _now_ms(),
        }

    def enrich_entities(
        self,
        entities: List[Any],
    ) -> List[Dict[str, Any]]:

        resolved = self.resolve_entities(entities)

        return [
            self.enrich_entity(entity)
            for entity in resolved
        ]

    # ------------------------------------------------------------------
    # Aliases
    # ------------------------------------------------------------------

    def get_aliases(
        self,
        canonical_name: str,
    ) -> List[str]:

        canonical_name = self.resolve_alias(canonical_name)

        aliases = []

        for alias, target in self.alias_map.items():

            if target == canonical_name:
                aliases.append(alias)

        aliases.append(canonical_name)

        return sorted(list(set(aliases)))

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    def get_relationships(
        self,
        canonical_name: str,
    ) -> List[Dict[str, Any]]:

        canonical_name = self.resolve_alias(canonical_name)

        return list(
            self.DEFAULT_RELATIONSHIPS.get(
                canonical_name,
                []
            )
        )

    def add_relationship(
        self,
        *,
        source: str,
        target: str,
        relationship: str,
    ) -> Dict[str, Any]:

        source = self.resolve_alias(source)
        target = self.resolve_alias(target)

        existing = self.DEFAULT_RELATIONSHIPS.get(
            source,
            []
        )

        existing.append({
            "target": target,
            "relationship": relationship,
        })

        self.DEFAULT_RELATIONSHIPS[source] = existing

        return {
            "source": source,
            "target": target,
            "relationship": relationship,
            "status": "added",
        }

    # ------------------------------------------------------------------
    # Entity Clustering
    # ------------------------------------------------------------------

    def cluster_entities(
        self,
        entities: List[Any],
    ) -> Dict[str, List[str]]:
        """
        Groups aliases into canonical buckets.
        """

        clusters = defaultdict(list)

        for entity in entities:

            normalized = self.normalize_entity(entity)

            if not normalized:
                continue

            canonical = self.resolve_alias(normalized)

            clusters[canonical].append(normalized)

        output = {}

        for canonical, aliases in clusters.items():
            output[canonical] = sorted(
                list(set(aliases))
            )

        return output

    # ------------------------------------------------------------------
    # Search / Pivot
    # ------------------------------------------------------------------

    def search_entity(
        self,
        query: str,
    ) -> Dict[str, Any]:

        normalized = self.normalize_entity(query)

        canonical = self.resolve_alias(normalized)

        enrichment = self.enrich_entity(canonical)

        return {
            "query": query,
            "normalized": normalized,
            "canonical": canonical,
            "entity": enrichment,
        }

    # ------------------------------------------------------------------
    # Case Correlation
    # ------------------------------------------------------------------

    def correlate_case_entities(
        self,
        *,
        case_entities: List[Any],
        other_case_entities: List[Any],
    ) -> Dict[str, Any]:

        left = set(
            self.resolve_entities(case_entities)
        )

        right = set(
            self.resolve_entities(other_case_entities)
        )

        overlap = sorted(list(left & right))

        score = min(
            100,
            len(overlap) * 25,
        )

        return {
            "shared_entities": overlap,
            "correlation_score": score,
            "is_correlated": bool(overlap),
        }

    # ------------------------------------------------------------------
    # Registry Management
    # ------------------------------------------------------------------

    def add_alias(
        self,
        *,
        alias: str,
        canonical_name: str,
    ) -> Dict[str, Any]:

        alias = self.normalize_entity(alias)

        canonical_name = self.normalize_entity(
            canonical_name
        )

        self.alias_map[alias] = canonical_name

        return {
            "alias": alias,
            "canonical_name": canonical_name,
            "status": "added",
        }

    def get_alias_registry(
        self,
    ) -> Dict[str, str]:

        return dict(self.alias_map)

    def get_entity_metadata_registry(
        self,
    ) -> Dict[str, Dict[str, Any]]:

        return dict(self.DEFAULT_ENTITY_METADATA)

    # ------------------------------------------------------------------
    # Export Control Detection
    # ------------------------------------------------------------------

    def detect_export_control_entities(
        self,
        entities: List[Any],
    ) -> List[str]:

        resolved = self.resolve_entities(
            entities
        )

        export_entities = []

        export_markers = {
            "ITAR",
            "EAR",
            "EAR99",
            "EXPORT_CONTROL",
            "CTI",
        }

        for entity in resolved:

            if entity in export_markers:
                export_entities.append(entity)

        return sorted(list(set(export_entities)))

    # ------------------------------------------------------------------
    # Intelligence Summary
    # ------------------------------------------------------------------

    def summarize_entities(
        self,
        entities: List[Any],
    ) -> Dict[str, Any]:

        resolved = self.resolve_entities(
            entities
        )

        enriched = self.enrich_entities(
            resolved
        )

        entity_types = defaultdict(int)

        risk_levels = defaultdict(int)

        for entity in enriched:

            metadata = entity.get(
                "metadata",
                {}
            )

            entity_type = metadata.get(
                "entity_type",
                "UNKNOWN",
            )

            risk = metadata.get(
                "risk_level",
                "UNKNOWN",
            )

            entity_types[entity_type] += 1
            risk_levels[risk] += 1

        return {
            "total_entities": len(resolved),
            "entity_types": dict(entity_types),
            "risk_levels": dict(risk_levels),
            "entities": enriched,
            "generated_at_ms": _now_ms(),
        }