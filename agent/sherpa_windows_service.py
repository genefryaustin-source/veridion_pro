"""
agent/sherpa_windows_service.py

Sherpa Windows Endpoint Agent.

Purpose:
- local mailbox scanner hook
- local filesystem scanner
- process telemetry
- local Ollama inference hook
- evidence staging
- secure upload queue
- containment command listener
- GovCloud-ready endpoint reporting

Safety:
- destructive local actions disabled by default
- command listener requires signed/authorized commands later
- no cloud LLM usage
"""

from __future__ import annotations

import os
import re
import json
import time
import uuid
import queue
import hashlib
import logging
import platform
import threading
import traceback
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


try:
    import requests
except Exception:
    requests = None


try:
    import psutil
except Exception:
    psutil = None


# ============================================================
# CONSTANTS
# ============================================================

AGENT_NAME = "sherpa_windows_agent"

DEFAULT_DATA_DIR = Path(os.environ.get("PROGRAMDATA", ".")) / "Veridion" / "Sherpa"
DEFAULT_STAGE_DIR = DEFAULT_DATA_DIR / "staging"
DEFAULT_QUEUE_DIR = DEFAULT_DATA_DIR / "upload_queue"
DEFAULT_LOG_DIR = DEFAULT_DATA_DIR / "logs"

SCAN_EXTENSIONS = {
    ".txt",
    ".csv",
    ".json",
    ".xml",
    ".log",
    ".eml",
    ".msg",
    ".pdf",
    ".docx",
    ".xlsx",
}

CUI_TERMS = [
    "controlled unclassified information",
    "cui",
    "controlled technical information",
    "cti",
    "covered defense information",
    "cdi",
    "itar",
    "ear99",
    "export controlled",
    "export-control",
    "usml",
    "defense article",
    "defense service",
]


# ============================================================
# MODELS
# ============================================================

@dataclass
class SherpaConfig:
    tenant_id: str = "default"
    endpoint_id: str = field(default_factory=lambda: platform.node() or str(uuid.uuid4()))

    api_base_url: Optional[str] = None
    api_token: Optional[str] = None

    scan_paths: List[str] = field(default_factory=list)
    mailbox_scan_enabled: bool = False
    filesystem_scan_enabled: bool = True
    process_telemetry_enabled: bool = True
    ollama_enabled: bool = True

    ollama_url: str = "http://127.0.0.1:11434/api/generate"
    ollama_model: str = "llama3"

    poll_interval_seconds: int = 30
    scan_interval_seconds: int = 300
    upload_interval_seconds: int = 60

    destructive_actions_enabled: bool = False
    dry_run: bool = True


@dataclass
class EvidenceItem:
    evidence_id: str
    tenant_id: str
    endpoint_id: str
    source_path: str
    sha256: str
    size_bytes: int
    detected_terms: List[str]
    created_at_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SherpaCommand:
    command_id: str
    command_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    received_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


# ============================================================
# SERVICE
# ============================================================

class SherpaWindowsService:
    def __init__(self, config: Optional[SherpaConfig] = None):
        self.config = config or SherpaConfig()

        self.data_dir = DEFAULT_DATA_DIR
        self.stage_dir = DEFAULT_STAGE_DIR
        self.queue_dir = DEFAULT_QUEUE_DIR
        self.log_dir = DEFAULT_LOG_DIR

        self.stop_event = threading.Event()
        self.command_queue: "queue.Queue[SherpaCommand]" = queue.Queue()

        self._ensure_dirs()
        self._setup_logging()

    # ========================================================
    # SETUP
    # ========================================================

    def _ensure_dirs(self) -> None:
        for path in [
            self.data_dir,
            self.stage_dir,
            self.queue_dir,
            self.log_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> None:
        log_path = self.log_dir / "sherpa.log"

        logging.basicConfig(
            filename=str(log_path),
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

        logging.info("Sherpa initialized")

    # ========================================================
    # LIFECYCLE
    # ========================================================

    def start(self) -> None:
        logging.info("Starting Sherpa Windows Agent")

        workers = [
            threading.Thread(target=self._scan_loop, daemon=True),
            threading.Thread(target=self._upload_loop, daemon=True),
            threading.Thread(target=self._command_poll_loop, daemon=True),
            threading.Thread(target=self._command_worker_loop, daemon=True),
        ]

        for worker in workers:
            worker.start()

        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        logging.info("Stopping Sherpa Windows Agent")
        self.stop_event.set()

    # ========================================================
    # SCANNING
    # ========================================================

    def _scan_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                if self.config.filesystem_scan_enabled:
                    self.scan_filesystem()

                if self.config.process_telemetry_enabled:
                    self.collect_process_telemetry()

            except Exception:
                logging.error("Scan loop error: %s", traceback.format_exc())

            self.stop_event.wait(self.config.scan_interval_seconds)

    def scan_filesystem(self) -> List[EvidenceItem]:
        results: List[EvidenceItem] = []

        paths = self.config.scan_paths or [
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Downloads"),
        ]

        for base in paths:
            base_path = Path(base)

            if not base_path.exists():
                continue

            for file_path in base_path.rglob("*"):
                if self.stop_event.is_set():
                    break

                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() not in SCAN_EXTENSIONS:
                    continue

                try:
                    item = self.inspect_file(file_path)
                    if item:
                        self.stage_evidence(item)
                        results.append(item)

                except Exception:
                    logging.warning("File inspection failed %s: %s", file_path, traceback.format_exc())

        return results

    def inspect_file(self, file_path: Path) -> Optional[EvidenceItem]:
        size = file_path.stat().st_size

        if size <= 0:
            return None

        if size > 25 * 1024 * 1024:
            return None

        raw = file_path.read_bytes()
        sha256 = hashlib.sha256(raw).hexdigest()

        text = self._safe_decode(raw)
        detected_terms = self.detect_sensitive_terms(text)

        if not detected_terms:
            return None

        evidence_id = str(uuid.uuid4())

        metadata = {
            "filename": file_path.name,
            "extension": file_path.suffix.lower(),
            "host": platform.node(),
            "platform": platform.platform(),
            "ollama_summary": None,
        }

        if self.config.ollama_enabled:
            metadata["ollama_summary"] = self.analyze_with_ollama(text[:8000])

        return EvidenceItem(
            evidence_id=evidence_id,
            tenant_id=self.config.tenant_id,
            endpoint_id=self.config.endpoint_id,
            source_path=str(file_path),
            sha256=sha256,
            size_bytes=size,
            detected_terms=detected_terms,
            created_at_ms=int(time.time() * 1000),
            metadata=metadata,
        )

    def detect_sensitive_terms(self, text: str) -> List[str]:
        lower = text.lower()
        return sorted({term for term in CUI_TERMS if term in lower})

    def _safe_decode(self, raw: bytes) -> str:
        for enc in ("utf-8", "utf-16", "latin-1"):
            try:
                return raw.decode(enc, errors="ignore")
            except Exception:
                continue
        return ""

    # ========================================================
    # PROCESS TELEMETRY
    # ========================================================

    def collect_process_telemetry(self) -> None:
        if psutil is None:
            return

        rows = []

        for proc in psutil.process_iter(["pid", "name", "username", "cmdline"]):
            try:
                info = proc.info
                rows.append(
                    {
                        "pid": info.get("pid"),
                        "name": info.get("name"),
                        "username": info.get("username"),
                        "cmdline": info.get("cmdline"),
                    }
                )
            except Exception:
                continue

        payload = {
            "event_type": "PROCESS_TELEMETRY",
            "tenant_id": self.config.tenant_id,
            "endpoint_id": self.config.endpoint_id,
            "created_at_ms": int(time.time() * 1000),
            "process_count": len(rows),
            "processes": rows[:500],
        }

        self.stage_payload("process_telemetry", payload)

    # ========================================================
    # OLLAMA
    # ========================================================

    def analyze_with_ollama(self, text: str) -> Optional[Dict[str, Any]]:
        if not self.config.ollama_enabled or requests is None:
            return None

        prompt = (
            "Analyze this local endpoint text for CUI, export-control, ITAR, "
            "EAR, controlled technical information, or sensitive government data. "
            "Return a concise JSON-like assessment with risk, categories, and rationale.\n\n"
            f"{text[:8000]}"
        )

        try:
            response = requests.post(
                self.config.ollama_url,
                json={
                    "model": self.config.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )

            if response.status_code >= 300:
                return {"error": response.text}

            data = response.json()

            return {
                "model": self.config.ollama_model,
                "response": data.get("response"),
            }

        except Exception:
            return {"error": traceback.format_exc()}

    # ========================================================
    # STAGING / UPLOAD QUEUE
    # ========================================================

    def stage_evidence(self, item: EvidenceItem) -> None:
        evidence_path = self.stage_dir / f"{item.evidence_id}.json"

        evidence_path.write_text(
            json.dumps(item.__dict__, indent=2, default=str),
            encoding="utf-8",
        )

        queue_path = self.queue_dir / f"{item.evidence_id}.json"

        queue_path.write_text(
            json.dumps(
                {
                    "type": "evidence",
                    "path": str(evidence_path),
                    "tenant_id": item.tenant_id,
                    "endpoint_id": item.endpoint_id,
                    "evidence_id": item.evidence_id,
                    "created_at_ms": item.created_at_ms,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        logging.info("Evidence staged: %s", item.evidence_id)

    def stage_payload(self, name: str, payload: Dict[str, Any]) -> None:
        payload_id = str(uuid.uuid4())
        path = self.stage_dir / f"{name}_{payload_id}.json"

        path.write_text(
            json.dumps(payload, indent=2, default=str),
            encoding="utf-8",
        )

        queue_path = self.queue_dir / f"{name}_{payload_id}.json"

        queue_path.write_text(
            json.dumps(
                {
                    "type": name,
                    "path": str(path),
                    "tenant_id": self.config.tenant_id,
                    "endpoint_id": self.config.endpoint_id,
                    "created_at_ms": int(time.time() * 1000),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def _upload_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                self.flush_upload_queue()
            except Exception:
                logging.error("Upload loop error: %s", traceback.format_exc())

            self.stop_event.wait(self.config.upload_interval_seconds)

    def flush_upload_queue(self) -> None:
        if not self.config.api_base_url or not self.config.api_token or requests is None:
            return

        for item_path in list(self.queue_dir.glob("*.json")):
            try:
                queue_item = json.loads(item_path.read_text(encoding="utf-8"))
                payload_path = Path(queue_item["path"])

                if not payload_path.exists():
                    item_path.unlink(missing_ok=True)
                    continue

                payload = json.loads(payload_path.read_text(encoding="utf-8"))

                response = requests.post(
                    f"{self.config.api_base_url.rstrip('/')}/api/sherpa/upload",
                    headers={
                        "Authorization": f"Bearer {self.config.api_token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30,
                )

                if response.status_code < 300:
                    item_path.unlink(missing_ok=True)
                    logging.info("Uploaded queue item: %s", item_path.name)
                else:
                    logging.warning("Upload failed %s: %s", item_path.name, response.text)

            except Exception:
                logging.error("Queue flush failed %s: %s", item_path, traceback.format_exc())

    # ========================================================
    # COMMAND POLLING
    # ========================================================

    def _command_poll_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                self.poll_commands()
            except Exception:
                logging.error("Command poll error: %s", traceback.format_exc())

            self.stop_event.wait(self.config.poll_interval_seconds)

    def poll_commands(self) -> None:
        if not self.config.api_base_url or not self.config.api_token or requests is None:
            return

        response = requests.get(
            f"{self.config.api_base_url.rstrip('/')}/api/sherpa/commands",
            headers={
                "Authorization": f"Bearer {self.config.api_token}",
            },
            params={
                "tenant_id": self.config.tenant_id,
                "endpoint_id": self.config.endpoint_id,
            },
            timeout=30,
        )

        if response.status_code >= 300:
            logging.warning("Command poll failed: %s", response.text)
            return

        data = response.json()

        for raw in data.get("commands", []):
            command = SherpaCommand(
                command_id=raw.get("command_id") or str(uuid.uuid4()),
                command_type=raw.get("command_type"),
                payload=raw.get("payload") or {},
            )
            self.command_queue.put(command)

    def _command_worker_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                command = self.command_queue.get(timeout=1)
                self.handle_command(command)
            except queue.Empty:
                continue
            except Exception:
                logging.error("Command worker error: %s", traceback.format_exc())

    # ========================================================
    # COMMAND HANDLERS
    # ========================================================

    def handle_command(self, command: SherpaCommand) -> Dict[str, Any]:
        logging.info("Handling command: %s", command.command_type)

        handlers = {
            "scan_now": self.command_scan_now,
            "collect_processes": self.command_collect_processes,
            "quarantine_file": self.command_quarantine_file,
            "delete_file": self.command_delete_file,
            "kill_process": self.command_kill_process,
        }

        handler = handlers.get(command.command_type)

        if not handler:
            result = {
                "success": False,
                "error": "unknown_command",
                "command_id": command.command_id,
            }
        else:
            result = handler(command.payload)
            result["command_id"] = command.command_id

        self.stage_payload("command_result", result)
        return result

    def command_scan_now(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        results = self.scan_filesystem()
        return {
            "success": True,
            "action": "scan_now",
            "evidence_count": len(results),
        }

    def command_collect_processes(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.collect_process_telemetry()
        return {
            "success": True,
            "action": "collect_processes",
        }

    def command_quarantine_file(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = Path(payload.get("path", ""))

        if not path.exists():
            return {"success": False, "error": "file_not_found"}

        quarantine_dir = self.data_dir / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)

        target = quarantine_dir / f"{uuid.uuid4()}_{path.name}"

        if self.config.dry_run or not self.config.destructive_actions_enabled:
            return {
                "success": True,
                "dry_run": True,
                "action": "quarantine_file",
                "source": str(path),
                "target": str(target),
            }

        path.rename(target)

        return {
            "success": True,
            "action": "quarantine_file",
            "source": str(path),
            "target": str(target),
        }

    def command_delete_file(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = Path(payload.get("path", ""))

        if not path.exists():
            return {"success": False, "error": "file_not_found"}

        if self.config.dry_run or not self.config.destructive_actions_enabled:
            return {
                "success": True,
                "dry_run": True,
                "action": "delete_file",
                "path": str(path),
            }

        path.unlink()

        return {
            "success": True,
            "action": "delete_file",
            "path": str(path),
        }

    def command_kill_process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pid = payload.get("pid")

        if not pid:
            return {"success": False, "error": "missing_pid"}

        if self.config.dry_run or not self.config.destructive_actions_enabled:
            return {
                "success": True,
                "dry_run": True,
                "action": "kill_process",
                "pid": pid,
            }

        if psutil is None:
            return {"success": False, "error": "psutil_unavailable"}

        proc = psutil.Process(int(pid))
        proc.terminate()

        return {
            "success": True,
            "action": "kill_process",
            "pid": pid,
        }


# ============================================================
# CONFIG LOADER
# ============================================================

def load_config(path: str = "sherpa_config.json") -> SherpaConfig:
    config_path = Path(path)

    if not config_path.exists():
        return SherpaConfig()

    data = json.loads(config_path.read_text(encoding="utf-8"))
    return SherpaConfig(**data)


def main() -> None:
    config = load_config()
    service = SherpaWindowsService(config)
    service.start()


if __name__ == "__main__":
    main()