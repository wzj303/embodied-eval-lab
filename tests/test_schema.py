import json
from pathlib import Path

from embodied_eval_lab.schema import ExperimentStep

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "sample" / "episode_001.jsonl"


def test_experiment_step_can_be_serialized() -> None:
    step = ExperimentStep(
        schema_version="1.0",
        episode_id="ep_test",
        step_id=0,
        timestamp_s=0.0,
        instruction="pick up the red cube",
        joint_positions_rad=[0.0] * 6,
        action=[0.1] * 6,
        inference_latency_ms=40.0,
        done=False,
        success=None,
        image_path=None,
    )

    payload = json.loads(step.to_json())

    assert payload["schema_version"] == "1.0"
    assert payload["episode_id"] == "ep_test"
    assert payload["step_id"] == 0
    assert payload["success"] is None
    assert len(payload["joint_positions_rad"]) == 6
    assert len(payload["action"]) == 6


def test_sample_jsonl_is_valid() -> None:
    lines = SAMPLE_PATH.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines if line.strip()]

    assert len(records) >= 3
    assert [record["step_id"] for record in records] == [0, 1, 2]
    assert records[0]["done"] is False
    assert records[0]["success"] is None
    assert records[-1]["done"] is True
    assert records[-1]["success"] is True