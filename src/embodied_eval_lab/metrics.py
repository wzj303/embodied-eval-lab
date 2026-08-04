import json
from pathlib import Path

import pandas as pd

REQUIRED_METRIC_COLUMNS = [
    "episode_id",
    "step_id",
    "timestamp_s",
    "inference_latency_ms",
    "done",
    "success",
]


def calculate_evaluation_metrics(
    dataframe: pd.DataFrame,
) -> dict[str, int | float]:
    """Calculate evaluation metrics from validated experiment records."""

    if dataframe.empty:
        raise ValueError("Cannot calculate metrics from an empty dataset")

    missing_columns = [
        column
        for column in REQUIRED_METRIC_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset is missing metric columns: {missing_columns}"
        )

    episode_stats = dataframe.groupby("episode_id").agg(
        step_count=("step_id", "count"),
        start_timestamp_s=("timestamp_s", "min"),
        end_timestamp_s=("timestamp_s", "max"),
    )

    episode_count = len(episode_stats)

    terminal_records = dataframe.loc[
        dataframe["done"].eq(True),
        ["episode_id", "success"],
    ]

    terminal_counts = terminal_records.groupby("episode_id").size()

    if (
        len(terminal_counts) != episode_count
        or not terminal_counts.eq(1).all()
    ):
        raise ValueError(
            "Each episode must contain exactly one terminal record"
        )

    if terminal_records["success"].isna().any():
        raise ValueError(
            "Terminal records must contain a success value"
        )

    success_count = int(
        terminal_records["success"].eq(True).sum()
    )

    episode_durations = (
        episode_stats["end_timestamp_s"]
        - episode_stats["start_timestamp_s"]
    )

    total_step_count = int(episode_stats["step_count"].sum())

    latency = dataframe["inference_latency_ms"]

    return {
        "episode_count": int(episode_count),
        "total_step_count": total_step_count,
        "success_count": success_count,
        "success_rate": float(success_count / episode_count),
        "average_steps_per_episode": float(
            episode_stats["step_count"].mean()
        ),
        "average_episode_duration_s": float(
            episode_durations.mean()
        ),
        "mean_inference_latency_ms": float(latency.mean()),
        "p95_inference_latency_ms": float(
            latency.quantile(0.95)
        ),
    }


def write_metrics_report(
    report: dict[str, int | float],
    output_path: Path,
) -> None:
    """Write an evaluation metrics report to a JSON file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )