# envguard.enforcer

The `enforcer` module applies named validation rules to specific keys in an env dict, producing a structured result that reports which checks passed or failed.

## Overview

Unlike the schema-based validator, the enforcer lets you attach arbitrary rule names to individual keys, making it easy to express per-key constraints declaratively.

## Usage

```python
from envguard.enforcer import enforce

env = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "SECRET_KEY": "s3cr3t!!",
    "PORT": "8080",
}

rules = {
    "DATABASE_URL": ["not_empty", "no_spaces"],
    "SECRET_KEY":   ["not_empty", "min_length_8"],
    "PORT":         ["not_empty", "no_spaces"],
}

result = enforce(env, rules)
print(result.summary())
# 3/3 checks passed, 0 failed
```

## Built-in Rules

| Rule name       | Description                                  |
|-----------------|----------------------------------------------|
| `not_empty`     | Value must not be blank or whitespace-only   |
| `no_spaces`     | Value must not contain space characters      |
| `uppercase_key` | Key name must be fully uppercase             |
| `min_length_8`  | Value must be at least 8 characters long     |
| `no_quotes`     | Value must not start with `"` or `'`         |

## Custom Rules

Pass a `custom_rules` dict mapping rule names to callables `(key, value) -> Optional[str]`. Return `None` to pass, or a message string to fail.

```python
def must_be_numeric(key, value):
    return None if value.isdigit() else f"{key} must be numeric"

result = enforce(env, {"PORT": ["numeric"]}, custom_rules={"must_be_numeric": must_be_numeric})
```

## API

### `enforce(env, rules, custom_rules=None) -> EnforceResult`

- **env** – `Dict[str, str]` of environment variables.
- **rules** – `Dict[str, List[str]]` mapping key names to lists of rule names.
- **custom_rules** – optional `Dict[str, RuleFunc]` for user-defined rules.

### `EnforceResult`

| Attribute / Method | Description                              |
|--------------------|------------------------------------------|
| `entries`          | List of `EnforceEntry` objects           |
| `has_failures`     | `True` if any entry failed               |
| `failed_keys`      | List of keys with at least one failure   |
| `passed_keys`      | List of keys where all rules passed      |
| `summary()`        | Human-readable pass/fail summary string  |

### `EnforceEntry`

| Field     | Type            | Description                        |
|-----------|-----------------|------------------------------------|
| `key`     | `str`           | Environment variable key           |
| `value`   | `str`           | Value at time of evaluation        |
| `rule`    | `str`           | Name of the rule applied           |
| `passed`  | `bool`          | Whether the rule passed            |
| `message` | `Optional[str]` | Failure message, or `None` on pass |
