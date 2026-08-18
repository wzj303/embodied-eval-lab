from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from embodied_eval_lab.database import (
    get_evaluation_run,
    initialize_database,
    list_evaluation_runs,
)

DEFAULT_DATABASE_PATH = Path("data/evaluation.db")


class HealthResponse(BaseModel):
    status: str


class EvaluationRunResponse(BaseModel):
    id: int
    run_name: str
    dataset_path: str
    created_at: str
    episode_count: int
    total_step_count: int
    success_count: int
    success_rate: float
    average_steps_per_episode: float
    average_episode_duration_s: float
    mean_inference_latency_ms: float
    p95_inference_latency_ms: float


def create_app(database_path: Path) -> FastAPI:
    """Create an API application backed by one SQLite database."""

    initialize_database(database_path)

    app = FastAPI(
        title="Embodied Eval Lab API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/evaluation-runs",
        response_model=list[EvaluationRunResponse],
    )
    def list_evaluation_runs_endpoint(
    ) -> list[dict[str, int | float | str]]:
        return list_evaluation_runs(database_path)

    @app.get(
        "/evaluation-runs/{run_id}",
        response_model=EvaluationRunResponse,
    )
    def get_evaluation_run_endpoint(
        run_id: int,
    ) -> dict[str, int | float | str]:
        evaluation_run = get_evaluation_run(
            database_path,
            run_id,
        )

        if evaluation_run is None:
            raise HTTPException(
                status_code=404,
                detail="Evaluation run not found",
            )

        return evaluation_run

    return app


app = create_app(DEFAULT_DATABASE_PATH)
