"""
Auto-Scaling-Manager: Monitors service load and emits scale-up/scale-down recommendations
"""
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Auto-Scaling-Manager", version="3.0.0")

class ScaleRequest(BaseModel):
    service: str
    cpu_percent: float
    memory_percent: float

@app.post("/api/v1/evaluate")
def evaluate_scaling(req: ScaleRequest):
    action = "none"
    if req.cpu_percent > 80 or req.memory_percent > 85:
        action = "scale_up"
    elif req.cpu_percent < 20 and req.memory_percent < 30:
        action = "scale_down"
    return {"service": req.service, "action": action, "cpu": req.cpu_percent, "memory": req.memory_percent}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Auto-Scaling-Manager", "timestamp": int(time.time())}
