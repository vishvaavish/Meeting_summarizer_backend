# app/memory.py
from typing import Dict, Literal, Optional
from dataclasses import dataclass, field
from datetime import datetime

JobStatus = Literal["queued", "processing", "completed", "error"]

@dataclass
class JobRecord:
    job_id: str
    status: JobStatus
    error: Optional[str] = None
    audio_path: Optional[str] = None
    transcript_id: Optional[str] = None  # AssemblyAI
    transcript_text: Optional[str] = None
    summary_text: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

JOBS: Dict[str, JobRecord] = {}
MEETINGS_INDEX: Dict[str, dict] = {}  # id -> metadata for /meetings listing
