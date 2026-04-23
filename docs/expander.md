# envguard — Expander

The **expander** module resolves abbreviated or shorthand environment variable
keys to their canonical, fully-qualified names.

## Use-case

Large teams often develop local conventions where keys are abbreviated to save
typing (`DB_PWD`, `LOG_LVL`, `APP_ENV`).  Before deploying, these must match
the canonical names expected by the application (`DB_PASSWORD`, `LOG_LEVEL`,
`APPLICATION_ENV`).  The expander automates this translation.

## Python API

```python
from envguard.expander import expand

env = {
    "DB_PWD": "s3cr3t",
    "LOG_LVL": "info",
    "APP_HOST": "localhost",
}

mapping = {
    "DB_PWD": "DB_PASSWORD",
    "LOG_LVL": "LOG_LEVEL",
}

result = expand(env, mapping)

print(result.has_expansions())   # True
print(result.expanded_keys())    # ['DB_PASSWORD', 'LOG_LEVEL']
print(result.as_dict())          # canonical key/value dict
print(result.summary())          # "2 key(s) expanded out of 3 total."
```

## ExpandResult

| Method | Description |
|---|---|
| `has_expansions()` | `True` if at least one key was expanded |
| `expanded_keys()` | List of canonical keys that were the result of an expansion |
| `as_dict()` | Final key/value mapping with canonical keys |
| `summary()` | Human-readable summary string |

## CLI

```bash
envguard-expand .env --map DB_PWD=DB_PASSWORD --map LOG_LVL=LOG_LEVEL
```

### Options

| Flag | Description |
|---|---|
| `--map ABBREV=CANONICAL` | Mapping pair (repeatable) |
| `--strict` | Exit with code `1` if any expansions were applied |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (no expansions, or expansions without `--strict`) |
| `1` | Expansions detected and `--strict` flag was set |
| `2` | File not found or invalid mapping format |
