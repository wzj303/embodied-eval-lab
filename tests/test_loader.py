import json
from pathlib import Path

import pytest

from embodied_eval_lab.loader import EXPECTED_COLUMNS, load_jsonl_dataset


def write_jsonl(path: Path, records: list[dict]) -> None:
    lines = [json.dumps(record) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_record(step_id: int, done: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "episode_id": "ep_test",
        "step_id": step_id,
        "timestamp_s": step_id * 0.1,
        "instruction": "pick up the red cube",
        "joint_positions_rad": [0.0] * 6,
        "action": [0.1] * 6,
        "inference_latency_ms": 40.0,
        "done": done,
        "success": True if done else None,
        "image_path": None,
    }


def test_load_jsonl_dataset_returns_dataframe(tmp_path) -> None:
    dataset_path = tmp_path / "episode.jsonl"
    records = [
        make_record(step_id=0),
        make_record(step_id=1),
        make_record(step_id=2, done=True),
    ]

    write_jsonl(dataset_path, records)

    dataframe = load_jsonl_dataset(dataset_path)

    assert len(dataframe) == 3
    assert list(dataframe.columns) == EXPECTED_COLUMNS
    assert dataframe.loc[0, "episode_id"] == "ep_test"
    assert dataframe.loc[2, "done"] is True


def test_load_jsonl_dataset_preserves_list_fields(tmp_path) -> None:
    dataset_path = tmp_path / "episode.jsonl"
    write_jsonl(dataset_path, [make_record(step_id=0, done=True)])

    dataframe = load_jsonl_dataset(dataset_path)

    assert dataframe.loc[0, "joint_positions_rad"] == [0.0] * 6
    assert dataframe.loc[0, "action"] == [0.1] * 6


def test_load_jsonl_dataset_rejects_missing_file(tmp_path) -> None:
    dataset_path = tmp_path / "missing.jsonl"

    with pytest.raises(FileNotFoundError, match="Dataset file does not exist"):
        load_jsonl_dataset(dataset_path)


def test_load_jsonl_dataset_rejects_empty_file(tmp_path) -> None:
    dataset_path = tmp_path / "empty.jsonl"
    dataset_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Dataset file is empty"):
        load_jsonl_dataset(dataset_path)


def test_load_jsonl_dataset_rejects_missing_columns(tmp_path) -> None:
    dataset_path = tmp_path / "invalid.jsonl"
    write_jsonl(
        dataset_path,
        [
            {
                "episode_id": "ep_test",
                "step_id": 0,
            }
        ],
    )

    with pytest.raises(ValueError, match="Dataset file is missing columns"):
        load_jsonl_dataset(dataset_path)