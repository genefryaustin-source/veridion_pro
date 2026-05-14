from __future__ import annotations

import time
from collections import Counter
from typing import Any, Dict, List, Optional

import streamlit as st

from ui.realtime.live_sync import LiveSync, get_live_sync
from ui.realtime.live_queue_refresh import LiveQueueRefresh


def _now_ms() -> int:
    return int(time.time() * 1000)


GRAPH_EVENT_TYPES = {
    "GRAPH_UPDATED",
    "GRAPH_REFRESH_REQUIRED",
    "CAMPAIGN_DETECTED",
    "ENTITY_RESOLVED",
    "RELATIONSHIP_UPDATED",
    "BLAST_RADIUS_UPDATED",
}


class LiveGraphUpdates:
    """
    UI-side live graph update coordinator.

    Handles:
    - live entity pivots
    - graph refresh signals
    - campaign propagation
    - relationship updates
    - blast-radius updates
    - graph event history

    Streamlit-compatible now, websocket-ready later.
    """

    PREFIX = "live_graph_updates"

    @classmethod
    def initialize(cls) -> None:
        defaults = {
            cls._k("graph_events"): [],
            cls._k("selected_entity"): None,
            cls._k("selected_campaign"): None,
            cls._k("selected_case_graph"): None,
            cls._k("last_graph_event_ms"): 0,
            cls._k("entity_pivots"): {},
            cls._k("campaign_pivots"): {},
            cls._k("relationship_updates"): [],
            cls._k("blast_radius_updates"): [],
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
    # Poll / Apply
    # ------------------------------------------------------------------

    @classmethod
    def poll_and_apply(
        cls,
        *,
        user_id: str = "unknown",
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        cls.initialize()

        sync = get_live_sync(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        events = sync.poll_events(limit=limit)

        applied = []

        for event in events:
            if str(event.get("event_type") or "").upper() in GRAPH_EVENT_TYPES:
                applied.append(cls.apply_graph_event(event))

        return {
            "events_seen": len(events),
            "graph_events_applied": len(applied),
            "applied": applied,
            "timestamp_ms": _now_ms(),
        }

    @classmethod
    def apply_graph_event(
        cls,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        cls.initialize()

        event_type = str(event.get("event_type") or "").upper()
        payload = event.get("payload") or {}
        case_id = event.get("case_id")

        graph_events = list(cls.get("graph_events", []) or [])
        graph_events.insert(0, event)
        cls.set("graph_events", graph_events[:250])

        cls.set("last_graph_event_ms", int(event.get("timestamp_ms") or _now_ms()))

        if event_type in {"GRAPH_UPDATED", "GRAPH_REFRESH_REQUIRED"}:
            LiveQueueRefresh.bump_graph(event_type)

            if case_id is not None:
                LiveQueueRefresh.bump_case(case_id, event_type)

        if event_type == "CAMPAIGN_DETECTED":
            campaign_id = payload.get("campaign_id")

            if campaign_id:
                cls.set("selected_campaign", campaign_id)

                campaign_pivots = dict(cls.get("campaign_pivots", {}) or {})
                campaign_pivots[campaign_id] = {
                    "campaign_id": campaign_id,
                    "case_id": case_id,
                    "payload": payload,
                    "timestamp_ms": event.get("timestamp_ms"),
                }
                cls.set("campaign_pivots", campaign_pivots)

            LiveQueueRefresh.bump_graph(event_type)
            LiveQueueRefresh.bump_activity(event_type)

        if event_type == "ENTITY_RESOLVED":
            entity = (
                payload.get("entity")
                or payload.get("canonical_name")
                or payload.get("entity_id")
            )

            if entity:
                cls.set("selected_entity", entity)

                pivots = dict(cls.get("entity_pivots", {}) or {})
                pivots[str(entity)] = {
                    "entity": entity,
                    "case_id": case_id,
                    "payload": payload,
                    "timestamp_ms": event.get("timestamp_ms"),
                }
                cls.set("entity_pivots", pivots)

            LiveQueueRefresh.bump_graph(event_type)

        if event_type == "RELATIONSHIP_UPDATED":
            updates = list(cls.get("relationship_updates", []) or [])
            updates.insert(
                0,
                {
                    "case_id": case_id,
                    "payload": payload,
                    "timestamp_ms": event.get("timestamp_ms"),
                },
            )
            cls.set("relationship_updates", updates[:100])
            LiveQueueRefresh.bump_graph(event_type)

        if event_type == "BLAST_RADIUS_UPDATED":
            updates = list(cls.get("blast_radius_updates", []) or [])
            updates.insert(
                0,
                {
                    "case_id": case_id,
                    "payload": payload,
                    "timestamp_ms": event.get("timestamp_ms"),
                },
            )
            cls.set("blast_radius_updates", updates[:100])
            LiveQueueRefresh.bump_graph(event_type)

        return {
            "event_type": event_type,
            "case_id": case_id,
            "applied": True,
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    @classmethod
    def get_graph_events(cls, limit: int = 50) -> List[Dict[str, Any]]:
        cls.initialize()
        return list(cls.get("graph_events", []) or [])[:limit]

    @classmethod
    def get_entity_pivots(cls) -> Dict[str, Any]:
        cls.initialize()
        return dict(cls.get("entity_pivots", {}) or {})

    @classmethod
    def get_campaign_pivots(cls) -> Dict[str, Any]:
        cls.initialize()
        return dict(cls.get("campaign_pivots", {}) or {})

    @classmethod
    def get_relationship_updates(cls, limit: int = 25) -> List[Dict[str, Any]]:
        cls.initialize()
        return list(cls.get("relationship_updates", []) or [])[:limit]

    @classmethod
    def get_blast_radius_updates(cls, limit: int = 25) -> List[Dict[str, Any]]:
        cls.initialize()
        return list(cls.get("blast_radius_updates", []) or [])[:limit]

    # ------------------------------------------------------------------
    # Renderers
    # ------------------------------------------------------------------

    @classmethod
    def render_live_graph_panel(
        cls,
        *,
        user_id: str = "unknown",
        tenant_id: Optional[str] = None,
        auto_poll: bool = True,
    ) -> None:
        cls.initialize()

        if auto_poll:
            cls.poll_and_apply(
                user_id=user_id,
                tenant_id=tenant_id,
            )

        with st.container(border=True):
            st.markdown("### 🕸️ Live Graph Intelligence")

            cls.render_graph_metrics()

            st.divider()

            tab_events, tab_entities, tab_campaigns, tab_relationships, tab_blast = st.tabs(
                [
                    "Graph Events",
                    "Entity Pivots",
                    "Campaigns",
                    "Relationships",
                    "Blast Radius",
                ]
            )

            with tab_events:
                cls.render_graph_events()

            with tab_entities:
                cls.render_entity_pivots()

            with tab_campaigns:
                cls.render_campaign_pivots()

            with tab_relationships:
                cls.render_relationship_updates()

            with tab_blast:
                cls.render_blast_radius_updates()

    @classmethod
    def render_graph_metrics(cls) -> None:
        events = cls.get_graph_events(limit=250)

        counter = Counter(
            str(e.get("event_type") or "UNKNOWN").upper()
            for e in events
        )

        cols = st.columns(5)

        with cols[0]:
            st.metric("Graph Events", len(events))

        with cols[1]:
            st.metric("Campaigns", counter.get("CAMPAIGN_DETECTED", 0))

        with cols[2]:
            st.metric("Entities", counter.get("ENTITY_RESOLVED", 0))

        with cols[3]:
            st.metric("Relations", counter.get("RELATIONSHIP_UPDATED", 0))

        with cols[4]:
            st.metric("Blast Radius", counter.get("BLAST_RADIUS_UPDATED", 0))

    @classmethod
    def render_graph_events(cls) -> None:
        events = cls.get_graph_events(limit=50)

        if not events:
            st.info("No live graph events.")
            return

        for event in events:
            payload = event.get("payload") or {}
            event_type = event.get("event_type")
            case_id = event.get("case_id")

            with st.container(border=True):
                st.markdown(f"**{event_type}**")
                st.caption(
                    f"Case: {case_id} • Source: {event.get('source')} • {event.get('timestamp_ms')}"
                )

                summary = (
                    payload.get("summary")
                    or payload.get("message")
                    or payload.get("campaign_id")
                    or payload.get("entity")
                    or payload.get("canonical_name")
                )

                if summary:
                    st.info(str(summary))

                with st.expander("Payload", expanded=False):
                    st.json(payload)

    @classmethod
    def render_entity_pivots(cls) -> None:
        pivots = cls.get_entity_pivots()

        if not pivots:
            st.info("No entity pivots yet.")
            return

        for entity, data in pivots.items():
            with st.container(border=True):
                st.markdown(f"#### 🧠 {entity}")
                st.caption(f"Case: {data.get('case_id')} • {data.get('timestamp_ms')}")

                payload = data.get("payload") or {}

                entity_id = payload.get("entity_id")
                aliases = payload.get("aliases") or []
                metadata = payload.get("metadata") or {}

                if entity_id:
                    st.caption(f"Entity ID: `{entity_id}`")

                if metadata:
                    cols = st.columns(3)

                    with cols[0]:
                        st.metric("Type", metadata.get("entity_type", "UNKNOWN"))

                    with cols[1]:
                        st.metric("Risk", metadata.get("risk_level", "UNKNOWN"))

                    with cols[2]:
                        st.metric("Country", metadata.get("country", "UNKNOWN"))

                if aliases:
                    st.markdown("**Aliases**")
                    st.write(", ".join(map(str, aliases)))

                with st.expander("Entity Payload", expanded=False):
                    st.json(payload)

    @classmethod
    def render_campaign_pivots(cls) -> None:
        campaigns = cls.get_campaign_pivots()

        if not campaigns:
            st.info("No live campaign pivots yet.")
            return

        for campaign_id, data in campaigns.items():
            payload = data.get("payload") or {}

            with st.container(border=True):
                st.markdown(f"#### 🎯 {campaign_id}")
                st.caption(f"Case: {data.get('case_id')} • {data.get('timestamp_ms')}")

                cols = st.columns(4)

                with cols[0]:
                    st.metric("Confidence", payload.get("confidence", "N/A"))

                with cols[1]:
                    st.metric("Type", payload.get("campaign_type", "UNKNOWN"))

                with cols[2]:
                    st.metric("Linked Cases", payload.get("linked_case_count", "N/A"))

                with cols[3]:
                    st.metric("Severity", payload.get("recommended_severity", "UNKNOWN"))

                with st.expander("Campaign Payload", expanded=False):
                    st.json(payload)

    @classmethod
    def render_relationship_updates(cls) -> None:
        updates = cls.get_relationship_updates(limit=50)

        if not updates:
            st.info("No relationship updates.")
            return

        for update in updates:
            payload = update.get("payload") or {}

            with st.container(border=True):
                st.markdown("#### 🔗 Relationship Updated")
                st.caption(f"Case: {update.get('case_id')} • {update.get('timestamp_ms')}")

                source = payload.get("source")
                target = payload.get("target")
                relationship = payload.get("relationship")

                if source or target:
                    st.markdown(f"`{source}` → **{relationship or 'RELATED_TO'}** → `{target}`")

                with st.expander("Relationship Payload", expanded=False):
                    st.json(payload)

    @classmethod
    def render_blast_radius_updates(cls) -> None:
        updates = cls.get_blast_radius_updates(limit=50)

        if not updates:
            st.info("No blast-radius updates.")
            return

        for update in updates:
            payload = update.get("payload") or {}

            with st.container(border=True):
                st.markdown("#### 💥 Blast Radius Updated")
                st.caption(f"Case: {update.get('case_id')} • {update.get('timestamp_ms')}")

                cols = st.columns(4)

                with cols[0]:
                    st.metric("Score", payload.get("blast_radius_score", "N/A"))

                with cols[1]:
                    st.metric("Entities", payload.get("entity_count", "N/A"))

                with cols[2]:
                    st.metric("Cases", payload.get("linked_case_count", "N/A"))

                with cols[3]:
                    st.metric("Evidence", payload.get("evidence_count", "N/A"))

                with st.expander("Blast Radius Payload", expanded=False):
                    st.json(payload)


def render_live_graph_updates(
    *,
    user_id: str = "unknown",
    tenant_id: Optional[str] = None,
    auto_poll: bool = True,
) -> None:
    LiveGraphUpdates.render_live_graph_panel(
        user_id=user_id,
        tenant_id=tenant_id,
        auto_poll=auto_poll,
    )