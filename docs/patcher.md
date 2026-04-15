# Patcher

The **patcher** module applies a set of `KEY=VALUE` overrides to an existing
`.env` mapping, producing a new merged mapping without mutating the original.

## Python API

```python
from envguard.patcher import patch

env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}
updates = {"PORT": "6543", "NEW_KEY": "hello"}

result = patch(env, updates)
print(result.patched)   # {'HOST': 'localhost', 'PORT': '6543', 'DEBUG': 'false', 'NEW_KEY': 'hello'}
print(result.summary()) # '1 added, 1 updated, 1 unchanged'
```

### `PatchResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `patched` | `dict` | Final merged mapping |
| `entries` | `list[PatchEntry]` | Per-key change records |
| `has_changes()` | `bool` | `True` if any key was added or updated |
| `summary()` | `str` | Human-readable counts |

### `PatchEntry`

| Field | Description |
|-------|-------------|
| `key` | Variable name |
| `old_value` | Previous value (`None` if newly added) |
| `new_value` | Value after patch |
| `action` | `'added'`, `'updated'`, or `'unchanged'` |

## CLI

```bash
# Print patched output to stdout
envguard-patch .env PORT=6543 DEBUG=true

# Overwrite the file in-place
envguard-patch .env PORT=6543 --in-place
```

### Options

| Flag | Description |
|------|-------------|
| `--in-place` | Write the result back to the source file |

## Notes

- The original `env` dict is **never mutated**.
- Multiple `KEY=VALUE` pairs may be supplied in a single invocation.
- Values may contain `=` characters; only the first `=` is used as the
  delimiter.
