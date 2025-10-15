# app/services/storage.py
from pathlib import Path
from typing import Tuple
import uuid
import json
from datetime import datetime

UPLOADS_DIR = Path("uploads")
ARTIFACTS_DIR = Path("artifacts")
UPLOADS_DIR.mkdir(exist_ok=True, parents=True)
ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)

def save_upload(content: bytes, suffix: str) -> Path:
    name = f"{uuid.uuid4().hex}{suffix}"
    path = UPLOADS_DIR / name
    path.write_bytes(content)
    return path

def save_artifact(job_id: str, *, transcript: str, summary: str) -> Tuple[Path, Path]:
    ts = datetime.utcnow().isoformat()
    tpath = ARTIFACTS_DIR / f"{job_id}.transcript.txt"
    spath = ARTIFACTS_DIR / f"{job_id}.summary.txt"
    meta  = ARTIFACTS_DIR / f"{job_id}.json"
    tpath.write_text(transcript, encoding="utf-8")
    spath.write_text(summary,   encoding="utf-8")
    meta.write_text(json.dumps({"job_id": job_id, "created_at": ts}), encoding="utf-8")
    return tpath, spath
