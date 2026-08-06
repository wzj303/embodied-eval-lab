## Data schema

Experiment records use the JSONL format.

See [docs/data-schema.md](docs/data-schema.md) for field definitions,
constraints and examples.


## Generate simulated data

Generate three simulated robot episodes:

```powershell
uv run python -m embodied_eval_lab.collector --episodes 3 --steps 20
```

## Load JSONL datasets

Load robot experiment records from a JSONL file into a pandas DataFrame:

```python
from pathlib import Path

from embodied_eval_lab.loader import load_jsonl_dataset

dataset = load_jsonl_dataset(Path("data/output/ep_0001.jsonl"))

print(dataset.head())
print(dataset.columns)
```

## Validate dataset quality

Validate a loaded dataset and generate a data quality report:

```python
from pathlib import Path

from embodied_eval_lab.loader import load_jsonl_dataset
from embodied_eval_lab.validation import validate_dataset

dataset = load_jsonl_dataset(Path("data/output/ep_0001.jsonl"))
report = validate_dataset(dataset)

print(report)
```


## Calculate evaluation metrics

Calculate evaluation metrics from a validated dataset and export them as JSON:

```python
from pathlib import Path

from embodied_eval_lab.loader import load_jsonl_dataset
from embodied_eval_lab.metrics import (
    calculate_evaluation_metrics,
    write_metrics_report,
)
from embodied_eval_lab.validation import validate_dataset

dataset = load_jsonl_dataset(Path("data/output/ep_0001.jsonl"))
quality_report = validate_dataset(dataset)

if not quality_report["is_valid"]:
    raise ValueError(f"Dataset validation failed: {quality_report}")

metrics = calculate_evaluation_metrics(dataset)
write_metrics_report(
    metrics,
    Path("reports/evaluation_metrics.json"),
)

print(metrics)
```

## Persist evaluation reports

Store evaluation metrics in SQLite and retrieve them later:

```python
from pathlib import Path

from embodied_eval_lab.database import (
    get_evaluation_run,
    initialize_database,
    save_evaluation_run,
)
from embodied_eval_lab.loader import load_jsonl_dataset
from embodied_eval_lab.metrics import calculate_evaluation_metrics
from embodied_eval_lab.validation import validate_dataset

dataset_path = Path("data/output/ep_0001.jsonl")
database_path = Path("data/evaluation.db")

dataset = load_jsonl_dataset(dataset_path)
quality_report = validate_dataset(dataset)

if not quality_report["is_valid"]:
    raise ValueError(f"Dataset validation failed: {quality_report}")

metrics = calculate_evaluation_metrics(dataset)

initialize_database(database_path)

run_id = save_evaluation_run(
    database_path=database_path,
    run_name="simulated-baseline",
    dataset_path=dataset_path,
    report=metrics,
)

saved_run = get_evaluation_run(database_path, run_id)
print(saved_run)
```