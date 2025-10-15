# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import uploads, jobs, meetings
# app/main.py
import os, logging
logging.getLogger("uvicorn.error").info(f"AAI key present: {bool(os.getenv('ASSEMBLYAI_API_KEY'))}")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads.router)
app.include_router(jobs.router)
app.include_router(meetings.router)

@app.get("/health")
def health():
    return {"ok": True}
