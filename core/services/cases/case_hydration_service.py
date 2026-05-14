from core.services.cases.case_link_service import (
    CaseLinkService
)

from core.services.graph.graph_risk_service import GraphRiskService

class CaseHydrationService:

    def __init__(
        self,
        ledger,
    ):

        self.ledger = ledger

        self.case_link_service = (
            CaseLinkService(
                ledger
            )
        )

        self.graph_risk_service = GraphRiskService(
            ledger
        )
    # =====================================================
    # MAIN HYDRATION
    # =====================================================

    def hydrate_case(
        self,
        case_id,
    ):

        bundle = {
            "case_id": case_id,
            "case": self._load_case(
                case_id
            ),
            "alerts": self.case_link_service.get_case_alerts(
                case_id
            ),
            "evidence": self._load_evidence(
                case_id
            ),
            "entities": self.case_link_service.get_case_entities(
                case_id
            ),
            "relationships": self._load_relationships(
                case_id
            ),
            "timeline": self._load_timeline(
                case_id
            ),
            "metrics": self._calculate_metrics(
                case_id
            ),
            "graph": self._build_graph(
                case_id
            ),
            "graph_risk": self.graph_risk_service.analyze_case_graph(
                case_id,
            ),
        }

        return bundle

    # =====================================================
    # CASE
    # =====================================================

    def _load_case(
        self,
        case_id,
    ):

        with self.ledger._connect() as con:

            row = con.execute(
                """
                SELECT *
                FROM cases
                WHERE case_id = ?
                   OR id = ?
                LIMIT 1
                """,
                (
                    case_id,
                    case_id,
                ),
            ).fetchone()

            return (
                dict(row)
                if row else {}
            )

    # =====================================================
    # EVIDENCE
    # =====================================================

    def _load_evidence(
        self,
        case_id,
    ):

        evidence_ids = (
            self.case_link_service.get_case_evidence_ids(
                case_id
            )
        )

        if not evidence_ids:
            return []

        placeholders = ",".join(
            "?"
            for _ in evidence_ids
        )

        with self.ledger._connect() as con:

            rows = con.execute(
                f"""
                SELECT *
                FROM evidence_records
                WHERE evidence_id IN ({placeholders})
                """,
                tuple(evidence_ids),
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    def _load_relationships(
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

            return [
                dict(r)
                for r in rows
            ]

    # =====================================================
    # TIMELINE
    # =====================================================

    def _load_timeline(
        self,
        case_id,
    ):

        events = []

        with self.ledger._connect() as con:

            # ---------------------------------------------
            # CASE EVENTS
            # ---------------------------------------------
            try:

                rows = con.execute(
                    """
                    SELECT *
                    FROM case_events
                    WHERE case_id = ?
                    ORDER BY created_at_ms DESC
                    """,
                    (case_id,),
                ).fetchall()

                for r in rows:

                    row = dict(r)

                    events.append({
                        "timestamp":
                            row.get(
                                "created_at_ms"
                            ),

                        "event_type":
                            row.get(
                                "event_type"
                            ),

                        "summary":
                            row.get(
                                "message"
                            ),

                        "source":
                            "case_events",
                    })

            except Exception:
                pass

            # ---------------------------------------------
            # ALERT EVENTS
            # ---------------------------------------------
            try:

                rows = con.execute(
                    """
                    SELECT *
                    FROM alerts
                    WHERE case_id = ?
                    ORDER BY created_at_ms DESC
                    """,
                    (case_id,),
                ).fetchall()

                for r in rows:

                    row = dict(r)

                    events.append({
                        "timestamp":
                            row.get(
                                "created_at_ms"
                            ),

                        "event_type":
                            "ALERT",

                        "summary":
                            row.get(
                                "message"
                            ),

                        "source":
                            "alerts",
                    })

            except Exception:
                pass

        events = sorted(
            events,
            key=lambda x:
                x.get(
                    "timestamp",
                    0
                ),
            reverse=True,
        )

        return events

    # =====================================================
    # GRAPH METRICS
    # =====================================================

    def _calculate_metrics(
        self,
        case_id,
    ):

        alerts = (
            self.case_link_service.get_case_alerts(
                case_id
            )
        )

        entities = (
            self.case_link_service.get_case_entities(
                case_id
            )
        )

        critical_alerts = len([
            a for a in alerts
            if (
                a.get(
                    "severity",
                    ""
                ).upper()
                == "CRITICAL"
            )
        ])

        export_hits = len([
            e for e in entities
            if (
                e.get(
                    "entity_type",
                    ""
                ).upper()
                in [
                    "ITAR_REFERENCE",
                    "EXPORT_CONTROL_TERM",
                    "CUI_MARKING",
                ]
            )
        ])

        relationship_density = max(
            1,
            len(entities) // 2
        )

        repeated_entities = len(set([
            e.get(
                "normalized_value"
            )
            for e in entities
        ]))

        risk_score = (
            critical_alerts * 30
            + export_hits * 15
            + relationship_density * 5
            + repeated_entities * 2
        )

        risk_score = min(
            risk_score,
            100
        )

        severity = "LOW"

        if risk_score >= 75:
            severity = "CRITICAL"

        elif risk_score >= 50:
            severity = "HIGH"

        elif risk_score >= 25:
            severity = "MEDIUM"

        return {
            "risk_score":
                risk_score,

            "severity":
                severity,

            "critical_alerts":
                critical_alerts,

            "export_hits":
                export_hits,

            "relationship_density":
                relationship_density,

            "repeated_entities":
                repeated_entities,
        }

    def _build_graph(
            self,
            case_id,
    ):

        nodes = []
        edges = []

        seen_nodes = set()
        seen_edges = set()

        with self.ledger._connect() as con:

            # =====================================================
            # CASE NODE
            # =====================================================
            case_row = con.execute(
                """
                SELECT *
                FROM cases
                WHERE case_id = ?
                   OR id = ?
                LIMIT 1
                """,
                (
                    case_id,
                    case_id,
                ),
            ).fetchone()

            case_data = (
                dict(case_row)
                if case_row else {}
            )

            case_node_id = f"CASE:{case_id}"

            nodes.append({
                "id": case_node_id,
                "label": (
                        case_data.get("title")
                        or f"Case {case_id}"
                ),
                "type": "CASE",
                "severity": (
                        case_data.get("severity")
                        or case_data.get("status")
                        or "INFO"
                ),
            })

            seen_nodes.add(case_node_id)

            # =====================================================
            # EVIDENCE
            # =====================================================
            evidence_ids = (
                self.case_link_service.get_case_evidence_ids(
                    case_id
                )
            )

            if evidence_ids:

                placeholders = ",".join(
                    "?"
                    for _ in evidence_ids
                )

                evidence_rows = con.execute(
                    f"""
                    SELECT *
                    FROM evidence_records
                    WHERE evidence_id IN ({placeholders})
                    """,
                    tuple(evidence_ids),
                ).fetchall()

                for r in evidence_rows:

                    row = dict(r)

                    evidence_id = row.get(
                        "evidence_id"
                    )

                    evidence_node_id = (
                        f"EVIDENCE:{evidence_id}"
                    )

                    if evidence_node_id not in seen_nodes:
                        nodes.append({
                            "id": evidence_node_id,
                            "label": (
                                    row.get("source_name")
                                    or evidence_id
                            ),
                            "type": "EVIDENCE",
                            "content_type": row.get(
                                "content_type"
                            ),
                        })

                        seen_nodes.add(
                            evidence_node_id
                        )

                    edge_key = (
                        case_node_id,
                        evidence_node_id,
                        "HAS_EVIDENCE",
                    )

                    if edge_key not in seen_edges:
                        edges.append({
                            "source":
                                case_node_id,

                            "target":
                                evidence_node_id,

                            "type":
                                "HAS_EVIDENCE",
                        })

                        seen_edges.add(
                            edge_key
                        )

            # =====================================================
            # ALERTS
            # =====================================================
            alerts = (
                self.case_link_service.get_case_alerts(
                    case_id
                )
            )

            for alert in alerts:

                alert_id = alert.get("id")

                alert_node_id = (
                    f"ALERT:{alert_id}"
                )

                if alert_node_id not in seen_nodes:
                    nodes.append({
                        "id": alert_node_id,
                        "label": (
                                alert.get("message")
                                or f"Alert {alert_id}"
                        ),
                        "type": "ALERT",
                        "severity": alert.get(
                            "severity",
                            "INFO"
                        ),
                    })

                    seen_nodes.add(
                        alert_node_id
                    )

                edge_key = (
                    case_node_id,
                    alert_node_id,
                    "HAS_ALERT",
                )

                if edge_key not in seen_edges:
                    edges.append({
                        "source":
                            case_node_id,

                        "target":
                            alert_node_id,

                        "type":
                            "HAS_ALERT",
                    })

                    seen_edges.add(
                        edge_key
                    )

                evidence_id = alert.get(
                    "evidence_id"
                )

                if evidence_id:

                    evidence_node_id = (
                        f"EVIDENCE:{evidence_id}"
                    )

                    edge_key = (
                        evidence_node_id,
                        alert_node_id,
                        "TRIGGERED_ALERT",
                    )

                    if edge_key not in seen_edges:
                        edges.append({
                            "source":
                                evidence_node_id,

                            "target":
                                alert_node_id,

                            "type":
                                "TRIGGERED_ALERT",
                        })

                        seen_edges.add(
                            edge_key
                        )

            # =====================================================
            # ENTITIES
            # =====================================================
            entity_rows = con.execute(
                """
                SELECT
                    ce.case_id,
                    ce.evidence_id,

                    e.entity_id,
                    e.entity_type,
                    e.entity_value,
                    e.normalized_value,
                    e.confidence

                FROM case_entities ce

                JOIN entities e
                    ON ce.entity_id = e.entity_id

                WHERE ce.case_id = ?
                """,
                (case_id,),
            ).fetchall()

            for r in entity_rows:

                row = dict(r)

                entity_id = row.get(
                    "entity_id"
                )

                evidence_id = row.get(
                    "evidence_id"
                )

                entity_node_id = (
                    f"ENTITY:{entity_id}"
                )

                if entity_node_id not in seen_nodes:
                    nodes.append({
                        "id": entity_node_id,
                        "label": (
                                row.get("entity_value")
                                or entity_id
                        ),
                        "type": "ENTITY",
                        "entity_type": row.get(
                            "entity_type"
                        ),
                        "confidence": row.get(
                            "confidence"
                        ),
                    })

                    seen_nodes.add(
                        entity_node_id
                    )

                if evidence_id:

                    evidence_node_id = (
                        f"EVIDENCE:{evidence_id}"
                    )

                    edge_key = (
                        evidence_node_id,
                        entity_node_id,
                        "HAS_ENTITY",
                    )

                    if edge_key not in seen_edges:
                        edges.append({
                            "source":
                                evidence_node_id,

                            "target":
                                entity_node_id,

                            "type":
                                "HAS_ENTITY",
                        })

                        seen_edges.add(
                            edge_key
                        )

            # =====================================================
            # RELATIONSHIP EDGES
            # =====================================================
            relationship_rows = con.execute(
                """
                SELECT
                    re.relationship_type,

                    s.entity_id AS source_entity_id,
                    s.entity_value AS source_value,

                    t.entity_id AS target_entity_id,
                    t.entity_value AS target_value

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

            for r in relationship_rows:

                row = dict(r)

                source_node = (
                    f"ENTITY:{row['source_entity_id']}"
                )

                target_node = (
                    f"ENTITY:{row['target_entity_id']}"
                )

                relationship_type = (
                        row.get(
                            "relationship_type"
                        )
                        or "RELATED_TO"
                )

                edge_key = (
                    source_node,
                    target_node,
                    relationship_type,
                )

                if edge_key not in seen_edges:
                    edges.append({
                        "source":
                            source_node,

                        "target":
                            target_node,

                        "type":
                            relationship_type,
                    })

                    seen_edges.add(
                        edge_key
                    )

        return {
            "nodes": nodes,
            "edges": edges,
        }