# envguard pinner

The **pinner** module lets you lock (pin) the checksum of each environment variable value and later detect any drift — new keys, removed keys, or changed values.

## Core Concepts

| Term | Description |
|------|-------------|
| **Pin** | A JSON file mapping each key to a 16-char SHA-256 checksum of its value. |
| **Drift** | Any difference between the current env and the saved pin. |

## Python API

```python
from envguard.pinner import pin, save_pin, load_pin

env = {"DB_HOST": "localhost", "DB_PORT": "5432"}

# Create a new pin (no existing reference)
result = pin(env)
print(result.summary())   # No drift detected.

# Save checksums to disk
save_pin(result, ".env.pin")

# Later — reload and compare
existing = load_pin(".env.pin")
result2 = pin(env, existing)
print(result2.has_drift())  # False
```

## PinResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `pinned` | `Dict[str, PinEntry]` | All pinned entries. |
| `changed` | `List[str]` | Keys whose value changed. |
| `new_keys` | `List[str]` | Keys present in env but not in pin. |
| `removed_keys` | `List[str]` | Keys in pin but absent from env. |

## CLI Usage

### Save a pin

```bash
envguard pin save .env --output .env.pin
```

### Check for drift

```bash
envguard pin check .env --pin .env.pin
```

Exits `0` when no drift is detected, `1` when drift is found, `2` on file errors.

## Pin File Format

```json
{
  "DB_HOST": "4a7b3c9d1e2f5a6b",
  "DB_PORT": "9c8d7e6f5a4b3c2d"
}
```

Checksums are the first 16 hex characters of the SHA-256 hash of the raw value string.
