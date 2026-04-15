# Transformer

The `transformer` module applies named transformation rules to the values of environment variables in a `.env` file.

## Built-in Rules

| Rule | Description |
|------|-------------|
| `uppercase` | Converts the value to upper case |
| `lowercase` | Converts the value to lower case |
| `strip` | Strips leading and trailing whitespace |
| `strip_quotes` | Removes surrounding single or double quotes |

## Python API

```python
from envguard.transformer import transform

env = {"LOG_LEVEL": "debug", "DB_HOST": "  localhost  "}
result = transform(env, rules={"LOG_LEVEL": "uppercase", "DB_HOST": "strip"})

print(result.vars)
# {'LOG_LEVEL': 'DEBUG', 'DB_HOST': 'localhost'}

print(result.has_changes())  # True
print(result.summary())
```

### Custom Rules

Pass a `custom_rules` dict mapping rule names to callables:

```python
result = transform(
    env,
    rules={"APP_ENV": "exclaim"},
    custom_rules={"exclaim": lambda v: v + "!"},
)
```

## CLI Usage

```bash
envguard transform .env --rule LOG_LEVEL=uppercase --rule DB_HOST=strip
```

### Options

| Flag | Description |
|------|-------------|
| `--rule KEY=RULE` | Apply a named rule to a key. Repeatable. |
| `--show-only-changed` | Only print keys whose values were changed. |

### Example

```bash
$ envguard transform .env --rule LOG_LEVEL=uppercase --show-only-changed
LOG_LEVEL=DEBUG
```

## Data Classes

### `TransformEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Variable name |
| `original` | `str` | Original value |
| `transformed` | `str` | Value after transformation |
| `rule` | `str` | Name of the applied rule |
| `changed` | `bool` | Whether the value changed |

### `TransformResult`

| Method | Description |
|--------|-------------|
| `has_changes()` | Returns `True` if any value changed |
| `summary()` | Human-readable summary of changes |
