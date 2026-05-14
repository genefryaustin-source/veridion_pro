"""
core/events/websocket_hub.py

Realtime WebSocket Hub for Veridion Pro / CUI GovCloud App.

Purpose:
- Central realtime event distribution
- Tenant/channel isolation
- SOC live updates
- War Room streaming
- Governance approval updates
- Execution timeline fanout
- Reconnect replay buffer
- Analyst presence tracking

Designed to work safely now as an in-process hub and later expand to:
- FastAPI WebSockets
- Redis Pub/Sub
- AWS API Gateway WebSockets
- EventBridge/SNS/SQS
- NATS/Kafka
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable, Deque, Dict, List, Optional, Set


# =============================================================================
# Constants
# =============================================================================

DEFAULT_TENANT = "default"
GLOBAL_CHANNEL = "global"
WARROOM_GLOBAL = "warroom/global"

DEFAULT_REPLAY_LIMIT = 500
DEFAULT_HEARTBEAT_TIMEOUT_MS = 90_000

EVENT_CLIENT_CONNECTED = "CLIENT_CONNECTED"
EVENT_CLIENT_DISCONNECTED = "CLIENT_DISCONNECTED"
EVENT_CLIENT_HEARTBEAT = "CLIENT_HEARTBEAT"
EVENT_CHANNEL_SUBSCRIBED = "CHANNEL_SUBSCRIBED"
EVENT_CHANNEL_UNSUBSCRIBED = "CHANNEL_UNSUBSCRIBED"

SEVERITY_INFO = "INFO"
SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


# =============================================================================
# Helpers
# =============================================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


def _safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def tenant_channel(tenant_id: Optional[str]) -> str:
    return f"tenant/{tenant_id or DEFAULT_TENANT}"


def case_channel(case_id: Any) -> str:
    return f"case/{case_id}"


def approval_channel(approval_id: str) -> str:
    return f"approval/{approval_id}"


def execution_channel(execution_id: str) -> str:
    return f"execution/{execution_id}"


def normalize_channel(channel: str) -> str:
    return _safe_str(channel, GLOBAL_CHANNEL).strip() or GLOBAL_CHANNEL


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class RealtimeEvent:
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)

    tenant_id: str = DEFAULT_TENANT
    channel: str = GLOBAL_CHANNEL
    source: str = "websocket_hub"
    severity: str = SEVERITY_INFO

    event_id: str = field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:12].upper()}")
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return _safe_json_dumps(self.to_dict())


@dataclass
class ClientSession:
    client_id: str
    tenant_id: str = DEFAULT_TENANT
    user_id: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[str] = None

    connected_at_ms: int = field(default_factory=_now_ms)
    last_heartbeat_ms: int = field(default_factory=_now_ms)

    channels: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "display_name": self.display_name,
            "role": self.role,
            "connected_at_ms": self.connected_at_ms,
            "last_heartbeat_ms": self.last_heartbeat_ms,
            "channels": sorted(self.channels),
            "metadata": self.metadata,
        }


# =============================================================================
# WebSocket Hub
# =============================================================================

class WebSocketHub:
    """
    In-process realtime hub.

    This supports two delivery styles:
    1. WebSocket-like client objects with async send_text()
    2. Callback subscribers for Streamlit/local testing
    """

    def __init__(
        self,
        *,
        replay_limit: int = DEFAULT_REPLAY_LIMIT,
        heartbeat_timeout_ms: int = DEFAULT_HEARTBEAT_TIMEOUT_MS,
        authorize_channel: Optional[Callable[[ClientSession, str], bool]] = None,
    ) -> None:
        self.replay_limit = replay_limit
        self.heartbeat_timeout_ms = heartbeat_timeout_ms
        self.authorize_channel = authorize_channel

        self.clients: Dict[str, ClientSession] = {}
        self.websockets: Dict[str, Any] = {}

        self.channel_clients: Dict[str, Set[str]] = defaultdict(set)
        self.replay_buffers: Dict[str, Deque[RealtimeEvent]] = defaultdict(
            lambda: deque(maxlen=self.replay_limit)
        )

        self.callbacks: Dict[str, List[Callable[[RealtimeEvent], Any]]] = defaultdict(list)

        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Client Lifecycle
    # ------------------------------------------------------------------

    async def connect(
        self,
        websocket: Any = None,
        *,
        client_id: Optional[str] = None,
        tenant_id: str = DEFAULT_TENANT,
        user_id: Optional[str] = None,
        display_name: Optional[str] = None,
        role: Optional[str] = None,
        channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        accept: bool = True,
    ) -> ClientSession:
        client_id = client_id or f"WS-{uuid.uuid4().hex[:12].upper()}"

        if websocket is not None and accept:
            accept_fn = getattr(websocket, "accept", None)
            if callable(accept_fn):
                maybe = accept_fn()
                if asyncio.iscoroutine(maybe):
                    await maybe

        session = ClientSession(
            client_id=client_id,
            tenant_id=tenant_id or DEFAULT_TENANT,
            user_id=user_id,
            display_name=display_name,
            role=role,
            metadata=metadata or {},
        )

        async with self._lock:
            self.clients[client_id] = session

            if websocket is not None:
                self.websockets[client_id] = websocket

        default_channels = [
            GLOBAL_CHANNEL,
            tenant_channel(session.tenant_id),
        ]

        for channel in default_channels + (channels or []):
            await self.subscribe(client_id, channel)

        await self.publish(
            event_type=EVENT_CLIENT_CONNECTED,
            tenant_id=session.tenant_id,
            channel=tenant_channel(session.tenant_id),
            source="websocket_hub",
            severity=SEVERITY_INFO,
            payload={
                "client": session.to_dict(),
            },
        )

        return session

    async def disconnect(self, client_id: str, *, reason: str = "") -> None:
        async with self._lock:
            session = self.clients.pop(client_id, None)
            self.websockets.pop(client_id, None)

            for channel in list(self.channel_clients.keys()):
                self.channel_clients[channel].discard(client_id)

        if session:
            await self.publish(
                event_type=EVENT_CLIENT_DISCONNECTED,
                tenant_id=session.tenant_id,
                channel=tenant_channel(session.tenant_id),
                source="websocket_hub",
                severity=SEVERITY_INFO,
                payload={
                    "client_id": client_id,
                    "reason": reason,
                },
            )

    async def heartbeat(self, client_id: str) -> bool:
        async with self._lock:
            session = self.clients.get(client_id)
            if not session:
                return False

            session.last_heartbeat_ms = _now_ms()

        await self.publish(
            event_type=EVENT_CLIENT_HEARTBEAT,
            tenant_id=session.tenant_id,
            channel=tenant_channel(session.tenant_id),
            source="websocket_hub",
            severity=SEVERITY_INFO,
            payload={
                "client_id": client_id,
                "last_heartbeat_ms": session.last_heartbeat_ms,
            },
            store=False,
        )

        return True

    async def cleanup_stale_clients(self) -> List[str]:
        now = _now_ms()
        stale: List[str] = []

        async with self._lock:
            for client_id, session in list(self.clients.items()):
                if now - session.last_heartbeat_ms > self.heartbeat_timeout_ms:
                    stale.append(client_id)

        for client_id in stale:
            await self.disconnect(client_id, reason="heartbeat_timeout")

        return stale

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    async def subscribe(self, client_id: str, channel: str) -> bool:
        channel = normalize_channel(channel)

        async with self._lock:
            session = self.clients.get(client_id)
            if not session:
                return False

            if self.authorize_channel and not self.authorize_channel(session, channel):
                return False

            session.channels.add(channel)
            self.channel_clients[channel].add(client_id)

        await self.publish(
            event_type=EVENT_CHANNEL_SUBSCRIBED,
            tenant_id=session.tenant_id,
            channel=channel,
            source="websocket_hub",
            severity=SEVERITY_INFO,
            payload={
                "client_id": client_id,
                "channel": channel,
            },
            store=False,
        )

        return True

    async def unsubscribe(self, client_id: str, channel: str) -> bool:
        channel = normalize_channel(channel)

        async with self._lock:
            session = self.clients.get(client_id)
            if not session:
                return False

            session.channels.discard(channel)
            self.channel_clients[channel].discard(client_id)

        await self.publish(
            event_type=EVENT_CHANNEL_UNSUBSCRIBED,
            tenant_id=session.tenant_id,
            channel=channel,
            source="websocket_hub",
            severity=SEVERITY_INFO,
            payload={
                "client_id": client_id,
                "channel": channel,
            },
            store=False,
        )

        return True

    def subscribe_callback(
        self,
        channel: str,
        callback: Callable[[RealtimeEvent], Any],
    ) -> None:
        channel = normalize_channel(channel)
        self.callbacks[channel].append(callback)

    def unsubscribe_callback(
        self,
        channel: str,
        callback: Callable[[RealtimeEvent], Any],
    ) -> None:
        channel = normalize_channel(channel)
        self.callbacks[channel] = [
            cb for cb in self.callbacks[channel] if cb != callback
        ]

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    async def publish(
        self,
        *,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: str = DEFAULT_TENANT,
        channel: Optional[str] = None,
        source: str = "system",
        severity: str = SEVERITY_INFO,
        fanout_tenant: bool = True,
        fanout_global: bool = False,
        store: bool = True,
    ) -> RealtimeEvent:
        channel = normalize_channel(channel or tenant_channel(tenant_id))

        event = RealtimeEvent(
            event_type=event_type,
            payload=payload or {},
            tenant_id=tenant_id or DEFAULT_TENANT,
            channel=channel,
            source=source,
            severity=severity,
        )

        target_channels = {channel}

        if fanout_tenant:
            target_channels.add(tenant_channel(event.tenant_id))

        if fanout_global:
            target_channels.add(GLOBAL_CHANNEL)

        if store:
            for ch in target_channels:
                self.replay_buffers[ch].append(event)

        await self._fanout(event, target_channels)

        return event

    async def publish_sync_safe(self, **kwargs) -> RealtimeEvent:
        return await self.publish(**kwargs)

    def publish_nowait(self, **kwargs) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(**kwargs))
        except RuntimeError:
            asyncio.run(self.publish(**kwargs))

    async def _fanout(self, event: RealtimeEvent, channels: Set[str]) -> None:
        client_ids: Set[str] = set()

        async with self._lock:
            for channel in channels:
                client_ids.update(self.channel_clients.get(channel, set()))

            websocket_targets = {
                client_id: self.websockets.get(client_id)
                for client_id in client_ids
            }

            callback_targets = []
            for channel in channels:
                callback_targets.extend(self.callbacks.get(channel, []))
                callback_targets.extend(self.callbacks.get("*", []))

        message = event.to_json()

        for client_id, websocket in websocket_targets.items():
            if websocket is None:
                continue

            try:
                send_text = getattr(websocket, "send_text", None)
                send_json = getattr(websocket, "send_json", None)

                if callable(send_text):
                    result = send_text(message)
                    if asyncio.iscoroutine(result):
                        await result
                elif callable(send_json):
                    result = send_json(event.to_dict())
                    if asyncio.iscoroutine(result):
                        await result

            except Exception:
                await self.disconnect(client_id, reason="send_failed")

        for callback in callback_targets:
            try:
                result = callback(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                continue

    # ------------------------------------------------------------------
    # Replay / Presence
    # ------------------------------------------------------------------

    def replay(
        self,
        channel: str,
        *,
        limit: int = 100,
        since_ms: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        channel = normalize_channel(channel)
        events = list(self.replay_buffers.get(channel, []))

        if since_ms:
            events = [e for e in events if e.created_at_ms >= since_ms]

        return [
            e.to_dict()
            for e in events[-limit:]
        ]

    def presence(
        self,
        channel: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if channel:
            channel = normalize_channel(channel)
            client_ids = self.channel_clients.get(channel, set())
            return [
                self.clients[cid].to_dict()
                for cid in client_ids
                if cid in self.clients
            ]

        if tenant_id:
            tenant = tenant_id or DEFAULT_TENANT
            return [
                session.to_dict()
                for session in self.clients.values()
                if session.tenant_id == tenant
            ]

        return [
            session.to_dict()
            for session in self.clients.values()
        ]

    def stats(self) -> Dict[str, Any]:
        return {
            "client_count": len(self.clients),
            "channel_count": len(self.channel_clients),
            "channels": {
                channel: len(client_ids)
                for channel, client_ids in self.channel_clients.items()
            },
            "replay_buffers": {
                channel: len(buffer)
                for channel, buffer in self.replay_buffers.items()
            },
        }


# =============================================================================
# Global Hub
# =============================================================================

_DEFAULT_HUB: Optional[WebSocketHub] = None


def get_websocket_hub(reset: bool = False) -> WebSocketHub:
    global _DEFAULT_HUB

    if reset or _DEFAULT_HUB is None:
        _DEFAULT_HUB = WebSocketHub()

    return _DEFAULT_HUB


# =============================================================================
# Sync-Friendly Convenience Functions
# =============================================================================

def broadcast_event(
    *,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: str = DEFAULT_TENANT,
    channel: Optional[str] = None,
    source: str = "system",
    severity: str = SEVERITY_INFO,
    fanout_tenant: bool = True,
    fanout_global: bool = False,
) -> None:
    hub = get_websocket_hub()
    hub.publish_nowait(
        event_type=event_type,
        payload=payload or {},
        tenant_id=tenant_id,
        channel=channel,
        source=source,
        severity=severity,
        fanout_tenant=fanout_tenant,
        fanout_global=fanout_global,
    )


def broadcast_case_event(
    *,
    case_id: Any,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: str = DEFAULT_TENANT,
    source: str = "system",
    severity: str = SEVERITY_INFO,
) -> None:
    broadcast_event(
        event_type=event_type,
        payload={
            "case_id": case_id,
            **(payload or {}),
        },
        tenant_id=tenant_id,
        channel=case_channel(case_id),
        source=source,
        severity=severity,
        fanout_tenant=True,
    )


def broadcast_approval_event(
    *,
    approval_id: str,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: str = DEFAULT_TENANT,
    source: str = "system",
    severity: str = SEVERITY_INFO,
) -> None:
    broadcast_event(
        event_type=event_type,
        payload={
            "approval_id": approval_id,
            **(payload or {}),
        },
        tenant_id=tenant_id,
        channel=approval_channel(approval_id),
        source=source,
        severity=severity,
        fanout_tenant=True,
    )


def broadcast_execution_event(
    *,
    execution_id: str,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: str = DEFAULT_TENANT,
    source: str = "system",
    severity: str = SEVERITY_INFO,
) -> None:
    broadcast_event(
        event_type=event_type,
        payload={
            "execution_id": execution_id,
            **(payload or {}),
        },
        tenant_id=tenant_id,
        channel=execution_channel(execution_id),
        source=source,
        severity=severity,
        fanout_tenant=True,
    )