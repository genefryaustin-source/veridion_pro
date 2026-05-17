"""
core/runtime/execution_domain_manager.py

Execution Domain Manager.

Purpose:
- sovereign execution boundary enforcement
- tenant-to-domain mapping
- workload sensitivity classification
- GovCloud / air-gapped / export-controlled domain controls
- domain-aware placement validation
- domain quarantine and emergency freeze

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden runtime mutation
- explicit service-owned state
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


DOMAIN_PUBLIC = "PUBLIC"
DOMAIN_GOVCLOUD = "GOVCLOUD"
DOMAIN_AIRGAPPED = "AIRGAPPED"
DOMAIN_CLASSIFIED = "CLASSIFIED"
DOMAIN_EXPORT_CONTROLLED = "EXPORT_CONTROLLED"
DOMAIN_CUSTOMER_ISOLATED = "CUSTOMER_ISOLATED"
DOMAIN_FORENSICS_ONLY = "FORENSICS_ONLY"
DOMAIN_LOCAL_DEV = "LOCAL_DEV"

DOMAIN_ACTIVE = "ACTIVE"
DOMAIN_DEGRADED = "DEGRADED"
DOMAIN_QUARANTINED = "QUARANTINED"
DOMAIN_FROZEN = "FROZEN"
DOMAIN_OFFLINE = "OFFLINE"

SENSITIVITY_PUBLIC = "PUBLIC"
SENSITIVITY_INTERNAL = "INTERNAL"
SENSITIVITY_CONFIDENTIAL = "CONFIDENTIAL"
SENSITIVITY_CUI = "CUI"
SENSITIVITY_EXPORT_CONTROLLED = "EXPORT_CONTROLLED"
SENSITIVITY_CLASSIFIED = "CLASSIFIED"

DECISION_ALLOWED = "ALLOWED"
DECISION_BLOCKED = "BLOCKED"
DECISION_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class ExecutionDomain:
    domain_id: str
    name: str
    domain_type: str
    status: str = DOMAIN_ACTIVE
    region: str = "local"
    trust_level: str = "HIGH"
    tenant_ids: List[str] = field(default_factory=list)
    allowed_sensitivities: List[str] = field(default_factory=list)
    allowed_capabilities: List[str] = field(default_factory=list)
    denied_capabilities: List[str] = field(default_factory=list)
    requires_approval: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    updated_at_ms: int = field(default_factory=_now_ms)
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DomainExecutionDecision:
    decision_id: str
    tenant_id: str
    domain_id: Optional[str]
    allowed: bool
    decision: str
    reason: str
    sensitivity: str
    capability: Optional[str] = None
    requires_approval: bool = False
    blocked_reasons: List[str] = field(default_factory=list)
    candidate_domains: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionDomainManager:
    def __init__(
        self,
        *,
        registry: Any = None,
        policy_manager: Any = None,
        federation_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
        self.registry = registry or getattr(storage, "runtime_service_registry", None)
        self.policy_manager = policy_manager or getattr(storage, "runtime_policy_manager", None)
        self.federation_manager = federation_manager or getattr(storage, "runtime_federation_manager", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._domains: Dict[str, ExecutionDomain] = {}
        self._tenant_domain_map: Dict[str, List[str]] = {}
        self._decisions: List[DomainExecutionDecision] = []

        self._register_default_domains()

    # ========================================================
    # DEFAULT DOMAINS
    # ========================================================

    def _register_default_domains(self) -> None:
        self.register_domain(
            domain_id="domain-local-dev",
            name="Local Development Domain",
            domain_type=DOMAIN_LOCAL_DEV,
            region="local",
            tenant_ids=[DEFAULT_TENANT],
            allowed_sensitivities=[
                SENSITIVITY_PUBLIC,
                SENSITIVITY_INTERNAL,
                SENSITIVITY_CONFIDENTIAL,
            ],
            allowed_capabilities=[
                "execution_queue",
                "worker_orchestration",
                "runtime_governance",
                "simulation",
            ],
            metadata={
                "default": True,
                "production_safe": False,
            },
        )

        self.register_domain(
            domain_id="domain-public",
            name="Public / Commercial Runtime Domain",
            domain_type=DOMAIN_PUBLIC,
            region="commercial",
            tenant_ids=[],
            allowed_sensitivities=[
                SENSITIVITY_PUBLIC,
                SENSITIVITY_INTERNAL,
                SENSITIVITY_CONFIDENTIAL,
            ],
            allowed_capabilities=[
                "execution_queue",
                "worker_orchestration",
                "runtime_governance",
                "connector_operations",
            ],
            metadata={
                "default": True,
                "production_safe": True,
            },
        )

    # ========================================================
    # DOMAIN REGISTRATION
    # ========================================================

    def register_domain(
        self,
        *,
        domain_id: Optional[str] = None,
        name: str,
        domain_type: str,
        region: str = "local",
        trust_level: str = "HIGH",
        tenant_ids: Optional[List[str]] = None,
        allowed_sensitivities: Optional[List[str]] = None,
        allowed_capabilities: Optional[List[str]] = None,
        denied_capabilities: Optional[List[str]] = None,
        requires_approval: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionDomain:
        domain_id = domain_id or f"domain-{uuid.uuid4().hex[:12].upper()}"

        domain = ExecutionDomain(
            domain_id=domain_id,
            name=name,
            domain_type=domain_type,
            region=region,
            trust_level=trust_level,
            tenant_ids=tenant_ids or [],
            allowed_sensitivities=allowed_sensitivities or [],
            allowed_capabilities=allowed_capabilities or [],
            denied_capabilities=denied_capabilities or [],
            requires_approval=requires_approval,
            metadata=metadata or {},
        )

        self._domains[domain_id] = domain

        for tenant_id in domain.tenant_ids:
            self._tenant_domain_map.setdefault(tenant_id, [])
            if domain_id not in self._tenant_domain_map[tenant_id]:
                self._tenant_domain_map[tenant_id].append(domain_id)

        self._emit(
            "EXECUTION_DOMAIN_REGISTERED",
            domain.to_dict(),
        )

        return domain

    def assign_tenant_to_domain(
        self,
        *,
        tenant_id: str,
        domain_id: str,
    ) -> bool:
        domain = self._domains.get(domain_id)

        if not domain:
            return False

        if tenant_id not in domain.tenant_ids:
            domain.tenant_ids.append(tenant_id)

        self._tenant_domain_map.setdefault(tenant_id, [])

        if domain_id not in self._tenant_domain_map[tenant_id]:
            self._tenant_domain_map[tenant_id].append(domain_id)

        domain.updated_at_ms = _now_ms()

        self._emit(
            "TENANT_ASSIGNED_TO_EXECUTION_DOMAIN",
            {
                "tenant_id": tenant_id,
                "domain_id": domain_id,
            },
        )

        return True

    # ========================================================
    # DOMAIN DECISIONING
    # ========================================================

    def can_execute(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        sensitivity: str = SENSITIVITY_INTERNAL,
        capability: Optional[str] = None,
        required_domain_type: Optional[str] = None,
        target_domain_id: Optional[str] = None,
        workload: Optional[Dict[str, Any]] = None,
    ) -> DomainExecutionDecision:
        workload = workload or {}

        candidates = self._candidate_domains(
            tenant_id=tenant_id,
            target_domain_id=target_domain_id,
            required_domain_type=required_domain_type,
        )

        blocked_reasons: List[str] = []

        for domain in candidates:
            ok, reasons = self._domain_allows(
                domain,
                tenant_id=tenant_id,
                sensitivity=sensitivity,
                capability=capability,
                workload=workload,
            )

            if ok:
                decision_type = (
                    DECISION_REQUIRES_APPROVAL
                    if domain.requires_approval
                    else DECISION_ALLOWED
                )

                decision = DomainExecutionDecision(
                    decision_id=self._new_decision_id(),
                    tenant_id=tenant_id,
                    domain_id=domain.domain_id,
                    allowed=not domain.requires_approval,
                    decision=decision_type,
                    reason=(
                        "Execution allowed."
                        if not domain.requires_approval
                        else "Execution requires approval for this domain."
                    ),
                    sensitivity=sensitivity,
                    capability=capability,
                    requires_approval=domain.requires_approval,
                    candidate_domains=[d.domain_id for d in candidates],
                    metadata={
                        "domain_type": domain.domain_type,
                        "region": domain.region,
                        "trust_level": domain.trust_level,
                    },
                )

                self._record_decision(decision)
                return decision

            blocked_reasons.extend(
                [f"{domain.domain_id}: {r}" for r in reasons]
            )

        decision = DomainExecutionDecision(
            decision_id=self._new_decision_id(),
            tenant_id=tenant_id,
            domain_id=None,
            allowed=False,
            decision=DECISION_BLOCKED,
            reason="No execution domain allowed this workload.",
            sensitivity=sensitivity,
            capability=capability,
            blocked_reasons=blocked_reasons,
            candidate_domains=[d.domain_id for d in candidates],
            metadata={
                "required_domain_type": required_domain_type,
                "target_domain_id": target_domain_id,
            },
        )

        self._record_decision(decision)
        return decision

    def _candidate_domains(
        self,
        *,
        tenant_id: str,
        target_domain_id: Optional[str],
        required_domain_type: Optional[str],
    ) -> List[ExecutionDomain]:
        if target_domain_id:
            domain = self._domains.get(target_domain_id)
            return [domain] if domain else []

        domain_ids = self._tenant_domain_map.get(tenant_id, [])

        if domain_ids:
            domains = [
                self._domains[d]
                for d in domain_ids
                if d in self._domains
            ]
        else:
            domains = list(self._domains.values())

        if required_domain_type:
            domains = [
                d for d in domains
                if d.domain_type == required_domain_type
            ]

        return domains

    def _domain_allows(
        self,
        domain: ExecutionDomain,
        *,
        tenant_id: str,
        sensitivity: str,
        capability: Optional[str],
        workload: Dict[str, Any],
    ) -> tuple[bool, List[str]]:
        reasons: List[str] = []

        if domain.status in {
            DOMAIN_QUARANTINED,
            DOMAIN_FROZEN,
            DOMAIN_OFFLINE,
        }:
            reasons.append(f"domain_status={domain.status}")

        if domain.tenant_ids and tenant_id not in domain.tenant_ids:
            reasons.append("tenant_not_assigned_to_domain")

        if domain.allowed_sensitivities and sensitivity not in domain.allowed_sensitivities:
            reasons.append(f"sensitivity_not_allowed={sensitivity}")

        if capability and capability in domain.denied_capabilities:
            reasons.append(f"capability_denied={capability}")

        if capability and domain.allowed_capabilities:
            if capability not in domain.allowed_capabilities:
                reasons.append(f"capability_not_allowed={capability}")

        if sensitivity == SENSITIVITY_EXPORT_CONTROLLED:
            if domain.domain_type not in {
                DOMAIN_EXPORT_CONTROLLED,
                DOMAIN_GOVCLOUD,
                DOMAIN_AIRGAPPED,
                DOMAIN_CUSTOMER_ISOLATED,
            }:
                reasons.append("export_controlled_domain_required")

        if sensitivity == SENSITIVITY_CLASSIFIED:
            if domain.domain_type not in {
                DOMAIN_CLASSIFIED,
                DOMAIN_AIRGAPPED,
            }:
                reasons.append("classified_domain_required")

        if bool(workload.get("requires_govcloud")):
            if domain.domain_type != DOMAIN_GOVCLOUD:
                reasons.append("govcloud_required")

        if bool(workload.get("requires_airgap")):
            if domain.domain_type != DOMAIN_AIRGAPPED:
                reasons.append("airgap_required")

        if bool(workload.get("forensics_only")):
            if domain.domain_type != DOMAIN_FORENSICS_ONLY:
                reasons.append("forensics_only_domain_required")

        return len(reasons) == 0, reasons

    # ========================================================
    # CLASSIFICATION HELPERS
    # ========================================================

    def classify_workload(
        self,
        workload: Dict[str, Any],
    ) -> str:
        categories = [
            str(c).upper()
            for c in workload.get("categories", [])
        ]

        flags = [
            str(f).upper()
            for f in workload.get("flags", [])
        ]

        text = str(workload.get("text", "")).upper()

        combined = set(categories + flags)

        if "CLASSIFIED" in combined:
            return SENSITIVITY_CLASSIFIED

        if (
            "EXPORT_CONTROL" in combined
            or "EXPORT_CONTROLLED" in combined
            or "ITAR" in combined
            or "EAR" in combined
            or "USML" in text
            or "ITAR" in text
        ):
            return SENSITIVITY_EXPORT_CONTROLLED

        if "CUI" in combined or "CONTROLLED_UNCLASSIFIED_INFORMATION" in combined:
            return SENSITIVITY_CUI

        if "CONFIDENTIAL" in combined:
            return SENSITIVITY_CONFIDENTIAL

        if "PUBLIC" in combined:
            return SENSITIVITY_PUBLIC

        return SENSITIVITY_INTERNAL

    def validate_workload_execution(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Dict[str, Any],
        capability: Optional[str] = None,
        target_domain_id: Optional[str] = None,
    ) -> DomainExecutionDecision:
        sensitivity = self.classify_workload(workload)

        return self.can_execute(
            tenant_id=tenant_id,
            sensitivity=sensitivity,
            capability=capability,
            target_domain_id=target_domain_id,
            workload=workload,
        )

    # ========================================================
    # DOMAIN STATE
    # ========================================================

    def quarantine_domain(
        self,
        domain_id: str,
        *,
        reason: str,
    ) -> bool:
        return self._set_domain_status(
            domain_id,
            DOMAIN_QUARANTINED,
            reason=reason,
        )

    def freeze_domain(
        self,
        domain_id: str,
        *,
        reason: str,
    ) -> bool:
        return self._set_domain_status(
            domain_id,
            DOMAIN_FROZEN,
            reason=reason,
        )

    def restore_domain(
        self,
        domain_id: str,
    ) -> bool:
        return self._set_domain_status(
            domain_id,
            DOMAIN_ACTIVE,
            reason=None,
        )

    def _set_domain_status(
        self,
        domain_id: str,
        status: str,
        *,
        reason: Optional[str],
    ) -> bool:
        domain = self._domains.get(domain_id)

        if not domain:
            return False

        domain.status = status
        domain.updated_at_ms = _now_ms()
        domain.last_error = reason

        self._emit(
            "EXECUTION_DOMAIN_STATUS_CHANGED",
            {
                "domain_id": domain_id,
                "status": status,
                "reason": reason,
            },
        )

        return True

    # ========================================================
    # READS
    # ========================================================

    def list_domains(
        self,
        *,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        domain_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        domains = list(self._domains.values())

        if tenant_id:
            domains = [
                d for d in domains
                if not d.tenant_ids or tenant_id in d.tenant_ids
            ]

        if status:
            domains = [
                d for d in domains
                if d.status == status
            ]

        if domain_type:
            domains = [
                d for d in domains
                if d.domain_type == domain_type
            ]

        return [
            d.to_dict()
            for d in domains
        ]

    def get_domain(
        self,
        domain_id: str,
    ) -> Optional[Dict[str, Any]]:
        domain = self._domains.get(domain_id)
        return domain.to_dict() if domain else None

    def list_decisions(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        decisions = sorted(
            self._decisions,
            key=lambda d: d.created_at_ms,
            reverse=True,
        )

        return [
            d.to_dict()
            for d in decisions[:limit]
        ]

    def domain_health(self) -> Dict[str, Any]:
        domains = list(self._domains.values())

        total = len(domains)
        active = len([d for d in domains if d.status == DOMAIN_ACTIVE])
        degraded = len([d for d in domains if d.status == DOMAIN_DEGRADED])
        quarantined = len([d for d in domains if d.status == DOMAIN_QUARANTINED])
        frozen = len([d for d in domains if d.status == DOMAIN_FROZEN])
        offline = len([d for d in domains if d.status == DOMAIN_OFFLINE])

        risk = "LOW"

        if degraded:
            risk = "MEDIUM"

        if quarantined or frozen:
            risk = "HIGH"

        if active == 0 and total > 0:
            risk = "CRITICAL"

        return {
            "total_domains": total,
            "active": active,
            "degraded": degraded,
            "quarantined": quarantined,
            "frozen": frozen,
            "offline": offline,
            "risk": risk,
        }

    # ========================================================
    # INTERNAL
    # ========================================================

    def _record_decision(
        self,
        decision: DomainExecutionDecision,
    ) -> None:
        self._decisions.append(decision)
        self._decisions = self._decisions[-500:]

        self._emit(
            "EXECUTION_DOMAIN_DECISION",
            decision.to_dict(),
        )

    def _new_decision_id(self) -> str:
        return f"DOMAIN-DECISION-{uuid.uuid4().hex[:12].upper()}"

    def _emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                source="execution_domain_manager",
                severity=payload.get("decision") or payload.get("status") or "INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_EXECUTION_DOMAIN_MANAGER: Optional[
    ExecutionDomainManager
] = None


def get_execution_domain_manager(
    *,
    registry: Any = None,
    policy_manager: Any = None,
    federation_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> ExecutionDomainManager:
    global _DEFAULT_EXECUTION_DOMAIN_MANAGER

    if reset or _DEFAULT_EXECUTION_DOMAIN_MANAGER is None:
        _DEFAULT_EXECUTION_DOMAIN_MANAGER = ExecutionDomainManager(
            registry=registry,
            policy_manager=policy_manager,
            federation_manager=federation_manager,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_EXECUTION_DOMAIN_MANAGER