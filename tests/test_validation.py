import pandas as pd

from embodied_eval_lab.validation import validate_dataset


def make_dataframe(overrides: list[dict] | None = None) -> pd.DataFrame:
    records = [
        {
            "schema_version": "1.0",
            "episode_id": "ep_test",
            "step_id": 0,
            "timestamp_s": 0.0,
            "instruction": "pick up the red cube",
            "joint_positions_rad": [0.0] * 6,
            "action": [0.1] * 6,
            "inference_latency_ms": 40.0,
            "done": False,
            "success": None,
            "image_path": None,
        },
        {
            "schema_version": "1.0",
            "episode_id": "ep_test",
            "step_id": 1,
            "timestamp_s": 0.1,
            "instruction": "pick up the red cube",
            "joint_positions_rad": [0.0] * 6,
            "action": [0.1] * 6,
            "inference_latency_ms": 42.0,
            "done": True,
            "success": True,
            "image_path": None,
        },
    ]

    if overrides:
        for index, values in enumerate(overrides):
            records[index].update(values)

    return pd.DataFrame(records)


def test_validate_dataset_accepts_valid_data() -> None:
    report = validate_dataset(make_dataframe())

    assert report["is_valid"] is True
    assert report["error_count"] == 0


def test_validate_dataset_counts_missing_values() -> None:
    dataframe = make_dataframe([
        {"instruction": None},
    ])

    report = validate_dataset(dataframe)

    assert report["is_valid"] is False
    assert report["missing_value_count"] == 1


def test_validate_dataset_counts_negative_latency() -> None:
    dataframe = make_dataframe([
        {"inference_latency_ms": -1.0},
    ])

    report = validate_dataset(dataframe)

    assert report["is_valid"] is False
    assert report["negative_latency_count"] == 1


def test_validate_dataset_counts_invalid_joint_positions() -> None:
    dataframe = make_dataframe([
        {"joint_positions_rad": [0.0] * 5},
    ])

    report = validate_dataset(dataframe)

    assert report["is_valid"] is False
    assert report["invalid_joint_position_count"] == 1


def test_validate_dataset_counts_invalid_actions() -> None:
    dataframe = make_dataframe([
        {"action": [0.1] * 7},
    ])

    report = validate_dataset(dataframe)

    assert report["is_valid"] is False
    assert report["invalid_action_count"] == 1


def test_validate_dataset_counts_timestamp_errors() -> None:
    dataframe = make_dataframe([
        {},
        {"timestamp_s": 0.0},
    ])

    report = validate_dataset(dataframe)

    assert report["is_valid"] is False
    assert report["timestamp_error_count"] == 1


def test_validate_dataset_counts_success_before_done() -> None:
    dataframe = make_dataframe([
        {"done": False, "success": True},
    ])

    report = validate_dataset(dataframe)

    assert report["is_valid"] is False
    assert report["success_before_done_count"] == 1


def test_validate_dataset_counts_missing_final_success() -> None:
    dataframe = make_dataframe([
        {},
        {"done": True, "success": None},
    ])

    report = validate_dataset(dataframe)

    assert report["is_valid"] is False
    assert report["missing_final_success_count"] == 1