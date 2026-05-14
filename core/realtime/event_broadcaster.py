from __future__ import annotations

import json
import logging
import threading
import time
from collections import defaultdict, deque
from typing import Any, Callable, Deque, Dict, List, Optional

from core.realtime.event_bus import (
    EventBus,
    RealtimeEvent,
    get_event_bus,
)


logger = logging.getLogger(__name__)


def _now_ms() -> int:
    return int(time.time() * 1000)


class EventBroadcaster:
    """
    Realtime operational event broadcaster.

    Consumes EventBus events and fans them out to:
    - websocket clients
    - dashboards
    - activity feeds
    - analyst listeners
    - notifications
    - external integrations

    This becomes:
    operational coordination infrastructure.
    """

    def __init__(
        self,
        *,
        event_bus: Optional[EventBus] = None,
        max_channel_history: int = 500,
    ):
        self.event_bus = event_bus or get_event_bus()

        self.max_channel_history = max_channel_history

        # --------------------------------------------------------------
        # Subscribers
        # --------------------------------------------------------------

        self._global_subscribers: List[Callable] = []

        self._channel_subscribers: Dict[
            str,
            List[Callable]
        ] = defaultdict(list)

        # --------------------------------------------------------------
        # Event History
        # --------------------------------------------------------------

        self._channel_history: Dict[
            str,
            Deque[Dict[str, Any]]
        ] = defaultdict(
            lambda: deque(maxlen=max_channel_history)
        )

        # --------------------------------------------------------------
        # Locks
        # --------------------------------------------------------------

        self._lock = threading.RLock()

        # --------------------------------------------------------------
        # Subscribe to ALL events
        # --------------------------------------------------------------

        self.event_bus.subscribe(
            "*",
            self._on_event,
        )

    # ------------------------------------------------------------------
    # Core Event Consumption
    # ------------------------------------------------------------------

    def _on_event(
        self,
        event: RealtimeEvent,
    ) -> None:
        try:

            event_dict = event.to_dict()

            channels = self._derive_channels(event)

            # ----------------------------------------------------------
            # Persist per-channel history
            # ----------------------------------------------------------

            with self._lock:

                for channel in channels:
                    self._channel_history[channel].append(
                        event_dict
                    )

            # ----------------------------------------------------------
            # Broadcast
            # ----------------------------------------------------------

            self._broadcast_global(event_dict)

            for channel in channels:
                self._broadcast_channel(
                    channel,
                    event_dict,
                )

        except Exception:
            logger.exception(
                "EventBroadcaster failed handling event"
            )

    # ------------------------------------------------------------------
    # Channel Derivation
    # ------------------------------------------------------------------

    def _derive_channels(
        self,
        event: RealtimeEvent,
    ) -> List[str]:

        channels = set()

        # --------------------------------------------------------------
        # Global
        # --------------------------------------------------------------

        channels.add("global")

        # --------------------------------------------------------------
        # Event Type
        # --------------------------------------------------------------

        channels.add(
            f"event:{event.event_type}"
        )

        # --------------------------------------------------------------
        # Case
        # --------------------------------------------------------------

        if event.case_id is not None:
            channels.add(
                f"case:{event.case_id}"
            )

        # --------------------------------------------------------------
        # Tenant
        # --------------------------------------------------------------

        if event.tenant_id:
            channels.add(
                f"tenant:{event.tenant_id}"
            )

        # --------------------------------------------------------------
        # Actor
        # --------------------------------------------------------------

        if event.actor:
            channels.add(
                f"actor:{event.actor}"
            )

        # --------------------------------------------------------------
        # Severity
        # --------------------------------------------------------------

        if event.severity:
            channels.add(
                f"severity:{event.severity.upper()}"
            )

        return sorted(list(channels))

    # ------------------------------------------------------------------
    # Subscription APIs
    # ------------------------------------------------------------------

    def subscribe_global(
        self,
        callback: Callable[[Dict[str, Any]], None],
    ) -> None:

        with self._lock:
            self._global_subscribers.append(
                callback
            )

    def unsubscribe_global(
        self,
        callback: Callable[[Dict[str, Any]], None],
    ) -> None:

        with self._lock:

            if callback in self._global_subscribers:
                self._global_subscribers.remove(
                    callback
                )

    def subscribe_channel(
        self,
        channel: str,
        callback: Callable[[Dict[str, Any]], None],
    ) -> None:

        with self._lock:
            self._channel_subscribers[
                channel
            ].append(callback)

    def unsubscribe_channel(
        self,
        channel: str,
        callback: Callable[[Dict[str, Any]], None],
    ) -> None:

        with self._lock:

            callbacks = self._channel_subscribers.get(
                channel,
                []
            )

            if callback in callbacks:
                callbacks.remove(callback)

    # ------------------------------------------------------------------
    # Broadcast
    # ------------------------------------------------------------------

    def _broadcast_global(
        self,
        event: Dict[str, Any],
    ) -> None:

        with self._lock:
            subscribers = list(
                self._global_subscribers
            )

        for callback in subscribers:

            try:
                callback(event)

            except Exception:
                logger.exception(
                    "Global broadcast callback failed"
                )

    def _broadcast_channel(
        self,
        channel: str,
        event: Dict[str, Any],
    ) -> None:

        with self._lock:
            subscribers = list(
                self._channel_subscribers.get(
                    channel,
                    []
                )
            )

        for callback in subscribers:

            try:
                callback(event)

            except Exception:
                logger.exception(
                    "Channel broadcast callback failed"
                )

    # ------------------------------------------------------------------
    # History / Replay
    # ------------------------------------------------------------------

    def get_channel_history(
        self,
        channel: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:

        with self._lock:

            history = list(
                self._channel_history.get(
                    channel,
                    []
                )
            )

        return history[-limit:]

    def replay_channel(
        self,
        *,
        channel: str,
        callback: Callable[[Dict[str, Any]], None],
        limit: int = 100,
    ) -> None:

        history = self.get_channel_history(
            channel=channel,
            limit=limit,
        )

        for event in history:

            try:
                callback(event)

            except Exception:
                logger.exception(
                    "Replay callback failed"
                )

    # ------------------------------------------------------------------
    # Activity Feed Support
    # ------------------------------------------------------------------

    def get_recent_activity(
        self,
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:

        channel = "global"

        if case_id is not None:
            channel = f"case:{case_id}"

        elif tenant_id:
            channel = f"tenant:{tenant_id}"

        events = self.get_channel_history(
            channel=channel,
            limit=limit,
        )

        return sorted(
            events,
            key=lambda e: e.get("timestamp_ms", 0),
            reverse=True,
        )

    # ------------------------------------------------------------------
    # Dashboard Feed
    # ------------------------------------------------------------------

    def build_dashboard_feed(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:

        events = self.get_recent_activity(
            tenant_id=tenant_id,
            limit=limit,
        )

        feed = []

        for event in events:

            feed.append({
                "event_type": event.get("event_type"),
                "severity": event.get("severity"),
                "timestamp_ms": event.get("timestamp_ms"),
                "case_id": event.get("case_id"),
                "actor": event.get("actor"),
                "source": event.get("source"),
                "summary": self._summarize_event(event),
                "payload": event.get("payload", {}),
            })

        return feed

    # ------------------------------------------------------------------
    # Notification Fanout
    # ------------------------------------------------------------------

    def should_notify(
        self,
        event: Dict[str, Any],
    ) -> bool:

        severity = str(
            event.get("severity", "")
        ).upper()

        if severity in [
            "CRITICAL",
            "HIGH",
        ]:
            return True

        important_events = {
            "CASE_ESCALATED",
            "SLA_BREACHED",
            "CAMPAIGN_DETECTED",
            "APPROVAL_REQUESTED",
        }

        return (
            event.get("event_type")
            in important_events
        )

    # ------------------------------------------------------------------
    # Event Summaries
    # ------------------------------------------------------------------

    def _summarize_event(
        self,
        event: Dict[str, Any],
    ) -> str:

        event_type = event.get(
            "event_type",
            "UNKNOWN"
        )

        payload = event.get(
            "payload",
            {}
        )

        case_id = event.get("case_id")

        summaries = {

            "CASE_CREATED":
                f"Case {case_id} created",

            "CASE_ASSIGNED":
                (
                    f"Case {case_id} assigned to "
                    f"{payload.get('analyst')}"
                ),

            "CASE_ESCALATED":
                (
                    f"Case {case_id} escalated "
                    f"({payload.get('reason')})"
                ),

            "SLA_BREACHED":
                f"SLA breached for case {case_id}",

            "APPROVAL_REQUESTED":
                (
                    f"Approval requested for "
                    f"case {case_id}"
                ),

            "GRAPH_UPDATED":
                (
                    f"Graph updated for "
                    f"case {case_id}"
                ),

            "CAMPAIGN_DETECTED":
                (
                    f"Campaign detected for "
                    f"case {case_id}"
                ),

            "PLAYBOOK_EXECUTED":
                (
                    f"Playbook executed for "
                    f"case {case_id}"
                ),
        }

        return summaries.get(
            event_type,
            f"{event_type} occurred",
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        with self._lock:

            channel_counts = {
                channel: len(events)
                for channel, events
                in self._channel_history.items()
            }

            subscriber_counts = {
                channel: len(callbacks)
                for channel, callbacks
                in self._channel_subscribers.items()
            }

        return {
            "global_subscribers":
                len(self._global_subscribers),

            "channels":
                len(channel_counts),

            "channel_history_counts":
                channel_counts,

            "channel_subscribers":
                subscriber_counts,

            "generated_at_ms":
                _now_ms(),
        }


# ----------------------------------------------------------------------
# Optional Global Singleton
# ----------------------------------------------------------------------

_GLOBAL_EVENT_BROADCASTER: Optional[
    EventBroadcaster
] = None


def get_event_broadcaster(
    *,
    event_bus: Optional[EventBus] = None,
) -> EventBroadcaster:

    global _GLOBAL_EVENT_BROADCASTER

    if _GLOBAL_EVENT_BROADCASTER is None:

        _GLOBAL_EVENT_BROADCASTER = (
            EventBroadcaster(
                event_bus=event_bus,
            )
        )

    return _GLOBAL_EVENT_BROADCASTER


def set_event_broadcaster(
    broadcaster: EventBroadcaster,
) -> None:

    global _GLOBAL_EVENT_BROADCASTER

    _GLOBAL_EVENT_BROADCASTER = broadcaster