# Changelog

## 0.1.0 - 2026-08-24

- Preserve the existing scaling-recommendation concept while adding explicit replica bounds and desired-replica output.
- Add policy validation, bounded scale steps, max/min enforcement, and mixed-signal hold behavior.
- Explicitly report that infrastructure is never mutated by this service.
- Add health/readiness endpoints, deterministic tests, modern Python dependencies, Ruff, pytest, pip-audit, Docker, non-root, and runtime smoke gates.
- Document recommendation-only security and production-controller responsibilities.
