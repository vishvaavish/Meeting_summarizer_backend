# app/routers/jobs.py
from fastapi import APIRouter, HTTPException
from ..memory import JOBS

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/{job_id}")
async def get_job(job_id: str):
    rec = JOBS.get(job_id)
    if not rec:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "job_id": rec.job_id,
        "status": rec.status,
        "error": rec.error,
        "transcript_text": rec.transcript_text if rec.status == "completed" else None,
        "summary_text": rec.summary_text if rec.status == "completed" else None,
    }
