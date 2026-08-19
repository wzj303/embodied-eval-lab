# Embodied Eval Lab

[![CI](https://github.com/wzj303/embodied-eval-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/wzj303/embodied-eval-lab/actions/workflows/ci.yml)

Embodied Eval Lab is a small evaluation pipeline for simulated embodied-robot
experiments. It generates deterministic JSONL episodes, validates data
quality, calculates metrics, stores reports in SQLite, exposes results through
FastAPI, and displays them in a TypeScript dashboard.

## Architecture

```text
simulated episodes (JSONL)
        |
        v
loader -> validation -> metrics -> SQLite -> FastAPI -> dashboard
```

The Python package is under `src/embodied_eval_lab`, the dashboard is under
`frontend`, and the SQLite database is stored at `data/evaluation.db`.

Detailed implementation notes are in
[docs/development.md](docs/development.md). The record contract is documented
in [docs/data_schema.md](docs/data_schema.md).

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js 22 or newer and npm
- Docker Desktop with Docker Compose for the container workflow

## Local Setup

From the repository root:

```powershell
uv sync --locked --all-groups
cd frontend
npm ci
cd ..
```

## Data Pipeline

Generate deterministic simulated episodes:

```powershell
uv run python -m embodied_eval_lab.collector --episodes 3 --steps 20 --seed 42
```

The default output directory is `data/output`. Load and validate a dataset:

```python
from pathlib import Path

from embodied_eval_lab.loader import load_jsonl_dataset
from embodied_eval_lab.validation import validate_dataset

dataset = load_jsonl_dataset(Path("data/output/ep_0001.jsonl"))
quality_report = validate_dataset(dataset)

if not quality_report["is_valid"]:
    raise ValueError(quality_report)
```

Calculate and save metrics:

```python
from pathlib import Path

from embodied_eval_lab.metrics import (
    calculate_evaluation_metrics,
    write_metrics_report,
)

metrics = calculate_evaluation_metrics(dataset)
write_metrics_report(metrics, Path("reports/evaluation_metrics.json"))
```

Persist a report in SQLite:

```python
from pathlib import Path

from embodied_eval_lab.database import initialize_database, save_evaluation_run

database_path = Path("data/evaluation.db")
initialize_database(database_path)
run_id = save_evaluation_run(
    database_path=database_path,
    run_name="simulated-baseline",
    dataset_path=Path("data/output/ep_0001.jsonl"),
    report=metrics,
)
print(run_id)
```

## Run the API

```powershell
uv run fastapi dev src/embodied_eval_lab/api.py
```

The API is available at `http://127.0.0.1:8000`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/evaluation-runs` | List runs, newest first |
| `GET` | `/evaluation-runs/{run_id}` | Fetch one run |

Interactive API documentation: `http://127.0.0.1:8000/docs`.

## Run the Dashboard

In a second terminal:

```powershell
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`. The dashboard handles loading, empty, error,
and successful response states. Build production assets with:

```powershell
npm run build
```

## Run with Docker

```powershell
docker compose up -d --build
```

Open the dashboard at `http://127.0.0.1:5173`. The API and API documentation
are at `http://127.0.0.1:8000` and `http://127.0.0.1:8000/docs`.

Useful commands:

```powershell
docker compose ps
docker compose logs -f
docker compose down
```

Compose mounts the host `data` directory at `/app/data`, so SQLite data
survives container recreation.

## Quality Checks

These are the checks used by GitHub Actions:

```powershell
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
cd frontend
npm ci
npm run build
```

## Project Layout

```text
src/embodied_eval_lab/  Python package
tests/                   Python tests
frontend/                Vite and TypeScript dashboard
data/                    JSONL data and SQLite database
docs/                    Schema and developer documentation
.github/workflows/       Continuous integration
Dockerfile               FastAPI image
docker-compose.yml       Local multi-service runtime
```

## Contributing

1. Create a branch from `main`.
2. Keep changes focused on one issue.
3. Add or update tests for behavior changes.
4. Update relevant documentation.
5. Run the local quality checks.
6. Open a pull request with an issue reference such as `Closes #11`.

See [docs/development.md](docs/development.md) for development conventions,
data flow, Docker details, troubleshooting, and the pull request checklist.
