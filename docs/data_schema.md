# Embodied Experiment Data Schema

## Overview

Each line in a JSONL file represents one robot experiment step.

Schema version: `1.0`

## Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | string | Yes | Data schema version |
| `episode_id` | string | Yes | Unique experiment episode identifier |
| `step_id` | integer | Yes | Step number inside an episode |
| `timestamp_s` | float | Yes | Seconds since the episode started |
| `instruction` | string | Yes | Natural-language task instruction |
| `joint_positions_rad` | float array | Yes | Six robot joint positions in radians |
| `action` | float array | Yes | Six-dimensional action produced by the policy |
| `inference_latency_ms` | float | Yes | Model inference latency in milliseconds |
| `done` | boolean | Yes | Whether the episode has ended |
| `success` | boolean or null | Yes | Final task result |
| `image_path` | string or null | Yes | Associated image path |

## Constraints

1. `schema_version` is currently `1.0`.
2. `step_id` starts from `0`.
3. `step_id` increases by one inside each episode.
4. `timestamp_s` increases inside each episode.
5. `inference_latency_ms` must not be negative.
6. `joint_positions_rad` contains six numbers.
7. `action` contains six numbers.
8. When `done` is `false`, `success` must be `null`.
9. The final record must have `done=true`.
10. When `done` is `true`, `success` must be `true` or `false`.

## Storage Format

Experiment data is stored as JSONL: one complete JSON object per line.

JSONL is used because new robot records can be appended without loading or
rewriting the complete file.