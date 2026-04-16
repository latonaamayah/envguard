# envguard freezer

The `freezer` module lets you **snapshot checksums** of `.env` variable values and later detect if any of them have drifted (changed) since the freeze was taken.

This is useful for auditing production environments where certain variables (e.g., secrets, API keys) should remain stable between deployments.

---

## Core Concepts

- **Freeze**: Record a SHA-256 (first 16 chars) checksum for each selected key.
- **Drift**: A key is considered drifted if its current value produces a different checksum than the frozen one, or if the key is missing entirely.

---

## API

### `freeze(env, keys=None) -> FreezeResult`

Freeze all (or selected) keys from a loaded env dict.

```python
from envguard.freezer import freeze

env = {"DB_HOST": "localhost", "API_KEY": "s3cr3t"}
result = freeze(env, keys=["API_KEY"])
print(result.summary())  # 1 key(s) frozen.
```

### `save_freeze(result, path)`

Persist a `FreezeResult` to a JSON file.

### `load_freeze(path) -> FreezeResult`

Load a previously saved freeze file.

### `FreezeResult.drifted(env) -> List[str]`

Returns a list of keys that have changed or disappeared since the freeze.

```python
from envguard.freezer import freeze, save_freeze, load_freeze

freeze_result = freeze(env)
save_freeze(freeze_result, ".env.freeze")

# Later...
loaded = load_freeze(".env.freeze")
drifted_keys = loaded.drifted(current_env)
if drifted_keys:
    print("Drift detected:", drifted_keys)
```

---

## CLI Usage

### Freeze an env file

```bash
envguard-freeze .env --output .env.freeze
```

### Check for drift

```bash
envguard-freeze .env --check --freeze-file .env.freeze
```

Exits with code `1` if drift is detected, `0` if clean.

### Freeze only specific keys

```bash
envguard-freeze .env --output .env.freeze --keys API_KEY DB_PASSWORD
```

---

## Output Format (`.env.freeze`)

```json
{
  "frozen": [
    {"key": "API_KEY", "checksum": "a1b2c3d4e5f60718"},
    {"key": "DB_PASSWORD", "checksum": "9f8e7d6c5b4a3210"}
  ]
}
```
