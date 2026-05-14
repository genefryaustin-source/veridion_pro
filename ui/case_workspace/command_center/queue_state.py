"""
Command Center Queue State

Centralized UI/session state manager for the SOC Command Center.

This prevents investigation_queue.py from becoming a giant
session_state mess and creates a clean operational state layer.

Responsibilities:
- selected cases
- filters
- sorting
- tenant selection
- refresh tracking
- pagination
- activity feed controls
- dashboard preferences
- command center tab state

Future:
- websocket state
- live event stream cursors
- collaborative analyst presence
- persisted user layouts
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import streamlit as st


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

DEFAULT_SORT = "SLA Urgency"

SORT_OPTIONS = [
    "SLA Urgency",
    "Graph Risk",
    "Criticality",
    "Escalation Level",
    "Recent Activity",
    "Cross-Case Links",
    "Evidence Volume",
    "Created Time",
    "Updated Time",
]

DEFAULT_STATUSES = [
    "NEW",
    "TRIAGE",
    "INVESTIGATING",
]

ALL_STATUSES = [
    "NEW",
    "TRIAGE",
    "INVESTIGATING",
    "ESCALATED",
    "CONTAINED",
    "RESOLVED",
    "CLOSED",
    "LEGAL_REVIEW",
    "EXPORT_REVIEW",
    "WAITING_APPROVAL",
    "FALSE_POSITIVE",
]

DEFAULT_PRIORITIES = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
]

ALL_PRIORITIES = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
]

DEFAULT_TABS = [
    "Queue",
    "Escalations",
    "Approvals",
    "SLA",
    "Activity",
    "Analytics",
]

DEFAULT_PAGE_SIZE = 25


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _now_ms() -> int:
    return int(time.time() * 1000)


# ---------------------------------------------------------------------
# Queue State
# ---------------------------------------------------------------------

class QueueState:
    """
    Centralized Command Center UI state manager.

    All Streamlit session state access should go through this layer.
    """

    PREFIX = "cmd_center"

    # -----------------------------------------------------------------
    # Initialization
    # -----------------------------------------------------------------

    @classmethod
    def initialize(cls) -> None:
        """
        Safe idempotent initialization.
        """

        defaults = {
            # ---------------------------------------------------------
            # Selection
            # ---------------------------------------------------------
            cls._k("selected_cases"): [],
            cls._k("selected_case"): None,

            # ---------------------------------------------------------
            # Filters
            # ---------------------------------------------------------
            cls._k("tenant_filter"): "ALL",
            cls._k("status_filters"): DEFAULT_STATUSES,
            cls._k("priority_filters"): DEFAULT_PRIORITIES,
            cls._k("assigned_filters"): [],
            cls._k("tag_filters"): [],
            cls._k("search_query"): "",

            # ---------------------------------------------------------
            # Sorting
            # ---------------------------------------------------------
            cls._k("sort_by"): DEFAULT_SORT,
            cls._k("sort_desc"): True,

            # ---------------------------------------------------------
            # UI
            # ---------------------------------------------------------
            cls._k("active_tab"): DEFAULT_TABS[0],
            cls._k("page_size"): DEFAULT_PAGE_SIZE,
            cls._k("page_number"): 1,

            # ---------------------------------------------------------
            # SLA
            # ---------------------------------------------------------
            cls._k("show_breached_only"): False,
            cls._k("show_near_breach"): True,

            # ---------------------------------------------------------
            # Activity Feed
            # ---------------------------------------------------------
            cls._k("activity_limit"): 50,
            cls._k("activity_auto_refresh"): True,

            # ---------------------------------------------------------
            # Refresh Tracking
            # ---------------------------------------------------------
            cls._k("last_refresh_ms"): _now_ms(),
            cls._k("auto_refresh_enabled"): True,
            cls._k("refresh_interval_sec"): 30,

            # ---------------------------------------------------------
            # Dashboard Controls
            # ---------------------------------------------------------
            cls._k("compact_mode"): False,
            cls._k("show_graph_metrics"): True,
            cls._k("show_ai_insights"): True,
            cls._k("show_activity_feed"): True,
            cls._k("show_sla_metrics"): True,

            # ---------------------------------------------------------
            # Analyst Routing
            # ---------------------------------------------------------
            cls._k("selected_analyst"): None,
            cls._k("routing_mode"): "balanced",

            # ---------------------------------------------------------
            # Escalation
            # ---------------------------------------------------------
            cls._k("escalation_only"): False,

            # ---------------------------------------------------------
            # Multi-Tenant
            # ---------------------------------------------------------
            cls._k("tenant_scope"): "current",

            # ---------------------------------------------------------
            # Future Live Ops
            # ---------------------------------------------------------
            cls._k("websocket_connected"): False,
            cls._k("event_cursor"): None,
            cls._k("live_mode"): False,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # -----------------------------------------------------------------
    # Internal Key Builder
    # -----------------------------------------------------------------

    @classmethod
    def _k(cls, name: str) -> str:
        return f"{cls.PREFIX}_{name}"

    # -----------------------------------------------------------------
    # Generic Get/Set
    # -----------------------------------------------------------------

    @classmethod
    def get(cls, name: str, default: Any = None) -> Any:
        return st.session_state.get(cls._k(name), default)

    @classmethod
    def set(cls, name: str, value: Any) -> None:
        st.session_state[cls._k(name)] = value

    # -----------------------------------------------------------------
    # Selection
    # -----------------------------------------------------------------

    @classmethod
    def get_selected_cases(cls) -> List[Any]:
        return cls.get("selected_cases", [])

    @classmethod
    def set_selected_cases(cls, case_ids: List[Any]) -> None:
        cls.set("selected_cases", case_ids or [])

    @classmethod
    def add_selected_case(cls, case_id: Any) -> None:
        selected = cls.get_selected_cases()

        if case_id not in selected:
            selected.append(case_id)

        cls.set_selected_cases(selected)

    @classmethod
    def remove_selected_case(cls, case_id: Any) -> None:
        selected = cls.get_selected_cases()

        if case_id in selected:
            selected.remove(case_id)

        cls.set_selected_cases(selected)

    @classmethod
    def clear_selected_cases(cls) -> None:
        cls.set_selected_cases([])

    # -----------------------------------------------------------------
    # Filters
    # -----------------------------------------------------------------

    @classmethod
    def get_status_filters(cls) -> List[str]:
        return cls.get("status_filters", DEFAULT_STATUSES)

    @classmethod
    def set_status_filters(cls, statuses: List[str]) -> None:
        cls.set("status_filters", statuses or [])

    @classmethod
    def get_priority_filters(cls) -> List[str]:
        return cls.get("priority_filters", DEFAULT_PRIORITIES)

    @classmethod
    def set_priority_filters(cls, priorities: List[str]) -> None:
        cls.set("priority_filters", priorities or [])

    @classmethod
    def get_tenant_filter(cls) -> str:
        return cls.get("tenant_filter", "ALL")

    @classmethod
    def set_tenant_filter(cls, tenant_id: str) -> None:
        cls.set("tenant_filter", tenant_id)

    @classmethod
    def get_search_query(cls) -> str:
        return cls.get("search_query", "")

    @classmethod
    def set_search_query(cls, query: str) -> None:
        cls.set("search_query", query or "")

    # -----------------------------------------------------------------
    # Sorting
    # -----------------------------------------------------------------

    @classmethod
    def get_sort_by(cls) -> str:
        return cls.get("sort_by", DEFAULT_SORT)

    @classmethod
    def set_sort_by(cls, sort_by: str) -> None:
        if sort_by not in SORT_OPTIONS:
            sort_by = DEFAULT_SORT

        cls.set("sort_by", sort_by)

    @classmethod
    def get_sort_desc(cls) -> bool:
        return cls.get("sort_desc", True)

    @classmethod
    def set_sort_desc(cls, enabled: bool) -> None:
        cls.set("sort_desc", bool(enabled))

    # -----------------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------------

    @classmethod
    def get_active_tab(cls) -> str:
        return cls.get("active_tab", DEFAULT_TABS[0])

    @classmethod
    def set_active_tab(cls, tab_name: str) -> None:
        cls.set("active_tab", tab_name)

    # -----------------------------------------------------------------
    # Pagination
    # -----------------------------------------------------------------

    @classmethod
    def get_page_size(cls) -> int:
        return int(cls.get("page_size", DEFAULT_PAGE_SIZE))

    @classmethod
    def set_page_size(cls, size: int) -> None:
        cls.set("page_size", max(1, int(size)))

    @classmethod
    def get_page_number(cls) -> int:
        return int(cls.get("page_number", 1))

    @classmethod
    def set_page_number(cls, page: int) -> None:
        cls.set("page_number", max(1, int(page)))

    @classmethod
    def next_page(cls) -> None:
        cls.set_page_number(cls.get_page_number() + 1)

    @classmethod
    def prev_page(cls) -> None:
        cls.set_page_number(max(1, cls.get_page_number() - 1))

    # -----------------------------------------------------------------
    # SLA Controls
    # -----------------------------------------------------------------

    @classmethod
    def show_breached_only(cls) -> bool:
        return bool(cls.get("show_breached_only", False))

    @classmethod
    def set_show_breached_only(cls, enabled: bool) -> None:
        cls.set("show_breached_only", bool(enabled))

    @classmethod
    def show_near_breach(cls) -> bool:
        return bool(cls.get("show_near_breach", True))

    @classmethod
    def set_show_near_breach(cls, enabled: bool) -> None:
        cls.set("show_near_breach", bool(enabled))

    # -----------------------------------------------------------------
    # Activity Feed
    # -----------------------------------------------------------------

    @classmethod
    def get_activity_limit(cls) -> int:
        return int(cls.get("activity_limit", 50))

    @classmethod
    def set_activity_limit(cls, value: int) -> None:
        cls.set("activity_limit", max(1, int(value)))

    # -----------------------------------------------------------------
    # Refresh
    # -----------------------------------------------------------------

    @classmethod
    def mark_refreshed(cls) -> None:
        cls.set("last_refresh_ms", _now_ms())

    @classmethod
    def get_last_refresh_ms(cls) -> int:
        return int(cls.get("last_refresh_ms", 0))

    @classmethod
    def should_refresh(cls) -> bool:
        if not cls.get("auto_refresh_enabled", True):
            return False

        last_refresh = cls.get_last_refresh_ms()
        interval_sec = int(cls.get("refresh_interval_sec", 30))

        return (_now_ms() - last_refresh) >= (interval_sec * 1000)

    # -----------------------------------------------------------------
    # Dashboard Toggles
    # -----------------------------------------------------------------

    @classmethod
    def compact_mode(cls) -> bool:
        return bool(cls.get("compact_mode", False))

    @classmethod
    def set_compact_mode(cls, enabled: bool) -> None:
        cls.set("compact_mode", bool(enabled))

    # -----------------------------------------------------------------
    # Operational Helpers
    # -----------------------------------------------------------------

    @classmethod
    def reset_filters(cls) -> None:
        cls.set_status_filters(DEFAULT_STATUSES)
        cls.set_priority_filters(DEFAULT_PRIORITIES)
        cls.set_tenant_filter("ALL")
        cls.set_search_query("")
        cls.set("assigned_filters", [])
        cls.set("tag_filters", [])
        cls.set("escalation_only", False)

    @classmethod
    def clear_all(cls) -> None:
        keys_to_remove = [
            k for k in st.session_state.keys()
            if k.startswith(f"{cls.PREFIX}_")
        ]

        for key in keys_to_remove:
            del st.session_state[key]

        cls.initialize()

    # -----------------------------------------------------------------
    # Snapshot
    # -----------------------------------------------------------------

    @classmethod
    def snapshot(cls) -> Dict[str, Any]:
        """
        Operational snapshot useful for debugging and future persistence.
        """

        return {
            "selected_cases": cls.get_selected_cases(),
            "tenant_filter": cls.get_tenant_filter(),
            "status_filters": cls.get_status_filters(),
            "priority_filters": cls.get_priority_filters(),
            "sort_by": cls.get_sort_by(),
            "sort_desc": cls.get_sort_desc(),
            "active_tab": cls.get_active_tab(),
            "page_number": cls.get_page_number(),
            "page_size": cls.get_page_size(),
            "last_refresh_ms": cls.get_last_refresh_ms(),
            "live_mode": cls.get("live_mode", False),
            "websocket_connected": cls.get("websocket_connected", False),
        }