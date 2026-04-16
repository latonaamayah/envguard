# Extractor

The `extractor` module lets you extract a subset of environment variables from a loaded env dictionary by matching keys (or values) against one or more regular-expression patterns.

## API

### `extract(env, patterns, match_values=False) -> ExtractResult`

Scans every key in `env` against each pattern in `patterns` (Python `re.search` semantics). The first matching pattern wins and the entry is recorded once.

| Parameter | Type | Description |
|-----------|------|-------------|
| `env` | `Dict[str, str]` | The loaded environment variables. |
| `patterns` | `List[str]` | One or more regex patterns to test against. |
| `match_values` | `bool` | When `True`, patterns are tested against the *value* instead of the key. |

Invalid regex patterns are silently skipped.

### `ExtractResult`

| Attribute / Method | Description |
|--------------------|-------------|
| `matches` | List of `ExtractEntry` objects for every matched key. |
| `unmatched_keys` | Keys that did not match any pattern. |
| `has_matches()` | Returns `True` when at least one key was extracted. |
| `keys_for_pattern(pattern)` | Returns keys matched by a specific pattern. |
| `as_dict()` | Returns matched key-value pairs as a plain `dict`. |
| `summary()` | Human-readable summary string. |

### `ExtractEntry`

| Field | Description |
|-------|-------------|
| `key` | The environment variable name. |
| `value` | The environment variable value. |
| `pattern` | The pattern that first matched this entry. |

## Examples

```python
from envguard.loader import load_env_file
from envguard.extractor import extract

env = load_env_file(".env")

# Extract all DB_ and AWS_ variables
result = extract(env, [r"^DB_", r"^AWS_"])
print(result.summary())
for key, value in result.as_dict().items():
    print(f"{key}={value}")

# Extract variables whose value looks like a URL
result = extract(env, [r"https?://"], match_values=True)
```
