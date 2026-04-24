# Combiner

The `combiner` module merges multiple environment variable dictionaries into a single unified mapping. Later sources take precedence over earlier ones (last-write wins), and all override events are tracked.

## Usage

```python
from envguard.combiner import combine

base = {"DB_HOST": "localhost", "APP_ENV": "dev"}
prod = {"DB_HOST": "prod-db", "SECRET_KEY": "abc"}

result = combine([base, prod], labels=["base", "prod"])

print(result.merged())        # final merged dict
print(result.overridden_keys())  # ["DB_HOST"]
print(result.summary())
```

## API

### `combine(sources, labels=None) -> CombineResult`

Merges a list of `Dict[str, str]` sources. Optional `labels` name each source for traceability.

### `CombineResult`

| Attribute / Method | Description |
|--------------------|-------------|
| `entries` | List of `CombineEntry` objects |
| `source_labels` | Labels assigned to each source |
| `has_overrides()` | `True` if any key was overridden by a later source |
| `overridden_keys()` | Keys that were overridden |
| `merged()` | Final `Dict[str, str]` after combining all sources |
| `summary()` | Human-readable summary string |

### `CombineEntry`

| Field | Description |
|-------|-------------|
| `key` | Environment variable name |
| `value` | Final resolved value |
| `sources` | List of source labels where this key appeared |
| `overridden` | `True` if the key existed in more than one source |
| `message()` | Descriptive string about this entry |

## Behaviour

- Keys present in only one source are passed through unchanged.
- Keys present in multiple sources are marked `overridden=True`, and the value from the **last** source wins.
- Sources are processed in list order (index 0 first, highest index last).
- Results are sorted alphabetically by key for deterministic output.
