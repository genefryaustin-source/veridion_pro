from __future__ import annotations

import queue
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


# ============================================================
# EVENT TYPES
# ============================================================

EXECUTION_STARTED = "EXECUTION_STARTED"
EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
EXECUTION_FAILED = "EXECUTION_FAILED"

APPROVAL_CREATED = "APPROVAL_CREATED"
APPROVAL_GRANTED = "APPROVAL_GRANTED"
APPROVAL_REJECTED = "APPROVAL_REJECTED"

ROLLBACK_TRIGGERED = "ROLLBACK_TRIGGERED"
ROLLBACK_COMPLETED = "ROLLBACK_COMPLETED"
ROLLBACK_FAILED = "ROLLBACK_FAILED"

VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
VERIFICATION_FAILED = "VERIFICATION_FAILED"

ANALYST_OVERRIDE = "ANALYST_OVERRIDE"
CASE_ESCALATED = "CASE_ESCALATED"
EVIDENCE_SEALED = "EVIDENCE_SEALED"
FORENSIC_REPLAY_TRIGGERED = "FORENSIC_REPLAY_TRIGGERED"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Event:
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    actor: str = "system"
    source: str = "event_bus"
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex}")
    created_at_ms: int = field(default_factory=_now_ms)


class EventBus:
    """
    Thread-safe in-process event bus.

    Purpose:
    - decouple execution engine
    - decouple verifier
    - decouple optimizer
    - decouple UI actions
    - decouple governance/replay telemetry

    This is intentionally lightweight for local/Streamlit runtime.
    Later this can be replaced with Redis, SQS, SNS, EventBridge, Kafka, etc.
    """

    def __init__(self, *, max_history: int = 1000):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._wildcard_subscribers: List[Callable[[Event], None]] = []
        self._history: List[Event] = []
        self._queue: "queue.Queue[Event]" = queue.Queue()
        self._lock = threading.RLock()
        self._running = False
        self._worker: Optional[threading.Thread] = None
        self.max_history = max_history

    # ========================================================
    # SUBSCRIBE
    # ========================================================

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Event], None],
    ) -> None:
        with self._lock:
            self._subscribers.setdefault(event_type, []).append(callback)

    def subscribe_all(
        self,
        callback: Callable[[Event], None],
    ) -> None:
        with self._lock:
            self._wildcard_subscribers.append(callback)

    # ========================================================
    # PUBLISH
    # ========================================================

    def publish(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        actor: str = "system",
        source: str = "event_bus",
        async_dispatch: bool = False,
    ) -> Event:
        event = Event(
            event_type=event_type,
            payload=payload or {},
            tenant_id=tenant_id,
            actor=actor,
            source=source,
        )

        self._store_event(event)

        if async_dispatch:
            self._queue.put(event)
        else:
            self._dispatch(event)

        return event

    def emit(self, event: Event, async_dispatch: bool = False) -> Event:
        self._store_event(event)

        if async_dispatch:
            self._queue.put(event)
        else:
            self._dispatch(event)

        return event

    # ========================================================
    # WORKER
    # ========================================================

    def start(self) -> None:
        with self._lock:
            if self._running:
                return

            self._running = True
            self._worker = threading.Thread(
                target=self._run_loop,
                daemon=True,
                name="EventBusWorker",
            )
            self._worker.start()

    def stop(self) -> None:
        with self._lock:
            self._running = False

    def _run_loop(self) -> None:
        while self._running:
            try:
                event = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self._dispatch(event)
            finally:
                self._queue.task_done()

    # ========================================================
    # HISTORY / REPLAY
    # ========================================================

    def history(
        self,
        event_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 250,
    ) -> List[Event]:
        with self._lock:
            events = list(self._history)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]

        return events[-limit:]

    def replay(
        self,
        events: Optional[List[Event]] = None,
        event_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 250,
    ) -> int:
        replay_events = events or self.history(
            event_type=event_type,
            tenant_id=tenant_id,
            limit=limit,
        )

        count = 0

        for event in replay_events:
            self._dispatch(event)
            count += 1

        return count

    # ========================================================
    # INTERNALS
    # ========================================================

    def _store_event(self, event: Event) -> None:
        with self._lock:
            self._history.append(event)

            if len(self._history) > self.max_history:
                self._history = self._history[-self.max_history:]

    def _dispatch(self, event: Event) -> None:
        callbacks: List[Callable[[Event], None]] = []

        with self._lock:
            callbacks.extend(self._subscribers.get(event.event_type, []))
            callbacks.extend(self._wildcard_subscribers)

        for callback in callbacks:
            try:
                callback(event)
            except Exception:
                traceback.print_exc()


# ============================================================
# SINGLETON
# ============================================================

_GLOBAL_EVENT_BUS: Optional[EventBus] = None
_GLOBAL_LOCK = threading.RLock()


def get_event_bus() -> EventBus:
    global _GLOBAL_EVENT_BUS

    with _GLOBAL_LOCK:
        if _GLOBAL_EVENT_BUS is None:
            _GLOBAL_EVENT_BUS = EventBus()
            _GLOBAL_EVENT_BUS.start()

        return _GLOBAL_EVENT_BUS