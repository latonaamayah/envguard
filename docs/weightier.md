# Weightier

The `weightier` module assigns numeric priority weights to environment variables based on configurable rules and heuristics.

## Overview

Not all environment variables are equal. Some are critical (e.g., secrets, API keys), while others are low-priority (e.g., display names, empty placeholders). The weightier helps you rank variables by importance.

## Usage

```python
from envguard.weightier import weight

env = {
    "DB_PASSWORD": "s3cr3t",
    "APP_NAME": "myapp",
    "EMPTY_VAR": "",
}

result = weight(env)
print(result.summary())

for entry in result.top(3):
    print(entry)
```

## Custom Rules

You can provide explicit weights for specific keys:

```python
result = weight(env, rules={"APP_NAME": 100, "EMPTY_VAR": -50})
```

Explicit rules always take precedence over heuristics.

## Heuristics

| Condition | Weight Delta |
|---|---|
| Key contains `password`, `secret`, `token`, `key`, `api`, `auth` | +30 |
| Value is empty | -20 |
| Value length > 64 characters | +10 |
| Key is fully uppercase | +5 |

## API

### `weight(env, rules=None) -> WeightResult`

Compute weights for all variables in `env`.

### `WeightResult`

| Method | Description |
|---|---|
| `has_entries()` | Returns `True` if any entries exist |
| `top(n)` | Returns top N highest-weighted entries |
| `bottom(n)` | Returns N lowest-weighted entries |
| `as_dict()` | Returns `{key: weight}` mapping |
| `summary()` | Human-readable summary string |

### `WeightEntry`

| Field | Type | Description |
|---|---|---|
| `key` | `str` | Variable name |
| `value` | `str` | Variable value |
| `weight` | `int` | Computed weight score |
| `reason` | `str` | Explanation for the score |
