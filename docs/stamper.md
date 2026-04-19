# Stamper

The `stamper` module timestamps and fingerprints environment variable values, creating an auditable record of when each variable was observed and what its value was at that point in time.

## Usage

```python
from envguard.stamper import stamp

env = {
    "DB_HOST": "localhost",
    "API_KEY": "secret123",
    "APP_ENV": "production",
}

result = stamp(env, label="deploy-v2.1")
print(result.summary())
# 3 key(s) stamped [deploy-v2.1].
```

## Stamping Selected Keys

```python
result = stamp(env, keys=["DB_HOST", "API_KEY"])
```

Only the specified keys will be included in the result. Keys not present in the env are silently skipped.

## StampEntry

Each entry contains:

| Field | Description |
|-------|-------------|
| `key` | The variable name |
| `value` | The variable value at stamp time |
| `stamped_at` | ISO 8601 UTC timestamp |
| `fingerprint` | 16-char MD5 hex digest of the value |

## StampResult

| Method | Description |
|--------|-------------|
| `has_entries()` | Returns `True` if any keys were stamped |
| `get(key)` | Returns the `StampEntry` for a key, or `None` |
| `summary()` | Human-readable summary string |
| `as_dict()` | Serialisable dictionary representation |
| `to_json()` | Pretty-printed JSON string |

## Fingerprinting

Fingerprints are computed as the first 16 characters of the MD5 hex digest of the raw value string. They are suitable for drift detection and audit trails, not cryptographic security.
