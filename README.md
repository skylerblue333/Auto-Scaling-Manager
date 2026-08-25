# Sky Scaling Policy

**Status: engineering beta.** A bounded FastAPI scaling-decision service that recommends replica changes from CPU/memory signals without mutating infrastructure.

## Implemented behavior

- validates bounded service identifiers and utilization percentages
- explicit current/min/max replica bounds
- configurable scale-up/down thresholds and step sizes
- rejects overlapping up/down threshold bands
- scales up when either upper utilization threshold is reached
- scales down only when both lower utilization thresholds are satisfied
- never recommends replicas outside configured min/max bounds
- explicitly reports `infrastructure_mutated: false`
- `/healthz` and `/readyz` operational endpoints
- tests for upper/lower bounds, mixed-signal hold behavior, invalid policies, and backward-compatible `action` output
- CI gates for compile, Ruff, pytest, runtime dependency audit, Docker build, non-root verification, and a real container health smoke test

## Example

```bash
curl -X POST http://127.0.0.1:8080/api/v1/evaluate \
  -H 'content-type: application/json' \
  -d '{"service":"api","cpu_percent":90,"memory_percent":70,"current_replicas":3,"min_replicas":2,"max_replicas":8}'
```

A recommendation may look like:

```json
{"service":"api","action":"scale_up","current_replicas":3,"desired_replicas":4,"reason":"upper utilization threshold reached","infrastructure_mutated":false}
```

## SKYCOIN4444 integration

Use this service as a policy/recommendation boundary for Kubernetes, ECS, EC2, workers, or other ecosystem workloads. A separately authenticated controller must decide whether to apply the recommendation and must enforce cooldown, rollout, quota, health, budget, and provider-specific safeguards.

## Explicit limitations

This repository does not call cloud APIs, change Kubernetes resources, hold AWS credentials, execute Terraform, or automatically scale infrastructure. It does not provide predictive autoscaling, queue-depth policies, SLO-aware decisions, cooldown history, stabilization windows, multi-metric time series, cost optimization, HA, or production deployment.

Single point-in-time CPU/memory values can be noisy. Production controllers should evaluate trusted aggregated telemetry and apply hysteresis/cooldown before infrastructure mutation.

See `SECURITY.md` and `CHANGELOG.md` for product and security boundaries.
