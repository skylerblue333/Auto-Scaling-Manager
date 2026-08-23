"""Policy-based scaling recommendation service for SKYCOIN4444."""
from __future__ import annotations

import time
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Auto-Scaling-Manager", version="3.1.0")


class ScaleRequest(BaseModel):
    service: str = Field(min_length=1, max_length=200)
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)


class ScalingPolicy(BaseModel):
    cpu_up: float = Field(default=80, ge=0, le=100)
    memory_up: float = Field(default=85, ge=0, le=100)
    cpu_down: float = Field(default=20, ge=0, le=100)
    memory_down: float = Field(default=30, ge=0, le=100)


def recommend(req: ScaleRequest, policy: ScalingPolicy | None = None) -> str:
    policy = policy or ScalingPolicy()
    if req.cpu_percent >= policy.cpu_up or req.memory_percent >= policy.memory_up:
        return "scale_up"
    if req.cpu_percent <= policy.cpu_down and req.memory_percent <= policy.memory_down:
        return "scale_down"
    return "none"


@app.post("/api/v1/evaluate")
def evaluate_scaling(req: ScaleRequest):
    action = recommend(req)
    return {
        "service": req.service.strip(),
        "action": action,
        "cpu": req.cpu_percent,
        "memory": req.memory_percent,
        "policy": ScalingPolicy().model_dump(),
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Auto-Scaling-Manager", "timestamp": int(time.time())}
