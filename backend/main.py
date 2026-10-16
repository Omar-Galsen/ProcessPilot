import os
import math
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()
app = FastAPI(title="ProcessPilot AI")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str = ""

class PipeRequest(BaseModel):
    length_m: float = Field(gt=0)
    diameter_m: float = Field(gt=0)
    velocity_m_s: float = Field(ge=0)
    density_kg_m3: float = Field(gt=0)
    viscosity_pa_s: float = Field(gt=0)
    roughness_m: float = Field(default=0, ge=0)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/calculate/pipe")
def calculate_pipe(p: PipeRequest):
    re = p.density_kg_m3 * p.velocity_m_s * p.diameter_m / p.viscosity_pa_s
    if re == 0:
        f = 0
    elif re < 2300:
        f = 64 / re
    else:
        f = (-1.8 * math.log10((p.roughness_m / p.diameter_m / 3.7) ** 1.11 + 6.9 / re)) ** -2
    dp = f * p.length_m / p.diameter_m * p.density_kg_m3 * p.velocity_m_s**2 / 2
    return {"reynolds": round(re, 2), "darcy_friction_factor": round(f, 6), "pressure_drop_pa": round(dp, 2), "note": "Educational estimate for straight-pipe friction only; transitional flow and fittings require further analysis."}

@app.post("/chat")
async def chat(p: ChatRequest):
    key = os.getenv("DIFY_API_KEY")
    if not key or key.startswith("replace-"):
        raise HTTPException(503, "Configure DIFY_API_KEY")
    base = os.getenv("DIFY_BASE_URL", "http://localhost/v1").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{base}/chat-messages", headers={"Authorization": f"Bearer {key}"}, json={"inputs": {}, "query": p.question, "response_mode": "blocking", "conversation_id": p.conversation_id, "user": "local-demo"})
            response.raise_for_status()
            data = response.json()
            return {"answer": data.get("answer", ""), "conversation_id": data.get("conversation_id", "")}
    except httpx.HTTPError:
        raise HTTPException(502, "Dify service unavailable")

# Serve the web app and API from the same public origin.
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/diagnostics/dify")
def dify_diagnostics():
    """Return non-secret configuration status for deployment troubleshooting."""
    key = os.getenv("DIFY_API_KEY", "").strip()
    return {
        "key_configured": bool(key) and not key.startswith("replace-"),
        "base_url_configured": bool(os.getenv("DIFY_BASE_URL", "").strip()),
    }
