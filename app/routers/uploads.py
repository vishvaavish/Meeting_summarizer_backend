# app/routers/uploads.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from starlette.responses import JSONResponse
from pathlib import Path
from ..services.storage import save_upload
from ..services.pipeline import create_job

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

@router.post("/audio")
async def upload_audio(background: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # naive suffix guard
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in [".mp3", ".wav", ".m4a", ".aac", ".mp4", ".webm"]:
            # allow common containers AssemblyAI supports
            pass

        content = await file.read()
        path = save_upload(content, suffix or ".bin")
        job_id = create_job(path, background=background)
        return JSONResponse({"ok": True, "job_id": job_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
