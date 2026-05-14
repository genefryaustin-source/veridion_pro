import json
from collections import Counter, defaultdict


HIGH_RISK_ENTITY_TYPES = {
    "ITAR_REFERENCE",
    "EXPORT_CONTROL_TERM",
    "CUI_MARKING",
    "CREDENTIAL_TERM",
    "CREDENTIAL",
    "API_KEY",
    "SECRET",
}

CRITICAL_ALERT_SEVERITIES = {
    "CRITICAL",
}

HIGH_ALERT_SEVERITIES = {
    "HIGH",
    "CRITICAL",
}


class GraphRiskService:

    def __init__(self, ledger):
        self.ledger = ledger

    # =====================================================
    # PUBLIC ENTRYPOINT
    # =====================================================
    def analyze_case_graph(
        self,
        case_id,
        graph=None,
    ):
        alerts = self._load_case_alerts(case_id)
        entities = self._load_case_entities(case_id)
        relationships = self._load_case_relationships(case_id)

        entity_scores = self.score_entities(
            entities
        )

        relationship_scores = self.score_relationships(
            relationships
        )

        case_score = self.score_case(
            alerts=alerts,
            entities=entities,
            relationships=relationships,
            entity_scores=entity_scores,
            relationship_scores=relationship_scores,
        )

        clusters = self.detect_clusters(
            entities=entities,
            relationships=relationships,
        )

        cross_case = self.find_cross_case_pivots(
            entities=entities,
        )

        return {
            "case_id": case_id,
            "case_risk": case_score,
            "entity_risk": entity_scores,
            "relationship_risk": relationship_scores,
            "clusters": clusters,
            "cross_case_pivots": cross_case,
        }

    # =====================================================
    # CASE RISK
    # =====================================================
    def score_case(
        self,
        alerts,
        entities,
        relationships,
        entity_scores,
        relationship_scores,
    ):
        score = 0
        reasons = []

        critical_alerts = [
            a for a in alerts
            if str(a.get("severity", "")).upper()
            in CRITICAL_ALERT_SEVERITIES
        ]

        high_alerts = [
            a for a in alerts
            if str(a.get("severity", "")).upper()
            in HIGH_ALERT_SEVERITIES
        ]

        if critical_alerts:
            points = min(len(critical_alerts) * 25, 50)
            score += points
            reasons.append(
                f"{len(critical_alerts)} critical alert(s)"
            )

        elif high_alerts:
            points = min(len(high_alerts) * 15, 30)
            score += points
            reasons.append(
                f"{len(high_alerts)} high-risk alert(s)"
            )

        high_risk_entities = [
            e for e in entities
            if str(e.get("entity_type", "")).upper()
            in HIGH_RISK_ENTITY_TYPES
        ]

        if high_risk_entities:
            points = min(len(high_risk_entities) * 12, 35)
            score += points
            reasons.append(
                f"{len(high_risk_entities)} high-risk entity/entities"
            )

        relationship_count = len(relationships)

        if relationship_count:
            density_points = min(relationship_count * 3, 20)
            score += density_points
            reasons.append(
                f"{relationship_count} relationship edge(s)"
            )

        repeated_pivots = [
            e for e in entity_scores
            if e.get("case_count", 0) > 1
        ]

        if repeated_pivots:
            points = min(len(repeated_pivots) * 10, 30)
            score += points
            reasons.append(
                f"{len(repeated_pivots)} cross-case pivot(s)"
            )

        critical_relationships = [
            r for r in relationship_scores
            if r.get("severity") == "CRITICAL"
        ]

        if critical_relationships:
            points = min(len(critical_relationships) * 15, 30)
            score += points
            reasons.append(
                f"{len(critical_relationships)} critical relationship(s)"
            )

        score = min(score, 100)

        severity = self._severity_from_score(score)

        return {
            "score": score,
            "severity": severity,
            "reasons": reasons,
            "critical_alerts": len(critical_alerts),
            "high_alerts": len(high_alerts),
            "high_risk_entities": len(high_risk_entities),
            "relationship_count": relationship_count,
            "cross_case_pivots": len(repeated_pivots),
        }

    # =====================================================
    # ENTITY RISK
    # =====================================================
    def score_entities(
        self,
        entities,
    ):
        results = []

        for entity in entities:
            entity_type = str(
                entity.get("entity_type", "")
            ).upper()

            normalized_value = (
                entity.get("normalized_value")
                or entity.get("entity_value")
                or ""
            ).lower()

            case_refs = self._find_cases_for_entity(
                normalized_value
            )

            alert_refs = self._find_alerts_for_entity(
                normalized_value
            )

            score = 0
            reasons = []

            if entity_type in HIGH_RISK_ENTITY_TYPES:
                score += 45
                reasons.append(
                    f"High-risk entity type: {entity_type}"
                )

            case_count = len(case_refs)

            if case_count > 1:
                points = min(case_count * 10, 35)
                score += points
                reasons.append(
                    f"Appears in {case_count} case(s)"
                )

            critical_alerts = [
                a for a in alert_refs
                if str(a.get("severity", "")).upper() == "CRITICAL"
            ]

            if critical_alerts:
                score += 25
                reasons.append(
                    "Linked to critical alert(s)"
                )

            score = min(score, 100)

            results.append({
                "entity_id": entity.get("entity_id"),
                "entity_type": entity_type,
                "entity_value": entity.get("entity_value"),
                "normalized_value": normalized_value,
                "score": score,
                "severity": self._severity_from_score(score),
                "case_count": case_count,
                "alert_count": len(alert_refs),
                "critical_alert_count": len(critical_alerts),
                "reasons": reasons,
                "cases": case_refs,
            })

        return results

    # =====================================================
    # RELATIONSHIP RISK
    # =====================================================
    def score_relationships(
        self,
        relationships,
    ):
        results = []

        for rel in relationships:
            source_value = (
                rel.get("source_value")
                or rel.get("source")
                or ""
            )

            target_value = (
                rel.get("target_value")
                or rel.get("target")
                or ""
            )

            relationship_type = (
                rel.get("relationship_type")
                or rel.get("type")
                or "RELATED_TO"
            )

            score = 0
            reasons = []

            pair_count = self._count_relationship_pair(
                source_value,
                target_value,
            )

            if pair_count > 1:
                points = min(pair_count * 15, 40)
                score += points
                reasons.append(
                    f"Relationship appears {pair_count} time(s)"
                )

            high_risk_terms = [
                "itar",
                "export",
                "credential",
                "password",
                "secret",
                "cui",
            ]

            joined = f"{source_value} {target_value}".lower()

            if any(term in joined for term in high_risk_terms):
                score += 45
                reasons.append(
                    "High-risk relationship co-occurrence"
                )

            if str(relationship_type).upper() == "CO_OCCURRENCE":
                score += 10
                reasons.append(
                    "Co-occurrence edge"
                )

            score = min(score, 100)

            results.append({
                "source": source_value,
                "target": target_value,
                "relationship_type": relationship_type,
                "score": score,
                "severity": self._severity_from_score(score),
                "pair_count": pair_count,
                "reasons": reasons,
            })

        return results

    # =====================================================
    # CLUSTER DETECTION
    # =====================================================
    def detect_clusters(
        self,
        entities,
        relationships,
    ):
        clusters = []

        entity_values = [
            str(e.get("entity_value", "")).lower()
            for e in entities
        ]

        entity_types = Counter(
            str(e.get("entity_type", "")).upper()
            for e in entities
        )

        text_blob = " ".join(entity_values)

        if any(
            term in text_blob
            for term in ["itar", "ear", "usml", "export"]
        ):
            clusters.append({
                "cluster_type": "EXPORT_CONTROL_CLUSTER",
                "severity": "CRITICAL",
                "summary": "Export-control indicators are present in the entity graph.",
            })

        if any(
            term in text_blob
            for term in ["password", "token", "secret", "api key"]
        ):
            clusters.append({
                "cluster_type": "CREDENTIAL_EXPOSURE_CLUSTER",
                "severity": "CRITICAL",
                "summary": "Credential-related indicators are present in the entity graph.",
            })

        if entity_types.get("EMAIL", 0) >= 3:
            clusters.append({
                "cluster_type": "COMMUNICATION_CLUSTER",
                "severity": "MEDIUM",
                "summary": "Multiple email entities appear in this investigation.",
            })

        if len(relationships) >= 5:
            clusters.append({
                "cluster_type": "DENSE_RELATIONSHIP_CLUSTER",
                "severity": "HIGH",
                "summary": "Relationship density suggests a connected investigation cluster.",
            })

        return clusters

    # =====================================================
    # CROSS-CASE PIVOTS
    # =====================================================
    def find_cross_case_pivots(
        self,
        entities,
    ):
        pivots = []

        seen = set()

        for entity in entities:
            normalized = (
                entity.get("normalized_value")
                or entity.get("entity_value")
                or ""
            ).lower()

            if not normalized or normalized in seen:
                continue

            seen.add(normalized)

            cases = self._find_cases_for_entity(
                normalized
            )

            if len(cases) > 1:
                pivots.append({
                    "entity_value": entity.get("entity_value"),
                    "normalized_value": normalized,
                    "entity_type": entity.get("entity_type"),
                    "case_count": len(cases),
                    "cases": cases,
                })

        return pivots

    # =====================================================
    # DATA LOADERS
    # =====================================================
    def _load_case_alerts(
        self,
        case_id,
    ):
        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT *
                FROM alerts
                WHERE case_id = ?
                ORDER BY created_at_ms DESC
                """,
                (case_id,),
            ).fetchall()

            return [dict(r) for r in rows]

    def _load_case_entities(
        self,
        case_id,
    ):
        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT
                    ce.case_id,
                    ce.evidence_id,
                    e.*
                FROM case_entities ce
                JOIN entities e
                    ON ce.entity_id = e.entity_id
                WHERE ce.case_id = ?
                """,
                (case_id,),
            ).fetchall()

            return [dict(r) for r in rows]

    def _load_case_relationships(
        self,
        case_id,
    ):
        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT
                    re.*,
                    s.entity_value AS source_value,
                    s.entity_type AS source_type,
                    t.entity_value AS target_value,
                    t.entity_type AS target_type
                FROM relationship_edges re
                JOIN entities s
                    ON re.source_entity_id = s.entity_id
                JOIN entities t
                    ON re.target_entity_id = t.entity_id
                JOIN case_entities ce
                    ON ce.entity_id = s.entity_id
                WHERE ce.case_id = ?
                """,
                (case_id,),
            ).fetchall()

            return [dict(r) for r in rows]

    def _find_cases_for_entity(
        self,
        normalized_value,
    ):
        if not normalized_value:
            return []

        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT DISTINCT
                    ce.case_id,
                    c.title,
                    c.status,
                    c.created_at_ms
                FROM case_entities ce
                JOIN entities e
                    ON ce.entity_id = e.entity_id
                LEFT JOIN cases c
                    ON c.case_id = ce.case_id
                WHERE e.normalized_value = ?
                ORDER BY c.created_at_ms DESC
                """,
                (normalized_value,),
            ).fetchall()

            return [dict(r) for r in rows]

    def _find_alerts_for_entity(
        self,
        normalized_value,
    ):
        if not normalized_value:
            return []

        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT DISTINCT
                    a.*
                FROM alerts a
                JOIN case_entities ce
                    ON ce.case_id = a.case_id
                JOIN entities e
                    ON e.entity_id = ce.entity_id
                WHERE e.normalized_value = ?
                """,
                (normalized_value,),
            ).fetchall()

            return [dict(r) for r in rows]

    def _count_relationship_pair(
        self,
        source_value,
        target_value,
    ):
        if not source_value or not target_value:
            return 0

        with self.ledger._connect() as con:
            row = con.execute(
                """
                SELECT COUNT(*) AS total
                FROM relationship_edges re
                JOIN entities s
                    ON re.source_entity_id = s.entity_id
                JOIN entities t
                    ON re.target_entity_id = t.entity_id
                WHERE LOWER(s.entity_value) = ?
                  AND LOWER(t.entity_value) = ?
                """,
                (
                    source_value.lower(),
                    target_value.lower(),
                ),
            ).fetchone()

            return int(row["total"] or 0)

    # =====================================================
    # HELPERS
    # =====================================================
    def _severity_from_score(
        self,
        score,
    ):
        if score >= 85:
            return "CRITICAL"

        if score >= 60:
            return "HIGH"

        if score >= 30:
            return "MEDIUM"

        return "LOW"