import pandas as pd

EXPECTED_VECTOR_LENGTH = 6

REQUIRED_NON_NULL_COLUMNS = [
    "schema_version",
    "episode_id",
    "step_id",
    "timestamp_s",
    "instruction",
    "joint_positions_rad",
    "action",
    "inference_latency_ms",
    "done",
]


def _is_valid_vector(value: object, expected_length: int) -> bool:
    return isinstance(value, list) and len(value) == expected_length


def validate_dataset(dataframe: pd.DataFrame) -> dict:
    """Validate loaded robot experiment records."""

    missing_value_count = int(
        dataframe[REQUIRED_NON_NULL_COLUMNS].isna().sum().sum()
    )

    negative_latency_count = int(
        (dataframe["inference_latency_ms"] < 0).sum()
    )

    invalid_joint_position_count = int(
        (~dataframe["joint_positions_rad"].apply(
            lambda value: _is_valid_vector(value, EXPECTED_VECTOR_LENGTH)
        )).sum()
    )

    invalid_action_count = int(
        (~dataframe["action"].apply(
            lambda value: _is_valid_vector(value, EXPECTED_VECTOR_LENGTH)
        )).sum()
    )

    timestamp_error_count = 0

    for _, episode in dataframe.groupby("episode_id"):
        timestamp_error_count += int(
            (episode["timestamp_s"].diff().dropna() <= 0).sum()
        )

    success_before_done_count = int(
        (
            dataframe["done"].eq(False)
            & dataframe["success"].notna()
        ).sum()
    )

    missing_final_success_count = int(
        (
            dataframe["done"].eq(True)
            & dataframe["success"].isna()
        ).sum()
    )

    error_count = (
        missing_value_count
        + negative_latency_count
        + invalid_joint_position_count
        + invalid_action_count
        + timestamp_error_count
        + success_before_done_count
        + missing_final_success_count
    )

    return {
        "is_valid": error_count == 0,
        "error_count": error_count,
        "missing_value_count": missing_value_count,
        "negative_latency_count": negative_latency_count,
        "invalid_joint_position_count": invalid_joint_position_count,
        "invalid_action_count": invalid_action_count,
        "timestamp_error_count": timestamp_error_count,
        "success_before_done_count": success_before_done_count,
        "missing_final_success_count": missing_final_success_count,
    }