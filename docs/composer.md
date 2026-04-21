# envguard — Composer

The `composer` module merges multiple `.env` dictionaries into a single output, applying later sources as overrides and maintaining a full audit trail of every key's provenance.

## Usage

```python
from envguard.composer import compose
from envguard.loader import load_env_file

base    = load_env_file(".env")
staging = load_env_file(".env.staging")

result = compose([base, staging], sources=[".env", ".env.staging"])

print(result.merged)          # final key→value dict
print(result.overridden_keys) # keys that were overwritten
print(result.summary())       # human-readable summary
```

## API

### `compose(envs, sources=None) -> ComposeResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `envs` | `List[Dict[str, str]]` | Ordered list of env dicts (first = lowest priority) |
| `sources` | `List[str] \| None` | Optional labels for each dict (used in audit trail) |

### `ComposeResult`

| Attribute / Property | Type | Description |
|----------------------|------|-------------|
| `entries` | `List[ComposeEntry]` | All entries including overridden ones |
| `sources` | `List[str]` | Source labels in composition order |
| `merged` | `Dict[str, str]` | Final winning values |
| `has_overrides` | `bool` | `True` if any key was overridden |
| `overridden_keys` | `List[str]` | Keys that lost to a later source |
| `summary()` | `str` | Human-readable composition summary |

### `ComposeEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Environment variable name |
| `value` | `str` | Value from this source |
| `source` | `str` | Filename / label that provided this entry |
| `overridden_by` | `str \| None` | Label of the source that won over this entry |
| `was_overridden` | `bool` | Convenience property |

## Example — three-layer composition

```python
defaults  = {"LOG_LEVEL": "info",  "TIMEOUT": "30"}
shared    = {"LOG_LEVEL": "warn",  "DB_HOST": "shared-db"}
local_env = {"DB_HOST": "localhost"}

result = compose(
    [defaults, shared, local_env],
    sources=["defaults", "shared", "local"],
)
# result.merged == {"LOG_LEVEL": "warn", "TIMEOUT": "30", "DB_HOST": "localhost"}
```
