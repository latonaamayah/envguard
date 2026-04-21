# Indexer

The `indexer` module builds a positional index of all environment variables in a `.env` file, providing fast lookup, length analysis, and empty-value detection.

## Usage

```python
from envguard.indexer import index

env = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "API_KEY": "secret",
    "EMPTY_VAR": "",
}

result = index(env)
```

## API

### `index(env: Dict[str, str]) -> IndexResult`

Builds a positional index from the given environment dictionary.

### `IndexResult`

| Method | Description |
|---|---|
| `has_entries()` | Returns `True` if any entries are indexed |
| `get(key)` | Returns the `IndexEntry` for the given key, or `None` |
| `keys()` | Returns a list of all indexed keys |
| `empty_keys()` | Returns a list of keys with empty or whitespace-only values |
| `longest()` | Returns the entry with the longest value |
| `shortest()` | Returns the entry with the shortest value |
| `summary()` | Returns a human-readable summary string |

### `IndexEntry`

| Field | Type | Description |
|---|---|---|
| `key` | `str` | The environment variable name |
| `value` | `str` | The raw value |
| `position` | `int` | Zero-based insertion order |
| `length` | `int` | Length of the value string |
| `is_empty` | `bool` | `True` if value is empty or whitespace |

## Example

```python
result = index(env)

print(result.summary())
# 4 entries indexed, 1 empty

entry = result.get("DB_HOST")
print(entry)
# [0] DB_HOST='localhost' (len=9)

print(result.empty_keys())
# ['EMPTY_VAR']

print(result.longest().key)
# DB_HOST
```
