from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import streamlit as st

from ui.realtime.live_sync import LiveSync, get_live_sync


def _now_ms() -> int:
    return int(time.time() * 1000)


class LiveQueueRefresh:
    """
    UI-side queue refresh coordinator.

    Handles:
    - investigation queue refresh flags
    - SLA widget refresh flags
    - case card refresh flags
    - routing panel refresh flags
    - activity refresh flags

    This is Streamlit-compatible now and prepares the app for
    future partial UI refresh behavior.
    """

    PREFIX = "live_queue_refresh"

    @classmethod
    def initialize(cls) -> None:
        defaults = {
            cls._k("queue_version"): 0,
            cls._k("sla_version"): 0,
            cls._k("routing_version"): 0,
            cls._k("activity_version"): 0,
            cls._k("graph_version"): 0,
            cls._k("case_versions"): {},
            cls._k("last_queue_refresh_ms"): 0,
            cls._k("last_sla_refresh_ms"): 0,
            cls._k("last_routing_refresh_ms"): 0,
            cls._k("last_activity_refresh_ms"): 0,
            cls._k("last_graph_refresh_ms"): 0,
            cls._k("refresh_log"): [],
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
    # Version Bumps
    # ------------------------------------------------------------------

    @classmethod
    def bump_queue(cls, reason: str = "queue_update") -> None:
        cls.initialize()
        cls.set("queue_version", int(cls.get("queue_version", 0)) + 1)
        cls.set("last_queue_refresh_ms", _now_ms())
        cls._log_refresh("queue", reason)

    @classmethod
    def bump_sla(cls, reason: str = "sla_update") -> None:
        cls.initialize()
        cls.set("sla_version", int(cls.get("sla_version", 0)) + 1)
        cls.set("last_sla_refresh_ms", _now_ms())
        cls._log_refresh("sla", reason)

    @classmethod
    def bump_routing(cls, reason: str = "routing_update") -> None:
        cls.initialize()
        cls.set("routing_version", int(cls.get("routing_version", 0)) + 1)
        cls.set("last_routing_refresh_ms", _now_ms())
        cls._log_refresh("routing", reason)

    @classmethod
    def bump_activity(cls, reason: str = "activity_update") -> None:
        cls.initialize()
        cls.set("activity_version", int(cls.get("activity_version", 0)) + 1)
        cls.set("last_activity_refresh_ms", _now_ms())
        cls._log_refresh("activity", reason)

    @classmethod
    def bump_graph(cls, reason: str = "graph_update") -> None:
        cls.initialize()
        cls.set("graph_version", int(cls.get("graph_version", 0)) + 1)
        cls.set("last_graph_refresh_ms", _now_ms())
        cls._log_refresh("graph", reason)

    @classmethod
    def bump_case(cls, case_id: Any, reason: str = "case_update") -> None:
        cls.initialize()

        versions = dict(cls.get("case_versions", {}) or {})
        key = str(case_id)

        versions[key] = int(versions.get(key, 0)) + 1

        cls.set("case_versions", versions)
        cls._log_refresh(f"case:{case_id}", reason)

    # ------------------------------------------------------------------
    # Refresh Checks
    # ------------------------------------------------------------------

    @classmethod
    def get_queue_version(cls) -> int:
        cls.initialize()
        return int(cls.get("queue_version", 0))

    @classmethod
    def get_sla_version(cls) -> int:
        cls.initialize()
        return int(cls.get("sla_version", 0))

    @classmethod
    def get_routing_version(cls) -> int:
        cls.initialize()
        return int(cls.get("routing_version", 0))

    @classmethod
    def get_activity_version(cls) -> int:
        cls.initialize()
        return int(cls.get("activity_version", 0))

    @classmethod
    def get_graph_version(cls) -> int:
        cls.initialize()
        return int(cls.get("graph_version", 0))

    @classmethod
    def get_case_version(cls, case_id: Any) -> int:
        cls.initialize()
        versions = cls.get("case_versions", {}) or {}
        return int(versions.get(str(case_id), 0))

    # ------------------------------------------------------------------
    # Event Application
    # ------------------------------------------------------------------

    @classmethod
    def apply_live_sync_flags(cls) -> Dict[str, Any]:
        """
        Reads LiveSync flags and converts them into refresh versions.

        This is where future partial refresh can attach.
        """

        cls.initialize()

        applied = {
            "queue": False,
            "sla": False,
            "activity": False,
            "graph": False,
        }

        if LiveSync.queue_refresh_required():
            cls.bump_queue("live_sync_queue_required")
            cls.bump_routing("live_sync_queue_required")
            applied["queue"] = True

        if LiveSync.sla_refresh_required():
            cls.bump_sla("live_sync_sla_required")
            applied["sla"] = True

        if LiveSync.activity_refresh_required():
            cls.bump_activity("live_sync_activity_required")
            applied["activity"] = True

        if LiveSync.graph_refresh_required():
            cls.bump_graph("live_sync_graph_required")
            applied["graph"] = True

        LiveSync.clear_refresh_flags()

        return applied

    @classmethod
    def apply_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a single realtime event to refresh domains.
        """

        cls.initialize()

        event_type = str(event.get("event_type") or "").upper()
        case_id = event.get("case_id")
        payload = event.get("payload") or {}

        applied = []

        if event_type in {
            "CASE_CREATED",
            "CASE_ASSIGNED",
            "CASE_ESCALATED",
            "CASE_STATUS_CHANGED",
            "CASE_CLOSED",
            "QUEUE_REFRESH_REQUIRED",
        }:
            cls.bump_queue(event_type)
            cls.bump_routing(event_type)
            applied.extend(["queue", "routing"])

        if case_id is not None:
            cls.bump_case(case_id, event_type)
            applied.append(f"case:{case_id}")

        if event_type in {
            "SLA_BREACHED",
            "SLA_WARNING",
            "SLA_REFRESH_REQUIRED",
        }:
            cls.bump_sla(event_type)
            applied.append("sla")

        if event_type in {
            "GRAPH_UPDATED",
            "GRAPH_REFRESH_REQUIRED",
            "CAMPAIGN_DETECTED",
            "ENTITY_RESOLVED",
        }:
            cls.bump_graph(event_type)
            applied.append("graph")

        if event_type in {
            "CASE_CREATED",
            "CASE_ASSIGNED",
            "CASE_ESCALATED",
            "CASE_STATUS_CHANGED",
            "SLA_BREACHED",
            "APPROVAL_REQUESTED",
            "GRAPH_UPDATED",
            "CAMPAIGN_DETECTED",
            "PLAYBOOK_EXECUTED",
            "ENTITY_RESOLVED",
        }:
            cls.bump_activity(event_type)
            applied.append("activity")

        target_refresh = payload.get("refresh")

        if isinstance(target_refresh, list):
            for target in target_refresh:
                cls._apply_named_refresh(str(target), event_type)
                applied.append(str(target))

        elif isinstance(target_refresh, str):
            cls._apply_named_refresh(target_refresh, event_type)
            applied.append(target_refresh)

        return {
            "event_type": event_type,
            "case_id": case_id,
            "applied": applied,
            "timestamp_ms": _now_ms(),
        }

    @classmethod
    def poll_and_apply(
        cls,
        *,
        user_id: str = "unknown",
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Poll LiveSync events and apply refresh versions.
        """

        sync = get_live_sync(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        events = sync.poll_events(limit=limit)

        applied = []

        for event in events:
            applied.append(cls.apply_event(event))

        flag_result = cls.apply_live_sync_flags()

        return {
            "events_seen": len(events),
            "events_applied": applied,
            "flags_applied": flag_result,
            "versions": cls.snapshot_versions(),
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Render Helpers
    # ------------------------------------------------------------------

    @classmethod
    def render_refresh_status(cls) -> None:
        cls.initialize()

        with st.container(border=True):
            st.markdown("### 🔁 Live Refresh State")

            cols = st.columns(5)

            with cols[0]:
                st.metric("Queue", cls.get_queue_version())

            with cols[1]:
                st.metric("SLA", cls.get_sla_version())

            with cols[2]:
                st.metric("Routing", cls.get_routing_version())

            with cols[3]:
                st.metric("Activity", cls.get_activity_version())

            with cols[4]:
                st.metric("Graph", cls.get_graph_version())

            log = cls.get_refresh_log(limit=10)

            if log:
                with st.expander("Recent Refresh Signals", expanded=False):
                    for item in log:
                        st.caption(
                            f"{item.get('domain')} • {item.get('reason')} • {item.get('timestamp_ms')}"
                        )

    @classmethod
    def render_compact_status(cls) -> None:
        cls.initialize()

        st.caption(
            "Live refresh "
            f"Q:{cls.get_queue_version()} "
            f"SLA:{cls.get_sla_version()} "
            f"R:{cls.get_routing_version()} "
            f"A:{cls.get_activity_version()} "
            f"G:{cls.get_graph_version()}"
        )

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    @classmethod
    def snapshot_versions(cls) -> Dict[str, Any]:
        cls.initialize()

        return {
            "queue_version": cls.get_queue_version(),
            "sla_version": cls.get_sla_version(),
            "routing_version": cls.get_routing_version(),
            "activity_version": cls.get_activity_version(),
            "graph_version": cls.get_graph_version(),
            "case_versions": cls.get("case_versions", {}),
        }

    @classmethod
    def get_refresh_log(cls, limit: int = 25) -> List[Dict[str, Any]]:
        cls.initialize()
        return list(cls.get("refresh_log", []) or [])[:limit]

    @classmethod
    def clear_refresh_log(cls) -> None:
        cls.set("refresh_log", [])

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @classmethod
    def _apply_named_refresh(cls, target: str, reason: str) -> None:
        target = str(target).lower().strip()

        if target == "queue":
            cls.bump_queue(reason)

        elif target == "sla":
            cls.bump_sla(reason)

        elif target == "routing":
            cls.bump_routing(reason)

        elif target == "activity":
            cls.bump_activity(reason)

        elif target == "graph":
            cls.bump_graph(reason)

        elif target.startswith("case:"):
            cls.bump_case(target.split("case:", 1)[1], reason)

    @classmethod
    def _log_refresh(cls, domain: str, reason: str) -> None:
        log = list(cls.get("refresh_log", []) or [])

        log.insert(
            0,
            {
                "domain": domain,
                "reason": reason,
                "timestamp_ms": _now_ms(),
            },
        )

        cls.set("refresh_log", log[:100])


def apply_live_queue_refresh(
    *,
    user_id: str = "unknown",
    tenant_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    return LiveQueueRefresh.poll_and_apply(
        user_id=user_id,
        tenant_id=tenant_id,
        limit=limit,
    )