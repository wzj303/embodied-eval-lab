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