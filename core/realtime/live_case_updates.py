from __future__ import annotations

import threading
import time
import uuid
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from core.realtime.event_broadcaster import (
    EventBroadcaster,
    get_event_broadcaster,
)
from core.realtime.event_bus import (
    EventBus,
    get_event_bus,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


class LiveCaseUpdates:
    """
    Scoped realtime operational routing layer.

    Handles:
    - channel membership
    - analyst/case/tenant/campaign presence
    - scoped operational broadcasts
    - queue refresh signaling
    - live activity routing

    Channel examples:
        global
        tenant:lockheed
        case:1042
        analyst:eugene
        severity:CRITICAL
        campaign:CAMP-123
    """

    def __init__(
        self,
        *,
        event_bus: Optional[EventBus] = None,
        broadcaster: Optional[EventBroadcaster] = None,
    ):
        self.event_bus = event_bus or get_event_bus()
        self.broadcaster = broadcaster or get_event_broadcaster(
            event_bus=self.event_bus,
        )

        self._lock = threading.RLock()

        # session_id -> session metadata
        self._sessions: Dict[str, Dict[str, Any]] = {}

        # channel -> session ids
        self._channel_members: Dict[str, Set[str]] = defaultdict(set)

        # session_id -> channels
        self._session_channels: Dict[str, Set[str]] = defaultdict(set)

        # user_id / analyst -> session ids
        self._user_sessions: Dict[str, Set[str]] = defaultdict(set)

    # ------------------------------------------------------------------
    # Session / Presence
    # ------------------------------------------------------------------

    def create_session(
        self,
        *,
        user_id: str,
        tenant_id: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        session_id = str(uuid.uuid4())

        with self._lock:
            self._sessions[session_id] = {
                "session_id": session_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role": role,
                "metadata": metadata or {},
                "created_at_ms": _now_ms(),
                "last_seen_ms": _now_ms(),
            }

            self._user_sessions[user_id].add(session_id)

        self.join_channel(
            session_id=session_id,
            channel="global",
        )

        if tenant_id:
            self.join_channel(
                session_id=session_id,
                channel=f"tenant:{tenant_id}",
            )

        if user_id:
            self.join_channel(
                session_id=session_id,
                channel=f"analyst:{user_id}",
            )

        return session_id

    def close_session(
        self,
        session_id: str,
    ) -> None:
        with self._lock:
            channels = list(
                self._session_channels.get(
                    session_id,
                    set(),
                )
            )

        for channel in channels:
            self.leave_channel(
                session_id=session_id,
                channel=channel,
            )

        with self._lock:
            session = self._sessions.pop(
                session_id,
                None,
            )

            if session:
                user_id = session.get("user_id")
                if user_id in self._user_sessions:
                    self._user_sessions[user_id].discard(
                        session_id,
                    )

    def touch_session(
        self,
        session_id: str,
    ) -> None:
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id]["last_seen_ms"] = _now_ms()

    # ------------------------------------------------------------------
    # Channel Management
    # ------------------------------------------------------------------

    def join_channel(
        self,
        *,
        session_id: str,
        channel: str,
    ) -> Dict[str, Any]:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": "unknown",
                    "tenant_id": None,
                    "role": None,
                    "metadata": {},
                    "created_at_ms": _now_ms(),
                    "last_seen_ms": _now_ms(),
                }

            self._channel_members[channel].add(session_id)
            self._session_channels[session_id].add(channel)
            self._sessions[session_id]["last_seen_ms"] = _now_ms()

        return {
            "session_id": session_id,
            "channel": channel,
            "status": "joined",
            "timestamp_ms": _now_ms(),
        }

    def leave_channel(
        self,
        *,
        session_id: str,
        channel: str,
    ) -> Dict[str, Any]:
        with self._lock:
            self._channel_members[channel].discard(session_id)
            self._session_channels[session_id].discard(channel)

            if session_id in self._sessions:
                self._sessions[session_id]["last_seen_ms"] = _now_ms()

        return {
            "session_id": session_id,
            "channel": channel,
            "status": "left",
            "timestamp_ms": _now_ms(),
        }

    def subscribe_session_to_case(
        self,
        *,
        session_id: str,
        case_id: Any,
    ) -> Dict[str, Any]:
        return self.join_channel(
            session_id=session_id,
            channel=f"case:{case_id}",
        )

    def subscribe_session_to_campaign(
        self,
        *,
        session_id: str,
        campaign_id: str,
    ) -> Dict[str, Any]:
        return self.join_channel(
            session_id=session_id,
            channel=f"campaign:{campaign_id}",
        )

    def subscribe_session_to_severity(
        self,
        *,
        session_id: str,
        severity: str,
    ) -> Dict[str, Any]:
        return self.join_channel(
            session_id=session_id,
            channel=f"severity:{str(severity).upper()}",
        )

    # ------------------------------------------------------------------
    # Broadcast APIs
    # ------------------------------------------------------------------

    def broadcast_to_channel(
        self,
        *,
        channel: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        payload = payload or {}

        event = self.event_bus.publish(
            event_type=event_type,
            payload={
                **payload,
                "target_channel": channel,
            },
            actor=actor,
            source="live_case_updates",
            severity=severity,
        )

        self.broadcaster._broadcast_channel(
            channel,
            event.to_dict(),
        )

        return {
            "channel": channel,
            "event_id": event.event_id,
            "event_type": event_type,
            "member_count": len(self.get_channel_members(channel)),
            "timestamp_ms": _now_ms(),
        }

    def broadcast_case_update(
        self,
        *,
        case_id: Any,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        assigned_analyst: Optional[str] = None,
        actor: str = "system",
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        payload = payload or {}

        event = self.event_bus.publish(
            event_type=event_type,
            payload=payload,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            source="live_case_updates",
            severity=severity,
        )

        channels = self.route_case_event(
            case_id=case_id,
            tenant_id=tenant_id,
            assigned_analyst=assigned_analyst,
            severity=severity,
            extra_channels=payload.get("extra_channels") or [],
        )

        event_dict = event.to_dict()

        for channel in channels:
            self.broadcaster._broadcast_channel(
                channel,
                event_dict,
            )

        return {
            "event_id": event.event_id,
            "case_id": case_id,
            "channels": channels,
            "timestamp_ms": _now_ms(),
        }

    def broadcast_tenant_update(
        self,
        *,
        tenant_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        return self.broadcast_to_channel(
            channel=f"tenant:{tenant_id}",
            event_type=event_type,
            payload={
                **(payload or {}),
                "tenant_id": tenant_id,
            },
            actor=actor,
            severity=severity,
        )

    def broadcast_analyst_update(
        self,
        *,
        analyst_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        return self.broadcast_to_channel(
            channel=f"analyst:{analyst_id}",
            event_type=event_type,
            payload={
                **(payload or {}),
                "analyst_id": analyst_id,
            },
            actor=actor,
            severity=severity,
        )

    def broadcast_campaign_update(
        self,
        *,
        campaign_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        return self.broadcast_to_channel(
            channel=f"campaign:{campaign_id}",
            event_type=event_type,
            payload={
                **(payload or {}),
                "campaign_id": campaign_id,
            },
            actor=actor,
            severity=severity,
        )

    # ------------------------------------------------------------------
    # Routing Logic
    # ------------------------------------------------------------------

    def route_case_event(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
        assigned_analyst: Optional[str] = None,
        severity: str = "INFO",
        extra_channels: Optional[List[str]] = None,
    ) -> List[str]:
        channels = {
            "global",
            f"case:{case_id}",
            f"severity:{str(severity).upper()}",
        }

        if tenant_id:
            channels.add(f"tenant:{tenant_id}")

        if assigned_analyst:
            channels.add(f"analyst:{assigned_analyst}")

        for channel in extra_channels or []:
            channels.add(channel)

        return sorted(list(channels))

    def signal_queue_refresh(
        self,
        *,
        tenant_id: Optional[str] = None,
        analyst_id: Optional[str] = None,
        reason: str = "case_update",
        actor: str = "system",
    ) -> Dict[str, Any]:
        channels = ["global"]

        if tenant_id:
            channels.append(f"tenant:{tenant_id}")

        if analyst_id:
            channels.append(f"analyst:{analyst_id}")

        results = []

        for channel in channels:
            results.append(
                self.broadcast_to_channel(
                    channel=channel,
                    event_type="QUEUE_REFRESH_REQUIRED",
                    payload={
                        "reason": reason,
                    },
                    actor=actor,
                    severity="INFO",
                )
            )

        return {
            "signals": results,
            "timestamp_ms": _now_ms(),
        }

    def signal_sla_refresh(
        self,
        *,
        tenant_id: Optional[str] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        return self.broadcast_tenant_update(
            tenant_id=tenant_id or "global",
            event_type="SLA_REFRESH_REQUIRED",
            payload={},
            actor=actor,
        )

    def signal_graph_refresh(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        return self.broadcast_case_update(
            case_id=case_id,
            tenant_id=tenant_id,
            event_type="GRAPH_REFRESH_REQUIRED",
            payload={},
            actor=actor,
        )

    # ------------------------------------------------------------------
    # Presence
    # ------------------------------------------------------------------

    def get_channel_members(
        self,
        channel: str,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            session_ids = list(
                self._channel_members.get(
                    channel,
                    set(),
                )
            )

            members = []

            for session_id in session_ids:
                session = self._sessions.get(session_id)
                if session:
                    members.append(dict(session))

        return members

    def get_session_channels(
        self,
        session_id: str,
    ) -> List[str]:
        with self._lock:
            return sorted(
                list(
                    self._session_channels.get(
                        session_id,
                        set(),
                    )
                )
            )

    def get_case_watchers(
        self,
        case_id: Any,
    ) -> List[Dict[str, Any]]:
        return self.get_channel_members(
            f"case:{case_id}",
        )

    def get_tenant_watchers(
        self,
        tenant_id: str,
    ) -> List[Dict[str, Any]]:
        return self.get_channel_members(
            f"tenant:{tenant_id}",
        )

    def get_analyst_sessions(
        self,
        analyst_id: str,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            session_ids = list(
                self._user_sessions.get(
                    analyst_id,
                    set(),
                )
            )

            return [
                dict(self._sessions[sid])
                for sid in session_ids
                if sid in self._sessions
            ]

    def get_presence_snapshot(
        self,
    ) -> Dict[str, Any]:
        with self._lock:
            channels = {
                channel: len(members)
                for channel, members
                in self._channel_members.items()
            }

            sessions = [
                dict(session)
                for session in self._sessions.values()
            ]

            users = {
                user: len(session_ids)
                for user, session_ids
                in self._user_sessions.items()
            }

        return {
            "active_sessions": len(sessions),
            "active_users": len(users),
            "channels": channels,
            "users": users,
            "sessions": sessions,
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup_stale_sessions(
        self,
        *,
        stale_after_ms: int = 30 * 60 * 1000,
    ) -> Dict[str, Any]:
        now = _now_ms()

        with self._lock:
            stale_sessions = [
                session_id
                for session_id, session
                in self._sessions.items()
                if now - int(session.get("last_seen_ms") or 0) > stale_after_ms
            ]

        for session_id in stale_sessions:
            self.close_session(session_id)

        return {
            "removed_sessions": stale_sessions,
            "count": len(stale_sessions),
            "timestamp_ms": _now_ms(),
        }


_GLOBAL_LIVE_CASE_UPDATES: Optional[LiveCaseUpdates] = None


def get_live_case_updates(
    *,
    event_bus: Optional[EventBus] = None,
    broadcaster: Optional[EventBroadcaster] = None,
) -> LiveCaseUpdates:
    global _GLOBAL_LIVE_CASE_UPDATES

    if _GLOBAL_LIVE_CASE_UPDATES is None:
        _GLOBAL_LIVE_CASE_UPDATES = LiveCaseUpdates(
            event_bus=event_bus,
            broadcaster=broadcaster,
        )

    return _GLOBAL_LIVE_CASE_UPDATES


def set_live_case_updates(
    live_updates: LiveCaseUpdates,
) -> None:
    global _GLOBAL_LIVE_CASE_UPDATES
    _GLOBAL_LIVE_CASE_UPDATES = live_updates