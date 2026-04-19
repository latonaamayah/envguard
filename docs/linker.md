# Linker

The `linker` module detects inter-variable references within a `.env` file and reports any broken (unresolvable) references.

## Overview

When environment variables reference other variables using `${VAR}` or `$VAR` syntax, the linker checks whether the referenced variable exists in the same env map.

## Usage

```python
from envguard.linker import link

env = {
    "BASE_URL": "https://example.com",
    "API_URL": "${BASE_URL}/api",
    "BROKEN": "${MISSING}/path",
}

result = link(env)
print(result.summary())
# 3 entries checked, 1 with broken references.

for entry in result.entries:
    if entry.has_broken:
        print(f"{entry.key} has broken refs: {entry.broken}")
```

## API

### `link(env: Dict[str, str]) -> LinkResult`

Analyses all values for variable references and returns a `LinkResult`.

### `LinkResult`

| Property | Type | Description |
|---|---|---|
| `entries` | `List[LinkEntry]` | All analysed entries |
| `has_broken` | `bool` | True if any entry has broken references |
| `broken_keys` | `List[str]` | Keys whose values contain broken references |

### `LinkEntry`

| Field | Type | Description |
|---|---|---|
| `key` | `str` | Variable name |
| `value` | `str` | Variable value |
| `references` | `List[str]` | All referenced variable names |
| `broken` | `List[str]` | Referenced names not found in env |

## Reference Syntax

The linker recognises two reference styles:

- Brace style: `${VAR_NAME}`
- Dollar style: `$VAR_NAME` (uppercase + underscores only)
