# Developer Guide

This guide explains how the repository is organized, how data moves through
the system, and how to develop and verify changes.

## System Boundaries

The project has a deliberately small set of boundaries:

1. The collector produces `ExperimentStep` records and writes JSONL files.
2. The loader converts one JSONL file into a pandas `DataFrame` and checks the
   required columns.
3. The validator checks record-level quality rules.
4. The metrics module aggregates validated records by episode.
5. The database module persists metric reports in SQLite.
6. FastAPI exposes read-only database queries to clients.
7. The TypeScript dashboard fetches those endpoints and renders the result.

Keeping these stages separate makes it possible to test data generation,
validation, metrics, storage, and HTTP behavior independently.

## Repository Layout

```text
src/embodied_eval_lab/
  collector.py       deterministic simulated episode generator
  schema.py          ExperimentStep dataclass and JSON serialization
  loader.py          JSONL to pandas DataFrame loader
  validation.py      data quality checks
  metrics.py         evaluation metric calculations and JSON export
  database.py        SQLite schema and persistence functions
  api.py             FastAPI application and response models

tests/
  test_collector.py
  test_schema.py
  test_loader.py
  test_validation.py
  test_metrics.py
  test_database.py
  test_api.py

frontend/src/
  api.ts             typed HTTP requests
  types.ts           API response types
  main.ts            dashboard state and rendering
  style.css          dashboard styles
```

## Development Environment

Install the exact locked dependency set:

```powershell
uv sync --locked --all-groups
```

The `dev` dependency group contains pytest, Ruff, and the HTTP client used by
FastAPI tests. Runtime dependencies are declared separately in
`pyproject.toml`.

The frontend uses the lockfile for reproducible installation:

```powershell
cd frontend
npm ci
```

Use `npm ci` in CI and clean environments. Use `npm install` only when
intentionally changing frontend dependencies and the lockfile.

## Data Flow

The normal evaluation flow is:

```text
collector.py
    -> data/output/*.jsonl
    -> loader.py
    -> validation.py
    -> metrics.py
    -> data/evaluation.db
    -> api.py
    -> frontend/src/api.ts
    -> frontend/src/main.ts
```

The collector uses a seeded NumPy random generator. A fixed seed makes a run
repeatable, which is useful for tests and debugging. The data schema is
defined in [data_schema.md](data_schema.md); changes to that contract should
update both the schema document and its tests.

## Database Rules

SQLite stores one row per evaluation run in the `evaluation_runs` table. The
database module creates the parent directory and table on initialization.

Writes use parameterized SQL and explicit transactions. Connections are
closed in `finally` blocks so errors do not leave file handles open. Database
`CHECK` constraints enforce basic metric invariants such as success rates
between `0` and `1`.

Tests use pytest's `tmp_path` fixture. Each test receives an isolated
temporary database, so tests cannot modify the developer's real
`data/evaluation.db`.

## API Contract

`create_app(database_path)` is the testable application factory. Production
startup uses the default `data/evaluation.db` path.

The API currently exposes read-only endpoints:

- `GET /health` returns `{ "status": "ok" }`.
- `GET /evaluation-runs` returns all runs in descending ID order.
- `GET /evaluation-runs/{run_id}` returns one run or HTTP 404.

The dashboard origins `http://127.0.0.1:5173` and
`http://localhost:5173` are allowed by CORS. The frontend currently calls
the API at `http://127.0.0.1:8000`.

When changing an endpoint, update the Pydantic response model, the API tests,
and the TypeScript type in `frontend/src/types.ts` together.

## Frontend States

The dashboard has four meaningful request states:

- Loading while the request is in progress.
- Empty when the API returns no evaluation runs.
- Error when the API is unavailable or returns an error.
- Success when metrics and run details can be rendered.

`frontend/src/api.ts` checks `response.ok` and parses JSON. `main.ts` owns
state transitions and rendering. User-controlled strings are escaped before
being inserted into HTML.

## Running the Complete Stack Locally

Start the API in one terminal:

```powershell
uv run fastapi dev src/embodied_eval_lab/api.py
```

Start the Vite development server in another:

```powershell
cd frontend
npm run dev
```

Use `http://127.0.0.1:5173` for the dashboard and
`http://127.0.0.1:8000/docs` to inspect the API.

## Running the Complete Stack with Docker

Build and start both services:

```powershell
docker compose up -d --build
```

The backend image installs only runtime Python dependencies. The frontend
image uses a Node build stage and a small Nginx runtime stage. Compose maps
host port `8000` to the API container and host port `5173` to Nginx.

Check service health and logs:

```powershell
docker compose ps
docker compose logs -f backend
```

The backend healthcheck requests `/health`. The frontend waits for the
backend to become healthy before it starts according to the Compose
dependency condition.

The host `data` directory is mounted into `/app/data`. Do not put the SQLite
database into the image or delete the data directory when testing container
recreation.

## Verification Checklist

Before opening a pull request, run:

```powershell
uv sync --locked --all-groups
uv run pytest
uv run ruff check .
cd frontend
npm ci
npm run build
cd ..
docker compose config
docker compose build
```

For API changes, verify:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/evaluation-runs
```

From WSL or another Bash shell, use `curl` instead:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/evaluation-runs
```

## Troubleshooting

### `uv` or `npm` is not recognized

The executable is not on the current shell's `PATH`. Open a new terminal or
use the executable's absolute path. In PowerShell, `npm.cmd` can be used when
PowerShell script execution policy blocks `npm.ps1`.

### Pytest reports `PermissionError` in a temporary directory

This is usually a Windows permission or locked-directory problem, not a test
assertion failure. Close processes using the directory and run pytest again
with a new writable temporary directory. CI runs on a clean Linux runner.

### Dashboard shows an API connection error

Confirm that the backend is running on port `8000`, then check `/health` and
the browser origin. For local development, run the API and Vite server in
separate terminals. For Docker, use `docker compose ps` and
`docker compose logs backend`.

### Docker cannot resolve a base image

This is a registry or network problem when Docker cannot fetch `python`,
`node`, or `nginx`. Check Docker Desktop's registry mirror or proxy settings,
then retry `docker pull` for the failed base image before rebuilding.

## Pull Requests

Use one branch per issue, keep commits focused, and include tests and docs
with behavior changes. The CI workflow must pass before merging. Reference
the issue in the pull request body, for example:

```text
Closes #11
```

After merge, verify that GitHub automatically closed the referenced issue.
