import json

import numpy as np

from embodied_eval_lab.collector import generate_episode, write_episode


def test_generate_episode() -> None:
    rng = np.random.default_rng(42)

    records = list(
        generate_episode(
            episode_id="ep_test",
            instruction="pick up the red cube",
            steps=3,
            sample_hz=10.0,
            rng=rng,
        )
    )

    assert len(records) == 3
    assert [record.step_id for record in records] == [0, 1, 2]
    assert [record.timestamp_s for record in records] == [0.0, 0.1, 0.2]

    assert all(record.done is False for record in records[:-1])
    assert all(record.success is None for record in records[:-1])

    assert records[-1].done is True
    assert isinstance(records[-1].success, bool)

    assert all(len(record.joint_positions_rad) == 6 for record in records)
    assert all(len(record.action) == 6 for record in records)
    assert all(record.inference_latency_ms >= 0 for record in records)


def test_write_episode(tmp_path) -> None:
    rng = np.random.default_rng(42)
    output_path = tmp_path / "episode.jsonl"

    records = generate_episode(
        episode_id="ep_test",
        instruction="pick up the red cube",
        steps=3,
        sample_hz=10.0,
        rng=rng,
    )

    record_count = write_episode(records, output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]

    assert record_count == 3
    assert len(payloads) == 3
    assert payloads[0]["episode_id"] == "ep_test"
    assert payloads[-1]["done"] is True