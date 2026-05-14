from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from core.ai.copilot.operational_context_builder import (
    OperationalContextBuilder,
)

from core.ai.copilot.investigation_reasoner import (
    InvestigationReasoner,
)

from core.ai.copilot.next_action_engine import (
    NextActionEngine,
)

from core.ai.copilot.case_summary_engine import (
    CaseSummaryEngine,
)

from core.ai.orchestration.playbook_orchestrator import (
    PlaybookOrchestrator,
)

from core.ai.orchestration.approval_aware_executor import (
    ApprovalAwareExecutor,
)

from core.ai.orchestration.risk_decision_engine import (
    RiskDecisionEngine,
)

from core.ai.orchestration.autonomous_response_engine import (
    AutonomousResponseEngine,
)

from core.ai.orchestration.containment_engine import (
    ContainmentEngine,
)
def _now_ms() -> int:
    return int(time.time() * 1000)


class CopilotService:
    """
    Master AI operational orchestration facade.

    Aggregates:
    - operational context
    - reasoning
    - next actions
    - summaries
    - operational priority
    - graph intelligence
    - campaign intelligence
    - playbook orchestration

    This becomes the unified AI entrypoint for:
    - SOC command center
    - analyst copilot
    - APIs
    - MSSP operations
    - GovCloud workflows
    """

    def __init__(
        self,
        ledger: Any,

        # Core Services
        sla_service: Any = None,
        graph_service: Any = None,
        graph_risk_service: Any = None,
        case_intelligence_service: Any = None,
        campaign_service: Any = None,
        entity_resolution_service: Any = None,
        recommendation_engine: Any = None,
        playbook_service: Any = None,
        approval_service: Any = None,
        assignment_service: Any = None,
        escalation_service: Any = None,
        event_broadcaster: Any = None,
        playbook_orchestrator: Any = None,
        approval_executor: Any = None,
        risk_decision_engine: Any = None,
        autonomous_response_engine: Any = None,
        containment_engine: Any = None,

        # Optional AI/LLM
        llm_service: Any = None,
    ):

        # --------------------------------------------------------------
        # Operational Context
        # --------------------------------------------------------------

        self.context_builder = OperationalContextBuilder(
            ledger=ledger,
            sla_service=sla_service,
            graph_service=graph_service,
            graph_risk_service=graph_risk_service,
            case_intelligence_service=case_intelligence_service,
            campaign_service=campaign_service,
            entity_resolution_service=entity_resolution_service,
            recommendation_engine=recommendation_engine,
            playbook_service=playbook_service,
            approval_service=approval_service,
            assignment_service=assignment_service,
            escalation_service=escalation_service,
            event_broadcaster=event_broadcaster,

        )

        # --------------------------------------------------------------
        # AI Reasoning
        # --------------------------------------------------------------

        self.reasoner = InvestigationReasoner(
            operational_context_builder=self.context_builder,
        )

        # --------------------------------------------------------------
        # Next Actions
        # --------------------------------------------------------------

        self.next_action_engine = NextActionEngine(
            playbook_service=playbook_service,
            recommendation_engine=recommendation_engine,
        )

        # --------------------------------------------------------------
        # Narrative Summaries
        # --------------------------------------------------------------

        self.summary_engine = CaseSummaryEngine(
            llm_service=llm_service,
        )

        self.ledger = ledger
        self.playbook_orchestrator = (
            playbook_orchestrator
        )

        self.approval_executor = (
            approval_executor
        )

        self.risk_decision_engine = (
            risk_decision_engine
        )

        self.autonomous_response_engine = (
            autonomous_response_engine
        )

        self.containment_engine = (
            containment_engine
        )
    # ------------------------------------------------------------------
    # Main AI Orchestration API
    # ------------------------------------------------------------------

    def analyze_case(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full operational AI analysis pipeline.
        """

        # --------------------------------------------------------------
        # Build Operational Context
        # --------------------------------------------------------------

        context = self.context_builder.build_case_context(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        # --------------------------------------------------------------
        # Investigation Reasoning
        # --------------------------------------------------------------

        reasoning = self.reasoner.analyze_case(
            context=context,
        )

        # --------------------------------------------------------------
        # Recommended Actions
        # --------------------------------------------------------------

        next_actions = self.next_action_engine.recommend_next_actions(
            context=context,
            reasoning=reasoning,
        )

        # --------------------------------------------------------------
        # Narrative Summaries
        # --------------------------------------------------------------

        summaries = self.summary_engine.generate_summaries(
            context=context,
            reasoning=reasoning,
            next_actions=next_actions,
        )

        # --------------------------------------------------------------
        # Unified AI Result
        # --------------------------------------------------------------

        result = {
            "case_id": case_id,
            "tenant_id": tenant_id,

            "context": context,
            "reasoning": reasoning,
            "next_actions": next_actions,
            "summaries": summaries,

            "priority_score":
                context.get("operational_priority_score"),

            "severity":
                context.get("severity"),

            "status":
                context.get("status"),

            "generated_at_ms":
                _now_ms(),

            "engine":
                "CopilotService",
        }

        return result

    # ------------------------------------------------------------------
    # Lightweight Summary APIs
    # ------------------------------------------------------------------

    def summarize_case(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
        summary_type: str = "analyst",
    ) -> Dict[str, Any]:

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        summaries = (
            analysis.get("summaries")
            or {}
        )

        mapping = {
            "executive":
                summaries.get("executive_summary"),

            "analyst":
                summaries.get("analyst_summary"),

            "escalation":
                summaries.get("escalation_summary"),

            "legal":
                summaries.get("legal_summary"),

            "export_control":
                summaries.get("export_control_summary"),

            "shift_handoff":
                summaries.get("shift_handoff_summary"),
        }

        return {
            "case_id": case_id,
            "summary_type": summary_type,
            "summary": mapping.get(summary_type),
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Explainability APIs
    # ------------------------------------------------------------------

    def explain_escalation(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        return {
            "case_id": case_id,
            "escalation_reasoning":
                analysis["reasoning"].get(
                    "escalation_reasoning",
                    {},
                ),

            "priority_reasoning":
                analysis["reasoning"].get(
                    "operational_priority_reasoning",
                    {},
                ),

            "generated_at_ms":
                _now_ms(),
        }

    def explain_graph_risk(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        context = analysis.get("context") or {}

        return {
            "case_id": case_id,

            "graph_risk":
                context.get("graph_risk"),

            "linked_cases":
                context.get("linked_cases"),

            "entities":
                context.get("entities"),

            "campaign":
                context.get("campaign"),

            "blast_radius":
                context.get("blast_radius_score"),

            "generated_at_ms":
                _now_ms(),
        }

    def explain_campaign(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        return {
            "case_id": case_id,

            "campaign_reasoning":
                analysis["reasoning"].get(
                    "campaign_reasoning",
                    {},
                ),

            "campaign":
                analysis["context"].get(
                    "campaign",
                    {},
                ),

            "linked_cases":
                analysis["context"].get(
                    "linked_cases",
                    [],
                ),

            "generated_at_ms":
                _now_ms(),
        }

    def explain_export_control(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        return {
            "case_id": case_id,

            "export_control_reasoning":
                analysis["reasoning"].get(
                    "export_control_reasoning",
                    {},
                ),

            "legal_review_reasoning":
                analysis["reasoning"].get(
                    "legal_review_reasoning",
                    {},
                ),

            "recommended_actions":
                analysis["next_actions"].get(
                    "recommended_actions",
                    [],
                ),

            "generated_at_ms":
                _now_ms(),
        }

    # ------------------------------------------------------------------
    # Recommendation APIs
    # ------------------------------------------------------------------

    def get_recommended_actions(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        return {
            "case_id": case_id,

            "recommended_actions":
                analysis["next_actions"].get(
                    "recommended_actions",
                    [],
                ),

            "top_action":
                analysis["next_actions"].get(
                    "top_action",
                ),

            "generated_at_ms":
                _now_ms(),
        }

    # ------------------------------------------------------------------
    # Queue Intelligence APIs
    # ------------------------------------------------------------------

    def analyze_queue(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:

        queue_context = (
            self.context_builder.build_queue_context(
                tenant_id=tenant_id,
                limit=limit,
            )
        )

        analyzed_cases = []

        for case_context in queue_context.get(
            "cases",
            [],
        ):

            if case_context.get("error"):
                analyzed_cases.append(case_context)
                continue

            try:

                reasoning = self.reasoner.analyze_case(
                    context=case_context,
                )

                next_actions = (
                    self.next_action_engine
                    .recommend_next_actions(
                        context=case_context,
                        reasoning=reasoning,
                    )
                )

                analyzed_cases.append({
                    "case_id":
                        case_context.get("case_id"),

                    "severity":
                        case_context.get("severity"),

                    "status":
                        case_context.get("status"),

                    "priority_score":
                        case_context.get(
                            "operational_priority_score"
                        ),

                    "top_action":
                        next_actions.get("top_action"),

                    "campaign":
                        case_context.get("campaign"),

                    "sla":
                        case_context.get("sla"),

                    "summary":
                        reasoning.get(
                            "summary",
                            {},
                        ),
                })

            except Exception as exc:

                analyzed_cases.append({
                    "case_id":
                        case_context.get("case_id"),

                    "error":
                        str(exc),
                })

        analyzed_cases = sorted(
            analyzed_cases,
            key=lambda x: (
                x.get("priority_score") or 0
            ),
            reverse=True,
        )

        return {
            "tenant_id":
                tenant_id,

            "case_count":
                len(analyzed_cases),

            "cases":
                analyzed_cases,

            "generated_at_ms":
                _now_ms(),

            "engine":
                "CopilotService.QueueAnalysis",
        }

    # ------------------------------------------------------------------
    # Operational Assistant APIs
    # ------------------------------------------------------------------

    def build_operational_briefing(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        context = analysis["context"]
        summaries = analysis["summaries"]
        reasoning = analysis["reasoning"]
        next_actions = analysis["next_actions"]

        return {
            "case_id": case_id,

            "headline":
                summaries["executive_summary"].get(
                    "summary"
                ),

            "severity":
                context.get("severity"),

            "status":
                context.get("status"),

            "priority_score":
                context.get(
                    "operational_priority_score"
                ),

            "sla":
                context.get("sla"),

            "top_action":
                next_actions.get("top_action"),

            "critical_reasons":
                reasoning.get(
                    "why_case_matters",
                    {}
                ).get(
                    "reasons",
                    []
                ),

            "campaign":
                context.get("campaign"),

            "blast_radius":
                context.get(
                    "blast_radius_score"
                ),

            "generated_at_ms":
                _now_ms(),
        }

    # ------------------------------------------------------------------
    # Future Chat / Prompt APIs
    # ------------------------------------------------------------------

    def ask_copilot(
        self,
        *,
        case_id: Any,
        question: str,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Future conversational copilot API.

        Placeholder for:
        - LLM reasoning
        - semantic retrieval
        - operational Q&A
        - graph explanations
        - timeline reasoning
        """

        analysis = self.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        return {
            "case_id":
                case_id,

            "question":
                question,

            "answer":
                (
                    "Copilot conversational reasoning "
                    "not yet implemented."
                ),

            "context":
                {
                    "severity":
                        analysis["context"].get(
                            "severity"
                        ),

                    "status":
                        analysis["context"].get(
                            "status"
                        ),

                    "priority_score":
                        analysis["context"].get(
                            "operational_priority_score"
                        ),
                },

            "generated_at_ms":
                _now_ms(),
        }

    # ------------------------------------------------------------------
    # AI ORCHESTRATION
    # ------------------------------------------------------------------

    def execute_recommendation(
            self,
            *,
            case_id: Any,
            recommendation: Dict[str, Any],
            tenant_id: Optional[str] = None,
            actor: str = "copilot",
            dry_run: bool = True,
    ) -> Dict[str, Any]:

        if self.autonomous_response_engine is None:
            return {
                "status": "unavailable",
                "reason":
                    "autonomous_response_engine not configured",
            }

        context = self.build_operational_context(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        return self.autonomous_response_engine.process_action(
            case_id=case_id,
            tenant_id=tenant_id,
            context=context,
            action=recommendation,
            actor=actor,
            dry_run=dry_run,
        )

    def execute_playbook(
            self,
            *,
            case_id: Any,
            playbook: str,
            tenant_id: Optional[str] = None,
            actor: str = "copilot",
            dry_run: bool = True,
    ) -> Dict[str, Any]:

        if self.playbook_orchestrator is None:
            return {
                "status": "unavailable",
                "reason":
                    "playbook_orchestrator not configured",
            }

        return self.playbook_orchestrator.execute_playbook(
            case_id=case_id,
            playbook=playbook,
            tenant_id=tenant_id,
            actor=actor,
            dry_run=dry_run,
        )

    def execute_containment(
            self,
            *,
            case_id: Any,
            action: Dict[str, Any],
            tenant_id: Optional[str] = None,
            actor: str = "copilot",
            dry_run: bool = True,
    ) -> Dict[str, Any]:

        if self.containment_engine is None:
            return {
                "status": "unavailable",
                "reason":
                    "containment_engine not configured",
            }

        return self.containment_engine.execute_containment_action(
            case_id=case_id,
            action=action,
            tenant_id=tenant_id,
            actor=actor,
            dry_run=dry_run,
        )