"""Safe Grok-style reply helper for Streamlit app.

This module lazily loads a text-generation pipeline. By default it uses a
lightweight model (`gpt2`) to avoid OOMs on local machines. To use a larger
model set the `GROK_MODEL` environment variable (and ensure you have the
hardware / tokens needed).
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests

app = FastAPI()
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
DEFAULT_MODEL = os.environ.get("GROK_MODEL", "gpt2")


class GenRequest(BaseModel):
    model: str | None = None
    prompt: str


def call_hf(model: str, prompt: str):
    if not HF_API_TOKEN:
        raise RuntimeError("HF_API_TOKEN not set")
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 150, "do_sample": True}}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    # parse similar to previous logic...
    if isinstance(data, list) and data:
        return data[0].get("generated_text") or str(data[0])
    if isinstance(data, dict):
        return data.get("generated_text") or str(data)
    return str(data)


# Optional: lazy load local pipeline when available
try:
    from transformers import pipeline

    _LOCAL = True
    _pipe = None

    def local_generate(model, prompt):
        global _pipe
        if _pipe is None:
            _pipe = pipeline("text-generation", model=model or DEFAULT_MODEL)
        out = _pipe(prompt, max_new_tokens=150, do_sample=True)[0].get("generated_text", "")
        return out

except Exception:
    _LOCAL = False


@app.post("/generate")
def generate(req: GenRequest):
    model = req.model or DEFAULT_MODEL
    prompt = req.prompt
    # try local
    if _LOCAL:
        try:
            return {"text": local_generate(model, prompt)}
        except Exception:
            pass
    # fallback to HF
    if HF_API_TOKEN:
        try:
            return {"text": call_hf(model, prompt)}
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))
    raise HTTPException(status_code=503, detail="No backend available (local transformers or HF token).")


FROM python:3.11-slim
WORKDIR /app
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt
COPY api_server.py .
EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]