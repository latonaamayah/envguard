# Coercer

The `coercer` module provides utilities to **force-convert** raw string values
from a `.env` file into typed Python values (`int`, `float`, `bool`, `str`).

## Usage

```python
from envguard.coercer import coerce

env = {"PORT": "8080", "DEBUG": "true", "RATIO": "0.5"}
rules = {"PORT": "int", "DEBUG": "bool", "RATIO": "float"}

result = coerce(env, rules)
print(result.as_dict())  # {"PORT": 8080, "DEBUG": True, "RATIO": 0.5}
```

## API

### `coerce(env, rules) -> CoerceResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `env` | `dict[str, str]` | Raw environment variables |
| `rules` | `dict[str, str]` | Mapping of key to target type |

Supported target types: `int`, `float`, `bool`, `str`.

Boolean coercion accepts:
- **True**: `1`, `true`, `yes`, `on`
- **False**: `0`, `false`, `no`, `off`

### `CoerceResult`

| Attribute / Method | Description |
|--------------------|-------------|
| `entries` | List of `CoerceEntry` objects |
| `has_errors` | `True` if any coercion failed |
| `failed_keys` | List of keys that could not be coerced |
| `as_dict()` | Dict of successfully coerced values |
| `summary()` | Human-readable summary string |

### `CoerceEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Variable name |
| `original` | `str` | Raw string value |
| `coerced` | `Any` | Converted value (or `None` on failure) |
| `target_type` | `str` | Requested target type |
| `success` | `bool` | Whether coercion succeeded |
| `error` | `str` | Error message on failure |
| `changed` | `bool` | Whether the value representation changed |

## Error Handling

Failed coercions are **recorded** in the result rather than raising exceptions,
allowing you to process all variables and report all failures at once.

```python
if result.has_errors:
    for key in result.failed_keys:
        print(f"Failed to coerce: {key}")
```
