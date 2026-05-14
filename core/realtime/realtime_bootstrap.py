from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, Optional

from core.realtime.event_broadcaster import (
    EventBroadcaster,
    get_event_broadcaster,
    set_event_broadcaster,
)
from core.realtime.event_bus import (
    EventBus,
    get_event_bus,
    set_event_bus,
)
from core.realtime.live_case_updates import (
    LiveCaseUpdates,
    get_live_case_updates,
    set_live_case_updates,
)
from core.realtime.websocket_manager import (
    WebSocketManager,
    get_websocket_manager,
    set_websocket_manager,
)


logger = logging.getLogger(__name__)


def _now_ms() -> int:
    return int(time.time() * 1000)


class RealtimeStack:
    """
    Unified realtime operational stack.

    Wires together:
    - EventBus
    - EventBroadcaster
    - LiveCaseUpdates
    - WebSocketManager

    This becomes the central operational
    coordination infrastructure.

    Future upgrades:
    - Redis
    - Kafka
    - AWS EventBridge
    - API Gateway WebSockets
    - multi-node sync
    """

    def __init__(
        self,
        *,
        ledger: Any = None,
        persist_events: bool = True,
        max_history: int = 1000,
    ):
        self.ledger = ledger

        # --------------------------------------------------------------
        # Core Event Bus
        # --------------------------------------------------------------

        self.event_bus = EventBus(
            ledger=ledger,
            persist_events=persist_events,
            max_history=max_history,
        )

        # --------------------------------------------------------------
        # Broadcaster
        # --------------------------------------------------------------

        self.event_broadcaster = EventBroadcaster(
            event_bus=self.event_bus,
        )

        # --------------------------------------------------------------
        # Presence / Routing
        # --------------------------------------------------------------

        self.live_case_updates = LiveCaseUpdates(
            event_bus=self.event_bus,
            broadcaster=self.event_broadcaster,
        )

        # --------------------------------------------------------------
        # WebSocket Transport
        # --------------------------------------------------------------

        self.websocket_manager = WebSocketManager(
            event_bus=self.event_bus,
            broadcaster=self.event_broadcaster,
            live_updates=self.live_case_updates,
        )

        # --------------------------------------------------------------
        # Diagnostics
        # --------------------------------------------------------------

        self.started_at_ms = _now_ms()

        self._heartbeat_thread = None
        self._running = False

    # ------------------------------------------------------------------
    # Startup / Shutdown
    # ------------------------------------------------------------------

    def start(
        self,
        *,
        enable_heartbeat: bool = True,
        heartbeat_interval_seconds: int = 30,
    ) -> Dict[str, Any]:

        logger.info(
            "Starting realtime operational stack..."
        )

        self._running = True

        # --------------------------------------------------------------
        # Register global singletons
        # --------------------------------------------------------------

        set_event_bus(self.event_bus)

        set_event_broadcaster(
            self.event_broadcaster
        )

        set_live_case_updates(
            self.live_case_updates
        )

        set_websocket_manager(
            self.websocket_manager
        )

        # --------------------------------------------------------------
        # Publish startup event
        # --------------------------------------------------------------

        self.event_bus.publish(
            event_type="REALTIME_STACK_STARTED",
            payload={
                "started_at_ms": self.started_at_ms,
            },
            source="realtime_bootstrap",
        )

        # --------------------------------------------------------------
        # Heartbeat
        # --------------------------------------------------------------

        if enable_heartbeat:
            self._start_heartbeat(
                interval_seconds=heartbeat_interval_seconds
            )

        logger.info(
            "Realtime operational stack started"
        )

        return self.diagnostics()

    def stop(
        self,
    ) -> Dict[str, Any]:

        logger.info(
            "Stopping realtime operational stack..."
        )

        self._running = False

        self.event_bus.publish(
            event_type="REALTIME_STACK_STOPPED",
            payload={
                "stopped_at_ms": _now_ms(),
            },
            source="realtime_bootstrap",
        )

        logger.info(
            "Realtime operational stack stopped"
        )

        return {
            "status": "stopped",
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    def _start_heartbeat(
        self,
        *,
        interval_seconds: int = 30,
    ) -> None:

        if self._heartbeat_thread:
            return

        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            kwargs={
                "interval_seconds": interval_seconds,
            },
            daemon=True,
            name="RealtimeHeartbeat",
        )

        self._heartbeat_thread.start()

    def _heartbeat_loop(
        self,
        *,
        interval_seconds: int = 30,
    ) -> None:

        while self._running:

            try:

                self.event_bus.publish(
                    event_type="REALTIME_HEARTBEAT",
                    payload={
                        "uptime_seconds": int(
                            (_now_ms() - self.started_at_ms)
                            / 1000
                        ),
                    },
                    source="realtime_bootstrap",
                )

                # ------------------------------------------------------
                # Cleanup stale presence
                # ------------------------------------------------------

                self.live_case_updates.cleanup_stale_sessions()

            except Exception:
                logger.exception(
                    "Realtime heartbeat loop failed"
                )

            time.sleep(interval_seconds)

    # ------------------------------------------------------------------
    # Core Accessors
    # ------------------------------------------------------------------

    def get_event_bus(
        self,
    ) -> EventBus:
        return self.event_bus

    def get_event_broadcaster(
        self,
    ) -> EventBroadcaster:
        return self.event_broadcaster

    def get_live_case_updates(
        self,
    ) -> LiveCaseUpdates:
        return self.live_case_updates

    def get_websocket_manager(
        self,
    ) -> WebSocketManager:
        return self.websocket_manager

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        return {

            # ----------------------------------------------------------
            # Runtime
            # ----------------------------------------------------------

            "running": self._running,

            "started_at_ms": self.started_at_ms,

            "uptime_seconds": int(
                (_now_ms() - self.started_at_ms)
                / 1000
            ),

            # ----------------------------------------------------------
            # Event Bus
            # ----------------------------------------------------------

            "event_bus": {
                "history_size": len(
                    self.event_bus.get_history(
                        limit=10000
                    )
                ),
            },

            # ----------------------------------------------------------
            # Broadcaster
            # ----------------------------------------------------------

            "event_broadcaster":
                self.event_broadcaster.diagnostics(),

            # ----------------------------------------------------------
            # Presence
            # ----------------------------------------------------------

            "live_case_updates":
                self.live_case_updates.get_presence_snapshot(),

            # ----------------------------------------------------------
            # WebSockets
            # ----------------------------------------------------------

            "websocket_manager":
                self.websocket_manager.diagnostics(),

            # ----------------------------------------------------------
            # Generated
            # ----------------------------------------------------------

            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_check(
        self,
    ) -> Dict[str, Any]:

        websocket_diag = (
            self.websocket_manager.diagnostics()
        )

        presence = (
            self.live_case_updates
            .get_presence_snapshot()
        )

        return {
            "status": "healthy",

            "connections":
                websocket_diag.get(
                    "total_connections",
                    0,
                ),

            "active_sessions":
                presence.get(
                    "active_sessions",
                    0,
                ),

            "channels":
                len(
                    presence.get(
                        "channels",
                        {}
                    )
                ),

            "uptime_seconds": int(
                (_now_ms() - self.started_at_ms)
                / 1000
            ),

            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Test / Smoke
    # ------------------------------------------------------------------

    def run_smoke_test(
        self,
    ) -> Dict[str, Any]:

        results = []

        try:

            event = self.event_bus.publish(
                event_type="SMOKE_TEST_EVENT",
                payload={
                    "message": "Realtime stack operational",
                },
                source="realtime_bootstrap",
            )

            results.append({
                "component": "event_bus",
                "status": "ok",
                "event_id": event.event_id,
            })

        except Exception as exc:

            results.append({
                "component": "event_bus",
                "status": "failed",
                "error": str(exc),
            })

        try:

            session_id = (
                self.live_case_updates
                .create_session(
                    user_id="smoke_test",
                    tenant_id="test",
                )
            )

            results.append({
                "component": "presence",
                "status": "ok",
                "session_id": session_id,
            })

        except Exception as exc:

            results.append({
                "component": "presence",
                "status": "failed",
                "error": str(exc),
            })

        return {
            "results": results,
            "timestamp_ms": _now_ms(),
        }


# ----------------------------------------------------------------------
# Global Singleton
# ----------------------------------------------------------------------

_GLOBAL_REALTIME_STACK: Optional[
    RealtimeStack
] = None


def bootstrap_realtime(
    *,
    ledger: Any = None,
    persist_events: bool = True,
    max_history: int = 1000,
    start: bool = True,
) -> RealtimeStack:
    """
    Main application bootstrap entrypoint.

    Example:
        realtime = bootstrap_realtime(
            ledger=ledger
        )
    """

    global _GLOBAL_REALTIME_STACK

    if _GLOBAL_REALTIME_STACK is None:

        _GLOBAL_REALTIME_STACK = RealtimeStack(
            ledger=ledger,
            persist_events=persist_events,
            max_history=max_history,
        )

        if start:
            _GLOBAL_REALTIME_STACK.start()

    return _GLOBAL_REALTIME_STACK


def get_realtime_stack(
) -> Optional[RealtimeStack]:
    return _GLOBAL_REALTIME_STACK


def shutdown_realtime(
) -> Dict[str, Any]:

    global _GLOBAL_REALTIME_STACK

    if _GLOBAL_REALTIME_STACK is None:
        return {
            "status": "not_running",
            "timestamp_ms": _now_ms(),
        }

    result = _GLOBAL_REALTIME_STACK.stop()

    _GLOBAL_REALTIME_STACK = None

    return result