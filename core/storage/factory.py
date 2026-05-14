# core/storage/factory.py
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from types import SimpleNamespace
from typing import Any, Optional

from .interfaces import StorageBundle
from .local_vault import LocalVault
from .sqlite_ledger import SQLiteLedger
from .governance_repository import GovernanceRepository
from core.events.event_bus import get_event_bus

def _truthy(v: Optional[str]) -> bool:
    if not v:
        return False
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


# ----------------------------
# Minimal, safe API surface
# ----------------------------

@dataclass(frozen=True)
class ApiV1:
    ledger: Any
    vault: Any
    governance: Any


@dataclass(frozen=True)
class ApiRoot:
    v1: ApiV1


def _attach_api(
    storage: Any,
    *,
    ledger: Any,
    vault: Any,
    governance: Any,
) -> Any:
    """
    Attach storage.api.v1.{ledger,vault} safely.

    If StorageBundle is frozen / disallows attribute set, we return a wrapper
    that preserves .ledger and .vault plus .api.
    """
    api = ApiRoot(
        v1=ApiV1(
            ledger=ledger,
            vault=vault,
            governance=governance,
        )
    )

    try:
        setattr(storage, "api", api)
        return storage
    except Exception:
        # Fallback wrapper (runtime-safe)
        return SimpleNamespace(
            ledger=ledger,
            vault=vault,
            governance=governance,
            api=api,
        )


@lru_cache(maxsize=1)
def build_storage() -> Any:
    """
    GLOBAL STORAGE SINGLETON.

    Guarantees:
      ✔ safe Streamlit reruns
      ✔ single storage instance per process
      ✔ stable paths + immutability flag

    Env:
      STORAGE_MODE=local|s3
      LEDGER_DB_PATH=data/ledger.db
      IMMUTABLE_LEDGER=1|true
    """
    mode = (os.getenv("STORAGE_MODE") or "local").strip().lower()
    immutable = _truthy(os.getenv("IMMUTABLE_LEDGER"))
    db_path = os.getenv("LEDGER_DB_PATH", "data/ledger.db")
    print("🔥 DB PATH BEING USED:", db_path)
    ledger = SQLiteLedger(db_path=db_path, immutable=immutable)

    # ---------------------------------------------------
    # GOVERNANCE REPOSITORY
    # ---------------------------------------------------

    governance = GovernanceRepository(db_path=db_path)
    governance.ensure_schema()

    governance.ensure_schema()

    if mode == "s3":
        from .s3_vault import S3Vault  # implemented later
        vault = S3Vault()
    else:
        vault = LocalVault()

    storage = StorageBundle(
        vault=vault,
        ledger=ledger
    )
    # ---------------------------------------------------
    # ATTACH GOVERNANCE
    # ---------------------------------------------------

    try:
        setattr(storage, "governance", governance)
    except Exception:
        pass
    storage = _attach_api(
        storage,
        ledger=ledger,
        vault=vault,
        governance=governance,
    )

    print(f"""
STORAGE INITIALIZED
-------------------
mode: {mode}
immutable: {immutable}
db: {db_path}
""")
    event_bus = get_event_bus()
    try:
        setattr(storage, "event_bus", event_bus)
    except Exception:
        pass
    return storage



