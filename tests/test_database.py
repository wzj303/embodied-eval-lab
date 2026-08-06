import sqlite3

import pytest

from embodied_eval_lab.database import (
    get_evaluation_run,
    initialize_database,
    list_evaluation_runs,
    save_evaluation_run,
)


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


def test_initialize_database_creates_table(tmp_path) -> None:
    database_path = tmp_path / "nested" / "evaluation.db"

    initialize_database(database_path)
    initialize_database(database_path)

    connection = sqlite3.connect(database_path)

    try:
        table = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'evaluation_runs'
            """
        ).fetchone()
    finally:
        connection.close()

    assert database_path.exists()
    assert table is not None


def test_save_and_get_evaluation_run(tmp_path) -> None:
    database_path = tmp_path / "evaluation.db"
    initialize_database(database_path)

    run_id = save_evaluation_run(
        database_path=database_path,
        run_name="baseline",
        dataset_path=tmp_path / "episode.jsonl",
        report=make_report(),
    )

    saved_run = get_evaluation_run(database_path, run_id)

    assert saved_run is not None
    assert saved_run["id"] == run_id
    assert saved_run["run_name"] == "baseline"
    assert saved_run["success_rate"] == pytest.approx(0.5)
    assert saved_run["created_at"]


def test_list_evaluation_runs_newest_first(tmp_path) -> None:
    database_path = tmp_path / "evaluation.db"
    initialize_database(database_path)

    first_id = save_evaluation_run(
        database_path,
        "first",
        tmp_path / "first.jsonl",
        make_report(),
    )
    second_id = save_evaluation_run(
        database_path,
        "second",
        tmp_path / "second.jsonl",
        make_report(),
    )

    runs = list_evaluation_runs(database_path)

    assert [run["id"] for run in runs] == [second_id, first_id]


def test_get_evaluation_run_returns_none_for_missing_id(
    tmp_path,
) -> None:
    database_path = tmp_path / "evaluation.db"
    initialize_database(database_path)

    assert get_evaluation_run(database_path, 999) is None


def test_save_evaluation_run_rejects_missing_metrics(
    tmp_path,
) -> None:
    database_path = tmp_path / "evaluation.db"
    initialize_database(database_path)

    report = make_report()
    report.pop("success_rate")

    with pytest.raises(
        ValueError,
        match="Metrics report is missing fields",
    ):
        save_evaluation_run(
            database_path,
            "invalid",
            tmp_path / "invalid.jsonl",
            report,
        )


def test_database_rejects_invalid_success_rate(tmp_path) -> None:
    database_path = tmp_path / "evaluation.db"
    initialize_database(database_path)

    report = make_report()
    report["success_rate"] = 1.5

    with pytest.raises(sqlite3.IntegrityError):
        save_evaluation_run(
            database_path,
            "invalid",
            tmp_path / "invalid.jsonl",
            report,
        )