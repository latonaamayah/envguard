# `validator_schema` — Schema-Based Env Validation

The `validator_schema` module provides structured validation of `.env` files against a schema definition. It checks each declared variable for presence, type correctness, and allowed values, returning a detailed result object.

## Usage

```python
from envguard.loader import load_env_file
from envguard.schema import Schema
from envguard.validator_schema import validate_schema

env = load_env_file(".env")
schema = Schema.from_file("schema.json")

result = validate_schema(env, schema)

if result.has_violations():
    for v in result.violations:
        print(v)
else:
    print("All variables are valid.")
```

## Result Object

`SchemaValidationResult` exposes:

| Attribute / Method | Description |
|--------------------|-------------|
| `violations` | List of `SchemaViolation` objects |
| `passed` | List of keys that passed all checks |
| `has_violations()` | `True` if any violations exist |
| `violation_keys()` | List of keys that have violations |
| `errors()` | Violations with rules: `required`, `type`, `allowed` |
| `warnings()` | Violations with any other rule |
| `summary()` | Human-readable summary string |

## `SchemaViolation` Fields

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | The env variable name |
| `rule` | `str` | The rule that was violated |
| `message` | `str` | Human-readable explanation |

## CLI

```bash
python -m envguard.cli_validate_schema .env schema.json
python -m envguard.cli_validate_schema .env schema.json --format json
python -m envguard.cli_validate_schema .env schema.json --strict
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All variables passed validation |
| `1` | One or more violations found |
| `2` | File or schema could not be loaded |

## Supported Types

- `string` — any non-empty string (default)
- `integer` — must be parseable as `int`
- `boolean` — must be one of `true`, `false`, `1`, `0`, `yes`, `no`

## Allowed Values

When `allowed_values` is specified in the schema, the variable's value must appear in the list or a violation is recorded with rule `allowed`.
