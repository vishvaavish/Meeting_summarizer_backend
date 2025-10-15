# app/services/huggingface.py
import httpx
import re
from ..config import settings

def _local_fallback_summary(text: str, max_sentences: int = 4) -> str:
    """
    Ultra-simple extractive summarizer:
    - Split into sentences
    - Score by term frequency
    - Return top N sentences ordered by their original position
    """
    # naive sentence split
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sents) <= max_sentences:
        return text.strip()

    # word frequencies (stopwords-light)
    words = re.findall(r"[A-Za-z0-9']+", text.lower())
    stop = set("""a an the and or but if then else when at by for from in into of on onto to with as is are was were be been being i you he she it we they them their our your this that these those not no""".split())
    freqs = {}
    for w in words:
        if w in stop or len(w) < 2:
            continue
        freqs[w] = freqs.get(w, 0) + 1

    def score(sent: str) -> int:
        return sum(freqs.get(w, 0) for w in re.findall(r"[A-Za-z0-9']+", sent.lower()))

    # score & pick top sentences, but preserve original order
    indexed = list(enumerate(sents))
    top = sorted(indexed, key=lambda kv: score(kv[1]), reverse=True)[:max_sentences]
    top_sorted = sorted(top, key=lambda kv: kv[0])
    return " ".join(s for _, s in top_sorted).strip()

async def summarize(text: str, max_length: int = 200, min_length: int = 60) -> str:
    """
    Try Hugging Face Inference API; on 401/missing key/network issues,
    return a local extractive summary so the job still completes.
    """
    key = settings.huggingface_api_key.strip() if settings.huggingface_api_key else ""
    model = settings.hf_summary_model

    if not key:
        return _local_fallback_summary(text)

    timeout = httpx.Timeout(settings.http_timeout_s)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": text,
        "parameters": {"max_length": max_length, "min_length": min_length, "do_sample": False},
        "options": {"wait_for_model": True},
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json=payload,
            )
            if r.status_code == 401:
                # invalid token or no access → fallback
                return _local_fallback_summary(text)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data and "summary_text" in data[0]:
                return data[0]["summary_text"]
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            # Unexpected payload → safe fallback
            return _local_fallback_summary(text)
    except Exception:
        # Network / 5xx / timeouts → fallback
        return _local_fallback_summary(text)
