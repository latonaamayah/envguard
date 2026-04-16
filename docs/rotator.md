# envguard rotator

The `rotator` module generates new secret values for selected (or all) keys in a `.env` file.

## Use Case

Rotate credentials, tokens, and secrets on a schedule or after a potential leak.

## API

```python
from envguard.rotator import rotate

env = {"DB_PASSWORD": "old", "API_KEY": "abc", "APP_NAME": "myapp"}

# Rotate all keys
result = rotate(env)

# Rotate specific keys only
result = rotate(env, keys=["DB_PASSWORD", "API_KEY"])

# Control secret length
result = rotate(env, keys=["DB_PASSWORD"], length=48)

# Use a custom generator
result = rotate(env, keys=["API_KEY"], generator=lambda: "my-custom-secret")
```

## RotateResult

| Attribute | Type | Description |
|---|---|---|
| `entries` | `List[RotateEntry]` | All processed entries |
| `has_rotated` | `bool` | True if any value changed |
| `rotated_keys` | `List[str]` | Keys whose values were rotated |
| `summary()` | `str` | Human-readable summary |
| `as_dict()` | `Dict[str, str]` | Final env mapping |

## CLI

```bash
# Rotate all keys and print to stdout
envguard rotate .env

# Rotate specific keys
envguard rotate .env --keys DB_PASSWORD API_KEY

# Set secret length
envguard rotate .env --length 48

# Write to file
envguard rotate .env --output .env.rotated
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `2` | File not found |
