import sqlite3
from pathlib import Path

METRIC_FIELDS = [
    "episode_count",
    "total_step_count",
    "success_count",
    "success_rate",
    "average_steps_per_episode",
    "average_episode_duration_s",
    "mean_inference_latency_ms",
    "p95_inference_latency_ms",
]

CREATE_EVALUATION_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_name TEXT NOT NULL,
    dataset_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    episode_count INTEGER NOT NULL CHECK (episode_count > 0),
    total_step_count INTEGER NOT NULL CHECK (total_step_count > 0),
    success_count INTEGER NOT NULL CHECK (success_count >= 0),
    success_rate REAL NOT NULL
        CHECK (success_rate >= 0 AND success_rate <= 1),
    average_steps_per_episode REAL NOT NULL
        CHECK (average_steps_per_episode > 0),
    average_episode_duration_s REAL NOT NULL
        CHECK (average_episode_duration_s >= 0),
    mean_inference_latency_ms REAL NOT NULL
        CHECK (mean_inference_latency_ms >= 0),
    p95_inference_latency_ms REAL NOT NULL
        CHECK (p95_inference_latency_ms >= 0),
    CHECK (success_count <= episode_count)
)
"""


def _connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def _validate_report(report: dict[str, int | float]) -> None:
    missing_fields = [
        field for field in METRIC_FIELDS
        if field not in report
    ]

    if missing_fields:
        raise ValueError(
            f"Metrics report is missing fields: {missing_fields}"
        )


def initialize_database(database_path: Path) -> None:
    """Create the database and required tables."""

    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = _connect(database_path)

    try:
        connection.execute(CREATE_EVALUATION_RUNS_TABLE)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def save_evaluation_run(
    database_path: Path,
    run_name: str,
    dataset_path: Path,
    report: dict[str, int | float],
) -> int:
    """Save one evaluation run and return its database ID."""

    if not run_name.strip():
        raise ValueError("Run name must not be empty")

    _validate_report(report)

    connection = _connect(database_path)

    try:
        cursor = connection.execute(
            """
            INSERT INTO evaluation_runs (
                run_name,
                dataset_path,
                episode_count,
                total_step_count,
                success_count,
                success_rate,
                average_steps_per_episode,
                average_episode_duration_s,
                mean_inference_latency_ms,
                p95_inference_latency_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_name,
                str(dataset_path),
                report["episode_count"],
                report["total_step_count"],
                report["success_count"],
                report["success_rate"],
                report["average_steps_per_episode"],
                report["average_episode_duration_s"],
                report["mean_inference_latency_ms"],
                report["p95_inference_latency_ms"],
            ),
        )

        run_id = cursor.lastrowid

        if run_id is None:
            raise RuntimeError("Database did not return a run ID")

        connection.commit()
        return int(run_id)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_evaluation_run(
    database_path: Path,
    run_id: int,
) -> dict[str, int | float | str] | None:
    """Retrieve one evaluation run by ID."""

    connection = _connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT *
            FROM evaluation_runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()
    finally:
        connection.close()

    return dict(row) if row is not None else None


def list_evaluation_runs(
    database_path: Path,
) -> list[dict[str, int | float | str]]:
    """List evaluation runs with the newest run first."""

    connection = _connect(database_path)

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM evaluation_runs
            ORDER BY id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return [dict(row) for row in rows]