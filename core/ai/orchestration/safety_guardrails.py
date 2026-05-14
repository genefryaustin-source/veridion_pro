from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


class SafetyGuardrails:
    """
    Operational AI safety enforcement layer.

    Responsibilities:
    - dangerous-action prevention
    - execution throttling
    - rollback protection
    - mass-action detection
    - runaway orchestration prevention
    - recursive orchestration prevention
    - emergency stop controls
    """

    DANGEROUS_ACTIONS = {
        "WIPE_DEVICE",
        "DELETE_EVIDENCE",
        "PURGE_MESSAGE",
        "DEACTIVATE_USER",
        "DISABLE_USER",
        "MERGE_INVESTIGATIONS",
        "EXPORT_EVIDENCE",
        "ISOLATE_ENDPOINT",
        "QUARANTINE_MAILBOX",
    }

    REQUIRES_ROLLBACK_PLAN = {
        "DISABLE_USER",
        "SUSPEND_USER",
        "ISOLATE_ENDPOINT",
        "REMOTE_LOCK",
        "QUARANTINE_MAILBOX",
        "MOVE_MESSAGE_TO_JUNK",
        "RETIRE_DEVICE",
    }

    DEFAULT_LIMITS = {
        "max_actions_per_run": 10,
        "max_devices_per_run": 5,
        "max_users_per_run": 3,
        "max_mailboxes_per_run": 3,
        "max_messages_per_run": 10,
        "max_recursive_depth": 2,
        "cooldown_seconds": 60,
    }

    def __init__(
        self,
        *,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        custom_limits: Optional[Dict[str, int]] = None,
    ):
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.limits = dict(self.DEFAULT_LIMITS)

        if custom_limits:
            self.limits.update(custom_limits)

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def evaluate_run(
        self,
        *,
        actions: List[Dict[str, Any]],
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "safety_guardrails",
        recursion_depth: int = 0,
        orchestration_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        orchestration_id = (
            orchestration_id
            or f"SAFE-{uuid.uuid4().hex[:12].upper()}"
        )

        violations: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        if self.is_emergency_stopped(tenant_id=tenant_id):
            violations.append(
                self._violation(
                    code="EMERGENCY_STOP_ACTIVE",
                    message="Emergency stop is active for this tenant or globally.",
                )
            )

        if recursion_depth > self.limits["max_recursive_depth"]:
            violations.append(
                self._violation(
                    code="RECURSIVE_ORCHESTRATION_BLOCKED",
                    message="Recursive orchestration depth exceeds allowed limit.",
                )
            )

        if len(actions) > self.limits["max_actions_per_run"]:
            violations.append(
                self._violation(
                    code="TOO_MANY_ACTIONS",
                    message=(
                        f"Action count {len(actions)} exceeds limit "
                        f"{self.limits['max_actions_per_run']}."
                    ),
                )
            )

        blast = self.detect_mass_action(actions=actions)

        if not blast["within_limits"]:
            violations.extend(blast["violations"])

        rollback = self.validate_rollback_protection(actions=actions)

        if not rollback["valid"]:
            violations.extend(rollback["violations"])

        runaway = self.detect_runaway_orchestration(
            actions=actions,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
        )

        if runaway.get("suspected"):
            violations.append(
                self._violation(
                    code="RUNAWAY_ORCHESTRATION_SUSPECTED",
                    message="Similar orchestration activity was detected recently.",
                    details=runaway,
                )
            )

        for action in actions:
            action_code = _upper(action.get("action") or action.get("label"))

            if action_code in self.DANGEROUS_ACTIONS:
                warnings.append(
                    self._warning(
                        code="DANGEROUS_ACTION",
                        message=f"{action_code} is classified as dangerous.",
                        details=action,
                    )
                )

        result = {
            "orchestration_id": orchestration_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "actor": actor,
            "allowed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "action_count": len(actions),
            "recursion_depth": recursion_depth,
            "evaluated_at_ms": _now_ms(),
            "engine": "SafetyGuardrails",
        }

        self._record_event(
            case_id=case_id,
            event_type="SAFETY_GUARDRAILS_EVALUATED",
            actor=actor,
            details=result,
        )

        self._publish(
            event_type="SAFETY_GUARDRAILS_EVALUATED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=result,
        )

        return result

    def evaluate_action(
        self,
        *,
        action: Dict[str, Any],
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "safety_guardrails",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.evaluate_run(
            actions=[action],
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            context=context,
        )

    # ------------------------------------------------------------------
    # Mass Action Detection
    # ------------------------------------------------------------------

    def detect_mass_action(
        self,
        *,
        actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        counts = {
            "devices": 0,
            "users": 0,
            "mailboxes": 0,
            "messages": 0,
        }

        for action in actions:
            targets = action.get("targets") or {}

            counts["devices"] += _safe_int(targets.get("devices"), 0)
            counts["users"] += _safe_int(targets.get("users"), 0)
            counts["mailboxes"] += _safe_int(targets.get("mailboxes"), 0)
            counts["messages"] += _safe_int(targets.get("messages"), 0)

            if action.get("device_id") or action.get("target_device"):
                counts["devices"] += 1

            if action.get("user_id") or action.get("target_user"):
                counts["users"] += 1

            if action.get("mailbox_id") or action.get("target_mailbox"):
                counts["mailboxes"] += 1

            if action.get("message_id"):
                counts["messages"] += 1

        violations = []

        if counts["devices"] > self.limits["max_devices_per_run"]:
            violations.append(
                self._violation(
                    code="DEVICE_BLAST_RADIUS_EXCEEDED",
                    message=(
                        f"Device count {counts['devices']} exceeds limit "
                        f"{self.limits['max_devices_per_run']}."
                    ),
                    details=counts,
                )
            )

        if counts["users"] > self.limits["max_users_per_run"]:
            violations.append(
                self._violation(
                    code="USER_BLAST_RADIUS_EXCEEDED",
                    message=(
                        f"User count {counts['users']} exceeds limit "
                        f"{self.limits['max_users_per_run']}."
                    ),
                    details=counts,
                )
            )

        if counts["mailboxes"] > self.limits["max_mailboxes_per_run"]:
            violations.append(
                self._violation(
                    code="MAILBOX_BLAST_RADIUS_EXCEEDED",
                    message=(
                        f"Mailbox count {counts['mailboxes']} exceeds limit "
                        f"{self.limits['max_mailboxes_per_run']}."
                    ),
                    details=counts,
                )
            )

        if counts["messages"] > self.limits["max_messages_per_run"]:
            violations.append(
                self._violation(
                    code="MESSAGE_BLAST_RADIUS_EXCEEDED",
                    message=(
                        f"Message count {counts['messages']} exceeds limit "
                        f"{self.limits['max_messages_per_run']}."
                    ),
                    details=counts,
                )
            )

        return {
            "within_limits": len(violations) == 0,
            "counts": counts,
            "violations": violations,
        }

    # ------------------------------------------------------------------
    # Rollback Protection
    # ------------------------------------------------------------------

    def validate_rollback_protection(
        self,
        *,
        actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        violations = []

        for action in actions:
            action_code = _upper(action.get("action") or action.get("label"))

            if action_code not in self.REQUIRES_ROLLBACK_PLAN:
                continue

            has_rollback = bool(
                action.get("rollback_action")
                or action.get("rollback_available")
                or action.get("reversible")
            )

            if not has_rollback:
                violations.append(
                    self._violation(
                        code="ROLLBACK_PLAN_REQUIRED",
                        message=f"{action_code} requires rollback metadata before execution.",
                        details=action,
                    )
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    # ------------------------------------------------------------------
    # Runaway / Recursive Protection
    # ------------------------------------------------------------------

    def detect_runaway_orchestration(
        self,
        *,
        actions: List[Dict[str, Any]],
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
    ) -> Dict[str, Any]:
        if self.ledger is None:
            return {
                "suspected": False,
                "reason": "No ledger configured.",
            }

        cooldown_ms = self.limits["cooldown_seconds"] * 1000
        since_ms = _now_ms() - cooldown_ms

        action_codes = sorted(
            [
                _upper(a.get("action") or a.get("label"))
                for a in actions
            ]
        )

        try:
            with self.ledger._connect() as con:
                rows = con.execute(
                    """
                    SELECT details
                    FROM case_events
                    WHERE case_id = ?
                      AND action IN (
                          'SAFETY_GUARDRAILS_EVALUATED',
                          'AI_AUTONOMOUS_RESPONSE_STARTED',
                          'AI_ORCHESTRATION_STARTED'
                      )
                      AND created_at_ms >= ?
                    ORDER BY created_at_ms DESC
                    LIMIT 10
                    """,
                    (case_id, since_ms),
                ).fetchall()

                for row in rows:
                    blob = str(dict(row))
                    if all(code in blob for code in action_codes):
                        return {
                            "suspected": True,
                            "reason": "Similar orchestration evaluated within cooldown window.",
                            "cooldown_seconds": self.limits["cooldown_seconds"],
                        }

        except Exception:
            pass

        return {
            "suspected": False,
            "reason": "No recent duplicate orchestration detected.",
        }

    # ------------------------------------------------------------------
    # Emergency Stop
    # ------------------------------------------------------------------

    def activate_emergency_stop(
        self,
        *,
        tenant_id: Optional[str] = None,
        actor: str = "safety_guardrails",
        reason: str = "Emergency stop activated",
    ) -> Dict[str, Any]:
        key = self._emergency_key(tenant_id)

        if self.ledger is not None:
            self._set_runtime_flag(
                key=key,
                value="1",
            )

        result = {
            "tenant_id": tenant_id,
            "active": True,
            "reason": reason,
            "actor": actor,
            "timestamp_ms": _now_ms(),
        }

        self._publish(
            event_type="AI_EMERGENCY_STOP_ACTIVATED",
            case_id=None,
            tenant_id=tenant_id,
            actor=actor,
            payload=result,
        )

        return result

    def clear_emergency_stop(
        self,
        *,
        tenant_id: Optional[str] = None,
        actor: str = "safety_guardrails",
        reason: str = "Emergency stop cleared",
    ) -> Dict[str, Any]:
        key = self._emergency_key(tenant_id)

        if self.ledger is not None:
            self._set_runtime_flag(
                key=key,
                value="0",
            )

        result = {
            "tenant_id": tenant_id,
            "active": False,
            "reason": reason,
            "actor": actor,
            "timestamp_ms": _now_ms(),
        }

        self._publish(
            event_type="AI_EMERGENCY_STOP_CLEARED",
            case_id=None,
            tenant_id=tenant_id,
            actor=actor,
            payload=result,
        )

        return result

    def is_emergency_stopped(
        self,
        *,
        tenant_id: Optional[str] = None,
    ) -> bool:
        global_flag = self._get_runtime_flag(
            key=self._emergency_key(None)
        )

        tenant_flag = self._get_runtime_flag(
            key=self._emergency_key(tenant_id)
        )

        return global_flag == "1" or tenant_flag == "1"

    # ------------------------------------------------------------------
    # Runtime Flags
    # ------------------------------------------------------------------

    def _set_runtime_flag(
        self,
        *,
        key: str,
        value: str,
    ) -> None:
        if self.ledger is None:
            return

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS runtime_flags (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    INSERT OR REPLACE INTO runtime_flags (
                        key,
                        value,
                        updated_at_ms
                    )
                    VALUES (?, ?, ?)
                    """,
                    (key, value, _now_ms()),
                )

                con.commit()

        except Exception:
            pass

    def _get_runtime_flag(
        self,
        *,
        key: str,
    ) -> Optional[str]:
        if self.ledger is None:
            return None

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS runtime_flags (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at_ms INTEGER
                    )
                    """
                )

                row = con.execute(
                    """
                    SELECT value
                    FROM runtime_flags
                    WHERE key = ?
                    LIMIT 1
                    """,
                    (key,),
                ).fetchone()

                if row:
                    return dict(row).get("value")

        except Exception:
            pass

        return None

    def _emergency_key(
        self,
        tenant_id: Optional[str],
    ) -> str:
        if tenant_id:
            return f"ai_emergency_stop:{tenant_id}"

        return "ai_emergency_stop:global"

    # ------------------------------------------------------------------
    # Result Helpers
    # ------------------------------------------------------------------

    def _violation(
        self,
        *,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "type": "violation",
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp_ms": _now_ms(),
        }

    def _warning(
        self,
        *,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "type": "warning",
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _record_event(
        self,
        *,
        case_id: Optional[Any],
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
        if self.ledger is None or case_id is None:
            return

        for method_name in [
            "add_case_event",
            "create_case_event",
            "record_case_event",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        event_type=event_type,
                        actor=actor,
                        details=details,
                    )
                    return
                except TypeError:
                    try:
                        method(case_id, event_type, actor, details)
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

    def _publish(
        self,
        *,
        event_type: str,
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is not None:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=actor,
                    source="safety_guardrails",
                )
            except Exception:
                pass

        if self.live_updates is not None:
            try:
                if case_id is not None:
                    self.live_updates.broadcast_case_update(
                        case_id=case_id,
                        tenant_id=tenant_id,
                        event_type=event_type,
                        payload=payload,
                        actor=actor,
                    )
                elif tenant_id is not None:
                    self.live_updates.broadcast_tenant_update(
                        tenant_id=tenant_id,
                        event_type=event_type,
                        payload=payload,
                        actor=actor,
                    )
            except Exception:
                pass