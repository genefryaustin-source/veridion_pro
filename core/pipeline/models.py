from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import time
import uuid


# -----------------------------------
# PIPELINE STAGES
# -----------------------------------
class PipelineStage(str, Enum):

    INGEST = "INGEST"

    EXTRACT = "EXTRACT"

    OCR = "OCR"

    DETECT = "DETECT"

    ENTITY_EXTRACT = "ENTITY_EXTRACT"

    RELATIONSHIP_BUILD = "RELATIONSHIP_BUILD"

    CASE_LINK = "CASE_LINK"

    CASE_HYDRATE = "CASE_HYDRATE"


# -----------------------------------
# PIPELINE STATUS
# -----------------------------------
class PipelineStatus(str, Enum):

    PENDING = "PENDING"

    PROCESSING = "PROCESSING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    RETRY = "RETRY"


# -----------------------------------
# PIPELINE JOB
# -----------------------------------
@dataclass
class PipelineJob:

    job_id: str

    stage: str

    status: str

    tenant_id: Optional[str] = None

    mailbox: Optional[str] = None

    case_id: Optional[str] = None

    evidence_id: Optional[str] = None

    alert_id: Optional[int] = None

    parent_job_id: Optional[str] = None

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    attempts: int = 0

    max_attempts: int = 5

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )

    updated_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


# -----------------------------------
# PIPELINE EVENT
# -----------------------------------
@dataclass
class PipelineEvent:

    event_id: str

    job_id: str

    stage: str

    status: str

    message: str

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


# -----------------------------------
# HELPERS
# -----------------------------------
def new_job_id():

    return uuid.uuid4().hex


def new_event_id():

    return uuid.uuid4().hex