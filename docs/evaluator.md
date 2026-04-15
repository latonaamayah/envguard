# Evaluator

The **evaluator** module scores an `.env` file against a schema and returns a
quality grade (A–F) along with a numeric score from 0 to 100.

## How scoring works

| Component | Max penalty |
|---|---|
| Validation errors (missing / wrong type / bad value) | −60 pts |
| Validation warnings | −20 pts |

The remaining score maps to a letter grade:

| Score | Grade |
|---|---|
| 90–100 | A |
| 75–89 | B |
| 60–74 | C |
| 40–59 | D |
| 0–39 | F |

## Python API

```python
from envguard.schema import Schema
from envguard.evaluator import evaluate

schema = Schema.from_file("schema.yaml")
env    = {"APP_ENV": "production", "PORT": "8080"}

result = evaluate(env, schema)
print(result.summary())
# Score: 100/100 (Grade: A) | Passed: 2 | Failed: 0 | Warnings: 0
```

### `EvaluationResult` attributes

| Attribute | Type | Description |
|---|---|---|
| `score` | `int` | Numeric quality score (0–100) |
| `grade` | `str` | Letter grade A–F |
| `total_vars` | `int` | Total variables in schema |
| `passed` | `int` | Variables that passed validation |
| `failed` | `int` | Variables that failed validation |
| `warnings` | `int` | Number of warnings raised |
| `breakdown` | `dict` | Per-component penalty breakdown |
| `notes` | `list[str]` | Human-readable evaluation notes |
| `has_failures` | `bool` | `True` when `failed > 0` |

## CLI usage

```bash
# Basic text output
envguard evaluate .env schema.yaml

# JSON output
envguard evaluate .env schema.yaml --format json

# Fail CI if score drops below 80
envguard evaluate .env schema.yaml --fail-below 80
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (score at or above threshold) |
| `1` | Score below `--fail-below` threshold |
| `2` | File or schema could not be loaded |
