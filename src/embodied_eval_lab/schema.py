import json
from dataclasses import asdict, dataclass


@dataclass
class ExperimentStep:
    """机器人实验中一个时间步的数据。"""

    schema_version: str
    episode_id: str
    step_id: int
    timestamp_s: float
    instruction: str
    joint_positions_rad: list[float]
    action: list[float]
    inference_latency_ms: float
    done: bool
    success: bool | None
    image_path: str | None

    def to_json(self) -> str:
        """将当前记录转换成一行 JSON 字符串。"""
        return json.dumps(
            asdict(self),
            ensure_ascii=False,
            separators=(",", ":"),
        )