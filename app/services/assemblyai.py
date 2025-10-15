# app/services/assemblyai.py
from typing import Optional
import asyncio
import httpx
from pathlib import Path
from ..config import settings

AAI_API_URL = "https://api.assemblyai.com/v2"

async def upload_audio(filepath: str) -> str:
    """
    Upload the audio file as raw bytes using AsyncClient.
    Avoid passing a file object/iterator to AsyncClient to prevent
    'Attempted to send a sync request with an AsyncClient instance.'
    """
    path = Path(filepath)
    data = path.read_bytes()  # read fully; simplest + reliable

    headers = {
        "authorization": settings.assemblyai_api_key,
        "content-type": "application/octet-stream",
    }
    timeout = httpx.Timeout(settings.http_timeout_s)

    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(f"{AAI_API_URL}/upload", headers=headers, content=data)
        r.raise_for_status()
        return r.json()["upload_url"]

async def create_transcript(audio_url: str) -> str:
    headers = {
        "authorization": settings.assemblyai_api_key,
        "content-type": "application/json",
    }
    payload = {"audio_url": audio_url, "speaker_labels": False}
    timeout = httpx.Timeout(settings.http_timeout_s)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(f"{AAI_API_URL}/transcript", headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["id"]

async def poll_transcript(transcript_id: str, *, poll_interval: float, max_wait: int) -> dict:
    headers = {"authorization": settings.assemblyai_api_key}
    timeout = httpx.Timeout(settings.http_timeout_s)
    elapsed = 0.0
    async with httpx.AsyncClient(timeout=timeout) as client:
        while elapsed < max_wait:
            r = await client.get(f"{AAI_API_URL}/transcript/{transcript_id}", headers=headers)
            r.raise_for_status()
            data = r.json()
            status = data.get("status")
            if status == "completed":
                return data
            if status == "error":
                raise RuntimeError(f"AssemblyAI error: {data.get('error')}")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
    raise TimeoutError("AssemblyAI polling timed out")
