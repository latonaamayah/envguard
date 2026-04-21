# Validator Rules

The `validator_rules` module provides a set of reusable, composable validation rule functions that can be applied to individual `.env` keys.

## Overview

Instead of writing ad-hoc validation logic, you can declare *named rules* and map them to specific keys. Each rule is a plain function with the signature:

```python
def my_rule(key: str, value: str) -> Optional[str]:
    """Return an error message string, or None if the value is valid."""
```

## Built-in Rules

| Rule name | Description |
|---|---|
| `not_empty` | Value must not be blank or whitespace-only |
| `no_whitespace` | Value must not have leading or trailing whitespace |
| `alphanumeric` | Value must match `[\w]+` (letters, digits, underscores) |
| `numeric` | Value must be parseable as a float |
| `url` | Value must start with `http://` or `https://` |

## Python API

```python
from envguard.validator_rules import apply_rules

env = {"DB_PORT": "abc", "API_URL": "not-a-url"}

result = apply_rules(
    env,
    rules={
        "numeric": ["DB_PORT"],
        "url": ["API_URL"],
    },
)

print(result.summary())   # "2 error(s), 0 warning(s)"
for v in result.violations:
    print(v)
```

### Severity

Pass `severity="warning"` to downgrade all violations produced by `apply_rules` to warnings:

```python
result = apply_rules(env, rules, severity="warning")
print(result.warnings)   # violations as warnings
print(result.errors)     # []
```

## CLI Usage

```bash
# Validate specific keys with named rules
envguard-rules .env --rule not_empty:DB_HOST --rule numeric:DB_PORT

# Treat violations as warnings; only fail with --strict
envguard-rules .env --rule not_empty:EMPTY_KEY --severity warning --strict

# List all available built-in rules
envguard-rules .env --list-rules
```

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | No errors (and no warnings when `--strict`) |
| `1` | One or more violations found |
| `2` | Input file not found |
