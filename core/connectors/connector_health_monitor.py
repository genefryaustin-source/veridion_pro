"""
core/connectors/connector_health_monitor.py

Connector health monitoring system.

Tracks:
- failures
- retries
- latency
- auth issues
- degraded state
- outages
- failover recommendations
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


HEALTH_HEALTHY = "HEALTHY"
HEALTH_DEGRADED = "DEGRADED"
HEALTH_OUTAGE = "OUTAGE"


@dataclass
class ConnectorHealthState:
    connector_name: str

    health: str = HEALTH_HEALTHY

    success_count: int = 0
    failure_count: int = 0
    retry_count: int = 0

    avg_latency_ms: float = 0.0

    auth_failures: int = 0

    last_success_ms: Optional[int] = None
    last_failure_ms: Optional[int] = None

    outage_detected: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectorHealthMonitor:

    def __init__(self):
        self._lock = threading.RLock()

        self.states: Dict[str, ConnectorHealthState] = {}

    # ========================================================
    # STATE
    # ========================================================

    def get_state(
        self,
        connector_name: str,
    ) -> ConnectorHealthState:

        with self._lock:

            if connector_name not in self.states:

                self.states[connector_name] = ConnectorHealthState(
                    connector_name=connector_name,
                )

            return self.states[connector_name]

    # ========================================================
    # RECORDING
    # ========================================================

    def record_success(
        self,
        connector_name: str,
        latency_ms: float = 0.0,
    ) -> None:

        state = self.get_state(connector_name)

        state.success_count += 1
        state.last_success_ms = self._now()

        if state.avg_latency_ms <= 0:
            state.avg_latency_ms = latency_ms
        else:
            state.avg_latency_ms = (
                (state.avg_latency_ms * 0.8)
                + (latency_ms * 0.2)
            )

        state.health = HEALTH_HEALTHY
        state.outage_detected = False

    def record_failure(
        self,
        connector_name: str,
        error: str = "",
        auth_failure: bool = False,
    ) -> None:

        state = self.get_state(connector_name)

        state.failure_count += 1
        state.last_failure_ms = self._now()

        if auth_failure:
            state.auth_failures += 1

        if state.failure_count >= 5:
            state.health = HEALTH_DEGRADED

        if state.failure_count >= 15:
            state.health = HEALTH_OUTAGE
            state.outage_detected = True

            dispatch_event(
                "CONNECTOR_OUTAGE_DETECTED",
                {
                    "connector": connector_name,
                    "error": error,
                },
                source="connector_health_monitor",
            )

    def record_retry(
        self,
        connector_name: str,
    ) -> None:

        state = self.get_state(connector_name)
        state.retry_count += 1

    # ========================================================
    # READS
    # ========================================================

    def list_states(self):

        return list(self.states.values())

    def stats(self):

        healthy = 0
        degraded = 0
        outage = 0

        for s in self.states.values():

            if s.health == HEALTH_HEALTHY:
                healthy += 1

            elif s.health == HEALTH_DEGRADED:
                degraded += 1

            elif s.health == HEALTH_OUTAGE:
                outage += 1

        return {
            "healthy": healthy,
            "degraded": degraded,
            "outage": outage,
            "total": len(self.states),
        }

    # ========================================================
    # HELPERS
    # ========================================================

    def _now(self):

        return int(time.time() * 1000)


# ============================================================
# GLOBAL SINGLETON
# ============================================================

_monitor: Optional[ConnectorHealthMonitor] = None


def get_connector_health_monitor():

    global _monitor

    if _monitor is None:
        _monitor = ConnectorHealthMonitor()

    return _monitor