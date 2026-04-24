# envguard differ2

The `differ2` module provides a **structural diff** between two `.env` dictionaries, with schema-aware sensitivity masking.

## Features

- Detects **added**, **removed**, **changed**, and **unchanged** keys
- Automatically masks values for sensitive keys (passwords, tokens, secrets, etc.)
- Returns a structured `StructDiffResult` with categorised entries
- Provides a human-readable `summary()`

## Usage

```python
from envguard.loader import load_env_file_safe
from envguard.differ2 import struct_diff

left = load_env_file_safe(".env.staging")
right = load_env_file_safe(".env.production")

result = struct_diff(left, right)

print(result.summary())
# +1 added, -1 removed, ~2 changed

for entry in result.changed:
    print(entry.message)
```

## CLI

```bash
envguard diff2 .env.staging .env.production
envguard diff2 .env.staging .env.production --no-unchanged
envguard diff2 .env.staging .env.production --strict
```

### Options

| Flag | Description |
|------|-------------|
| `--no-unchanged` | Hide unchanged entries from output |
| `--strict` | Exit with code 1 if any differences are found |

## Data Model

### `StructDiffEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Environment variable name |
| `left_value` | `Optional[str]` | Value in the left (base) file |
| `right_value` | `Optional[str]` | Value in the right (target) file |
| `status` | `str` | One of: `added`, `removed`, `changed`, `unchanged` |
| `is_sensitive` | `bool` | Whether the key matches a sensitive pattern |

### `StructDiffResult`

| Property | Description |
|----------|-------------|
| `has_changes` | `True` if any entry is not `unchanged` |
| `added` | List of entries with status `added` |
| `removed` | List of entries with status `removed` |
| `changed` | List of entries with status `changed` |
| `summary()` | Short string: `+N added, -N removed, ~N changed` |
