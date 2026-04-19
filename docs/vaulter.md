# Vaulter

The `vaulter` module masks and checksums environment variable values, producing a `VaultResult` that can be inspected or serialised to JSON.

## Usage

```python
from envguard.vaulter import vault

env = {"DB_PASSWORD": "supersecret", "API_KEY": "abc123xyz"}
result = vault(env)

for entry in result.entries:
    print(entry)  # DB_PASSWORD=supe******* [a3f1c2b4]
```

## Vault selected keys only

```python
result = vault(env, keys=["DB_PASSWORD"])
```

## JSON output

```python
print(result.to_json())
```

```json
{
  "DB_PASSWORD": {
    "masked": "supe*******",
    "checksum": "a3f1c2b4d5e6f7a8"
  }
}
```

## CLI

```bash
envguard vault .env
envguard vault .env --keys DB_PASSWORD API_KEY
envguard vault .env --json
```

## API

### `vault(env, keys=None) -> VaultResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `env` | `dict` | Key/value pairs to vault |
| `keys` | `list` \| `None` | Subset of keys to process; all keys if `None` |

### `VaultResult`

| Method | Returns | Description |
|--------|---------|-------------|
| `has_entries()` | `bool` | Whether any entries were vaulted |
| `get(key)` | `VaultEntry \| None` | Look up a single entry |
| `keys()` | `list[str]` | All vaulted key names |
| `as_dict()` | `dict` | Plain key/value pairs (unmasked) |
| `to_json()` | `str` | JSON representation of masked values |
| `summary()` | `str` | Human-readable summary |
