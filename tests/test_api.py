from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from embodied_eval_lab.api import create_app
from embodied_eval_lab.database import save_evaluation_run


def make_report() -> dict[str, int | float]:
    return {
        "episode_count": 2,
        "total_step_count": 5,
        "success_count": 1,
        "success_rate": 0.5,
        "average_steps_per_episode": 2.5,
        "average_episode_duration_s": 1.5,
        "mean_inference_latency_ms": 30.0,
        "p95_inference_latency_ms": 48.0,
    }


@pytest.fixture
def api_client(
    tmp_path,
) -> Iterator[tuple[TestClient, int]]:
    database_path = tmp_path / "evaluation.db"
    app = create_app(database_path)

    run_id = save_evaluation_run(
        database_path=database_path,
        run_name="test-run",
        dataset_path=tmp_path / "episode.jsonl",
        report=make_report(),
    )

    with TestClient(app) as client:
        yield client, run_id


def test_health_check(
    api_client: tuple[TestClient, int],
) -> None:
    client, _ = api_client

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_evaluation_runs(
    api_client: tuple[TestClient, int],
) -> None:
    client, run_id = api_client

    response = client.get("/evaluation-runs")

    assert response.status_code == 200

    runs = response.json()

    assert len(runs) == 1
    assert runs[0]["id"] == run_id
    assert runs[0]["run_name"] == "test-run"


def test_get_evaluation_run(
    api_client: tuple[TestClient, int],
) -> None:
    client, run_id = api_client

    response = client.get(f"/evaluation-runs/{run_id}")

    assert response.status_code == 200

    run = response.json()

    assert run["id"] == run_id
    assert run["success_rate"] == pytest.approx(0.5)
    assert run["p95_inference_latency_ms"] == pytest.approx(48.0)


def test_get_evaluation_run_returns_404_for_missing_id(
    api_client: tuple[TestClient, int],
) -> None:
    client, _ = api_client

    response = client.get("/evaluation-runs/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Evaluation run not found"
    }


def test_get_evaluation_run_rejects_invalid_id(
    api_client: tuple[TestClient, int],
) -> None:
    client, _ = api_client

    response = client.get("/evaluation-runs/not-a-number")

    assert response.status_code == 422


def test_api_allows_dashboard_origin(
    api_client: tuple[TestClient, int],
) -> None:
    client, _ = api_client

    response = client.get(
        "/health",
        headers={"Origin": "http://127.0.0.1:5173"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "http://127.0.0.1:5173"
    )
