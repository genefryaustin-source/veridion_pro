from __future__ import annotations

import json
import threading
import time
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RealtimeEvent:
    """
    Canonical realtime event envelope.

    This is the universal event shape for:
    - websocket updates
    - activity feeds
    - notifications
    - audit/event replay
    - AI orchestration triggers
    """

    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_ms: int = field(default_factory=_now_ms)

    tenant_id: Optional[str] = None
    case_id: Optional[Any] = None
    actor: str = "system"
    source: str = "event_bus"

    severity: str = "INFO"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            default=str,
            ensure_ascii=False,
        )


class EventBus:
    """
    In-process realtime event bus.

    Responsibilities:
    - publish operational events
    - subscribe handlers
    - broadcast to all subscribers
    - optionally persist events through ledger
    - maintain short in-memory event history

    Future-compatible with:
    - Redis pub/sub
    - Kafka
    - AWS SNS/SQS
    - API Gateway WebSockets
    - EventBridge
    """

    def __init__(
        self,
        ledger: Any = None,
        max_history: int = 1000,
        persist_events: bool = True,
    ):
        self.ledger = ledger
        self.max_history = max_history
        self.persist_events = persist_events

        self._subscribers: Dict[str, List[Callable[[RealtimeEvent], None]]] = {}
        self._wildcard_subscribers: List[Callable[[RealtimeEvent], None]] = []
        self._history: List[RealtimeEvent] = []

        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    def publish(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        actor: str = "system",
        source: str = "event_bus",
        severity: str = "INFO",
    ) -> RealtimeEvent:
        event = RealtimeEvent(
            event_type=event_type,
            payload=payload or {},
            tenant_id=tenant_id,
            case_id=case_id,
            actor=actor,
            source=source,
            severity=severity,
        )

        self.publish_event(event)

        return event

    def publish_event(
        self,
        event: RealtimeEvent,
    ) -> None:
        with self._lock:
            self._append_history(event)

        if self.persist_events:
            self._persist_event(event)

        self._dispatch(event)

    # ------------------------------------------------------------------
    # Subscribe
    # ------------------------------------------------------------------

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[RealtimeEvent], None],
    ) -> None:
        """
        Subscribe a callback to one event type.

        Use "*" for wildcard subscription.
        """

        with self._lock:
            if event_type == "*":
                self._wildcard_subscribers.append(callback)
                return

            self._subscribers.setdefault(event_type, []).append(callback)

    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[RealtimeEvent], None],
    ) -> None:
        with self._lock:
            if event_type == "*":
                if callback in self._wildcard_subscribers:
                    self._wildcard_subscribers.remove(callback)
                return

            callbacks = self._subscribers.get(event_type, [])

            if callback in callbacks:
                callbacks.remove(callback)

    # ------------------------------------------------------------------
    # History / Replay
    # ------------------------------------------------------------------

    def get_history(
        self,
        *,
        event_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            events = list(self._history)

        if event_type:
            events = [
                e for e in events
                if e.event_type == event_type
            ]

        if tenant_id:
            events = [
                e for e in events
                if e.tenant_id == tenant_id
            ]

        if case_id is not None:
            events = [
                e for e in events
                if str(e.case_id) == str(case_id)
            ]

        events = sorted(
            events,
            key=lambda e: e.timestamp_ms,
            reverse=True,
        )

        return [
            e.to_dict()
            for e in events[:limit]
        ]

    def replay(
        self,
        *,
        event_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        limit: int = 100,
    ) -> List[RealtimeEvent]:
        with self._lock:
            events = list(self._history)

        if event_type:
            events = [
                e for e in events
                if e.event_type == event_type
            ]

        if tenant_id:
            events = [
                e for e in events
                if e.tenant_id == tenant_id
            ]

        if case_id is not None:
            events = [
                e for e in events
                if str(e.case_id) == str(case_id)
            ]

        return sorted(
            events,
            key=lambda e: e.timestamp_ms,
            reverse=True,
        )[:limit]

    # ------------------------------------------------------------------
    # Convenience Event Publishers
    # ------------------------------------------------------------------

    def case_created(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
        actor: str = "system",
        payload: Optional[Dict[str, Any]] = None,
    ) -> RealtimeEvent:
        return self.publish(
            "CASE_CREATED",
            payload or {},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="case_service",
        )

    def case_assigned(
        self,
        *,
        case_id: Any,
        analyst: str,
        tenant_id: Optional[str] = None,
        actor: str = "system",
    ) -> RealtimeEvent:
        return self.publish(
            "CASE_ASSIGNED",
            {
                "analyst": analyst,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="assignment_service",
        )

    def case_escalated(
        self,
        *,
        case_id: Any,
        reason: str,
        escalation_level: Optional[int] = None,
        tenant_id: Optional[str] = None,
        actor: str = "system",
    ) -> RealtimeEvent:
        return self.publish(
            "CASE_ESCALATED",
            {
                "reason": reason,
                "escalation_level": escalation_level,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="escalation_service",
            severity="HIGH",
        )

    def sla_breached(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
        actor: str = "system",
        payload: Optional[Dict[str, Any]] = None,
    ) -> RealtimeEvent:
        return self.publish(
            "SLA_BREACHED",
            payload or {},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="sla_service",
            severity="HIGH",
        )

    def approval_requested(
        self,
        *,
        case_id: Any,
        approval_type: str,
        tenant_id: Optional[str] = None,
        actor: str = "system",
    ) -> RealtimeEvent:
        return self.publish(
            "APPROVAL_REQUESTED",
            {
                "approval_type": approval_type,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="approval_service",
        )

    def graph_updated(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
        actor: str = "system",
        payload: Optional[Dict[str, Any]] = None,
    ) -> RealtimeEvent:
        return self.publish(
            "GRAPH_UPDATED",
            payload or {},
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="graph_service",
        )

    def campaign_detected(
        self,
        *,
        case_id: Any,
        campaign_id: str,
        tenant_id: Optional[str] = None,
        actor: str = "system",
        payload: Optional[Dict[str, Any]] = None,
    ) -> RealtimeEvent:
        data = payload or {}
        data["campaign_id"] = campaign_id

        return self.publish(
            "CAMPAIGN_DETECTED",
            data,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="campaign_detection_service",
            severity="HIGH",
        )

    def playbook_executed(
        self,
        *,
        case_id: Any,
        playbook_name: str,
        action: Optional[str] = None,
        tenant_id: Optional[str] = None,
        actor: str = "system",
    ) -> RealtimeEvent:
        return self.publish(
            "PLAYBOOK_EXECUTED",
            {
                "playbook_name": playbook_name,
                "action": action,
            },
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="playbook_service",
        )

    # ------------------------------------------------------------------
    # Internal Dispatch
    # ------------------------------------------------------------------

    def _dispatch(
        self,
        event: RealtimeEvent,
    ) -> None:
        with self._lock:
            direct_callbacks = list(
                self._subscribers.get(
                    event.event_type,
                    [],
                )
            )

            wildcard_callbacks = list(
                self._wildcard_subscribers
            )

        callbacks = direct_callbacks + wildcard_callbacks

        for callback in callbacks:
            try:
                callback(event)
            except Exception:
                self._handle_callback_error(
                    event=event,
                    callback=callback,
                )

    def _append_history(
        self,
        event: RealtimeEvent,
    ) -> None:
        self._history.append(event)

        if len(self._history) > self.max_history:
            self._history = self._history[-self.max_history:]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist_event(
        self,
        event: RealtimeEvent,
    ) -> None:
        if self.ledger is None:
            return

        for method_name in [
            "record_realtime_event",
            "add_realtime_event",
            "add_event",
            "record_event",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    method(event.to_dict())
                    return
                except TypeError:
                    try:
                        method(
                            event_type=event.event_type,
                            payload_json=event.to_json(),
                            tenant_id=event.tenant_id,
                            case_id=event.case_id,
                            actor=event.actor,
                            source=event.source,
                            severity=event.severity,
                            timestamp_ms=event.timestamp_ms,
                        )
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

        if event.case_id is not None:
            for method_name in [
                "add_case_event",
                "create_case_event",
                "record_case_event",
            ]:
                method = getattr(self.ledger, method_name, None)

                if callable(method):
                    try:
                        method(
                            case_id=event.case_id,
                            event_type=event.event_type,
                            actor=event.actor,
                            details={
                                "payload": event.payload,
                                "event_id": event.event_id,
                                "source": event.source,
                                "severity": event.severity,
                                "timestamp_ms": event.timestamp_ms,
                            },
                        )
                        return
                    except TypeError:
                        try:
                            method(
                                event.case_id,
                                event.event_type,
                                event.actor,
                                json.dumps(event.payload, default=str),
                            )
                            return
                        except Exception:
                            pass
                    except Exception:
                        pass

    def _handle_callback_error(
        self,
        *,
        event: RealtimeEvent,
        callback: Callable[[RealtimeEvent], None],
    ) -> None:
        error_payload = {
            "failed_event_id": event.event_id,
            "failed_event_type": event.event_type,
            "callback": repr(callback),
            "traceback": traceback.format_exc(limit=5),
        }

        with self._lock:
            self._append_history(
                RealtimeEvent(
                    event_type="EVENT_HANDLER_ERROR",
                    payload=error_payload,
                    tenant_id=event.tenant_id,
                    case_id=event.case_id,
                    actor="event_bus",
                    source="event_bus",
                    severity="ERROR",
                )
            )


# ----------------------------------------------------------------------
# Optional Global Singleton
# ----------------------------------------------------------------------

_GLOBAL_EVENT_BUS: Optional[EventBus] = None


def get_event_bus(
    ledger: Any = None,
) -> EventBus:
    global _GLOBAL_EVENT_BUS

    if _GLOBAL_EVENT_BUS is None:
        _GLOBAL_EVENT_BUS = EventBus(
            ledger=ledger,
        )

    return _GLOBAL_EVENT_BUS


def set_event_bus(
    bus: EventBus,
) -> None:
    global _GLOBAL_EVENT_BUS
    _GLOBAL_EVENT_BUS = bus