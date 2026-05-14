from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Set

from core.realtime.event_broadcaster import (
    EventBroadcaster,
    get_event_broadcaster,
)
from core.realtime.event_bus import (
    EventBus,
    RealtimeEvent,
    get_event_bus,
)
from core.realtime.live_case_updates import (
    LiveCaseUpdates,
    get_live_case_updates,
)


logger = logging.getLogger(__name__)


def _now_ms() -> int:
    return int(time.time() * 1000)


class WebSocketConnection:
    """
    Lightweight websocket connection wrapper.

    The underlying websocket object can be:
    - FastAPI WebSocket
    - Starlette WebSocket
    - any object exposing send_text()
    """

    def __init__(
        self,
        *,
        websocket: Any,
        session_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.websocket = websocket
        self.session_id = session_id
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role
        self.metadata = metadata or {}

        self.connected_at_ms = _now_ms()
        self.last_seen_ms = _now_ms()

        self.channels: Set[str] = set()

    async def send_json(
        self,
        payload: Dict[str, Any],
    ) -> None:
        self.last_seen_ms = _now_ms()

        message = json.dumps(
            payload,
            default=str,
            ensure_ascii=False,
        )

        if hasattr(self.websocket, "send_text"):
            result = self.websocket.send_text(message)

            if asyncio.iscoroutine(result):
                await result

            return

        if hasattr(self.websocket, "send_json"):
            result = self.websocket.send_json(payload)

            if asyncio.iscoroutine(result):
                await result

            return

        raise AttributeError(
            "WebSocket object must expose send_text() or send_json()"
        )


class WebSocketManager:
    """
    Realtime websocket transport manager.

    Handles:
    - websocket registration
    - channel subscriptions
    - case/tenant/analyst/campaign channels
    - event fanout
    - presence sync
    - heartbeat/ping
    - stale connection cleanup

    This is transport-layer infrastructure.
    """

    def __init__(
        self,
        *,
        event_bus: Optional[EventBus] = None,
        broadcaster: Optional[EventBroadcaster] = None,
        live_updates: Optional[LiveCaseUpdates] = None,
    ):
        self.event_bus = event_bus or get_event_bus()
        self.broadcaster = broadcaster or get_event_broadcaster(
            event_bus=self.event_bus,
        )
        self.live_updates = live_updates or get_live_case_updates(
            event_bus=self.event_bus,
            broadcaster=self.broadcaster,
        )

        self._connections: Dict[str, WebSocketConnection] = {}
        self._channel_connections: Dict[str, Set[str]] = {}
        self._lock = asyncio.Lock()

        self.broadcaster.subscribe_global(
            self._sync_broadcast_from_broadcaster
        )

    # ------------------------------------------------------------------
    # Connection Lifecycle
    # ------------------------------------------------------------------

    async def connect(
        self,
        *,
        websocket: Any,
        user_id: str,
        tenant_id: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        accept: bool = True,
    ) -> str:
        if accept and hasattr(websocket, "accept"):
            result = websocket.accept()
            if asyncio.iscoroutine(result):
                await result

        session_id = self.live_updates.create_session(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            metadata=metadata or {},
        )

        connection = WebSocketConnection(
            websocket=websocket,
            session_id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            metadata=metadata,
        )

        async with self._lock:
            self._connections[session_id] = connection

        await self.join_channel(
            session_id=session_id,
            channel="global",
        )

        if tenant_id:
            await self.join_channel(
                session_id=session_id,
                channel=f"tenant:{tenant_id}",
            )

        if user_id:
            await self.join_channel(
                session_id=session_id,
                channel=f"analyst:{user_id}",
            )

        await connection.send_json({
            "type": "CONNECTED",
            "session_id": session_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "timestamp_ms": _now_ms(),
        })

        self.event_bus.publish(
            event_type="WEBSOCKET_CONNECTED",
            payload={
                "session_id": session_id,
                "user_id": user_id,
                "role": role,
            },
            tenant_id=tenant_id,
            actor=user_id,
            source="websocket_manager",
        )

        return session_id

    async def disconnect(
        self,
        session_id: str,
    ) -> None:
        async with self._lock:
            connection = self._connections.pop(
                session_id,
                None,
            )

            channels = []

            if connection:
                channels = list(connection.channels)

            for channel in channels:
                self._channel_connections.get(
                    channel,
                    set(),
                ).discard(session_id)

        for channel in channels:
            self.live_updates.leave_channel(
                session_id=session_id,
                channel=channel,
            )

        self.live_updates.close_session(
            session_id,
        )

        if connection:
            self.event_bus.publish(
                event_type="WEBSOCKET_DISCONNECTED",
                payload={
                    "session_id": session_id,
                    "user_id": connection.user_id,
                },
                tenant_id=connection.tenant_id,
                actor=connection.user_id,
                source="websocket_manager",
            )

    # ------------------------------------------------------------------
    # Channel Subscription
    # ------------------------------------------------------------------

    async def join_channel(
        self,
        *,
        session_id: str,
        channel: str,
    ) -> Dict[str, Any]:
        async with self._lock:
            connection = self._connections.get(session_id)

            if not connection:
                return {
                    "status": "error",
                    "message": "session not connected",
                    "session_id": session_id,
                    "channel": channel,
                }

            connection.channels.add(channel)

            self._channel_connections.setdefault(
                channel,
                set(),
            ).add(session_id)

        self.live_updates.join_channel(
            session_id=session_id,
            channel=channel,
        )

        return {
            "status": "joined",
            "session_id": session_id,
            "channel": channel,
            "timestamp_ms": _now_ms(),
        }

    async def leave_channel(
        self,
        *,
        session_id: str,
        channel: str,
    ) -> Dict[str, Any]:
        async with self._lock:
            connection = self._connections.get(session_id)

            if connection:
                connection.channels.discard(channel)

            if channel in self._channel_connections:
                self._channel_connections[channel].discard(session_id)

        self.live_updates.leave_channel(
            session_id=session_id,
            channel=channel,
        )

        return {
            "status": "left",
            "session_id": session_id,
            "channel": channel,
            "timestamp_ms": _now_ms(),
        }

    async def subscribe_case(
        self,
        *,
        session_id: str,
        case_id: Any,
    ) -> Dict[str, Any]:
        return await self.join_channel(
            session_id=session_id,
            channel=f"case:{case_id}",
        )

    async def subscribe_tenant(
        self,
        *,
        session_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        return await self.join_channel(
            session_id=session_id,
            channel=f"tenant:{tenant_id}",
        )

    async def subscribe_analyst(
        self,
        *,
        session_id: str,
        analyst_id: str,
    ) -> Dict[str, Any]:
        return await self.join_channel(
            session_id=session_id,
            channel=f"analyst:{analyst_id}",
        )

    async def subscribe_campaign(
        self,
        *,
        session_id: str,
        campaign_id: str,
    ) -> Dict[str, Any]:
        return await self.join_channel(
            session_id=session_id,
            channel=f"campaign:{campaign_id}",
        )

    async def subscribe_severity(
        self,
        *,
        session_id: str,
        severity: str,
    ) -> Dict[str, Any]:
        return await self.join_channel(
            session_id=session_id,
            channel=f"severity:{str(severity).upper()}",
        )

    # ------------------------------------------------------------------
    # Sending / Broadcasting
    # ------------------------------------------------------------------

    async def send_to_session(
        self,
        *,
        session_id: str,
        message: Dict[str, Any],
    ) -> bool:
        async with self._lock:
            connection = self._connections.get(session_id)

        if not connection:
            return False

        try:
            await connection.send_json(message)
            return True
        except Exception:
            logger.exception(
                "Failed sending websocket message to session %s",
                session_id,
            )
            await self.disconnect(session_id)
            return False

    async def broadcast_to_channel(
        self,
        *,
        channel: str,
        message: Dict[str, Any],
    ) -> Dict[str, Any]:
        async with self._lock:
            session_ids = list(
                self._channel_connections.get(
                    channel,
                    set(),
                )
            )

        sent = 0
        failed = 0

        for session_id in session_ids:
            ok = await self.send_to_session(
                session_id=session_id,
                message={
                    **message,
                    "channel": channel,
                    "timestamp_ms": message.get("timestamp_ms") or _now_ms(),
                },
            )

            if ok:
                sent += 1
            else:
                failed += 1

        return {
            "channel": channel,
            "sent": sent,
            "failed": failed,
            "timestamp_ms": _now_ms(),
        }

    async def broadcast_event(
        self,
        *,
        event: RealtimeEvent,
    ) -> Dict[str, Any]:
        channels = self._derive_channels(event)

        results = []

        for channel in channels:
            results.append(
                await self.broadcast_to_channel(
                    channel=channel,
                    message={
                        "type": "REALTIME_EVENT",
                        "event": event.to_dict(),
                    },
                )
            )

        return {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "channels": channels,
            "results": results,
        }

    # ------------------------------------------------------------------
    # Incoming Client Messages
    # ------------------------------------------------------------------

    async def handle_client_message(
        self,
        *,
        session_id: str,
        message: Dict[str, Any],
    ) -> Dict[str, Any]:
        message_type = str(
            message.get("type") or ""
        ).upper()

        self.live_updates.touch_session(session_id)

        if message_type == "PING":
            return await self._handle_ping(session_id)

        if message_type == "JOIN_CHANNEL":
            return await self.join_channel(
                session_id=session_id,
                channel=message.get("channel"),
            )

        if message_type == "LEAVE_CHANNEL":
            return await self.leave_channel(
                session_id=session_id,
                channel=message.get("channel"),
            )

        if message_type == "SUBSCRIBE_CASE":
            return await self.subscribe_case(
                session_id=session_id,
                case_id=message.get("case_id"),
            )

        if message_type == "SUBSCRIBE_TENANT":
            return await self.subscribe_tenant(
                session_id=session_id,
                tenant_id=message.get("tenant_id"),
            )

        if message_type == "SUBSCRIBE_ANALYST":
            return await self.subscribe_analyst(
                session_id=session_id,
                analyst_id=message.get("analyst_id"),
            )

        if message_type == "SUBSCRIBE_CAMPAIGN":
            return await self.subscribe_campaign(
                session_id=session_id,
                campaign_id=message.get("campaign_id"),
            )

        if message_type == "SUBSCRIBE_SEVERITY":
            return await self.subscribe_severity(
                session_id=session_id,
                severity=message.get("severity"),
            )

        return {
            "status": "ignored",
            "message": "unknown message type",
            "type": message_type,
        }

    async def _handle_ping(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        await self.send_to_session(
            session_id=session_id,
            message={
                "type": "PONG",
                "timestamp_ms": _now_ms(),
            },
        )

        return {
            "status": "ok",
            "type": "PONG",
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Broadcaster Bridge
    # ------------------------------------------------------------------

    def _sync_broadcast_from_broadcaster(
        self,
        event_dict: Dict[str, Any],
    ) -> None:
        """
        Sync callback from EventBroadcaster.

        This callback is intentionally sync because EventBroadcaster is sync.
        It schedules async fanout when an event loop is running.
        """

        try:
            event_type = event_dict.get("event_type")
            payload = event_dict.get("payload") or {}

            event = RealtimeEvent(
                event_type=event_type,
                payload=payload,
                event_id=event_dict.get("event_id") or str(uuid.uuid4()),
                timestamp_ms=event_dict.get("timestamp_ms") or _now_ms(),
                tenant_id=event_dict.get("tenant_id"),
                case_id=event_dict.get("case_id"),
                actor=event_dict.get("actor") or "system",
                source=event_dict.get("source") or "event_broadcaster",
                severity=event_dict.get("severity") or "INFO",
            )

            loop = asyncio.get_event_loop()

            if loop.is_running():
                loop.create_task(
                    self.broadcast_event(event=event)
                )

        except RuntimeError:
            # No active event loop. This is fine in Streamlit/local sync mode.
            return

        except Exception:
            logger.exception(
                "Failed bridging broadcaster event to websocket manager"
            )

    # ------------------------------------------------------------------
    # Diagnostics / Presence
    # ------------------------------------------------------------------

    def get_connection_snapshot(
        self,
    ) -> Dict[str, Any]:
        return asyncio.run(
            self._get_connection_snapshot_async()
        )

    async def _get_connection_snapshot_async(
        self,
    ) -> Dict[str, Any]:
        async with self._lock:
            connections = [
                {
                    "session_id": c.session_id,
                    "user_id": c.user_id,
                    "tenant_id": c.tenant_id,
                    "role": c.role,
                    "channels": sorted(list(c.channels)),
                    "connected_at_ms": c.connected_at_ms,
                    "last_seen_ms": c.last_seen_ms,
                }
                for c in self._connections.values()
            ]

            channel_counts = {
                channel: len(session_ids)
                for channel, session_ids
                in self._channel_connections.items()
            }

        return {
            "active_connections": len(connections),
            "connections": connections,
            "channels": channel_counts,
            "presence": self.live_updates.get_presence_snapshot(),
            "timestamp_ms": _now_ms(),
        }

    async def cleanup_stale_connections(
        self,
        *,
        stale_after_ms: int = 30 * 60 * 1000,
    ) -> Dict[str, Any]:
        now = _now_ms()

        async with self._lock:
            stale = [
                session_id
                for session_id, connection
                in self._connections.items()
                if now - int(connection.last_seen_ms or 0) > stale_after_ms
            ]

        for session_id in stale:
            await self.disconnect(session_id)

        self.live_updates.cleanup_stale_sessions(
            stale_after_ms=stale_after_ms,
        )

        return {
            "removed_connections": stale,
            "count": len(stale),
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _derive_channels(
        self,
        event: RealtimeEvent,
    ) -> List[str]:
        channels = {
            "global",
            f"event:{event.event_type}",
            f"severity:{str(event.severity).upper()}",
        }

        if event.case_id is not None:
            channels.add(f"case:{event.case_id}")

        if event.tenant_id:
            channels.add(f"tenant:{event.tenant_id}")

        if event.actor:
            channels.add(f"analyst:{event.actor}")
            channels.add(f"actor:{event.actor}")

        payload = event.payload or {}

        assigned_analyst = (
            payload.get("assigned_analyst")
            or payload.get("analyst")
        )

        if assigned_analyst:
            channels.add(f"analyst:{assigned_analyst}")

        campaign_id = payload.get("campaign_id")

        if campaign_id:
            channels.add(f"campaign:{campaign_id}")

        target_channel = payload.get("target_channel")

        if target_channel:
            channels.add(str(target_channel))

        extra_channels = payload.get("extra_channels") or []

        for channel in extra_channels:
            channels.add(str(channel))

        return sorted(list(channels))


_GLOBAL_WEBSOCKET_MANAGER: Optional[WebSocketManager] = None


def get_websocket_manager(
    *,
    event_bus: Optional[EventBus] = None,
    broadcaster: Optional[EventBroadcaster] = None,
    live_updates: Optional[LiveCaseUpdates] = None,
) -> WebSocketManager:
    global _GLOBAL_WEBSOCKET_MANAGER

    if _GLOBAL_WEBSOCKET_MANAGER is None:
        _GLOBAL_WEBSOCKET_MANAGER = WebSocketManager(
            event_bus=event_bus,
            broadcaster=broadcaster,
            live_updates=live_updates,
        )

    return _GLOBAL_WEBSOCKET_MANAGER


def set_websocket_manager(
    manager: WebSocketManager,
) -> None:
    global _GLOBAL_WEBSOCKET_MANAGER
    _GLOBAL_WEBSOCKET_MANAGER = manager