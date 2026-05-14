from __future__ import annotations

import json
from typing import Any, Dict, Optional

import streamlit as st


AUTONOMY_LEVELS = [
    "MANUAL_ONLY",
    "APPROVAL_FIRST",
    "SEMI_AUTONOMOUS",
    "AGGRESSIVE_CONTAINMENT",
    "FULL_AUTONOMOUS",
]


DEFAULT_SETTINGS = {
    "autonomy_level": "APPROVAL_FIRST",
    "max_users_disabled": 3,
    "max_devices_isolated": 5,
    "max_mailboxes_quarantined": 3,
    "max_messages_purged": 10,
    "require_legal_review": True,
    "require_export_review": True,
    "require_manager_approval": True,
    "enable_emergency_stop": False,
}


# ----------------------------------------------------------------------
# Persistence Helpers
# ----------------------------------------------------------------------

def _ensure_table(ledger: Any) -> None:
    if ledger is None:
        return

    try:
        with ledger._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_governance_settings (
                    tenant_id TEXT PRIMARY KEY,
                    settings_json TEXT,
                    updated_by TEXT,
                    updated_at_ms INTEGER
                )
                """
            )

            con.commit()

    except Exception:
        pass


def _load_settings(
    ledger: Any,
    tenant_id: str,
) -> Dict[str, Any]:
    if ledger is None:
        return dict(DEFAULT_SETTINGS)

    _ensure_table(ledger)

    try:
        with ledger._connect() as con:
            row = con.execute(
                """
                SELECT settings_json
                FROM ai_governance_settings
                WHERE tenant_id = ?
                LIMIT 1
                """,
                (tenant_id,),
            ).fetchone()

            if not row:
                return dict(DEFAULT_SETTINGS)

            data = dict(row)

            blob = data.get("settings_json")

            if not blob:
                return dict(DEFAULT_SETTINGS)

            settings = json.loads(blob)

            merged = dict(DEFAULT_SETTINGS)
            merged.update(settings)

            return merged

    except Exception:
        return dict(DEFAULT_SETTINGS)


def _save_settings(
    ledger: Any,
    tenant_id: str,
    settings: Dict[str, Any],
    updated_by: str,
) -> None:
    if ledger is None:
        return

    _ensure_table(ledger)

    try:
        import time

        with ledger._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO ai_governance_settings (
                    tenant_id,
                    settings_json,
                    updated_by,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    tenant_id,
                    json.dumps(settings),
                    updated_by,
                    int(time.time() * 1000),
                ),
            )

            con.commit()

    except Exception:
        pass


# ----------------------------------------------------------------------
# Main Render
# ----------------------------------------------------------------------

def render_autonomous_control_panel(storage=None):
    """
    Operational AI governance console.

    Controls:
    - autonomy levels
    - blast-radius limits
    - approval thresholds
    - emergency stop
    - live orchestration visibility
    """

    # -------------------------------------------------------
    # SAFE STORAGE CONTEXT
    # -------------------------------------------------------

    if storage is None:
        st.error("Storage unavailable.")
        return

    ledger = getattr(storage, "ledger", None)
    governance = getattr(storage, "governance", None)

    # OPTIONAL SERVICES
    orchestration_memory = getattr(
        storage,
        "orchestration_memory",
        None,
    )

    execution_audit = getattr(
        storage,
        "execution_audit",
        None,
    )

    safety_guardrails = getattr(
        storage,
        "safety_guardrails",
        None,
    )

    live_updates = getattr(
        storage,
        "live_updates",
        None,
    )

    tenant_id = (
        st.session_state.get("active_tenant_id")
        or st.session_state.get("tenant_id")
        or "default_tenant"
    )

    # -------------------------------------------------------
    # SAFE USER CONTEXT
    # -------------------------------------------------------

    session_user = (
        st.session_state.get("user")
        or st.session_state.get("current_user")
        or {}
    )

    if not isinstance(session_user, dict):
        session_user = {}

    user = session_user

    role = user.get("role", "analyst")

    actor = (
        user.get("email")
        or user.get("username")
        or "unknown"
    )

    # -------------------------------------------------------
    # LOAD SETTINGS
    # -------------------------------------------------------

    settings = _load_settings(
        ledger=ledger,
        tenant_id=tenant_id,
    )

    st.markdown("## 🤖 Autonomous Governance Control")

    tabs = st.tabs(
        [
            "Governance",
            "Blast Radius",
            "Approvals",
            "Realtime Ops",
            "Emergency Controls",
            "Execution Visibility",
        ]
    )

    # ------------------------------------------------------------------
    # Governance
    # ------------------------------------------------------------------

    with tabs[0]:

        st.markdown("### 🧠 AI Autonomy Level")

        current_level = settings.get(
            "autonomy_level",
            "APPROVAL_FIRST",
        )

        if current_level not in AUTONOMY_LEVELS:
            current_level = "APPROVAL_FIRST"

        autonomy_level = st.selectbox(
            "Autonomy Level",
            AUTONOMY_LEVELS,
            index=AUTONOMY_LEVELS.index(current_level),
            key=f"autonomy_level_{tenant_id}",
        )

        st.caption(
            "Controls how aggressively AI may orchestrate containment and operational actions."
        )

        governance_col1, governance_col2 = st.columns(2)

        with governance_col1:

            require_legal_review = st.checkbox(
                "Require Legal Review",
                value=bool(
                    settings.get(
                        "require_legal_review",
                        True,
                    )
                ),
                key=f"legal_review_{tenant_id}",
            )

            require_export_review = st.checkbox(
                "Require Export-Control Review",
                value=bool(
                    settings.get(
                        "require_export_review",
                        True,
                    )
                ),
                key=f"export_review_{tenant_id}",
            )

        with governance_col2:

            require_manager_approval = st.checkbox(
                "Require Manager Approval",
                value=bool(
                    settings.get(
                        "require_manager_approval",
                        True,
                    )
                ),
                key=f"manager_approval_{tenant_id}",
            )

            enable_emergency_stop = st.checkbox(
                "Emergency Stop Active",
                value=bool(
                    settings.get(
                        "enable_emergency_stop",
                        False,
                    )
                ),
                key=f"emergency_stop_checkbox_{tenant_id}",
            )

        settings.update(
            {
                "autonomy_level": autonomy_level,
                "require_legal_review": require_legal_review,
                "require_export_review": require_export_review,
                "require_manager_approval": require_manager_approval,
                "enable_emergency_stop": enable_emergency_stop,
            }
        )

    # ------------------------------------------------------------------
    # Blast Radius
    # ------------------------------------------------------------------

    with tabs[1]:

        st.markdown("### 💥 Blast Radius Limits")

        col1, col2 = st.columns(2)

        with col1:

            max_users_disabled = st.number_input(
                "Max Users Disabled",
                min_value=0,
                max_value=1000,
                value=int(
                    settings.get(
                        "max_users_disabled",
                        3,
                    )
                ),
                key=f"max_users_disabled_{tenant_id}",
            )

            max_devices_isolated = st.number_input(
                "Max Devices Isolated",
                min_value=0,
                max_value=1000,
                value=int(
                    settings.get(
                        "max_devices_isolated",
                        5,
                    )
                ),
                key=f"max_devices_isolated_{tenant_id}",
            )

        with col2:

            max_mailboxes_quarantined = st.number_input(
                "Max Mailboxes Quarantined",
                min_value=0,
                max_value=1000,
                value=int(
                    settings.get(
                        "max_mailboxes_quarantined",
                        3,
                    )
                ),
                key=f"max_mailboxes_quarantined_{tenant_id}",
            )

            max_messages_purged = st.number_input(
                "Max Messages Purged",
                min_value=0,
                max_value=100000,
                value=int(
                    settings.get(
                        "max_messages_purged",
                        10,
                    )
                ),
                key=f"max_messages_purged_{tenant_id}",
            )

        settings.update(
            {
                "max_users_disabled": max_users_disabled,
                "max_devices_isolated": max_devices_isolated,
                "max_mailboxes_quarantined": max_mailboxes_quarantined,
                "max_messages_purged": max_messages_purged,
            }
        )

        st.info(
            "Blast-radius controls prevent runaway or mass autonomous operations."
        )

    # ------------------------------------------------------------------
    # Approvals
    # ------------------------------------------------------------------

    with tabs[2]:

        from ui.copilot.governance_approval_console import (
            render_governance_approval_console,
        )

        render_governance_approval_console(
            storage,
            event_bus=getattr(
                storage,
                "event_bus",
                None,
            ),
        )



    # ------------------------------------------------------------------
    # Realtime Ops
    # ------------------------------------------------------------------

    with tabs[3]:

        st.markdown("### 📡 Live Operational State")

        realtime_col1, realtime_col2 = st.columns(2)

        with realtime_col1:

            st.metric(
                "Autonomy Level",
                settings.get(
                    "autonomy_level",
                    "UNKNOWN",
                ),
            )

            st.metric(
                "Emergency Stop",
                (
                    "ACTIVE"
                    if settings.get(
                        "enable_emergency_stop"
                    )
                    else "OFF"
                ),
            )

        with realtime_col2:

            if orchestration_memory:

                try:
                    profile = orchestration_memory.get_tenant_behavior_profile(
                        tenant_id=tenant_id
                    )

                    st.metric(
                        "Tenant Preference",
                        profile.get(
                            "inferred_preference",
                            "UNKNOWN",
                        ),
                    )

                    st.metric(
                        "Analyst Overrides",
                        profile.get(
                            "analyst_overrides",
                            0,
                        ),
                    )

                except Exception as exc:

                    st.warning(
                        f"Behavior profile unavailable: {exc}"
                    )

        st.markdown("---")

        st.markdown("#### Active Operational Visibility")

        visibility_items = [
            "Active orchestrations",
            "Pending approvals",
            "Rollback chains",
            "Blocked executions",
            "Autonomous actions",
            "Emergency stop status",
            "Realtime escalation routing",
        ]

        for item in visibility_items:
            st.markdown(f"- {item}")

    # ------------------------------------------------------------------
    # Emergency Controls
    # ------------------------------------------------------------------

    with tabs[4]:

        st.markdown("### 🚨 Emergency Controls")

        st.error(
            "Emergency stop disables autonomous orchestration execution."
        )

        emergency_col1, emergency_col2 = st.columns(2)

        with emergency_col1:

            if st.button(
                "🛑 Activate Emergency Stop",
                use_container_width=True,
                key=f"activate_emergency_stop_{tenant_id}",
            ):

                settings["enable_emergency_stop"] = True

                if safety_guardrails:

                    try:
                        safety_guardrails.activate_emergency_stop(
                            tenant_id=tenant_id,
                            actor=actor,
                            reason="Manual governance activation",
                        )

                    except Exception as exc:

                        st.warning(
                            f"Emergency stop activation issue: {exc}"
                        )

                st.success(
                    "Emergency stop activated."
                )

        with emergency_col2:

            if st.button(
                "✅ Clear Emergency Stop",
                use_container_width=True,
                key=f"clear_emergency_stop_{tenant_id}",
            ):

                settings["enable_emergency_stop"] = False

                if safety_guardrails:

                    try:
                        safety_guardrails.clear_emergency_stop(
                            tenant_id=tenant_id,
                            actor=actor,
                            reason="Manual governance clearance",
                        )

                    except Exception as exc:

                        st.warning(
                            f"Emergency stop clearance issue: {exc}"
                        )

                st.success(
                    "Emergency stop cleared."
                )

    # ------------------------------------------------------------------
    # Execution Visibility
    # ------------------------------------------------------------------

    with tabs[5]:

        st.markdown("### 🧾 Execution Visibility")

        if execution_audit:

            try:
                rows = execution_audit.search_executions(
                    tenant_id=tenant_id,
                    limit=25,
                )

                if rows:

                    import pandas as pd

                    df = pd.DataFrame(rows)

                    df = df.fillna("")

                    for col in df.columns:
                        try:
                            df[col] = df[col].astype(str)
                        except Exception:
                            pass

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No execution records available."
                    )

            except Exception as exc:

                st.warning(
                    f"Execution visibility unavailable: {exc}"
                )

        st.markdown("---")

        st.markdown("#### Governance Components")

        components = [
            "PolicyEngine",
            "SafetyGuardrails",
            "ApprovalGate",
            "ExecutionAudit",
            "RollbackManager",
            "OrchestrationMemory",
        ]

        for component in components:
            st.markdown(f"- {component}")

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    st.markdown("---")

    save_col1, save_col2 = st.columns([1, 4])

    with save_col1:

        if st.button(
            "💾 Save Governance Settings",
            use_container_width=True,
            key=f"save_governance_settings_{tenant_id}",
        ):

            _save_settings(
                ledger=ledger,
                tenant_id=tenant_id,
                settings=settings,
                updated_by=actor,
            )

            if live_updates:

                try:
                    live_updates.broadcast_tenant_update(
                        tenant_id=tenant_id,
                        event_type="AI_GOVERNANCE_UPDATED",
                        payload=settings,
                        actor=actor,
                    )

                except Exception:
                    pass

            st.success(
                "Governance settings updated."
            )

    with save_col2:

        st.caption(
            "These controls govern autonomous orchestration behavior, approval enforcement, and operational safety limits."
        )