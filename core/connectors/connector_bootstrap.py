"""
core/connectors/connector_bootstrap.py

Centralized connector bootstrap + registration layer.

Responsibilities:
- Load connector config/secrets
- Initialize connectors
- Register into ConnectorRegistry
- Validate auth state
- Emit connector telemetry
- Support multi-tenant registration
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from core.connectors.connector_registry import (
    ConnectorRegistry,
    get_connector_registry,
)

from core.connectors.microsoft_graph_connector import (
    MicrosoftGraphConnector,
)

from core.connectors.okta_connector import (
    OktaConnector,
)
from core.connectors.crowdstrike_connector import (
    CrowdStrikeConnector,
)
from core.connectors.sentinelone_connector import (
    SentinelOneConnector,
)
from core.connectors.google_workspace_connector import (
    GoogleWorkspaceConnector,
)

DEFAULT_TENANT = "default"


def _safe_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


# ----------------------------------------------------------------------
# CONFIG LOADERS
# ----------------------------------------------------------------------

def load_graph_config(
    storage: Any = None,
    *,
    tenant_id: str = DEFAULT_TENANT,
) -> Dict[str, Any]:

    secrets = getattr(storage, "secrets", {}) if storage else {}

    return {
        "tenant_id": tenant_id,
        "client_id": (
            os.getenv("MS_GRAPH_CLIENT_ID")
            or secrets.get("MS_GRAPH_CLIENT_ID")
        ),
        "client_secret": (
            os.getenv("MS_GRAPH_CLIENT_SECRET")
            or secrets.get("MS_GRAPH_CLIENT_SECRET")
        ),
        "tenant": (
            os.getenv("MS_GRAPH_TENANT_ID")
            or secrets.get("MS_GRAPH_TENANT_ID")
        ),
        "authority": (
            os.getenv("MS_GRAPH_AUTHORITY")
            or secrets.get("MS_GRAPH_AUTHORITY")
        ),
        "scope": (
            os.getenv("MS_GRAPH_SCOPE")
            or secrets.get("MS_GRAPH_SCOPE")
            or "https://graph.microsoft.com/.default"
        ),
        "timeout": _safe_int(
            os.getenv("MS_GRAPH_TIMEOUT")
            or secrets.get("MS_GRAPH_TIMEOUT"),
            30,
        ),
    }


def load_okta_config(
    storage: Any = None,
    *,
    tenant_id: str = DEFAULT_TENANT,
) -> Dict[str, Any]:

    secrets = getattr(storage, "secrets", {}) if storage else {}

    return {
        "tenant_id": tenant_id,
        "okta_domain": (
            os.getenv("OKTA_DOMAIN")
            or secrets.get("OKTA_DOMAIN")
            or secrets.get("OKTA_BASE_URL")
        ),
        "api_token": (
            os.getenv("OKTA_API_TOKEN")
            or secrets.get("OKTA_API_TOKEN")
        ),
        "timeout": _safe_int(
            os.getenv("OKTA_TIMEOUT")
            or secrets.get("OKTA_TIMEOUT"),
            30,
        ),
    }

# ----------------------------------------------------------------------
# CROWDSTRIKE CONFIG
# ----------------------------------------------------------------------

def load_crowdstrike_config(
    storage: Any = None,
    *,
    tenant_id: str = DEFAULT_TENANT,
) -> Dict[str, Any]:

    secrets = getattr(
        storage,
        "secrets",
        {},
    ) if storage else {}

    return {
        "tenant_id": tenant_id,

        "client_id": (
            os.getenv(
                "CROWDSTRIKE_CLIENT_ID"
            )
            or secrets.get(
                "CROWDSTRIKE_CLIENT_ID"
            )
        ),

        "client_secret": (
            os.getenv(
                "CROWDSTRIKE_CLIENT_SECRET"
            )
            or secrets.get(
                "CROWDSTRIKE_CLIENT_SECRET"
            )
        ),

        "base_url": (
            os.getenv(
                "CROWDSTRIKE_BASE_URL"
            )
            or secrets.get(
                "CROWDSTRIKE_BASE_URL"
            )
            or "https://api.crowdstrike.com"
        ),

        "timeout": _safe_int(
            os.getenv(
                "CROWDSTRIKE_TIMEOUT"
            )
            or secrets.get(
                "CROWDSTRIKE_TIMEOUT"
            ),
            30,
        ),
    }

# ----------------------------------------------------------------------
# SENTINELONE CONFIG
# ----------------------------------------------------------------------

def load_sentinelone_config(
    storage: Any = None,
    *,
    tenant_id: str = DEFAULT_TENANT,
) -> Dict[str, Any]:

    secrets = getattr(
        storage,
        "secrets",
        {},
    ) if storage else {}

    return {
        "tenant_id": tenant_id,

        "api_token": (
            os.getenv(
                "S1_API_TOKEN"
            )
            or secrets.get(
                "S1_API_TOKEN"
            )
            or secrets.get(
                "SENTINELONE_API_TOKEN"
            )
        ),

        "base_url": (
            os.getenv(
                "S1_BASE_URL"
            )
            or secrets.get(
                "S1_BASE_URL"
            )
            or secrets.get(
                "SENTINELONE_BASE_URL"
            )
            or "https://usea1-partners.sentinelone.net/web/api/v2.1"
        ),

        "timeout": _safe_int(
            os.getenv(
                "S1_TIMEOUT"
            )
            or secrets.get(
                "S1_TIMEOUT"
            ),
            30,
        ),
    }

# ----------------------------------------------------------------------
# GOOGLE WORKSPACE CONFIG
# ----------------------------------------------------------------------

def load_google_workspace_config(
    storage: Any = None,
    *,
    tenant_id: str = DEFAULT_TENANT,
) -> Dict[str, Any]:

    secrets = getattr(
        storage,
        "secrets",
        {},
    ) if storage else {}

    return {
        "tenant_id": tenant_id,

        # ----------------------------------------------------------
        # GOOGLE ACCESS TOKEN
        # ----------------------------------------------------------

        "access_token": (
            os.getenv(
                "GOOGLE_ACCESS_TOKEN"
            )
            or secrets.get(
                "GOOGLE_ACCESS_TOKEN"
            )
        ),

        # ----------------------------------------------------------
        # ADMIN SDK BASE
        # ----------------------------------------------------------

        "base_url": (
            os.getenv(
                "GOOGLE_ADMIN_BASE_URL"
            )
            or secrets.get(
                "GOOGLE_ADMIN_BASE_URL"
            )
            or "https://admin.googleapis.com"
        ),

        # ----------------------------------------------------------
        # GMAIL BASE
        # ----------------------------------------------------------

        "gmail_base": (
            os.getenv(
                "GOOGLE_GMAIL_BASE_URL"
            )
            or secrets.get(
                "GOOGLE_GMAIL_BASE_URL"
            )
            or "https://gmail.googleapis.com"
        ),

        # ----------------------------------------------------------
        # DRIVE BASE
        # ----------------------------------------------------------

        "drive_base": (
            os.getenv(
                "GOOGLE_DRIVE_BASE_URL"
            )
            or secrets.get(
                "GOOGLE_DRIVE_BASE_URL"
            )
            or "https://www.googleapis.com"
        ),

        # ----------------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------------

        "timeout": _safe_int(
            os.getenv(
                "GOOGLE_TIMEOUT"
            )
            or secrets.get(
                "GOOGLE_TIMEOUT"
            ),
            30,
        ),
    }



# ----------------------------------------------------------------------
# REGISTRATION HELPERS
# ----------------------------------------------------------------------

def register_graph_connector(
    registry: ConnectorRegistry,
    *,
    storage: Any = None,
    tenant_id: str = DEFAULT_TENANT,
    event_bus: Any = None,
    simulation_mode: bool = True,
) -> MicrosoftGraphConnector:

    config = load_graph_config(
        storage,
        tenant_id=tenant_id,
    )

    connector = MicrosoftGraphConnector(
        tenant_id=tenant_id,
        config=config,
        event_bus=event_bus,
        storage=storage,
        simulation_mode=simulation_mode,
    )

    auth_state = connector.authenticate()

    registry.register(
        connector,
        tenant_id=tenant_id,
    )

    _emit_connector_bootstrap_event(
        event_bus,
        event_type="CONNECTOR_REGISTERED",
        tenant_id=tenant_id,
        connector_id=connector.connector_id,
        payload={
            "connector": "microsoft_graph",
            "authenticated": auth_state.authenticated,
            "simulation_mode": simulation_mode,
        },
    )

    return connector


def register_okta_connector(
    registry: ConnectorRegistry,
    *,
    storage: Any = None,
    tenant_id: str = DEFAULT_TENANT,
    event_bus: Any = None,
    simulation_mode: bool = True,
) -> OktaConnector:

    config = load_okta_config(
        storage,
        tenant_id=tenant_id,
    )

    connector = OktaConnector(
        tenant_id=tenant_id,
        config=config,
        event_bus=event_bus,
        storage=storage,
        simulation_mode=simulation_mode,
    )

    auth_state = connector.authenticate()

    registry.register(
        connector,
        tenant_id=tenant_id,
    )

    _emit_connector_bootstrap_event(
        event_bus,
        event_type="CONNECTOR_REGISTERED",
        tenant_id=tenant_id,
        connector_id=connector.connector_id,
        payload={
            "connector": "okta",
            "authenticated": auth_state.authenticated,
            "simulation_mode": simulation_mode,
            "okta_domain": config.get("okta_domain"),
        },
    )

    return connector

# ----------------------------------------------------------------------
# CROWDSTRIKE CONNECTOR
# ----------------------------------------------------------------------

def register_crowdstrike_connector(
    registry: ConnectorRegistry,
    *,
    storage: Any = None,
    tenant_id: str = DEFAULT_TENANT,
    event_bus: Any = None,
    simulation_mode: bool = True,
) -> CrowdStrikeConnector:

    config = load_crowdstrike_config(
        storage,
        tenant_id=tenant_id,
    )

    connector = CrowdStrikeConnector(
        tenant_id=tenant_id,
        config=config,
        event_bus=event_bus,
        storage=storage,
        simulation_mode=simulation_mode,
    )

    auth_state = connector.authenticate()

    registry.register(
        connector,
        tenant_id=tenant_id,
    )

    _emit_connector_bootstrap_event(
        event_bus,
        event_type="CONNECTOR_REGISTERED",
        tenant_id=tenant_id,
        connector_id=connector.connector_id,
        payload={
            "connector": "crowdstrike",
            "authenticated": (
                auth_state.authenticated
            ),
            "simulation_mode": (
                simulation_mode
            ),
            "base_url": (
                config.get("base_url")
            ),
        },
    )

    return connector

# ----------------------------------------------------------------------
# SENTINELONE CONNECTOR
# ----------------------------------------------------------------------

def register_sentinelone_connector(
    registry: ConnectorRegistry,
    *,
    storage: Any = None,
    tenant_id: str = DEFAULT_TENANT,
    event_bus: Any = None,
    simulation_mode: bool = True,
) -> SentinelOneConnector:

    config = load_sentinelone_config(
        storage,
        tenant_id=tenant_id,
    )

    connector = SentinelOneConnector(
        tenant_id=tenant_id,
        config=config,
        event_bus=event_bus,
        storage=storage,
        simulation_mode=simulation_mode,
    )

    auth_state = connector.authenticate()

    registry.register(
        connector,
        tenant_id=tenant_id,
    )

    _emit_connector_bootstrap_event(
        event_bus,
        event_type="CONNECTOR_REGISTERED",
        tenant_id=tenant_id,
        connector_id=connector.connector_id,
        payload={
            "connector": "sentinelone",
            "authenticated": (
                auth_state.authenticated
            ),
            "simulation_mode": (
                simulation_mode
            ),
            "base_url": (
                config.get("base_url")
            ),
        },
    )

    return connector
# ----------------------------------------------------------------------
# GOOGLE WORKSPACE CONNECTOR
# ----------------------------------------------------------------------

def register_google_workspace_connector(
    registry: ConnectorRegistry,
    *,
    storage: Any = None,
    tenant_id: str = DEFAULT_TENANT,
    event_bus: Any = None,
    simulation_mode: bool = True,
) -> GoogleWorkspaceConnector:

    config = load_google_workspace_config(
        storage,
        tenant_id=tenant_id,
    )

    connector = GoogleWorkspaceConnector(
        tenant_id=tenant_id,
        config=config,
        event_bus=event_bus,
        storage=storage,
        simulation_mode=simulation_mode,
    )

    auth_state = connector.authenticate()

    registry.register(
        connector,
        tenant_id=tenant_id,
    )

    _emit_connector_bootstrap_event(
        event_bus,
        event_type="CONNECTOR_REGISTERED",
        tenant_id=tenant_id,
        connector_id=connector.connector_id,
        payload={
            "connector": "google_workspace",
            "authenticated": (
                auth_state.authenticated
            ),
            "simulation_mode": (
                simulation_mode
            ),
            "base_url": (
                config.get("base_url")
            ),
        },
    )

    return connector

# ----------------------------------------------------------------------
# MAIN BOOTSTRAP
# ----------------------------------------------------------------------

def bootstrap_connectors(
    storage: Any = None,
    *,
    registry: Optional[ConnectorRegistry] = None,
    event_bus: Any = None,
    tenant_id: str = DEFAULT_TENANT,
    simulation_mode: bool = True,
    enable_graph: bool = True,
    enable_okta: bool = True,
    enable_crowdstrike: bool = True,
    enable_sentinelone: bool = True,
    enable_google_workspace: bool = True,
) -> ConnectorRegistry:

    registry = registry or get_connector_registry()

    connectors: List[Any] = []

    # --------------------------------------------------------------
    # MICROSOFT GRAPH
    # --------------------------------------------------------------

    if enable_graph:
        try:
            connectors.append(
                register_graph_connector(
                    registry,
                    storage=storage,
                    tenant_id=tenant_id,
                    event_bus=event_bus,
                    simulation_mode=simulation_mode,
                )
            )
        except Exception as exc:
            _emit_connector_bootstrap_event(
                event_bus,
                event_type="CONNECTOR_REGISTRATION_FAILED",
                tenant_id=tenant_id,
                connector_id="microsoft_graph",
                payload={
                    "error": str(exc),
                },
                severity="HIGH",
            )

    # --------------------------------------------------------------
    # OKTA
    # --------------------------------------------------------------

    if enable_okta:
        try:
            connectors.append(
                register_okta_connector(
                    registry,
                    storage=storage,
                    tenant_id=tenant_id,
                    event_bus=event_bus,
                    simulation_mode=simulation_mode,
                )
            )
        except Exception as exc:
            _emit_connector_bootstrap_event(
                event_bus,
                event_type="CONNECTOR_REGISTRATION_FAILED",
                tenant_id=tenant_id,
                connector_id="okta",
                payload={
                    "error": str(exc),
                },
                severity="HIGH",
            )
    # --------------------------------------------------------------
    # CROWDSTRIKE
    # --------------------------------------------------------------

    if enable_crowdstrike:

        try:

            connectors.append(
                register_crowdstrike_connector(
                    registry,
                    storage=storage,
                    tenant_id=tenant_id,
                    event_bus=event_bus,
                    simulation_mode=simulation_mode,
                )
            )

        except Exception as exc:

            _emit_connector_bootstrap_event(
                event_bus,
                event_type=(
                    "CONNECTOR_REGISTRATION_FAILED"
                ),
                tenant_id=tenant_id,
                connector_id="crowdstrike",
                payload={
                    "error": str(exc),
                },
                severity="HIGH",
            )

            # --------------------------------------------------------------
            # SENTINELONE
            # --------------------------------------------------------------

            if enable_sentinelone:

                try:

                    connectors.append(
                        register_sentinelone_connector(
                            registry,
                            storage=storage,
                            tenant_id=tenant_id,
                            event_bus=event_bus,
                            simulation_mode=simulation_mode,
                        )
                    )

                except Exception as exc:

                    _emit_connector_bootstrap_event(
                        event_bus,
                        event_type=(
                            "CONNECTOR_REGISTRATION_FAILED"
                        ),
                        tenant_id=tenant_id,
                        connector_id="sentinelone",
                        payload={
                            "error": str(exc),
                        },
                        severity="HIGH",
                    )
                # --------------------------------------------------------------
                # GOOGLE WORKSPACE
                # --------------------------------------------------------------

                if enable_google_workspace:

                    try:

                        connectors.append(
                            register_google_workspace_connector(
                                registry,
                                storage=storage,
                                tenant_id=tenant_id,
                                event_bus=event_bus,
                                simulation_mode=simulation_mode,
                            )
                        )

                    except Exception as exc:

                        _emit_connector_bootstrap_event(
                            event_bus,
                            event_type=(
                                "CONNECTOR_REGISTRATION_FAILED"
                            ),
                            tenant_id=tenant_id,
                            connector_id="google_workspace",
                            payload={
                                "error": str(exc),
                            },
                            severity="HIGH",
                        )
    # --------------------------------------------------------------
    # FINAL TELEMETRY
    # --------------------------------------------------------------

    _emit_connector_bootstrap_event(
        event_bus,
        event_type="CONNECTOR_BOOTSTRAP_COMPLETED",
        tenant_id=tenant_id,
        connector_id="bootstrap",
        payload={
            "registered_connectors": [
                c.connector_id
                for c in connectors
            ],
            "connector_count": len(connectors),
            "simulation_mode": simulation_mode,
        },
    )

    return registry


# ----------------------------------------------------------------------
# TENANT BULK BOOTSTRAP
# ----------------------------------------------------------------------

def bootstrap_multi_tenant_connectors(
    storage: Any,
    *,
    tenant_ids: List[str],
    registry: Optional[ConnectorRegistry] = None,
    event_bus: Any = None,
    simulation_mode: bool = True,
) -> ConnectorRegistry:

    registry = registry or get_connector_registry()

    for tenant_id in tenant_ids:
        bootstrap_connectors(
            storage,
            registry=registry,
            event_bus=event_bus,
            tenant_id=tenant_id,
            simulation_mode=simulation_mode,
        )

    return registry


# ----------------------------------------------------------------------
# TELEMETRY
# ----------------------------------------------------------------------

def _emit_connector_bootstrap_event(
    event_bus: Any,
    *,
    event_type: str,
    tenant_id: str,
    connector_id: str,
    payload: Dict[str, Any],
    severity: str = "LOW",
) -> None:

    if event_bus is None:
        return

    try:
        event_bus.publish(
            event_type=event_type,
            tenant_id=tenant_id,
            source="connector_bootstrap",
            severity=severity,
            payload={
                "connector_id": connector_id,
                **payload,
            },
        )
    except TypeError:
        try:
            event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                payload={
                    "connector_id": connector_id,
                    **payload,
                },
            )
        except Exception:
            pass
    except Exception:
        pass