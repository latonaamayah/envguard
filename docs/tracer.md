# Tracer

The `tracer` module tracks how environment variable values are resolved across multiple `.env` layers. It helps debug configuration precedence by showing which layer introduced a key and which layer overrode it.

## Usage

```python
from envguard.tracer import trace

base = {"DB_HOST": "localhost", "APP_ENV": "development"}
prod = {"DB_HOST": "prod.db.example.com", "APP_ENV": "production"}

result = trace([base, prod], labels=["base", "prod"])

for entry in result.entries:
    print(entry.message())
```

### Output

```
DB_HOST: 'localhost' (from base) overridden by 'prod.db.example.com' (from prod)
APP_ENV: 'development' (from base) overridden by 'production' (from prod)
```

## API

### `trace(layers, labels=None) -> TraceResult`

- `layers`: list of `dict[str, str]` representing env layers (first = lowest priority)
- `labels`: optional list of string labels for each layer

### `TraceResult`

| Property | Description |
|---|---|
| `entries` | List of `TraceEntry` objects |
| `has_overrides` | True if any key was overridden |
| `overridden_keys` | Keys that were overridden by a later layer |
| `summary()` | Human-readable summary string |
| `as_dict()` | Final resolved key-value mapping |

### `TraceEntry`

| Field | Description |
|---|---|
| `key` | Variable name |
| `value` | Value from the originating layer |
| `source` | Label of the originating layer |
| `overridden_by` | Label of the overriding layer (if any) |
| `final_value` | The winning value after override |
| `was_overridden` | Boolean convenience property |
| `message()` | Human-readable trace message |
