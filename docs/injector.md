# Injector

The **injector** module merges variables from a source `.env` file into a target environment mapping, with fine-grained control over whether existing keys are preserved or overwritten.

## API

### `inject(env, target=None, *, overwrite=False) -> InjectResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `env` | `Dict[str, str]` | Variables to inject. |
| `target` | `Dict[str, str] \| None` | Destination mapping. Defaults to a new empty dict. |
| `overwrite` | `bool` | When `True`, existing keys in `target` are replaced. |

Returns an `InjectResult` containing:

- `injected` — list of `InjectEntry` objects for keys that were written.
- `skipped` — list of key names that were left untouched.

### `InjectEntry`

```python
@dataclass
class InjectEntry:
    key: str
    value: str
    overwritten: bool  # True when the key already existed in target
```

### `InjectResult` helpers

| Method | Returns | Description |
|--------|---------|-------------|
| `has_injected()` | `bool` | `True` if at least one key was injected. |
| `has_skipped()` | `bool` | `True` if at least one key was skipped. |
| `summary()` | `str` | Human-readable summary, e.g. `"3 injected, 1 skipped"`. |
| `as_dict()` | `dict` | Mapping of injected key → value. |

## CLI

```
envguard inject <source> <target> [--overwrite] [--dry-run]
```

| Flag | Description |
|------|-------------|
| `--overwrite` | Replace existing keys in the target file. |
| `--dry-run` | Print the result without modifying the target file. |

## Examples

```bash
# Inject new variables from .env.defaults into .env (keep existing values)
envguard inject .env.defaults .env

# Force-overwrite all keys from .env.ci into .env
envguard inject .env.ci .env --overwrite

# Preview what would be injected without touching the file
envguard inject .env.staging .env --dry-run
```
