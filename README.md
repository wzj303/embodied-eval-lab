## Data schema

Experiment records use the JSONL format.

See [docs/data-schema.md](docs/data-schema.md) for field definitions,
constraints and examples.


## Generate simulated data

Generate three simulated robot episodes:

```powershell
uv run python -m embodied_eval_lab.collector --episodes 3 --steps 20