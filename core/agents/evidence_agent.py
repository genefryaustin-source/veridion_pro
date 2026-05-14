"""
core/agents/evidence_agent.py

Evidence intelligence agent.

Capabilities:
- evidence enrichment
- chain-of-custody validation
- evidence graph linking
- entity extraction
- forensic scoring
- evidence prioritization
"""

from __future__ import annotations

import re
import time
import hashlib
from typing import Any, Dict, List, Optional

from core.agents.base_agent import BaseAgent, AgentExecutionResult


class EvidenceAgent(BaseAgent):
    AGENT_NAME = "evidence_agent"

    EXECUTION_SCOPE = [
        "enrich_evidence",
        "validate_chain_of_custody",
        "link_evidence_graph",
        "extract_entities",
        "score_forensics",
        "prioritize_evidence",
    ]

    REQUIRED_PERMISSIONS = [
        "evidence.read",
        "evidence.analyze",
        "evidence.link",
    ]

    DEFAULT_CONFIDENCE = 0.86

    def _execute(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:
        context = context or {}

        handlers = {
            "enrich_evidence": self.enrich_evidence,
            "validate_chain_of_custody": self.validate_chain_of_custody,
            "link_evidence_graph": self.link_evidence_graph,
            "extract_entities": self.extract_entities,
            "score_forensics": self.score_forensics,
            "prioritize_evidence": self.prioritize_evidence,
        }

        handler = handlers.get(action)

        if not handler:
            return AgentExecutionResult(
                success=False,
                action=action,
                agent_name=self.AGENT_NAME,
                error="unknown_action",
            )

        return handler(context)

    def enrich_evidence(self, context: Dict[str, Any]) -> AgentExecutionResult:
        text = str(context.get("text") or context.get("body") or "")
        evidence_id = context.get("evidence_id")

        enrichment = {
            "evidence_id": evidence_id,
            "length": len(text),
            "sha256_hint": hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest() if text else None,
            "contains_export_terms": self._contains_export_terms(text),
            "contains_cui_terms": self._contains_cui_terms(text),
            "created_at_ms": int(time.time() * 1000),
        }

        self.emit_event("EVIDENCE_ENRICHED", enrichment)

        return AgentExecutionResult(
            success=True,
            action="enrich_evidence",
            agent_name=self.AGENT_NAME,
            confidence=0.88,
            evidence_ids=[str(evidence_id)] if evidence_id else [],
            metadata=enrichment,
        )

    def validate_chain_of_custody(self, context: Dict[str, Any]) -> AgentExecutionResult:
        evidence_id = context.get("evidence_id")
        custody_events = context.get("custody_events") or []

        valid = bool(evidence_id) and len(custody_events) > 0

        payload = {
            "evidence_id": evidence_id,
            "custody_event_count": len(custody_events),
            "valid_chain": valid,
            "issues": [] if valid else ["missing_evidence_id_or_custody_events"],
        }

        self.emit_event(
            "CHAIN_OF_CUSTODY_VALIDATED" if valid else "CHAIN_OF_CUSTODY_VALIDATION_FAILED",
            payload,
        )

        return AgentExecutionResult(
            success=valid,
            action="validate_chain_of_custody",
            agent_name=self.AGENT_NAME,
            confidence=0.93 if valid else 0.35,
            evidence_ids=[str(evidence_id)] if evidence_id else [],
            metadata=payload,
            error=None if valid else "invalid_chain_of_custody",
        )

    def link_evidence_graph(self, context: Dict[str, Any]) -> AgentExecutionResult:
        evidence_id = context.get("evidence_id")
        case_id = context.get("case_id")
        entities = context.get("entities") or []

        links = []

        if evidence_id and case_id:
            links.append({"from": f"evidence:{evidence_id}", "to": f"case:{case_id}", "type": "belongs_to"})

        for entity in entities:
            links.append({"from": f"evidence:{evidence_id}", "to": f"entity:{entity}", "type": "mentions"})

        payload = {
            "evidence_id": evidence_id,
            "case_id": case_id,
            "links": links,
            "link_count": len(links),
        }

        self.emit_event("EVIDENCE_GRAPH_LINKED", payload)

        return AgentExecutionResult(
            success=True,
            action="link_evidence_graph",
            agent_name=self.AGENT_NAME,
            confidence=0.84,
            evidence_ids=[str(evidence_id)] if evidence_id else [],
            metadata=payload,
        )

    def extract_entities(self, context: Dict[str, Any]) -> AgentExecutionResult:
        text = str(context.get("text") or context.get("body") or "")

        emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))
        ips = sorted(set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)))
        possible_files = sorted(set(re.findall(r"\b[\w\-. ]+\.(?:pdf|docx|xlsx|csv|txt|zip|7z|pst|eml)\b", text, re.I)))

        entities = {
            "emails": emails,
            "ips": ips,
            "files": possible_files,
            "entity_count": len(emails) + len(ips) + len(possible_files),
        }

        self.emit_event("EVIDENCE_ENTITIES_EXTRACTED", entities)

        return AgentExecutionResult(
            success=True,
            action="extract_entities",
            agent_name=self.AGENT_NAME,
            confidence=0.82,
            metadata=entities,
        )

    def score_forensics(self, context: Dict[str, Any]) -> AgentExecutionResult:
        text = str(context.get("text") or context.get("body") or "")
        severity = str(context.get("severity", "")).upper()

        score = 10

        if self._contains_cui_terms(text):
            score += 25
        if self._contains_export_terms(text):
            score += 35
        if severity == "CRITICAL":
            score += 25
        elif severity == "HIGH":
            score += 15

        if context.get("has_attachment"):
            score += 10
        if context.get("external_sender"):
            score += 10

        score = min(score, 100)

        payload = {
            "forensic_score": score,
            "priority": self._priority_from_score(score),
            "severity": severity or "UNKNOWN",
        }

        self.emit_event("EVIDENCE_FORENSIC_SCORED", payload)

        return AgentExecutionResult(
            success=True,
            action="score_forensics",
            agent_name=self.AGENT_NAME,
            confidence=0.87,
            metadata=payload,
        )

    def prioritize_evidence(self, context: Dict[str, Any]) -> AgentExecutionResult:
        forensic_score = int(context.get("forensic_score", 0) or 0)
        hit_count = int(context.get("hit_count", 0) or 0)
        export_control = bool(context.get("export_control") or context.get("category") == "EXPORT_CONTROL")

        priority_score = forensic_score + min(hit_count * 3, 30)

        if export_control:
            priority_score += 35

        priority_score = min(priority_score, 100)

        payload = {
            "priority_score": priority_score,
            "priority": self._priority_from_score(priority_score),
            "export_control": export_control,
            "hit_count": hit_count,
        }

        self.emit_event("EVIDENCE_PRIORITIZED", payload)

        return AgentExecutionResult(
            success=True,
            action="prioritize_evidence",
            agent_name=self.AGENT_NAME,
            confidence=0.89,
            metadata=payload,
        )

    def _contains_export_terms(self, text: str) -> bool:
        terms = [
            "itar",
            "export controlled",
            "export-control",
            "defense article",
            "defense service",
            "usml",
            "ear99",
            "export administration regulations",
        ]
        lower = text.lower()
        return any(term in lower for term in terms)

    def _contains_cui_terms(self, text: str) -> bool:
        terms = [
            "controlled unclassified information",
            "cui",
            "controlled technical information",
            "cti",
            "covered defense information",
            "cdi",
        ]
        lower = text.lower()
        return any(term in lower for term in terms)

    def _priority_from_score(self, score: int) -> str:
        if score >= 85:
            return "CRITICAL"
        if score >= 65:
            return "HIGH"
        if score >= 35:
            return "MEDIUM"
        return "LOW"