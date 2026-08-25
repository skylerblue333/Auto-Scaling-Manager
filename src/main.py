"""Bounded scaling recommendation service with no infrastructure mutation."""
from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Sky Scaling Policy", version="0.1.0")


class ScaleRequest(BaseModel):
    service: str = Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    current_replicas: int = Field(default=1, ge=1, le=10_000)
    min_replicas: int = Field(default=1, ge=1, le=10_000)
    max_replicas: int = Field(default=100, ge=1, le=10_000)

    @model_validator(mode="after")
    def validate_replica_bounds(self) -> "ScaleRequest":
        if self.min_replicas > self.max_replicas:
            raise ValueError("min_replicas cannot exceed max_replicas")
        if not self.min_replicas <= self.current_replicas <= self.max_replicas:
            raise ValueError("current_replicas must be within min/max bounds")
        return self


class ScalingPolicy(BaseModel):
    cpu_up: float = Field(default=80, ge=1, le=100)
    memory_up: float = Field(default=85, ge=1, le=100)
    cpu_down: float = Field(default=20, ge=0, le=99)
    memory_down: float = Field(default=30, ge=0, le=99)
    scale_up_step: int = Field(default=1, ge=1, le=100)
    scale_down_step: int = Field(default=1, ge=1, le=100)

    @model_validator(mode="after")
    def validate_thresholds(self) -> "ScalingPolicy":
        if self.cpu_down >= self.cpu_up or self.memory_down >= self.memory_up:
            raise ValueError("down thresholds must be lower than up thresholds")
        return self


class ScalingDecision(BaseModel):
    service: str
    action: Literal["scale_up", "scale_down", "none"]
    current_replicas: int
    desired_replicas: int
    reason: str
    infrastructure_mutated: Literal[False] = False


def decide(req: ScaleRequest, policy: ScalingPolicy | None = None) -> ScalingDecision:
    policy = policy or ScalingPolicy()
    if req.cpu_percent >= policy.cpu_up or req.memory_percent >= policy.memory_up:
        desired = min(req.max_replicas, req.current_replicas + policy.scale_up_step)
        action: Literal["scale_up", "scale_down", "none"] = "scale_up" if desired > req.current_replicas else "none"
        reason = "upper utilization threshold reached" if action == "scale_up" else "already at max_replicas"
    elif req.cpu_percent <= policy.cpu_down and req.memory_percent <= policy.memory_down:
        desired = max(req.min_replicas, req.current_replicas - policy.scale_down_step)
        action = "scale_down" if desired < req.current_replicas else "none"
        reason = "both lower utilization thresholds reached" if action == "scale_down" else "already at min_replicas"
    else:
        desired = req.current_replicas
        action = "none"
        reason = "utilization remains inside policy band"

    return ScalingDecision(
        service=req.service,
        action=action,
        current_replicas=req.current_replicas,
        desired_replicas=desired,
        reason=reason,
    )


def recommend(req: ScaleRequest, policy: ScalingPolicy | None = None) -> str:
    """Backward-compatible action-only recommendation helper."""
    return decide(req, policy).action


@app.post("/api/v1/evaluate", response_model=ScalingDecision)
def evaluate_scaling(req: ScaleRequest) -> ScalingDecision:
    return decide(req)


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sky-scaling-policy"}


@app.get("/readyz")
def ready() -> dict[str, object]:
    return {"ready": True, "infrastructureMutationEnabled": False}


@app.get("/health")
def legacy_health() -> dict[str, str]:
    return health()
