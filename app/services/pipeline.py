# app/services/pipeline.py
import uuid
from pathlib import Path
from fastapi import BackgroundTasks
from ..memory import JOBS, JobRecord
from ..config import settings
from . import assemblyai as aai
from . import huggingface as hf
from .storage import save_artifact

async def _run_job(job_id: str):
    rec = JOBS[job_id]
    rec.status = "processing"

    try:
        # 1) Upload to AssemblyAI & create transcript
        audio_url = await aai.upload_audio(rec.audio_path)           # type: ignore[arg-type]
        transcript_id = await aai.create_transcript(audio_url)
        rec.transcript_id = transcript_id

        # 2) Poll for completion
        data = await aai.poll_transcript(
            transcript_id,
            poll_interval=settings.aai_poll_interval_s,
            max_wait=settings.aai_max_wait_s,
        )
        transcript_text = (data.get("text") or "").strip()
        if not transcript_text:
            raise RuntimeError("Empty transcript text")
        rec.transcript_text = transcript_text

        # 3) Summarize via Hugging Face
        summary_text = await hf.summarize(transcript_text)
        rec.summary_text = summary_text

        # 4) Save artifacts
        save_artifact(job_id, transcript=transcript_text, summary=summary_text)

        rec.status = "completed"

    except Exception as e:
        rec.status = "error"
        rec.error = str(e)

def create_job(audio_path: Path, *, background: BackgroundTasks) -> str:
    job_id = uuid.uuid4().hex
    JOBS[job_id] = JobRecord(job_id=job_id, status="queued", audio_path=str(audio_path))
    background.add_task(_run_job, job_id)
    return job_id
