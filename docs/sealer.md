# envguard sealer

The `sealer` module provides tamper-detection for `.env` files by computing and storing checksums for each variable value.

## Overview

When you **seal** an env file, each value is hashed with SHA-256 and the first 16 hex characters are stored as a fingerprint. Later, you can **verify** the env file against those fingerprints to detect any changes.

## API

### `seal(env: Dict[str, str]) -> SealResult`

Computes checksums for all keys in `env` and returns a `SealResult`.

### `verify(env: Dict[str, str], seal_data: Dict[str, str]) -> SealResult`

Compares current values against stored checksums. Keys whose checksums differ are reported as tampered.

### `save_seal(result: SealResult, path: str) -> None`

Persists the seal data (key → checksum mapping) to a JSON file.

### `load_seal(path: str) -> Dict[str, str]`

Loads a previously saved seal file.

## Data Classes

### `SealEntry`
- `key` — variable name
- `value` — current value
- `checksum` — 16-char SHA-256 fingerprint

### `SealResult`
- `entries` — list of `SealEntry`
- `tampered` — list of keys whose values changed
- `has_entries()` — whether any entries exist
- `has_tampering()` — whether any tampering was detected
- `as_dict()` — returns `{key: checksum}` mapping
- `summary()` — human-readable status string

## Example

```python
from envguard.loader import load_env_file
from envguard.sealer import seal, verify, save_seal, load_seal

env = load_env_file(".env")

# Seal and save
result = seal(env)
save_seal(result, ".env.seal")

# Later: verify
env_now = load_env_file(".env")
seal_data = load_seal(".env.seal")
check = verify(env_now, seal_data)

if check.has_tampering():
    print("Tampered keys:", check.tampered)
else:
    print("All clear.")
```
