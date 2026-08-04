from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "schema_version",
    "episode_id",
    "step_id",
    "timestamp_s",
    "instruction",
    "joint_positions_rad",
    "action",
    "inference_latency_ms",
    "done",
    "success",
    "image_path",
]


def load_jsonl_dataset(path: Path) -> pd.DataFrame:
    """Load robot experiment records from a JSONL file."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Dataset path is not a file: {path}")

    if path.stat().st_size == 0:
        raise ValueError(f"Dataset file is empty: {path}")

    dataframe = pd.read_json(path, lines=True)

    if dataframe.empty:
        raise ValueError(f"Dataset file has no records: {path}")

    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset file is missing columns: {missing_columns}"
        )

    return dataframe[EXPECTED_COLUMNS]