# Security Policy

Sky Scaling Policy is an engineering-beta recommendation service, not an infrastructure control plane.

The service validates bounded service identifiers, utilization percentages, replica ranges, and policy thresholds. It never receives or stores cloud credentials and does not call Kubernetes, AWS, Terraform, or other infrastructure APIs. Every decision explicitly reports `infrastructure_mutated: false`. The container runs as a non-root user and CI audits runtime dependencies.

Production controllers must independently authenticate requests, authorize target workloads, validate telemetry provenance, enforce cooldown/stabilization windows, quotas, budgets, rollout health, and provider-specific limits before applying any recommendation. This repository does not provide tenant isolation, secrets management, audit-log durability, HA, or production deployment controls.

Report suspected vulnerabilities privately through GitHub security reporting when available. Do not publish credentials, production topology, or working exploit details in public issues.
