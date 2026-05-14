from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

import streamlit as st

from core.realtime.event_broadcaster import get_event_broadcaster
from core.realtime.live_case_updates import get_live_case_updates


def _now_ms() -> int:
    return int(time.time() * 1000)


class LiveSync:
    """
    Streamlit-side realtime synchronization coordinator.

    Handles:
    - channel subscriptions
    - queue refresh flags
    - activity refresh flags
    - SLA refresh flags
    - graph refresh flags
    - analyst notifications
    - escalation banners

    This is polling-compatible now and websocket-ready later.
    """

    PREFIX = "live_sync"

    def __init__(self):
        self.broadcaster = get_event_broadcaster()
        self.live_updates = get_live_case_updates()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    @classmethod
    def initialize(cls, *, user_id: str = "unknown", tenant_id: Optional[str] = None) -> None:
        defaults = {
            cls._k("session_id"): str(uuid.uuid4()),
            cls._k("user_id"): user_id,
            cls._k("tenant_id"): tenant_id,
            cls._k("channels"): [],
            cls._k("notifications"): [],
            cls._k("last_seen_event_ms"): 0,
            cls._k("queue_refresh_required"): False,
            cls._k("activity_refresh_required"): False,
            cls._k("sla_refresh_required"): False,
            cls._k("graph_refresh_required"): False,
            cls._k("escalation_banner"): None,
            cls._k("campaign_banner"): None,
            cls._k("approval_banner"): None,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @classmethod
    def _k(cls, name: str) -> str:
        return f"{cls.PREFIX}_{name}"

    @classmethod
    def get(cls, name: str, default: Any = None) -> Any:
        return st.session_state.get(cls._k(name), default)

    @classmethod
    def set(cls, name: str, value: Any) -> None:
        st.session_state[cls._k(name)] = value

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def subscribe_channel(self, channel: str) -> None:
        session_id = self.get("session_id")
        channels = self.get("channels", [])

        if channel not in channels:
            channels.append(channel)

        self.set("channels", channels)

        self.live_updates.join_channel(
            session_id=session_id,
            channel=channel,
        )

    def subscribe_case(self, case_id: Any) -> None:
        self.subscribe_channel(f"case:{case_id}")

    def subscribe_tenant(self, tenant_id: str) -> None:
        self.subscribe_channel(f"tenant:{tenant_id}")

    def subscribe_analyst(self, user_id: str) -> None:
        self.subscribe_channel(f"analyst:{user_id}")

    def subscribe_severity(self, severity: str) -> None:
        self.subscribe_channel(f"severity:{str(severity).upper()}")

    def subscribe_campaign(self, campaign_id: str) -> None:
        self.subscribe_channel(f"campaign:{campaign_id}")

    # ------------------------------------------------------------------
    # Event Polling Adapter
    # ------------------------------------------------------------------

    def poll_events(self, *, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Streamlit-safe polling adapter.

        Later this can be replaced by true websocket push events.
        """

        channels = self.get("channels", [])
        last_seen = int(self.get("last_seen_event_ms", 0) or 0)

        collected: List[Dict[str, Any]] = []

        for channel in channels:
            events = self.broadcaster.get_channel_history(
                channel=channel,
                limit=limit,
            )

            for event in events:
                ts = int(event.get("timestamp_ms") or 0)

                if ts > last_seen:
                    collected.append(event)

        collected.sort(
            key=lambda e: int(e.get("timestamp_ms") or 0)
        )

        if collected:
            self.set(
                "last_seen_event_ms",
                max(int(e.get("timestamp_ms") or 0) for e in collected),
            )

        for event in collected:
            self._apply_event(event)

        return collected

    # ------------------------------------------------------------------
    # Event Handling
    # ------------------------------------------------------------------

    def _apply_event(self, event: Dict[str, Any]) -> None:
        event_type = str(event.get("event_type") or "").upper()
        severity = str(event.get("severity") or "").upper()

        if event_type in {
            "CASE_CREATED",
            "CASE_ASSIGNED",
            "CASE_ESCALATED",
            "CASE_STATUS_CHANGED",
            "CASE_CLOSED",
            "QUEUE_REFRESH_REQUIRED",
        }:
            self.set("queue_refresh_required", True)

        if event_type in {
            "CASE_ESCALATED",
            "SLA_BREACHED",
            "SLA_WARNING",
            "SLA_REFRESH_REQUIRED",
        }:
            self.set("sla_refresh_required", True)

        if event_type in {
            "GRAPH_UPDATED",
            "GRAPH_REFRESH_REQUIRED",
            "CAMPAIGN_DETECTED",
        }:
            self.set("graph_refresh_required", True)

        if event_type in {
            "CASE_CREATED",
            "CASE_ASSIGNED",
            "CASE_ESCALATED",
            "SLA_BREACHED",
            "APPROVAL_REQUESTED",
            "GRAPH_UPDATED",
            "CAMPAIGN_DETECTED",
            "PLAYBOOK_EXECUTED",
        }:
            self.set("activity_refresh_required", True)
            self.add_notification(event)

        if event_type == "CASE_ESCALATED":
            self.set("escalation_banner", event)

        if event_type == "CAMPAIGN_DETECTED":
            self.set("campaign_banner", event)

        if event_type == "APPROVAL_REQUESTED":
            self.set("approval_banner", event)

        if severity in {"CRITICAL", "HIGH"}:
            self.add_notification(event)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    @classmethod
    def add_notification(cls, event: Dict[str, Any]) -> None:
        notifications = cls.get("notifications", [])

        event_id = event.get("event_id")

        if event_id and any(n.get("event_id") == event_id for n in notifications):
            return

        notifications.insert(0, event)

        cls.set("notifications", notifications[:100])

    @classmethod
    def get_notifications(cls, limit: int = 25) -> List[Dict[str, Any]]:
        return cls.get("notifications", [])[:limit]

    @classmethod
    def clear_notifications(cls) -> None:
        cls.set("notifications", [])

    # ------------------------------------------------------------------
    # Refresh Flags
    # ------------------------------------------------------------------

    @classmethod
    def queue_refresh_required(cls) -> bool:
        return bool(cls.get("queue_refresh_required", False))

    @classmethod
    def activity_refresh_required(cls) -> bool:
        return bool(cls.get("activity_refresh_required", False))

    @classmethod
    def sla_refresh_required(cls) -> bool:
        return bool(cls.get("sla_refresh_required", False))

    @classmethod
    def graph_refresh_required(cls) -> bool:
        return bool(cls.get("graph_refresh_required", False))

    @classmethod
    def clear_refresh_flags(cls) -> None:
        cls.set("queue_refresh_required", False)
        cls.set("activity_refresh_required", False)
        cls.set("sla_refresh_required", False)
        cls.set("graph_refresh_required", False)

    # ------------------------------------------------------------------
    # UI Helpers
    # ------------------------------------------------------------------

    @classmethod
    def render_live_banners(cls) -> None:
        escalation = cls.get("escalation_banner")
        campaign = cls.get("campaign_banner")
        approval = cls.get("approval_banner")

        if escalation:
            st.error(
                f"🚨 Case escalated: {escalation.get('case_id')}"
            )

        if campaign:
            payload = campaign.get("payload") or {}
            st.warning(
                f"🕸️ Campaign detected: {payload.get('campaign_id') or campaign.get('case_id')}"
            )

        if approval:
            payload = approval.get("payload") or {}
            st.info(
                f"📝 Approval requested: {payload.get('approval_type') or approval.get('case_id')}"
            )

    @classmethod
    def render_live_status(cls) -> None:
        channels = cls.get("channels", [])

        st.caption(
            f"Live sync active • {len(channels)} subscribed channels"
        )


def get_live_sync(
    *,
    user_id: str = "unknown",
    tenant_id: Optional[str] = None,
) -> LiveSync:
    LiveSync.initialize(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    sync = LiveSync()

    sync.subscribe_channel("global")

    if tenant_id:
        sync.subscribe_tenant(tenant_id)

    if user_id:
        sync.subscribe_analyst(user_id)

    sync.subscribe_severity("HIGH")
    sync.subscribe_severity("CRITICAL")

    return sync