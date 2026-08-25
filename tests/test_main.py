from fastapi.testclient import TestClient

from src.main import ScaleRequest, ScalingPolicy, app, decide


def test_health_and_readiness() -> None:
    with TestClient(app) as client:
        assert client.get("/healthz").json()["status"] == "ok"
        ready = client.get("/readyz").json()
        assert ready["ready"] is True
        assert ready["infrastructureMutationEnabled"] is False


def test_scale_up_returns_bounded_desired_replicas() -> None:
    decision = decide(
        ScaleRequest(
            service="api",
            cpu_percent=90,
            memory_percent=70,
            current_replicas=3,
            min_replicas=2,
            max_replicas=4,
        ),
        ScalingPolicy(scale_up_step=2),
    )
    assert decision.action == "scale_up"
    assert decision.desired_replicas == 4
    assert decision.infrastructure_mutated is False


def test_does_not_scale_past_bounds() -> None:
    up = decide(
        ScaleRequest(service="api", cpu_percent=99, memory_percent=99, current_replicas=4, min_replicas=1, max_replicas=4)
    )
    assert up.action == "none"
    assert up.desired_replicas == 4

    down = decide(
        ScaleRequest(service="api", cpu_percent=1, memory_percent=1, current_replicas=2, min_replicas=2, max_replicas=10)
    )
    assert down.action == "none"
    assert down.desired_replicas == 2


def test_scale_down_requires_both_low_signals() -> None:
    low = decide(ScaleRequest(service="api", cpu_percent=10, memory_percent=15, current_replicas=3))
    assert low.action == "scale_down"
    assert low.desired_replicas == 2

    mixed = decide(ScaleRequest(service="api", cpu_percent=10, memory_percent=60, current_replicas=3))
    assert mixed.action == "none"
    assert mixed.desired_replicas == 3


def test_api_preserves_action_contract() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/evaluate",
            json={"service": "api", "cpu_percent": 90, "memory_percent": 70, "current_replicas": 2},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["action"] == "scale_up"
        assert payload["desired_replicas"] == 3
        assert payload["infrastructure_mutated"] is False


def test_invalid_replica_and_policy_ranges_fail() -> None:
    try:
        ScaleRequest(
            service="api",
            cpu_percent=50,
            memory_percent=50,
            current_replicas=5,
            min_replicas=6,
            max_replicas=10,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid replica bounds should fail")

    try:
        ScalingPolicy(cpu_down=80, cpu_up=80)
    except ValueError:
        pass
    else:
        raise AssertionError("overlapping thresholds should fail")
