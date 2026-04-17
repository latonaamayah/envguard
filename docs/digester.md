# Digester

The `digester` module computes cryptographic hashes of environment variable values.
This is useful for detecting value changes without exposing sensitive data in logs or reports.

## Usage

```python
from envguard.digester import digest

env = {
    "DB_PASSWORD": "secret",
    "API_KEY": "mykey",
}

result = digest(env, algorithm="sha256")
print(result.summary())
# 2 key(s) digested using sha256

for entry in result.entries:
    print(entry)
# DB_PASSWORD=<sha256hex> (sha256)
# API_KEY=<sha256hex> (sha256)
```

## Supported Algorithms

| Algorithm | Digest Length |
|-----------|---------------|
| `md5`     | 32 hex chars  |
| `sha1`    | 40 hex chars  |
| `sha256`  | 64 hex chars  |

## Selective Digesting

Pass a list of keys to digest only specific variables:

```python
result = digest(env, algorithm="sha1", keys=["DB_PASSWORD"])
```

## API

### `digest(env, algorithm, keys) -> DigestResult`

- `env`: dict of environment variables
- `algorithm`: one of `"md5"`, `"sha1"`, `"sha256"` (default: `"sha256"`)
- `keys`: optional list of keys to include; all keys used if `None`

### `DigestResult`

| Method / Property | Description |
|-------------------|-------------|
| `has_entries()`   | True if any entries exist |
| `as_dict()`       | Returns `{key: digest}` mapping |
| `summary()`       | Human-readable summary string |
| `entries`         | List of `DigestEntry` objects |

### `DigestEntry`

| Field       | Type  | Description                  |
|-------------|-------|------------------------------|
| `key`       | str   | Environment variable name    |
| `value`     | str   | Original value               |
| `algorithm` | str   | Hash algorithm used          |
| `digest`    | str   | Hex digest of the value      |
