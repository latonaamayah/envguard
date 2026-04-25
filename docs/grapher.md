# envguard grapher

The `grapher` module analyses a `.env` file and builds a **dependency graph** of variable references.

It detects both `${VAR}` and `$VAR` style references.

## Core API

```python
from envguard.grapher import graph

env = {
    "BASE_URL": "https://example.com",
    "API_URL": "${BASE_URL}/api",
    "FULL_URL": "${API_URL}/v1",
}

result = graph(env)
print(result.summary())
# nodes=3 edges=2 cycles=no
```

## Data classes

### `GraphNode`

| Attribute | Type | Description |
|---|---|---|
| `key` | `str` | Variable name |
| `references` | `List[str]` | Variables this key refers to |
| `referenced_by` | `List[str]` | Variables that refer to this key |

### `GraphResult`

| Method | Returns | Description |
|---|---|---|
| `has_cycles()` | `bool` | `True` if a cycle exists in the graph |
| `roots()` | `List[str]` | Keys not referenced by any other key |
| `leaves()` | `List[str]` | Keys that reference no other key |
| `summary()` | `str` | One-line statistics string |

## CLI usage

```bash
# Print full graph
envguard graph .env

# Print summary only
envguard graph --summary .env

# Exit 1 if cycles are present
envguard graph --cycles-only .env
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (no cycles when `--cycles-only`) |
| `1` | Cycles detected (only with `--cycles-only`) |
| `2` | File not found or parse error |
