# core/ui/scan_page.py

import io
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from core.alerts.notifier import notify


# ============================================================
# SAFE NORMALIZATION HELPERS
# ============================================================

def normalize_severity(val: Any) -> str:
    if not val:
        return "LOW"

    val = str(val).upper().strip()
    val = (
        val.replace("🔴", "")
        .replace("🟠", "")
        .replace("🟡", "")
        .replace("🟢", "")
        .strip()
    )

    if val in {"CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"}:
        return val

    return "LOW"


def normalize_category(cat: Any) -> str:
    if cat is None:
        return "UNCATEGORIZED"

    if isinstance(cat, list):
        return str(cat[0]).upper().strip() if cat else "UNCATEGORIZED"

    if isinstance(cat, str):
        try:
            parsed = json.loads(cat)
            if isinstance(parsed, list) and parsed:
                return str(parsed[0]).upper().strip()
            if isinstance(parsed, dict):
                for key in ("primary_category", "category", "type"):
                    if parsed.get(key):
                        return str(parsed[key]).upper().strip()
        except Exception:
            pass

        clean = cat.strip()
        return clean.upper() if clean else "UNCATEGORIZED"

    return str(cat).upper().strip()


def resolve_severity(category: str, hits: Any) -> str:
    try:
        hits = int(float(hits or 0))
    except Exception:
        hits = 0

    category = normalize_category(category)

    if hits <= 0 or category == "UNCATEGORIZED":
        return "NONE"

    if category in {
        "EXPORT_CONTROL",
        "CONTROLLED_TECHNICAL_INFORMATION",
        "CREDENTIALS",
        "CREDENTIAL",
    }:
        return "CRITICAL"

    if category == "CUI":
        return "HIGH"

    if category in {"PII", "PHI", "FINANCIAL", "GOV_ID"}:
        return "MEDIUM"

    return "LOW"


def normalize_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val

    if val is None:
        return False

    if isinstance(val, (int, float)):
        return val > 0

    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "y", "cui", "has_cui"}


def safe_ts(x: Any) -> Optional[Any]:
    try:
        if pd.isna(x):
            return None
        if isinstance(x, (int, float)):
            return datetime.fromtimestamp(x / 1000)
        return x
    except Exception:
        return None


def format_category(cat: Any) -> str:
    cat = normalize_category(cat)

    return {
        "CREDENTIALS": "🔴 CREDENTIALS",
        "CREDENTIAL": "🔴 CREDENTIAL",
        "CUI": "🔴 CUI",
        "EXPORT_CONTROL": "🔴 EXPORT",
        "CONTROLLED_TECHNICAL_INFORMATION": "🔴 CTI",
        "PHI": "🟠 PHI",
        "FINANCIAL": "🟠 FIN",
        "GOV_ID": "🟡 GOV ID",
        "PII": "🟡 PII",
        "SYSTEM_INTERNAL": "🔵 SYSTEM",
        "IP": "🟢 IP",
    }.get(cat, cat)


def highlight_rows(row):
    color_map = {
        "CREDENTIALS": "#ffcccc",
        "CREDENTIAL": "#ffcccc",
        "CUI": "#ffcccc",
        "EXPORT_CONTROL": "#ffcccc",
        "CONTROLLED_TECHNICAL_INFORMATION": "#ffcccc",
        "PHI": "#ffe0b2",
        "FINANCIAL": "#ffe0b2",
        "GOV_ID": "#fff59d",
        "PII": "#fff59d",
        "SYSTEM_INTERNAL": "#e1f5fe",
        "IP": "#e8f5e9",
    }

    category = row.get("Category", "UNCATEGORIZED")
    severity = row.get("Severity", "LOW")

    color = color_map.get(category, "#ffffff")
    style = f"background-color: {color}; border-left: 6px solid black;"

    if severity in {"HIGH", "CRITICAL"}:
        style += " font-weight: bold;"

    return [style] * len(row)


def _rows_to_dicts(cursor, rows) -> List[Dict[str, Any]]:
    if not rows:
        return []

    try:
        return [dict(r) for r in rows]
    except Exception:
        columns = [d[0] for d in cursor.description]
        return [dict(zip(columns, r)) for r in rows]


def _table_exists(storage: Any, table_name: str) -> bool:
    try:
        with storage.ledger._connect() as con:
            row = con.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name=?
                LIMIT 1
                """,
                (table_name,),
            ).fetchone()

            return row is not None
    except Exception:
        return False


def _table_columns(storage: Any, table_name: str) -> List[str]:
    try:
        with storage.ledger._connect() as con:
            rows = con.execute(f"PRAGMA table_info({table_name})").fetchall()

        cols = []
        for r in rows:
            try:
                cols.append(r["name"])
            except Exception:
                cols.append(r[1])

        return cols
    except Exception:
        return []


def _safe_read_sql(storage: Any, sql: str, params: tuple = ()) -> pd.DataFrame:
    try:
        with storage.ledger._connect() as con:
            return pd.read_sql_query(sql, con, params=params)
    except Exception as e:
        print("⚠️ SAFE SQL READ ERROR:", e)
        return pd.DataFrame()


def _safe_commit(con):
    try:
        con.commit()
    except Exception:
        pass


# ============================================================
# DATA LOADERS
# ============================================================

def load_detection_rows(storage: Any, limit: int = 250) -> pd.DataFrame:
    try:
        with storage.ledger._connect() as con:
            cur = con.execute(
                """
                SELECT
                    evidence_id,
                    created_at_ms AS created,
                    json_extract(data_json, '$.primary_category') AS category,
                    json_extract(data_json, '$.category') AS fallback_category,
                    json_extract(data_json, '$.hit_count') AS hit_count,
                    json_extract(data_json, '$.severity') AS severity,
                    json_extract(data_json, '$.has_cui') AS has_cui,
                    event_type,
                    CASE
                        WHEN event_type = 'ATTACHMENT_CUI_ANALYSIS'
                        THEN 'attachment'
                        ELSE 'email'
                    END AS source,
                    data_json
                FROM evidence_events
                WHERE event_type IN (
                    'EVIDENCE_CUI_ANALYSIS',
                    'ATTACHMENT_CUI_ANALYSIS'
                )
                ORDER BY created_at_ms DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cur.fetchall()
            records = _rows_to_dicts(cur, rows)

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        if "evidence_id" not in df.columns:
            return pd.DataFrame()

        df["evidence_id"] = df["evidence_id"].astype(str).str.strip()

        df = df[
            df["evidence_id"].notna()
            & (df["evidence_id"] != "")
            & (df["evidence_id"] != "None")
            & (df["evidence_id"] != "0")
        ].copy()

        if df.empty:
            return df

        # category fallback
        if "category" not in df.columns:
            df["category"] = "UNCATEGORIZED"

        if "fallback_category" in df.columns:
            df["category"] = df["category"].fillna(df["fallback_category"])

        # parse data_json as additional fallback
        def category_from_json(row):
            existing = row.get("category")
            if existing:
                return existing

            raw = row.get("data_json")
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
                if isinstance(parsed, dict):
                    return (
                        parsed.get("primary_category")
                        or parsed.get("category")
                        or parsed.get("categories")
                        or parsed.get("flags")
                    )
            except Exception:
                pass

            return "UNCATEGORIZED"

        df["category"] = df.apply(category_from_json, axis=1)
        df["category"] = df["category"].apply(normalize_category)

        df["hit_count"] = pd.to_numeric(
            df.get("hit_count", pd.Series(index=df.index)),
            errors="coerce",
        ).fillna(0).astype(int)

        if "severity" not in df.columns:
            df["severity"] = None

        df["severity"] = df.apply(
            lambda r: normalize_severity(r.get("severity"))
            if normalize_severity(r.get("severity")) != "LOW"
            else resolve_severity(r.get("category"), r.get("hit_count")),
            axis=1,
        )

        if "source" not in df.columns:
            df["source"] = "email"

        df["source"] = df["source"].fillna("email").apply(
            lambda x: "Attachment" if str(x).lower() == "attachment" else "Email"
        )

        if "event_type" not in df.columns:
            df["event_type"] = "EVIDENCE_CUI_ANALYSIS"

        if "created" not in df.columns:
            df["created"] = None

        df["created"] = df["created"].apply(safe_ts)

        if "has_cui" not in df.columns:
            df["has_cui"] = False

        df["has_cui"] = df["has_cui"].apply(normalize_bool)

        # Final safe derived has_cui.
        df["has_cui"] = df.apply(
            lambda r: bool(r.get("has_cui"))
            or (
                int(r.get("hit_count") or 0) > 0
                and normalize_category(r.get("category")) != "UNCATEGORIZED"
            ),
            axis=1,
        )

        df = df[
            (df["hit_count"] > 0)
            & (df["category"] != "UNCATEGORIZED")
            & (df["severity"] != "NONE")
            & (df["has_cui"] == True)
        ].copy()

        if df.empty:
            return df

        df["location"] = ""
        df["notes"] = ""
        df["status"] = "OPEN"
        df["id"] = range(len(df))

        priority_map = {
            "EXPORT_CONTROL": 5,
            "CONTROLLED_TECHNICAL_INFORMATION": 5,
            "CREDENTIALS": 5,
            "CREDENTIAL": 5,
            "CUI": 4,
            "PHI": 3,
            "FINANCIAL": 3,
            "PII": 2,
            "GOV_ID": 2,
            "IP": 1,
        }

        risk_order = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
            "NONE": 0,
        }

        df["priority"] = df["category"].map(priority_map).fillna(0).astype(int)
        df["risk_score"] = df["severity"].map(risk_order).fillna(0).astype(int)
        df["cui_flag"] = df["has_cui"].apply(lambda x: "🟥 YES" if x else "🟩 NO")

        threshold = df["hit_count"].mean() + 2 * df["hit_count"].std()
        if pd.isna(threshold):
            threshold = df["hit_count"].max() + 1

        df["is_anomaly"] = df["hit_count"] > threshold

        df = df.sort_values(
            by=["risk_score", "priority", "hit_count"],
            ascending=[False, False, False],
        ).reset_index(drop=True)

        return df

    except Exception as e:
        print("🔥 LOAD DETECTION ROWS ERROR:", e)
        return pd.DataFrame()


def load_case_mapping(storage: Any) -> pd.DataFrame:
    if not _table_exists(storage, "case_evidence_map"):
        return pd.DataFrame(columns=["case_id", "evidence_id"])

    return _safe_read_sql(
        storage,
        """
        SELECT
            case_id,
            evidence_id
        FROM case_evidence_map
        """,
    )


def merge_case_ids(storage: Any, df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    mapping_df = load_case_mapping(storage)

    if mapping_df.empty:
        if "case_id" not in df.columns:
            df["case_id"] = None
        return df

    mapping_df["evidence_id"] = mapping_df["evidence_id"].astype(str).str.strip()

    df = df.drop(columns=["case_id"], errors="ignore")
    df = df.merge(mapping_df, on="evidence_id", how="left")

    return df


def build_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    display_df = df.rename(
        columns={
            "id": "ID",
            "evidence_id": "evidence_id",
            "case_id": "case_id",
            "category": "Category",
            "severity": "Severity",
            "source": "Source",
            "hit_count": "Hit Count",
            "created": "Created",
            "location": "Location",
            "notes": "Notes",
            "status": "Status",
            "event_type": "Event Type",
            "cui_flag": "CUI",
        }
    )

    required = [
        "ID",
        "case_id",
        "evidence_id",
        "Category",
        "Severity",
        "Source",
        "Hit Count",
        "CUI",
        "Created",
        "Status",
        "Location",
        "Notes",
        "Event Type",
    ]

    for col in required:
        if col not in display_df.columns:
            display_df[col] = None

    display_df["Display Category"] = display_df["Category"].apply(format_category)

    return display_df


def build_case_df(display_df: pd.DataFrame) -> pd.DataFrame:
    if display_df.empty or "case_id" not in display_df.columns:
        return pd.DataFrame()

    case_source_df = display_df.copy()
    case_source_df = case_source_df[
        case_source_df["case_id"].notna()
        & (case_source_df["case_id"].astype(str).str.strip() != "")
    ].copy()

    if case_source_df.empty:
        return pd.DataFrame()

    case_source_df = case_source_df.drop_duplicates(
        subset=["evidence_id", "Event Type"],
        keep="first",
    )

    case_df = (
        case_source_df.groupby("case_id", dropna=True)
        .agg(
            {
                "Category": lambda x: list(sorted(set([str(v) for v in x if v]))),
                "Severity": "first",
                "evidence_id": "count",
                "Source": "first",
                "Created": ["min", "max"],
                "Hit Count": "sum",
            }
        )
    )

    case_df.columns = [
        "Category",
        "Severity",
        "Alert Count",
        "Source",
        "First Seen",
        "Last Seen",
        "Total Hits",
    ]

    case_df = case_df.reset_index()

    severity_sort = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "NONE": 0,
    }

    case_df["_severity_rank"] = case_df["Severity"].map(severity_sort).fillna(0)

    case_df = case_df.sort_values(
        by=["_severity_rank", "Total Hits", "Alert Count"],
        ascending=[False, False, False],
    ).drop(columns=["_severity_rank"])

    return case_df


def load_timeline_details(storage: Any, case_id: Any) -> pd.DataFrame:
    if not case_id:
        return pd.DataFrame()

    if not _table_exists(storage, "case_timeline"):
        return pd.DataFrame()

    cols = _table_columns(storage, "case_timeline")

    order_col = "created_at_ms" if "created_at_ms" in cols else "ts" if "ts" in cols else None

    if not order_col:
        order_clause = ""
    else:
        order_clause = f"ORDER BY {order_col} DESC"

    sql = f"""
        SELECT
            case_id,
            event_type,
            details
        FROM case_timeline
        WHERE case_id = ?
        AND event_type = 'ALERT_CREATED'
        {order_clause}
    """

    return _safe_read_sql(storage, sql, params=(case_id,))


def extract_correlation_reason(v: Any) -> Optional[str]:
    try:
        if isinstance(v, str):
            v = json.loads(v)

        if isinstance(v, dict):
            return v.get("correlation_reason")
    except Exception:
        pass

    return None


def create_alerts_and_link_cases(storage: Any, df: pd.DataFrame) -> None:
    """
    Keeps existing behavior from the prior file, but prevents closed-connection
    access and avoids timeline/notification writes from Streamlit render.
    """

    if df.empty:
        return

    if not _table_exists(storage, "alerts"):
        return

    SEVERITY_RANK = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "NONE": 0,
    }

    now = int(time.time() * 1000)
    cutoff = now - 300000

    try:
        with storage.ledger._connect() as con:
            for _, row in df.iterrows():
                severity = normalize_severity(row.get("severity"))
                evidence_id = str(row.get("evidence_id", "")).strip()

                if not evidence_id:
                    continue

                if severity not in {"CRITICAL", "HIGH"}:
                    continue

                existing = con.execute(
                    """
                    SELECT severity, created_at_ms
                    FROM alerts
                    WHERE evidence_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT 1
                    """,
                    (evidence_id,),
                ).fetchone()

                allow_insert = True

                if existing:
                    try:
                        last_sev = existing["severity"]
                        last_ts = existing["created_at_ms"]
                    except Exception:
                        last_sev, last_ts = existing

                    if SEVERITY_RANK.get(severity, 0) > SEVERITY_RANK.get(last_sev, 0):
                        allow_insert = True
                    elif last_ts and last_ts > cutoff:
                        allow_insert = False

                if not allow_insert:
                    continue

                cur = con.execute(
                    """
                    INSERT OR IGNORE INTO alerts (
                        evidence_id,
                        severity,
                        message,
                        created_at_ms,
                        resolved,
                        status,
                        category,
                        location,
                        notes,
                        source_name,
                        detection_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        evidence_id,
                        severity,
                        f"CUI detected: {row.get('category', 'UNKNOWN')}",
                        now,
                        0,
                        "OPEN",
                        row.get("category"),
                        row.get("source"),
                        "",
                        row.get("event_type"),
                        json.dumps(row.to_dict(), default=str),
                    ),
                )

                if cur.rowcount > 0 and hasattr(storage.ledger, "ensure_case_for_alert"):
                    alert_row = con.execute(
                        """
                        SELECT id
                        FROM alerts
                        WHERE evidence_id = ?
                        AND severity = ?
                        ORDER BY created_at_ms DESC
                        LIMIT 1
                        """,
                        (evidence_id, severity),
                    ).fetchone()

                    if alert_row:
                        try:
                            alert_id = alert_row["id"]
                        except Exception:
                            alert_id = alert_row[0]

                        try:
                            storage.ledger.ensure_case_for_alert(
                                alert_id=alert_id,
                                evidence_id=evidence_id,
                                job_id=row.get("job_id"),
                            )
                        except Exception as e:
                            print("⚠️ CASE LINK ERROR:", e)

            _safe_commit(con)

    except Exception as e:
        print("⚠️ ALERT CREATION ERROR:", e)


# ============================================================
# MAIN PAGE
# ============================================================

def render_scan_page(storage: Any):
    st.title("📡 Scan Control")

    ledger = storage.ledger

    # ----------------------------
    # LOAD IMAP CONFIGS
    # ----------------------------
    imap_configs = getattr(storage, "imap_configs", [])

    providers = ["gmail"]
    if imap_configs:
        providers.append("imap")

    provider = st.selectbox("Provider", providers)

    st.subheader("Scan Configuration")

    mailbox = None
    selected_config = None

    if provider == "imap":
        if not imap_configs:
            st.warning("No IMAP accounts configured")
            return

        selected_config = st.selectbox(
            "Select IMAP Account",
            options=imap_configs,
            format_func=lambda x: f"{x.get('provider')} — {x.get('username')} @ {x.get('host')}",
        )

        mailbox = selected_config.get("mailbox", "INBOX")
        st.info(f"Using mailbox: {mailbox}")

    elif provider == "gmail":
        connected_mailboxes = []

        if hasattr(ledger, "list_connected_mailboxes"):
            try:
                connected_mailboxes = ledger.list_connected_mailboxes(provider="gmail")
            except Exception as e:
                st.warning(f"Could not load connected Gmail mailboxes: {e}")

        if connected_mailboxes:
            mailbox = st.selectbox("Connected Mailbox", connected_mailboxes)
        else:
            mailbox = st.text_input("Mailbox")

    lookback = st.number_input("Lookback Hours", min_value=1, max_value=720, value=168)
    attachments_only = st.checkbox("Attachments Only", value=True)
    max_messages = st.number_input("Max Messages", min_value=1, max_value=5000, value=100)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Enqueue Scan", use_container_width=True):
            mailbox = (mailbox or "").strip()

            if not mailbox:
                st.error("Please select or enter a mailbox.")
                return

            if provider == "gmail":
                if hasattr(ledger, "get_oauth_token"):
                    token = ledger.get_oauth_token("gmail", mailbox)

                    if not token:
                        st.error(
                            f"No Gmail OAuth token found for {mailbox}. "
                            "Connect it from the Admin page first."
                        )
                        return

                job_id = ledger.enqueue_scan(
                    provider="gmail",
                    mailbox=mailbox,
                    lookback_hours=int(lookback),
                    attachments_only=attachments_only,
                    max_messages=int(max_messages),
                    payload={},
                )

                st.success(f"Gmail scan enqueued (job_id={job_id})")
                st.rerun()

            elif provider == "imap":
                job_id = ledger.enqueue_scan(
                    provider="imap",
                    mailbox=mailbox,
                    lookback_hours=int(lookback),
                    attachments_only=attachments_only,
                    max_messages=int(max_messages),
                    payload=selected_config,
                )

                st.success(f"IMAP scan enqueued (job_id={job_id})")
                st.rerun()

    with col2:
        if st.button("🔄 Refresh Jobs", use_container_width=True):
            st.rerun()

    auto_refresh = st.checkbox("Auto Refresh", value=True)

    st.divider()
    st.subheader("🚀 Running Jobs")

    running_jobs = []

    if hasattr(ledger, "list_running_jobs"):
        try:
            running_jobs = ledger.list_running_jobs(limit=20)
        except Exception as e:
            st.warning(f"Could not load running jobs: {e}")

    if running_jobs:
        for job in running_jobs:
            c1, c2, c3, c4, c5 = st.columns([1, 2, 3, 2, 2])

            job_id = job.get("id")
            mailbox_val = job.get("mailbox")
            status = job.get("status")

            current = job.get("progress_current") or 0
            total = job.get("progress_total") or 1
            progress = current / max(total, 1)

            started = job.get("started_at_ms")
            duration = "-"

            if started:
                try:
                    duration_sec = int((time.time() * 1000 - int(started)) / 1000)
                    duration = f"{duration_sec}s"
                except Exception:
                    duration = "-"

            c1.write(job_id)
            c2.write(status)
            c3.write(mailbox_val)
            c4.progress(min(max(progress, 0), 1))
            c5.write(duration)
    else:
        st.info("No running jobs.")

    st.divider()
    st.subheader("⚡ Bulk Job Controls")

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        if st.button("🔁 Retry All Failed"):
            if hasattr(ledger, "retry_all_failed"):
                ledger.retry_all_failed()
                st.success("All failed jobs requeued")
                st.rerun()
            else:
                st.warning("retry_all_failed() is not available on this ledger.")

    with b2:
        if st.button("🗑 Delete Completed"):
            if hasattr(ledger, "delete_completed"):
                ledger.delete_completed()
                st.warning("Completed jobs deleted")
                st.rerun()
            else:
                st.warning("delete_completed() is not available on this ledger.")

    with b3:
        if st.button("🛑 Cancel Running"):
            if hasattr(ledger, "cancel_all_running"):
                ledger.cancel_all_running()
                st.error("All running jobs cancelled")
                st.rerun()
            else:
                st.warning("cancel_all_running() is not available on this ledger.")

    with b4:
        confirm_wipe = st.checkbox("Confirm full wipe", key="confirm_full_job_wipe")

        if st.button("☢️ Clear ALL Jobs"):
            if not confirm_wipe:
                st.warning("Check confirm full wipe first.")
            elif hasattr(ledger, "clear_all_jobs"):
                ledger.clear_all_jobs()
                st.error("ALL jobs deleted")
                st.rerun()
            else:
                st.warning("clear_all_jobs() is not available on this ledger.")

    st.divider()
    st.subheader("📋 Scan Job Queue")

    jobs = []

    if hasattr(ledger, "list_scan_jobs"):
        try:
            jobs = ledger.list_scan_jobs(limit=100)
        except Exception as e:
            st.warning(f"Could not load scan jobs: {e}")

    if jobs:
        for job in jobs:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 2, 2, 3])

            jid = job.get("id")
            status = (job.get("status") or "").upper()
            completed = job.get("completed_at_ms")

            if status == "RUNNING" and completed:
                status = "COMPLETED"

            col1.write(jid)
            col2.write(job.get("provider"))
            col3.write(job.get("mailbox"))
            col4.write(status)
            col5.write(job.get("last_error") or "-")

            with col6:
                if status in {"RUNNING", "QUEUED", "PENDING", "PROCESSING"}:
                    if st.button("Cancel", key=f"cancel_{jid}"):
                        if hasattr(ledger, "cancel_scan"):
                            ledger.cancel_scan(jid)
                            st.warning(f"Cancelled job {jid}")
                            st.rerun()
                        else:
                            st.warning("cancel_scan() is not available.")

                elif status == "FAILED":
                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button("Retry", key=f"retry_{jid}"):
                            if hasattr(ledger, "retry_scan"):
                                ledger.retry_scan(jid)
                                st.success(f"Requeued job {jid}")
                                st.rerun()
                            else:
                                st.warning("retry_scan() is not available.")

                    with c2:
                        if st.button("Delete", key=f"delete_{jid}"):
                            if hasattr(ledger, "delete_scan"):
                                ledger.delete_scan(jid)
                                st.error(f"Deleted job {jid}")
                                st.rerun()
                            else:
                                st.warning("delete_scan() is not available.")

                elif status == "COMPLETED":
                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button("Re-run", key=f"rerun_{jid}"):
                            if hasattr(ledger, "retry_scan"):
                                ledger.retry_scan(jid)
                                st.success(f"Re-running job {jid}")
                                st.rerun()
                            else:
                                st.warning("retry_scan() is not available.")

                    with c2:
                        if st.button("Delete", key=f"delete_completed_{jid}"):
                            if hasattr(ledger, "delete_scan"):
                                ledger.delete_scan(jid)
                                st.error(f"Deleted job {jid}")
                                st.rerun()
                            else:
                                st.warning("delete_scan() is not available.")
    else:
        st.info("No scan jobs found.")

    st.divider()
    st.subheader("📊 Scan Results")

    if hasattr(ledger, "get_scan_stats"):
        try:
            stats = ledger.get_scan_stats()

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total Jobs", stats.get("total_jobs", 0))
            c2.metric("Queued", stats.get("queued", 0))
            c3.metric("Running", stats.get("running", 0))
            c4.metric("Completed", stats.get("completed", 0))
            c5.metric("Failed", stats.get("failed", 0))

            if stats.get("last_run"):
                ts = datetime.fromtimestamp(stats["last_run"] / 1000)
                st.caption(f"🕒 Last Scan Run: {ts}")
        except Exception as e:
            st.warning(f"Could not load scan stats: {e}")

    if "scan_auto_refresh_count" not in st.session_state:
        st.session_state["scan_auto_refresh_count"] = 0

    if auto_refresh and st.session_state["scan_auto_refresh_count"] < 10:
        st.session_state["scan_auto_refresh_count"] += 1
        time.sleep(2)
        st.rerun()

    if not auto_refresh:
        st.session_state["scan_auto_refresh_count"] = 0

    st.divider()
    st.subheader("📊 Scan Job Analytics")

    print("🔥 ANALYTICS DB PATH:", getattr(ledger, "db_path", "UNKNOWN"))

    if hasattr(ledger, "get_scan_analytics"):
        try:
            stats = ledger.get_scan_analytics()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total Jobs", stats.get("total", 0))
            c2.metric("Completed", stats.get("completed", 0))
            c3.metric("Failed", stats.get("failed", 0))
            c4.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")

            st.metric(
                "Avg Duration (sec)",
                f"{(stats.get('avg_duration_ms') or 0) / 1000:.2f}",
            )

            st.subheader("📈 Jobs Over Time")

            if stats.get("recent_jobs"):
                trend_df = pd.DataFrame(stats["recent_jobs"])
                if not trend_df.empty and "day" in trend_df.columns and "jobs" in trend_df.columns:
                    trend_df = trend_df.sort_values("day")
                    st.line_chart(trend_df.set_index("day")["jobs"])
                else:
                    st.info("No valid recent job trend data.")
            else:
                st.info("No recent job trend data.")

            st.subheader("❌ Top Errors")

            if stats.get("top_errors"):
                err_df = pd.DataFrame(stats["top_errors"])
                st.dataframe(err_df, use_container_width=True)
            else:
                st.info("No errors recorded")

            st.subheader("📧 Most Active Mailboxes")

            if stats.get("top_mailboxes"):
                mb_df = pd.DataFrame(stats["top_mailboxes"])
                st.dataframe(mb_df, use_container_width=True)
            else:
                st.info("No mailbox activity yet.")

        except Exception as e:
            st.warning(f"Could not load scan analytics: {e}")

    # ============================================================
    # ALERTS + CASES SYSTEM
    # ============================================================

    st.divider()
    st.subheader("🚨 Sensitive Data Detections")

    print("🔥 USING EVIDENCE QUERY")

    df = load_detection_rows(storage, limit=250)

    print("EVIDENCE ROW COUNT:", len(df))
    if not df.empty:
        print("EVIDENCE SAMPLE:", df.head(1).to_dict("records"))
    else:
        print("EVIDENCE SAMPLE: NO ROWS")

    if df.empty:
        st.info("No detections yet.")
        return

    print("🔥 FILTERED CUI DF ROW COUNT:", len(df))
    print("🔥 FILTERED CUI SAMPLE:", df.head(5).to_dict("records"))

    # Alert/case creation kept safe and connection-isolated.
    create_alerts_and_link_cases(storage, df)

    # Reload/merge case IDs after alert/case linking.
    df = merge_case_ids(storage, df)

    print(
        "🧪 FINAL REAL CASE IDS:",
        df.get("case_id", pd.Series(dtype=str)).dropna().unique().tolist()
        if "case_id" in df.columns
        else [],
    )

    display_df = build_display_df(df)

    print("✅ FINAL CUI DF COLUMNS:", df.columns.tolist())
    print("🧪 DISPLAY DF REAL CASE IDS:", display_df["case_id"].dropna().unique().tolist())

    case_df = build_case_df(display_df)

    # ----------------------------
    # DETECTION ROWS
    # ----------------------------
    st.markdown("### 🛡️ Detection Rows")

    detection_columns = [
        "ID",
        "case_id",
        "evidence_id",
        "Display Category",
        "Severity",
        "Source",
        "Hit Count",
        "CUI",
        "Created",
        "Status",
    ]

    st.dataframe(
        display_df[detection_columns],
        use_container_width=True,
    )

    # ----------------------------
    # CASE SUMMARY
    # ----------------------------
    st.subheader("📁 Case Summary")

    if case_df.empty:
        st.warning(
            "Detections exist, but no case mappings were found yet. "
            "Run the worker/supervisor case orchestrator if cases should be created outside the UI."
        )
    else:
        st.dataframe(case_df, use_container_width=True)

    # ----------------------------
    # RISK DISTRIBUTION
    # ----------------------------
    st.subheader("🔥 Risk Distribution")

    if "severity" in df.columns:
        st.bar_chart(df["severity"].value_counts())
    else:
        st.info("No severity data available.")

    if case_df.empty:
        st.markdown("### ⬇️ Export")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Export JSON",
                data=json.dumps(display_df.to_dict(orient="records"), indent=2, default=str),
                file_name="alerts.json",
                mime="application/json",
            )

        with col2:
            buffer = io.StringIO()
            display_df.to_csv(buffer, index=False)

            st.download_button(
                "Export CSV",
                data=buffer.getvalue(),
                file_name="alerts.csv",
                mime="text/csv",
            )

        return

    # ============================================================
    # CORRELATED ALERTS
    # ============================================================

    st.markdown("### 🔗 Correlated Alerts")

    selected_case = st.selectbox(
        "Select Case",
        options=case_df["case_id"].tolist(),
        key="scan_selected_case",
    )

    case_alerts = display_df[
        display_df["case_id"] == selected_case
    ].reset_index(drop=True)

    timeline_rows = load_timeline_details(storage, selected_case)

    if not timeline_rows.empty:
        details_value = timeline_rows.iloc[0].get("details")
        case_alerts["details"] = details_value
    else:
        case_alerts["details"] = None

    case_alerts["correlation_reason"] = case_alerts["details"].apply(
        extract_correlation_reason
    )

    print(
        "🔗 CORRELATION VALUES:",
        case_alerts["correlation_reason"].dropna().tolist(),
    )

    if case_alerts.empty:
        st.info("No alerts linked to this case.")
        return

    st.dataframe(
        case_alerts.style.apply(highlight_rows, axis=1),
        use_container_width=True,
    )

    # ----------------------------
    # ALERT SELECTOR
    # ----------------------------
    selected_evidence_id = st.selectbox(
        "Select Alert",
        options=case_alerts["evidence_id"].tolist(),
        key="scan_selected_alert",
        format_func=lambda eid: (
            f"{str(eid)[:10]} | "
            f"{case_alerts[case_alerts['evidence_id'] == eid].iloc[0]['Category']} | "
            f"{case_alerts[case_alerts['evidence_id'] == eid].iloc[0]['Severity']}"
        ),
    )

    alert_row = case_alerts[
        case_alerts["evidence_id"] == selected_evidence_id
    ].iloc[0]

    # ----------------------------
    # DETAILS PANEL
    # ----------------------------
    st.markdown("### 📄 Details")

    st.write("**Category:**", format_category(alert_row.get("Category")))
    st.write("**Severity:**", alert_row.get("Severity"))
    st.write("**Location:**", alert_row.get("Location"))
    st.write("**Source:**", alert_row.get("Source"))
    st.write("**Notes:**", alert_row.get("Notes"))
    st.write("**Created:**", alert_row.get("Created"))
    st.write("**Evidence ID:**", alert_row.get("evidence_id"))

    # ----------------------------
    # CORRELATION DETAILS
    # ----------------------------
    reason = alert_row.get("correlation_reason")

    if reason:
        reason = str(reason).strip().upper()

        badge_map = {
            "ATTACHMENT_SHA_MATCH": "🟣 Exact Attachment Match",
            "SENDER_MATCH": "🔵 Same Sender",
            "SUBJECT_MATCH": "🟠 Same Subject",
            "THREAD_MATCH": "🟢 Same Thread",
            "CATEGORY_CLUSTER": "⚪ Category Cluster",
        }

        st.markdown("### 🔗 Correlation")
        st.info(badge_map.get(reason, reason))

    # ----------------------------
    # ALERT → EVIDENCE LINK
    # ----------------------------
    notes = alert_row.get("Notes", "") or ""
    evidence_id = str(alert_row.get("evidence_id", "")).strip()

    if st.button("🔎 View Evidence", use_container_width=True):
        if not evidence_id:
            st.error("No evidence_id linked to this alert")
        else:
            st.session_state["selected_evidence_id"] = evidence_id
            st.session_state["alert_notes"] = notes
            st.session_state["page"] = "Evidence Viewer"
            st.rerun()

    # ----------------------------
    # EVIDENCE HELPER
    # ----------------------------
    def get_evidence(alert_id):
        try:
            with storage.ledger._connect() as con:
                row = con.execute(
                    """
                    SELECT evidence_id
                    FROM evidence_records
                    WHERE evidence_id LIKE ?
                    LIMIT 1
                    """,
                    (f"{alert_id}%",),
                ).fetchone()

            if not row:
                return None

            try:
                found_evidence_id = row["evidence_id"]
            except Exception:
                found_evidence_id = row[0]

            data = storage.vault.open_bytes(found_evidence_id)

            if not data:
                return None

            try:
                return data.decode("utf-8", errors="ignore")
            except Exception:
                return str(data[:2000])

        except Exception as e:
            return f"[evidence error] {e}"

    # ----------------------------
    # EXPORT
    # ----------------------------
    st.markdown("### ⬇️ Export")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Export JSON",
            data=json.dumps(display_df.to_dict(orient="records"), indent=2, default=str),
            file_name="alerts.json",
            mime="application/json",
        )

    with col2:
        buffer = io.StringIO()
        display_df.to_csv(buffer, index=False)

        st.download_button(
            "Export CSV",
            data=buffer.getvalue(),
            file_name="alerts.csv",
            mime="text/csv",
        )