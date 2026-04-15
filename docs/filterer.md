# envguard — Filterer

The `filterer` module lets you partition a dictionary of environment variables
into **matched** and **excluded** groups based on flexible criteria.

## API

```python
from envguard.filterer import filter_env

result = filter_env(
    env,
    prefix="DB_",       # match keys that start with DB_
    suffix="_KEY",      # OR end with _KEY
    pattern=r"^AWS_",  # OR match a regex
    keys=["LOG_LEVEL"], # OR appear in an explicit list
    invert=False,       # set True to flip the match
)

print(result.matched)   # {"DB_HOST": "localhost", ...}
print(result.excluded)  # remaining keys
print(result.summary()) # "2 matched, 4 excluded"
```

### `FilterResult`

| Attribute  | Type            | Description                        |
|------------|-----------------|------------------------------------|
| `matched`  | `Dict[str,str]` | Variables that satisfied criteria  |
| `excluded` | `Dict[str,str]` | Variables that did not match       |

#### Methods

- `has_matches() -> bool` — `True` when at least one variable matched.
- `summary() -> str` — Human-readable count of matched vs excluded.

## Criteria

Criteria are combined with **OR** — a variable matches if *any* criterion is
satisfied. Pass `invert=True` to negate the combined result.

At least one criterion must be supplied, otherwise a `ValueError` is raised.

## CLI integration

The filterer is used internally by other CLI commands (e.g. `envguard group`)
and can be composed with modules such as `masker`, `redactor`, or `exporter`
to process a targeted subset of variables.
