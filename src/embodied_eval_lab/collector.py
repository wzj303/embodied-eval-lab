import argparse
from collections.abc import Iterable, Iterator
from pathlib import Path

import numpy as np
from numpy.random import Generator

from embodied_eval_lab.schema import ExperimentStep

JOINT_COUNT = 6
SUCCESS_PROBABILITY = 0.8


def generate_episode(
    episode_id: str,
    instruction: str,
    steps: int,
    sample_hz: float,
    rng: Generator,
) -> Iterator[ExperimentStep]:
    """逐步生成一个模拟机器人实验。"""

    if steps <= 0:
        raise ValueError("steps must be greater than zero")

    if sample_hz <= 0:
        raise ValueError("sample_hz must be greater than zero")

    joint_positions = np.zeros(JOINT_COUNT, dtype=float)

    for step_id in range(steps):
        action = np.clip(
            joint_positions + rng.normal(0.0, 0.05, JOINT_COUNT),
            -np.pi,
            np.pi,
        )

        inference_latency_ms = max(
            0.0,
            float(rng.normal(40.0, 5.0)),
        )

        done = step_id == steps - 1
        success = (
            bool(rng.random() < SUCCESS_PROBABILITY)
            if done
            else None
        )

        yield ExperimentStep(
            schema_version="1.0",
            episode_id=episode_id,
            step_id=step_id,
            timestamp_s=round(step_id / sample_hz, 6),
            instruction=instruction,
            joint_positions_rad=joint_positions.tolist(),
            action=action.tolist(),
            inference_latency_ms=inference_latency_ms,
            done=done,
            success=success,
            image_path=None,
        )

        joint_positions = action


def write_episode(
    records: Iterable[ExperimentStep],
    output_path: Path,
) -> int:
    """把实验记录逐行写入JSONL文件。"""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0

    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(record.to_json() + "\n")
            count += 1

    return count


def build_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器。"""

    parser = argparse.ArgumentParser(
        description="Generate simulated embodied robot experiment data."
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/output"),
    )
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--sample-hz", type=float, default=10.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--instruction",
        default="pick up the red cube",
    )

    return parser


def main() -> None:
    """运行模拟数据采集器。"""

    args = build_parser().parse_args()
    rng = np.random.default_rng(args.seed)

    for episode_number in range(1, args.episodes + 1):
        episode_id = f"ep_{episode_number:04d}"
        output_path = args.output_dir / f"{episode_id}.jsonl"

        records = generate_episode(
            episode_id=episode_id,
            instruction=args.instruction,
            steps=args.steps,
            sample_hz=args.sample_hz,
            rng=rng,
        )

        record_count = write_episode(records, output_path)

        print(f"Wrote {record_count} records to {output_path}")


if __name__ == "__main__":
    main()