# Sanitizer

The `sanitizer` module cleans environment variable values by applying transformation rules, removing unwanted characters, and normalizing formatting.

## Usage

```python
from envguard.sanitizer import sanitize

env = {
    "APP_NAME": "  myapp  ",
    "DB_PASS": '"secret"',
    "API_KEY": "key\nwith\nnewlines",
}

result = sanitize(env, rules=["strip", "strip_quotes", "remove_newlines"])
print(result.as_dict)
# {'APP_NAME': 'myapp', 'DB_PASS': 'secret', 'API_KEY': 'keywith newlines'}
```

## Available Rules

| Rule | Description |
|------|-------------|
| `strip` | Remove leading and trailing whitespace |
| `strip_quotes` | Remove surrounding single or double quotes |
| `remove_newlines` | Remove `\n` and `\r` characters |
| `remove_nulls` | Remove null bytes (`\x00`) |
| `alphanumeric_only` | Keep only letters and digits |
| `lowercase` | Convert value to lowercase |
| `uppercase` | Convert value to uppercase |

## Per-Key Rules

You can override global rules for specific keys:

```python
result = sanitize(
    env,
    rules=["strip"],
    key_rules={
        "DB_PASS": ["strip_quotes"],
        "TOKEN": ["remove_nulls", "strip"],
    },
)
```

## API

### `sanitize(env, rules, key_rules) -> SanitizeResult`

- `env`: `Dict[str, str]` — input environment variables
- `rules`: global list of rules applied to all keys (default: `["strip"]`)
- `key_rules`: per-key rule overrides

### `SanitizeResult`

| Property / Method | Description |
|-------------------|-------------|
| `has_changes` | `True` if any value was modified |
| `changed_keys` | List of keys whose values changed |
| `as_dict` | Sanitized key-value dictionary |
| `summary()` | Human-readable summary string |
| `entries` | List of `SanitizeEntry` objects |

### `SanitizeEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Variable name |
| `original` | `str` | Value before sanitization |
| `sanitized` | `str` | Value after sanitization |
| `changed` | `bool` | Whether the value was modified |
