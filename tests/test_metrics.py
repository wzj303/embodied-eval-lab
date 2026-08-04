import json

import pandas as pd
import pytest

from embodied_eval_lab.metrics import (
    calculate_evaluation_metrics,
    write_metrics_report,
)


def make_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "episode_id": "ep_1",
                "step_id": 0,
                "timestamp_s": 0.0,
                "inference_latency_ms": 10.0,
                "done": False,
                "success": None,
            },
            {
                "episode_id": "ep_1",
                "step_id": 1,
                "timestamp_s": 1.0,
                "inference_latency_ms": 20.0,
                "done": True,
                "success": True,
            },
            {
                "episode_id": "ep_2",
                "step_id": 0,
                "timestamp_s": 0.0,
                "inference_latency_ms": 30.0,
                "done": False,
                "success": None,
            },
            {
                "episode_id": "ep_2",
                "step_id": 1,
                "timestamp_s": 1.0,
                "inference_latency_ms": 40.0,
                "done": False,
                "success": None,
            },
            {
                "episode_id": "ep_2",
                "step_id": 2,
                "timestamp_s": 2.0,
                "inference_latency_ms": 50.0,
                "done": True,
                "success": False,
            },
        ]
    )


def test_calculate_evaluation_metrics() -> None:
    report = calculate_evaluation_metrics(make_dataframe())

    assert report["episode_count"] == 2
    assert report["total_step_count"] == 5
    assert report["success_count"] == 1
    assert report["success_rate"] == pytest.approx(0.5)
    assert report["average_steps_per_episode"] == pytest.approx(2.5)
    assert report["average_episode_duration_s"] == pytest.approx(1.5)
    assert report["mean_inference_latency_ms"] == pytest.approx(30.0)
    assert report["p95_inference_latency_ms"] == pytest.approx(48.0)


def test_calculate_evaluation_metrics_rejects_empty_data() -> None:
    with pytest.raises(
        ValueError,
        match="Cannot calculate metrics from an empty dataset",
    ):
        calculate_evaluation_metrics(pd.DataFrame())


def test_calculate_evaluation_metrics_rejects_missing_columns() -> None:
    dataframe = pd.DataFrame(
        [{"episode_id": "ep_1"}]
    )

    with pytest.raises(
        ValueError,
        match="Dataset is missing metric columns",
    ):
        calculate_evaluation_metrics(dataframe)


def test_calculate_evaluation_metrics_requires_terminal_record() -> None:
    dataframe = make_dataframe()
    dataframe.loc[dataframe["episode_id"] == "ep_2", "done"] = False

    with pytest.raises(
        ValueError,
        match="Each episode must contain exactly one terminal record",
    ):
        calculate_evaluation_metrics(dataframe)


def test_write_metrics_report(tmp_path) -> None:
    report = calculate_evaluation_metrics(make_dataframe())
    output_path = tmp_path / "reports" / "metrics.json"

    write_metrics_report(report, output_path)

    saved_report = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert saved_report == report