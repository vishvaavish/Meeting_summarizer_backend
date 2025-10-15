# app/routers/meetings.py
from fastapi import APIRouter
from pathlib import Path
from ..memory import JOBS

router = APIRouter(prefix="/api/meetings", tags=["meetings"])

@router.get("")
async def list_meetings():
    # expose completed jobs as meetings
    meetings = []
    for j in JOBS.values():
        if j.status == "completed":
            meetings.append({
                "id": j.job_id,
                "title": f"Meeting {j.job_id[:6]}",
                "summary": j.summary_text,
            })
    return {"meetings": meetings}

@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str):
    j = JOBS.get(meeting_id)
    if not j or j.status != "completed":
        return {"id": meeting_id, "status": j.status if j else "missing"}
    return {
        "id": j.job_id,
        "transcript": j.transcript_text,
        "summary": j.summary_text,
    }
