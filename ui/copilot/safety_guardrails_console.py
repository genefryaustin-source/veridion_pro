"""
ui/copilot/safety_guardrails_console.py
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

from core.runtime.safety_guardrails import (
    SafetyGuardrailPolicy,
    get_safety_guardrails,
)


def _fmt_ms(ms: Any) -> str:
    try:
        value = int(ms or 0)
        if value <= 0:
            return ""
        return pd.to_datetime(value, unit="ms").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""


def _badge(value: Any) -> str:
    text = str(value or "UNKNOWN").upper()
    colors = {
        "ALLOW": "#16a34a",
        "BLOCK": "#991b1b",
        "REQUIRE_APPROVAL": "#f59e0b",
        "REQUIRE_EXECUTIVE_APPROVAL": "#7c2d12",
        "LOW": "#2563eb",
        "MEDIUM": "#f59e0b",
        "HIGH": "#dc2626",
        "CRITICAL": "#7f1d1d",
    }
    color = colors.get(text, "#64748b")
    return (
        f"<span style='background:{color};color:white;"
        f"padding:4px 10px;border-radius:999px;"
        f"font-size:12px;font-weight:800;'>{text}</span>"
    )


def _render_header() -> None:
    st.markdown(
        """
        <div style="
            padding:20px 24px;
            border-radius:18px;
            background:linear-gradient(135deg,#111827,#1e293b,#334155);
            color:white;
            margin-bottom:18px;
            box-shadow:0 12px 30px rgba(15,23,42,.25);
        ">
            <div style="font-size:13px;opacity:.8;letter-spacing:.12em;font-weight:800;">
                VERIDION PRO GOVCLOUD
            </div>
            <div style="font-size:30px;font-weight:900;margin-top:6px;">
                🛡️ Safety Guardrails Console
            </div>
            <div style="font-size:15px;opacity:.9;margin-top:8px;">
                Autonomy kill switches, tenant freeze controls, quotas, throttles, recursion limits, and safety decision audit.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _policy_from_form(tenant_id: str, current: SafetyGuardrailPolicy) -> SafetyGuardrailPolicy:
    st.markdown("### Guardrail Policy")

    c1, c2, c3 = st.columns(3)

    with c1:
        global_enabled = st.toggle(
            "Global autonomy enabled",
            value=current.global_autonomy_enabled,
            key=f"safety_global_enabled_{tenant_id}",
        )

    with c2:
        tenant_enabled = st.toggle(
            "Tenant autonomy enabled",
            value=current.tenant_autonomy_enabled,
            key=f"safety_tenant_enabled_{tenant_id}",
        )

    with c3:
        emergency_freeze = st.toggle(
            "Emergency freeze enabled",
            value=current.emergency_freeze_enabled,
            key=f"safety_freeze_enabled_{tenant_id}",
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        max_hour = st.number_input(
            "Max actions / hour",
            min_value=0,
            value=int(current.max_actions_per_hour),
            step=1,
            key=f"safety_max_hour_{tenant_id}",
        )

    with c5:
        max_day = st.number_input(
            "Max actions / day",
            min_value=0,
            value=int(current.max_actions_per_day),
            step=1,
            key=f"safety_max_day_{tenant_id}",
        )

    with c6:
        max_destructive = st.number_input(
            "Max destructive / hour",
            min_value=0,
            value=int(current.max_destructive_actions_per_hour),
            step=1,
            key=f"safety_max_destructive_{tenant_id}",
        )

    c7, c8, c9 = st.columns(3)

    with c7:
        max_rollback_depth = st.number_input(
            "Max rollback depth",
            min_value=0,
            value=int(current.max_rollback_depth),
            step=1,
            key=f"safety_max_rollback_depth_{tenant_id}",
        )

    with c8:
        max_chain_depth = st.number_input(
            "Max execution chain depth",
            min_value=0,
            value=int(current.max_chain_depth),
            step=1,
            key=f"safety_max_chain_depth_{tenant_id}",
        )

    with c9:
        max_targets = st.number_input(
            "Max targets / action",
            min_value=1,
            value=int(current.max_targets_per_action),
            step=1,
            key=f"safety_max_targets_{tenant_id}",
        )

    c10, c11 = st.columns(2)

    with c10:
        storm_window_min = st.number_input(
            "Containment storm window minutes",
            min_value=1,
            value=max(1, int(current.containment_storm_window_ms / 60000)),
            step=1,
            key=f"safety_storm_window_{tenant_id}",
        )

    with c11:
        storm_threshold = st.number_input(
            "Containment storm threshold",
            min_value=1,
            value=int(current.containment_storm_threshold),
            step=1,
            key=f"safety_storm_threshold_{tenant_id}",
        )

    actor = st.text_input(
        "Updated by",
        value="admin",
        key=f"safety_policy_actor_{tenant_id}",
    )

    policy = SafetyGuardrailPolicy(
        tenant_id=tenant_id,
        global_autonomy_enabled=bool(global_enabled),
        tenant_autonomy_enabled=bool(tenant_enabled),
        emergency_freeze_enabled=bool(emergency_freeze),
        max_actions_per_hour=int(max_hour),
        max_actions_per_day=int(max_day),
        max_destructive_actions_per_hour=int(max_destructive),
        max_rollback_depth=int(max_rollback_depth),
        max_chain_depth=int(max_chain_depth),
        max_targets_per_action=int(max_targets),
        cooldown_seconds_by_action=current.cooldown_seconds_by_action,
        containment_storm_window_ms=int(storm_window_min) * 60 * 1000,
        containment_storm_threshold=int(storm_threshold),
        updated_by=actor,
    )

    return policy


def _render_emergency_controls(engine: Any, tenant_id: str) -> None:
    st.markdown("### Emergency Controls")

    reason = st.text_input(
        "Reason",
        value="SOC operator action from Safety Guardrails Console.",
        key=f"safety_emergency_reason_{tenant_id}",
    )

    actor = st.text_input(
        "Actor",
        value="admin",
        key=f"safety_emergency_actor_{tenant_id}",
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("🚨 Enable Emergency Freeze", key=f"safety_enable_freeze_{tenant_id}"):
            engine.enable_emergency_freeze(
                tenant_id=tenant_id,
                actor=actor,
                reason=reason,
            )
            st.success("Emergency freeze enabled.")
            st.rerun()

    with c2:
        if st.button("✅ Disable Emergency Freeze", key=f"safety_disable_freeze_{tenant_id}"):
            engine.disable_emergency_freeze(
                tenant_id=tenant_id,
                actor=actor,
                reason=reason,
            )
            st.success("Emergency freeze disabled.")
            st.rerun()

    with c3:
        if st.button("🛑 Disable Tenant Autonomy", key=f"safety_disable_tenant_autonomy_{tenant_id}"):
            engine.disable_tenant_autonomy(
                tenant_id=tenant_id,
                actor=actor,
                reason=reason,
            )
            st.warning("Tenant autonomy disabled.")
            st.rerun()


def _render_decisions(engine: Any, tenant_id: Optional[str]) -> None:
    st.markdown("### Recent Safety Decisions")

    rows = engine.list_recent_decisions(
        tenant_id=tenant_id if tenant_id and tenant_id != "All" else None,
        limit=500,
    )

    if not rows:
        st.info("No safety decisions recorded yet.")
        return

    df = pd.DataFrame(rows)

    if "created_at_ms" in df.columns:
        df["created_at"] = df["created_at_ms"].apply(_fmt_ms)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Decisions", len(df))
    c2.metric("Blocked", int((df["blocked"].astype(int) == 1).sum()) if "blocked" in df.columns else 0)
    c3.metric(
        "Exec Approval",
        int((df["requires_executive_approval"].astype(int) == 1).sum())
        if "requires_executive_approval" in df.columns
        else 0,
    )
    c4.metric(
        "Critical",
        int((df["risk_level"].astype(str).str.upper() == "CRITICAL").sum())
        if "risk_level" in df.columns
        else 0,
    )

    display_cols = [
        c
        for c in [
            "created_at",
            "tenant_id",
            "action",
            "decision",
            "risk_level",
            "reason",
            "findings_json",
        ]
        if c in df.columns
    ]

    st.dataframe(
        df[display_cols],
        use_container_width=True,
        height=420,
        hide_index=True,
        key="safety_guardrail_decisions_table",
    )

    with st.expander("Raw latest decision"):
        st.json(rows[0])


def _render_test_panel(engine: Any, tenant_id: str) -> None:
    st.markdown("### Test Guardrail Decision")

    c1, c2, c3 = st.columns(3)

    with c1:
        action = st.selectbox(
            "Action",
            [
                "DISABLE_USER",
                "REVOKE_SESSIONS",
                "QUARANTINE_EMAIL",
                "DELETE_EMAIL",
                "ISOLATE_ENDPOINT",
                "DEVICE_WIPE",
            ],
            key=f"safety_test_action_{tenant_id}",
        )

    with c2:
        target_count = st.number_input(
            "Target count",
            min_value=1,
            value=1,
            step=1,
            key=f"safety_test_target_count_{tenant_id}",
        )

    with c3:
        rollback_depth = st.number_input(
            "Rollback depth",
            min_value=0,
            value=0,
            step=1,
            key=f"safety_test_rollback_depth_{tenant_id}",
        )

    actor = st.text_input(
        "Test actor",
        value="safety_console",
        key=f"safety_test_actor_{tenant_id}",
    )

    if st.button("Run Safety Check", key=f"safety_run_test_{tenant_id}"):
        result = engine.check_action(
            tenant_id=tenant_id,
            action=action,
            payload={
                "target_count": int(target_count),
                "rollback_depth": int(rollback_depth),
            },
            actor=actor,
            autonomous=True,
        )

        if result.blocked:
            st.error(result.reason)
        elif result.requires_executive_approval:
            st.warning(result.reason)
        else:
            st.success(result.reason)

        st.json(result.to_dict())


def render_safety_guardrails_console(storage: Any, event_bus: Any = None) -> None:
    _render_header()

    engine = get_safety_guardrails(
        storage,
        event_bus=event_bus,
    )

    tenant_id = st.text_input(
        "Tenant ID",
        value="default",
        key="safety_guardrails_tenant_id",
    ).strip() or "default"

    current = engine.get_policy(tenant_id)

    tab_policy, tab_emergency, tab_decisions, tab_test = st.tabs(
        [
            "Policy",
            "Emergency Controls",
            "Safety Decisions",
            "Test Decision",
        ]
    )

    with tab_policy:
        policy = _policy_from_form(tenant_id, current)

        if st.button("Save Guardrail Policy", key=f"safety_save_policy_{tenant_id}"):
            engine.save_policy(policy)
            st.success("Safety guardrail policy saved.")
            st.rerun()

        st.markdown("#### Current Policy")
        st.json(current.__dict__)

    with tab_emergency:
        _render_emergency_controls(engine, tenant_id)

    with tab_decisions:
        _render_decisions(engine, tenant_id)

    with tab_test:
        _render_test_panel(engine, tenant_id)


render_guardrails_console = render_safety_guardrails_console