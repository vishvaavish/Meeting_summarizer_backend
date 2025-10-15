# app/config.py
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    assemblyai_api_key: str = os.getenv("ASSEMBLYAI_API_KEY", "")
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    hf_summary_model: str = os.getenv("HF_SUMMARY_MODEL", "facebook/bart-large-cnn")  # ← add
    port: int = int(os.getenv("PORT", "8000"))
    http_timeout_s: int = 60
    aai_poll_interval_s: float = 1.5
    aai_max_wait_s: int = 180


settings = Settings()
