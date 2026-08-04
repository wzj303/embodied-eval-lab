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