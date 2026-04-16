# Deduplicator

The `deduplicator` module resolves duplicate keys in a list of `(key, value)` pairs, such as those parsed from a raw `.env` file where a key appears more than once.

## Behaviour

- The **last** occurrence of a key wins and is kept in the cleaned output.
- All earlier values for the same key are recorded as `removed_values`.
- Keys with no duplicates pass through unchanged.

## Usage

```python
from envguard.deduplicator import deduplicate

pairs = [
    ("HOST", "localhost"),
    ("PORT", "5432"),
    ("HOST", "remotehost"),  # duplicate
]

result = deduplicate(pairs)
print(result.cleaned)       # {"HOST": "remotehost", "PORT": "5432"}
print(result.has_duplicates)  # True
print(result.summary())
```

## API

### `deduplicate(pairs: List[tuple]) -> DeduplicateResult`

Accepts an ordered list of `(key, value)` tuples and returns a `DeduplicateResult`.

### `DeduplicateResult`

| Attribute | Type | Description |
|---|---|---|
| `entries` | `List[DeduplicateEntry]` | One entry per duplicated key |
| `cleaned` | `Dict[str, str]` | Resolved env vars (last value wins) |
| `has_duplicates` | `bool` | True if any duplicates were found |
| `duplicate_keys` | `List[str]` | Keys that had duplicates |
| `summary()` | `str` | Human-readable summary |

### `DeduplicateEntry`

| Attribute | Type | Description |
|---|---|---|
| `key` | `str` | The duplicated key name |
| `kept_value` | `str` | The value that was retained |
| `removed_values` | `List[str]` | Earlier values that were discarded |
| `count` | `int` | Number of removed values |
