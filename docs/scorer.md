# Scorer

The `scorer` module evaluates the quality of a `.env` file and assigns a score based on simple heuristics.

## How It Works

Each key is evaluated independently and awarded up to **10 points**:

| Criterion | Points |
|---|---|
| Non-empty value | 5 |
| Key length ≥ 3 characters | 2 |
| Key is fully uppercase | 3 |

The final score is expressed as a percentage and mapped to a letter grade.

## Grades

| Percentage | Grade |
|---|---|
| ≥ 90% | A |
| ≥ 75% | B |
| ≥ 60% | C |
| ≥ 40% | D |
| < 40% | F |

## Usage

```python
from envguard.scorer import score

env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"}
result = score(env)
print(result.summary())
# Score: 20/20 (100.0%) Grade: A
```

## CLI

```bash
python -m envguard.cli_score .env
python -m envguard.cli_score .env --verbose
```

### Verbose Output

```
  DATABASE_URL: 10/10 — non-empty, key length ok, uppercase key
  PORT: 10/10 — non-empty, key length ok, uppercase key
Score: 20/20 (100.0%) Grade: A
```
