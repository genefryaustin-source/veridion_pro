import pandas as pd
import streamlit as st


def _query_df(storage, sql, params=None):
    try:
        return pd.read_sql_query(sql, storage.ledger.conn, params=params or {})
    except Exception:
        return pd.DataFrame()


def _table_exists(storage, table_name):
    df = _query_df(
        storage,
        "SELECT name FROM sqlite_master WHERE type='table' AND name=:name",
        {"name": table_name},
    )
    return not df.empty


def _pct(n, d):
    if not d:
        return 0
    return round((n / d) * 100, 1)


def render_policy_insight_panel(storage):
    st.subheader("📐 Adaptive Policy Insights")
    st.caption("Turns operational history into tenant-specific governance recommendations.")

    insights = []

    # ---------------------------------------------------------
    # APPROVAL BEHAVIOR
    # ---------------------------------------------------------
    if _table_exists(storage, "approval_requests"):
        df = _query_df(storage, "SELECT * FROM approval_requests")

        if not df.empty and "status" in df.columns:
            status = df["status"].astype(str).str.upper()
            approved = int(status.isin(["APPROVED", "GRANTED"]).sum())
            rejected = int(status.isin(["REJECTED", "DENIED"]).sum())
            total = len(df)

            insights.append({
                "Signal": "Approval tendency",
                "Finding": f"{_pct(approved, total)}% approved, {_pct(rejected, total)}% rejected",
                "Policy Recommendation": "Use approval history to tune future autonomous action thresholds.",
                "Confidence": "Medium" if total < 10 else "High",
            })

            if rejected > approved:
                insights.append({
                    "Signal": "Manual review preference",
                    "Finding": "Rejected approvals exceed approved approvals.",
                    "Policy Recommendation": "Shift tenant profile toward manual approval for destructive or irreversible actions.",
                    "Confidence": "High",
                })

    # ---------------------------------------------------------
    # ANALYST OVERRIDES
    # ---------------------------------------------------------
    if _table_exists(storage, "analyst_overrides"):
        df = _query_df(storage, "SELECT * FROM analyst_overrides")

        if not df.empty:
            total = len(df)
            isolation_rejects = 0

            if "original_action" in df.columns:
                isolation_rejects = int(
                    df["original_action"]
                    .astype(str)
                    .str.lower()
                    .str.contains("isolation|isolate")
                    .sum()
                )

            insights.append({
                "Signal": "Analyst override behavior",
                "Finding": f"{total} analyst override(s) recorded.",
                "Policy Recommendation": "Feed override patterns into adaptive policy optimizer.",
                "Confidence": "Medium",
            })

            if isolation_rejects:
                insights.append({
                    "Signal": "Endpoint isolation friction",
                    "Finding": f"{isolation_rejects} override(s) involved isolation actions.",
                    "Policy Recommendation": "Require approval before endpoint isolation for this tenant unless severity is critical.",
                    "Confidence": "High",
                })

    # ---------------------------------------------------------
    # ROLLBACK PATTERNS
    # ---------------------------------------------------------
    if _table_exists(storage, "rollback_events"):
        df = _query_df(storage, "SELECT * FROM rollback_events")

        if not df.empty:
            insights.append({
                "Signal": "Rollback frequency",
                "Finding": f"{len(df)} rollback event(s) recorded.",
                "Policy Recommendation": "Increase pre-execution validation and approval requirements for similar future actions.",
                "Confidence": "High",
            })

            if "rollback_action" in df.columns:
                mailbox_rollbacks = int(
                    df["rollback_action"]
                    .astype(str)
                    .str.lower()
                    .str.contains("mailbox|purge|quarantine")
                    .sum()
                )

                if mailbox_rollbacks:
                    insights.append({
                        "Signal": "Mailbox action rollback risk",
                        "Finding": f"{mailbox_rollbacks} mailbox-related rollback event(s).",
                        "Policy Recommendation": "Require legal/compliance approval before mailbox purge or quarantine actions.",
                        "Confidence": "High",
                    })

    # ---------------------------------------------------------
    # CONTAINMENT SUCCESS
    # ---------------------------------------------------------
    if _table_exists(storage, "orchestration_decisions"):
        df = _query_df(storage, "SELECT * FROM orchestration_decisions")

        if not df.empty and "final_action" in df.columns and "outcome" in df.columns:
            containment = df[
                df["final_action"]
                .astype(str)
                .str.lower()
                .str.contains("contain|isolate|quarantine")
            ]

            if not containment.empty:
                outcome = containment["outcome"].astype(str).str.upper()
                success = int(outcome.isin(["SUCCESS", "SUCCEEDED", "COMPLETED"]).sum())

                insights.append({
                    "Signal": "Containment outcome",
                    "Finding": f"{_pct(success, len(containment))}% containment success rate.",
                    "Policy Recommendation": "Use containment success rate to tune autonomous containment aggressiveness.",
                    "Confidence": "Medium" if len(containment) < 10 else "High",
                })

    if not insights:
        st.info("No policy insights yet. This panel will populate after approvals, overrides, decisions, and rollback events exist.")
        return

    df_out = pd.DataFrame(insights)
    st.dataframe(df_out, use_container_width=True, hide_index=True)

    st.markdown("### Recommended Tenant Policy Direction")

    if any("Manual review" in x["Signal"] for x in insights):
        st.warning("Tenant appears to prefer manual approval for sensitive actions.")
    elif any("Containment outcome" in x["Signal"] for x in insights):
        st.success("Tenant may support more aggressive containment when confidence is high.")
    else:
        st.info("Continue collecting governance history before changing automation posture.")